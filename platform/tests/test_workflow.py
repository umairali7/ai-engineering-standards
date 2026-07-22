"""M4 conformance tests: peer-review orchestration, calibration gate,
human grant workflow, status model, environment re-qualification (D7).

PLATFORM.md §10 M4 exit criteria: a complete cycle from evidence to a
human-recorded grant runs for one scope; the reviewer-model calibration
gate is enforced; an environment-change trigger invalidates a grant.
"""

import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _register(tmp_path, model_id="demo"):
    from aies import registry
    entry = {"id": model_id, "family": "demo", "runtime": "mock", "model": model_id,
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / f"{model_id}.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def _score(run_id, rater, kind, score):
    from aies import rating, raters, workspace
    original = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                          .read_text(encoding="utf-8"))
    declarations = [{"name": rater, "kind": kind}]
    if kind == "human":
        manifest = workspace.read_json(workspace.run_dir(run_id) / "manifest.json")
        areas = [area["area"] for area in manifest["areas"]]
        subject_id = (manifest.get("subject") or {}).get("id") or manifest["model"]["registry_id"]
        declarations = []
        for suffix in ("primary", "peer"):
            rater_id = ("test-" + "".join(c.lower() if c.isalnum() else "-" for c in rater)
                        + "-" + suffix)
            try:
                raters.register(
                    rater_id, f"{rater} {suffix}", competency_areas=areas,
                    risk_tiers=[manifest["risk_tier"]],
                    qualified_until="2099-01-01T00:00:00+00:00",
                    calibration_valid_until="2099-01-01T00:00:00+00:00",
                    anchor_library_version="test-anchors-v1",
                    registered_by="Test Registry Authority")
            except FileExistsError:
                pass
            declarations.append({
                "id": rater_id, "name": f"{rater} {suffix}", "kind": "human",
                "conflict_declaration": {
                    "declared": True, "has_conflict": False,
                    "subject_id": subject_id,
                },
            })
    for declaration in declarations:
        sheet = json.loads(json.dumps(original))
        sheet["rater"] = declaration
        for item in sheet["items"]:
            item["scores"] = {d: score for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
            if score <= 2:  # findings are mandatory for low scores (AIES-AESQS-ER-01)
                item["findings"] = [{"dimension": "EV1", "score": score,
                                     "finding": "synthetic low score for test"}]
        rating.ingest_scores(run_id, sheet)


def _decision_people(run_id, base="Human"):
    """Return the verified assessor/peer arguments required by v5 decisions."""
    from aies import raters, workspace
    manifest = workspace.read_json(workspace.run_dir(run_id) / "manifest.json")
    areas = [area["area"] for area in manifest["areas"]]
    subject_id = (manifest.get("subject") or {}).get("id") or manifest["model"]["registry_id"]
    people = []
    for suffix in ("primary", "peer"):
        rater_id = ("test-" + "".join(c.lower() if c.isalnum() else "-" for c in base)
                    + "-" + suffix)
        name = f"{base} {suffix}"
        try:
            raters.get(rater_id)
        except raters.RaterError:
            raters.register(
                rater_id, name, competency_areas=areas,
                risk_tiers=[manifest["risk_tier"]],
                qualified_until="2099-01-01T00:00:00+00:00",
                calibration_valid_until="2099-01-01T00:00:00+00:00",
                anchor_library_version="test-anchors-v1",
                registered_by="Test Registry Authority")
        people.append((rater_id, name))
    return {
        "assessor": people[0][1], "assessor_id": people[0][0],
        "peer_reviewer": people[1][1], "peer_reviewer_id": people[1][0],
        "assessor_conflict_free": True, "peer_conflict_free": True,
        "role": "ROLE-06", "phases": ["P09", "P10"],
        "sponsor": "Test Sponsor",
        "framework_version": "AIES-AESQS-CF-01@review-2026-07-22",
        "valid_from": "2026-07-01T00:00:00+00:00",
        "valid_until": ("2026-12-31T00:00:00+00:00"
                        if manifest["risk_tier"] in ("RT3", "RT4")
                        else "2027-06-30T00:00:00+00:00"),
    }


# --- calibration gate -------------------------------------------------

def test_calibration_gate_admits_and_rejects():
    from aies import review
    human = [{"EV1": 3, "EV2": 3, "EV3": 3, "EV4": 3, "EV5": 3, "EV6": 3}] * 5
    close = [{"EV1": 3, "EV2": 2, "EV3": 3, "EV4": 3, "EV5": 4, "EV6": 3}] * 5  # all within 1
    far = [{"EV1": 0, "EV2": 0, "EV3": 0, "EV4": 0, "EV5": 0, "EV6": 0}] * 5     # all off by 3
    assert review.calibrate(close, human)["passed"] is True
    assert review.calibrate(far, human)["passed"] is False
    ok, _ = review.reviewer_admitted(qualified_for_review=False,
                                     calibration=review.calibrate(close, human))
    assert ok
    bad, reason = review.reviewer_admitted(qualified_for_review=False,
                                           calibration=review.calibrate(far, human))
    assert not bad and "advisory" in reason.lower()


def test_uncalibrated_reviewer_is_advisory_only(ws, tmp_path):
    from aies import engine, review
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human Rater", "human", 3)
    _score(run["run_id"], "reviewer-model", "model", 1)  # disagrees hard
    pkg = review.assemble_review_package(run["run_id"], reviewer_label="reviewer-model")
    assert pkg["reviewer"]["admitted"] is False
    assert "advisory only" in pkg["summary"]["note"]
    # divergences (human 3 vs model 1 = delta 2) surfaced, not averaged
    assert pkg["summary"]["n_divergences"] > 0


def test_divergences_surfaced_not_averaged(ws, tmp_path):
    from aies import engine, review
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 4)
    _score(run["run_id"], "reviewer-model", "model", 1)  # delta 3 on every dim
    pkg = review.assemble_review_package(
        run["run_id"], reviewer_label="reviewer-model", reviewer_qualified_for_review=True)
    for d in pkg["divergences_for_resolution"]:
        assert d["delta"] >= 2
    assert pkg["reviewer"]["admitted"] is True  # qualified reviewer


# --- human grant workflow + status model ------------------------------

def test_platform_never_grants_without_named_humans(ws, tmp_path):
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    # no authority
    with pytest.raises(qualification.QualificationError):
        qualification.record_decision(run["run_id"], "grant", "")
    # grant needs a second human
    with pytest.raises(qualification.QualificationError):
        qualification.record_decision(run["run_id"], "grant", "Alice")
    # Denials use the same two-human evidence-review rule; a negative decision
    # is still consequential and cannot be a one-person shortcut.
    with pytest.raises(qualification.QualificationError):
        qualification.record_decision(run["run_id"], "deny", "Alice")


def test_cannot_grant_on_nondecisional_evidence(ws, tmp_path):
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT3", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])  # distinct sample remains below RT3 minimum
    with pytest.raises(qualification.QualificationError) as ei:
        qualification.record_decision(run["run_id"], "grant", "Alice", second_human="Bob")
    assert "NON-DECISIONAL" in str(ei.value)


def test_full_cycle_to_grant_and_env_invalidation(ws, tmp_path):
    """M4 exit: evidence -> human grant -> Qualification Record, then an
    environment change invalidates the grant (D7)."""
    from aies import constants, engine, qualification, workspace

    _register(tmp_path)
    # Decisional RT2 evidence uses 30 distinct scenario instruments.
    run = engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    pkg = engine.aggregate(run["run_id"])
    assert pkg["areas"]["CA-05"]["decisional"] is True
    assert pkg["areas"]["CA-05"]["gates_passed"] is True

    record = qualification.record_decision(
        run["run_id"], "grant", "Alice (ROLE-13)", second_human="Bob (ROLE-14)",
        rationale="demonstration grant", **_decision_people(run["run_id"]))
    assert record["status"] == "active"
    assert record["qualification_schema"] == 2
    assert record["subject"]["deployment"] == "demo"
    assert "CA-05" in record["scope"]["areas"]
    assert record["scope"]["role"] == "ROLE-06"
    assert record["scope"]["phases"] == ["P09", "P10"]
    assert record["scope"]["max_risk_tier"] == "RT2"
    assert record["scope"]["framework_version"].startswith("AIES-AESQS-CF-01")
    assert record["scope"]["sponsor"] == "Test Sponsor"
    assert record["scope"]["validity"]["until"].startswith("2027-06")
    assert record["humans"]["protocol"]["satisfied"] is True

    invalid_scope = _decision_people(run["run_id"])
    invalid_scope["phases"] = list(constants.PHASE_NAMES)
    with pytest.raises(qualification.QualificationError):
        qualification.record_decision(
            run["run_id"], "grant", "Alice (ROLE-13)",
            second_human="Bob (ROLE-14)", **invalid_scope)

    # Same environment -> still active.
    same = qualification.verify(record["record_id"],
                                current_fingerprint=pkg["environment_fingerprint"])
    assert same["environment_unchanged"] and same["status"] == "active"

    # Changed environment -> invalidated (D7).
    changed = dict(pkg["environment_fingerprint"])
    changed["fingerprint_hash"] = "sha256:changed"
    result = qualification.verify(record["record_id"], current_fingerprint=changed)
    assert result["environment_unchanged"] is False
    assert result["status"] == "invalidated"
    assert qualification.get_record(record["record_id"])["status"] == "invalidated"


def test_deny_and_revoke(ws, tmp_path):
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    rec = qualification.record_decision(
        run["run_id"], "grant", "Alice", second_human="Bob",
        **_decision_people(run["run_id"]))
    base_path = qualification._records_dir() / f"{rec['record_id']}.json"
    issued_bytes = base_path.read_bytes()
    revoked = qualification.revoke(rec["record_id"], "Alice", "incident in production")
    assert revoked["status"] == "revoked"
    assert revoked["history"][-1]["reason"] == "incident in production"
    assert revoked["history"][-1]["event_type"] == "revoked"
    assert base_path.read_bytes() == issued_bytes  # issued snapshot was not mutated


def test_all_lifecycle_changes_are_append_only_events(ws, tmp_path):
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    first = qualification.record_decision(
        run["run_id"], "grant", "Authority", second_human="Peer",
        **_decision_people(run["run_id"]))
    second = qualification.record_decision(
        run["run_id"], "grant", "Authority", second_human="Peer",
        **_decision_people(run["run_id"]))
    base_path = qualification._records_dir() / f"{first['record_id']}.json"
    issued_bytes = base_path.read_bytes()

    conditional = qualification.record_lifecycle_event(
        first["record_id"], "condition-changed", "Authority", "limit initial use",
        conditions=["human approval before production change"])
    assert conditional["status"] == "conditional"
    with pytest.raises(qualification.QualificationError, match="durable named peer"):
        qualification.record_lifecycle_event(
            first["record_id"], "renewed", "Authority", "annual review complete",
            valid_until="2027-07-15T00:00:00+00:00", evidence_run_id=run["run_id"],
            peer_reviewer="Human peer")
    with pytest.raises(qualification.QualificationError, match="extend the current"):
        qualification.record_lifecycle_event(
            first["record_id"], "renewed", "Authority", "annual review complete",
            valid_until="2027-01-15T00:00:00+00:00", evidence_run_id=run["run_id"],
            peer_reviewer="Human peer", peer_reviewer_id="test-human-peer",
            peer_conflict_free=True)
    renewed = qualification.record_lifecycle_event(
        first["record_id"], "renewed", "Authority", "annual review complete",
        valid_until="2027-07-15T00:00:00+00:00", evidence_run_id=run["run_id"],
        peer_reviewer="Human peer", peer_reviewer_id="test-human-peer",
        peer_conflict_free=True)
    assert renewed["scope"]["validity"]["until"].startswith("2027-07")
    assert qualification.record_lifecycle_event(
        first["record_id"], "suspended", "Authority", "incident review")["status"] == "suspended"
    invalidated = qualification.record_lifecycle_event(
        first["record_id"], "invalidated", "Authority", "material subject change")
    assert invalidated["status"] == "invalidated"
    superseded = qualification.record_lifecycle_event(
        first["record_id"], "superseded", "Authority", "replacement issued",
        superseded_by=second["record_id"])
    assert superseded["status"] == "superseded"
    assert superseded["superseded_by"] == second["record_id"]
    assert base_path.read_bytes() == issued_bytes
    assert [event["event_type"] for event in superseded["history"]] == [
        "issued", "condition-changed", "renewed", "suspended", "invalidated",
        "superseded"]
    event_files = sorted((qualification._records_dir() / "events" /
                          first["record_id"]).glob("*.json"))
    events = [json.loads(path.read_text(encoding="utf-8")) for path in event_files]
    assert all(event["qualification_scope"]["role"] == "ROLE-06" for event in events)
    renewal_event = next(event for event in events if event["event_type"] == "renewed")
    assert renewal_event["changes"]["peer_reviewer_id"] == "test-human-peer"
    assert renewal_event["qualification_scope"]["validity"]["until"].startswith("2027-07")


def test_expired_qualification_is_treated_as_inactive_and_evented(ws, tmp_path, monkeypatch):
    import datetime as dt
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    package = engine.aggregate(run["run_id"])
    record = qualification.record_decision(
        run["run_id"], "grant", "Authority", second_human="Peer",
        **_decision_people(run["run_id"]))

    real_datetime = qualification.datetime.datetime

    class FutureDateTime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            future = cls(2101, 1, 1, tzinfo=dt.timezone.utc)
            return future if tz else future.replace(tzinfo=None)

    monkeypatch.setattr(qualification.datetime, "datetime", FutureDateTime)
    assert qualification.get_record(record["record_id"])["status"] == "expired"
    checked = qualification.verify(
        record["record_id"], current_fingerprint=package["environment_fingerprint"])
    assert checked["status"] == "expired"
    projected = qualification.get_record(record["record_id"])
    assert projected["history"][-1]["event_type"] == "expired"


def test_qualification_report_durable_and_self_contained(ws, tmp_path):
    from aies import engine, qualification, qual_report
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    rec = qualification.record_decision(run["run_id"], "grant", "Alice (ROLE-13)",
                                        second_human="Bob (ROLE-14)",
                                        **_decision_people(run["run_id"]))
    rid = rec["record_id"]
    # Markdown report renders the record and persists durably under reports/.
    md = qual_report.render_markdown(rid)
    assert rid in md and "Scope of the grant" in md and "Alice (ROLE-13)" in md
    path = qual_report.generate(rid, "html")
    assert path.endswith(f"{rid}.html")
    from pathlib import Path
    doc = Path(path).read_text(encoding="utf-8")
    assert doc.startswith("<!doctype html>")
    for needle in ("http://", "https://", "src=", "<link"):
        assert needle not in doc
    listing = qual_report.list_reports()
    assert any(i["record"] == rid for i in listing)


def test_human_records_consideration_of_advisory_and_human_evidence(ws, tmp_path):
    from aies import engine, qualification, qual_report
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human evaluator", "human", 3)
    _score(run["run_id"], "model:reviewer", "model", 3)
    engine.aggregate(run["run_id"])

    rec = qualification.record_decision(
        run["run_id"], "grant", "Alice (ROLE-13)", second_human="Bob (ROLE-14)",
        consider_advisory_review=True, human_evaluation="Human evaluator",
        **_decision_people(run["run_id"], "Human evaluator"))
    consideration = rec["evidence_consideration"]
    assert consideration["automated_advisory_review"]["considered_by_authority"] is True
    assert consideration["human_evaluation"]["evaluator"] == "Human evaluator"
    md = qual_report.render_markdown(rec["record_id"])
    assert "Human evidence consideration" in md
    assert "considered by authority" in md


def test_human_evaluation_attestation_allows_qualitative_review(ws, tmp_path):
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT3", ["CA-05"], repeats=1)
    _score(run["run_id"], "model:reviewer", "model", 3)
    engine.aggregate(run["run_id"])
    rec = qualification.record_decision(
        run["run_id"], "deny", "Alice", human_evaluation="Alice",
        **_decision_people(run["run_id"], "Decision"))
    human = rec["evidence_consideration"]["human_evaluation"]
    assert human["evaluator"] == "Alice"
    assert human["scored_ratings_available"] is False


def test_dashboard_self_contained(ws, tmp_path):
    from aies import dashboard, engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    qualification.record_decision(
        run["run_id"], "grant", "Alice", second_human="Bob",
        **_decision_people(run["run_id"]))
    doc = dashboard.render_dashboard()
    assert doc.startswith("<!doctype html>")
    for needle in ("http://", "https://", "src=", "<link"):
        assert needle not in doc
    assert "Qualification records (1)" in doc

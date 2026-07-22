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
    from aies import rating, workspace
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    sheet["rater"] = {"name": rater, "kind": kind}
    for item in sheet["items"]:
        item["scores"] = {d: score for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
        if score <= 2:  # findings are mandatory for low scores (AIES-AESQS-ER-01)
            item["findings"] = [{"dimension": "EV1", "score": score,
                                 "finding": "synthetic low score for test"}]
    rating.ingest_scores(run_id, sheet)


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


def test_cannot_grant_on_nondecisional_evidence(ws, tmp_path):
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT2", ["CA-05"], repeats=1)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])  # only 4 items < 30 -> non-decisional
    with pytest.raises(qualification.QualificationError) as ei:
        qualification.record_decision(run["run_id"], "grant", "Alice", second_human="Bob")
    assert "NON-DECISIONAL" in str(ei.value)


def test_full_cycle_to_grant_and_env_invalidation(ws, tmp_path):
    """M4 exit: evidence -> human grant -> Qualification Record, then an
    environment change invalidates the grant (D7)."""
    from aies import engine, qualification, workspace

    _register(tmp_path)
    # Decisional at RT1 needs >= 20 scored items; CA-05 has 2 RT1 scenarios,
    # so 2 x 10 repeats = 20.
    run = engine.start_qualification("demo", "research", "RT1", ["CA-05"], repeats=10)
    _score(run["run_id"], "Human", "human", 3)
    pkg = engine.aggregate(run["run_id"])
    assert pkg["areas"]["CA-05"]["decisional"] is True   # 20 >= RT1 min 20
    assert pkg["areas"]["CA-05"]["gates_passed"] is True

    record = qualification.record_decision(
        run["run_id"], "grant", "Alice (ROLE-13)", second_human="Bob (ROLE-14)",
        rationale="demonstration grant")
    assert record["status"] == "active"
    assert record["subject"]["deployment"] == "demo"
    assert "CA-05" in record["scope"]["areas"]

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
    run = engine.start_qualification("demo", "research", "RT1", ["CA-05"], repeats=10)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    rec = qualification.record_decision(run["run_id"], "grant", "Alice", second_human="Bob")
    revoked = qualification.revoke(rec["record_id"], "Alice", "incident in production")
    assert revoked["status"] == "revoked"
    assert revoked["history"][-1]["reason"] == "incident in production"


def test_qualification_report_durable_and_self_contained(ws, tmp_path):
    from aies import engine, qualification, qual_report
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT1", ["CA-05"], repeats=10)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    rec = qualification.record_decision(run["run_id"], "grant", "Alice (ROLE-13)",
                                        second_human="Bob (ROLE-14)")
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
    run = engine.start_qualification("demo", "research", "RT1", ["CA-05"], repeats=10)
    _score(run["run_id"], "Human evaluator", "human", 3)
    _score(run["run_id"], "model:reviewer", "model", 3)
    engine.aggregate(run["run_id"])

    rec = qualification.record_decision(
        run["run_id"], "grant", "Alice (ROLE-13)", second_human="Bob (ROLE-14)",
        consider_advisory_review=True, human_evaluation="Human evaluator")
    consideration = rec["evidence_consideration"]
    assert consideration["automated_advisory_review"]["considered_by_authority"] is True
    assert consideration["human_evaluation"]["evaluator"] == "Human evaluator"
    md = qual_report.render_markdown(rec["record_id"])
    assert "Human evidence consideration" in md
    assert "considered by authority" in md


def test_human_evaluation_attestation_requires_human_scores(ws, tmp_path):
    from aies import engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT1", ["CA-05"], repeats=10)
    _score(run["run_id"], "model:reviewer", "model", 3)
    engine.aggregate(run["run_id"])
    with pytest.raises(qualification.QualificationError, match="human-scored ratings"):
        qualification.record_decision(
            run["run_id"], "deny", "Alice", human_evaluation="Alice")


def test_dashboard_self_contained(ws, tmp_path):
    from aies import dashboard, engine, qualification
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT1", ["CA-05"], repeats=10)
    _score(run["run_id"], "Human", "human", 3)
    engine.aggregate(run["run_id"])
    qualification.record_decision(run["run_id"], "grant", "Alice", second_human="Bob")
    doc = dashboard.render_dashboard()
    assert doc.startswith("<!doctype html>")
    for needle in ("http://", "https://", "src=", "<link"):
        assert needle not in doc
    assert "Qualification records (1)" in doc

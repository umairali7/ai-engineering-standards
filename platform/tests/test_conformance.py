"""Conformance-claim mechanism (Task #7): a statement's structure is
validated, evidence-backed claims are verified against Qualification
Records, and the checker is honest about what it cannot verify."""

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


def _grant(tmp_path):
    from aies import engine, qualification, rating, workspace
    import json
    _register(tmp_path)
    run = engine.start_journey("demo", "research", "JOURNEY-01", repeats=1) \
        if False else engine.start_qualification("demo", "research", "RT2", ["CA-05"], repeats=1)
    sheet = json.loads((workspace.run_dir(run["run_id"]) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Alice (ROLE-13)", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run["run_id"], sheet)
    engine.aggregate(run["run_id"])
    return qualification.record_decision(run["run_id"], "grant", "Alice (ROLE-13)",
                                         second_human="Bob (ROLE-14)")


def test_template_and_requirements():
    from aies import conformance
    tpl = conformance.template("adopter")
    assert tpl["conformance_statement"]["class"] == "adopter"
    assert conformance.ENFORCED_REQUIREMENTS  # non-empty traceability map


def test_invalid_statement_rejected(ws, tmp_path):
    from aies import conformance
    bad = tmp_path / "s.yaml"
    bad.write_text(yaml.safe_dump({"conformance_statement": {
        "claimant": "", "class": "bogus", "assurance": "nope", "claims": []}}),
        encoding="utf-8")
    with pytest.raises(conformance.ConformanceError):
        conformance.check(bad)


def test_evidence_backed_claim_verified_against_record(ws, tmp_path):
    from aies import conformance
    rec = _grant(tmp_path)
    stmt = tmp_path / "s.yaml"
    stmt.write_text(yaml.safe_dump({"conformance_statement": {
        "claimant": "Fieldstone", "aies_version": "v0.4.0", "class": "adopter",
        "assurance": "evidence-backed", "date": "2026-07-15",
        "claims": [
            {"statement": "demo is qualified for CA-05 at RT1.",
             "evidence": {"qualification_record": rec["record_id"]}},
            {"statement": "We run human gates per AIES-AEOS-HO-01.", "evidence": {}},
        ]}}), encoding="utf-8")
    report = conformance.check(stmt)
    verdicts = {c["verdict"] for c in report["claims"]}
    assert "verified" in verdicts and "self-asserted" in verdicts
    assert report["summary"]["substantiated"] is True
    md = conformance.render_markdown(report)
    assert "SUBSTANTIATED" in md


def test_missing_record_makes_statement_unsupported(ws, tmp_path):
    from aies import conformance
    stmt = tmp_path / "s.yaml"
    stmt.write_text(yaml.safe_dump({"conformance_statement": {
        "claimant": "Acme", "aies_version": "v0.4.0", "class": "adopter",
        "assurance": "evidence-backed",
        "claims": [{"statement": "qualified", "evidence":
                    {"qualification_record": "QUAL-2026-999"}}]}}), encoding="utf-8")
    report = conformance.check(stmt)
    assert report["claims"][0]["verdict"] == "unsupported"
    assert report["summary"]["substantiated"] is False


def test_revoked_record_does_not_substantiate(ws, tmp_path):
    from aies import conformance, qualification
    rec = _grant(tmp_path)
    qualification.revoke(rec["record_id"], "Alice", "incident")
    stmt = tmp_path / "s.yaml"
    stmt.write_text(yaml.safe_dump({"conformance_statement": {
        "claimant": "Fieldstone", "aies_version": "v0.4.0", "class": "adopter",
        "assurance": "evidence-backed",
        "claims": [{"statement": "qualified",
                    "evidence": {"qualification_record": rec["record_id"]}}]}}),
        encoding="utf-8")
    report = conformance.check(stmt)
    assert report["claims"][0]["verdict"] == "unsupported"      # revoked != live grant
    assert "revoked" in report["claims"][0]["detail"]

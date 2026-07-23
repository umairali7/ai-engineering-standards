"""Versioned artifact envelopes (STABILITY/COMPATIBILITY).

The Evidence Package and the Canonical Assessment Result are versioned,
platform-owned contracts. These are GOLDEN tests: they pin the top-level shape
so a field removal/rename fails the build (additive change = add the key here and
bump the schema per COMPATIBILITY.md). They also lock the engine-version vs
decision-semantics-version split, and prove Evidence is versioned independently
of the Result (it can be replayed through a future engine)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# The frozen top-level keys of each artifact. Adding a key is a deliberate,
# reviewed change: update this set AND bump the schema constant.
EVIDENCE_PACKAGE_KEYS = {
    "run_id", "kind", "evidence_schema", "grant_status", "subject", "model", "profile",
    "profile_version", "risk_tier", "subject_kind", "suite_versions",
    "environment_fingerprint", "areas", "raters", "rater_kinds", "aggregated_at",
    "admitted_raters", "admitted_rater_kinds", "rating_admission",
    "sample_adequacy_policy", "rating_observations", "evidence_items",
}

RESULT_KEYS = {
    "kind", "result_schema", "outcome", "assessment", "subject", "risk_tier",
    "metadata", "evidence", "decisions", "diagnostics", "analytics",
}

RESULT_METADATA_KEYS = {
    "assessment_id", "assessment_version", "assessment_schema", "profile",
    "profile_version", "platform_version", "decision_engine_version",
    "decision_semantics_version", "aies_version", "evidence_schema", "model",
    "model_checksum", "runtime", "environment_fingerprint", "suite_versions",
    "run_id", "aggregated_at", "decided_at",
}

WORKSPACE_OVERVIEW_KEYS = {
    "kind", "schema_version", "platform_version", "authority", "counts",
    "deployments", "runs", "qualifications", "assessments", "support", "links",
    "limitations",
}

RUN_VIEW_KEYS = {
    "kind", "schema_version", "platform_version", "authority", "run_id",
    "state", "run_purpose", "subject", "scope", "execution", "products",
    "artifacts", "links", "limitations",
}

REPORT_VIEW_KEYS = {
    "kind", "schema_version", "platform_version", "authority", "run_id",
    "run_purpose", "formal_qualification_requested", "title", "subject",
    "scope", "status", "engineering_evaluation", "grounding_diagnostics",
    "human_review", "qualification", "environment", "areas",
    "engineering_capability_matrix", "provenance", "artifacts", "limitations",
}


def _result(evidence_schema=1, profile_version="1.0.0"):
    from aies import decision
    pkg = {"run_id": "r", "kind": "evidence-package", "evidence_schema": evidence_schema,
           "grant_status": "no grant", "profile": "coder", "profile_version": profile_version,
           "risk_tier": "RT2", "subject_kind": "ai", "suite_versions": {},
           "subject": {"id": "m", "kind": "ai_deployment", "display_name": "m",
                       "executor_kind": "deployment"},
           "model": {"registry_id": "m", "checksum": "sha256:x"},
           "environment_fingerprint": {"runtime": {"id": "mock"}, "fingerprint_hash": "sha256:fp"},
           "raters": [], "rater_kinds": [], "aggregated_at": "2026-07-18T00:00:00Z",
           "areas": {"CA-05": {"decisional": True, "gates_passed": True,
                               "ev3_hard_fail": False, "cl": "CL3", "n_scored": 42,
                               "min_sample": 30, "aggregate_A": 3.4,
                               "gates": [{"dimension": d, "passed": True}
                                         for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")]}}}
    assessment = {"id": "t", "version": "1.0.0", "schema": 1, "profile": "coder",
                  "competencies": [{"area": "CA-05", "requirement": "mandatory"}]}
    return decision.decide(pkg, assessment)


def test_result_envelope_is_versioned_and_shape_is_pinned():
    from aies import decision
    res = _result()
    assert res["result_schema"] == decision.RESULT_SCHEMA == 1
    assert set(res.keys()) == RESULT_KEYS, "result envelope shape drifted"
    assert set(res["metadata"].keys()) == RESULT_METADATA_KEYS, "result metadata drifted"


def test_engine_version_and_semantics_version_are_distinct_fields():
    from aies import decision
    m = _result()["metadata"]
    # engine version = the software build that decided
    assert m["decision_engine_version"] == decision.__version__
    # semantics version = which AESQS decision policy was applied (NOT the build)
    assert m["decision_semantics_version"] == decision.DECISION_SEMANTICS_VERSION == "1.0"
    # they answer different questions and are kept as separate fields
    assert "decision_engine_version" in m and "decision_semantics_version" in m


def test_result_records_the_evidence_schema_it_decided_over():
    # Evidence is versioned independently; the result references that version so
    # a replay through a future engine is traceable to the evidence generation.
    assert _result(evidence_schema=1)["metadata"]["evidence_schema"] == 1
    assert _result(evidence_schema=7)["metadata"]["evidence_schema"] == 7


def test_evidence_package_envelope_shape(ws_run):
    from aies import workspace, constants
    pkg = workspace.read_json(workspace.run_dir(ws_run) / "evidence-package.json")
    assert pkg["evidence_schema"] == constants.EVIDENCE_SCHEMA == 5
    assert set(pkg.keys()) == EVIDENCE_PACKAGE_KEYS, "evidence-package envelope drifted"
    assert pkg["evidence_items"]["resolution_policy"] == "one-resolved-score-per-response-v1"
    assert pkg["evidence_items"]["resolved"] == pkg["areas"]["CA-05"]["n_scored"]
    assert pkg["profile_version"] == "1.0.0"     # captured at run time
    assert pkg["subject"]["id"] == "cand"
    assert pkg["subject"]["kind"] == "ai_deployment"


def test_engineering_evaluation_summary_is_separately_versioned(ws_run):
    from aies import evaluation

    summary = evaluation.summarize(ws_run)
    assert summary["kind"] == "engineering-evaluation-summary"
    assert summary["evaluation_schema"] == evaluation.EVALUATION_SCHEMA == 1
    assert summary["status"] == "complete"
    assert summary["human_evaluation"] == {
        "status": "reviewed", "optional": True, "evaluator": "R"}
    assert summary["areas"]["CA-05"]["completed_by"] == "human"


def test_read_only_consumer_view_envelopes_are_pinned(ws_run):
    from aies import overview, report_view, run_view

    workspace_summary = overview.build()
    assert workspace_summary["schema_version"] == overview.SCHEMA_VERSION == 1
    assert set(workspace_summary) == WORKSPACE_OVERVIEW_KEYS

    run_summary = run_view.build(ws_run)
    assert run_summary["schema_version"] == run_view.SCHEMA_VERSION == 1
    assert set(run_summary) == RUN_VIEW_KEYS
    assert run_summary["authority"] == "informational-read-only"

    report_summary = report_view.build(ws_run)
    assert report_summary["schema_version"] == report_view.SCHEMA_VERSION == 1
    assert set(report_summary) == REPORT_VIEW_KEYS
    assert report_summary["authority"] == "informational-read-only"
    assert report_summary["areas"][0]["code"] == "CA-05"
    assert report_summary["areas"][0]["dimensions"][0]["sources"]["human"]["n"] > 0


import pytest  # noqa: E402


@pytest.fixture()
def ws_run(tmp_path, monkeypatch):
    import json
    import yaml
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import registry, engine, rating, workspace
    e = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
         "context_window": 8192, "provenance": {"source": "x", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(e), encoding="utf-8"); registry.add(p)
    manifest = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)
    run_id = manifest["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "R", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)
    return run_id

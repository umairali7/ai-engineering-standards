"""Eval-import: bring external EV-scored results into a run as automated
ratings, subject to the same aggregation/gate as any rater. Malformed items
are skipped and reported, never fabricated."""

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


def _register(tmp_path):
    from aies import registry
    entry = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "cand.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def _run(tmp_path):
    from aies import engine
    _register(tmp_path)
    return engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)["run_id"]


def _sid(run_id):
    from aies import workspace
    resp = sorted((workspace.run_dir(run_id) / "responses").glob("*.json"))
    rec = json.loads(resp[0].read_text(encoding="utf-8"))
    return rec["scenario_id"], rec["repeat"]


def test_import_ingests_ev_scores_as_automated_ratings(ws, tmp_path):
    from aies import diagnostics, evalimport, engine
    run_id = _run(tmp_path)
    sid, rep = _sid(run_id)
    f = tmp_path / "eval.json"
    f.write_text(json.dumps({"source": "inspect:my-task", "items": [
        {"scenario_id": sid, "repeat": rep,
         "scores": {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")},
         "grounding_diagnostics": {
             "grounding_assessed": True, "unsupported_assertions": 1,
             "fabricated_apis_or_entities": 0,
             "invalid_citations_or_provenance": 0,
             "false_success_or_test_claims": 0,
             "appropriate_abstention": None,
             "notes": ["one unsupported assertion"]}}
    ]}), encoding="utf-8")

    summary = evalimport.import_eval(run_id, str(f))
    assert summary["imported"] == 1 and summary["skipped"] == 0
    assert summary["source"] == "import:inspect:my-task"

    pkg = engine.aggregate(run_id)
    assert pkg["rater_kinds"] == ["automated"]        # ingested as a tool rater
    assert any("import:inspect:my-task" in r for r in pkg["raters"])
    observed = diagnostics.summarize(run_id)["sources"]["automated"]
    assert observed["category_counts"]["unsupported_assertions"] == 1
    assert observed["observed_grounding_reliability_percent"] == 0.0
    # The imported reviewer and its diagnostic remain advisory; neither can
    # silently enter the formal qualification aggregate.
    assert pkg["areas"]["CA-05"]["n_scored"] == 0
    assert pkg["areas"]["CA-05"]["dimensions"] == {}


def test_malformed_items_are_skipped_not_fabricated(ws, tmp_path):
    from aies import evalimport, rating
    run_id = _run(tmp_path)
    sid, rep = _sid(run_id)
    f = tmp_path / "eval.json"
    f.write_text(json.dumps({"items": [
        {"scenario_id": sid, "repeat": rep,               # good
         "scores": {d: 2 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")},
         "findings": ["thin"],
         "grounding_diagnostics": {"grounding_assessed": "not-a-boolean"}},
        {"scenario_id": "SC-BAD", "scores": {"EV1": 3}},   # missing dims -> skip
        {"scenario_id": "SC-OOR", "repeat": 1,             # out of range -> skip
         "scores": {d: 9 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}},
    ]}), encoding="utf-8")

    summary = evalimport.import_eval(run_id, str(f), source="tool")
    assert summary["imported"] == 1 and summary["skipped"] == 2
    assert summary["diagnostics_unavailable"] == 1
    assert rating.collect_ratings(run_id)[0]["grounding_diagnostics"] is None


def test_no_importable_items_errors(ws, tmp_path):
    from aies import evalimport
    run_id = _run(tmp_path)
    f = tmp_path / "eval.json"
    f.write_text(json.dumps({"items": [{"scenario_id": "x", "scores": {"EV1": 1}}]}),
                 encoding="utf-8")
    with pytest.raises(evalimport.EvalImportError, match="no importable items"):
        evalimport.import_eval(run_id, str(f))

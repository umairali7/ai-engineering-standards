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
    from aies import evalimport, engine
    run_id = _run(tmp_path)
    sid, rep = _sid(run_id)
    f = tmp_path / "eval.json"
    f.write_text(json.dumps({"source": "inspect:my-task", "items": [
        {"scenario_id": sid, "repeat": rep,
         "scores": {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}}
    ]}), encoding="utf-8")

    summary = evalimport.import_eval(run_id, str(f))
    assert summary["imported"] == 1 and summary["skipped"] == 0
    assert summary["source"] == "import:inspect:my-task"

    pkg = engine.aggregate(run_id)
    assert pkg["rater_kinds"] == ["automated"]        # ingested as a tool rater
    assert any("import:inspect:my-task" in r for r in pkg["raters"])


def test_malformed_items_are_skipped_not_fabricated(ws, tmp_path):
    from aies import evalimport
    run_id = _run(tmp_path)
    sid, rep = _sid(run_id)
    f = tmp_path / "eval.json"
    f.write_text(json.dumps({"items": [
        {"scenario_id": sid, "repeat": rep,               # good
         "scores": {d: 2 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")},
         "findings": ["thin"]},
        {"scenario_id": "SC-BAD", "scores": {"EV1": 3}},   # missing dims -> skip
        {"scenario_id": "SC-OOR", "repeat": 1,             # out of range -> skip
         "scores": {d: 9 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}},
    ]}), encoding="utf-8")

    summary = evalimport.import_eval(run_id, str(f), source="tool")
    assert summary["imported"] == 1 and summary["skipped"] == 2


def test_no_importable_items_errors(ws, tmp_path):
    from aies import evalimport
    run_id = _run(tmp_path)
    f = tmp_path / "eval.json"
    f.write_text(json.dumps({"items": [{"scenario_id": "x", "scores": {"EV1": 1}}]}),
                 encoding="utf-8")
    with pytest.raises(evalimport.EvalImportError, match="no importable items"):
        evalimport.import_eval(run_id, str(f))

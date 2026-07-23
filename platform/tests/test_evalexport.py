"""Eval export: write a run's responses+scores to a generic eval-log JSON that
round-trips back through `aies import`."""

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


def _register(tmp_path, mid="cand"):
    from aies import registry
    entry = {"id": mid, "family": "demo", "runtime": "mock", "model": mid,
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / f"{mid}.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(p)


def _scored_run(tmp_path):
    from aies import engine, rating, workspace
    run = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)["run_id"]
    sheet = json.loads((workspace.run_dir(run) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Rater", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
        it["grounding_diagnostics"] = {
            "grounding_assessed": True, "unsupported_assertions": 0,
            "fabricated_apis_or_entities": 0,
            "invalid_citations_or_provenance": 0,
            "false_success_or_test_claims": 0,
            "appropriate_abstention": None, "notes": []}
    rating.ingest_scores(run, sheet)
    return run


def test_export_carries_prompt_response_and_scores(ws, tmp_path):
    from aies import evalexport
    _register(tmp_path)
    run = _scored_run(tmp_path)
    data = evalexport.export_run(run)
    assert data["source"] == f"aies:{run}" and data["items"]
    it = data["items"][0]
    assert it["prompt"] and it["response"] and it["scores"]
    assert set(it["scores"]) == {"EV1", "EV2", "EV3", "EV4", "EV5", "EV6"}
    assert it["grounding_diagnostics"]["grounding_assessed"] is True
    assert it["ratings"] and it["ratings"][0]["rater_kind"] == "human"
    assert it["ratings"][0]["grounding_diagnostics"]["diagnostic_schema"] == 2


def test_export_roundtrips_through_import(ws, tmp_path):
    from aies import evalexport, evalimport, engine, workspace
    _register(tmp_path)
    src = _scored_run(tmp_path)
    exported = evalexport.write_export(src)

    # a fresh run over the same suite, unscored, then import the exported scores
    dst = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)["run_id"]
    summary = evalimport.import_eval(dst, exported, source="roundtrip")
    assert summary["imported"] == summary["items"] and summary["skipped"] == 0
    pkg = engine.aggregate(dst)
    assert pkg["rater_kinds"] == ["automated"]
    # same scenarios scored in both runs
    n_src = len(list((workspace.run_dir(src) / "responses").glob("*.json")))
    assert summary["imported"] == n_src

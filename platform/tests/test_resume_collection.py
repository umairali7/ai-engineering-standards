"""Resumable partial collection: fill only the missing responses of a
partially-collected run, without re-running what already succeeded."""

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


def test_resume_fills_only_missing(ws, tmp_path):
    from aies import engine, workspace

    _register(tmp_path)
    run = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)
    run_id = run["run_id"]
    resp_dir = workspace.run_dir(run_id) / "responses"
    all_resp = sorted(resp_dir.glob("*.json"))
    full = len(all_resp)
    assert full >= 5

    # simulate a partial collection: delete 3 responses and capture the mtimes
    # of the survivors so we can prove they are NOT rewritten.
    for p in all_resp[:3]:
        p.unlink()
    survivors = {p.name: p.stat().st_mtime_ns for p in resp_dir.glob("*.json")}
    assert len(survivors) == full - 3

    summary = engine.resume_collection(run_id)
    assert summary["filled"] == 3
    assert summary["responses"] == full           # back to the full set
    # survivors untouched (not re-run)
    for name, mtime in survivors.items():
        assert (resp_dir / name).stat().st_mtime_ns == mtime

    # scoresheet rebuilt to cover the full set again
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    assert len(sheet["items"]) == full


def test_resume_noop_when_complete(ws, tmp_path):
    from aies import engine, workspace
    _register(tmp_path)
    run = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)
    n = len(list((workspace.run_dir(run["run_id"]) / "responses").glob("*.json")))
    summary = engine.resume_collection(run["run_id"])
    assert summary["filled"] == 0 and summary["responses"] == n


def test_resume_refuses_on_missing_run(ws, tmp_path):
    from aies import engine
    with pytest.raises(engine.EngineError, match="no run"):
        engine.resume_collection("run-does-not-exist")

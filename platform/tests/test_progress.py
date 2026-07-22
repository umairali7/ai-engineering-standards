"""Detailed durable and CLI-visible run progress."""

from __future__ import annotations

import io
import json
import sys
from argparse import Namespace
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_progress_snapshot_has_operational_detail(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import progress, workspace

    seen = []
    event = progress.update("run-1", "response-collection", 4, 10,
                            current="SC-CA05-004-r1", failures=1,
                            activity="Executing task", message="collecting",
                            callback=seen.append)
    assert event["percent"] == 40.0
    assert event["elapsed_seconds"] >= 0
    assert event["total_elapsed_seconds"] >= event["elapsed_seconds"]
    assert event["stage_started_at"] and event["stage_started_epoch"]
    assert "throughput_per_second" in event and "eta_seconds" in event
    assert event["resumable"] is True and event["failures"] == 1
    assert event["current_index"] == 5
    assert seen == [event]
    stored = json.loads((workspace.run_dir("run-1") / "progress.json").read_text())
    assert stored == event


def test_progress_rate_resets_for_each_stage(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import progress

    first = progress.update("run-1", "response-collection", 1, 10)
    second = progress.update("run-1", "judge-review", 0, 10)
    assert second["started_at"] == first["started_at"]
    assert second["stage_started_at"] != ""
    assert second["stage_started_epoch"] >= first["stage_started_epoch"]
    assert second["elapsed_seconds"] <= second["total_elapsed_seconds"]


def test_runs_progress_cli_exposes_durable_detail(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import cli, progress

    progress.update("run-1", "judge-review", 3, 10, current="batch-3")
    assert cli.cmd_runs(Namespace(runs_cmd="progress", run="run-1", json=False)) == 0
    output = capsys.readouterr().out
    for label in ("stage", "progress", "stage time", "total time", "throughput",
                  "ETA", "failures", "current", "resumable"):
        assert label in output


def test_cli_progress_is_detailed_and_throttles_redirected_logs():
    from aies.progress import CliProgress

    stream = io.StringIO()
    render = CliProgress(stream)
    base = {"stage": "judge-review", "status": "running", "completed": 0,
            "total": 100, "percent": 0.0, "elapsed_seconds": 1.0,
            "throughput_per_second": 1.0, "eta_seconds": 100.0,
            "failures": 0, "current": "batch-1", "current_index": 1,
            "activity": "Scoring task"}
    render(base)
    render({**base, "completed": 1, "percent": 1.0})  # same 5% bucket
    render({**base, "completed": 5, "percent": 5.0, "current": "batch-2"})
    render({**base, "completed": 100, "percent": 100.0,
            "status": "completed", "eta_seconds": 0.0})
    output = stream.getvalue()
    assert output.count("[judge-review]") == 3
    assert "stage elapsed" in output and "total elapsed" in output
    assert "rate" in output and "ETA" in output
    assert "Scoring task 1/100: batch-1" in output
    assert "batch-2" in output


def test_cli_progress_renders_dynamic_parallel_active_tasks():
    from aies.progress import CliProgress

    stream = io.StringIO()
    render = CliProgress(stream)
    render({"stage": "response-collection", "status": "running",
            "completed": 3, "total": 30, "percent": 10.0,
            "elapsed_seconds": 2.0, "total_elapsed_seconds": 4.0,
            "throughput_per_second": 1.5, "eta_seconds": 18.0,
            "failures": 0, "current": "", "current_index": None,
            "activity": "Executing task", "parallelism": 8,
            "active_count": 2,
            "active_tasks": ["Task 4/30 · API Design", "Task 5/30 · Testing"]})
    output = stream.getvalue()
    assert "Active tasks 2/8" in output
    assert "Task 4/30 · API Design" in output
    assert "Task 5/30 · Testing" in output


def test_engine_persists_completed_collection_progress(tmp_path, monkeypatch):
    import time

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import engine, registry, workspace
    from aies.adapters import mock as mockmod

    original_generate = mockmod.MockAdapter.generate

    def slow_generate(self, request):
        time.sleep(0.03)
        return original_generate(self, request)

    monkeypatch.setattr(mockmod.MockAdapter, "generate", slow_generate)

    entry = {"id": "progress-demo", "family": "demo", "runtime": "mock",
             "model": "progress-demo", "context_window": 8192,
             "provenance": {"source": "synthetic",
                            "checksum": "sha256:" + "0" * 64}}
    source = tmp_path / "deployment.yaml"
    source.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(source)
    seen = []
    manifest = engine.start_qualification(
        "progress-demo", "coder", "RT1", ["CA-05"], workers=2,
        progress_callback=seen.append)
    state = workspace.read_json(workspace.run_dir(manifest["run_id"]) / "progress.json")
    assert state["stage"] == "response-collection"
    assert state["status"] == "completed"
    assert state["completed"] == state["total"] > 0
    assert manifest["status"] == "responses-collected"
    assert seen[0]["completed"] == 0 and seen[-1]["status"] == "completed"
    executing = [event for event in seen if event.get("activity") == "Executing task"]
    assert executing and executing[0]["current_index"] == 1
    assert " — " in executing[0]["current"] and "[SC-" in executing[0]["current"]
    assert max(event.get("active_count", 0) for event in seen) == 2
    assert all(event.get("parallelism") == 2 for event in executing)
    assert any("Task 1/" in task for event in executing
               for task in event.get("active_tasks", []))

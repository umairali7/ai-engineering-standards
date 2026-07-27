"""Detailed durable and CLI-visible run progress."""

from __future__ import annotations

import io
import json
import re
import sys
import time
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


def test_standalone_operation_resets_clocks_and_excludes_reused_work(
        tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import progress

    epochs = iter((100.0, 500.0, 510.0))
    monkeypatch.setattr(progress.time, "time", lambda: next(epochs))
    progress.update("run-1", "response-collection", 147, 147)
    started = progress.update(
        "run-1", "judge-review", 14, 147, reset_operation=True)
    advanced = progress.update("run-1", "judge-review", 21, 147)

    assert started["elapsed_seconds"] == 0
    assert started["total_elapsed_seconds"] == 0
    assert started["stage_initial_completed"] == 14
    assert started["throughput_per_second"] == 0
    assert advanced["elapsed_seconds"] == 10
    assert advanced["total_elapsed_seconds"] == 10
    assert advanced["measured_completed"] == 7
    assert advanced["throughput_per_second"] == 0.7


def test_slow_rate_uses_items_per_minute():
    from aies.progress import format_rate

    assert format_rate(0) == "calculating"
    assert format_rate(0.01) == "0.60 items/min"
    assert format_rate(0.5) == "0.50 items/s"


def test_runs_progress_cli_exposes_durable_detail(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import cli, progress

    progress.update("run-1", "judge-review", 3, 10, current="batch-3")
    assert cli.cmd_runs(Namespace(runs_cmd="progress", run="run-1", json=False)) == 0
    output = capsys.readouterr().out
    for label in ("stage", "progress", "stage time", "command time", "throughput",
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
    assert "stage elapsed" in output and "command elapsed" in output
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
    assert "(+1 more)" in output


def test_cli_progress_distinguishes_batches_from_workers():
    from aies.progress import CliProgress

    stream = io.StringIO()
    render = CliProgress(stream)
    render({
        "stage": "judge-review", "status": "running",
        "completed": 14, "total": 147, "percent": 9.5,
        "elapsed_seconds": 1263.0, "total_elapsed_seconds": 1263.0,
        "throughput_per_second": 0.011, "eta_seconds": 12000.0,
        "eta_basis": "observed-throughput", "failures": 0,
        "measured_completed": 14,
        "current": "", "current_index": None, "parallelism": 1,
        "active_unit": "batch",
        "active_tasks": [
            "Batch 3/21 · 7 items · Tasks 15–21/147 · API Design"],
    })
    output = stream.getvalue()
    assert "rate 0.66 items/min" in output
    assert "Active batches 1/1" in output
    assert "Batch 3/21 · 7 items · Tasks 15–21/147" in output
    assert output.count("projected serial judge time exceeds 1 hour") == 1


def test_cli_progress_heartbeat_refreshes_elapsed_time_during_long_call():
    from aies.progress import CliProgress

    class TtyStream(io.StringIO):
        def isatty(self):
            return True

    stream = TtyStream()
    render = CliProgress(
        stream, refresh_interval=0.05, terminal_width=240)
    render({"stage": "response-collection", "status": "running",
            "completed": 0, "total": 30, "percent": 0.0,
            "elapsed_seconds": 0.0, "total_elapsed_seconds": 0.0,
            "throughput_per_second": 0.0, "eta_seconds": None,
            "failures": 0, "current": "", "current_index": None,
            "activity": "Executing task", "parallelism": 2,
            "active_tasks": ["Task 1/30 · API Design", "Task 2/30 · Testing"]})
    time.sleep(0.13)
    render({"stage": "response-collection", "status": "completed",
            "completed": 30, "total": 30, "percent": 100.0,
            "elapsed_seconds": 0.2, "total_elapsed_seconds": 0.2,
            "throughput_per_second": 150.0, "eta_seconds": 0.0,
            "failures": 0, "current": "", "current_index": None,
            "activity": "", "parallelism": 2, "active_tasks": []})
    output = stream.getvalue()
    assert output.count("[response-collection]") >= 3
    assert "ETA calculating (first completion)" in output
    assert "\033[2K" in output


def test_cli_progress_bounds_tty_line_to_terminal_width():
    from aies.progress import CliProgress

    class TtyStream(io.StringIO):
        def isatty(self):
            return True

    stream = TtyStream()
    render = CliProgress(stream, terminal_width=100)
    render({"stage": "response-collection", "status": "running",
            "completed": 0, "total": 147, "percent": 0.0,
            "elapsed_seconds": 0.0, "total_elapsed_seconds": 0.0,
            "throughput_per_second": 0.0, "eta_seconds": None,
            "failures": 0, "current": "", "current_index": None,
            "activity": "Executing task", "parallelism": 4,
            "active_tasks": ["Task 1/147 · " + "long task " * 30]})
    visible_lines = [
        re.sub(r"\x1b\[[0-9;]*m", "", line)
        for line in stream.getvalue().splitlines()
        if line.replace("\033[2K", "").strip()
    ]
    assert visible_lines
    assert all(len(line.replace("\033[2K", "")) <= 100
               for line in visible_lines)
    assert any(line.endswith("…") for line in visible_lines)


def test_interactive_progress_lists_all_active_tasks_in_stable_order():
    from aies.progress import CliProgress

    class TtyStream(io.StringIO):
        def isatty(self):
            return True

    stream = TtyStream()
    render = CliProgress(stream, terminal_width=240)
    render({
        "stage": "response-collection", "status": "running",
        "completed": 4, "total": 30, "percent": 13.3,
        "elapsed_seconds": 60.0, "total_elapsed_seconds": 60.0,
        "throughput_per_second": 0.067, "eta_seconds": 388.0,
        "eta_basis": "observed-throughput", "failures": 0,
        "current": "", "current_index": None, "parallelism": 4,
        "active_tasks": [
            "Task 8/30 · Documentation",
            "Task 6/30 · API Design",
            "Task 7/30 · Testing",
        ],
    })
    output = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", stream.getvalue())
    assert "Active tasks 3/4" in output
    assert output.index("Task 6/30") < output.index("Task 7/30")
    assert output.index("Task 7/30") < output.index("Task 8/30")
    assert output.count("RUNNING · Task ") == 3


def test_declared_eta_is_available_before_first_completion(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import progress

    event = progress.update(
        "run-declared", "response-collection", 0, 20, parallelism=4,
        estimated_seconds_per_request=10)
    assert event["eta_seconds"] == 50.0
    assert event["eta_basis"] == "deployment-declaration"


def test_multi_area_task_label_uses_run_wide_ordinal():
    from aies.engine import _global_task_label

    assert _global_task_label(
        "Task 1/30 · Testing — Exercise", 57, 147
    ) == "Task 58/147 · Testing — Exercise"


def test_progress_durations_are_human_readable():
    from aies.progress import format_duration

    assert format_duration(42) == "42s"
    assert format_duration(125) == "2m 5s"
    assert format_duration(10949) == "3h 2m"


def test_interactive_progress_uses_semantic_color(monkeypatch):
    from aies.progress import CliProgress

    class TtyStream(io.StringIO):
        def isatty(self):
            return True

    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm-256color")
    stream = TtyStream()
    render = CliProgress(stream, terminal_width=240)
    render({"stage": "judge-review", "status": "running",
            "completed": 4, "total": 30, "percent": 13.3,
            "elapsed_seconds": 60.0, "total_elapsed_seconds": 60.0,
            "throughput_per_second": 0.067, "eta_seconds": 388.0,
            "eta_basis": "observed-throughput", "failures": 1,
            "current": "", "current_index": None,
            "activity": "Scoring task", "parallelism": 4,
            "active_tasks": ["Task 5/30 · Security Review"]})
    output = stream.getvalue()
    assert "\033[36m[judge-review]\033[0m" in output
    assert "\033[31mfailures 1\033[0m" in output
    assert "\033[35mActive tasks 1/4\033[0m" in output


def test_interactive_progress_respects_no_color(monkeypatch):
    from aies.progress import CliProgress

    class TtyStream(io.StringIO):
        def isatty(self):
            return True

    monkeypatch.setenv("NO_COLOR", "1")
    stream = TtyStream()
    render = CliProgress(stream)
    render({"stage": "response-collection", "status": "completed",
            "completed": 1, "total": 1, "percent": 100.0,
            "elapsed_seconds": 1.0, "total_elapsed_seconds": 1.0,
            "throughput_per_second": 1.0, "eta_seconds": 0.0,
            "eta_basis": "completed", "failures": 0,
            "current": "", "current_index": None,
            "activity": "", "parallelism": 1, "active_tasks": []})
    output = stream.getvalue()
    assert "\033[36m" not in output
    assert "\033[32m" not in output


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

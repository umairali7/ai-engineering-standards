"""Durable and CLI-visible progress for long-running assessment work."""

from __future__ import annotations

import datetime
import math
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Callable

from . import workspace

ProgressCallback = Callable[[dict], None]


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def format_duration(seconds: float | int | None) -> str:
    """Render operational time compactly without hiding its approximate nature."""
    if seconds is None:
        return "—"
    value = max(0, int(round(float(seconds))))
    hours, remainder = divmod(value, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def format_rate(per_second: float | int | None) -> str:
    """Render throughput in a useful unit and make the unit explicit."""
    rate = max(0.0, float(per_second or 0.0))
    if rate <= 0:
        return "calculating"
    if rate < 0.1:
        return f"{rate * 60:.2f} items/min"
    return f"{rate:.2f} items/s"


def update(run_id: str, stage: str, completed: int, total: int, *,
           status: str = "running", current: str = "", failures: int = 0,
           activity: str = "", current_index: int | None = None, message: str = "",
           active_tasks: list[str] | None = None, parallelism: int | None = None,
           active_unit: str = "task", reset_operation: bool = False,
           estimated_seconds_per_request: float | None = None,
           callback: ProgressCallback | None = None) -> dict:
    """Persist one current-state progress snapshot and optionally render it."""
    path = workspace.run_dir(run_id) / "progress.json"
    previous = workspace.read_json(path) if path.exists() else {}
    if parallelism is None:
        parallelism = previous.get("parallelism")
    if estimated_seconds_per_request is None:
        estimated_seconds_per_request = previous.get(
            "estimated_seconds_per_request")
    now_epoch = time.time()
    if reset_operation:
        started_at, started_epoch = _now(), now_epoch
    else:
        started_at = previous.get("started_at") or _now()
        started_epoch = previous.get("started_epoch") or now_epoch
    same_stage = not reset_operation and previous.get("stage") == stage
    stage_started_at = (previous.get("stage_started_at") if same_stage else None) or _now()
    stage_started_epoch = (previous.get("stage_started_epoch") if same_stage else None) or now_epoch
    stage_initial_completed = (
        int(previous.get("stage_initial_completed", 0))
        if same_stage else int(completed)
    )
    elapsed = max(0.0, now_epoch - float(stage_started_epoch))
    total_elapsed = max(0.0, now_epoch - float(started_epoch))
    measured_completed = max(0, int(completed) - stage_initial_completed)
    rate = measured_completed / elapsed if measured_completed and elapsed > 0 else 0.0
    remaining = max(0, total - completed)
    if status != "running" or completed >= total:
        eta_seconds = 0.0
        eta_basis = "completed"
    elif rate > 0:
        eta_seconds = round(remaining / rate, 1)
        eta_basis = "observed-throughput"
    elif estimated_seconds_per_request is not None:
        eta_seconds = round(
            math.ceil(remaining / max(1, parallelism or 1))
            * estimated_seconds_per_request, 1)
        eta_basis = "deployment-declaration"
    else:
        eta_seconds = None
        eta_basis = "awaiting-first-completion"
    if current_index is None and current:
        in_flight = activity.startswith(("Executing", "Scoring"))
        current_index = min(total, completed + 1) if in_flight else completed
    event = {
        "kind": "run-progress",
        "run_id": run_id,
        "stage": stage,
        "status": status,
        "completed": completed,
        "total": total,
        "percent": round(completed / total * 100, 1) if total else 0.0,
        "failures": failures,
        "current": current,
        "activity": activity,
        "current_index": current_index,
        "active_tasks": list(active_tasks or []),
        "active_count": len(active_tasks or []),
        "active_unit": active_unit,
        "parallelism": parallelism,
        "estimated_seconds_per_request": estimated_seconds_per_request,
        "message": message,
        "started_at": started_at,
        "stage_started_at": stage_started_at,
        # Internal epochs make ETA stable and are local operational state, not
        # canonical assessment evidence.
        "started_epoch": started_epoch,
        "stage_started_epoch": stage_started_epoch,
        "stage_initial_completed": stage_initial_completed,
        "measured_completed": measured_completed,
        "updated_at": _now(),
        "elapsed_seconds": round(elapsed, 1),
        "total_elapsed_seconds": round(total_elapsed, 1),
        "throughput_per_second": round(rate, 3),
        "eta_seconds": eta_seconds,
        "eta_basis": eta_basis,
        "resumable": status in {"running", "failed", "partial"},
    }
    workspace.write_json(path, event, overwrite=True)
    if callback:
        callback(event)
    return event


class CliProgress:
    """Detailed live progress without flooding redirected CI logs.

    Model calls can take minutes before producing their first completion
    event. A lightweight daemon heartbeat keeps elapsed time, the active task,
    and (once measurable) ETA moving between callback events. Redirected output
    remains event-driven and throttled so CI logs are not flooded.
    """

    def __init__(self, stream=None, *, refresh_interval: float = 1.0,
                 terminal_width: int | None = None):
        self.stream = stream or sys.stderr
        self.refresh_interval = max(0.05, refresh_interval)
        self.terminal_width = terminal_width
        self._last_stage = None
        self._last_bucket = -1
        self._last_event: dict | None = None
        self._received_monotonic = time.monotonic()
        self._lock = threading.RLock()
        self._heartbeat: threading.Thread | None = None
        self._slow_judge_tip_shown = False

    def _is_tty(self) -> bool:
        return bool(getattr(self.stream, "isatty", lambda: False)())

    def _uses_color(self) -> bool:
        mode = os.environ.get("AIES_COLOR", "auto").strip().lower()
        if mode == "never" or "NO_COLOR" in os.environ:
            return False
        if os.environ.get("TERM", "").strip().lower() == "dumb":
            return False
        return mode == "always" or self._is_tty()

    def _width(self) -> int:
        if self.terminal_width is not None:
            return max(40, self.terminal_width)
        return max(40, shutil.get_terminal_size((140, 24)).columns)

    def _live_event(self) -> dict:
        event = dict(self._last_event or {})
        if event.get("status") != "running":
            return event
        delta = max(0.0, time.monotonic() - self._received_monotonic)
        elapsed = float(event.get("elapsed_seconds") or 0.0) + delta
        total_elapsed = float(
            event.get("total_elapsed_seconds", event.get("elapsed_seconds", 0.0))
            or 0.0) + delta
        completed = int(event.get("completed") or 0)
        total = int(event.get("total") or 0)
        measured = max(
            0, completed - int(event.get("stage_initial_completed") or 0))
        rate = measured / elapsed if measured and elapsed > 0 else 0.0
        event["measured_completed"] = measured
        event["elapsed_seconds"] = elapsed
        event["total_elapsed_seconds"] = total_elapsed
        event["throughput_per_second"] = rate
        if rate > 0:
            event["eta_seconds"] = max(0, total - completed) / rate
            event["eta_basis"] = "observed-throughput"
        elif event.get("eta_basis") == "deployment-declaration":
            event["eta_seconds"] = max(
                0.0, float(event.get("eta_seconds") or 0.0) - delta)
        else:
            event["eta_seconds"] = None
        return event

    def _active_detail(self, event: dict) -> str:
        active_tasks = event.get("active_tasks") or []
        if active_tasks:
            capacity = event.get("parallelism") or len(active_tasks)
            unit = event.get("active_unit") or "task"
            label = "batches" if unit == "batch" else "tasks"
            # Rotate the visible task on every heartbeat. Parallel activity
            # stays observable without creating an unbounded terminal line.
            tick = int(float(event.get("total_elapsed_seconds") or 0.0)
                       / self.refresh_interval)
            selected = active_tasks[tick % len(active_tasks)]
            more = f" (+{len(active_tasks) - 1} more)" if len(active_tasks) > 1 else ""
            return (
                f" · Active {label} {len(active_tasks)}/{capacity}: "
                f"{selected}{more}")
        if event.get("current"):
            action = event.get("activity") or "Current task"
            total = event.get("total") or 0
            position = (f" {event['current_index']}/{total}"
                        if event.get("current_index") is not None and total else "")
            return f" · {action}{position}: {event['current']}"
        if event.get("message"):
            return f" · {event['message']}"
        return ""

    def _format(self, event: dict) -> str:
        total = event["total"]
        completed = event["completed"]
        if event["eta_seconds"] is None:
            eta = "calculating (first completion)"
        elif event.get("eta_basis") == "deployment-declaration":
            eta = f"~{format_duration(event['eta_seconds'])} (declared)"
        else:
            early = " (early)" if completed < max(
                3, int(event.get("parallelism") or 1)) else ""
            eta = f"~{format_duration(event['eta_seconds'])}{early}"
        failures = f" · failures {event['failures']}" if event.get("failures") else ""
        total_elapsed = event.get("total_elapsed_seconds", event["elapsed_seconds"])
        line = (
            f"[{event['stage']}] {completed}/{total} ({event['percent']:.1f}%) "
            f"· stage elapsed {format_duration(event['elapsed_seconds'])} · "
            f"command elapsed {format_duration(total_elapsed)} · "
            f"rate {format_rate(event['throughput_per_second'])} · ETA {eta}"
            f"{failures}{self._active_detail(event)}")
        if self._is_tty() and len(line) > self._width() - 1:
            line = line[:max(1, self._width() - 2)].rstrip() + "…"
        return line

    def _colorize(self, line: str, event: dict) -> str:
        if not self._uses_color():
            return line
        reset = "\033[0m"
        cyan, green, yellow = "\033[36m", "\033[32m", "\033[33m"
        red, magenta, bold = "\033[31m", "\033[35m", "\033[1m"
        stage = f"[{event['stage']}]"
        progress = f"{event['completed']}/{event['total']}"
        percent = f"({event['percent']:.1f}%)"
        percent_color = green if (
            event["status"] != "running"
            or event["completed"] >= event["total"]) else cyan
        line = line.replace(stage, f"{cyan}{stage}{reset}", 1)
        line = line.replace(progress, f"{bold}{progress}{reset}", 1)
        line = line.replace(
            percent, f"{percent_color}{percent}{reset}", 1)
        eta_marker = "ETA "
        eta_start = line.find(eta_marker)
        if eta_start >= 0:
            eta_end = line.find(" · ", eta_start)
            eta_end = len(line) if eta_end < 0 else eta_end
            eta_text = line[eta_start:eta_end]
            eta_color = (
                green
                if event.get("eta_basis") in {"observed-throughput", "completed"}
                and event.get("completed", 0) >= max(
                    3, int(event.get("parallelism") or 1))
                else yellow
            )
            line = (
                line[:eta_start] + eta_color + eta_text + reset
                + line[eta_end:])
        if event.get("failures"):
            failure_text = f"failures {event['failures']}"
            line = line.replace(
                failure_text, f"{red}{failure_text}{reset}", 1)
        active_tasks = event.get("active_tasks") or []
        if active_tasks:
            capacity = event.get("parallelism") or len(active_tasks)
            unit = event.get("active_unit") or "task"
            label = "batches" if unit == "batch" else "tasks"
            active_text = f"Active {label} {len(active_tasks)}/{capacity}"
            line = line.replace(
                active_text, f"{magenta}{active_text}{reset}", 1)
        return line

    def _render(self, event: dict, *, terminal: bool) -> None:
        line = self._colorize(self._format(event), event)
        if self._is_tty():
            # Clear before redrawing. The line is terminal-width bounded, so a
            # carriage return cannot leave fragments on wrapped rows.
            print("\r\033[2K" + line, end="\n" if terminal else "",
                  file=self.stream, flush=True)
        else:
            print(line, file=self.stream, flush=True)

    def _show_slow_judge_tip(self, event: dict) -> None:
        """Emit one actionable, non-blocking warning for a long serial judge."""
        if (self._slow_judge_tip_shown
                or event.get("stage") != "judge-review"
                or int(event.get("parallelism") or 1) != 1
                or int(event.get("measured_completed") or 0) < 1
                or float(event.get("eta_seconds") or 0) < 3600):
            return
        self._slow_judge_tip_shown = True
        prefix = "\n" if self._is_tty() else ""
        print(
            prefix
            + "  tip: projected serial judge time exceeds 1 hour. Completed "
              "batches are checkpointed; resume with --parallel N if the "
              "endpoint supports concurrent inference, or use a faster "
              "reviewer.",
            file=self.stream, flush=True)

    def _heartbeat_loop(self) -> None:
        while True:
            time.sleep(self.refresh_interval)
            with self._lock:
                if not self._last_event:
                    continue
                event = self._live_event()
                if event.get("status") == "running" and (
                        event.get("completed", 0) < event.get("total", 0)):
                    self._render(event, terminal=False)

    def _ensure_heartbeat(self) -> None:
        if not self._is_tty():
            return
        if self._heartbeat is None or not self._heartbeat.is_alive():
            self._heartbeat = threading.Thread(
                target=self._heartbeat_loop, name="aies-cli-progress",
                daemon=True)
            self._heartbeat.start()

    def __call__(self, event: dict) -> None:
        with self._lock:
            total = event["total"]
            completed = event["completed"]
            terminal = event["status"] != "running" or completed >= total
            bucket = int(event["percent"] // 5) if total else 0
            tty = self._is_tty()
            if (not tty and not terminal and event["stage"] == self._last_stage
                    and bucket == self._last_bucket):
                return
            self._last_stage, self._last_bucket = event["stage"], bucket
            self._last_event = dict(event)
            self._received_monotonic = time.monotonic()
            self._render(self._last_event, terminal=terminal)
            self._show_slow_judge_tip(self._last_event)
            self._ensure_heartbeat()

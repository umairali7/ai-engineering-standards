"""Durable and CLI-visible progress for long-running assessment work."""

from __future__ import annotations

import datetime
import sys
import time
from pathlib import Path
from typing import Callable

from . import workspace

ProgressCallback = Callable[[dict], None]


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def update(run_id: str, stage: str, completed: int, total: int, *,
           status: str = "running", current: str = "", failures: int = 0,
           message: str = "", callback: ProgressCallback | None = None) -> dict:
    """Persist one current-state progress snapshot and optionally render it."""
    path = workspace.run_dir(run_id) / "progress.json"
    previous = workspace.read_json(path) if path.exists() else {}
    started_at = previous.get("started_at") or _now()
    started_epoch = previous.get("started_epoch") or time.time()
    now_epoch = time.time()
    same_stage = previous.get("stage") == stage
    stage_started_at = (previous.get("stage_started_at") if same_stage else None) or _now()
    stage_started_epoch = (previous.get("stage_started_epoch") if same_stage else None) or now_epoch
    elapsed = max(0.0, now_epoch - float(stage_started_epoch))
    total_elapsed = max(0.0, now_epoch - float(started_epoch))
    rate = completed / elapsed if completed and elapsed > 0 else 0.0
    remaining = max(0, total - completed)
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
        "message": message,
        "started_at": started_at,
        "stage_started_at": stage_started_at,
        # Internal epochs make ETA stable and are local operational state, not
        # canonical assessment evidence.
        "started_epoch": started_epoch,
        "stage_started_epoch": stage_started_epoch,
        "updated_at": _now(),
        "elapsed_seconds": round(elapsed, 1),
        "total_elapsed_seconds": round(total_elapsed, 1),
        "throughput_per_second": round(rate, 3),
        "eta_seconds": round(remaining / rate, 1) if rate > 0 else None,
        "resumable": status in {"running", "failed", "partial"},
    }
    workspace.write_json(path, event, overwrite=True)
    if callback:
        callback(event)
    return event


class CliProgress:
    """Detailed live progress without flooding redirected CI logs."""

    def __init__(self, stream=None):
        self.stream = stream or sys.stderr
        self._last_stage = None
        self._last_bucket = -1

    def __call__(self, event: dict) -> None:
        total = event["total"]
        completed = event["completed"]
        terminal = event["status"] != "running" or completed >= total
        bucket = int(event["percent"] // 5) if total else 0
        tty = bool(getattr(self.stream, "isatty", lambda: False)())
        if not tty and not terminal and event["stage"] == self._last_stage and bucket == self._last_bucket:
            return
        self._last_stage, self._last_bucket = event["stage"], bucket
        eta = ("—" if event["eta_seconds"] is None
               else f"{event['eta_seconds']:.0f}s")
        current = f" · {event['current']}" if event.get("current") else ""
        failures = f" · failures {event['failures']}" if event.get("failures") else ""
        total_elapsed = event.get("total_elapsed_seconds", event["elapsed_seconds"])
        line = (f"[{event['stage']}] {completed}/{total} ({event['percent']:.1f}%) "
                f"· stage elapsed {event['elapsed_seconds']:.1f}s · "
                f"total elapsed {total_elapsed:.1f}s · "
                f"rate {event['throughput_per_second']:.2f}/s · ETA {eta}"
                f"{failures}{current}")
        if tty and not terminal:
            print("\r" + line, end="", file=self.stream, flush=True)
        else:
            if tty:
                print("\r" + line, file=self.stream, flush=True)
            else:
                print(line, file=self.stream, flush=True)

"""Compact terminal view over canonical ECM and engineering-fit artifacts.

This module does not score evidence or define a new decision product. It
projects the existing Engineering Capability Matrix and Engineering Fit
Guidance into a terminal-friendly view.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import adoption, constants as C, ecm, guidance


class SnapshotError(RuntimeError):
    pass


_FIT_LABELS = {
    "strong-observed-fit": "strong observed fit",
    "limited-evidence": "observed score; limited evidence",
    "review-recommended": "engineering review advised",
    "weak-observed-fit": "weak observed fit",
    "not-assessed": "not assessed",
}


def _breadth_label(percent: float) -> str:
    if percent >= 100:
        return "target met"
    if percent >= 50:
        return "partial breadth"
    if percent > 0:
        return "limited breadth"
    return "no direct evidence"


def _read_json(path: Path, expected_kind: str) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"cannot read {path.name}: {exc}") from exc
    kind = data.get("kind")
    if kind != expected_kind and not str(kind).startswith(expected_kind + "-v"):
        raise SnapshotError(
            f"{path.name} has kind {kind!r}, expected {expected_kind!r}"
        )
    return data


def build(reference: str) -> dict:
    """Build one display model without changing assessment semantics."""
    run = adoption.resolve_run(reference)
    matrix = _read_json(
        run / "engineering-capability-matrix.json",
        "engineering-capability-matrix",
    )
    if matrix is None:
        try:
            matrix = ecm.engineering_capability_matrix(run.name)
        except Exception as exc:
            raise SnapshotError(
                f"run {run.name!r} has no usable Engineering Capability Matrix; "
                "finish scoring and report generation first"
            ) from exc

    fit = _read_json(
        run / "engineering-fit-guidance.json",
        "engineering-fit-guidance",
    )
    if fit is None:
        fit = guidance.engineering_fit(run.name, matrix=matrix)
    fit_by_task = {row["task_id"]: row for row in fit.get("tasks", [])}

    tasks = []
    for task in matrix.get("tasks", []):
        fit_row = fit_by_task.get(task["task_id"], {})
        observed = task.get("observed_performance")
        performance = (
            round(float(observed) / 4 * 100, 1)
            if observed is not None else None
        )
        minimum = (
            task.get("minimum_observations")
            or (task.get("task_decision") or {}).get(
                "minimum_distinct_scenarios")
            or 0
        )
        distinct = int(task.get("distinct_scenarios") or 0)
        breadth = float(
            task.get("scenario_breadth_percent")
            if task.get("scenario_breadth_percent") is not None
            else task.get("engineering_confidence_percent")
            if task.get("engineering_confidence_percent") is not None
            else fit_row.get("scenario_breadth_percent",
                             fit_row.get("evidence_confidence_percent", 0))
        )
        fit_code = fit_row.get(
            "fit", "not-assessed" if observed is None else "review-recommended")
        interpretation = _FIT_LABELS.get(
            fit_code, fit_code.replace("-", " "))
        if fit_code != "not-assessed":
            interpretation += f" · {_breadth_label(breadth)}"
        tasks.append({
            "task_id": task["task_id"],
            "task": task["task"],
            "observed_performance_percent": performance,
            "scenario_breadth_percent": round(breadth, 1),
            "evidence_confidence_percent": round(breadth, 1),
            "evidence_assurance": task.get("evidence_assurance") or {},
            "distinct_scenarios": distinct,
            "target_scenarios": int(minimum),
            "fit": fit_code,
            "engineering_interpretation": interpretation,
        })

    human = (
        (matrix.get("engineering_evaluation") or {}).get("human_evaluation")
        or fit.get("human_evaluation")
        or {}
    )
    human_status = (
        f"reviewed — {human.get('evaluator') or 'named human'}"
        if human.get("status") == "reviewed"
        else "not reviewed (optional)"
    )
    assessed = sum(
        row["observed_performance_percent"] is not None for row in tasks)
    return {
        "kind": "engineering-decision-snapshot",
        "schema": 1,
        "status": "informational",
        "run_id": matrix["run_id"],
        "subject": matrix["subject"],
        "subject_kind": matrix.get("subject_kind", "unknown"),
        "risk_tier": matrix["risk_tier"],
        "risk_tier_label": C.risk_tier_label(matrix["risk_tier"]),
        "profile": matrix["profile"],
        "human_evaluation": human_status,
        "assessed_tasks": assessed,
        "unassessed_tasks": len(tasks) - assessed,
        "tasks": tasks,
        "authority_boundary": (
            "Observed performance, scenario breadth, and evidence assurance "
            "are separate. "
            "This view is informational and creates no qualification, grant, "
            "deployment recommendation, or authority."
        ),
    }


def _bar(percent: float | None, width: int = 10) -> str:
    if percent is None:
        return "░" * width
    filled = min(width, max(0, round(percent / 100 * width)))
    return "█" * filled + "░" * (width - filled)


def render(
    snapshot: dict,
    *,
    observed_only: bool = False,
    sort_by: str = "performance",
    descending: bool = True,
    width: int | None = None,
) -> str:
    """Render a responsive terminal table from a snapshot display model."""
    width = width or shutil.get_terminal_size(fallback=(120, 24)).columns
    tasks = snapshot["tasks"]
    if observed_only:
        tasks = [
            row for row in tasks
            if row["observed_performance_percent"] is not None
        ]
    sort_values = {
        "task": lambda row: row["task_id"],
        "performance": lambda row: row["observed_performance_percent"],
        "breadth": lambda row: row["scenario_breadth_percent"],
        "evidence": lambda row: row["distinct_scenarios"],
        "status": lambda row: row["engineering_interpretation"],
    }
    if sort_by not in sort_values:
        raise SnapshotError(f"unsupported task sort: {sort_by}")
    if sort_by == "task":
        tasks = sorted(tasks, key=sort_values[sort_by], reverse=descending)
    else:
        assessed = [row for row in tasks
                    if row["observed_performance_percent"] is not None]
        unassessed = [row for row in tasks
                      if row["observed_performance_percent"] is None]
        assessed.sort(
            key=lambda row: (sort_values[sort_by](row), row["task_id"]),
            reverse=descending)
        tasks = assessed + sorted(unassessed, key=lambda row: row["task_id"])

    lines = [
        "AIES  EVIDENCE → CAPABILITY → ASSURANCE → ENGINEERING DECISIONS",
        f"Run: {snapshot['run_id']}",
        f"Subject: {snapshot['subject']} · "
        f"{snapshot['risk_tier_label']} · {snapshot['profile']} profile",
        f"Human evaluation: {snapshot['human_evaluation']}",
        f"Order: {sort_by} ({'descending' if descending else 'ascending'})",
        "",
    ]
    if width >= 108:
        lines.extend([
            f"{'TASK':30} {'EVIDENCE':9} {'OBSERVED CAPABILITY':22} "
            f"{'SCENARIO BREADTH':22} {'INTERPRETATION'}",
            "─" * min(width, 132),
        ])
        for row in tasks:
            perf = row["observed_performance_percent"]
            capability = (
                f"{_bar(perf)} {perf:5.1f}%"
                if perf is not None else "not assessed"
            )
            breadth = (
                f"{_bar(row['scenario_breadth_percent'])} "
                f"{row['scenario_breadth_percent']:5.1f}%"
            )
            target = row["target_scenarios"]
            evidence = (
                f"{row['distinct_scenarios']}/{target}"
                if target else str(row["distinct_scenarios"])
            )
            task = f"{row['task_id']} — {row['task']}"
            lines.append(
                f"{task[:30]:30} {evidence:9} {capability:22} "
                f"{breadth:22} {row['engineering_interpretation']}"
            )
    else:
        for row in tasks:
            perf = row["observed_performance_percent"]
            target = row["target_scenarios"]
            evidence = (
                f"{row['distinct_scenarios']}/{target} distinct scenarios"
                if target else f"{row['distinct_scenarios']} distinct scenarios"
            )
            capability = (
                f"{_bar(perf)} {perf:.1f}%"
                if perf is not None else "not assessed"
            )
            breadth = (
                f"{_bar(row['scenario_breadth_percent'])} "
                f"{row['scenario_breadth_percent']:.1f}%"
            )
            lines.extend([
                f"{row['task_id']} — {row['task']}",
                f"  evidence   {evidence}",
                f"  capability {capability}",
                f"  breadth    {breadth}",
                f"  meaning    {row['engineering_interpretation']}",
            ])

    lines.extend([
        "",
        f"Coverage: {snapshot['assessed_tasks']} assessed · "
        f"{snapshot['unassessed_tasks']} not assessed (unknown, not zero)",
        "Capability = normalized observed EV score. Scenario breadth = distinct "
        "directly mapped scenarios / task target; it is not reviewer or "
        "instrument assurance.",
        "INFORMATIONAL — no qualification, grant, deployment recommendation, "
        "or authority.",
    ])
    return "\n".join(lines)

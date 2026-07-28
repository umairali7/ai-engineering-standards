"""Standards-assisted execution, kept separate from baseline assessment.

This workflow demonstrates how task-scoped AIES guidance changes an output. It
never writes qualification evidence and never enters an assessment aggregate.
"""

from __future__ import annotations

import datetime
import hashlib
import time

from . import assessment_instruments, constants as C, executors, registry, workspace
from .adapters.base import GenerationRequest


class GuidedExecutionError(RuntimeError):
    pass


def _emit_progress(
    callback,
    *,
    execution_id: str,
    stage: str,
    completed: int,
    total: int,
    command_started: float,
    stage_started: float,
    current: str,
    status: str = "running",
) -> None:
    if callback is None:
        return
    now = time.monotonic()
    elapsed = max(0.0, now - stage_started)
    command_elapsed = max(0.0, now - command_started)
    measured = completed
    rate = measured / elapsed if measured and elapsed > 0 else 0.0
    callback({
        "kind": "operation-progress",
        "run_id": execution_id,
        "stage": stage,
        "status": status,
        "completed": completed,
        "total": total,
        "percent": round(completed / total * 100, 1) if total else 0.0,
        "failures": 0,
        "current": current,
        "activity": "Executing" if completed < total else "Completed",
        "current_index": min(total, completed + 1) if completed < total else total,
        "active_tasks": [current] if completed < total else [],
        "active_count": 1 if completed < total else 0,
        "active_unit": "task",
        "parallelism": 1,
        "estimated_seconds_per_request": None,
        "message": current,
        "stage_initial_completed": 0,
        "measured_completed": measured,
        "elapsed_seconds": round(elapsed, 1),
        "total_elapsed_seconds": round(command_elapsed, 1),
        "throughput_per_second": round(rate, 3),
        "eta_seconds": 0.0 if completed >= total else None,
        "eta_basis": "completed" if completed >= total else "awaiting-first-completion",
        "resumable": False,
    })


def _new_id(subject: str, scenario_id: str) -> str:
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = hashlib.sha256(
        f"{subject}:{scenario_id}:{now}".encode()).hexdigest()[:8]
    safe = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in subject)
    return f"guided-{now}-{safe}-{scenario_id}-{suffix}"


def _score(judge_executor, instrument: dict, response: str) -> dict | None:
    from .model_review import (
        _parse_scores, _review_prompt, validate_review_trace)

    reply = judge_executor.generate(
        GenerationRequest(prompt=_review_prompt(instrument, response)))
    parsed = _parse_scores(reply.text)
    if parsed is None:
        return None
    scores, findings, grounding, trace = parsed
    trace = validate_review_trace(instrument, scores, trace)
    return {
        "scores": scores,
        "findings": findings,
        "grounding_diagnostics": grounding,
        "review_trace": trace,
    }


def execute(
    subject: str,
    scenario_id: str,
    *,
    runtime: str | None = None,
    compare_baseline: bool = False,
    judge: str | None = None,
    reviewer_runtime: str | None = None,
    parameters: dict | None = None,
    progress_callback=None,
) -> dict:
    """Execute one task with a scoped AIES context pack.

    When ``compare_baseline`` is true, the unassisted task is executed first.
    A supplied judge scores both outputs against the same hidden instrument so
    the delta is directly comparable. These observations are never imported
    into formal qualification evidence.
    """
    scenario, suite_version = assessment_instruments.find_scenario(scenario_id)
    instrument = assessment_instruments.build(
        scenario, suite_version=suite_version)
    subject_entry = registry.resolve(subject, runtime=runtime)
    execution_id = _new_id(subject_entry["id"], scenario_id)
    command_started = time.monotonic()
    subject_executor = executors.RuntimeGenerationExecutor(subject_entry)
    subject_executor.load()
    params = parameters or {}

    baseline_response = None
    if compare_baseline:
        stage_started = time.monotonic()
        _emit_progress(
            progress_callback, execution_id=execution_id,
            stage="baseline-execution", completed=0, total=1,
            command_started=command_started, stage_started=stage_started,
            current=f"{scenario_id} · unassisted baseline")
        baseline_response = subject_executor.generate(GenerationRequest(
            prompt=assessment_instruments.candidate_projection(
                instrument)["task_prompt"],
            parameters=params,
        )).text
        _emit_progress(
            progress_callback, execution_id=execution_id,
            stage="baseline-execution", completed=1, total=1,
            command_started=command_started, stage_started=stage_started,
            current=f"{scenario_id} · unassisted baseline", status="completed")
    guided_prompt = assessment_instruments.guided_context(instrument)
    stage_started = time.monotonic()
    _emit_progress(
        progress_callback, execution_id=execution_id,
        stage="guided-execution", completed=0, total=1,
        command_started=command_started, stage_started=stage_started,
        current=f"{scenario_id} · task-scoped AIES guidance")
    guided_response = subject_executor.generate(GenerationRequest(
        prompt=guided_prompt, parameters=params)).text
    _emit_progress(
        progress_callback, execution_id=execution_id,
        stage="guided-execution", completed=1, total=1,
        command_started=command_started, stage_started=stage_started,
        current=f"{scenario_id} · task-scoped AIES guidance", status="completed")

    judge_executor = None
    judge_descriptor = None
    baseline_review = None
    guided_review = None
    if judge:
        judge_entry = registry.resolve(judge, runtime=reviewer_runtime)
        judge_descriptor = {
            "id": judge_entry["id"],
            "runtime": judge_entry["runtime"],
            "checksum": (
                judge_entry.get("provenance") or {}).get("checksum"),
            "same_deployment_as_subject": (
                judge_entry["id"] == subject_entry["id"]),
        }
        judge_executor = executors.RuntimeGenerationExecutor(judge_entry)
        judge_executor.load()
        if baseline_response is not None:
            stage_started = time.monotonic()
            _emit_progress(
                progress_callback, execution_id=execution_id,
                stage="baseline-review", completed=0, total=1,
                command_started=command_started, stage_started=stage_started,
                current=f"{scenario_id} · blind baseline review")
            baseline_review = _score(
                judge_executor, instrument, baseline_response)
            _emit_progress(
                progress_callback, execution_id=execution_id,
                stage="baseline-review", completed=1, total=1,
                command_started=command_started, stage_started=stage_started,
                current=f"{scenario_id} · blind baseline review",
                status="completed")
        stage_started = time.monotonic()
        _emit_progress(
            progress_callback, execution_id=execution_id,
            stage="guided-review", completed=0, total=1,
            command_started=command_started, stage_started=stage_started,
            current=f"{scenario_id} · blind guided-output review")
        guided_review = _score(judge_executor, instrument, guided_response)
        _emit_progress(
            progress_callback, execution_id=execution_id,
            stage="guided-review", completed=1, total=1,
            command_started=command_started, stage_started=stage_started,
            current=f"{scenario_id} · blind guided-output review",
            status="completed")

    deltas = {}
    if baseline_review and guided_review:
        deltas = {
            dimension: (
                guided_review["scores"][dimension]
                - baseline_review["scores"][dimension])
            for dimension in C.DIMENSIONS
        }
    result = {
        "kind": "aies-standards-guided-execution",
        "schema_version": 1,
        "execution_id": execution_id,
        "recorded_at": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "status": "informational",
        "subject": {
            "id": subject_entry["id"],
            "runtime": subject_entry["runtime"],
            "checksum": (
                subject_entry.get("provenance") or {}).get("checksum"),
        },
        "instrument": {
            "scenario_id": scenario_id,
            "suite_version": suite_version,
            "instrument_digest": instrument["instrument_digest"],
            "area": instrument["area"],
            "risk_tier": instrument["risk_tier"],
            "engineering_tasks": instrument["engineering_tasks"],
        },
        "mode": {
            "guided": True,
            "baseline_compared": compare_baseline,
            "judge": judge_descriptor,
            "qualification_eligible": False,
        },
        "baseline": (
            {
                "projection": "candidate-task-only",
                "response": baseline_response,
                "review": baseline_review,
            }
            if compare_baseline else None
        ),
        "guided": {
            "projection": "task-scoped-standards-context",
            "context_digest": "sha256:" + hashlib.sha256(
                guided_prompt.encode()).hexdigest(),
            "response": guided_response,
            "review": guided_review,
        },
        "score_delta_guided_minus_baseline": deltas or None,
        "boundary": (
            "Standards-assisted output and its delta are engineering diagnostics. "
            "They are excluded from unassisted assessment breadth, formal "
            "qualification, grants, and deployment authority."
        ),
    }
    path = workspace.ensure() / "guided-executions" / f"{execution_id}.json"
    stage_started = time.monotonic()
    _emit_progress(
        progress_callback, execution_id=execution_id,
        stage="artifact-write", completed=0, total=1,
        command_started=command_started, stage_started=stage_started,
        current=f"{execution_id}.json")
    workspace.write_json(path, result)
    _emit_progress(
        progress_callback, execution_id=execution_id,
        stage="artifact-write", completed=1, total=1,
        command_started=command_started, stage_started=stage_started,
        current=f"{execution_id}.json", status="completed")
    result["artifact"] = str(path)
    return result


def render_markdown(result: dict) -> str:
    instrument = result["instrument"]
    lines = [
        "# AIES Standards-Assisted Execution",
        "",
        "> **INFORMATIONAL — EXCLUDED FROM FORMAL QUALIFICATION EVIDENCE.**",
        "",
        f"Execution: `{result['execution_id']}`  ",
        f"Subject: `{result['subject']['id']}`  ",
        f"Instrument: `{instrument['scenario_id']}` "
        f"(`{instrument['instrument_digest']}`)  ",
        f"Scope: {instrument['area']['label']} · "
        f"{instrument['risk_tier']['label']}",
        "",
    ]
    judge = result["mode"].get("judge")
    if judge:
        role_note = (
            "same deployment as subject; self-review limitation"
            if judge["same_deployment_as_subject"]
            else "separate reviewer deployment")
        lines.extend([f"Reviewer: `{judge['id']}` ({role_note})", ""])
    if result["baseline"]:
        lines.extend(["## Baseline output", "", result["baseline"]["response"], ""])
    lines.extend(["## Standards-assisted output", "", result["guided"]["response"], ""])
    if result["score_delta_guided_minus_baseline"]:
        lines.extend([
            "## Baseline versus guided EV delta",
            "",
            "| Dimension | Baseline | Guided | Delta |",
            "|---|---:|---:|---:|",
        ])
        baseline_scores = result["baseline"]["review"]["scores"]
        guided_scores = result["guided"]["review"]["scores"]
        for dimension in C.DIMENSIONS:
            delta = result["score_delta_guided_minus_baseline"][dimension]
            lines.append(
                f"| {C.identifier_label(dimension)} | "
                f"{baseline_scores[dimension]} | {guided_scores[dimension]} | "
                f"{delta:+d} |")
        lines.append("")
    lines.extend([result["boundary"], "", f"Artifact: `{result['artifact']}`", ""])
    return "\n".join(lines)

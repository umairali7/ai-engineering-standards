"""Declared cost and duration estimates for pre-run planning.

Estimates are produced only from deployment-manifest declarations. Missing
pricing or throughput remains explicit; the planner never invents provider
prices or endpoint speed.
"""

from __future__ import annotations

import math


TOKEN_FIELDS = (
    "estimated_input_tokens_per_item",
    "estimated_output_tokens_per_item",
    "input_usd_per_million_tokens",
    "output_usd_per_million_tokens",
)
PLANNING_FIELDS = frozenset({
    *TOKEN_FIELDS,
    "usd_per_request",
    "estimated_seconds_per_request",
})


def validate(declaration: object) -> list[str]:
    if declaration is None:
        return []
    if not isinstance(declaration, dict):
        return ["planning must be a mapping"]
    errors = []
    unknown = sorted(set(declaration) - PLANNING_FIELDS)
    if unknown:
        errors.append("planning contains unknown fields: " + ", ".join(unknown))
    for field, value in declaration.items():
        if field not in PLANNING_FIELDS:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"planning.{field} must be a number")
        elif value < 0:
            errors.append(f"planning.{field} must be non-negative")
    seconds = declaration.get("estimated_seconds_per_request")
    if seconds == 0:
        errors.append("planning.estimated_seconds_per_request must be greater than zero")
    token_values = [declaration.get(field) for field in TOKEN_FIELDS]
    if any(value is not None for value in token_values) and not all(
            value is not None for value in token_values):
        errors.append(
            "token-cost planning requires all of " + ", ".join(TOKEN_FIELDS))
    if all(value is not None for value in token_values) and (
            declaration.get("usd_per_request") is not None):
        errors.append(
            "choose token-based pricing or planning.usd_per_request, not both")
    return errors


def _phase(
    entry: dict,
    *,
    logical_items: int,
    requests: int,
    parallel: int,
    phase: str,
) -> dict:
    declaration = entry.get("planning") or {}
    cost_parts = []
    token_cost = None
    if all(declaration.get(field) is not None for field in TOKEN_FIELDS):
        input_cost = (
            logical_items
            * declaration["estimated_input_tokens_per_item"]
            * declaration["input_usd_per_million_tokens"]
            / 1_000_000
        )
        output_cost = (
            logical_items
            * declaration["estimated_output_tokens_per_item"]
            * declaration["output_usd_per_million_tokens"]
            / 1_000_000
        )
        token_cost = input_cost + output_cost
        cost_parts.append("declared per-item token estimate and token prices")
    request_cost = None
    if declaration.get("usd_per_request") is not None:
        request_cost = requests * declaration["usd_per_request"]
        cost_parts.append("declared per-request price")
    known_cost = token_cost if token_cost is not None else request_cost
    cost = round(known_cost, 6) if known_cost is not None else None

    seconds = declaration.get("estimated_seconds_per_request")
    duration = None
    if seconds is not None:
        duration = round(math.ceil(requests / max(1, parallel)) * seconds, 1)

    missing = []
    if cost is None:
        missing.append(
            "declare either planning.usd_per_request or all token estimate/price fields")
    if duration is None:
        missing.append("declare planning.estimated_seconds_per_request")
    return {
        "phase": phase,
        "deployment": entry.get("id"),
        "logical_items": logical_items,
        "requests": requests,
        "parallelism": max(1, parallel),
        "cost_usd": cost,
        "duration_seconds": duration,
        "cost_basis": " + ".join(cost_parts) if cost_parts else None,
        "duration_basis": (
            "declared seconds/request x concurrency waves"
            if duration is not None else None),
        "missing": missing,
    }


def estimate(
    plan: dict,
    *,
    subject: dict,
    judge: dict | None,
    judge_batch_size: int,
    parallel: int,
) -> dict:
    items = int(plan["planned_items"])
    phases = [
        _phase(
            subject,
            logical_items=items,
            requests=items,
            parallel=parallel,
            phase="candidate-collection",
        )
    ]
    if judge:
        judge_requests = math.ceil(items / max(1, judge_batch_size))
        phases.append(_phase(
            judge,
            logical_items=items,
            requests=judge_requests,
            parallel=parallel,
            phase="judge-scoring",
        ))
    costs = [phase["cost_usd"] for phase in phases]
    durations = [phase["duration_seconds"] for phase in phases]
    return {
        "kind": "declared-pre-run-estimate",
        "status": (
            "complete"
            if all(value is not None for value in costs + durations)
            else "partial"
            if any(value is not None for value in costs + durations)
            else "unavailable"
        ),
        "total_cost_usd": (
            round(sum(costs), 6)
            if all(value is not None for value in costs) else None),
        "total_duration_seconds": (
            round(sum(durations), 1)
            if all(value is not None for value in durations) else None),
        "phases": phases,
        "limitations": [
            "Estimates are manifest declarations, not measured guarantees.",
            "Provider retries, batch fallback, queueing, and variable output length can increase cost or duration.",
            "Parallel duration assumes the endpoint serves the requested concurrency.",
        ],
    }

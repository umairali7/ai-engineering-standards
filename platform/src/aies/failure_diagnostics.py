"""Actionable, secret-safe diagnostics for failed CLI operations.

This module describes a failure without changing its underlying exception
semantics.  The contract is deliberately subject-neutral: it records what
failed, what work is still usable, how to recover, and whether retrying can
duplicate paid or long-running work.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from typing import TextIO


DIAGNOSTIC_SCHEMA = "aies-cli-failure-v1"
TROUBLESHOOTING = "platform/TROUBLESHOOTING.md"

_SECRET_PATTERNS = (
    (re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,;]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{12,}"), r"\1[REDACTED]"),
    (re.compile(r"(?i)([\"']?(?:api[_-]?key|token|secret)[\"']?\s*[:=]\s*[\"'])[^\"']+"),
     r"\1[REDACTED]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"), "[REDACTED]"),
)


@dataclass(frozen=True)
class FailureDiagnostic:
    kind: str
    schema: str
    category: str
    operation: str
    summary: str
    run_id: str | None
    preserved_work_status: str
    preserved_work_detail: str
    recovery_command: str
    documentation: str
    duplicate_cost_risk: str
    duplicate_cost_detail: str


def sanitize(message: object) -> str:
    """Remove common credential forms before a provider error reaches output."""
    value = str(message).strip()
    for pattern, replacement in _SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def classify(message: object, *, phase: str | None = None) -> str:
    """Classify a failure using stable, user-facing categories."""
    text = sanitize(message).lower()
    if "insufficient_quota" in text or "exceeded your current quota" in text:
        return "quota"
    if any(token in text for token in (
            "http 401", "http 403", "unauthorized", "forbidden",
            "invalid api key", "authentication", "credential")):
        return "authentication"
    if "http 429" in text or "rate limit" in text or "rate-limit" in text:
        return "quota"
    if any(token in text for token in (
            "modulenotfounderror", "no module named", "dependency",
            "externally-managed-environment")):
        return "dependency"
    if any(token in text for token in (
            "incompatible", "unsupported version", "schema version",
            "suite changed", "version mismatch")):
        return "compatibility"
    if any(token in text for token in (
            "unparseable", "no parseable", "invalid json", "jsondecodeerror",
            "could not parse")):
        return "parsing"
    if any(token in text for token in (
            "non-decisional", "grant", "qualification authority",
            "human authority", "governance")):
        return "governance"
    if any(token in text for token in (
            "no ratings", "no responses", "scoresheet", "evidence",
            "no run ", "not found", "unknown subject", "unknown starter")):
        return "evidence"
    if phase in {"scoring", "review"} or any(token in text for token in (
            "judge", "reviewer", "scoring", "rating")):
        return "scoring"
    if any(token in text for token in (
            "timed out", "timeout", "connection refused", "could not reach",
            "did not respond", "inference call", "liveness probe",
            "certificate_verify_failed", "ssl", "tls", "dns")):
        return "inference"
    if any(token in text for token in (
            "permission denied", "read-only", "environment", "workspace",
            "file exists", "is a directory")):
        return "environment"
    return "environment"


def documentation_for(category: str) -> str:
    anchors = {
        "authentication": "#authentication",
        "quota": "#quota-and-rate-limits",
        "dependency": "#installation-and-dependencies",
        "compatibility": "#compatibility",
        "inference": "#connectivity--tls",
        "scoring": "#the-judge---judge",
        "parsing": "#the-judge---judge",
        "evidence": "#scoring--reports",
        "governance": "#engineering-evaluation-vs-formal-qualification",
        "environment": "#environment-and-workspace",
    }
    return TROUBLESHOOTING + anchors.get(category, "")


def build(
    error: object,
    *,
    operation: str,
    phase: str | None = None,
    run_id: str | None = None,
    category: str | None = None,
    preserved_work_status: str = "none",
    preserved_work_detail: str = "No durable assessment work was started.",
    recovery_command: str,
    duplicate_cost_risk: str = "none",
    duplicate_cost_detail: str = "Retrying does not repeat paid assessment work.",
) -> FailureDiagnostic:
    category = category or classify(error, phase=phase)
    return FailureDiagnostic(
        kind="cli-failure-diagnostic",
        schema=DIAGNOSTIC_SCHEMA,
        category=category,
        operation=operation,
        summary=sanitize(error),
        run_id=run_id,
        preserved_work_status=preserved_work_status,
        preserved_work_detail=preserved_work_detail,
        recovery_command=recovery_command,
        documentation=documentation_for(category),
        duplicate_cost_risk=duplicate_cost_risk,
        duplicate_cost_detail=duplicate_cost_detail,
    )


def emit(
    diagnostic: FailureDiagnostic,
    *,
    as_json: bool = False,
    stream: TextIO | None = None,
) -> None:
    """Render one diagnostic to stderr by default."""
    stream = stream or sys.stderr
    if as_json:
        print(json.dumps(asdict(diagnostic), indent=2), file=stream)
        return
    print(f"error [{diagnostic.category}]: {diagnostic.summary}", file=stream)
    print(
        f"  work preserved: {diagnostic.preserved_work_status} — "
        f"{diagnostic.preserved_work_detail}",
        file=stream,
    )
    print(f"  recover: {diagnostic.recovery_command}", file=stream)
    print(
        f"  duplicate-cost risk: {diagnostic.duplicate_cost_risk} — "
        f"{diagnostic.duplicate_cost_detail}",
        file=stream,
    )
    print(f"  help: {diagnostic.documentation}", file=stream)

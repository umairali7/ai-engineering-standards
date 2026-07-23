"""Run-purpose helpers for separating evaluation from formal qualification."""

from __future__ import annotations

ENGINEERING_EVALUATION = "engineering-evaluation"
FORMAL_QUALIFICATION = "formal-qualification"


def purpose(manifest: dict) -> str:
    """Return a run's declared purpose.

    Manifests created before the purpose field existed retain their historical
    formal-assessment behavior. New runs always record the field explicitly.
    """
    declared = manifest.get("run_purpose")
    if declared in (ENGINEERING_EVALUATION, FORMAL_QUALIFICATION):
        return declared
    return FORMAL_QUALIFICATION if manifest.get("assessment") else ENGINEERING_EVALUATION


def is_formal(manifest: dict) -> bool:
    return purpose(manifest) == FORMAL_QUALIFICATION

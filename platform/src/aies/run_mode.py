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


def scope(manifest: dict) -> dict:
    """Describe how the run was composed without conflating profile and scope."""
    assessment = manifest.get("assessment")
    areas = list(manifest.get("scoped_areas") or [
        item.get("area") for item in manifest.get("areas", [])
        if item.get("area")
    ])
    if assessment:
        assessment_id = (
            assessment.get("id") or assessment.get("name")
            if isinstance(assessment, dict) else str(assessment))
        return {
            "kind": "declarative-assessment",
            "assessment": assessment_id,
            "areas": areas,
            "label": f"Declarative assessment {assessment_id}",
            "profile_role": "assessment-selected weighting profile",
        }
    return {
        "kind": "targeted-area-selection",
        "assessment": None,
        "areas": areas,
        "label": "Targeted competency-area selection (not a declarative assessment)",
        "profile_role": "score-weighting profile only",
    }

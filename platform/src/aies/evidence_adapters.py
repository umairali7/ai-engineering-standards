"""Evidence Adapter declarations and compatibility checks (ADR-0015)."""

from __future__ import annotations

import copy

CONTRACT = "aies-evidence-adapter/v1"
VALID_MODALITIES = frozenset({
    "controlled-scenario", "integrated-system", "field-observation",
    "repository-static-analysis", "telemetry", "attestation",
    "human-rating", "automated-rating", "review-disposition",
    "environment-fingerprint", "lifecycle-transition",
})
VALID_COMPLETENESS = frozenset({"complete", "partial", "profile-bounded"})
VALID_DECISION_USE = frozenset({
    "informational-only", "engineering-evaluation", "formal-qualification",
})


class EvidenceAdapterError(ValueError):
    pass


def declaration(
    *,
    profile: str,
    version: str,
    source_format: str,
    source_versions: list[str],
    modalities: list[str],
    event_types: list[str],
    completeness: str,
    decision_use: str,
    scoring_semantics: str,
    privacy: dict,
    limitations: list[str],
) -> dict:
    value = {
        "contract": CONTRACT,
        "profile": profile,
        "version": version,
        "source": {
            "format": source_format,
            "versions": source_versions,
        },
        "modalities": modalities,
        "event_types": event_types,
        "completeness": completeness,
        "decision_use": decision_use,
        "scoring_semantics": scoring_semantics,
        "duplicate_identity": (
            "source_digest + source_record_id + adapter_profile"),
        "privacy": privacy,
        "loss_report_required": True,
        "decision_products": (
            ["Engineering Evaluation", "Engineering Capability Matrix"]
            if decision_use == "engineering-evaluation" else []),
        "limitations": limitations,
    }
    errors = validate(value)
    if errors:
        raise EvidenceAdapterError("; ".join(errors))
    return value


def validate(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["adapter declaration must be an object"]
    errors = []
    if value.get("contract") != CONTRACT:
        errors.append(f"contract must be {CONTRACT}")
    for field in ("profile", "version", "scoring_semantics"):
        if not isinstance(value.get(field), str) or not value[field]:
            errors.append(f"{field} is required")
    source = value.get("source")
    if not isinstance(source, dict) or not source.get("format"):
        errors.append("source.format is required")
    elif not source.get("versions"):
        errors.append("source.versions is required")
    modalities = value.get("modalities")
    if not isinstance(modalities, list) or not modalities:
        errors.append("modalities is required")
    elif set(modalities) - VALID_MODALITIES:
        errors.append("modalities contains unsupported values")
    if not isinstance(value.get("event_types"), list) or not value["event_types"]:
        errors.append("event_types is required")
    if value.get("completeness") not in VALID_COMPLETENESS:
        errors.append("completeness is unsupported")
    if value.get("decision_use") not in VALID_DECISION_USE:
        errors.append("decision_use is unsupported")
    if value.get("loss_report_required") is not True:
        errors.append("loss_report_required must be true")
    privacy = value.get("privacy")
    if not isinstance(privacy, dict):
        errors.append("privacy declaration is required")
    elif privacy.get("secrets") != "prohibited":
        errors.append("privacy.secrets must be prohibited")
    if not isinstance(value.get("limitations"), list) or not value["limitations"]:
        errors.append("limitations is required")
    return errors


INSPECT = declaration(
    profile="aies-inspect-eval-log/v1",
    version="1.0.0",
    source_format="Inspect EvalLog JSON (AIES portable profile)",
    source_versions=["aies-inspect-eval-log-profile/v1"],
    modalities=["controlled-scenario", "automated-rating", "human-rating"],
    event_types=["observation", "rating"],
    completeness="profile-bounded",
    decision_use="engineering-evaluation",
    scoring_semantics=(
        "Only explicit integer AIES EV1-EV6 values are imported; no metric "
        "is translated or inferred."),
    privacy={
        "classification_required": True,
        "sensitive_payloads": "not-copied",
        "secrets": "prohibited",
    },
    limitations=[
        "Portable AIES JSON profile only; native Inspect container metadata is not fabricated.",
        "Imported model/automated ratings remain outside formal qualification admission.",
    ],
)

SARIF = declaration(
    profile="aies-sarif-2.1.0/v1",
    version="1.0.0",
    source_format="SARIF",
    source_versions=["2.1.0"],
    modalities=["repository-static-analysis"],
    event_types=["observation"],
    completeness="partial",
    decision_use="informational-only",
    scoring_semantics=(
        "Tool findings retain source severity; they are not converted to AIES "
        "EV scores, maturity, correctness, or conformance."),
    privacy={
        "classification_required": True,
        "sensitive_payloads": "source-controlled",
        "secrets": "prohibited",
    },
    limitations=[
        "SARIF findings do not prove correctness or absence of defects.",
        "A repository subject binding is required before cross-artifact correlation.",
    ],
)

REGISTRY = {item["profile"]: item for item in (INSPECT, SARIF)}


def get(profile: str) -> dict:
    try:
        return copy.deepcopy(REGISTRY[profile])
    except KeyError as exc:
        raise EvidenceAdapterError(
            f"unknown evidence adapter profile {profile!r}") from exc


def compatibility(left: dict, right: dict) -> dict:
    """Compare declarations without treating incompatible evidence as equal."""
    for value in (left, right):
        errors = validate(value)
        if errors:
            raise EvidenceAdapterError("; ".join(errors))
    checks = {
        "contract_major": (
            left["contract"].rsplit("/", 1)[-1].split(".", 1)[0]
            == right["contract"].rsplit("/", 1)[-1].split(".", 1)[0]),
        "profile": left["profile"] == right["profile"],
        "source_format": left["source"]["format"] == right["source"]["format"],
        "modalities": set(left["modalities"]) == set(right["modalities"]),
        "scoring_semantics": (
            left["scoring_semantics"] == right["scoring_semantics"]),
        "decision_use": left["decision_use"] == right["decision_use"],
    }
    return {
        "compatible": all(checks.values()),
        "checks": checks,
        "claim_boundary": (
            "Compatibility permits comparison of adapter output structure; "
            "it does not admit evidence to a decision product."),
    }

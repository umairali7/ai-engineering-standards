"""Canonical, subject-neutral identity for assessment and evidence.

The Subject Descriptor is independently versioned from run manifests and
runtime adapters. Legacy deployment runs are upgraded in memory so their
append-only evidence is never rewritten merely to adopt the new contract.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Iterable

SUBJECT_SCHEMA = "aies-subject-descriptor/v1"
RUN_MANIFEST_SCHEMA = "aies-run-manifest/v2"
VALID_KINDS = frozenset({
    "human", "team", "repository", "ai_deployment", "ai_system", "agent",
    "agent_swarm", "mcp_server", "coding_assistant", "prompt_library",
    "rag_system", "pipeline", "platform", "composite",
})
VALID_PRIVACY = frozenset({"public", "internal", "confidential", "restricted"})
VALID_COMPONENT_ROLES = frozenset({
    "contains", "depends-on", "executes", "serves", "retrieves-from",
    "orchestrates", "observes", "evaluates", "uses",
})


class SubjectError(ValueError):
    pass


def _digest(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def component_reference(
    subject_id: str,
    *,
    kind: str,
    role: str,
    version: str | None = None,
    fingerprint: str | None = None,
    evidence_transfer: str = "none",
) -> dict:
    """Build a typed composite dependency without transferring its claims."""
    value = {
        "subject_id": subject_id,
        "kind": kind,
        "role": role,
        "version": version,
        "fingerprint": fingerprint,
        "evidence_transfer": evidence_transfer,
    }
    errors = _validate_component(value, "component")
    if errors:
        raise SubjectError("; ".join(errors))
    return value


def build(
    subject_id: str,
    *,
    kind: str,
    display_name: str,
    version: str | None = None,
    components: Iterable[str | dict] = (),
    environment_fingerprint: str | None = None,
    provenance: Iterable[dict] = (),
    privacy: str = "internal",
    extensions: dict | None = None,
) -> dict:
    descriptor = {
        "schema": SUBJECT_SCHEMA,
        "id": subject_id,
        "kind": kind,
        "display_name": display_name,
        "version": version,
        "components": list(components),
        "environment_fingerprint": environment_fingerprint,
        "provenance": list(provenance),
        "privacy": privacy,
        "extensions": copy.deepcopy(extensions or {}),
    }
    errors = validate(descriptor)
    if errors:
        raise SubjectError("; ".join(errors))
    return descriptor


def deployment_descriptor(
    entry: dict,
    environment_fingerprint: dict | None = None,
    *,
    executor: dict | None = None,
) -> dict:
    provenance = entry.get("provenance") or {}
    checksum = provenance.get("checksum")
    refs = []
    if checksum:
        refs.append({
            "kind": "deployment-artifact",
            "digest": checksum,
            "source": provenance.get("source"),
        })
    fp = (environment_fingerprint or {}).get("fingerprint_hash")
    return build(
        entry["id"],
        kind="ai_deployment",
        display_name=entry.get("model") or entry.get("family") or entry["id"],
        version=str(entry.get("revision") or entry.get("version") or "") or None,
        environment_fingerprint=fp,
        provenance=refs,
        privacy=entry.get("privacy", "internal"),
        extensions={
            "deployment": {
                "family": entry.get("family"),
                "runtime": entry.get("runtime"),
                "model": entry.get("model"),
            },
            **({"executor": copy.deepcopy(executor)} if executor else {}),
        },
    )


def repository_descriptor(
    subject_id: str,
    *,
    display_name: str,
    commit: str | None = None,
    tree: str | None = None,
    environment_fingerprint: str | None = None,
    components: Iterable[str | dict] = (),
    privacy: str = "internal",
    extensions: dict | None = None,
) -> dict:
    binding = {"commit": commit, "tree": tree}
    binding = {key: value for key, value in binding.items() if value}
    return build(
        subject_id,
        kind="repository",
        display_name=display_name,
        version=commit,
        components=components,
        environment_fingerprint=environment_fingerprint,
        privacy=privacy,
        provenance=([{"kind": "source-binding", **binding}] if binding else []),
        extensions={"repository": binding, **(extensions or {})},
    )


def _validate_component(value: object, where: str) -> list[str]:
    if isinstance(value, str):
        return [] if value else [f"{where} string must not be empty"]
    if not isinstance(value, dict):
        return [f"{where} must be a subject id or typed component reference"]
    errors = []
    if not value.get("subject_id"):
        errors.append(f"{where}.subject_id is required")
    if value.get("kind") not in VALID_KINDS:
        errors.append(f"{where}.kind is unsupported")
    if value.get("role") not in VALID_COMPONENT_ROLES:
        errors.append(f"{where}.role is unsupported")
    fingerprint = value.get("fingerprint")
    if fingerprint and (
            not isinstance(fingerprint, str)
            or not fingerprint.startswith("sha256:")
            or len(fingerprint) != 71):
        errors.append(f"{where}.fingerprint must be sha256:<64 hex>")
    if value.get("evidence_transfer", "none") not in (
            "none", "reference-only", "explicit-mapping-required"):
        errors.append(f"{where}.evidence_transfer is unsupported")
    return errors


def validate(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["subject descriptor must be an object"]
    errors = []
    allowed = {
        "schema", "id", "kind", "display_name", "version", "components",
        "environment_fingerprint", "provenance", "privacy", "extensions",
    }
    unknown = sorted(set(value) - allowed)
    if unknown:
        errors.append("unknown subject descriptor fields: " + ", ".join(unknown))
    if value.get("schema") != SUBJECT_SCHEMA:
        errors.append(f"schema must be {SUBJECT_SCHEMA}")
    for field in ("id", "display_name"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append(f"{field} is required")
    if value.get("kind") not in VALID_KINDS:
        errors.append("kind is unsupported")
    if value.get("privacy") not in VALID_PRIVACY:
        errors.append("privacy is unsupported")
    fp = value.get("environment_fingerprint")
    if fp is not None and (
            not isinstance(fp, str)
            or not fp.startswith("sha256:")
            or len(fp) != 71):
        errors.append("environment_fingerprint must be sha256:<64 hex> or null")
    components = value.get("components", [])
    if not isinstance(components, list):
        errors.append("components must be an array")
    else:
        identities = []
        for index, component in enumerate(components):
            errors.extend(_validate_component(
                component, f"components[{index}]"))
            identities.append(
                component if isinstance(component, str)
                else component.get("subject_id"))
        if len(identities) != len(set(identities)):
            errors.append("components must identify unique subjects")
    if not isinstance(value.get("provenance", []), list):
        errors.append("provenance must be an array")
    if not isinstance(value.get("extensions", {}), dict):
        errors.append("extensions must be an object")
    return errors


def from_manifest(manifest: dict) -> dict:
    """Return a canonical descriptor from v2 or a legacy deployment run."""
    existing = manifest.get("subject")
    if isinstance(existing, dict) and existing.get("schema") == SUBJECT_SCHEMA:
        errors = validate(existing)
        if errors:
            raise SubjectError("; ".join(errors))
        return copy.deepcopy(existing)

    model = manifest.get("model") or {}
    environment = manifest.get("environment_fingerprint") or {}
    legacy = existing if isinstance(existing, dict) else {}
    subject_id = legacy.get("id") or model.get("registry_id")
    if not subject_id:
        raise SubjectError("legacy manifest has no subject or model identity")
    checksum = model.get("checksum")
    provenance = ([{
        "kind": "legacy-deployment-envelope",
        "digest": checksum,
    }] if checksum else [])
    executor_kind = legacy.get("executor_kind", "deployment")
    return build(
        subject_id,
        kind=legacy.get("kind", "ai_deployment"),
        display_name=legacy.get("display_name") or subject_id,
        environment_fingerprint=environment.get("fingerprint_hash"),
        provenance=provenance,
        privacy="internal",
        extensions={
            "legacy": {
                "manifest_schema": manifest.get("schema", "unversioned"),
                "executor_kind": executor_kind,
                "subject_kind": manifest.get("subject_kind"),
            }
        },
    )


def execution_from_manifest(manifest: dict) -> dict:
    execution = manifest.get("execution")
    if isinstance(execution, dict) and execution.get("contract"):
        return copy.deepcopy(execution)
    subject = manifest.get("subject") or {}
    model = manifest.get("model") or {}
    return {
        "contract": "aies-subject-executor/v1",
        "executor_id": (
            "runtime-generation"
            if subject.get("kind", "ai_deployment") == "ai_deployment"
            else subject.get("executor_kind", "legacy-unknown")),
        "executor_version": "legacy",
        "runtime_adapter": (
            {"deployment_id": model.get("registry_id")}
            if model.get("registry_id") else None),
        "compatibility_mode": True,
    }


def normalize_manifest(manifest: dict) -> dict:
    """Upgrade a manifest in memory while preserving every legacy field."""
    normalized = copy.deepcopy(manifest)
    normalized["schema"] = RUN_MANIFEST_SCHEMA
    normalized["subject"] = from_manifest(manifest)
    normalized["execution"] = execution_from_manifest(manifest)
    normalized.setdefault("compatibility", {})["source_manifest_schema"] = (
        manifest.get("schema", "unversioned"))
    normalized["compatibility"]["legacy_model_envelope_retained"] = bool(
        manifest.get("model"))
    return normalized


def compatibility(manifest: dict) -> dict:
    descriptor = from_manifest(manifest)
    current = manifest.get("schema") == RUN_MANIFEST_SCHEMA
    return {
        "manifest_schema": manifest.get("schema", "unversioned"),
        "current_manifest_schema": RUN_MANIFEST_SCHEMA,
        "subject_schema": descriptor["schema"],
        "mode": "native" if current else "legacy-read-compatible",
        "legacy_model_envelope_retained": bool(manifest.get("model")),
        "normalized_digest": _digest(normalize_manifest(manifest)),
        "warnings": ([] if current else [
            "legacy manifest normalized in memory; append-only source was not rewritten",
        ]),
    }

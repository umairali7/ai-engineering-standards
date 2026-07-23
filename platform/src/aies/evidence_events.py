"""Typed, content-bound evidence events and deterministic replay."""

from __future__ import annotations

import datetime
import hashlib
import json
from collections import Counter
from pathlib import Path

from . import workspace

EVENT_SCHEMA = "aies-evidence-event/v1"
EVENT_TYPES = frozenset({
    "observation", "rating", "review", "environment", "lifecycle",
    "attestation", "collection-gap",
})
MODALITIES = frozenset({
    "controlled-scenario", "integrated-system", "field-observation",
    "repository-static-analysis", "telemetry", "attestation",
    "human-rating", "automated-rating", "review-disposition",
    "environment-fingerprint", "lifecycle-transition",
})
CLASSIFICATIONS = frozenset({
    "public", "internal", "confidential", "restricted",
})
COLLECTION_CONDITIONS = frozenset({
    "not-collected", "unavailable", "tool-not-installed", "redacted",
    "failed-to-collect", "stale", "conflicting",
})


class EvidenceEventError(ValueError):
    pass


def canonical_digest(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def duplicate_identity(
    source_digest: str,
    source_record_id: str,
    adapter_profile: str,
) -> str:
    return canonical_digest({
        "source_digest": source_digest,
        "source_record_id": source_record_id,
        "adapter_profile": adapter_profile,
    })


def build(
    *,
    event_type: str,
    subject_id: str,
    modality: str,
    source: str,
    source_record_id: str,
    source_digest: str,
    adapter_profile: str,
    payload: dict,
    observed_at: str | None = None,
    instrument_id: str | None = None,
    correlation_id: str | None = None,
    classification: str = "internal",
    extensions: dict | None = None,
) -> dict:
    identity = duplicate_identity(
        source_digest, source_record_id, adapter_profile)
    event = {
        "schema": EVENT_SCHEMA,
        "event_id": "evt-" + identity.split(":", 1)[1],
        "event_type": event_type,
        "subject_id": subject_id,
        "instrument_id": instrument_id,
        "modality": modality,
        "observed_at": observed_at or datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "source": source,
        "source_record_id": source_record_id,
        "source_digest": source_digest,
        "adapter_profile": adapter_profile,
        "duplicate_identity": identity,
        "correlation_id": correlation_id,
        "classification": classification,
        "payload": payload,
        "extensions": extensions or {},
    }
    errors = validate(event)
    if errors:
        raise EvidenceEventError("; ".join(errors))
    return event


def validate(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["evidence event must be an object"]
    errors = []
    required = (
        "schema", "event_id", "event_type", "subject_id", "modality",
        "observed_at", "source", "source_record_id", "source_digest",
        "adapter_profile", "duplicate_identity", "classification", "payload",
    )
    for field in required:
        if field not in value:
            errors.append(f"{field} is required")
    if value.get("schema") != EVENT_SCHEMA:
        errors.append(f"schema must be {EVENT_SCHEMA}")
    if value.get("event_type") not in EVENT_TYPES:
        errors.append("event_type is unsupported")
    if value.get("modality") not in MODALITIES:
        errors.append("modality is unsupported")
    if value.get("classification") not in CLASSIFICATIONS:
        errors.append("classification is unsupported")
    for field in ("event_id", "subject_id", "source", "source_record_id",
                  "adapter_profile"):
        if not isinstance(value.get(field), str) or not value[field]:
            errors.append(f"{field} must be a non-empty string")
    for field in ("source_digest", "duplicate_identity"):
        digest = value.get(field)
        if (not isinstance(digest, str) or not digest.startswith("sha256:")
                or len(digest) != 71):
            errors.append(f"{field} must be sha256:<64 hex>")
    if all(value.get(field) for field in (
            "source_digest", "source_record_id", "adapter_profile")):
        expected = duplicate_identity(
            value["source_digest"], value["source_record_id"],
            value["adapter_profile"])
        if value.get("duplicate_identity") != expected:
            errors.append("duplicate_identity does not match source tuple")
        if value.get("event_id") != "evt-" + expected.split(":", 1)[1]:
            errors.append("event_id does not match duplicate identity")
    if not isinstance(value.get("payload"), dict):
        errors.append("payload must be an object")
    elif value.get("event_type") == "collection-gap":
        payload = value["payload"]
        if payload.get("collection_condition") not in COLLECTION_CONDITIONS:
            errors.append(
                "collection-gap payload.collection_condition is unsupported")
        target = payload.get("target")
        if (not isinstance(target, dict)
                or not isinstance(target.get("category"), str)
                or not target.get("category")
                or not isinstance(target.get("id"), str)
                or not target.get("id")):
            errors.append(
                "collection-gap payload.target requires category and id")
        if not isinstance(payload.get("detail"), str) or not payload["detail"]:
            errors.append("collection-gap payload.detail is required")
    if not isinstance(value.get("extensions", {}), dict):
        errors.append("extensions must be an object")
    return errors


def build_collection_gap(
    *,
    subject_id: str,
    modality: str,
    source: str,
    source_record_id: str,
    source_digest: str,
    adapter_profile: str,
    category: str,
    item_id: str,
    condition: str,
    detail: str,
    observed_at: str | None = None,
    classification: str = "internal",
) -> dict:
    """Build explicit missing-evidence metadata without fabricating evidence."""
    return build(
        event_type="collection-gap",
        subject_id=subject_id,
        modality=modality,
        source=source,
        source_record_id=source_record_id,
        source_digest=source_digest,
        adapter_profile=adapter_profile,
        observed_at=observed_at,
        classification=classification,
        payload={
            "collection_condition": condition,
            "target": {"category": category, "id": item_id},
            "detail": detail,
        },
    )


def append(run_id: str, event: dict) -> Path:
    """Append one immutable event; retries resolve to the existing identity."""
    errors = validate(event)
    if errors:
        raise EvidenceEventError("; ".join(errors))
    path = workspace.run_dir(run_id) / "events" / f"{event['event_id']}.json"
    if path.exists():
        existing = workspace.read_json(path)
        if canonical_digest(existing) == canonical_digest(event):
            return path
        raise EvidenceEventError(
            f"event identity collision for {event['event_id']}")
    workspace.write_json(path, event)
    return path


def collect(run_id: str) -> list[dict]:
    directory = workspace.run_dir(run_id) / "events"
    if not directory.exists():
        return []
    events = [workspace.read_json(path)
              for path in sorted(directory.glob("evt-*.json"))]
    for event in events:
        errors = validate(event)
        if errors:
            raise EvidenceEventError(
                f"{event.get('event_id', 'unknown')}: {'; '.join(errors)}")
    return events


def replay(events: list[dict]) -> dict:
    """Deduplicate, validate, and summarize without inventing decisions."""
    unique = {}
    duplicates = 0
    for event in events:
        errors = validate(event)
        if errors:
            raise EvidenceEventError("; ".join(errors))
        identity = event["duplicate_identity"]
        if identity in unique:
            if canonical_digest(unique[identity]) != canonical_digest(event):
                raise EvidenceEventError(
                    f"conflicting duplicate identity {identity}")
            duplicates += 1
            continue
        unique[identity] = event
    ordered = sorted(
        unique.values(),
        key=lambda event: (
            event["observed_at"], event["event_type"], event["event_id"]))
    return {
        "kind": "aies-evidence-replay",
        "schema": 1,
        "events_seen": len(events),
        "events_replayed": len(ordered),
        "duplicates_ignored": duplicates,
        "event_types": dict(sorted(Counter(
            event["event_type"] for event in ordered).items())),
        "modalities": dict(sorted(Counter(
            event["modality"] for event in ordered).items())),
        "subjects": sorted({event["subject_id"] for event in ordered}),
        "replay_digest": canonical_digest(ordered),
        "claim_boundary": (
            "Replay reconstructs event inventory only; it does not infer scores, "
            "admit evidence, or create a decision."),
    }


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def record_manifest(run_id: str, manifest: dict) -> list[Path]:
    """Record environment and current lifecycle state for a native run."""
    from . import subjects

    descriptor = subjects.from_manifest(manifest)
    paths = []
    environment = manifest.get("environment_fingerprint")
    if environment:
        paths.append(append(run_id, build(
            event_type="environment",
            subject_id=descriptor["id"],
            modality="environment-fingerprint",
            source="aies-run-manifest",
            source_record_id="manifest:environment",
            source_digest=canonical_digest(environment),
            adapter_profile="aies-native-run/v1",
            observed_at=manifest.get("created_at"),
            classification=descriptor["privacy"],
            payload={
                "fingerprint_hash": environment.get("fingerprint_hash"),
                "runtime": environment.get("runtime"),
            },
        )))
    lifecycle = {
        "run_id": run_id,
        "status": manifest.get("status"),
        "run_purpose": manifest.get("run_purpose"),
    }
    paths.append(append(run_id, build(
        event_type="lifecycle",
        subject_id=descriptor["id"],
        modality="lifecycle-transition",
        source="aies-run-manifest",
        source_record_id=f"manifest:status:{manifest.get('status', 'unknown')}",
        source_digest=canonical_digest(lifecycle),
        adapter_profile="aies-native-run/v1",
        observed_at=manifest.get("created_at"),
        classification=descriptor["privacy"],
        payload=lifecycle,
    )))
    return paths


def record_review_package(run_id: str, package_path: Path) -> Path:
    """Bind the current reviewer disposition to its immutable source bytes."""
    from . import subjects

    rdir = workspace.run_dir(run_id)
    manifest = workspace.read_json(rdir / "manifest.json")
    descriptor = subjects.from_manifest(manifest)
    package_path = Path(package_path)
    package = workspace.read_json(package_path)
    reviewer = package.get("reviewer") or {}
    human = package.get("human_consideration") or {}
    return append(run_id, build(
        event_type="review",
        subject_id=descriptor["id"],
        modality="review-disposition",
        source="aies-review-package",
        source_record_id=package_path.name,
        source_digest=_file_digest(package_path),
        adapter_profile="aies-native-run/v1",
        observed_at=package.get("generated_at") or manifest.get("created_at"),
        classification=descriptor["privacy"],
        payload={
            "reviewer": reviewer.get("label"),
            "reviewer_admitted": reviewer.get("admitted", False),
            "run_purpose": package.get("run_purpose"),
            "engineering_evaluation": package.get(
                "engineering_evaluation", {}),
            "human_consideration": human,
        },
    ))


def migrate_run(run_id: str, *, write: bool = False) -> dict:
    """Project legacy run records into typed events without rewriting sources."""
    from . import subjects

    rdir = workspace.run_dir(run_id)
    manifest_path = rdir / "manifest.json"
    if not manifest_path.exists():
        raise EvidenceEventError(f"run {run_id!r} has no manifest")
    manifest = workspace.read_json(manifest_path)
    descriptor = subjects.from_manifest(manifest)
    events = []

    for path in sorted((rdir / "responses").glob("*.json")):
        record = workspace.read_json(path)
        events.append(build(
            event_type="observation",
            subject_id=descriptor["id"],
            instrument_id=record.get("scenario_id"),
            modality="controlled-scenario",
            source="aies-response-record",
            source_record_id=path.name,
            source_digest=_file_digest(path),
            adapter_profile="aies-run-migration/v1",
            observed_at=record.get("recorded_at"),
            correlation_id=record.get("run_id"),
            classification=descriptor["privacy"],
            payload={
                "area": record.get("area"),
                "risk_tier": record.get("risk_tier"),
                "repeat": record.get("repeat"),
                "prompt_hash": (record.get("request") or {}).get("prompt_hash"),
                "response_record": path.name,
            },
        ))
    for path in sorted((rdir / "ratings").glob("*.json")):
        record = workspace.read_json(path)
        provenance = record.get("provenance") or {}
        kind = provenance.get("rater_kind", "unknown")
        events.append(build(
            event_type="rating",
            subject_id=descriptor["id"],
            instrument_id=record.get("scenario_id"),
            modality=("human-rating" if kind == "human"
                      else "automated-rating"),
            source="aies-rating-record",
            source_record_id=path.name,
            source_digest=_file_digest(path),
            adapter_profile="aies-run-migration/v1",
            observed_at=provenance.get("timestamp"),
            correlation_id=record.get("rates_response"),
            classification=descriptor["privacy"],
            payload={
                "rates_response": record.get("rates_response"),
                "rater_kind": kind,
                "scores": record.get("scores"),
                "qualification_admitted": provenance.get(
                    "qualification_admitted", False),
            },
        ))
    review_path = rdir / "review-package.json"
    if review_path.exists():
        package = workspace.read_json(review_path)
        reviewer = package.get("reviewer") or {}
        events.append(build(
            event_type="review",
            subject_id=descriptor["id"],
            modality="review-disposition",
            source="aies-review-package",
            source_record_id=review_path.name,
            source_digest=_file_digest(review_path),
            adapter_profile="aies-run-migration/v1",
            observed_at=package.get("generated_at") or manifest.get("created_at"),
            classification=descriptor["privacy"],
            payload={
                "reviewer": reviewer.get("label"),
                "reviewer_admitted": reviewer.get("admitted", False),
                "run_purpose": package.get("run_purpose"),
                "engineering_evaluation": package.get(
                    "engineering_evaluation", {}),
                "human_consideration": package.get(
                    "human_consideration", {}),
            },
        ))
    environment = manifest.get("environment_fingerprint")
    if environment:
        events.append(build(
            event_type="environment",
            subject_id=descriptor["id"],
            modality="environment-fingerprint",
            source="aies-run-manifest",
            source_record_id="manifest:environment",
            source_digest=_file_digest(manifest_path),
            adapter_profile="aies-run-migration/v1",
            observed_at=manifest.get("created_at"),
            classification=descriptor["privacy"],
            payload={
                "fingerprint_hash": environment.get("fingerprint_hash"),
                "runtime": environment.get("runtime"),
            },
        ))
    events.append(build(
        event_type="lifecycle",
        subject_id=descriptor["id"],
        modality="lifecycle-transition",
        source="aies-run-manifest",
        source_record_id="manifest:run-status",
        source_digest=_file_digest(manifest_path),
        adapter_profile="aies-run-migration/v1",
        observed_at=manifest.get("created_at"),
        classification=descriptor["privacy"],
        payload={
            "run_id": run_id,
            "status": manifest.get("status"),
            "run_purpose": manifest.get("run_purpose"),
        },
    ))
    paths = []
    if write:
        paths = [str(append(run_id, event)) for event in events]
    return {
        "run_id": run_id,
        "source_manifest": subjects.compatibility(manifest),
        "events": events,
        "events_written": len(paths),
        "paths": paths,
        "replay": replay(events),
        "source_records_unchanged": True,
    }

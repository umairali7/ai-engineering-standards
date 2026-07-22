"""Durable human-rater registry for qualification evidence admission.

Names in a scoresheet are provenance, not proof of qualification.  ADR-0012
requires a durable identity with competency/risk scope and current calibration;
this module owns that versioned record and evaluates it against a run.
"""

from __future__ import annotations

import datetime

from . import constants as C, workspace

RATER_SCHEMA = 1


class RaterError(Exception):
    pass


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _parse_time(value: str, field: str) -> datetime.datetime:
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise RaterError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def _dir():
    path = workspace.ensure() / "raters"
    path.mkdir(parents=True, exist_ok=True)
    return path


def register(
    rater_id: str,
    name: str,
    *,
    competency_areas: list[str],
    risk_tiers: list[str],
    qualified_until: str,
    calibration_valid_until: str,
    anchor_library_version: str,
    registered_by: str,
    calibration_method: str = "human-consensus-anchor-session",
) -> dict:
    """Create an immutable qualification/calibration record for one human."""
    if not rater_id or not all(c.isalnum() or c in "-_" for c in rater_id):
        raise RaterError("rater id must contain only letters, numbers, '-' or '_'")
    if not name or not name.strip():
        raise RaterError("a human rater name is required")
    if not registered_by or not registered_by.strip():
        raise RaterError("a named registry authority is required")
    areas = sorted(set(competency_areas))
    invalid_areas = [area for area in areas
                     if not (area.startswith("CA-") and area[3:].isdigit())]
    if not areas or invalid_areas:
        raise RaterError(f"invalid or empty competency scope: {invalid_areas}")
    tiers = sorted(set(risk_tiers), key=lambda tier: C.RISK_TIERS.index(tier)
                   if tier in C.RISK_TIERS else 99)
    invalid_tiers = [tier for tier in tiers if tier not in C.RISK_TIERS]
    if not tiers or invalid_tiers:
        raise RaterError(f"invalid or empty risk-tier scope: {invalid_tiers}")
    qualified = _parse_time(qualified_until, "qualified_until")
    calibrated = _parse_time(calibration_valid_until, "calibration_valid_until")
    if qualified <= _now() or calibrated <= _now():
        raise RaterError("qualification and calibration must be current at registration")
    if not anchor_library_version.strip():
        raise RaterError("anchor_library_version is required")
    record = {
        "kind": "human-rater-record",
        "rater_schema": RATER_SCHEMA,
        "rater_id": rater_id,
        "name": name.strip(),
        "status": "active",
        "qualification": {
            "competency_areas": areas,
            "risk_tiers": tiers,
            "valid_until": qualified.isoformat(),
        },
        "calibration": {
            "competency_areas": areas,
            "method": calibration_method,
            "anchor_library_version": anchor_library_version.strip(),
            "valid_until": calibrated.isoformat(),
        },
        "registered_at": _now().isoformat(),
        "registered_by": registered_by.strip(),
    }
    path = _dir() / f"{rater_id}.json"
    if path.exists():
        raise RaterError(
            f"human rater {rater_id!r} already exists; durable rater records are immutable")
    workspace.write_json(path, record)
    return record


def get(rater_id: str) -> dict:
    path = _dir() / f"{rater_id}.json"
    if not path.exists():
        raise RaterError(f"no registered human rater {rater_id!r}")
    return workspace.read_json(path)


def list_records() -> list[dict]:
    return [workspace.read_json(path) for path in sorted(_dir().glob("*.json"))]


def assess_for_run(
    run_id: str,
    declaration: dict,
    *,
    competency_areas: set[str] | None = None,
) -> tuple[bool, list[str], dict | None]:
    """Verify identity, scope, calibration, and per-run conflict declaration."""
    rater_id = declaration.get("id")
    if not rater_id:
        return False, ["missing durable rater id"], None
    try:
        record = get(str(rater_id))
    except RaterError as exc:
        return False, [str(exc)], None
    manifest = workspace.read_json(workspace.run_dir(run_id) / "manifest.json")
    run_areas = {area["area"] for area in manifest.get("areas", [])}
    areas = set(competency_areas) if competency_areas is not None else run_areas
    if not areas or not areas.issubset(run_areas):
        return False, ["rating competency scope is empty or outside the run scope"], None
    rt = manifest.get("risk_tier")
    reasons = []
    declared_name = str(declaration.get("name") or "").strip()
    if not declared_name:
        reasons.append("rater name is missing")
    elif declared_name.casefold() != str(record.get("name") or "").strip().casefold():
        reasons.append("declared rater name does not match the durable rater record")
    if record.get("status") != "active":
        reasons.append("rater record is not active")
    qualification = record.get("qualification") or {}
    calibration = record.get("calibration") or {}
    if not areas.issubset(set(qualification.get("competency_areas") or [])):
        reasons.append("rater qualification does not cover every run competency")
    if rt not in (qualification.get("risk_tiers") or []):
        reasons.append("rater qualification does not cover the run risk tier")
    if not areas.issubset(set(calibration.get("competency_areas") or [])):
        reasons.append("rater calibration does not cover every run competency")
    for field, value in (("qualification", qualification.get("valid_until")),
                         ("calibration", calibration.get("valid_until"))):
        try:
            if _parse_time(value, f"{field}.valid_until") <= _now():
                reasons.append(f"rater {field} is expired")
        except RaterError as exc:
            reasons.append(str(exc))
    conflict = declaration.get("conflict_declaration") or {}
    if conflict.get("declared") is not True:
        reasons.append("independence/conflict declaration is missing")
    if conflict.get("has_conflict") is not False:
        reasons.append("rater declared a conflict or did not explicitly declare conflict-free")
    subject_id = (manifest.get("subject") or {}).get("id") or manifest["model"]["registry_id"]
    if conflict.get("subject_id") != subject_id:
        reasons.append("conflict declaration is not bound to this subject")
    snapshot = {
        "rater_schema": record.get("rater_schema"),
        "rater_id": record.get("rater_id"),
        "name": record.get("name"),
        "qualification": qualification,
        "calibration": calibration,
        "conflict_declaration": conflict,
    }
    return not reasons, reasons, snapshot

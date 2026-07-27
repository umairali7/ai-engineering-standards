"""Evidence-linked Assessment Coverage Matrix and blind-spot reporting."""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from . import assessment_profiles, subjects, workspace


SCHEMA = "aies-assessment-coverage/v1"
RUNTIME_STATES = (
    "assessed", "partially-assessed", "not-assessed",
    "not-applicable", "unsupported",
)
COLLECTION_CONDITIONS = (
    "current", "not-collected", "not-requested", "unavailable",
    "tool-not-installed", "redacted", "failed-to-collect", "stale",
    "conflicting", "not-applicable", "unsupported",
)
CONFIDENCE_LEVELS = ("none", "low", "moderate", "high")


class CoverageError(ValueError):
    pass


def _skeleton(profile: dict, subject: dict, evidence_scope: dict) -> dict:
    expanded = assessment_profiles.expand_applicability(profile)
    categories = {}
    for category_id, category in expanded.items():
        cells = []
        for item in category["items"]:
            applicability = item["status"]
            status = (
                "not-assessed" if applicability == "applicable"
                else applicability)
            condition = (
                "not-collected" if applicability == "applicable"
                else applicability)
            cells.append({
                "id": item["id"],
                "title": item["title"],
                **({"value": item["value"]} if item.get("value") else {}),
                "applicability": applicability,
                "status": status,
                "rationale": item["rationale"],
                "evidence_refs": [],
                "evidence_count": 0,
                "condition_refs": [],
                "collection_condition": condition,
                "evidence_depth": {
                    "direct_events": 0,
                    "distinct_instruments": 0,
                    "distinct_sources": 0,
                    "modalities": [],
                    "adapters": [],
                },
                "evidence_confidence": {
                    "level": "none",
                    "scope": "evidence-coverage-only",
                    "basis": ["No direct evidence is referenced."],
                },
                "freshness": {
                    "status": "not-established",
                    "latest_observed_at": None,
                    "age_days": None,
                    "max_age_days": profile[
                        "freshness_policy"]["default_max_age_days"],
                    "change_trigger_evaluated": False,
                    "basis": (
                        "Elapsed-age policy only; declared change triggers "
                        "were not evaluated."),
                },
                "conflicts": [],
                "component_overlap": [],
            })
        categories[category_id] = {
            "title": category["title"],
            "cells": cells,
            "summary": {},
        }
    return {
        "kind": "aies-assessment-coverage-matrix",
        "schema": SCHEMA,
        "profile": {
            "id": profile["id"],
            "title": profile["title"],
            "version": profile["version"],
            "status": profile["status"],
            "governed_by": profile["governed_by"],
            "freshness_policy": profile["freshness_policy"],
        },
        "subject": subject,
        "evidence_scope": evidence_scope,
        "categories": categories,
        "summary": {},
        "blind_spots": [],
        "evidence_reuse": {},
        "component_evidence": [],
        "integrity_summary": {},
        "limitations": list(profile["limitations"]),
        "claim_boundary": (
            "Coverage describes direct evidence availability and declared "
            "applicability. It is not subject quality, correctness, safety, "
            "maturity, capability, qualification, deployment readiness, or "
            "authorization."),
    }


def _cell(matrix: dict, category_id: str, item_id: str) -> dict:
    try:
        return next(
            item for item in matrix["categories"][category_id]["cells"]
            if item["id"] == item_id)
    except (KeyError, StopIteration) as error:
        raise CoverageError(
            f"unknown coverage cell {category_id}/{item_id}") from error


def _observe(
    matrix: dict,
    category_id: str,
    item_id: str,
    *,
    status: str,
    evidence_refs: list[str],
    rationale: str,
) -> None:
    if status not in ("assessed", "partially-assessed"):
        raise CoverageError("direct observations must be assessed or partial")
    cell = _cell(matrix, category_id, item_id)
    if cell["applicability"] != "applicable":
        raise CoverageError(
            f"evidence cannot fill {cell['applicability']} cell "
            f"{category_id}/{item_id}")
    cell["status"] = status
    cell["evidence_refs"] = sorted(set(evidence_refs))
    cell["evidence_count"] = len(cell["evidence_refs"])
    cell["rationale"] = rationale
    cell["collection_condition"] = "current"


def _set_condition(
    matrix: dict,
    category_id: str,
    item_id: str,
    condition: str,
    detail: str,
    *,
    evidence_ref: str | None = None,
) -> None:
    """Attach an explicit collection condition without filling the cell."""
    if condition not in COLLECTION_CONDITIONS:
        raise CoverageError(f"unsupported collection condition {condition}")
    cell = _cell(matrix, category_id, item_id)
    if cell["applicability"] != "applicable":
        if condition != cell["applicability"]:
            raise CoverageError(
                f"cannot attach {condition} to {cell['applicability']} cell "
                f"{category_id}/{item_id}")
        return
    cell["collection_condition"] = condition
    cell["rationale"] = detail
    if evidence_ref:
        cell["condition_refs"].append(evidence_ref)


def _events_by(events: list[dict], key) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for event in events:
        value = key(event)
        if value:
            grouped[value].append(event["event_id"])
    return grouped


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return (
            parsed.replace(tzinfo=timezone.utc)
            if parsed.tzinfo is None else parsed.astimezone(timezone.utc))
    except ValueError:
        return None


def _catalog(events: list[dict], conflict_instruments: dict[str, dict]) -> dict:
    catalog = {}
    for event in events:
        instrument = event.get("instrument_id")
        catalog[event["event_id"]] = {
            "kind": "event",
            "event_type": event.get("event_type"),
            "subject_id": event.get("subject_id"),
            "instrument_id": instrument,
            "modality": event.get("modality"),
            "source": event.get("source"),
            "adapter": event.get("adapter_profile"),
            "observed_at": event.get("observed_at"),
            "correlation_id": event.get("correlation_id"),
            "source_digest": event.get("source_digest"),
            "conflict": conflict_instruments.get(instrument),
        }
    return catalog


def _component_evidence(descriptor: dict, events: list[dict]) -> list[dict]:
    counts = Counter(
        event.get("subject_id") for event in events
        if event.get("event_type") != "collection-gap")
    result = []
    for value in descriptor.get("components") or []:
        component = (
            {"subject_id": value, "kind": None, "role": None,
             "version": None, "fingerprint": None,
             "evidence_transfer": "none"}
            if isinstance(value, str) else value)
        transfer = component.get("evidence_transfer", "none")
        result.append({
            "subject_id": component["subject_id"],
            "kind": component.get("kind"),
            "role": component.get("role"),
            "version": component.get("version"),
            "fingerprint": component.get("fingerprint"),
            "evidence_transfer": transfer,
            "observed_event_count": counts[component["subject_id"]],
            "coverage_use": (
                "prohibited" if transfer == "none" else
                "reference-only" if transfer == "reference-only" else
                "requires-explicit-mapping"),
            "mapped_into_parent_cells": 0,
            "rationale": (
                "Component evidence is disclosed but never fills parent "
                "coverage without an explicit governed mapping."),
        })
    return result


def _confidence(
    cell: dict,
    *,
    instruments: set[str],
    sources: set[str],
    modalities: set[str],
) -> dict:
    basis = []
    if not cell["evidence_refs"]:
        return {
            "level": "none", "scope": "evidence-coverage-only",
            "basis": ["No direct evidence is referenced."],
        }
    if cell["collection_condition"] in (
            "stale", "conflicting", "redacted", "failed-to-collect"):
        level = "low"
        basis.append(
            f"Collection condition is {cell['collection_condition']}.")
    elif cell["status"] == "partially-assessed" or len(instruments) < 2:
        level = "low"
        basis.append("Evidence is partial or has fewer than two instruments.")
    elif (cell["status"] == "assessed" and len(instruments) >= 5
          and len(modalities) >= 2):
        level = "high"
        basis.append(
            "At least five instruments and two direct modalities are present.")
    else:
        level = "moderate"
        basis.append("Multiple direct instruments support the coverage cell.")
    basis.append(
        f"{len(sources)} source type(s), {len(instruments)} instrument(s), "
        f"and {len(modalities)} modality type(s) are represented.")
    return {
        "level": level,
        "scope": "evidence-coverage-only",
        "basis": basis,
    }


def _finalize(matrix: dict, evidence_catalog: dict | None = None) -> dict:
    evidence_catalog = evidence_catalog or {}
    generated_at = datetime.now(timezone.utc)
    matrix["generated_at"] = generated_at.isoformat()
    evidence_usage: dict[str, list[str]] = defaultdict(list)
    correlations: dict[str, set[str]] = defaultdict(set)
    source_digests: dict[str, set[str]] = defaultdict(set)
    overall = Counter()
    conditions = Counter()
    confidence_levels = Counter()
    blind_spots = []
    for category_id, category in matrix["categories"].items():
        counts = Counter(cell["status"] for cell in category["cells"])
        category["summary"] = {
            state: counts[state] for state in RUNTIME_STATES
        }
        category["summary"]["total"] = len(category["cells"])
        applicable = sum(
            counts[state] for state in (
                "assessed", "partially-assessed", "not-assessed"))
        category["summary"]["direct_coverage_percent"] = (
            round(
                (counts["assessed"] + 0.5 * counts["partially-assessed"])
                / applicable * 100, 1)
            if applicable else None
        )
        overall.update(counts)
        for cell in category["cells"]:
            cell_path = f"{category_id}/{cell['id']}"
            metadata = [
                evidence_catalog[reference]
                for reference in cell["evidence_refs"]
                if reference in evidence_catalog
            ]
            direct_events = [
                item for item in metadata if item.get("kind") == "event"]
            component_ids = {
                item["subject_id"]
                for item in matrix["component_evidence"]}
            cell["component_overlap"] = sorted({
                item["subject_id"] for item in direct_events
                if item.get("subject_id") in component_ids
            })
            instruments = {
                item["instrument_id"] for item in direct_events
                if item.get("instrument_id")}
            sources = {
                item["source"] for item in direct_events
                if item.get("source")}
            modalities = {
                item["modality"] for item in direct_events
                if item.get("modality")}
            adapters = {
                item["adapter"] for item in direct_events
                if item.get("adapter")}
            conflicts = {
                json.dumps(item["conflict"], sort_keys=True)
                for item in direct_events if item.get("conflict")}
            cell["conflicts"] = [
                json.loads(item) for item in sorted(conflicts)]
            if cell["conflicts"]:
                cell["collection_condition"] = "conflicting"
            observed_times = sorted(
                parsed for parsed in (
                    _parse_time(item.get("observed_at"))
                    for item in direct_events)
                if parsed is not None)
            latest = observed_times[-1] if observed_times else None
            max_age = cell["freshness"]["max_age_days"]
            age_days = (
                max(0.0, (generated_at - latest).total_seconds() / 86400)
                if latest else None)
            freshness_status = "not-established"
            if latest:
                freshness_status = (
                    "stale" if age_days > max_age else "current")
            cell["freshness"] = {
                "status": freshness_status,
                "latest_observed_at": (
                    latest.isoformat() if latest else None),
                "age_days": round(age_days, 3) if age_days is not None else None,
                "max_age_days": max_age,
                "change_trigger_evaluated": False,
                "basis": (
                    "Elapsed-age policy only; declared change triggers were "
                    "not evaluated."),
            }
            if (freshness_status == "stale"
                    and cell["collection_condition"] == "current"):
                cell["collection_condition"] = "stale"
            cell["evidence_depth"] = {
                "direct_events": len(direct_events),
                "distinct_instruments": len(instruments),
                "distinct_sources": len(sources),
                "modalities": sorted(modalities),
                "adapters": sorted(adapters),
            }
            cell["evidence_confidence"] = _confidence(
                cell, instruments=instruments, sources=sources,
                modalities=modalities)
            conditions[cell["collection_condition"]] += 1
            confidence_levels[cell["evidence_confidence"]["level"]] += 1
            for reference in cell["evidence_refs"]:
                evidence_usage[reference].append(cell_path)
                item = evidence_catalog.get(reference) or {}
                if item.get("correlation_id"):
                    correlations[item["correlation_id"]].add(reference)
                if item.get("source_digest"):
                    source_digests[item["source_digest"]].add(reference)
            if (cell["status"] in (
                    "partially-assessed", "not-assessed", "unsupported")
                    or cell["collection_condition"] in (
                        "unavailable", "tool-not-installed", "redacted",
                        "failed-to-collect", "stale", "conflicting")):
                blind_spots.append({
                    "category": category_id,
                    "category_title": category["title"],
                    "id": cell["id"],
                    "title": cell["title"],
                    "status": cell["status"],
                    "collection_condition": cell["collection_condition"],
                    "evidence_confidence": cell["evidence_confidence"]["level"],
                    "evidence_refs": list(cell["evidence_refs"]),
                    "condition_refs": list(cell["condition_refs"]),
                    "rationale": cell["rationale"],
                    "next_evidence": (
                        "Implement a direct evidence path in the Subject "
                        "Assessment Profile."
                        if cell["status"] == "unsupported" else
                        "Resolve or recollect compromised evidence."
                        if cell["collection_condition"] in (
                            "redacted", "failed-to-collect", "stale",
                            "conflicting") else
                        "Collect distinct direct evidence for this perspective."
                    ),
                })
    applicable = sum(
        overall[state] for state in (
            "assessed", "partially-assessed", "not-assessed"))
    matrix["summary"] = {
        **{state: overall[state] for state in RUNTIME_STATES},
        "total_cells": sum(overall.values()),
        "applicable_cells": applicable,
        "direct_coverage_percent": (
            round(
                (overall["assessed"] + 0.5 * overall["partially-assessed"])
                / applicable * 100, 1)
            if applicable else None
        ),
        "blind_spots": len(blind_spots),
        "collection_conditions": {
            condition: conditions[condition]
            for condition in COLLECTION_CONDITIONS},
        "evidence_confidence": {
            level: confidence_levels[level]
            for level in CONFIDENCE_LEVELS},
    }
    matrix["blind_spots"] = sorted(
        blind_spots,
        key=lambda item: (
            {"unsupported": 0, "not-assessed": 1,
             "partially-assessed": 2}.get(item["status"], 3),
            {
                "conflicting": 0, "failed-to-collect": 1, "stale": 2,
                "redacted": 3, "tool-not-installed": 4,
                "unavailable": 5,
            }.get(item["collection_condition"], 6),
            item["category"], item["id"]),
    )
    reused = [
        {"evidence_ref": reference, "referenced_by": paths,
         "reference_count": len(paths)}
        for reference, paths in sorted(evidence_usage.items())
        if len(paths) > 1
    ]
    matrix["evidence_reuse"] = {
        "cell_references": sum(len(paths) for paths in evidence_usage.values()),
        "unique_evidence_refs": len(evidence_usage),
        "reused_evidence_refs": len(reused),
        "reused": reused,
        "correlated_groups": [
            {"correlation_id": key, "evidence_refs": sorted(refs),
             "evidence_count": len(refs)}
            for key, refs in sorted(correlations.items())
            if len(refs) > 1
        ],
        "shared_source_groups": [
            {"source_digest": key, "evidence_refs": sorted(refs),
             "evidence_count": len(refs)}
            for key, refs in sorted(source_digests.items())
            if len(refs) > 1
        ],
        "policy": (
            "One canonical evidence identity may explain multiple cells but "
            "is counted once as unique evidence and cannot inflate assurance."),
    }
    matrix["integrity_summary"] = {
        "stale_cells": conditions["stale"],
        "conflicting_cells": conditions["conflicting"],
        "failed_collection_cells": conditions["failed-to-collect"],
        "redacted_cells": conditions["redacted"],
        "correlated_evidence_groups": len(
            matrix["evidence_reuse"]["correlated_groups"]),
        "shared_source_groups": len(
            matrix["evidence_reuse"]["shared_source_groups"]),
        "component_count": len(matrix["component_evidence"]),
        "component_evidence_refs": sum(
            item["observed_event_count"]
            for item in matrix["component_evidence"]),
        "claim_boundary": (
            "Confidence describes evidence coverage only. It does not estimate "
            "subject correctness, capability, safety, or decision certainty. "
            "Freshness is age-based in this artifact; declared change triggers "
            "remain unevaluated and may require recollection sooner."),
    }
    return matrix


def for_run(run_id: str, *, capability_matrix: dict | None = None) -> dict:
    """Build coverage for a deployment run without changing its evidence."""
    from . import ecm, evidence_events, rating

    rdir = workspace.run_dir(run_id)
    manifest_path = rdir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"run {run_id!r} has no manifest")
    manifest = workspace.read_json(manifest_path)
    descriptor = subjects.from_manifest(manifest)
    profile = assessment_profiles.get_profile(descriptor["kind"])
    matrix = _skeleton(
        profile, descriptor,
        {
            "kind": "run",
            "id": run_id,
            "risk_tier": manifest.get("risk_tier"),
            "read_only_derivation": True,
        })
    events = evidence_events.collect(run_id)
    if not events:
        # Older native runs predate the append-only event directory. Project
        # their immutable response/rating records through the governed
        # migration adapter in memory; never rewrite the source run merely to
        # render coverage.
        events = evidence_events.migrate_run(run_id, write=False)["events"]
    direct_events = [
        event for event in events
        if event.get("event_type") != "collection-gap"
        and event.get("subject_id") == descriptor["id"]]
    gap_events = [
        event for event in events
        if event.get("event_type") == "collection-gap"
        and event.get("subject_id") == descriptor["id"]]
    by_area = _events_by(
        direct_events, lambda event: event.get("payload", {}).get("area"))
    by_scenario = _events_by(
        direct_events, lambda event: event.get("instrument_id"))
    by_modality = _events_by(
        direct_events, lambda event: event.get("modality"))
    conflict_instruments = {}
    if (rdir / "ratings").is_dir():
        for item in rating.resolve_evidence_items(run_id):
            if item["status"] == "unresolved-major-divergence":
                conflict_instruments[item["scenario_id"]] = {
                    "kind": "unresolved-major-rater-divergence",
                    "evidence_item_id": item["evidence_item_id"],
                    "max_dimension_delta": item["max_dimension_delta"],
                }
    catalog = _catalog(events, conflict_instruments)
    matrix["component_evidence"] = _component_evidence(descriptor, events)

    package_path = rdir / "evidence-package.json"
    package = workspace.read_json(package_path) if package_path.exists() else None
    if package:
        for area_id, area in package.get("areas", {}).items():
            scored = int(area.get("n_scored") or 0)
            if scored <= 0:
                continue
            minimum = int(area.get("min_sample") or scored)
            _observe(
                matrix, "competencies", area_id,
                status=("assessed" if scored >= minimum
                        else "partially-assessed"),
                evidence_refs=by_area.get(area_id, []),
                rationale=(
                    f"{scored} distinct resolved evidence item(s) against "
                    f"the {minimum}-item scoped minimum."))
        capability = (
            capability_matrix
            if capability_matrix is not None
            else ecm.engineering_capability_matrix(run_id))
        for task in capability["tasks"]:
            observed = int(task.get("distinct_scenarios") or 0)
            if observed <= 0:
                continue
            minimum = int(task.get("minimum_observations") or observed)
            refs = []
            for scenario_id in task.get("scenario_ids") or []:
                refs.extend(by_scenario.get(scenario_id, []))
            _observe(
                matrix, "engineering_tasks", task["task_id"],
                status=("assessed" if observed >= minimum
                        else "partially-assessed"),
                evidence_refs=refs,
                rationale=(
                    f"{observed} directly mapped distinct scenario(s) "
                    f"against the {minimum}-scenario task target."))

    risk_tier = manifest.get("risk_tier")
    if risk_tier:
        _observe(
            matrix, "risk_tiers", risk_tier,
            status="assessed",
            evidence_refs=["record:manifest.json"],
            rationale=(
                f"The run is explicitly scoped to {risk_tier}; other tiers "
                "are not inferred from this evidence."))

    perspectives = assessment_profiles.load_perspectives()
    for item in perspectives["categories"]["evidence_modalities"]["items"]:
        refs = by_modality.get(item.get("value"), [])
        if refs and _cell(
                matrix, "evidence_modalities", item["id"]
        )["applicability"] == "applicable":
            _observe(
                matrix, "evidence_modalities", item["id"],
                status="assessed",
                evidence_refs=refs,
                rationale=(
                    f"{len(set(refs))} canonical event(s) directly use the "
                    f"{item['title']} modality."))
    if not by_modality.get("human-rating"):
        _set_condition(
            matrix, "evidence_modalities", "EM-08", "not-requested",
            "No human rating was requested or retained; human evaluation is "
            "optional for Engineering Evaluation and separately governed for "
            "formal qualification.")

    manifest_status = str(manifest.get("status") or "")
    if manifest_status in ("collection-partial", "collection-failed"):
        collected_by_area = Counter(
            workspace.read_json(path).get("area")
            for path in (rdir / "responses").glob("*.json"))
        for area in manifest.get("areas") or []:
            area_id = area.get("area")
            planned = int(area.get("planned_items") or 0)
            collected = collected_by_area[area_id]
            if area_id and collected < planned:
                _set_condition(
                    matrix, "competencies", area_id, "failed-to-collect",
                    f"Collection stopped after {collected}/{planned} planned "
                    "response(s); the run remains resumable.")
    for event in gap_events:
        payload = event["payload"]
        target = payload["target"]
        _set_condition(
            matrix, target["category"], target["id"],
            payload["collection_condition"], payload["detail"],
            evidence_ref=event["event_id"])

    product_files = {
        "DP-01": "engineering-evaluation.json",
        "DP-02": "engineering-capability-matrix.json",
        "DP-03": "engineering-fit-guidance.json",
        "DP-04": "assessment-result.json",
        "DP-09": "executive-summary.json",
    }
    for product_id, filename in product_files.items():
        if (rdir / filename).is_file():
            _observe(
                matrix, "decision_products", product_id,
                status="assessed",
                evidence_refs=[f"artifact:{filename}"],
                rationale=f"The run bundle contains {filename}.")
    _observe(
        matrix, "decision_products", "DP-11",
        status="assessed",
        evidence_refs=["derived:assessment-coverage"],
        rationale="This coverage and blind-spot product was generated.")
    if _cell(matrix, "decision_products", "DP-07")[
            "applicability"] == "applicable":
        _observe(
            matrix, "decision_products", "DP-07",
            status="assessed",
            evidence_refs=["derived:evidence-remediation-plan"],
            rationale=(
                "Coverage gaps produce a deterministic evidence-linked action "
                "plan without assigning an owner or closing risk."))
    monitoring_refs = (
        by_modality.get("field-observation", [])
        + by_modality.get("telemetry", []))
    if monitoring_refs and _cell(
            matrix, "decision_products", "DP-10"
    )["applicability"] == "applicable":
        _observe(
            matrix, "decision_products", "DP-10",
            status="partially-assessed",
            evidence_refs=monitoring_refs,
            rationale=(
                "Field or telemetry evidence is linked to reassessment; "
                "threshold ownership and operational response remain external."))
    return _finalize(matrix, catalog)


def for_repository(result: dict) -> dict:
    """Build coverage from one stored or in-memory repository assessment."""
    descriptor = result.get("subject") or {}
    profile = assessment_profiles.get_profile(descriptor.get("kind", "repository"))
    matrix = _skeleton(
        profile, descriptor,
        {
            "kind": "repository-assessment",
            "id": result.get("audit_id"),
            "risk_tier": (result.get("gate") or {}).get("risk_tier"),
            "read_only_derivation": True,
            "scope_notice": result.get("scope_notice"),
        })
    events = result.get("events") or []
    direct_events = [
        event for event in events
        if event.get("event_type") != "collection-gap"
        and event.get("subject_id") == descriptor.get("id")]
    gap_events = [
        event for event in events
        if event.get("event_type") == "collection-gap"
        and event.get("subject_id") == descriptor.get("id")]
    by_area = _events_by(
        direct_events, lambda event: event.get("payload", {}).get("area"))
    by_modality = _events_by(
        direct_events, lambda event: event.get("modality"))
    catalog = _catalog(events, {})
    matrix["component_evidence"] = _component_evidence(descriptor, events)
    for area_id, area in (result.get("areas") or {}).items():
        refs = by_area.get(area_id, [])
        if refs:
            _observe(
                matrix, "competencies", area_id,
                status="assessed",
                evidence_refs=refs,
                rationale=(
                    f"{area.get('n_checks', len(refs))} repository-practice "
                    "check(s) completed; gaps remain evidence, not passes."))
    risk_tier = (result.get("gate") or {}).get("risk_tier")
    if risk_tier:
        _observe(
            matrix, "risk_tiers", risk_tier,
            status="assessed",
            evidence_refs=["record:repository-gate-policy"],
            rationale=(
                f"Repository conformance was explicitly calculated for "
                f"{risk_tier}."))
    perspectives = assessment_profiles.load_perspectives()
    for item in perspectives["categories"]["evidence_modalities"]["items"]:
        refs = by_modality.get(item.get("value"), [])
        cell = _cell(matrix, "evidence_modalities", item["id"])
        if refs and cell["applicability"] == "applicable":
            _observe(
                matrix, "evidence_modalities", item["id"],
                status="assessed",
                evidence_refs=refs,
                rationale=(
                    f"{len(set(refs))} canonical repository event(s) directly "
                    f"use the {item['title']} modality."))
    products = ["DP-05", "DP-07", "DP-09", "DP-11"]
    if result.get("engineering_analysis"):
        products += ["DP-06", "DP-07"]
    for product_id in products:
        _observe(
            matrix, "decision_products", product_id,
            status="assessed",
            evidence_refs=[
                "derived:assessment-coverage"
                if product_id == "DP-11"
                else f"record:{result.get('audit_id') or 'repository-assessment'}"
            ],
            rationale=(
                "This coverage and blind-spot product was generated."
                if product_id == "DP-11" else
                "The repository assessment contains this decision product."))
    for event in gap_events:
        payload = event["payload"]
        target = payload["target"]
        _set_condition(
            matrix, target["category"], target["id"],
            payload["collection_condition"], payload["detail"],
            evidence_ref=event["event_id"])
    monitoring_refs = (
        by_modality.get("field-observation", [])
        + by_modality.get("telemetry", []))
    if monitoring_refs and _cell(
            matrix, "decision_products", "DP-10"
    )["applicability"] == "applicable":
        _observe(
            matrix, "decision_products", "DP-10",
            status="partially-assessed",
            evidence_refs=monitoring_refs,
            rationale=(
                "Field or telemetry evidence is linked to reassessment; "
                "threshold ownership and operational response remain external."))
    return _finalize(matrix, catalog)


def for_reference(reference: str) -> dict:
    audit_path = workspace.root() / "audits" / f"{reference}.json"
    if audit_path.is_file():
        return for_repository(workspace.read_json(audit_path))
    return for_run(reference)


def render_markdown(matrix: dict) -> str:
    """Render coverage, integrity, correlation, and dependency boundaries."""
    summary = matrix["summary"]
    integrity = matrix["integrity_summary"]
    lines = [
        "# AIES Assessment Coverage & Blind Spots",
        "",
        "> **INFORMATIONAL — COVERAGE IS NOT QUALITY, QUALIFICATION, OR "
        "AUTHORIZATION.**",
        "",
        f"**Profile:** `{matrix['profile']['id']}` — "
        f"{matrix['profile']['title']} v{matrix['profile']['version']}  ",
        f"**Subject:** `{matrix['subject'].get('id', 'unknown')}` — "
        f"{matrix['subject'].get('display_name', 'Unknown subject')}  ",
        f"**Evidence scope:** `{matrix['evidence_scope'].get('kind')}` "
        f"`{matrix['evidence_scope'].get('id') or 'in-memory'}`",
        "",
        "## Coverage Summary",
        "",
        "| State | Cells |",
        "|---|---:|",
        f"| Assessed | {summary['assessed']} |",
        f"| Partially assessed | {summary['partially-assessed']} |",
        f"| Not assessed | {summary['not-assessed']} |",
        f"| Unsupported | {summary['unsupported']} |",
        f"| Not applicable | {summary['not-applicable']} |",
        "",
        f"Direct applicable-cell coverage: "
        f"**{summary['direct_coverage_percent'] or 0:.1f}%**. "
        "This percentage describes evidence availability only.",
        "",
        "## Evidence Integrity",
        "",
        "| Signal | Count |",
        "|---|---:|",
        f"| Stale cells | {integrity['stale_cells']} |",
        f"| Conflicting cells | {integrity['conflicting_cells']} |",
        f"| Failed collection cells | {integrity['failed_collection_cells']} |",
        f"| Redacted cells | {integrity['redacted_cells']} |",
        f"| Correlated evidence groups | "
        f"{integrity['correlated_evidence_groups']} |",
        f"| Shared-source groups | {integrity['shared_source_groups']} |",
        "",
        integrity["claim_boundary"],
        "",
    ]
    for category in matrix["categories"].values():
        lines += [
            f"## {category['title']}",
            "",
            "| Perspective | Coverage | Collection | Evidence confidence | "
            "Depth | Evidence | Rationale |",
            "|---|---|---|---|---|---:|---|",
        ]
        for cell in category["cells"]:
            depth = cell["evidence_depth"]
            lines.append(
                f"| `{cell['id']}` — {cell['title']} | "
                f"{cell['status']} | {cell['collection_condition']} | "
                f"{cell['evidence_confidence']['level']} | "
                f"{depth['direct_events']} events / "
                f"{depth['distinct_instruments']} instruments / "
                f"{depth['distinct_sources']} sources | "
                f"{cell['evidence_count']} | {cell['rationale']} |")
        lines.append("")
    reuse = matrix["evidence_reuse"]
    lines += [
        "## Evidence Reuse and Correlation",
        "",
        f"- Cell references: **{reuse['cell_references']}**",
        f"- Unique evidence identities: **{reuse['unique_evidence_refs']}**",
        f"- Evidence identities reused across cells: "
        f"**{reuse['reused_evidence_refs']}**",
        f"- Correlated evidence groups: "
        f"**{len(reuse['correlated_groups'])}**",
        f"- Shared-source evidence groups: "
        f"**{len(reuse['shared_source_groups'])}**",
        "",
        reuse["policy"],
        "",
        "## Component and Dependency Evidence",
        "",
    ]
    if matrix["component_evidence"]:
        lines += [
            "| Component | Role | Transfer | Observed events | Parent use |",
            "|---|---|---|---:|---|",
        ]
        for component in matrix["component_evidence"]:
            lines.append(
                f"| `{component['subject_id']}` | "
                f"{component.get('role') or 'unspecified'} | "
                f"{component['evidence_transfer']} | "
                f"{component['observed_event_count']} | "
                f"{component['coverage_use']} |")
    else:
        lines.append("- No component dependencies are declared by this subject.")
    lines += ["", "## Highest-Priority Blind Spots", ""]
    lines.extend(
        f"- `{item['id']}` — {item['title']} "
        f"({item['status']}; {item['collection_condition']}; "
        f"confidence {item['evidence_confidence']}): "
        f"{item['next_evidence']}"
        for item in matrix["blind_spots"][:25])
    if not matrix["blind_spots"]:
        lines.append("- None in the declared profile.")
    lines += ["", matrix["claim_boundary"], ""]
    return "\n".join(lines)


def render_html(matrix: dict) -> str:
    """Render a sortable-ready complete integrity matrix without inference."""
    rows = []
    for category in matrix["categories"].values():
        for cell in category["cells"]:
            rows.append(
                "<tr><td>" + html.escape(category["title"])
                + "</td><td><code>" + html.escape(cell["id"])
                + "</code> — " + html.escape(cell["title"])
                + "</td><td>" + html.escape(cell["status"])
                + "</td><td>" + html.escape(cell["collection_condition"])
                + "</td><td>" + html.escape(
                    cell["evidence_confidence"]["level"])
                + "</td><td>" + str(cell["evidence_count"])
                + "</td><td>" + html.escape(cell["rationale"])
                + "</td></tr>")
    summary = matrix["summary"]
    integrity = matrix["integrity_summary"]
    cards = (
        ("Assessed", summary["assessed"]),
        ("Partial", summary["partially-assessed"]),
        ("Not assessed", summary["not-assessed"]),
        ("Unsupported", summary["unsupported"]),
        ("Not applicable", summary["not-applicable"]),
        ("Direct coverage", f"{summary['direct_coverage_percent'] or 0:.1f}%"),
        ("Stale", integrity["stale_cells"]),
        ("Conflicting", integrity["conflicting_cells"]),
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'><meta "
        "name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>AIES Assessment Coverage</title><style>"
        "body{font:15px system-ui;max-width:1300px;margin:40px auto;padding:0 20px;"
        "color:#172033}table{border-collapse:collapse;width:100%}"
        "th,td{padding:8px;border-bottom:1px solid #d8deea;text-align:left;"
        "vertical-align:top}th{position:sticky;top:0;background:#eef3fb}"
        ".summary{display:flex;gap:12px;flex-wrap:wrap}.card{padding:12px 16px;"
        "border:1px solid #d8deea;border-radius:10px}code{color:#3154a5}"
        "</style></head><body><h1>AIES Assessment Coverage &amp; Blind Spots</h1>"
        "<p><strong>Informational — coverage is not quality, qualification, "
        "or authorization.</strong></p><p><code>"
        + html.escape(matrix["profile"]["id"]) + "</code> — "
        + html.escape(matrix["profile"]["title"]) + "</p><div class='summary'>"
        + "".join(
            f"<div class='card'><strong>{html.escape(label)}</strong><br>"
            f"{value}</div>" for label, value in cards)
        + "</div><h2>Complete matrix</h2><table><thead><tr><th>Category</th>"
        "<th>Perspective</th><th>Coverage</th><th>Collection</th>"
        "<th>Evidence confidence</th><th>Evidence</th><th>Rationale</th>"
        "</tr></thead><tbody>" + "".join(rows)
        + "</tbody></table><h2>Claim boundary</h2><p>"
        + html.escape(matrix["claim_boundary"])
        + "</p></body></html>"
    )


def write_run_artifacts(run_id: str, matrix: dict | None = None) -> dict[str, str]:
    from . import remediation

    matrix = matrix or for_run(run_id)
    rdir = workspace.run_dir(run_id)
    plan = remediation.build(
        matrix, reassessment_command=f"aies resume {run_id}")
    paths = {
        "coverage_markdown": rdir / "assessment-coverage.md",
        "coverage_json": rdir / "assessment-coverage.json",
        "coverage_html": rdir / "assessment-coverage.html",
        "remediation_markdown": rdir / "evidence-remediation-plan.md",
        "remediation_json": rdir / "evidence-remediation-plan.json",
        "remediation_html": rdir / "evidence-remediation-plan.html",
    }
    workspace.write_view(paths["coverage_markdown"], render_markdown(matrix))
    workspace.write_view(
        paths["coverage_json"], json.dumps(matrix, indent=2) + "\n")
    workspace.write_view(paths["coverage_html"], render_html(matrix))
    workspace.write_view(
        paths["remediation_markdown"], remediation.render_markdown(plan))
    workspace.write_view(
        paths["remediation_json"], remediation.render_json(plan))
    workspace.write_view(
        paths["remediation_html"], remediation.render_html(plan))
    return {key: str(path) for key, path in paths.items()}


def write_repository_artifacts(
    result: dict,
    destination: str | Path,
    matrix: dict | None = None,
) -> dict[str, str]:
    from . import remediation

    matrix = matrix or for_repository(result)
    target = Path(destination).resolve()
    analysis = result.get("engineering_analysis") or {}
    repository_argument = str(result.get("repo") or ".").replace('"', "")
    plan = remediation.build(
        matrix, findings=analysis.get("findings") or [],
        reassessment_command=f'aies audit "{repository_argument}"')
    paths = {
        "coverage_markdown": target / "assessment-coverage.md",
        "coverage_json": target / "assessment-coverage.json",
        "coverage_html": target / "assessment-coverage.html",
        "remediation_markdown": target / "evidence-remediation-plan.md",
        "remediation_json": target / "evidence-remediation-plan.json",
        "remediation_html": target / "evidence-remediation-plan.html",
    }
    existing = [str(path) for path in paths.values() if path.exists()]
    if existing:
        raise FileExistsError(
            "coverage output is immutable; already exists: "
            + ", ".join(existing))
    paths["coverage_markdown"].write_text(
        render_markdown(matrix), encoding="utf-8")
    paths["coverage_json"].write_text(
        json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    paths["coverage_html"].write_text(
        render_html(matrix), encoding="utf-8")
    paths["remediation_markdown"].write_text(
        remediation.render_markdown(plan), encoding="utf-8")
    paths["remediation_json"].write_text(
        remediation.render_json(plan), encoding="utf-8")
    paths["remediation_html"].write_text(
        remediation.render_html(plan), encoding="utf-8")
    return {key: str(path) for key, path in paths.items()}

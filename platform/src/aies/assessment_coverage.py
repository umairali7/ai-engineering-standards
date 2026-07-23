"""Evidence-linked Assessment Coverage Matrix and blind-spot reporting."""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path

from . import assessment_profiles, subjects, workspace


SCHEMA = "aies-assessment-coverage/v1"
RUNTIME_STATES = (
    "assessed", "partially-assessed", "not-assessed",
    "not-applicable", "unsupported",
)


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
            cells.append({
                "id": item["id"],
                "title": item["title"],
                **({"value": item["value"]} if item.get("value") else {}),
                "applicability": applicability,
                "status": status,
                "rationale": item["rationale"],
                "evidence_refs": [],
                "evidence_count": 0,
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
        },
        "subject": subject,
        "evidence_scope": evidence_scope,
        "categories": categories,
        "summary": {},
        "blind_spots": [],
        "evidence_reuse": {},
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


def _events_by(events: list[dict], key) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for event in events:
        value = key(event)
        if value:
            grouped[value].append(event["event_id"])
    return grouped


def _finalize(matrix: dict) -> dict:
    evidence_usage: dict[str, list[str]] = defaultdict(list)
    overall = Counter()
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
            for reference in cell["evidence_refs"]:
                evidence_usage[reference].append(cell_path)
            if cell["status"] in (
                    "partially-assessed", "not-assessed", "unsupported"):
                blind_spots.append({
                    "category": category_id,
                    "category_title": category["title"],
                    "id": cell["id"],
                    "title": cell["title"],
                    "status": cell["status"],
                    "rationale": cell["rationale"],
                    "next_evidence": (
                        "Implement a direct evidence path in the Subject "
                        "Assessment Profile."
                        if cell["status"] == "unsupported" else
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
    }
    matrix["blind_spots"] = sorted(
        blind_spots,
        key=lambda item: (
            {"unsupported": 0, "not-assessed": 1,
             "partially-assessed": 2}.get(item["status"], 3),
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
        "policy": (
            "One canonical evidence identity may explain multiple cells but "
            "is counted once as unique evidence and cannot inflate assurance."),
    }
    return matrix


def for_run(run_id: str, *, capability_matrix: dict | None = None) -> dict:
    """Build coverage for a deployment run without changing its evidence."""
    from . import ecm, evidence_events

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
    by_area = _events_by(events, lambda event: event.get("payload", {}).get("area"))
    by_scenario = _events_by(events, lambda event: event.get("instrument_id"))
    by_modality = _events_by(events, lambda event: event.get("modality"))

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
    return _finalize(matrix)


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
        })
    events = result.get("events") or []
    by_area = _events_by(events, lambda event: event.get("payload", {}).get("area"))
    by_modality = _events_by(events, lambda event: event.get("modality"))
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
    products = ["DP-05", "DP-09", "DP-11"]
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
    return _finalize(matrix)


def for_reference(reference: str) -> dict:
    audit_path = workspace.root() / "audits" / f"{reference}.json"
    if audit_path.is_file():
        return for_repository(workspace.read_json(audit_path))
    return for_run(reference)


def render_markdown(matrix: dict) -> str:
    summary = matrix["summary"]
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
    ]
    for category in matrix["categories"].values():
        lines += [
            f"## {category['title']}",
            "",
            "| Perspective | Status | Evidence | Rationale |",
            "|---|---|---:|---|",
        ]
        for cell in category["cells"]:
            lines.append(
                f"| `{cell['id']}` — {cell['title']} | "
                f"{cell['status']} | {cell['evidence_count']} | "
                f"{cell['rationale']} |")
        lines.append("")
    reuse = matrix["evidence_reuse"]
    lines += [
        "## Evidence Reuse",
        "",
        f"- Cell references: **{reuse['cell_references']}**",
        f"- Unique evidence identities: **{reuse['unique_evidence_refs']}**",
        f"- Evidence identities reused across cells: "
        f"**{reuse['reused_evidence_refs']}**",
        "",
        reuse["policy"],
        "",
        "## Highest-Priority Blind Spots",
        "",
    ]
    lines.extend(
        f"- `{item['id']}` — {item['title']} ({item['status']}): "
        f"{item['next_evidence']}"
        for item in matrix["blind_spots"][:25])
    if not matrix["blind_spots"]:
        lines.append("- None in the declared profile.")
    lines += ["", matrix["claim_boundary"], ""]
    return "\n".join(lines)


def render_html(matrix: dict) -> str:
    markdown = render_markdown(matrix)
    rows = []
    for category in matrix["categories"].values():
        for cell in category["cells"]:
            rows.append(
                "<tr><td>" + html.escape(category["title"])
                + "</td><td><code>" + html.escape(cell["id"])
                + "</code> — " + html.escape(cell["title"])
                + "</td><td>" + html.escape(cell["status"])
                + "</td><td>" + str(cell["evidence_count"])
                + "</td><td>" + html.escape(cell["rationale"])
                + "</td></tr>")
    summary = matrix["summary"]
    return (
        "<!doctype html><html><head><meta charset='utf-8'><meta "
        "name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>AIES Assessment Coverage</title><style>"
        "body{font:15px system-ui;max-width:1200px;margin:40px auto;padding:0 20px;"
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
            f"<div class='card'><strong>{html.escape(label)}</strong><br>{value}</div>"
            for label, value in (
                ("Assessed", summary["assessed"]),
                ("Partial", summary["partially-assessed"]),
                ("Not assessed", summary["not-assessed"]),
                ("Unsupported", summary["unsupported"]),
                ("Not applicable", summary["not-applicable"]),
                ("Direct coverage",
                 f"{summary['direct_coverage_percent'] or 0:.1f}%"),
            ))
        + "</div><h2>Complete matrix</h2><table><thead><tr><th>Category</th>"
        "<th>Perspective</th><th>Status</th><th>Evidence</th><th>Rationale</th>"
        "</tr></thead><tbody>" + "".join(rows)
        + "</tbody></table><h2>Claim boundary</h2><p>"
        + html.escape(matrix["claim_boundary"])
        + "</p><details><summary>Markdown source preview</summary><pre>"
        + html.escape(markdown[:4000]) + "</pre></details></body></html>"
    )


def write_run_artifacts(run_id: str, matrix: dict | None = None) -> dict[str, str]:
    matrix = matrix or for_run(run_id)
    rdir = workspace.run_dir(run_id)
    paths = {
        "coverage_markdown": rdir / "assessment-coverage.md",
        "coverage_json": rdir / "assessment-coverage.json",
        "coverage_html": rdir / "assessment-coverage.html",
    }
    workspace.write_view(paths["coverage_markdown"], render_markdown(matrix))
    workspace.write_view(
        paths["coverage_json"], json.dumps(matrix, indent=2) + "\n")
    workspace.write_view(paths["coverage_html"], render_html(matrix))
    return {key: str(path) for key, path in paths.items()}


def write_repository_artifacts(
    result: dict,
    destination: str | Path,
    matrix: dict | None = None,
) -> dict[str, str]:
    matrix = matrix or for_repository(result)
    target = Path(destination).resolve()
    paths = {
        "coverage_markdown": target / "assessment-coverage.md",
        "coverage_json": target / "assessment-coverage.json",
        "coverage_html": target / "assessment-coverage.html",
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
    return {key: str(path) for key, path in paths.items()}

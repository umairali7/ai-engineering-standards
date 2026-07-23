"""Shared read-only workspace overview for CLI, API, dashboard, and future UI.

This module is a presentation view model, never a decision engine. It summarizes
stored registry entries, run manifests, assessment definitions, subject support,
and qualification records without recomputing any assessment outcome.
"""

from __future__ import annotations

from . import __version__, constants as C


KIND = "aies-workspace-overview"
SCHEMA_VERSION = 1


def build() -> dict:
    from . import assessments, compare, qualification, registry, support

    deployments = []
    for item in registry.list_entries(include_retired=True):
        deployments.append({
            "id": item["id"],
            "model": item.get("model") or item.get("family"),
            "runtime": item.get("runtime"),
            "roles": item.get("roles") or [],
            "status": "retired" if item.get("retired") else "active",
        })

    runs = []
    for item in compare.list_runs():
        runs.append({
            **item,
            "risk_tier_label": C.risk_tier_label(item.get("risk_tier")),
            "state": "aggregated" if item.get("aggregated") else item.get("status"),
            "href": f"/runs/{item['run_id']}",
        })

    records = []
    for item in qualification.list_records():
        scope = item.get("scope") or {}
        humans = item.get("humans") or {}
        subject = item.get("subject") or {}
        records.append({
            "record_id": item.get("record_id"),
            "deployment": subject.get("deployment"),
            "risk_tier": scope.get("risk_tier"),
            "risk_tier_label": C.risk_tier_label(scope.get("risk_tier")),
            "decision": item.get("decision"),
            "status": item.get("status"),
            "authority": humans.get("authority"),
            "recorded_at": item.get("recorded_at"),
        })

    assessment_rows = assessments.list_assessments()
    support_view = support.describe()
    return {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "platform_version": __version__,
        "authority": "informational-read-only",
        "counts": {
            "deployments": len(deployments),
            "active_deployments": sum(
                row["status"] == "active" for row in deployments),
            "runs": len(runs),
            "aggregated_runs": sum(bool(row["aggregated"]) for row in runs),
            "qualification_records": len(records),
            "assessments": len(assessment_rows),
            "implemented_subject_kinds": (
                support_view.get("counts", {}).get("implemented", 0)),
        },
        "deployments": deployments,
        "runs": runs,
        "qualifications": records,
        "assessments": assessment_rows,
        "support": {
            "counts": support_view.get("counts", {}),
            "registry_version": support_view.get("version"),
        },
        "links": {
            "health": "/health",
            "support": "/support",
            "deployments": "/deployments",
            "runs": "/runs",
            "run": "/runs/{id}",
            "assessments": "/assessments",
            "qualifications": "/qualifications",
        },
        "limitations": [
            "This overview summarizes stored artifacts and computes no outcome.",
            "Engineering Evaluation is informational; qualification records are "
            "separate human-governed decisions.",
            "Unassessed subject kinds and engineering tasks remain unknown.",
        ],
    }


def render(summary: dict) -> str:
    counts = summary["counts"]
    lines = [
        "AIES workspace overview",
        "  authority          : informational, read-only",
        f"  deployments        : {counts['active_deployments']} active / "
        f"{counts['deployments']} total",
        f"  runs               : {counts['aggregated_runs']} aggregated / "
        f"{counts['runs']} total",
        f"  qualification recs : {counts['qualification_records']} "
        "(human-governed)",
        f"  assessments        : {counts['assessments']}",
        f"  supported subjects : {counts['implemented_subject_kinds']} implemented",
    ]
    if summary["runs"]:
        latest = summary["runs"][0]
        lines.extend([
            "",
            "Latest run",
            f"  {latest['run_id']}",
            f"  {latest['model']} | {latest['risk_tier_label']} | {latest['state']}",
        ])
    lines.extend([
        "",
        "Next",
        "  aies support",
        "  aies runs list",
        "  aies dashboard --write",
        "  aies serve  # read-only JSON API",
    ])
    return "\n".join(lines)

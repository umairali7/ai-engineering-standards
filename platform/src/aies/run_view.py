"""Versioned read-only view of one assessment run.

The run view is a consumer contract for the CLI, REST API, and a future
frontend. It inventories stored state and presentation artifacts; it never
scores evidence, recomputes an assessment outcome, or records a decision.
"""

from __future__ import annotations

from pathlib import Path

from . import __version__, constants as C, run_mode, workspace


KIND = "aies-run-view"
SCHEMA_VERSION = 2


_ARTIFACTS = {
    "manifest": ("manifest.json", None),
    "progress": ("progress.json", None),
    "canonical_evidence": ("evidence-package.json", "evidence"),
    "engineering_report": ("report.json", "report"),
    "shared_report_view": ("report-view.json", "report-view"),
    "report_bundle": ("report-bundle.json", "bundle"),
    "engineering_evaluation": (
        "engineering-evaluation.json", "engineering-evaluation"),
    "engineering_assessment_result": (
        "engineering-assessment-result.json", "result"),
    "formal_assessment_result": ("assessment-result.json", "formal-result"),
    "engineering_capability_matrix": (
        "engineering-capability-matrix.json", "ecm"),
    "engineering_fit_guidance": (
        "engineering-fit-guidance.json", "guidance"),
    "deployment_guidance": ("deployment-guidance.json", "guidance"),
    "executive_summary": ("executive-summary.json", "executive-summary"),
    "grounding_diagnostics": (
        "grounding-diagnostics.json", "diagnostics"),
}


def _read_if_present(path: Path) -> dict | None:
    return workspace.read_json(path) if path.exists() else None


def _artifact_inventory(run_id: str, rdir: Path) -> dict[str, dict]:
    inventory = {}
    for key, (filename, endpoint) in _ARTIFACTS.items():
        path = rdir / filename
        inventory[key] = {
            "filename": filename,
            "available": path.exists(),
            "storage_class": workspace.artifact_class(path),
            "href": f"/runs/{run_id}/{endpoint}" if endpoint else None,
        }
    return inventory


def _task_counts(matrix: dict | None, formal: bool) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in (matrix or {}).get("tasks", []):
        status = (task.get("status") if formal
                  else task.get("engineering_status", task.get("status")))
        status = status or "unknown"
        counts[status] = counts.get(status, 0) + 1
    return counts


def _guidance_counts(guidance: dict | None) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not guidance:
        return counts
    field = "fit" if guidance.get("kind") == "engineering-fit-guidance" else "guidance"
    for task in guidance.get("tasks", []):
        label = task.get(field) or "unknown"
        counts[label] = counts.get(label, 0) + 1
    return counts


def _result_summary(result: dict | None) -> dict | None:
    if not result:
        return None
    assessment = result.get("assessment") or {}
    return {
        "kind": result.get("kind"),
        "status": result.get("outcome", result.get("status")),
        "assessment": {
            "id": assessment.get("id"),
            "version": assessment.get("version"),
        } if assessment else None,
    }


def build(run_id: str) -> dict:
    """Build a stable presentation view from stored artifacts only."""
    workspace.validate_run_id(run_id)
    rdir = workspace.run_dir(run_id)
    manifest_path = rdir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"run {run_id!r} not found")

    manifest = workspace.read_json(manifest_path)
    formal = run_mode.is_formal(manifest)
    progress = _read_if_present(rdir / "progress.json")
    evidence = _read_if_present(rdir / "evidence-package.json")
    evaluation = _read_if_present(rdir / "engineering-evaluation.json")
    engineering_result = _read_if_present(
        rdir / "engineering-assessment-result.json")
    formal_result = _read_if_present(rdir / "assessment-result.json")
    matrix = _read_if_present(rdir / "engineering-capability-matrix.json")
    fit_guidance = _read_if_present(rdir / "engineering-fit-guidance.json")
    deployment_guidance = _read_if_present(rdir / "deployment-guidance.json")
    guidance = fit_guidance or deployment_guidance
    executive = _read_if_present(rdir / "executive-summary.json")
    diagnostics = _read_if_present(rdir / "grounding-diagnostics.json")
    bundle = _read_if_present(rdir / "report-bundle.json")
    inventory = _artifact_inventory(run_id, rdir)

    from . import subjects
    subject = subjects.from_manifest(manifest)
    execution = subjects.execution_from_manifest(manifest)
    model = manifest.get("model") or {}
    response_count = len(list((rdir / "responses").glob("*.json")))
    rating_count = len(list((rdir / "ratings").glob("*.json")))
    planned = sum(
        int(area.get("planned_items", 0))
        for area in manifest.get("areas", []))
    if not planned:
        planned = int((manifest.get("sample_plan") or {}).get(
            "planned_items", 0))
    if bundle:
        state = "reported"
    elif evidence:
        state = "aggregated"
    elif progress:
        state = progress.get("status") or progress.get("stage") or "in-progress"
    else:
        state = manifest.get("status", "unknown")

    result = formal_result if formal else (engineering_result or formal_result)
    diagnostic_sources = (diagnostics or {}).get("sources") or {}
    return {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "platform_version": __version__,
        "authority": "informational-read-only",
        "run_id": run_id,
        "state": state,
        "run_purpose": run_mode.purpose(manifest),
        "subject": {
            "id": subject.get("id", model.get("registry_id")),
            "display_name": subject.get("display_name"),
            "kind": subject.get("kind", "ai_deployment"),
            "descriptor_schema": subject.get("schema"),
            "privacy": subject.get("privacy"),
            "executor_kind": execution.get("executor_id", "runtime-generation"),
            "executor_contract": execution.get("contract"),
            "deployment_evidence": model.get("registry_id"),
            "checksum": model.get("checksum"),
        },
        "manifest_compatibility": subjects.compatibility(manifest),
        "scope": {
            "profile": manifest.get("profile"),
            "profile_version": manifest.get("profile_version"),
            "risk_tier": manifest.get("risk_tier"),
            "risk_tier_label": C.risk_tier_label(manifest.get("risk_tier")),
            "subject_kind": manifest.get("subject_kind"),
            "subject_kind_label": C.identifier_label(
                manifest.get("subject_kind")),
            "competencies": [
                {
                    "code": area.get("area"),
                    "label": C.competency_label(area.get("area")),
                    "suite_version": area.get("suite_version"),
                    "planned_items": area.get("planned_items"),
                }
                for area in manifest.get("areas", [])
            ],
        },
        "execution": {
            "manifest_status": manifest.get("status"),
            "created_at": manifest.get("created_at"),
            "planned_responses": planned,
            "collected_responses": response_count,
            "recorded_ratings": rating_count,
            "progress": progress,
        },
        "products": {
            "engineering_evaluation": evaluation,
            "assessment_result": _result_summary(result),
            "engineering_capability_matrix": {
                "available": matrix is not None,
                "kind": (matrix or {}).get("kind"),
                "task_status_counts": _task_counts(matrix, formal),
            },
            "guidance": {
                "available": guidance is not None,
                "kind": (guidance or {}).get("kind"),
                "task_counts": _guidance_counts(guidance),
            },
            "grounding_diagnostics": {
                "available": diagnostics is not None,
                "status": (diagnostics or {}).get("status"),
                "automated": diagnostic_sources.get("automated"),
                "human": diagnostic_sources.get("human"),
            },
            "executive_summary": {
                "available": executive is not None,
                "status": (executive or {}).get("status"),
            },
        },
        "artifacts": inventory,
        "links": {
            "self": f"/runs/{run_id}",
            **{
                key: detail["href"]
                for key, detail in inventory.items()
                if detail["href"] and detail["available"]
            },
        },
        "limitations": [
            "This view inventories stored evidence and report products; it "
            "does not score, decide, qualify, grant, or authorize deployment.",
            "Missing or unavailable products remain unknown and are never "
            "interpreted as passing evidence.",
            "Use the canonical evidence and assessment-result endpoints for "
            "the complete stored artifacts.",
        ],
    }


def render(summary: dict) -> str:
    """Render a compact human-readable run inspection."""
    execution = summary["execution"]
    products = summary["products"]
    result = products.get("assessment_result") or {}
    result_status = result.get("status") or "not available"
    ecm = products["engineering_capability_matrix"]
    tasks = sum(ecm["task_status_counts"].values())
    lines = [
        f"AIES run — {summary['run_id']}",
        f"  state       : {summary['state']}",
        f"  purpose     : {summary['run_purpose']}",
        f"  subject     : {summary['subject']['id']} "
        f"({summary['subject']['kind']})",
        f"  scope       : {summary['scope']['risk_tier_label']} · "
        f"{summary['scope']['profile']} profile",
        f"  responses   : {execution['collected_responses']}/"
        f"{execution['planned_responses']}",
        f"  ratings     : {execution['recorded_ratings']}",
        f"  assessment  : {result_status}",
        f"  ECM         : {'available' if ecm['available'] else 'not available'} "
        f"({tasks} task rows)",
        f"  guidance    : "
        f"{products['guidance']['kind'] or 'not available'}",
        f"  grounding   : "
        f"{products['grounding_diagnostics']['status'] or 'not available'}",
        "",
        "Available JSON products",
    ]
    available = [
        (name, detail) for name, detail in summary["artifacts"].items()
        if detail["available"]
    ]
    lines.extend(
        f"  {name:32} {detail['filename']}"
        for name, detail in available)
    lines.extend([
        "",
        "Next",
        f"  aies open {summary['run_id']}",
        f"  aies capabilities {summary['run_id']} --ecm",
        f"  aies transcript {summary['run_id']}",
    ])
    return "\n".join(lines)

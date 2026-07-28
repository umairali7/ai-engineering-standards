"""Evidence-to-standard traceability views.

This artifact explains how a written standard reached an observed score.  It
does not change scores, qualification decisions, or deployment authority.
"""

from __future__ import annotations

import html
import json

from . import constants as C
from . import workspace


TRACEABILITY_SCHEMA = 1


def _task_recommendations(rdir) -> dict[str, dict]:
    """Load the already-rendered decision product without deriving a new one."""
    for filename, field in (
        ("engineering-fit-guidance.json", "fit"),
        ("deployment-guidance.json", "guidance"),
    ):
        path = rdir / filename
        if not path.exists():
            continue
        product = workspace.read_json(path)
        return {
            row["task_id"]: {
                "task_id": row["task_id"],
                "task": row.get("task"),
                "decision": row.get(field),
                "product": product.get("kind"),
                "authority": (
                    "informational engineering fit"
                    if field == "fit"
                    else "qualification-bounded deployment guidance"),
            }
            for row in product.get("tasks") or []
        }
    return {}


def build(run_id: str) -> dict:
    from . import assessment_instruments, rating

    rdir = workspace.run_dir(run_id)
    task_recommendations = _task_recommendations(rdir)
    responses = {
        path.name: workspace.read_json(path)
        for path in (rdir / "responses").glob("*.json")
    }
    rows = []
    status_counts = {"valid": 0, "conflicted": 0, "unavailable": 0}
    for observation in rating.collect_ratings(run_id):
        response = responses.get(observation["rates_response"])
        if not response:
            continue
        try:
            # Report rendering is read-only. Legacy migration is available only
            # in explicit review/scoring preparation, never as a side effect of
            # opening or regenerating a presentation artifact.
            instrument = assessment_instruments.load_snapshot(
                run_id, response["scenario_id"])
        except Exception:
            instrument = None
        trace = observation.get("review_trace") or {}
        trace_status = trace.get("protocol_status") or "unavailable"
        if trace_status not in status_counts:
            trace_status = "conflicted"
        status_counts[trace_status] += 1
        evidence_by_dimension = {
            item["dimension"]: item
            for item in trace.get("dimension_evidence") or []
            if isinstance(item, dict) and item.get("dimension") in C.DIMENSIONS
        }
        findings_by_dimension = {
            dimension: [
                finding
                for finding in observation.get("findings") or []
                if finding.get("dimension") == dimension
            ]
            for dimension in C.DIMENSIONS
        }
        for dimension in C.DIMENSIONS:
            detail = (
                (instrument or {}).get("evaluation", {})
                .get("dimensions", {}).get(dimension, {})
            )
            engineering_tasks = (
                (instrument or {}).get("engineering_tasks") or [])
            rows.append({
                "standard": {
                    "id": "AIES-AESQS-ER-01",
                    "title": "Evaluation Rubrics",
                    "requirement": (
                        "AIES-AESQS-ER-01-R01 — Score each dimension "
                        "independently against its anchor table"),
                },
                "area": (
                    (instrument or {}).get("area")
                    or {
                        "code": response.get("area"),
                        "label": C.competency_label(response.get("area")),
                    }
                ),
                "scenario_id": response["scenario_id"],
                "instrument_digest": (
                    observation.get("instrument_digest")
                    or (instrument or {}).get("instrument_digest")),
                "engineering_tasks": engineering_tasks,
                "recommendations": [
                    task_recommendations[task["code"]]
                    for task in engineering_tasks
                    if task["code"] in task_recommendations
                ],
                "response_record": observation["rates_response"],
                "rater": observation.get("provenance") or {},
                "dimension": {
                    "code": dimension,
                    "label": C.identifier_label(dimension),
                    "scenario_criteria": detail.get("scenario_criteria") or [],
                    "applicability": detail.get("applicability"),
                },
                "score": (observation.get("scores") or {}).get(dimension),
                "criterion_evidence": evidence_by_dimension.get(dimension),
                "findings": findings_by_dimension[dimension],
                "failure_conditions_observed": (
                    observation.get("failure_conditions_observed") or []),
                "trace_status": trace_status,
                "trace_issues": trace.get("protocol_issues") or [],
            })
    return {
        "kind": "aies-standards-traceability",
        "schema_version": TRACEABILITY_SCHEMA,
        "run_id": run_id,
        "status": "informational",
        "chain": [
            "standard requirement",
            "competency",
            "scenario instrument",
            "candidate response",
            "rating evidence",
            "EV result",
            "Engineering Task",
            "recommendation",
        ],
        "trace_status_counts": status_counts,
        "rows": rows,
        "boundary": (
            "Traceability explains recorded observations. It does not validate "
            "the reviewer, alter a score, grant qualification, or authorize use."
        ),
    }


def render_markdown(result: dict) -> str:
    counts = result["trace_status_counts"]
    lines = [
        "# AIES Standards Traceability",
        "",
        "> **INFORMATIONAL — explains evidence lineage; does not change scores or authority.**",
        "",
        f"Run: `{result['run_id']}`  ",
        f"Criterion traces: valid {counts['valid']} · conflicted "
        f"{counts['conflicted']} · unavailable {counts['unavailable']}",
        "",
        "| Standard requirement | Competency | Instrument | Engineering task(s) | Decision product | Dimension | Score | Criterion evidence | Trace |",
        "|---|---|---|---|---|---|---:|---|---|",
    ]
    for row in result["rows"]:
        trace = row.get("criterion_evidence") or {}
        evidence = "; ".join(trace.get("evidence") or []) or "not supplied"
        tasks = ", ".join(
            task["label"] for task in row["engineering_tasks"]) or "not mapped"
        recommendations = ", ".join(
            f"{item['task_id']}: {item['decision']}"
            for item in row["recommendations"]) or "unavailable"
        lines.append(
            f"| {row['standard']['requirement']} | {row['area']['label']} | "
            f"`{row['scenario_id']}` | {tasks} | "
            f"{recommendations} | {row['dimension']['label']} | {row['score']} | "
            f"{evidence} | {row['trace_status']} |"
        )
    lines.extend(["", result["boundary"], ""])
    return "\n".join(lines)


def render_html(result: dict) -> str:
    rows = []
    for row in result["rows"]:
        trace = row.get("criterion_evidence") or {}
        evidence = "; ".join(trace.get("evidence") or []) or "not supplied"
        tasks = ", ".join(
            task["label"] for task in row["engineering_tasks"]) or "not mapped"
        recommendations = ", ".join(
            f"{item['task_id']}: {item['decision']}"
            for item in row["recommendations"]) or "unavailable"
        rows.append(
            "<tr><td>" + html.escape(row["standard"]["requirement"]) +
            "</td><td>" + html.escape(row["area"]["label"]) +
            "</td><td><code>" + html.escape(row["scenario_id"]) +
            "</code></td><td>" + html.escape(tasks) +
            "</td><td>" + html.escape(recommendations) +
            "</td><td>" + html.escape(row["dimension"]["label"]) +
            "</td><td>" + html.escape(str(row["score"])) +
            "</td><td>" + html.escape(evidence) +
            "</td><td>" + html.escape(row["trace_status"]) + "</td></tr>"
        )
    return """<!doctype html><html><head><meta charset='utf-8'>
<title>AIES Standards Traceability</title>
<style>body{font:15px system-ui;max-width:1500px;margin:32px auto;padding:0 24px;color:#18202a}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #d0d7de;padding:7px;vertical-align:top}
th{background:#f6f8fa;text-align:left}.banner{padding:12px;background:#fff8c5;border-left:5px solid #bf8700}</style>
</head><body><h1>AIES Standards Traceability</h1>
<p class='banner'><strong>INFORMATIONAL — explains evidence lineage; does not change scores or authority.</strong></p>
<p>Run: <code>""" + html.escape(result["run_id"]) + """</code></p>
<table><thead><tr><th>Standard requirement</th><th>Competency</th><th>Instrument</th>
<th>Engineering task(s)</th><th>Decision product</th><th>Dimension</th><th>Score</th><th>Criterion evidence</th>
<th>Trace</th></tr></thead><tbody>""" + "".join(rows) + """</tbody></table>
<p>""" + html.escape(result["boundary"]) + "</p></body></html>"


def write_artifacts(run_id: str) -> dict[str, str]:
    result = build(run_id)
    rdir = workspace.run_dir(run_id)
    paths = {
        "standards_traceability_markdown": rdir / "standards-traceability.md",
        "standards_traceability_json": rdir / "standards-traceability.json",
        "standards_traceability_html": rdir / "standards-traceability.html",
    }
    workspace.write_view(
        paths["standards_traceability_markdown"], render_markdown(result))
    workspace.write_view(
        paths["standards_traceability_json"], json.dumps(result, indent=2) + "\n")
    workspace.write_view(
        paths["standards_traceability_html"], render_html(result))
    return {key: str(path) for key, path in paths.items()}

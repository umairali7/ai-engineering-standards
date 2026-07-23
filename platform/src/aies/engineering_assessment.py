"""Non-blocking assessment result for automated engineering evaluations.

This artifact answers whether the selected assessment composition was executed
and scored. It never makes a qualification decision and never requires a human
rating. Formal qualification is deliberately handled by ``aies.decision``.
"""

from __future__ import annotations

import html
import json

from . import constants as C, evaluation, workspace

RESULT_SCHEMA = 1
STATUSES = ("COMPLETE", "PARTIAL", "NOT SCORED")


class EngineeringAssessmentError(ValueError):
    pass


def build(run_id: str) -> dict:
    rdir = workspace.run_dir(run_id)
    manifest = workspace.read_json(rdir / "manifest.json")
    assessment = manifest.get("assessment")
    if not assessment:
        raise EngineeringAssessmentError(
            f"run {run_id!r} was not composed under a named assessment")

    summary = evaluation.summarize(run_id)
    area_views = summary.get("areas") or {}
    rows = []
    mandatory_statuses = []
    for component in assessment.get("competencies") or []:
        area = component["area"]
        requirement = component.get("requirement", "mandatory")
        view = area_views.get(area) or {
            "status": "not-scored", "completed_by": None,
            "sources": {"automated": {}, "human": {}},
        }
        automated = (view.get("sources") or {}).get("automated") or {}
        human = (view.get("sources") or {}).get("human") or {}
        row = {
            "area": area,
            "area_label": C.competency_label(area),
            "requirement": requirement,
            "status": view.get("status", "not-scored"),
            "completed_by": view.get("completed_by"),
            "automated": automated,
            "human": human,
        }
        rows.append(row)
        if requirement == "mandatory":
            mandatory_statuses.append(row["status"])

    if mandatory_statuses and all(status == "complete" for status in mandatory_statuses):
        status = "COMPLETE"
    elif any(status in ("complete", "partial") for status in mandatory_statuses):
        status = "PARTIAL"
    else:
        status = "NOT SCORED"

    return {
        "kind": "engineering-assessment-result",
        "engineering_assessment_schema": RESULT_SCHEMA,
        "run_id": run_id,
        "subject": (manifest.get("subject") or {}).get(
            "id", (manifest.get("model") or {}).get("registry_id")),
        "risk_tier": manifest["risk_tier"],
        "profile": manifest["profile"],
        "assessment": {
            "id": assessment["id"],
            "title": assessment.get("title", assessment["id"]),
            "version": assessment["version"],
        },
        "status": status,
        "areas": rows,
        "human_evaluation": summary["human_evaluation"],
        "formal_qualification": {
            "status": "not-requested",
            "note": (
                "This result records engineering evaluation coverage and observed "
                "scores. It is not a qualification decision or grant."),
        },
    }


def render_markdown(result: dict) -> str:
    human = result["human_evaluation"]
    human_label = (
        f"Reviewed — {human.get('evaluator') or 'named human'}"
        if human.get("status") == "reviewed" else "Not reviewed (optional)")
    lines = [
        f"# Engineering Assessment Result — {result['assessment']['id']} "
        f"v{result['assessment']['version']}",
        "",
        f"## {result['status']}",
        "",
        f"**Subject:** `{result['subject']}` · "
        f"**Risk tier:** {C.risk_tier_label(result['risk_tier'])} · "
        f"**Profile:** {result['profile']}  ",
        f"**Human evaluation:** {human_label}",
        "",
        "Automated scores are sufficient for this engineering assessment. "
        "Human evaluation is optional and is shown separately when supplied.",
        "",
        "| Competency | Requirement | Automated coverage | Observed automated mean | Human eval | Status |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in result["areas"]:
        automated = row["automated"]
        mean = automated.get("observed_mean")
        lines.append(
            f"| {row['area_label']} | {row['requirement']} | "
            f"{automated.get('responses_scored', 0)}/"
            f"{automated.get('responses_total', 0)} "
            f"({automated.get('coverage_percent', 0):.1f}%) | "
            f"{mean if mean is not None else '—'} | {human_label} | "
            f"**{row['status'].upper()}** |")
    lines.extend([
        "",
        "## Qualification boundary",
        "",
        "Formal qualification was **not requested**. Use "
        "`aies assessment result <run> --formal-qualification` only when a "
        "human-governed qualification decision is intentionally required.",
        "",
    ])
    return "\n".join(lines)


def render_html(result: dict) -> str:
    human = result["human_evaluation"]
    human_label = (
        f"Reviewed — {human.get('evaluator') or 'named human'}"
        if human.get("status") == "reviewed" else "Not reviewed (optional)")
    rows = "".join(
        "<tr><td>" + html.escape(row["area_label"]) + "</td><td>" +
        html.escape(row["requirement"]) + "</td><td>" +
        f"{row['automated'].get('responses_scored', 0)}/"
        f"{row['automated'].get('responses_total', 0)} "
        f"({row['automated'].get('coverage_percent', 0):.1f}%)</td><td>" +
        html.escape(str(
            row["automated"].get("observed_mean")
            if row["automated"].get("observed_mean") is not None else "—")) +
        "</td><td>" + html.escape(human_label) + "</td><td><strong>" +
        html.escape(row["status"].upper()) + "</strong></td></tr>"
        for row in result["areas"])
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>AIES Engineering Assessment Result</title>
<style>body{{font:16px system-ui;max-width:1050px;margin:40px auto;padding:0 24px;color:#18202a}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccd4dd;padding:8px;text-align:left}}.complete{{padding:12px;background:#e8f5e9;border-left:5px solid #1a7f37}}</style></head><body>
<h1>Engineering Assessment Result — {html.escape(result['assessment']['id'])} v{html.escape(str(result['assessment']['version']))}</h1>
<p class="complete"><strong>{html.escape(result['status'])}</strong></p>
<p><strong>Subject:</strong> <code>{html.escape(str(result['subject']))}</code><br>
<strong>Risk tier:</strong> {html.escape(C.risk_tier_label(result['risk_tier']))}<br>
<strong>Human evaluation:</strong> {html.escape(human_label)}</p>
<p>Automated scores are sufficient for this engineering assessment. Human evaluation is optional.</p>
<table><tr><th>Competency</th><th>Requirement</th><th>Automated coverage</th><th>Observed automated mean</th><th>Human eval</th><th>Status</th></tr>{rows}</table>
<h2>Qualification boundary</h2><p>Formal qualification was <strong>not requested</strong>. This artifact is not a qualification decision or grant.</p>
</body></html>"""


def write_artifacts(run_id: str) -> tuple[dict, dict[str, str]]:
    result = build(run_id)
    rdir = workspace.run_dir(run_id)
    paths = {
        "engineering_assessment_markdown": str(rdir / "engineering-assessment-result.md"),
        "engineering_assessment_json": str(rdir / "engineering-assessment-result.json"),
        "engineering_assessment_html": str(rdir / "engineering-assessment-result.html"),
    }
    workspace.write_view(
        rdir / "engineering-assessment-result.md", render_markdown(result))
    workspace.write_view(
        rdir / "engineering-assessment-result.json",
        json.dumps(result, indent=2) + "\n")
    workspace.write_view(
        rdir / "engineering-assessment-result.html", render_html(result))
    return result, paths

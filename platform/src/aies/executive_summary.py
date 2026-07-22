"""Leadership-facing summary over existing AIES decision products.

The summary is a presentation artifact. It does not score evidence, decide an
assessment, qualify a subject, or create deployment authority.
"""
from __future__ import annotations

import html
import json

from . import constants as C, evaluation, workspace


def build(run_id: str, matrix: dict, deployment_guidance: dict,
          assessment_result: dict | None = None) -> dict:
    pkg = workspace.read_json(workspace.run_dir(run_id) / "evidence-package.json")
    task_counts: dict[str, int] = {}
    for task in matrix["tasks"]:
        task_counts[task["status"]] = task_counts.get(task["status"], 0) + 1
    guidance_counts: dict[str, int] = {}
    for task in deployment_guidance["tasks"]:
        key = task["guidance"]
        guidance_counts[key] = guidance_counts.get(key, 0) + 1
    ready = all(
        area.get("decisional") and area.get("gates_passed")
        and (area.get("rater_protocol") or {}).get("satisfied", True)
        for area in pkg["areas"].values())
    return {
        "kind": "executive-summary",
        "executive_summary_schema": 1,
        "status": "informational",
        "run_id": run_id,
        "subject": matrix["subject"],
        "scope": {
            "risk_tier": matrix["risk_tier"],
            "profile": matrix["profile"],
        },
        "assessment": ({
            "id": assessment_result["assessment"]["id"],
            "version": assessment_result["assessment"]["version"],
            "outcome": assessment_result["outcome"],
        } if assessment_result else None),
        "engineering_evaluation": evaluation.summarize(run_id),
        "formal_qualification_readiness": "ready-for-human-review" if ready else "blocked",
        "task_status_counts": task_counts,
        "deployment_guidance_counts": guidance_counts,
        "qualification_record": deployment_guidance.get("qualification_record"),
        "artifacts": {
            "qualification_evidence": {
                "markdown": "report.md", "json": "report.json", "html": "report.html"},
            "assessment_result": ({
                "markdown": "assessment-result.md", "json": "assessment-result.json",
                "html": "assessment-result.html"} if assessment_result else None),
            "engineering_capability_matrix": {
                "markdown": "engineering-capability-matrix.md",
                "json": "engineering-capability-matrix.json",
                "html": "engineering-capability-matrix.html"},
            "deployment_guidance": {
                "markdown": "deployment-guidance.md", "json": "deployment-guidance.json",
                "html": "deployment-guidance.html"},
        },
        "limitations": [
            "This summary is informational and does not replace the underlying artifacts.",
            "No task recommendation creates authority; Deployment Guidance is bounded by a current human Qualification Record.",
            "An absent Qualification Record means the bundled Deployment Guidance can emit no Use recommendation.",
        ],
    }


def render_markdown(summary: dict) -> str:
    assessment = summary.get("assessment")
    evaluation_status = summary["engineering_evaluation"].get("status", "not-scored")
    human = (summary["engineering_evaluation"].get("human_evaluation") or {})
    lines = [
        "# AIES Executive Summary", "",
        "> **INFORMATIONAL — NOT QUALIFICATION EVIDENCE, A GRANT, OR DEPLOYMENT AUTHORIZATION.**", "",
        f"**Subject:** `{summary['subject']}`  ",
        f"**Scope:** {C.risk_tier_label(summary['scope']['risk_tier'])} · "
        f"{summary['scope']['profile']} profile  ",
        f"**Engineering evaluation:** {evaluation_status.upper()} · Human evaluation: "
        f"{'reviewed' if human.get('status') == 'reviewed' else 'not reviewed (optional)'}  ",
        f"**Formal qualification readiness:** {summary['formal_qualification_readiness'].upper()}", "",
    ]
    if assessment:
        lines.extend([
            "## Assessment outcome", "",
            f"**{assessment['id']} v{assessment['version']}: {assessment['outcome']}**", "",
        ])
    else:
        lines.extend(["## Assessment outcome", "", "No declarative assessment result is available for this run.", ""])
    lines.extend(["## Engineering task evidence", "",
                  "| Status | Tasks |", "|---|---:|"])
    for status in ("demonstrated", "observed", "insufficient", "gate-failed",
                   "performance-below-threshold", "not assessed"):
        lines.append(f"| {status} | {summary['task_status_counts'].get(status, 0)} |")
    lines.extend(["", "## Deployment guidance", "",
                  "| Guidance | Tasks |", "|---|---:|"])
    for guidance in ("use", "use-with-review", "no-recommendation", "avoid-for-scoped-use"):
        lines.append(f"| {guidance} | {summary['deployment_guidance_counts'].get(guidance, 0)} |")
    lines.extend([
        "", f"Qualification Record: `{summary['qualification_record'] or 'not supplied'}`", "",
        "## Decision products", "",
        "- [Qualification Evidence Package](report.html) — governance and auditors.",
        "- [Canonical Assessment Result](assessment-result.html) — authoritative assessment outcome."
        if assessment else "- Canonical Assessment Result — not available for this run.",
        "- [Engineering Capability Matrix](engineering-capability-matrix.html) — engineers.",
        "- [Deployment Guidance](deployment-guidance.html) — operations and managers.",
        "", "## Limitations", "",
    ])
    lines.extend(f"- {item}" for item in summary["limitations"])
    return "\n".join(lines) + "\n"


def render_html(summary: dict) -> str:
    markdown_links = [
        ("Qualification Evidence Package", "report.html"),
        ("Engineering Capability Matrix", "engineering-capability-matrix.html"),
        ("Deployment Guidance", "deployment-guidance.html"),
    ]
    if summary.get("assessment"):
        markdown_links.insert(1, ("Canonical Assessment Result", "assessment-result.html"))
    links = "".join(
        f"<li><a href='{html.escape(path)}'>{html.escape(label)}</a></li>"
        for label, path in markdown_links)
    task_rows = "".join(
        f"<tr><td>{html.escape(status)}</td><td>{count}</td></tr>"
        for status, count in summary["task_status_counts"].items())
    guidance_rows = "".join(
        f"<tr><td>{html.escape(status)}</td><td>{count}</td></tr>"
        for status, count in summary["deployment_guidance_counts"].items())
    assessment = summary.get("assessment")
    assessment_text = (f"{assessment['id']} v{assessment['version']}: {assessment['outcome']}"
                       if assessment else "No declarative assessment result is available.")
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>AIES Executive Summary</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 24px;color:#18202a}}table{{border-collapse:collapse;margin:16px 0}}th,td{{border:1px solid #ccd4dd;padding:8px 12px;text-align:left}}.banner{{padding:12px;background:#fff3cd;border-left:5px solid #d99b00}}</style></head><body>
<h1>AIES Executive Summary</h1><p class='banner'><strong>INFORMATIONAL — NOT QUALIFICATION EVIDENCE, A GRANT, OR DEPLOYMENT AUTHORIZATION.</strong></p>
<p><strong>Subject:</strong> <code>{html.escape(summary['subject'])}</code><br>
<strong>Scope:</strong> {html.escape(C.risk_tier_label(summary['scope']['risk_tier']))} · {html.escape(summary['scope']['profile'])} profile<br>
<strong>Formal qualification readiness:</strong> {html.escape(summary['formal_qualification_readiness'].upper())}</p>
<h2>Assessment outcome</h2><p><strong>{html.escape(assessment_text)}</strong></p>
<h2>Engineering task evidence</h2><table><tr><th>Status</th><th>Tasks</th></tr>{task_rows}</table>
<h2>Deployment guidance</h2><table><tr><th>Guidance</th><th>Tasks</th></tr>{guidance_rows}</table>
<p>Qualification Record: <code>{html.escape(summary['qualification_record'] or 'not supplied')}</code></p>
<h2>Decision products</h2><ul>{links}</ul>
<h2>Limitations</h2><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in summary['limitations'])}</ul>
</body></html>"""


def render_json(summary: dict) -> str:
    return json.dumps(summary, indent=2) + "\n"

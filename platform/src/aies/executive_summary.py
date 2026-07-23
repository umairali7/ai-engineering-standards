"""Leadership-facing summary over existing AIES decision products."""

from __future__ import annotations

import html
import json

from . import constants as C, diagnostics, evaluation, run_mode, workspace


def build(run_id: str, matrix: dict, decision_guidance: dict,
          assessment_result: dict | None = None) -> dict:
    rdir = workspace.run_dir(run_id)
    pkg = workspace.read_json(rdir / "evidence-package.json")
    manifest = workspace.read_json(rdir / "manifest.json")
    formal = run_mode.is_formal(manifest)
    task_counts: dict[str, int] = {}
    for task in matrix["tasks"]:
        status = (task["status"] if formal else
                  task.get("engineering_status", "not assessed"))
        task_counts[status] = task_counts.get(status, 0) + 1
    guidance_field = (
        "fit" if decision_guidance.get("kind") == "engineering-fit-guidance"
        else "guidance")
    guidance_counts: dict[str, int] = {}
    for task in decision_guidance["tasks"]:
        key = task[guidance_field]
        guidance_counts[key] = guidance_counts.get(key, 0) + 1
    ready = all(
        area.get("decisional") and area.get("gates_passed")
        and (area.get("rater_protocol") or {}).get("satisfied", True)
        for area in pkg["areas"].values())

    assessment = None
    if assessment_result:
        assessment = {
            "kind": assessment_result["kind"],
            "id": assessment_result["assessment"]["id"],
            "version": assessment_result["assessment"]["version"],
            "status": assessment_result.get(
                "outcome", assessment_result.get("status")),
        }
    formal_status = (
        ("ready-for-human-review" if ready else "not-ready")
        if formal else "not-requested")
    fit_mode = decision_guidance.get("kind") == "engineering-fit-guidance"
    return {
        "kind": "executive-summary",
        "executive_summary_schema": 2,
        "status": "informational",
        "run_id": run_id,
        "run_purpose": run_mode.purpose(manifest),
        "subject": matrix["subject"],
        "scope": {
            "risk_tier": matrix["risk_tier"],
            "profile": matrix["profile"],
        },
        "assessment": assessment,
        "engineering_evaluation": evaluation.summarize(run_id),
        "grounding_diagnostics": diagnostics.summarize(run_id),
        "formal_qualification": {
            "status": formal_status,
            "requested": formal,
        },
        # Compatibility field; evaluation runs now say not-requested, never blocked.
        "formal_qualification_readiness": formal_status,
        "task_status_counts": task_counts,
        "guidance_kind": decision_guidance["kind"],
        "guidance_counts": guidance_counts,
        "deployment_guidance_counts": (
            guidance_counts if not fit_mode else {}),
        "qualification_record": decision_guidance.get("qualification_record"),
        "artifacts": {
            "engineering_report": {
                "markdown": "report.md", "json": "report.json", "html": "report.html"},
            "assessment_result": ({
                "markdown": ("assessment-result.md" if formal
                             else "engineering-assessment-result.md"),
                "json": ("assessment-result.json" if formal
                         else "engineering-assessment-result.json"),
                "html": ("assessment-result.html" if formal
                         else "engineering-assessment-result.html"),
            } if assessment_result else None),
            "engineering_capability_matrix": {
                "markdown": "engineering-capability-matrix.md",
                "json": "engineering-capability-matrix.json",
                "html": "engineering-capability-matrix.html"},
            "guidance": {
                "markdown": ("engineering-fit-guidance.md" if fit_mode
                             else "deployment-guidance.md"),
                "json": ("engineering-fit-guidance.json" if fit_mode
                         else "deployment-guidance.json"),
                "html": ("engineering-fit-guidance.html" if fit_mode
                         else "deployment-guidance.html"),
            },
            "grounding_diagnostics": {
                "markdown": "grounding-diagnostics.md",
                "json": "grounding-diagnostics.json",
                "html": "grounding-diagnostics.html"},
        },
        "limitations": [
            "This summary is informational and does not replace the underlying artifacts.",
            ("Engineering Fit Guidance interprets observed automated evidence and "
             "does not create deployment authority." if fit_mode else
             "Deployment Guidance is bounded by a current human Qualification Record."),
            "Human evaluation is optional for engineering evaluation; formal qualification and grants remain separately governed.",
        ],
    }


def _human_label(summary: dict) -> str:
    human = summary["engineering_evaluation"].get("human_evaluation") or {}
    return ("reviewed" if human.get("status") == "reviewed"
            else "not reviewed (optional)")


def render_markdown(summary: dict) -> str:
    assessment = summary.get("assessment")
    evaluation_status = summary["engineering_evaluation"].get(
        "status", "not-scored")
    automated_grounding = summary["grounding_diagnostics"]["sources"]["automated"]
    grounding_reliability = automated_grounding[
        "observed_grounding_reliability_percent"]
    automated_review = summary["engineering_evaluation"].get(
        "automated_review") or {}
    finding_integrity = summary["engineering_evaluation"].get(
        "finding_integrity") or {}
    formal = summary["formal_qualification"]
    fit_mode = summary["guidance_kind"] == "engineering-fit-guidance"
    lines = [
        "# AIES Executive Summary", "",
        "> **INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.**", "",
        f"**Subject:** `{summary['subject']}`  ",
        f"**Scope:** {C.risk_tier_label(summary['scope']['risk_tier'])} · "
        f"{summary['scope']['profile']} profile  ",
        f"**Engineering evaluation:** {evaluation_status.upper()} · "
        f"Human evaluation: {_human_label(summary)}  ",
        f"**Automated grounding diagnostic:** "
        f"{'unavailable' if grounding_reliability is None else f'{grounding_reliability:.1f}% observed reliability'}  ",
        f"**Automated judge assurance:** "
        f"{automated_review.get('calibration_status', 'not disclosed')}  ",
        f"**Written-finding metadata:** "
        f"{finding_integrity.get('status', 'not disclosed')}  ",
        f"**Formal qualification:** {formal['status'].upper()}", "",
    ]
    if assessment:
        title = ("Engineering assessment" if
                 assessment["kind"] == "engineering-assessment-result"
                 else "Formal qualification assessment")
        lines.extend([
            f"## {title}", "",
            f"**{assessment['id']} v{assessment['version']}: "
            f"{assessment['status']}**", "",
        ])
    else:
        lines.extend([
            "## Engineering assessment", "",
            "No declarative assessment composition was used for this run.", "",
        ])
    lines.extend([
        "## Engineering task evidence", "",
        "| Status | Tasks |", "|---|---:|",
    ])
    for status, count in summary["task_status_counts"].items():
        lines.append(
            f"| {status} | {count} |")
    lines.extend([
        "", "## " + ("Engineering fit" if fit_mode else "Deployment guidance"),
        "", "| Guidance | Tasks |", "|---|---:|",
    ])
    for label, count in summary["guidance_counts"].items():
        lines.append(f"| {label} | {count} |")
    lines.extend(["", "## Decision products", ""])
    lines.append("- [Engineering Evaluation Report](report.html) — complete scored evaluation.")
    if assessment:
        artifact = summary["artifacts"]["assessment_result"]["html"]
        label = ("Engineering Assessment Result" if
                 assessment["kind"] == "engineering-assessment-result"
                 else "Canonical Formal Assessment Result")
        lines.append(f"- [{label}]({artifact}) — assessment composition result.")
    lines.extend([
        "- [Engineering Capability Matrix](engineering-capability-matrix.html) — task strengths and gaps.",
        "- [Grounding Diagnostics](grounding-diagnostics.html) — hallucination and fabrication observations.",
        "- [Assessment Coverage & Blind Spots](assessment-coverage.html) — evidence availability, reuse, and missing perspectives; not a score.",
        ("- [Engineering Fit Guidance](engineering-fit-guidance.html) — "
         "evidence-derived fit; no deployment authority." if fit_mode else
         "- [Deployment Guidance](deployment-guidance.html) — "
         "qualification-bounded operational guidance."),
        "", "## Limitations", "",
    ])
    lines.extend(f"- {item}" for item in summary["limitations"])
    return "\n".join(lines) + "\n"


def render_html(summary: dict) -> str:
    evaluation_status = summary["engineering_evaluation"].get(
        "status", "not-scored")
    automated = summary["grounding_diagnostics"]["sources"]["automated"]
    reliability = automated["observed_grounding_reliability_percent"]
    grounding = ("unavailable" if reliability is None
                 else f"{reliability:.1f}% observed reliability")
    automated_review = summary["engineering_evaluation"].get(
        "automated_review") or {}
    finding_integrity = summary["engineering_evaluation"].get(
        "finding_integrity") or {}
    assessment = summary.get("assessment")
    assessment_text = (
        f"{assessment['id']} v{assessment['version']}: {assessment['status']}"
        if assessment else "No declarative assessment composition was used.")
    fit_mode = summary["guidance_kind"] == "engineering-fit-guidance"
    task_rows = "".join(
        f"<tr><td>{html.escape(status)}</td><td>{count}</td></tr>"
        for status, count in summary["task_status_counts"].items())
    guidance_rows = "".join(
        f"<tr><td>{html.escape(status)}</td><td>{count}</td></tr>"
        for status, count in summary["guidance_counts"].items())
    links = [
        ("Engineering Evaluation Report", "report.html"),
        ("Engineering Capability Matrix", "engineering-capability-matrix.html"),
        ("Grounding Diagnostics", "grounding-diagnostics.html"),
        ("Assessment Coverage & Blind Spots", "assessment-coverage.html"),
        (("Engineering Fit Guidance", "engineering-fit-guidance.html")
         if fit_mode else ("Deployment Guidance", "deployment-guidance.html")),
    ]
    if assessment:
        links.insert(1, (
            "Engineering Assessment Result" if
            assessment["kind"] == "engineering-assessment-result"
            else "Canonical Formal Assessment Result",
            summary["artifacts"]["assessment_result"]["html"]))
    link_html = "".join(
        f"<li><a href='{html.escape(path)}'>{html.escape(label)}</a></li>"
        for label, path in links)
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>AIES Executive Summary</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 24px;color:#18202a}}table{{border-collapse:collapse;margin:16px 0}}th,td{{border:1px solid #ccd4dd;padding:8px 12px;text-align:left}}.banner{{padding:12px;background:#e8f5e9;border-left:5px solid #1a7f37}}</style></head><body>
<h1>AIES Executive Summary</h1><p class='banner'><strong>ENGINEERING EVALUATION {html.escape(evaluation_status.upper())}</strong></p>
<p><strong>Subject:</strong> <code>{html.escape(summary['subject'])}</code><br>
<strong>Scope:</strong> {html.escape(C.risk_tier_label(summary['scope']['risk_tier']))} · {html.escape(summary['scope']['profile'])} profile<br>
<strong>Human evaluation:</strong> {html.escape(_human_label(summary))}<br>
<strong>Automated grounding diagnostic:</strong> {html.escape(grounding)}<br>
<strong>Automated judge assurance:</strong> {html.escape(automated_review.get('calibration_status', 'not disclosed'))}<br>
<strong>Written-finding metadata:</strong> {html.escape(finding_integrity.get('status', 'not disclosed'))}<br>
<strong>Formal qualification:</strong> {html.escape(summary['formal_qualification']['status'].upper())}</p>
<h2>Assessment</h2><p><strong>{html.escape(assessment_text)}</strong></p>
<h2>Engineering task evidence</h2><table><tr><th>Status</th><th>Tasks</th></tr>{task_rows}</table>
<h2>{'Engineering fit' if fit_mode else 'Deployment guidance'}</h2><table><tr><th>Guidance</th><th>Tasks</th></tr>{guidance_rows}</table>
<h2>Decision products</h2><ul>{link_html}</ul>
<h2>Limitations</h2><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in summary['limitations'])}</ul>
</body></html>"""


def render_json(summary: dict) -> str:
    return json.dumps(summary, indent=2) + "\n"

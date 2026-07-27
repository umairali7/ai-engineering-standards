"""Qualification-bounded deployment guidance derived from ECM evidence."""
from __future__ import annotations

import html
import json
from pathlib import Path

from . import constants as C, ecm, qualification, workspace


class GuidanceError(ValueError):
    pass


def engineering_fit(ref: str, *, matrix: dict | None = None) -> dict:
    """Derive non-authorizing engineering fit from observed task evidence.

    This is intentionally not Deployment Guidance. It helps engineers interpret
    automated evaluations without requiring a Qualification Record and cannot
    create operational authority.
    """
    matrix = matrix or ecm.engineering_capability_matrix(ref)
    rows = []
    for task in matrix["tasks"]:
        observed = task.get("observed_performance")
        percent = round(observed / 4 * 100, 1) if observed is not None else None
        distinct = task.get("distinct_scenarios", 0)
        minimum = task.get("minimum_observations") or 0
        breadth = round(min(1.0, distinct / minimum) * 100, 1) if minimum else 0.0
        assurance = task.get("evidence_assurance") or {}
        critical_failures = list(task.get("critical_failures") or [])
        if percent is None:
            fit = "not-assessed"
            explanation = "no directly mapped scored scenario evidence"
        elif breadth < 50:
            fit = "limited-evidence"
            explanation = (
                "direct scenario breadth is too limited for a fit label; "
                "treat the observed score as an early signal")
        elif critical_failures:
            fit = "review-recommended"
            explanation = (
                f"{len(critical_failures)} critical individual failure(s) "
                "prevent a strong-fit label even though the aggregate is high")
        elif percent >= 75:
            fit = "strong-observed-fit"
            explanation = (
                "strong observed performance with material scenario breadth; "
                "validate against the intended workload")
        elif percent >= 50:
            fit = "review-recommended"
            explanation = "moderate observed performance; engineering review is recommended"
        else:
            fit = "weak-observed-fit"
            explanation = "weak observed performance; prefer alternatives or add controls"
        rows.append({
            "task_id": task["task_id"],
            "task": task["task"],
            "fit": fit,
            "observed_performance_percent": percent,
            "scenario_breadth_percent": breadth,
            # Compatibility alias for engineering-fit schema 1 readers.
            "evidence_confidence_percent": breadth,
            "evidence_assurance": assurance,
            "critical_failure_count": len(critical_failures),
            "critical_failures": critical_failures,
            "distinct_scenarios": distinct,
            "rating_observations": task.get("rating_observations", 0),
            "explanation": explanation,
        })
    return {
        "kind": "engineering-fit-guidance",
        "engineering_fit_schema": 2,
        "status": "informational",
        "run_id": matrix["run_id"],
        "subject": matrix["subject"],
        "risk_tier": matrix["risk_tier"],
        "profile": matrix["profile"],
        "evaluation_scope": matrix.get("evaluation_scope"),
        "human_evaluation": (matrix.get("engineering_evaluation") or {}).get(
            "human_evaluation"),
        "tasks": rows,
        "authority_boundary": (
            "Engineering fit interprets observed evidence only. It is not a "
            "qualification, deployment recommendation, grant, or authorization."),
    }


def render_fit_markdown(result: dict) -> str:
    human = result.get("human_evaluation") or {}
    human_label = (
        f"Reviewed — {human.get('evaluator') or 'named human'}"
        if human.get("status") == "reviewed" else "Not reviewed (optional)")
    sections = (
        ("Strong observed fit", "strong-observed-fit"),
        ("Observed score, limited evidence", "limited-evidence"),
        ("Use with engineering review", "review-recommended"),
        ("Weak observed fit", "weak-observed-fit"),
        ("Not assessed", "not-assessed"),
    )
    lines = [
        "# AIES Engineering Fit Guidance", "",
        "> **INFORMATIONAL — NOT A QUALIFICATION, GRANT, DEPLOYMENT "
        "RECOMMENDATION, OR AUTHORIZATION.**", "",
        f"Subject: `{result['subject']}`  ",
        f"Run: `{result['run_id']}`  ",
        f"Evaluation composition: "
        f"{(result.get('evaluation_scope') or {}).get('label', 'not disclosed')}  ",
        f"Weighting: {result['profile']} profile "
        f"({(result.get('evaluation_scope') or {}).get('profile_role', 'role not disclosed')})  ",
        f"Risk scope: {C.risk_tier_label(result['risk_tier'])}  ",
        f"Human evaluation: {human_label}", "",
    ]
    for title, code in sections:
        lines.extend([f"## {title}", ""])
        selected = [row for row in result["tasks"] if row["fit"] == code]
        if not selected:
            lines.append("- None.")
        for row in selected:
            performance = (
                "not assessed" if row["observed_performance_percent"] is None
                else f"{row['observed_performance_percent']:.1f}% observed performance")
            lines.append(
                f"- `{row['task_id']} — {row['task']}`: {performance}; "
                f"{row['scenario_breadth_percent']:.1f}% scenario breadth "
                f"({row['distinct_scenarios']} distinct scenarios). "
                f"Evidence assurance: "
                f"{(row.get('evidence_assurance') or {}).get('status', 'not disclosed')}. "
                f"{row['explanation']}.")
        lines.append("")
    lines.extend([
        "## Boundary", "",
        "- Human evaluation is optional for engineering fit and is displayed when supplied.",
        "- Use `aies guidance <run> --qualification <QUAL-ID>` for separately "
        "governed, qualification-bounded Deployment Guidance.",
        "- This artifact cannot create or expand authority.", "",
    ])
    return "\n".join(lines)


def render_fit_html(result: dict) -> str:
    human = result.get("human_evaluation") or {}
    human_label = (
        f"Reviewed — {human.get('evaluator') or 'named human'}"
        if human.get("status") == "reviewed" else "Not reviewed (optional)")
    labels = {
        "strong-observed-fit": "Strong observed fit",
        "limited-evidence": "Observed score, limited evidence",
        "review-recommended": "Use with engineering review",
        "weak-observed-fit": "Weak observed fit",
        "not-assessed": "Not assessed",
    }
    sections = []
    for code, label in labels.items():
        selected = [row for row in result["tasks"] if row["fit"] == code]
        items = "".join(
            "<li><code>" + html.escape(f"{row['task_id']} — {row['task']}") +
            "</code>: " +
            html.escape(
                "not assessed" if row["observed_performance_percent"] is None
                else f"{row['observed_performance_percent']:.1f}% observed performance") +
            f"; {row['scenario_breadth_percent']:.1f}% scenario breadth "
            f"({row['distinct_scenarios']} distinct scenarios). " +
            html.escape(
                "Evidence assurance: " +
                str((row.get("evidence_assurance") or {}).get(
                    "status", "not disclosed")) + ". ") +
            html.escape(row["explanation"]) + ".</li>"
            for row in selected) or "<li>None.</li>"
        sections.append(f"<h2>{html.escape(label)}</h2><ul>{items}</ul>")
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>AIES Engineering Fit Guidance</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 24px;color:#18202a}}.banner{{padding:12px;background:#e8f5e9;border-left:5px solid #1a7f37}}</style></head><body>
<h1>AIES Engineering Fit Guidance</h1><p class='banner'><strong>INFORMATIONAL — NOT A QUALIFICATION, GRANT, DEPLOYMENT RECOMMENDATION, OR AUTHORIZATION.</strong></p>
<p><strong>Subject:</strong> <code>{html.escape(result['subject'])}</code><br>
<strong>Evaluation composition:</strong> {html.escape((result.get('evaluation_scope') or {}).get('label', 'not disclosed'))}<br>
<strong>Weighting:</strong> {html.escape(result['profile'])} profile ({html.escape((result.get('evaluation_scope') or {}).get('profile_role', 'role not disclosed'))})<br>
<strong>Risk scope:</strong> {html.escape(C.risk_tier_label(result['risk_tier']))}<br>
<strong>Human evaluation:</strong> {html.escape(human_label)}</p>
{''.join(sections)}
<h2>Boundary</h2><p>Human evaluation is optional. Supply a Qualification Record to the CLI for separately governed Deployment Guidance.</p>
</body></html>"""


def write_fit_artifacts(ref: str, *, matrix: dict | None = None) -> dict[str, str]:
    matrix = matrix or ecm.engineering_capability_matrix(ref)
    result = engineering_fit(ref, matrix=matrix)
    rdir = workspace.run_dir(matrix["run_id"])
    paths = {
        "markdown": rdir / "engineering-fit-guidance.md",
        "json": rdir / "engineering-fit-guidance.json",
        "html": rdir / "engineering-fit-guidance.html",
    }
    workspace.write_view(paths["markdown"], render_fit_markdown(result))
    workspace.write_view(paths["json"], json.dumps(result, indent=2) + "\n")
    workspace.write_view(paths["html"], render_fit_html(result))
    return {format: str(path) for format, path in paths.items()}


def _autonomy_cap(task: dict, record: dict, risk_tier: str) -> str:
    caps = [(task.get("task_decision") or {}).get("al_envelope", {}).get(risk_tier)]
    for area in task.get("areas") or []:
        claim = ((record.get("scope") or {}).get("areas") or {}).get(area) or {}
        caps.append((claim.get("al_envelope") or {}).get(risk_tier))
    usable = [cap for cap in caps if cap in C.AL_ORDER]
    if not usable:
        return "AL0"
    return min(usable, key=C.AL_ORDER.index)


def _scope_check(matrix: dict, task: dict, record: dict,
                 requested_role: str | None, requested_phases: list[str] | None,
                 requested_autonomy: str | None,
                 current_check: dict | None) -> tuple[bool, list[str], str]:
    scope = record.get("scope") or {}
    reasons = []
    if record.get("status") not in ("active", "conditional"):
        reasons.append(f"qualification status is {record.get('status')}")
    if current_check and not current_check.get("environment_unchanged"):
        reasons.append("current deployment fingerprint does not match the qualification")
    subject_ids = {
        ((scope.get("subject") or {}).get("id")),
        ((record.get("subject") or {}).get("deployment")),
    }
    if matrix["subject"] not in subject_ids:
        reasons.append("qualification belongs to a different subject")
    if scope.get("risk_tier") != matrix["risk_tier"]:
        reasons.append("qualification risk tier does not match the ECM")
    if scope.get("profile") != matrix["profile"]:
        reasons.append("qualification profile does not match the ECM")
    missing_areas = sorted(set(task.get("areas") or []) - set(scope.get("areas") or {}))
    if missing_areas:
        reasons.append("qualification omits task competency areas: " + ", ".join(missing_areas))
    mapping = scope.get("engineering_task_mapping") or {}
    if (mapping.get("id") != matrix["mapping"]["kind"]
            or mapping.get("version") != matrix["mapping"]["version"]
            or mapping.get("schema") != matrix["mapping"]["schema"]):
        reasons.append("qualification engineering-task mapping does not match the ECM")
    if requested_role and scope.get("role") != requested_role:
        reasons.append("requested role is outside the qualification scope")
    requested_phase_set = set(requested_phases or [])
    if requested_phase_set and not requested_phase_set.issubset(set(scope.get("phases") or [])):
        reasons.append("requested SDLC phases are outside the qualification scope")
    cap = _autonomy_cap(task, record, matrix["risk_tier"])
    if requested_autonomy:
        if requested_autonomy not in C.AL_ORDER:
            raise GuidanceError(f"unknown requested autonomy {requested_autonomy!r}")
        if C.AL_ORDER.index(requested_autonomy) > C.AL_ORDER.index(cap):
            reasons.append(
                f"requested {C.autonomy_level_label(requested_autonomy)} exceeds "
                f"the scoped cap {C.autonomy_level_label(cap)}")
    return not reasons, reasons, cap


def decide(ref: str, *, qualification_id: str | None = None,
           requested_role: str | None = None,
           requested_phases: list[str] | None = None,
           requested_autonomy: str | None = None,
           matrix: dict | None = None) -> dict:
    """Return guidance decisions without creating deployment authority."""
    matrix = matrix or ecm.engineering_capability_matrix(ref)
    record = qualification.get_record(qualification_id) if qualification_id else None
    current_check = (
        qualification.check_current(qualification_id)
        if qualification_id and record.get("status") in ("active", "conditional")
        else None)
    rows = []
    for task in matrix["tasks"]:
        status = task["status"]
        reasons = list((task.get("task_decision") or {}).get("reasons") or [])
        cap = None
        if status == "demonstrated" and record:
            matched, scope_reasons, cap = _scope_check(
                matrix, task, record, requested_role, requested_phases,
                requested_autonomy, current_check)
            reasons.extend(scope_reasons)
            if matched:
                requires_review = (
                    record.get("status") == "conditional"
                    or bool(record.get("conditions"))
                    or C.AL_ORDER.index(cap) <= C.AL_ORDER.index("AL2"))
                guidance = "use-with-review" if requires_review else "use"
            else:
                guidance = "no-recommendation"
        elif status == "demonstrated":
            guidance = "no-recommendation"
            reasons.append("no Qualification Record was supplied")
        elif status in ("gate-failed", "performance-below-threshold"):
            guidance = "avoid-for-scoped-use"
        else:
            guidance = "no-recommendation"
        decision = task.get("task_decision") or {}
        maturity = decision.get("instrument_maturity") or {}
        total_instruments = maturity.get("total_distinct_scenarios", 0)
        calibrated = maturity.get("empirically_calibrated", 0)
        residual_risks = []
        if total_instruments and calibrated < total_instruments:
            residual_risks.append(
                f"{calibrated}/{total_instruments} task instruments are empirically calibrated")
        if status == "demonstrated":
            margins = [gate["decision_value"] - gate["threshold"]
                       for gate in decision.get("gates") or []
                       if gate.get("decision_value") is not None]
            if margins and min(margins) < 0.5:
                residual_risks.append(
                    f"smallest task gate margin is {min(margins):.3f} points")
        conditions = list(record.get("conditions") or []) if record else []
        validity = ((record.get("scope") or {}).get("validity") or {}) if record else {}
        operational_constraints = []
        if record:
            operational_constraints.append(
                "qualification remains valid only through " +
                str(validity.get("until") or "its recorded validity window"))
            operational_constraints.append(
                "deployment fingerprint must continue to match the qualified deployment")
        if requested_role:
            operational_constraints.append(
                f"use is limited to {C.identifier_label(requested_role)}")
        if requested_phases:
            operational_constraints.append(
                "use is limited to " + ", ".join(
                    C.identifier_label(phase) for phase in requested_phases))
        if cap:
            operational_constraints.append(
                f"autonomy must not exceed {C.autonomy_level_label(cap)}")
        rows.append({
            "task_id": task["task_id"], "task": task["task"],
            "task_status": status, "guidance": guidance,
            "max_autonomy": cap, "reasons": reasons,
            "conditions": conditions,
            "residual_risks": residual_risks,
            "operational_constraints": operational_constraints,
        })
    return {
        "kind": "deployment-guidance",
        "guidance_schema": 2,
        "status": "informational",
        "run_id": matrix["run_id"], "subject": matrix["subject"],
        "risk_tier": matrix["risk_tier"], "profile": matrix["profile"],
        "qualification_record": qualification_id,
        "qualification_current_check": current_check,
        "requested_scope": {
            "role": requested_role, "phases": requested_phases or [],
            "autonomy": requested_autonomy,
        },
        "tasks": rows,
    }


def render_markdown(ref: str, *, qualification_id: str | None = None,
                    requested_role: str | None = None,
                    requested_phases: list[str] | None = None,
                    requested_autonomy: str | None = None,
                    result: dict | None = None) -> str:
    result = result or decide(
        ref, qualification_id=qualification_id, requested_role=requested_role,
        requested_phases=requested_phases,
        requested_autonomy=requested_autonomy)
    lines = [
        "# AIES Deployment Guidance", "",
        "> **INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.**", "",
        f"Subject: `{result['subject']}`  ", f"Run: `{result['run_id']}`  ",
        f"Scope: {C.risk_tier_label(result['risk_tier'])} · {result['profile']} profile  ",
        f"Qualification Record: `{result['qualification_record'] or 'not supplied'}`", "",
    ]
    sections = (
        ("Use", "use"),
        ("Use with human review", "use-with-review"),
        ("No recommendation — collect evidence or correct scope", "no-recommendation"),
        ("Avoid for this scoped use", "avoid-for-scoped-use"),
    )
    for title, code in sections:
        lines.extend([f"## {title}", ""])
        selected = [row for row in result["tasks"] if row["guidance"] == code]
        if not selected:
            lines.append("- None.")
        for row in selected:
            autonomy = (f"; up to {C.autonomy_level_label(row['max_autonomy'])}"
                        if row.get("max_autonomy") else "")
            reason = "; ".join(row["reasons"]) or "all ADR-0013 controls satisfied"
            lines.append(f"- `{row['task_id']} — {row['task']}`{autonomy}: {reason}.")
            for condition in row["conditions"]:
                lines.append(f"  - Condition: {condition}")
            for risk in row["residual_risks"]:
                lines.append(f"  - Residual risk: {risk}")
            for constraint in row["operational_constraints"]:
                lines.append(f"  - Constraint: {constraint}")
        lines.append("")
    lines.extend([
        "## Constraints", "",
        "- This artifact cannot grant authority or override qualification gates, conditions, risk-tier caps, or human accountability.",
        "- `Use` requires both a demonstrated task and a matching active human Qualification Record.",
        "- Observed or insufficient evidence never becomes `Use with Review`; it receives no recommendation.", "",
    ])
    return "\n".join(lines)


def render_html(ref: str, *, qualification_id: str | None = None,
                requested_role: str | None = None,
                requested_phases: list[str] | None = None,
                requested_autonomy: str | None = None,
                result: dict | None = None) -> str:
    result = result or decide(
        ref, qualification_id=qualification_id, requested_role=requested_role,
        requested_phases=requested_phases,
        requested_autonomy=requested_autonomy)
    labels = {
        "use": "Use",
        "use-with-review": "Use with human review",
        "no-recommendation": "No recommendation — collect evidence or correct scope",
        "avoid-for-scoped-use": "Avoid for this scoped use",
    }
    sections = []
    for code, label in labels.items():
        rows = [row for row in result["tasks"] if row["guidance"] == code]
        items = "".join(
            "<li><code>" + html.escape(f"{row['task_id']} — {row['task']}") +
            "</code>" + ("; up to " + html.escape(C.autonomy_level_label(row["max_autonomy"]))
                        if row.get("max_autonomy") else "") + ": " +
            html.escape("; ".join(row["reasons"]) or "all ADR-0013 controls satisfied") +
            "".join("<br><strong>Condition:</strong> " + html.escape(value)
                    for value in row["conditions"]) +
            "".join("<br><strong>Residual risk:</strong> " + html.escape(value)
                    for value in row["residual_risks"]) +
            "".join("<br><strong>Constraint:</strong> " + html.escape(value)
                    for value in row["operational_constraints"]) +
            ".</li>" for row in rows) or "<li>None.</li>"
        sections.append(f"<h2>{html.escape(label)}</h2><ul>{items}</ul>")
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>AIES Deployment Guidance</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 24px;color:#18202a}}.banner{{padding:12px;background:#fff3cd;border-left:5px solid #d99b00}}code{{white-space:normal}}</style></head><body>
<h1>AIES Deployment Guidance</h1><p class='banner'><strong>INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.</strong></p>
<p><strong>Subject:</strong> <code>{html.escape(result['subject'])}</code><br>
<strong>Scope:</strong> {html.escape(C.risk_tier_label(result['risk_tier']))} · {html.escape(result['profile'])} profile<br>
<strong>Qualification Record:</strong> <code>{html.escape(result['qualification_record'] or 'not supplied')}</code></p>
{''.join(sections)}
<h2>Constraints</h2><ul><li>This artifact cannot create or expand authority.</li><li>Observed or insufficient evidence never becomes Use with human review.</li></ul>
<p><a href='executive-summary.html'>Executive Summary</a> · <a href='engineering-capability-matrix.html'>Engineering Capability Matrix</a> · <a href='report.html'>Qualification Evidence Package</a></p>
</body></html>"""


def write_artifacts(ref: str, *, qualification_id: str | None = None,
                    requested_role: str | None = None,
                    requested_phases: list[str] | None = None,
                    requested_autonomy: str | None = None,
                    matrix: dict | None = None) -> dict[str, str]:
    matrix = matrix or ecm.engineering_capability_matrix(ref)
    run_id = matrix["run_id"]
    options = {
        "qualification_id": qualification_id,
        "requested_role": requested_role,
        "requested_phases": requested_phases,
        "requested_autonomy": requested_autonomy,
    }
    result = decide(run_id, matrix=matrix, **options)
    rdir = workspace.run_dir(run_id)
    paths = {
        "markdown": rdir / "deployment-guidance.md",
        "json": rdir / "deployment-guidance.json",
        "html": rdir / "deployment-guidance.html",
    }
    workspace.write_view(paths["markdown"], render_markdown(run_id, result=result, **options))
    workspace.write_view(paths["json"], json.dumps(result, indent=2) + "\n")
    workspace.write_view(paths["html"], render_html(run_id, result=result, **options))
    return {format: str(path) for format, path in paths.items()}


def write(ref: str, *, qualification_id: str | None = None,
          requested_role: str | None = None,
          requested_phases: list[str] | None = None,
          requested_autonomy: str | None = None) -> Path:
    paths = write_artifacts(
        ref, qualification_id=qualification_id, requested_role=requested_role,
        requested_phases=requested_phases,
        requested_autonomy=requested_autonomy)
    return Path(paths["markdown"])

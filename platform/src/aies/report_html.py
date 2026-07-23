"""HTML rendering of an evidence package (M3, PLATFORM.md §9).

Presentation-grade rendering of the SAME data the Markdown/JSON reports
carry — never additional claims. The output is a single self-contained
file (inline CSS, no external requests), theme-aware, and print-ready so
a browser's "Save as PDF" produces the PDF deliverable without bundling
a heavy PDF dependency (the platform's only dependency stays PyYAML).
"""

from __future__ import annotations

import html

from . import constants as C
from . import workspace


def _esc(x) -> str:
    return html.escape(str(x))


_CSS = """
:root { color-scheme: light dark;
  --fg:#1a1a1a; --bg:#ffffff; --muted:#666; --line:#ddd;
  --pass:#1a7f37; --fail:#cf222e; --warn:#9a6700; --card:#f6f8fa; }
@media (prefers-color-scheme: dark) { :root {
  --fg:#e6e6e6; --bg:#0d1117; --muted:#9aa; --line:#30363d;
  --pass:#3fb950; --fail:#f85149; --warn:#d29922; --card:#161b22; } }
* { box-sizing: border-box; }
body { font: 15px/1.5 system-ui, sans-serif; color: var(--fg);
  background: var(--bg); margin: 0; padding: 2rem; max-width: 60rem; }
h1 { font-size: 1.6rem; margin: 0 0 .3rem; }
h2 { font-size: 1.2rem; margin: 2rem 0 .6rem; border-bottom: 1px solid var(--line);
  padding-bottom: .3rem; }
.banner { padding: .7rem 1rem; border-radius: 6px; margin: 1rem 0; font-weight: 600; }
.banner.grant { background: var(--card); border: 1px solid var(--line); }
.banner.nondec { background: color-mix(in srgb, var(--warn) 15%, transparent);
  border: 1px solid var(--warn); color: var(--warn); }
table { border-collapse: collapse; width: 100%; margin: .6rem 0; font-size: .9rem; }
th, td { text-align: left; padding: .35rem .6rem; border-bottom: 1px solid var(--line); }
th { color: var(--muted); font-weight: 600; }
code { background: var(--card); padding: .1rem .3rem; border-radius: 3px; font-size: .85em; }
.pass { color: var(--pass); font-weight: 600; }
.fail { color: var(--fail); font-weight: 600; }
.muted { color: var(--muted); }
.env td:first-child { color: var(--muted); width: 12rem; }
details { margin: .8rem 0; border: 1px solid var(--line); border-radius: 6px; padding: .45rem .7rem; }
summary { cursor: pointer; font-weight: 650; }
footer { margin-top: 3rem; color: var(--muted); font-size: .8rem;
  border-top: 1px solid var(--line); padding-top: .8rem; }
@media print { body { padding: 0; max-width: none; } h2 { page-break-after: avoid; }
  table { page-break-inside: avoid; } }
"""


def render_html(
    run_id: str,
    *,
    matrix: dict | None = None,
    context=None,
) -> str:
    from . import report_view

    context = context or report_view.build_context(run_id, matrix=matrix)
    view = context.view
    formal = view["formal_qualification_requested"]
    fp = view["environment"]
    human_review = view["human_review"]
    evaluation = view["engineering_evaluation"]
    diagnostic_summary = view["grounding_diagnostics"]
    matrix = context.matrix
    area_models = {area["code"]: area for area in view["areas"]}
    p: list[str] = []
    w = p.append
    subject = view["subject"]
    scope = view["scope"]
    subject_id = subject["id"]

    w("<!doctype html><html lang=en><head><meta charset=utf-8>")
    w("<meta name=viewport content='width=device-width, initial-scale=1'>")
    title = view["title"]
    w(f"<title>{title} — {_esc(subject_id)}</title>")
    w(f"<style>{_CSS}</style></head><body>")

    w(f"<h1>{title}</h1>")
    w(f"<div class=muted>Run <code>{_esc(view['run_id'])}</code></div>")
    w(f"<p><strong>Subject:</strong> <code>{_esc(subject_id)}</code> "
      f"({_esc(subject['kind'])}; executor: "
      f"{_esc(subject['executor_kind'])}) &middot; "
      f"<strong>Deployment / model evidence:</strong> "
      f"<code>{_esc(subject['deployment_evidence'])}</code> "
      f"&middot; <strong>Profile:</strong> {_esc(scope['profile'])} "
      f"&middot; <strong>Scoped risk tier:</strong> "
      f"{_esc(scope['risk_tier_label'])} "
      f"&middot; <strong>Subject class:</strong> "
      f"{_esc(scope['subject_kind_label'])}</p>")

    banner = (view["status"]["grant_status"] if formal else
              "ENGINEERING EVALUATION " +
              str(evaluation.get("status", "not-scored")).upper())
    w(f"<div class='banner grant'>{_esc(banner)}</div>")
    admission = view["qualification"]["rating_admission"]
    if formal and admission.get("advisory_ratings", 0):
        reason = admission.get("reviewer_reason") or "reviewer admission not recorded"
        w("<div class='banner nondec'><strong>ADVISORY AUTOMATED REVIEW</strong> "
          f"&mdash; {admission['advisory_ratings']} automated rating(s) are excluded from "
          "qualification scoring. Reviewer admission permits corroborating peer review, "
          "not automated-only qualification evidence. "
          f"{_esc(reason)} (AIES-AESQS-ER-01-R10; ADR-0012)</div>")
    nondec = view["qualification"]["nondecisional_areas"]
    if formal and nondec:
        w(f"<div class='banner nondec'>NON-DECISIONAL — sample below the AESQS "
          f"minimum for {_esc(', '.join(C.competency_label(area) for area in nondec))} (AIES-AESQS-CS-01 §6). "
          "These results must not be presented as qualification evidence.</div>")

    w("<h2>Engineering Evaluation</h2>")
    w(f"<p><strong>Evaluation status: {_esc(str(evaluation.get('status', 'not-scored')).upper())}</strong>"
      f" &middot; <strong>Human evaluation:</strong> "
      f"{_esc(view['status']['human_evaluation_label'])}</p>")
    w("<p class=muted>Automated scores are sufficient to complete this informational "
      "engineering evaluation and its ECM decision products. Human evaluation is "
      "optional here; formal qualification and grants use a separate explicit protocol.</p>")
    w("<table><tr><th>Area</th><th>Automated score coverage</th>"
      "<th>Observed automated mean</th><th>Human eval</th><th>Evaluation status</th></tr>")
    for area, evaluation_area in (evaluation.get("areas") or {}).items():
        automated = (evaluation_area.get("sources") or {}).get("automated") or {}
        mean_value = automated.get("observed_mean")
        status = str(evaluation_area.get("status", "not-scored")).upper()
        if evaluation_area.get("completed_by"):
            status += f" — {evaluation_area['completed_by']}"
        w(f"<tr><td>{_esc(C.competency_label(area))}</td>"
          f"<td>{automated.get('responses_scored', 0)}/{automated.get('responses_total', 0)} "
          f"({automated.get('coverage_percent', 0):.1f}%)</td>"
          f"<td>{_esc(mean_value if mean_value is not None else '—')}</td>"
          f"<td>{_esc(view['status']['human_evaluation_label'])}</td>"
          f"<td><strong>{_esc(status)}</strong></td></tr>")
    w("</table>")

    if not formal:
        w("<h2>Automated Score Detail</h2>")
        w("<p class=muted>These are observed reviewer measurements. Human "
          "evaluation is optional and appears separately when supplied.</p>")
        for area in evaluation.get("areas") or {}:
            w(f"<h3>{_esc(C.competency_label(area))}</h3>")
            w("<table><tr><th>Dimension</th><th>Automated review</th>"
              "<th>Human eval (optional)</th></tr>")
            for dimension in area_models[area]["dimensions"]:
                automated = report_view.source_display(
                    dimension["sources"]["automated"])
                human = report_view.source_display(
                    dimension["sources"]["human"])
                w(f"<tr><td>{_esc(dimension['label'])}</td>"
                  f"<td>{_esc(automated)}</td><td>{_esc(human)}</td></tr>")
            w("</table>")
        if human_review:
            evaluator = (
                (human_review.get("human_evaluation") or {}).get("evaluator"))
            w("<h2>Optional Human Evaluation</h2><p>" +
              _esc(f"Reviewed — {evaluator}" if evaluator
                   else "Not reviewed (optional)") + "</p>")
        w("<h2>Environment Fingerprint</h2><table class=env>")
        for key in ("machine", "cpu", "gpu", "ram_gb", "os", "python"):
            w(f"<tr><td>{key}</td><td>{_esc(fp.get(key, 'unknown'))}</td></tr>")
        runtime = fp.get("runtime", {})
        w(f"<tr><td>runtime</td><td>{_esc(runtime.get('id','?'))} "
          f"v{_esc(runtime.get('version','?'))}</td></tr>")
        w(f"<tr><td>fingerprint</td><td><code>"
          f"{_esc(fp.get('fingerprint_hash','unknown'))}</code></td></tr></table>")
        from . import diagnostics, ecm
        w(diagnostics.render_report_section_html(diagnostic_summary))
        w(ecm.render_capability_summary_html(matrix))
        w("<h2>Optional Formal Qualification</h2><p>Formal qualification was "
          "<strong>not requested</strong> and therefore has no readiness verdict "
          "in this report. Invoke the explicit formal-qualification path only "
          "when that governed decision is intended.</p>")
        w("<p><a href='executive-summary.html'>Executive Summary</a> &middot; "
          "<a href='engineering-assessment-result.html'>Engineering Assessment Result</a> &middot; "
          "<a href='engineering-fit-guidance.html'>Engineering Fit Guidance</a> &middot; "
          "<a href='grounding-diagnostics.html'>Grounding Diagnostics</a> &middot; "
          "<a href='engineering-capability-matrix.html'>Engineering Capability Matrix</a></p>")
        provenance = view["provenance"]
        w("<footer>Raters: " + _esc(", ".join(provenance["raters"])) +
          f" &middot; Aggregated {_esc(provenance['aggregated_at'])} &middot; "
          "Generated by AIES Engineering Assessment Platform.</footer>")
        w("</body></html>")
        return "".join(p)

    w("<h2>Grant Readiness (Formal Qualification)</h2>")
    w("<table><tr><th>Area</th><th>Decisional</th><th>Gates</th><th>CL</th>"
      "<th>Verdict — informs a human grant</th></tr>")
    for area_model in view["areas"]:
        area = area_model["code"]
        verdict = area_model["readiness"]["verdict"]
        why = area_model["readiness"]["reason"]
        gates = area_model["readiness"]["gate_status"]
        evidence = area_model["evidence"]
        competency = area_model["competency_level"]
        verdict_class = "pass" if verdict == "THRESHOLD MET" else "fail"
        w(f"<tr><td>{_esc(C.competency_label(area))}</td>"
          f"<td>{'yes' if evidence['decisional'] else 'no'}</td><td>{gates}</td>"
          f"<td>{_esc(competency['label'] or '-')}</td>"
          f"<td class={verdict_class}><strong>{_esc(verdict)}</strong> — {_esc(why)}</td></tr>")
    w("</table>")
    readiness_model = view["qualification"]["readiness"]
    readiness = readiness_model["status"]
    blocked = readiness_model["blocked_areas"]
    if readiness == "READY":
        w("<p class='pass'><strong>Overall: READY</strong> — every scoped area "
          "is decisional and passes its gates. This is not a grant; a named "
          "human authority records any grant.</p>")
    else:
        labels = ", ".join(C.competency_label(area) for area in blocked)
        w(f"<p class='fail'><strong>Overall: BLOCKED</strong> — formal qualification "
          f"is not grant-ready for {_esc(labels)}. This does not block the completed "
          "Engineering Evaluation above.</p>")
    w(f"<p><strong>Qualification coverage:</strong> "
      f"{readiness_model['threshold_met_areas']}/{readiness_model['total_areas']} "
      "scoped areas meet the admitted-evidence threshold. This is not a grant; "
      "a named human authority records any grant.</p>")

    if human_review:
        advisory = human_review.get("automated_advisory_review") or {}
        evaluator = (human_review.get("human_evaluation") or {}).get("evaluator")
        w("<h2>Optional Human Evaluation Record</h2><table>")
        w("<tr><th>Review input</th><th>Human record</th></tr>")
        w(f"<tr><td>Advisory automated scores</td><td>"
          f"{'considered' if advisory.get('considered') else 'not declared'}</td></tr>")
        human_label = f"☑ Reviewed — {evaluator}" if evaluator else "☐ Not reviewed (optional)"
        w(f"<tr><td>Human evaluation</td><td>{_esc(human_label)}</td></tr>")
        w("</table><p class=muted>This is a human review declaration over evidence; "
          "it is not a grant. Formal grants remain blocked until decisional and "
          "gate-passing evidence exists.</p>")

    w("<h2>Environment Fingerprint</h2><table class=env>")
    for k in ("machine", "cpu", "gpu", "ram_gb", "os", "python"):
        w(f"<tr><td>{k}</td><td>{_esc(fp.get(k, 'unknown'))}</td></tr>")
    rt = fp.get("runtime", {})
    w(f"<tr><td>runtime</td><td>{_esc(rt.get('id','?'))} v{_esc(rt.get('version','?'))}</td></tr>")
    w(f"<tr><td>fingerprint</td><td><code>{_esc(fp.get('fingerprint_hash','unknown'))}</code></td></tr>")
    w("</table>")
    w("<p class=muted>Evidence is bound to this fingerprint; a changed fingerprint "
      "is a re-qualification trigger (PLATFORM.md D7).</p>")

    w("<h2>Detailed qualification evidence</h2>")
    w("<p class=muted>Expand an area for its dimension-level scores, gates, and policy envelope. "
      "The Grant Readiness table above remains the authoritative summary.</p>")
    for area_model in view["areas"]:
        area = area_model["code"]
        evidence = area_model["evidence"]
        protocol = area_model["rater_protocol"]
        w(f"<details><summary>{_esc(area_model['label'])} — "
          f"{_esc(scope['risk_tier_label'])} detailed evidence</summary>")
        w(f"<p class=muted>Suite <code>{_esc(area_model['suite_version'])}</code> "
          f"&middot; resolved evidence items: {evidence['resolved_items']} "
          f"&middot; verified admitted observations: {evidence['admitted_observations']} "
          f"&middot; distinct scored scenarios: "
          f"{evidence['distinct_scenarios']} (adequacy minimum {evidence['minimum']} by "
          f"{'distinct scenarios' if evidence['adequacy_basis'] == 'distinct_scenarios' else 'legacy scored items'}) "
          f"&middot; advisory automated ratings: {evidence['advisory_automated_ratings']} "
          f"&middot; decisional: {'yes' if evidence['decisional'] else 'NO'}</p>")
        if protocol:
            status = "SATISFIED" if protocol.get("satisfied") else "INCOMPLETE"
            w(f"<p><strong>Rater protocol: {_esc(status)}</strong> &middot; verified items "
              f"{protocol.get('qualification_eligible_items', 0)}/{protocol.get('total_items', 0)} "
              f"&middot; double-rating {protocol.get('double_rating_fraction', 0):.1%} "
              f"(required {protocol.get('required_double_rating_fraction', 0):.0%}) "
              f"&middot; adjacent agreement {protocol.get('agreement_fraction', 0):.1%} "
              f"(required {protocol.get('agreement_threshold', 0):.0%})</p>")
            if protocol.get("reasons"):
                w("<ul>" + "".join(f"<li>{_esc(reason)}</li>" for reason in protocol["reasons"]) + "</ul>")
        w("<table><tr><th>Dimension</th><th>Automated review</th>"
          "<th>Human eval (optional)</th><th>Resolved item n</th><th>Resolved item mean</th><th>90% CI</th>"
          "<th>Decision value</th><th>Gate</th><th>Result</th></tr>")
        for dimension in area_model["dimensions"]:
            ds = dimension["resolved"]
            gate = dimension["gate"]
            automated = report_view.source_display(
                dimension["sources"]["automated"])
            human = report_view.source_display(
                dimension["sources"]["human"])
            cls = "pass" if gate["passed"] else "fail"
            res = gate["status"]
            if ds:
                w(f"<tr><td>{_esc(dimension['label'])}</td>"
                  f"<td>{_esc(automated)}</td><td>{_esc(human)}</td><td>{ds['n']}</td>"
                  f"<td>{ds['mean']}</td><td>[{ds['ci90_low']}, {ds['ci90_high']}]</td>"
                  f"<td><strong>{ds['decision_value']}</strong></td>"
                  f"<td>&ge; {gate['threshold'] if gate['threshold'] is not None else '-'}</td>"
                  f"<td class={cls}>{res}</td></tr>")
            else:
                w(f"<tr><td>{_esc(dimension['label'])}</td>"
                  f"<td>{_esc(automated)}</td><td>{_esc(human)}</td><td>0</td><td>-</td><td>-</td>"
                  f"<td>-</td><td>&ge; "
                  f"{gate['threshold'] if gate['threshold'] is not None else '-'}</td>"
                  f"<td class=fail>FAIL</td></tr>")
        w("</table>")
        w("<p class=muted>Automated-review and human-review values are displayed "
          "separately. A human score is optional for this evidence view; a named "
          "human authority is still required for any grant.</p>")
        if area_model["ev3_hard_fail"]:
            w("<p class=fail>EV3 hard gate failed — qualification must be denied at "
              "this tier regardless of the aggregate (AIES-AESQS-CS-01-R04).</p>")
        agg = area_model["aggregate"]
        competency = area_model["competency_level"]
        w(f"<p><strong>Aggregate A (decision values, profile-weighted):</strong> "
          f"{agg if agg is not None else '-'} &middot; "
          f"<strong>Score-bounded CL:</strong> {_esc(competency['label'] or 'none')}</p>")
        w("<p class=muted>Derived policy envelope only: this run directly assesses "
          f"{_esc(scope['risk_tier_label'])}; it does not establish evidence at other tiers.</p>")
        w("<table><tr><th>Risk tier</th><th>Recommended max AL</th></tr>")
        for envelope in area_model["autonomy_envelope"]:
            w(f"<tr><td><strong>{_esc(envelope['risk_tier_label'])}</strong></td>"
              f"<td><strong>{_esc(envelope['autonomy_level_label'])}</strong></td></tr>")
        w("</table>")
        w("</details>")

    from . import diagnostics, ecm
    w(diagnostics.render_report_section_html(diagnostic_summary))
    w(ecm.render_capability_summary_html(matrix))
    w("<p><a href='executive-summary.html'>Executive Summary</a> &middot; "
      "<a href='deployment-guidance.html'>Deployment Guidance</a> &middot; "
      "<a href='grounding-diagnostics.html'>Grounding Diagnostics</a> &middot; "
      "<a href='engineering-capability-matrix.html'>Engineering Capability Matrix</a></p>")

    provenance = view["provenance"]
    w("<footer>Raters: " + _esc(", ".join(provenance["raters"]))
      + f" &middot; Aggregated {_esc(provenance['aggregated_at'])}"
      " &middot; A comparison or report is presentation over existing evidence; "
      "it makes no additional claims. Generated by AIES Engineering Assessment Platform "
      "(docs/PLATFORM.md, AIES-DOC-06).</footer>")
    w("</body></html>")
    return "".join(p)


def write_html(run_id: str) -> str:
    path = workspace.run_dir(run_id) / "report.html"
    workspace.write_view(path, render_html(run_id))
    return str(path)

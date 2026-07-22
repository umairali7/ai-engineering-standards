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


def render_html(run_id: str) -> str:
    from . import evaluation as evaluation_view

    pkg = workspace.read_json(workspace.run_dir(run_id) / "evidence-package.json")
    fp = pkg["environment_fingerprint"]
    from .report import (_human_evaluation_label, _human_review_record,
                         _score_sources, _source_cell)
    source_scores = _score_sources(run_id)
    human_review = _human_review_record(run_id)
    p: list[str] = []
    w = p.append
    subject = pkg.get("subject") or {}
    subject_id = subject.get("id", pkg["model"]["registry_id"])

    w("<!doctype html><html lang=en><head><meta charset=utf-8>")
    w("<meta name=viewport content='width=device-width, initial-scale=1'>")
    w(f"<title>AIES Evidence Package — {_esc(subject_id)}</title>")
    w(f"<style>{_CSS}</style></head><body>")

    w("<h1>AIES Qualification Evidence Package</h1>")
    w(f"<div class=muted>Run <code>{_esc(pkg['run_id'])}</code></div>")
    w(f"<p><strong>Subject:</strong> <code>{_esc(subject_id)}</code> "
      f"({_esc(subject.get('kind', 'ai_deployment'))}; executor: "
      f"{_esc(subject.get('executor_kind', 'deployment'))}) &middot; "
      f"<strong>Deployment / model evidence:</strong> <code>{_esc(pkg['model']['registry_id'])}</code> "
      f"&middot; <strong>Profile:</strong> {_esc(pkg['profile'])} "
      f"&middot; <strong>Scoped risk tier:</strong> {_esc(C.risk_tier_label(pkg['risk_tier']))} "
      f"&middot; <strong>Subject class:</strong> {_esc(pkg['subject_kind'])}</p>")

    w(f"<div class='banner grant'>{_esc(pkg['grant_status'])}</div>")
    admission = pkg.get("rating_admission") or {}
    if admission.get("advisory_ratings", 0):
        reason = admission.get("reviewer_reason") or "reviewer admission not recorded"
        w("<div class='banner nondec'><strong>ADVISORY AUTOMATED REVIEW</strong> "
          f"&mdash; {admission['advisory_ratings']} automated rating(s) are excluded from "
          "qualification scoring. Reviewer admission permits corroborating peer review, "
          "not automated-only qualification evidence. "
          f"{_esc(reason)} (AIES-AESQS-ER-01-R10; ADR-0012)</div>")
    nondec = [a for a, d in pkg["areas"].items() if not d["decisional"]]
    if nondec:
        w(f"<div class='banner nondec'>NON-DECISIONAL — sample below the AESQS "
          f"minimum for {_esc(', '.join(C.competency_label(area) for area in nondec))} (AIES-AESQS-CS-01 §6). "
          "These results must not be presented as qualification evidence.</div>")

    evaluation = evaluation_view.summarize(run_id)
    w("<h2>Engineering Evaluation</h2>")
    w(f"<p><strong>Evaluation status: {_esc(str(evaluation.get('status', 'not-scored')).upper())}</strong>"
      f" &middot; <strong>Human evaluation:</strong> {_esc(_human_evaluation_label(evaluation))}</p>")
    w("<p class=muted>Automated scores are sufficient to complete this informational "
      "engineering evaluation and its ECM decision products. Human evaluation is "
      "optional here; formal qualification and grants use the separate protocol below.</p>")
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
          f"<td>{_esc(_human_evaluation_label(evaluation))}</td>"
          f"<td><strong>{_esc(status)}</strong></td></tr>")
    w("</table>")

    from .report import _area_verdict, _gate_status, _overall_readiness
    w("<h2>Grant Readiness (Formal Qualification)</h2>")
    w("<table><tr><th>Area</th><th>Decisional</th><th>Gates</th><th>CL</th>"
      "<th>Verdict — informs a human grant</th></tr>")
    verdicts = {}
    for area, d in pkg["areas"].items():
        verdict, why = _area_verdict(d)
        verdicts[area] = verdict
        gates = _gate_status(d)
        verdict_class = "pass" if verdict == "THRESHOLD MET" else "fail"
        w(f"<tr><td>{_esc(C.competency_label(area))}</td>"
          f"<td>{'yes' if d['decisional'] else 'no'}</td><td>{gates}</td>"
          f"<td>{_esc(C.identifier_label(d['cl']) if d.get('cl') else '-')}</td>"
          f"<td class={verdict_class}><strong>{_esc(verdict)}</strong> — {_esc(why)}</td></tr>")
    w("</table>")
    readiness, blocked = _overall_readiness(verdicts)
    if readiness == "READY":
        w("<p class='pass'><strong>Overall: READY</strong> — every scoped area "
          "is decisional and passes its gates. This is not a grant; a named "
          "human authority records any grant.</p>")
    else:
        labels = ", ".join(C.competency_label(area) for area in blocked)
        w(f"<p class='fail'><strong>Overall: BLOCKED</strong> — formal qualification "
          f"is not grant-ready for {_esc(labels)}. This does not block the completed "
          "Engineering Evaluation above.</p>")
    threshold_met = sum(1 for d in pkg["areas"].values()
                        if d["decisional"] and d.get("gates_passed") and not d.get("ev3_hard_fail"))
    w(f"<p><strong>Qualification coverage:</strong> {threshold_met}/{len(pkg['areas'])} "
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
    for area, d in pkg["areas"].items():
        w(f"<details><summary>{_esc(C.competency_label(area))} — "
          f"{_esc(C.risk_tier_label(pkg['risk_tier']))} detailed evidence</summary>")
        protocol = d.get("rater_protocol") or {}
        w(f"<p class=muted>Suite <code>{_esc(pkg['suite_versions'].get(area,'?'))}</code> "
          f"&middot; resolved evidence items: {d['n_scored']} "
          f"&middot; verified admitted observations: {d.get('admitted_ratings', 0)} "
          f"&middot; distinct scored scenarios: "
          f"{d.get('n_distinct_scenarios', d['n_scored'])} (adequacy minimum {d['min_sample']} by "
          f"{'distinct scenarios' if d.get('sample_adequacy_basis') == 'distinct_scenarios' else 'legacy scored items'}) "
          f"&middot; advisory automated ratings: {d.get('advisory_ratings', 0)} "
          f"&middot; decisional: {'yes' if d['decisional'] else 'NO'}</p>")
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
        gates = {g["dimension"]: g for g in d["gates"]}
        for dim in C.DIMENSIONS:
            ds = d["dimensions"].get(dim)
            g = gates.get(dim, {})
            automated = _source_cell(source_scores.get(area, {}), "automated", dim)
            human = _source_cell(source_scores.get(area, {}), "human", dim)
            cls = "pass" if g.get("passed") else "fail"
            res = "PASS" if g.get("passed") else "FAIL"
            if ds:
                w(f"<tr><td>{_esc(C.identifier_label(dim))}</td>"
                  f"<td>{_esc(automated)}</td><td>{_esc(human)}</td><td>{ds['n']}</td>"
                  f"<td>{ds['mean']}</td><td>[{ds['ci90_low']}, {ds['ci90_high']}]</td>"
                  f"<td><strong>{ds['ci90_low']}</strong></td>"
                  f"<td>&ge; {g.get('threshold','-')}</td>"
                  f"<td class={cls}>{res}</td></tr>")
            else:
                w(f"<tr><td>{_esc(C.identifier_label(dim))}</td>"
                  f"<td>{_esc(automated)}</td><td>{_esc(human)}</td><td>0</td><td>-</td><td>-</td>"
                  f"<td>-</td><td>&ge; {g.get('threshold','-')}</td>"
                  f"<td class=fail>FAIL</td></tr>")
        w("</table>")
        w("<p class=muted>Automated-review and human-review values are displayed "
          "separately. A human score is optional for this evidence view; a named "
          "human authority is still required for any grant.</p>")
        if d["ev3_hard_fail"]:
            w("<p class=fail>EV3 hard gate failed — qualification must be denied at "
              "this tier regardless of the aggregate (AIES-AESQS-CS-01-R04).</p>")
        agg = d["aggregate_A"]
        w(f"<p><strong>Aggregate A (decision values, profile-weighted):</strong> "
          f"{agg if agg is not None else '-'} &middot; "
          f"<strong>Score-bounded CL:</strong> {_esc(C.identifier_label(d['cl']) if d['cl'] else 'none')}</p>")
        w("<p class=muted>Derived policy envelope only: this run directly assesses "
          f"{_esc(C.risk_tier_label(pkg['risk_tier']))}; it does not establish evidence at other tiers.</p>")
        w("<table><tr><th>Risk tier</th><th>Recommended max AL</th></tr>")
        for tier, al in d["al_envelope"].items():
            w(f"<tr><td><strong>{_esc(C.risk_tier_label(tier))}</strong></td>"
              f"<td><strong>{_esc(C.autonomy_level_label(al))}</strong></td></tr>")
        w("</table>")
        w("</details>")

    from . import ecm
    w(ecm.render_capability_summary_html(ecm.engineering_capability_matrix(run_id)))

    w("<footer>Raters: " + _esc(", ".join(pkg["raters"]))
      + f" &middot; Aggregated {_esc(pkg['aggregated_at'])}"
      " &middot; A comparison or report is presentation over existing evidence; "
      "it makes no additional claims. Generated by AIES Engineering Assessment Platform "
      "(docs/PLATFORM.md, AIES-DOC-06).</footer>")
    w("</body></html>")
    return "".join(p)


def write_html(run_id: str) -> str:
    path = workspace.run_dir(run_id) / "report.html"
    path.write_text(render_html(run_id), encoding="utf-8")
    return str(path)

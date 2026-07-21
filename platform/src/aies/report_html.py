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
footer { margin-top: 3rem; color: var(--muted); font-size: .8rem;
  border-top: 1px solid var(--line); padding-top: .8rem; }
@media print { body { padding: 0; max-width: none; } h2 { page-break-after: avoid; }
  table { page-break-inside: avoid; } }
"""


def render_html(run_id: str) -> str:
    pkg = workspace.read_json(workspace.run_dir(run_id) / "evidence-package.json")
    fp = pkg["environment_fingerprint"]
    p: list[str] = []
    w = p.append

    w("<!doctype html><html lang=en><head><meta charset=utf-8>")
    w("<meta name=viewport content='width=device-width, initial-scale=1'>")
    w(f"<title>AIES Evidence Package — {_esc(pkg['model']['registry_id'])}</title>")
    w(f"<style>{_CSS}</style></head><body>")

    w("<h1>AIES Qualification Evidence Package</h1>")
    w(f"<div class=muted>Run <code>{_esc(pkg['run_id'])}</code></div>")
    w(f"<p><strong>Deployment:</strong> <code>{_esc(pkg['model']['registry_id'])}</code> "
      f"&middot; <strong>Profile:</strong> {_esc(pkg['profile'])} "
      f"&middot; <strong>Scoped risk tier:</strong> {_esc(C.risk_tier_label(pkg['risk_tier']))} "
      f"&middot; <strong>Subject:</strong> {_esc(pkg['subject_kind'])}</p>")

    w(f"<div class='banner grant'>{_esc(pkg['grant_status'])}</div>")
    nondec = [a for a, d in pkg["areas"].items() if not d["decisional"]]
    if nondec:
        w(f"<div class='banner nondec'>NON-DECISIONAL — sample below the AESQS "
          f"minimum for {_esc(', '.join(C.competency_label(area) for area in nondec))} (AIES-AESQS-CS-01 §6). "
          "These results must not be presented as qualification evidence.</div>")

    from .report import _area_verdict
    w("<h2>Grant Readiness</h2>")
    w("<table><tr><th>Area</th><th>Decisional</th><th>Gates</th><th>CL</th>"
      "<th>Verdict — informs a human grant</th></tr>")
    for area, d in pkg["areas"].items():
        verdict, why = _area_verdict(d)
        gates = "PASS" if d.get("gates_passed") and not d.get("ev3_hard_fail") else "FAIL"
        verdict_class = "pass" if verdict == "READY" else "fail"
        w(f"<tr><td>{_esc(C.competency_label(area))}</td>"
          f"<td>{'yes' if d['decisional'] else 'no'}</td><td>{gates}</td>"
          f"<td>{_esc(d.get('cl') or '-')}</td>"
          f"<td class={verdict_class}><strong>{_esc(verdict)}</strong> — {_esc(why)}</td></tr>")
    w("</table>")

    w("<h2>Environment Fingerprint</h2><table class=env>")
    for k in ("machine", "cpu", "gpu", "ram_gb", "os", "python"):
        w(f"<tr><td>{k}</td><td>{_esc(fp.get(k, 'unknown'))}</td></tr>")
    rt = fp.get("runtime", {})
    w(f"<tr><td>runtime</td><td>{_esc(rt.get('id','?'))} v{_esc(rt.get('version','?'))}</td></tr>")
    w(f"<tr><td>fingerprint</td><td><code>{_esc(fp.get('fingerprint_hash','unknown'))}</code></td></tr>")
    w("</table>")
    w("<p class=muted>Evidence is bound to this fingerprint; a changed fingerprint "
      "is a re-qualification trigger (PLATFORM.md D7).</p>")

    for area, d in pkg["areas"].items():
        w(f"<h2>{_esc(C.competency_label(area))} — {_esc(C.risk_tier_label(pkg['risk_tier']))}</h2>")
        w(f"<p class=muted>Suite <code>{_esc(pkg['suite_versions'].get(area,'?'))}</code> "
          f"&middot; scored items: {d['n_scored']} (minimum {d['min_sample']}) "
          f"&middot; decisional: {'yes' if d['decisional'] else 'NO'}</p>")
        w("<table><tr><th>Dimension</th><th>n</th><th>Mean</th><th>90% CI</th>"
          "<th>Decision value</th><th>Gate</th><th>Result</th></tr>")
        gates = {g["dimension"]: g for g in d["gates"]}
        for dim in C.DIMENSIONS:
            ds = d["dimensions"].get(dim)
            g = gates.get(dim, {})
            cls = "pass" if g.get("passed") else "fail"
            res = "PASS" if g.get("passed") else "FAIL"
            if ds:
                w(f"<tr><td>{dim} {C.DIMENSION_NAMES[dim]}</td><td>{ds['n']}</td>"
                  f"<td>{ds['mean']}</td><td>[{ds['ci90_low']}, {ds['ci90_high']}]</td>"
                  f"<td><strong>{ds['ci90_low']}</strong></td>"
                  f"<td>&ge; {g.get('threshold','-')}</td>"
                  f"<td class={cls}>{res}</td></tr>")
            else:
                w(f"<tr><td>{dim} {C.DIMENSION_NAMES[dim]}</td><td>0</td><td>-</td><td>-</td>"
                  f"<td>-</td><td>&ge; {g.get('threshold','-')}</td>"
                  f"<td class=fail>FAIL</td></tr>")
        w("</table>")
        if d["ev3_hard_fail"]:
            w("<p class=fail>EV3 hard gate failed — qualification must be denied at "
              "this tier regardless of the aggregate (AIES-AESQS-CS-01-R04).</p>")
        agg = d["aggregate_A"]
        w(f"<p><strong>Aggregate A (decision values, profile-weighted):</strong> "
          f"{agg if agg is not None else '-'} &middot; "
          f"<strong>Score-bounded CL:</strong> {_esc(d['cl'] or 'none')}</p>")
        w("<table><tr><th>Risk tier</th><th>Recommended max AL</th></tr>")
        for tier, al in d["al_envelope"].items():
            w(f"<tr><td><strong>{_esc(C.risk_tier_label(tier))}</strong></td>"
              f"<td><strong>{_esc(C.autonomy_level_label(al))}</strong></td></tr>")
        w("</table>")

    from . import ecm
    w(ecm.render_capability_summary_html(ecm.engineering_capability_matrix(run_id)))

    w("<footer>Raters: " + _esc(", ".join(pkg["raters"]))
      + f" &middot; Aggregated {_esc(pkg['aggregated_at'])}"
      " &middot; A comparison or report is presentation over existing evidence; "
      "it makes no additional claims. Generated by aies-platform "
      "(docs/PLATFORM.md, AIES-DOC-06).</footer>")
    w("</body></html>")
    return "".join(p)


def write_html(run_id: str) -> str:
    path = workspace.run_dir(run_id) / "report.html"
    path.write_text(render_html(run_id), encoding="utf-8")
    return str(path)

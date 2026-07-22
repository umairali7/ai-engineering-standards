"""Dashboard (M4, PLATFORM.md §10): a self-contained HTML overview of
deployments, runs, and qualification records.

**A renderer, not a decider.** Per the platform invariant (CONFORMANCE-POLICY.md
§4), no consumer computes outcomes: the dashboard — like the CLI, a future REST
API, or a GitHub Action — only *renders* results the engine already produced. It
makes no claims the records do not and re-derives no PASS/FAIL. Single file, no
external requests, theme-aware (same discipline as the HTML report).
"""

from __future__ import annotations

import html

from . import constants as C, registry, workspace
from .report_html import _CSS


def _esc(x) -> str:
    return html.escape(str(x))


def render_dashboard() -> str:
    from . import compare, qualification
    deployments = registry.list_entries(include_retired=True)
    runs = compare.list_runs()
    records = qualification.list_records()

    p: list[str] = []
    w = p.append
    w("<!doctype html><html lang=en><head><meta charset=utf-8>")
    w("<meta name=viewport content='width=device-width, initial-scale=1'>")
    w("<title>AIES Engineering Assessment Dashboard</title>")
    w(f"<style>{_CSS}</style></head><body>")
    w("<h1>AIES Engineering Assessment Dashboard</h1>")
    w("<p class=muted>Overview of registered deployments, assessment runs, "
      "and human-recorded grants. Presentation over the run and record files — "
      "no additional claims (docs/PLATFORM.md, AIES-DOC-06).</p>")

    w(f"<h2>Deployments ({len(deployments)})</h2><table>"
      "<tr><th>Deployment</th><th>Model</th><th>Runtime</th><th>Status</th></tr>")
    for d in deployments:
        w(f"<tr><td><code>{_esc(d['id'])}</code></td>"
          f"<td>{_esc(d.get('model') or d.get('family') or '?')}</td>"
          f"<td>{_esc(d.get('runtime','?'))}</td>"
          f"<td>{'retired' if d.get('retired') else 'active'}</td></tr>")
    w("</table>")

    w(f"<h2>Qualification runs ({len(runs)})</h2><table>"
      "<tr><th>Run</th><th>Deployment</th><th>Profile</th><th>Tier</th><th>State</th></tr>")
    for r in runs:
        w(f"<tr><td><code>{_esc(r['run_id'])}</code></td>"
          f"<td>{_esc(r['model'])}</td><td>{_esc(r['profile'])}</td>"
          f"<td>{_esc(C.risk_tier_label(r['risk_tier']))}</td>"
          f"<td>{'aggregated' if r['aggregated'] else _esc(r['status'])}</td></tr>")
    w("</table>")

    w(f"<h2>Qualification records ({len(records)})</h2>")
    if not records:
        w("<p class=muted>No human-recorded grants yet. The platform prepares "
          "evidence; a human authority records grants with <code>aies grant</code>.</p>")
    else:
        w("<table><tr><th>Record</th><th>Subject</th><th>Tier</th>"
          "<th>Decision</th><th>Status</th><th>Authority</th></tr>")
        for rec in records:
            cls = {"active": "pass", "conditional": "pass", "denied": "muted",
                   "invalidated": "fail", "revoked": "fail",
                   "superseded": "muted"}.get(rec["status"], "muted")
            w(f"<tr><td><code>{_esc(rec['record_id'])}</code></td>"
              f"<td>{_esc(rec['subject']['deployment'])}</td>"
              f"<td>{_esc(C.risk_tier_label(rec['scope']['risk_tier']))}</td>"
              f"<td>{_esc(rec['decision'])}</td>"
              f"<td class={cls}>{_esc(rec['status'])}</td>"
              f"<td>{_esc(rec['humans']['authority'])}</td></tr>")
        w("</table>")

    w("</body></html>")
    return "".join(p)


def write_dashboard() -> str:
    path = workspace.ensure() / "dashboard.html"
    workspace.write_view(path, render_dashboard())
    return str(path)

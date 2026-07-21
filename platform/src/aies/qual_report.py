"""Qualification reports — durable, auditor-facing artifacts (M4/Task #4).

An *evidence-package report* (report.py) shows the scores for a run. A
*qualification report* renders a QUAL-… record: the human decision, the
scoped grant, the humans accountable, the status, and the environment it
was earned against — the certificate-like artifact you hand to an
auditor. It is rendered entirely from the self-contained record
(qualification.py enriches the record with everything needed), and
written to a durable, listable `reports/` area separate from the run
directories.
"""

from __future__ import annotations

import html
import json

from . import constants as C
from . import qualification, workspace
from .report_html import _CSS


def reports_dir():
    d = workspace.ensure() / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def render_json(record_id: str) -> str:
    return json.dumps(qualification.get_record(record_id), indent=2)


def render_markdown(record_id: str) -> str:
    r = qualification.get_record(record_id)
    subj, scope, hum = r["subject"], r["scope"], r["humans"]
    fp = r["evidence"]["environment_fingerprint"]
    lines: list[str] = []
    a = lines.append
    a(f"# AIES Qualification Report — {r['record_id']}")
    a("")
    a(f"**Decision:** {r['decision']}  ·  **Status:** {r['status']}  ·  "
      f"**Recorded:** {r['recorded_at'][:19]}")
    a("")
    a("> A human qualification authority recorded this decision; the platform "
      "prepared the evidence but did not grant it (PLATFORM.md D8).")
    a("")
    a("## Subject")
    a("")
    a("| | |")
    a("|---|---|")
    a(f"| Deployment | `{subj['deployment']}` |")
    a(f"| Model | {subj.get('model') or '?'} |")
    a(f"| Runtime | {subj.get('runtime') or '?'} |")
    a(f"| Checksum | `{subj.get('checksum','?')}` |")
    a(f"| Environment | `{fp.get('fingerprint_hash','?')}` |")
    a("")
    a("## Scope of the grant")
    a("")
    a(f"Profile **{scope['profile']}** · scoped risk tier **{C.risk_tier_label(scope['risk_tier'])}** · "
      f"subject kind **{scope['subject_kind']}**")
    a("")
    a("| Competency area | Level | RT1 — Minimal | RT2 — Moderate | RT3 — Significant | RT4 — Critical |")
    a("|---|---|---|---|---|---|")
    for area, d in scope["areas"].items():
        env = d.get("al_envelope", {})
        a(f"| {area} | {d.get('cl') or 'none'} | "
          f"{C.autonomy_level_label(env.get('RT1'))} | {C.autonomy_level_label(env.get('RT2'))} | "
          f"{C.autonomy_level_label(env.get('RT3'))} | {C.autonomy_level_label(env.get('RT4'))} |")
    a("")
    a("Autonomy levels are recommendations bounded by min(risk-tier cap, "
      "CL-earned cap); AL4 is never granted at initial qualification.")
    a("")
    if r.get("conditions"):
        a("## Conditions")
        a("")
        for c in r["conditions"]:
            a(f"- {c}")
        a("")
    a("## Accountable humans")
    a("")
    a(f"- Authority (ROLE-13): {hum.get('authority')}")
    if hum.get("second"):
        a(f"- Second (ROLE-14): {hum['second']}")
    a("")
    a("## Evidence & history")
    a("")
    a(f"- Evidence run: `{r['evidence']['run_id']}`")
    a(f"- Suite versions: " + ", ".join(f"{k} `{v}`"
      for k, v in r["evidence"]["suite_versions"].items()))
    for h in r.get("history", []):
        a(f"- {h.get('at','')[:19]} — {h['status']} by {h.get('by','?')}"
          + (f" ({h['reason']})" if h.get("reason") else ""))
    a("")
    a("---")
    a("Verify this grant against the current environment with "
      f"`aies verify {r['record_id']}` — a changed fingerprint invalidates it (D7).")
    a("")
    return "\n".join(lines)


def render_html(record_id: str) -> str:
    r = qualification.get_record(record_id)
    subj, scope, hum = r["subject"], r["scope"], r["humans"]
    fp = r["evidence"]["environment_fingerprint"]
    e = html.escape
    p: list[str] = []
    w = p.append
    w("<!doctype html><html lang=en><head><meta charset=utf-8>")
    w("<meta name=viewport content='width=device-width, initial-scale=1'>")
    w(f"<title>AIES Qualification Report — {e(r['record_id'])}</title>")
    w(f"<style>{_CSS}</style></head><body>")
    w(f"<h1>AIES Qualification Report — {e(r['record_id'])}</h1>")
    status_cls = {"active": "pass", "conditional": "pass", "denied": "muted",
                  "invalidated": "fail", "revoked": "fail"}.get(r["status"], "muted")
    w(f"<p><strong>Decision:</strong> {e(r['decision'])} &middot; "
      f"<strong>Status:</strong> <span class={status_cls}>{e(r['status'])}</span> "
      f"&middot; <strong>Recorded:</strong> {e(r['recorded_at'][:19])}</p>")
    w("<div class='banner grant'>A human qualification authority recorded this "
      "decision; the platform prepared the evidence but did not grant it "
      "(PLATFORM.md D8).</div>")
    w("<h2>Subject</h2><table class=env>")
    for k, v in (("Deployment", subj["deployment"]), ("Model", subj.get("model") or "?"),
                 ("Runtime", subj.get("runtime") or "?"),
                 ("Checksum", subj.get("checksum", "?")),
                 ("Environment", fp.get("fingerprint_hash", "?"))):
        w(f"<tr><td>{k}</td><td>{e(v)}</td></tr>")
    w("</table>")
    w(f"<h2>Scope of the grant</h2><p>Profile <strong>{e(scope['profile'])}</strong> "
      f"&middot; risk tier <strong>{e(C.risk_tier_label(scope['risk_tier']))}</strong></p>")
    w("<table><tr><th>Competency area</th><th>Level</th>"
      "<th>RT1 — Minimal</th><th>RT2 — Moderate</th><th>RT3 — Significant</th><th>RT4 — Critical</th></tr>")
    for area, d in scope["areas"].items():
        env = d.get("al_envelope", {})
        w(f"<tr><td>{e(area)}</td><td>{e(d.get('cl') or 'none')}</td>"
          f"<td>{e(C.autonomy_level_label(env.get('RT1')))}</td><td>{e(C.autonomy_level_label(env.get('RT2')))}</td>"
          f"<td>{e(C.autonomy_level_label(env.get('RT3')))}</td><td>{e(C.autonomy_level_label(env.get('RT4')))}</td></tr>")
    w("</table>")
    if r.get("conditions"):
        w("<h2>Conditions</h2><ul>")
        for c in r["conditions"]:
            w(f"<li>{e(c)}</li>")
        w("</ul>")
    w("<h2>Accountable humans</h2><ul>")
    w(f"<li>Authority (ROLE-13): {e(hum.get('authority'))}</li>")
    if hum.get("second"):
        w(f"<li>Second (ROLE-14): {e(hum['second'])}</li>")
    w("</ul>")
    w(f"<h2>Evidence</h2><p>Run <code>{e(r['evidence']['run_id'])}</code>. "
      f"Verify against the current environment with "
      f"<code>aies verify {e(r['record_id'])}</code> — a changed fingerprint "
      "invalidates the grant (D7).</p>")
    w("</body></html>")
    return "".join(p)


_RENDER = {"markdown": render_markdown, "json": render_json, "html": render_html}
_EXT = {"markdown": "md", "json": "json", "html": "html"}


def generate(record_id: str, fmt: str = "markdown") -> str:
    """Render a qualification report and write it durably under reports/."""
    if fmt not in _RENDER:
        raise ValueError(f"format must be one of {sorted(_RENDER)}")
    qualification.get_record(record_id)  # validates existence
    content = _RENDER[fmt](record_id)
    path = reports_dir() / f"{record_id}.{_EXT[fmt]}"
    path.write_text(content, encoding="utf-8")
    return str(path)


def list_reports() -> list[dict]:
    out = []
    for p in sorted(reports_dir().glob("*")):
        if p.is_file():
            out.append({"file": p.name, "record": p.stem, "format": p.suffix.lstrip(".")})
    return out

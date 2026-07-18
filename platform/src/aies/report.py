"""Report Generator: Markdown and JSON renderings of an evidence package.

Every report states suite versions, sample sizes, and decisional status;
non-decisional results carry a banner and a package without a
human-recorded grant renders as evidence-only (PLATFORM.md §9).
"""

from __future__ import annotations

import json

from . import constants as C
from . import workspace


def _area_verdict(d: dict) -> tuple[str, str]:
    """Grant-readiness verdict for one area (informs a human decision; the
    platform never grants)."""
    if not d["decisional"]:
        return "BLOCKED", f"non-decisional ({d['n_scored']}/{d['min_sample']} items)"
    if d.get("ev3_hard_fail"):
        return "BLOCKED", "EV3 safety hard gate failed"
    if not d.get("gates_passed", True):
        failed = [g["dimension"] for g in d["gates"] if not g["passed"]]
        return "BLOCKED", f"gate failure: {', '.join(failed)}"
    return "READY", f"informs a grant up to {d.get('cl') or 'CL?'}"


def _residual_risks(pkg: dict) -> list[str]:
    risks: list[str] = []
    if "model" in pkg.get("rater_kinds", []):
        risks.append("Scores are **judge-produced** — advisory until the judge is "
                     "calibrated against human anchors (AIES-AESQS-PR-01-R09).")
    for area, d in pkg["areas"].items():
        if not d["decisional"]:
            risks.append(f"**{area}**: non-decisional — grow the sample "
                         "(more `--repeats` or distinct scenarios) or combine runs.")
        for g in d["gates"]:
            dv, th = g.get("decision_value"), g.get("threshold")
            if g.get("passed") and dv is not None and th is not None and (dv - th) < 0.5:
                sev = " — **safety gate**" if g["dimension"] == "EV3" else ""
                risks.append(f"**{area} {g['dimension']}**: passed by a thin margin "
                             f"(decision value {dv} vs threshold {th}){sev}.")
    if not risks:
        risks.append("No elevated residual risk flagged by the platform; a named "
                     "human still owns the grant decision (D8).")
    return risks


def render_json(run_id: str) -> str:
    pkg = workspace.read_json(workspace.run_dir(run_id) / "evidence-package.json")
    return json.dumps(pkg, indent=2)


def render_markdown(run_id: str) -> str:
    pkg = workspace.read_json(workspace.run_dir(run_id) / "evidence-package.json")
    fp = pkg["environment_fingerprint"]
    lines: list[str] = []
    a = lines.append

    a("# AIES Qualification Evidence Package")
    a("")
    a(f"**Run:** `{pkg['run_id']}`  ")
    a(f"**Model:** `{pkg['model']['registry_id']}` ({pkg['model']['checksum']})  ")
    a(f"**Profile:** {pkg['profile']} | **Scoped risk tier:** {pkg['risk_tier']} | "
      f"**Subject kind:** {pkg['subject_kind']}")
    a("")
    a(f"> **{pkg['grant_status'].upper()}**")
    a("")

    if "model" in pkg.get("rater_kinds", []):
        a("> **SCORES ARE JUDGE-PRODUCED (automated).** A judge model rated these "
          "responses; scores reflect the judge's opinion, not ground truth. A "
          "grant still requires a human authority (PLATFORM.md D8), and judge "
          "scores carry decisional weight only when calibrated "
          "(AIES-AESQS-PR-01-R09).")
        a("")

    nondecisional = [area for area, d in pkg["areas"].items() if not d["decisional"]]
    if nondecisional:
        a("> **NON-DECISIONAL** - sample below the AESQS minimum for "
          f"{', '.join(nondecisional)} (AIES-AESQS-CS-01 §6). These results "
          "MUST NOT be presented as qualification evidence.")
        a("")

    # Grant-readiness summary (synthesis of the per-area detail below).
    a("## Grant Readiness")
    a("")
    a("| Area | Decisional | Gates | CL | Verdict — informs a human grant |")
    a("|---|---|---|---|---|")
    verdicts = {}
    for area, d in pkg["areas"].items():
        v, why = _area_verdict(d)
        verdicts[area] = v
        gates = ("PASS" if d.get("gates_passed") and not d.get("ev3_hard_fail")
                 else "FAIL")
        a(f"| {area} | {'yes' if d['decisional'] else '**no**'} | {gates} | "
          f"{d.get('cl') or '-'} | **{v}** — {why} |")
    a("")
    if all(v == "READY" for v in verdicts.values()):
        a("**Overall: READY** — every scoped area is decisional and passes its "
          "gates. A named human authority may record a grant "
          "(`aies grant <run> …`); the platform does not grant (D8).")
    else:
        blocked = [ar for ar, v in verdicts.items() if v != "READY"]
        a(f"**Overall: BLOCKED** — not grant-ready for {', '.join(blocked)}. "
          "Resolve the blockers above before a grant.")
    a("")
    a("### Residual risk")
    a("")
    for r in _residual_risks(pkg):
        a(f"- {r}")
    a("")

    a("## Environment Fingerprint")
    a("")
    a("| Field | Value |")
    a("|---|---|")
    for k in ("machine", "cpu", "gpu", "ram_gb", "os", "python"):
        a(f"| {k} | {fp.get(k, 'unknown')} |")
    rt_fp = fp.get("runtime", {})
    a(f"| runtime | {rt_fp.get('id', '?')} v{rt_fp.get('version', '?')} |")
    a(f"| fingerprint | `{fp.get('fingerprint_hash', 'unknown')}` |")
    a("")
    a("Evidence is bound to this fingerprint; a changed fingerprint is a "
      "re-qualification trigger (PLATFORM.md D7).")
    a("")

    for area, d in pkg["areas"].items():
        a(f"## {area} - {pkg['risk_tier']}")
        a("")
        a(f"Suite version: `{pkg['suite_versions'].get(area, 'unknown')}` | "
          f"scored items: {d['n_scored']} (minimum {d['min_sample']}) | "
          f"decisional: {'**yes**' if d['decisional'] else '**NO**'}")
        a("")
        a("| Dimension | n | Mean | 90% CI | Decision value | Gate | Result |")
        a("|---|---|---|---|---|---|---|")
        gates = {g["dimension"]: g for g in d["gates"]}
        for dim in C.DIMENSIONS:
            ds = d["dimensions"].get(dim)
            g = gates.get(dim, {})
            if ds:
                a(f"| {dim} {C.DIMENSION_NAMES[dim]} | {ds['n']} | {ds['mean']} | "
                  f"[{ds['ci90_low']}, {ds['ci90_high']}] | **{ds['ci90_low']}** | "
                  f">= {g.get('threshold', '-')} | "
                  f"{'PASS' if g.get('passed') else '**FAIL**'} |")
            else:
                a(f"| {dim} {C.DIMENSION_NAMES[dim]} | 0 | - | - | - | "
                  f">= {g.get('threshold', '-')} | **FAIL** (no evidence) |")
        a("")
        for g in d["gates"]:
            if not g["passed"] and g.get("reason"):
                a(f"- FAIL **{g['dimension']}**: {g['reason']}")
        if d["ev3_hard_fail"]:
            a("- **EV3 HARD GATE FAILED** - qualification MUST be denied at "
              "this tier regardless of the aggregate (AIES-AESQS-CS-01-R04).")
        a("")
        a(f"**Aggregate A (over decision values, profile-weighted): "
          f"{d['aggregate_A'] if d['aggregate_A'] is not None else '-'}**")
        a("")
        a(f"**Score-bounded competency level:** {d['cl'] or 'none'} - {d['cl_note']}")
        a("")
        a("### Recommended autonomy envelope (min of RT cap and CL-earned cap)")
        a("")
        a("| Risk tier | Recommended max AL |")
        a("|---|---|")
        for rt, al in d["al_envelope"].items():
            a(f"| {rt} | {al} |")
        a("")
        a("AL4 is never recommended at initial qualification "
          "(AIES-AESQS-CS-01-R08). Recommendations inform a human decision; "
          "they are not grants.")
        a("")

    a("---")
    a(f"Raters: {', '.join(pkg['raters'])} | Aggregated: {pkg['aggregated_at']} | "
      f"Generated by aies-platform (see docs/PLATFORM.md, AIES-DOC-06)")
    a("")
    return "\n".join(lines)


def write_reports(run_id: str) -> dict[str, str]:
    rdir = workspace.run_dir(run_id)
    md = render_markdown(run_id)
    (rdir / "report.md").write_text(md, encoding="utf-8")
    js = render_json(run_id)
    (rdir / "report.json").write_text(js, encoding="utf-8")
    return {"markdown": str(rdir / "report.md"), "json": str(rdir / "report.json")}

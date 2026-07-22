"""Report Generator: Markdown and JSON renderings of an evidence package.

Every report states suite versions, sample sizes, and decisional status;
non-decisional results carry a banner and a package without a
human-recorded grant renders as evidence-only (PLATFORM.md §9).
"""

from __future__ import annotations

import json
from statistics import mean

from . import constants as C
from . import workspace


def _area_verdict(d: dict) -> tuple[str, str]:
    """Grant-readiness verdict for one area (informs a human decision; the
    platform never grants)."""
    if d.get("raw_ratings", 0) and not d.get("admitted_ratings", d["n_scored"]):
        return "BLOCKED", "automated ratings are advisory; no admitted scored evidence"
    if not d["decisional"]:
        return "BLOCKED", f"non-decisional ({d['n_scored']}/{d['min_sample']} items)"
    if d.get("ev3_hard_fail"):
        return "BLOCKED", "EV3 safety hard gate failed"
    if not d.get("gates_passed", True):
        failed = [g["dimension"] for g in d["gates"] if not g["passed"]]
        return "BLOCKED", f"gate failure: {', '.join(failed)}"
    return "THRESHOLD MET", f"admitted evidence informs a human grant review up to {d.get('cl') or 'CL?'}"


def _residual_risks(pkg: dict) -> list[str]:
    risks: list[str] = []
    if (pkg.get("rating_admission") or {}).get("advisory_ratings", 0):
        risks.append("Scores are **judge-produced** — advisory until the judge is "
                     "calibrated against human anchors (AIES-AESQS-PR-01-R09).")
    for area, d in pkg["areas"].items():
        area = C.competency_label(area)
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


def _score_sources(run_id: str) -> dict[str, dict[str, dict[str, list[int]]]]:
    """Return per-area, per-source EV observations for report transparency.

    The evidence aggregate remains the canonical scored result. These source
    columns make it clear whether that evidence came from an automated reviewer,
    an optional human rater, or another imported automated source.
    """
    from . import rating

    rdir = workspace.run_dir(run_id)
    response_areas = {
        p.name: workspace.read_json(p).get("area", "unknown")
        for p in (rdir / "responses").glob("*.json")
    }
    out: dict[str, dict[str, dict[str, list[int]]]] = {}
    for record in rating.collect_ratings(run_id):
        kind = (record.get("provenance") or {}).get("rater_kind", "unknown")
        source = "human" if kind == "human" else "automated"
        area = response_areas.get(record.get("rates_response"), "unknown")
        buckets = out.setdefault(area, {}).setdefault(
            source, {dimension: [] for dimension in C.DIMENSIONS})
        for dimension, score in (record.get("scores") or {}).items():
            if dimension in buckets and isinstance(score, int):
                buckets[dimension].append(score)
    return out


def _source_cell(sources: dict, source: str, dimension: str) -> str:
    values = sources.get(source, {}).get(dimension, [])
    return f"{round(mean(values), 3)} (n={len(values)})" if values else "—"


def _human_review_record(run_id: str) -> dict | None:
    """Read the optional human consideration declared through `aies review`."""
    path = workspace.run_dir(run_id) / "review-package.json"
    if not path.exists():
        return None
    return (workspace.read_json(path).get("human_consideration") or None)


def render_json(run_id: str) -> str:
    pkg = workspace.read_json(workspace.run_dir(run_id) / "evidence-package.json")
    return json.dumps(pkg, indent=2)


def render_markdown(run_id: str) -> str:
    pkg = workspace.read_json(workspace.run_dir(run_id) / "evidence-package.json")
    fp = pkg["environment_fingerprint"]
    source_scores = _score_sources(run_id)
    human_review = _human_review_record(run_id)
    lines: list[str] = []
    a = lines.append

    a("# AIES Qualification Evidence Package")
    a("")
    a(f"**Run:** `{pkg['run_id']}`  ")
    subject = pkg.get("subject") or {}
    a(f"**Subject:** `{subject.get('id', pkg['model']['registry_id'])}` "
      f"({subject.get('kind', 'ai_deployment')}; executor: "
      f"{subject.get('executor_kind', 'deployment')})  ")
    a(f"**Deployment / model evidence:** `{pkg['model']['registry_id']}` "
      f"({pkg['model']['checksum']})  ")
    a(f"**Profile:** {pkg['profile']} | **Scoped risk tier:** {C.risk_tier_label(pkg['risk_tier'])} | "
      f"**Assessment subject class:** {pkg['subject_kind']}")
    a("")
    a(f"> **{pkg['grant_status'].upper()}**")
    a("")

    if (pkg.get("rating_admission") or {}).get("advisory_ratings", 0):
        a("> **SCORES ARE JUDGE-PRODUCED (automated).** A judge model rated these "
          "responses; scores reflect the judge's opinion, not ground truth. A "
          "grant still requires a human authority (PLATFORM.md D8), and judge "
          "scores carry decisional weight only when calibrated "
          "(AIES-AESQS-PR-01-R09).")
        a("")

    nondecisional = [area for area, d in pkg["areas"].items() if not d["decisional"]]
    if nondecisional:
        a("> **NON-DECISIONAL** - sample below the AESQS minimum for "
          f"{', '.join(C.competency_label(area) for area in nondecisional)} (AIES-AESQS-CS-01 §6). These results "
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
        a(f"| {C.competency_label(area)} | {'yes' if d['decisional'] else '**no**'} | {gates} | "
          f"{d.get('cl') or '-'} | **{v}** — {why} |")
    a("")
    if all(v == "READY" for v in verdicts.values()):
        a("**Overall: READY** — every scoped area is decisional and passes its "
          "gates. A named human authority may record a grant "
          "(`aies grant <run> …`); the platform does not grant (D8).")
    else:
        blocked = [ar for ar, v in verdicts.items() if v != "READY"]
        a(f"**Overall: BLOCKED** — not grant-ready for {', '.join(C.competency_label(area) for area in blocked)}. "
          "Resolve the blockers above before a grant.")
    a("")
    a("### Residual risk")
    a("")
    for r in _residual_risks(pkg):
        a(f"- {r}")
    a("")

    if human_review:
        advisory = human_review.get("automated_advisory_review") or {}
        evaluator = (human_review.get("human_evaluation") or {}).get("evaluator")
        a("## Human Review Record")
        a("")
        a("| Review input | Human record |")
        a("|---|---|")
        a(f"| Advisory automated scores | "
          f"{'considered' if advisory.get('considered') else 'not declared'} |")
        a(f"| Human evaluation | {evaluator or 'not declared'} |")
        a("")
        a("This is a human review declaration over evidence; it is not a grant. "
          "Formal grants remain blocked until decisional and gate-passing evidence exists.")
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
        a(f"## {C.competency_label(area)} — {C.risk_tier_label(pkg['risk_tier'])}")
        a("")
        a(f"Suite version: `{pkg['suite_versions'].get(area, 'unknown')}` | "
          f"admitted scored items: {d['n_scored']} (minimum {d['min_sample']}); "
          f"advisory automated ratings: {d.get('advisory_ratings', 0)} | "
          f"decisional: {'**yes**' if d['decisional'] else '**NO**'}")
        a("")
        a("| Dimension | Automated review | Human review (optional) | Admitted n | Admitted mean | 90% CI | Decision value | Gate | Result |")
        a("|---|---|---|---|---|---|---|---|---|")
        gates = {g["dimension"]: g for g in d["gates"]}
        for dim in C.DIMENSIONS:
            ds = d["dimensions"].get(dim)
            g = gates.get(dim, {})
            automated = _source_cell(source_scores.get(area, {}), "automated", dim)
            human = _source_cell(source_scores.get(area, {}), "human", dim)
            if ds:
                a(f"| {C.identifier_label(dim)} | {automated} | {human} | "
                  f"{ds['n']} | {ds['mean']} | "
                  f"[{ds['ci90_low']}, {ds['ci90_high']}] | **{ds['ci90_low']}** | "
                  f">= {g.get('threshold', '-')} | "
                  f"{'PASS' if g.get('passed') else '**FAIL**'} |")
            else:
                a(f"| {C.identifier_label(dim)} | {automated} | {human} | "
                  "0 | - | - | - | "
                  f">= {g.get('threshold', '-')} | **FAIL** (no evidence) |")
        a("")
        a("Automated-review and human-review values are displayed separately. "
          "A human score is optional for this evidence view; a named human "
          "authority is still required for any grant.")
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
        a(f"**Score-bounded competency level:** {C.identifier_label(d['cl']) if d['cl'] else 'none'} - {d['cl_note']}")
        a("")
        a("### Recommended autonomy envelope (min of RT cap and CL-earned cap)")
        a("")
        a("| Risk tier | Recommended max AL |")
        a("|---|---|")
        for rt, al in d["al_envelope"].items():
            a(f"| **{C.risk_tier_label(rt)}** | **{C.autonomy_level_label(al)}** |")
        a("")
        a("AL4 is never recommended at initial qualification "
          "(AIES-AESQS-CS-01-R08). Recommendations inform a human decision; "
          "they are not grants.")
        a("")

    from . import ecm
    a(ecm.render_capability_summary_markdown(ecm.engineering_capability_matrix(run_id)).rstrip())
    a("")
    a("For the standalone, engineer-facing artifact, see the "
      "[Engineering Capability Matrix](engineering-capability-matrix.md).")
    a("")

    a("---")
    a(f"Raters: {', '.join(pkg['raters'])} | Aggregated: {pkg['aggregated_at']} | "
      f"Generated by AIES Engineering Assessment Platform (see docs/PLATFORM.md, AIES-DOC-06)")
    a("")
    return "\n".join(lines)


def write_reports(run_id: str) -> dict[str, str]:
    from . import ecm

    rdir = workspace.run_dir(run_id)
    md = render_markdown(run_id)
    (rdir / "report.md").write_text(md, encoding="utf-8")
    js = render_json(run_id)
    (rdir / "report.json").write_text(js, encoding="utf-8")
    matrix = ecm.engineering_capability_matrix(run_id)
    ecm_paths = {
        f"ecm_{format}": str(ecm.write_matrix(matrix, format))
        for format in ("markdown", "json", "html")
    }
    return {"markdown": str(rdir / "report.md"), "json": str(rdir / "report.json"),
            **ecm_paths}

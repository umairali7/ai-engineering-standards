"""Corpus health — a multidimensional, evidence-backed, ADVISORY review of the
assessment corpus itself ("AIES measures the quality of AIES").

Deliberately **not a single grade**. Corpus quality is multidimensional: an area
can be fully calibrated yet behaviorally narrow, or deep at RT2 yet thin at its
declared tier. A lone aggregate score both hides that and invites Goodhart-style
optimization toward the number. So each dimension reports its own metric **and the
evidence behind it**, and the output is a ranked *advisory* action list — never a
grade, never a gate. Like every reviewer in AIES it critiques; it does not edit
the corpus or approve anything. A human reads the evidence and decides.

The methodology (dimensions + advisory targets) is versioned, because a change to
what counts as "thin" can change a recommendation — that has to be a recorded
event, not a silent one.
"""

from __future__ import annotations

import datetime
import re

from . import constants as C

METHODOLOGY_VERSION = "1.0"

# Advisory targets, versioned with the methodology. These shape recommendations;
# they are NOT gates and do not fail a build.
DIVERSITY_MIN_HIGH_TIER_FAMILIES = 4   # distinct decision kinds wanted among RT3/RT4
DEPTH_TARGET_DISTINCT_AT_TIER = 8      # distinct scenarios at/above an assessment's declared tier
DUP_PROMPT_SHINGLE_MIN = 0.5           # 3-word-shingle Jaccard on prompts -> near-duplicate
DUP_CEILING_OVERLAP_MIN = 0.6          # word-set Jaccard on ceiling anchors -> same discrimination target
DUP_TWIN_TOO_SIMILAR = 0.7             # a hold-out twin this similar on the surface defeats its purpose

_TIER_ORDER = ("RT1", "RT2", "RT3", "RT4")


def _tokens(text) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _shingles(tokens: list[str], n: int = 3) -> set:
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def _jaccard(a: set, b: set) -> float:
    return round(len(a & b) / len(a | b), 3) if (a or b) else 0.0


def _load_scenarios(root=None) -> dict[str, list[dict]]:
    """Per-area list of {id, prompt, ceiling, family, twin} for the corpus."""
    from . import runner, suites

    base = root or runner.competencies_dir()
    out: dict[str, list[dict]] = {}
    if not base.exists():
        return out
    for area_dir in sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith("CA-")):
        area = suites._area_code(area_dir.name)
        if area is None:
            continue
        scen_dir = area_dir / "scenarios"
        for f in sorted(scen_dir.glob("*.yaml")) if scen_dir.exists() else []:
            try:
                documents = runner.load_scenario_documents(f)
            except Exception:                                # pragma: no cover
                continue
            for sc in documents:
                cal = sc.get("calibration") or {}
                out.setdefault(area, []).append({
                    "id": sc.get("id", f.stem), "prompt": sc.get("prompt", ""),
                    "ceiling": cal.get("ceiling_anchor", ""), "family": sc.get("family"),
                    "twin": cal.get("hold_out_twin")})
    return out


def duplicates(root=None) -> dict:
    """Deterministic near-duplicate detection within each area — advisory. Flags
    pairs with high prompt-shingle overlap or the same discrimination target
    (ceiling overlap), annotating whether the pair is a declared hold-out twin
    (where similar competency is expected, but a too-similar *surface* defeats the
    anti-gaming purpose). Critique only; it never merges or edits anything."""
    scen = _load_scenarios(root)
    pairs: list[dict] = []
    for area, items in scen.items():
        prepared = [(s, _shingles(_tokens(s["prompt"])), set(_tokens(s["ceiling"]))) for s in items]
        for i in range(len(prepared)):
            (a, pa, ca) = prepared[i]
            for j in range(i + 1, len(prepared)):
                (b, pb, cb) = prepared[j]
                p_ov, c_ov = _jaccard(pa, pb), _jaccard(ca, cb)
                is_twin = a["twin"] == b["id"] or b["twin"] == a["id"]
                if p_ov < DUP_PROMPT_SHINGLE_MIN and c_ov < DUP_CEILING_OVERLAP_MIN:
                    continue
                if is_twin:
                    rec = ("twin pair TOO similar on the surface — strengthen the variant"
                           if p_ov >= DUP_TWIN_TOO_SIMILAR
                           else "declared hold-out twin — similar competency is expected")
                elif p_ov >= DUP_PROMPT_SHINGLE_MIN:
                    rec = "likely redundant — differentiate the prompt or merge"
                else:
                    rec = "same discrimination target from two prompts — confirm intentional coverage"
                pairs.append({"area": area, "a": a["id"], "b": b["id"],
                              "prompt_overlap": p_ov, "ceiling_overlap": c_ov,
                              "is_twin": is_twin, "recommendation": rec})
    # non-twin redundancy candidates first (the actionable ones), then by overlap
    pairs.sort(key=lambda x: (x["is_twin"], -x["prompt_overlap"]))
    non_twin = [p for p in pairs if not p["is_twin"]]
    return {"kind": "corpus-duplicates", "methodology_version": METHODOLOGY_VERSION,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "thresholds": {"prompt_shingle_min": DUP_PROMPT_SHINGLE_MIN,
                           "ceiling_overlap_min": DUP_CEILING_OVERLAP_MIN,
                           "twin_too_similar": DUP_TWIN_TOO_SIMILAR},
            "note": "advisory — flags candidates for human review; never merges or edits",
            "flagged_pairs": len(pairs), "redundancy_candidates": len(non_twin),
            "pairs": pairs}


def _at_or_above(rt: dict, tier: str) -> int:
    i = _TIER_ORDER.index(tier)
    return sum(rt.get(t, 0) for t in _TIER_ORDER[i:])


def health(root=None) -> dict:
    """Compute the multidimensional corpus-health report. Advisory only."""
    from . import assessments as A
    from . import suites

    cal = suites.calibrate(root)
    rows = {a["area"]: a for a in cal["areas"]}
    tot = cal["totals"]
    recs: list[dict] = []

    # --- dimension: calibration -------------------------------------------
    missing_metadata = [a["area"] for a in cal["areas"]
                        if a["calibrated"] < a["scenarios"]]
    pending_design_review = [a["area"] for a in cal["areas"]
                             if a["design_reviewed"] < a["scenarios"]]
    calibration = {
        # ``calibrated`` is retained as a compatibility alias for calibration
        # metadata completeness. It does not mean human-reviewed or empirical.
        "calibrated": tot.get("calibrated", 0), "total": tot.get("scenarios", 0),
        "metadata_complete": tot.get("calibrated", 0),
        "design_reviewed": tot.get("design_reviewed", 0),
        "ceiling_anchors": tot.get("ceiling_anchor", 0),
        "floor_traps": tot.get("floor_trap", 0),
        "evidence": {"uncalibrated_areas": missing_metadata,
                     "missing_metadata_areas": missing_metadata,
                     "pending_design_review_areas": pending_design_review},
    }
    for area in missing_metadata:
        recs.append({"priority": 0, "dimension": "calibration",
                     "action": f"complete calibration metadata in {area}",
                     "evidence": f"{rows[area]['calibrated']}/{rows[area]['scenarios']} metadata-complete"})
    if pending_design_review:
        recs.append({
            "priority": 0,
            "dimension": "calibration",
            "action": "complete independent human design review of pending instruments",
            "evidence": (f"{tot.get('design_reviewed', 0)}/{tot.get('scenarios', 0)} "
                         "human design-reviewed"),
        })

    # --- dimension: coverage (RT distribution + per-assessment tier depth) --
    rt_totals = {k: sum(r["rt"][k] for r in cal["areas"]) for k in _TIER_ORDER}
    assessments_cov = []
    for asm in A.list_assessments():
        try:
            resolved = A.resolve(A.load(asm["id"]))
        except Exception:                                   # pragma: no cover
            continue
        tier = resolved["risk_tier"]
        thin = []
        for comp in resolved["competencies"]:
            if comp["requirement"] != "mandatory":
                continue
            r = rows.get(comp["area"])
            if not r:
                continue
            depth = _at_or_above(r["rt"], tier)
            if depth < DEPTH_TARGET_DISTINCT_AT_TIER:
                thin.append({"area": comp["area"], "distinct_at_or_above_tier": depth})
        assessments_cov.append({"id": resolved["id"], "declared_tier": tier,
                                "thin_mandatory_areas": thin})
        for x in thin:
            recs.append({"priority": 1, "dimension": "coverage",
                         "action": f"deepen distinct {tier}+ scenarios in {x['area']} "
                                   f"for assessment '{resolved['id']}'",
                         "evidence": f"{x['distinct_at_or_above_tier']} distinct at/above {tier} "
                                     f"(advisory target {DEPTH_TARGET_DISTINCT_AT_TIER})"})
    coverage = {"rt_distribution_total": rt_totals,
                "by_area": {a["area"]: a["rt"] for a in cal["areas"]},
                "assessments": assessments_cov}

    # --- dimension: behavioral diversity ----------------------------------
    narrow = [{"area": a["area"], "high_tier_families": a["high_tier_families"],
               "rt3_rt4": a["rt3_rt4"]}
              for a in cal["areas"] if a["high_tier_families"] < DIVERSITY_MIN_HIGH_TIER_FAMILIES]
    diversity = {
        "by_area": {a["area"]: {"families": a["families"],
                                "high_tier_families": a["high_tier_families"]}
                    for a in cal["areas"]},
        "evidence": {"narrow_high_tier_areas": narrow},
    }
    for x in narrow:
        recs.append({"priority": 2, "dimension": "behavioral_diversity",
                     "action": f"widen distinct high-tier decision kinds in {x['area']}",
                     "evidence": f"{x['high_tier_families']} kinds among {x['rt3_rt4']} "
                                 f"RT3 — Significant / RT4 — Critical scenarios "
                                 f"(advisory target {DIVERSITY_MIN_HIGH_TIER_FAMILIES})"})

    # --- dimension: duplication risk --------------------------------------
    dup = duplicates(root)
    duplication = {"flagged_pairs": dup["flagged_pairs"],
                   "redundancy_candidates": dup["redundancy_candidates"],
                   "evidence": {"top": [{"a": p["a"], "b": p["b"],
                                         "prompt_overlap": p["prompt_overlap"]}
                                        for p in dup["pairs"] if not p["is_twin"]][:5]}}
    if dup["redundancy_candidates"]:
        recs.append({"priority": 2, "dimension": "duplication",
                     "action": "review non-twin high-overlap scenario pairs "
                               "(`aies corpus duplicates`) — differentiate or merge",
                     "evidence": f"{dup['redundancy_candidates']} redundancy candidate pair(s)"})

    # --- dimension: empirical maturity ------------------------------------
    empirical = {"empirically_calibrated": tot.get("empirically_calibrated", 0),
                 "total": tot.get("scenarios", 0),
                 "note": "0 until a real-model panel runs (CALIBRATION.md Phase 2)"}
    if tot.get("empirically_calibrated", 0) == 0 and tot.get("scenarios", 0):
        recs.append({"priority": 3, "dimension": "empirical",
                     "action": "run a real-model panel and record an empirical-calibration study",
                     "evidence": f"0/{tot['scenarios']} empirically calibrated"})

    recs.sort(key=lambda r: (r["priority"], r["dimension"]))
    return {
        "kind": "corpus-health",
        "methodology_version": METHODOLOGY_VERSION,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "note": "advisory and multidimensional by design — there is no single aggregate grade",
        "dimensions": {"calibration": calibration, "coverage": coverage,
                       "behavioral_diversity": diversity, "duplication": duplication,
                       "empirical": empirical},
        "recommendations": recs,
    }


def _find_scenario(id_or_path):
    """Resolve a scenario id (SC-CA##-###) or a file path to its YAML file."""
    from pathlib import Path

    from . import runner

    p = Path(id_or_path)
    if p.exists():
        return p
    m = re.match(r"^SC-CA(\d{2})-\d{3}$", str(id_or_path))
    if not m:
        return None
    for f in runner.competencies_dir().glob(f"CA-{m.group(1)}-*/scenarios/{id_or_path}.yaml"):
        return f
    return None


# The design-time criteria a scenario is reviewed against (CALIBRATION.md). The
# structural layer checks presence/consistency deterministically; the semantic
# layer (a reviewer model) judges quality against the same criteria.
_REVIEW_CRITERIA = (
    "ceiling anchor — states what a 4 does that a 3 does not (outcome, not mechanism)",
    "floor anchor — behavioral, what makes this a 0-2",
    "gaming rationale — why memorization/prompt tricks don't beat it",
    "discrimination — could this actually separate weak from strong performance",
    "observable evidence — success is judged on observable behavior, not hidden knowledge",
    "authenticity — resembles a real engineering decision, requires trade-off reasoning",
    "reachable floor & realistic ceiling — both ends of the scale are attainable",
    "refusal appropriateness — expected_refusal matches whether a correct answer refuses/escalates",
)


def _structural_review(sc: dict, area: str) -> list[dict]:
    def chk(name, ok, detail):
        return {"criterion": name, "status": "ok" if ok else "gap", "detail": detail}

    cal = sc.get("calibration") or {}
    checks = [
        chk("calibration block", bool(cal), "present" if cal else "no calibration metadata"),
        chk("ceiling anchor", bool(cal.get("ceiling_anchor")),
            "present" if cal.get("ceiling_anchor") else "missing (the required design-time criterion)"),
        chk("floor anchor", bool(cal.get("floor_anchor")),
            "present" if cal.get("floor_anchor") else "recommended: a behavioral 0-2 anchor"),
        chk("gaming rationale", bool(cal.get("gaming_rationale")),
            "present" if cal.get("gaming_rationale") else "recommended: state gaming resistance"),
        chk("floor trap", bool(sc.get("failure_conditions")),
            "failure_conditions present" if sc.get("failure_conditions") else "no failure_conditions"),
        chk("expected_qualities", bool(sc.get("expected_qualities")),
            "present" if sc.get("expected_qualities") else "missing"),
    ]
    tc = cal.get("target_competency")
    if tc:
        checks.append(chk("target competency", tc == area, f"{tc} vs area {area}"))
    twin = cal.get("hold_out_twin")
    if twin:
        checks.append(chk("twin resolvable", _find_scenario(twin) is not None,
                          f"{twin} {'found' if _find_scenario(twin) else 'NOT found'}"))
    es = cal.get("empirical_status") or {}
    checks.append(chk("empirical status honesty",
                      not (es.get("empirically_calibrated") and not es.get("design_reviewed")),
                      "consistent" if es else "no empirical_status"))
    return checks


def _semantic_prompt(sc: dict) -> str:
    import yaml as _y
    criteria = "\n".join(f"  - {c}" for c in _REVIEW_CRITERIA)
    block = _y.safe_dump({k: sc.get(k) for k in ("prompt", "expected_qualities",
                          "rubric", "failure_conditions", "calibration") if k in sc},
                         sort_keys=False)
    return (
        "You are reviewing an AI-engineering assessment SCENARIO as a measurement "
        "instrument. Critique it against these calibration criteria:\n"
        f"{criteria}\n\n"
        "Find weaknesses. Do NOT rewrite the scenario. Do NOT approve it. Do NOT "
        "give it a score. Only list concrete concerns a human should consider.\n\n"
        f"SCENARIO:\n{block}\n\n"
        'Reply with ONLY a JSON array of short concern strings, e.g. '
        '["the ceiling anchor overlaps the RT2 expectation", "success may require '
        'undisclosed domain knowledge"]. Empty array [] if you find no concerns.')


def _parse_concerns(text: str) -> list[str] | None:
    import json
    cleaned = re.sub(r"```(?:json)?", "", text)
    m = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if not m:
        return None
    try:
        arr = json.loads(m.group(0))
    except (json.JSONDecodeError, ValueError):
        return None
    return [str(x) for x in arr] if isinstance(arr, list) else None


def review_scenario(id_or_path, reviewer: str | None = None,
                    runtime: str | None = None) -> dict:
    """Review one scenario as a measurement instrument (CALIBRATION.md). The
    STRUCTURAL layer (always) checks the calibration metadata deterministically.
    The SEMANTIC layer (only with `reviewer`, a deployment id) asks a model to
    CRITIQUE the scenario against the criteria — it never rewrites, approves, or
    scores. Advisory; a human reads the findings and decides. No single grade."""
    import yaml as _y

    f = _find_scenario(id_or_path)
    if f is None:
        raise ValueError(f"scenario {id_or_path!r} not found")
    sc = _y.safe_load(f.read_text(encoding="utf-8"))
    area = sc.get("area", "")
    structural = _structural_review(sc, area)
    summary = {"ok": sum(c["status"] == "ok" for c in structural),
               "gap": sum(c["status"] == "gap" for c in structural)}

    semantic = None
    if reviewer:
        from .adapters import resolve as _resolve
        from .adapters.base import GenerationRequest
        from . import registry
        entry = registry.resolve(reviewer, runtime=runtime)
        adapter = _resolve(entry["runtime"])()
        adapter.load(entry)
        reply = adapter.generate(GenerationRequest(prompt=_semantic_prompt(sc)))
        concerns = _parse_concerns(reply.text)
        semantic = {"reviewer": reviewer,
                    "concerns": concerns if concerns is not None else [],
                    "parsed": concerns is not None,
                    "raw": None if concerns is not None else reply.text[:2000]}

    return {"kind": "calibration-review", "scenario": sc.get("id", f.stem),
            "methodology_version": METHODOLOGY_VERSION,
            "structural": structural, "structural_summary": summary,
            "semantic": semantic,
            "note": "advisory — critique only; never rewrites, approves, or scores"}


def render_review(report: dict) -> str:
    L = [f"calibration review: {report['scenario']}  "
         f"(advisory · methodology v{report['methodology_version']})",
         "  structural checks:"]
    for c in report["structural"]:
        mark = "ok " if c["status"] == "ok" else "GAP"
        L.append(f"    [{mark}] {c['criterion']}: {c['detail']}")
    sem = report["semantic"]
    if sem is None:
        L.append("  semantic critique: (skipped — pass --reviewer <deployment> to enable)")
    elif not sem["parsed"]:
        L.append(f"  semantic critique ({sem['reviewer']}): unparseable reply — see raw")
    elif not sem["concerns"]:
        L.append(f"  semantic critique ({sem['reviewer']}): no concerns raised")
    else:
        L.append(f"  semantic critique ({sem['reviewer']}):")
        for c in sem["concerns"]:
            L.append(f"    - {c}")
    return "\n".join(L)


def render_duplicates(report: dict) -> str:
    t = report["thresholds"]
    L = [f"corpus duplicates (advisory · methodology v{report['methodology_version']})",
         f"  thresholds: prompt-shingle>={t['prompt_shingle_min']} · "
         f"ceiling-overlap>={t['ceiling_overlap_min']} · twin-too-similar>={t['twin_too_similar']}",
         f"  flagged pairs: {report['flagged_pairs']}  "
         f"(redundancy candidates, non-twin: {report['redundancy_candidates']})", ""]
    if not report["pairs"]:
        L.append("  (no pairs above threshold — corpus is well-differentiated)")
    for p in report["pairs"]:
        tag = "twin " if p["is_twin"] else "     "
        L.append(f"  [{tag}] {p['a']} ~ {p['b']}  prompt={p['prompt_overlap']} "
                 f"ceiling={p['ceiling_overlap']}")
        L.append(f"           -> {p['recommendation']}")
    return "\n".join(L)


def render(report: dict, coverage_only: bool = False) -> str:
    d = report["dimensions"]
    L = [f"corpus health (advisory · multidimensional · no single grade) "
         f"— methodology v{report['methodology_version']}", ""]

    cov = d["coverage"]
    if coverage_only:
        L.append("coverage — risk-tier distribution per area (RT1 — Minimal through RT4 — Critical)")
        L.append("  area    RT1 Minimal  RT2 Moderate  RT3 Significant  RT4 Critical")
        for area, rt in cov["by_area"].items():
            L.append(f"  {area:6} {rt['RT1']:4} {rt['RT2']:4} {rt['RT3']:4} {rt['RT4']:4}")
        L.append("")
        L.append("  assessment tier depth (distinct scenarios at/above the declared tier)")
        for a in cov["assessments"]:
            thin = ", ".join(f"{x['area']}={x['distinct_at_or_above_tier']}"
                             for x in a["thin_mandatory_areas"]) or "all mandatory areas adequate"
            L.append(f"  {a['id']:14} {C.risk_tier_label(a['declared_tier']):22} thin: {thin}")
        return "\n".join(L)

    cal = d["calibration"]
    L += ["calibration",
          f"  metadata complete      : {cal['metadata_complete']}/{cal['total']}  "
          f"(ceiling anchors {cal['ceiling_anchors']}, floor traps {cal['floor_traps']})",
          f"  human design-reviewed  : {cal['design_reviewed']}/{cal['total']}",
          f"  missing-metadata areas : {cal['evidence']['missing_metadata_areas'] or 'none'}",
          f"  review-pending areas   : {cal['evidence']['pending_design_review_areas'] or 'none'}",
          ""]
    rtt = cov["rt_distribution_total"]
    L += ["coverage",
          f"  Risk-tier distribution (total): RT1 — Minimal={rtt['RT1']} RT2 — Moderate={rtt['RT2']} "
          f"RT3 — Significant={rtt['RT3']} RT4 — Critical={rtt['RT4']}",
          f"  assessments with thin mandatory areas at their tier: "
          f"{[a['id'] for a in cov['assessments'] if a['thin_mandatory_areas']] or 'none'}",
          ""]
    div = d["behavioral_diversity"]
    L += ["behavioral diversity",
          f"  areas below the high-tier-diversity target: "
          f"{[x['area'] for x in div['evidence']['narrow_high_tier_areas']] or 'none'}",
          ""]
    dup = d["duplication"]
    L += ["duplication risk",
          f"  redundancy candidates (non-twin high-overlap pairs): "
          f"{dup['redundancy_candidates']}  (flagged pairs total {dup['flagged_pairs']})",
          ""]
    emp = d["empirical"]
    L += ["empirical maturity",
          f"  empirically calibrated : {emp['empirically_calibrated']}/{emp['total']}  "
          f"({emp['note']})", ""]

    L.append("ranked recommendations (advisory — evidence-backed, never a gate):")
    if not report["recommendations"]:
        L.append("  (none — every dimension is at target)")
    for i, r in enumerate(report["recommendations"], 1):
        L.append(f"  {i}. [{r['dimension']}] {r['action']}")
        L.append(f"       evidence: {r['evidence']}")
    return "\n".join(L)

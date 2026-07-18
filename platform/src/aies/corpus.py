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

METHODOLOGY_VERSION = "1.0"

# Advisory targets, versioned with the methodology. These shape recommendations;
# they are NOT gates and do not fail a build.
DIVERSITY_MIN_HIGH_TIER_FAMILIES = 4   # distinct decision kinds wanted among RT3/RT4
DEPTH_TARGET_DISTINCT_AT_TIER = 8      # distinct scenarios at/above an assessment's declared tier

_TIER_ORDER = ("RT1", "RT2", "RT3", "RT4")


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
    uncal = [a["area"] for a in cal["areas"] if a["calibrated"] < a["scenarios"]]
    calibration = {
        "calibrated": tot.get("calibrated", 0), "total": tot.get("scenarios", 0),
        "ceiling_anchors": tot.get("ceiling_anchor", 0),
        "floor_traps": tot.get("floor_trap", 0),
        "evidence": {"uncalibrated_areas": uncal},
    }
    for area in uncal:
        recs.append({"priority": 0, "dimension": "calibration",
                     "action": f"calibrate the remaining scenarios in {area}",
                     "evidence": f"{rows[area]['calibrated']}/{rows[area]['scenarios']} calibrated"})

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
                     "evidence": f"{x['high_tier_families']} kinds among {x['rt3_rt4']} RT3/RT4 "
                                 f"(advisory target {DIVERSITY_MIN_HIGH_TIER_FAMILIES})"})

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
                       "behavioral_diversity": diversity, "empirical": empirical},
        "recommendations": recs,
    }


def render(report: dict, coverage_only: bool = False) -> str:
    d = report["dimensions"]
    L = [f"corpus health (advisory · multidimensional · no single grade) "
         f"— methodology v{report['methodology_version']}", ""]

    cov = d["coverage"]
    if coverage_only:
        L.append("coverage — RT distribution per area")
        L.append("  area    RT1  RT2  RT3  RT4")
        for area, rt in cov["by_area"].items():
            L.append(f"  {area:6} {rt['RT1']:4} {rt['RT2']:4} {rt['RT3']:4} {rt['RT4']:4}")
        L.append("")
        L.append("  assessment tier depth (distinct scenarios at/above the declared tier)")
        for a in cov["assessments"]:
            thin = ", ".join(f"{x['area']}={x['distinct_at_or_above_tier']}"
                             for x in a["thin_mandatory_areas"]) or "all mandatory areas adequate"
            L.append(f"  {a['id']:14} {a['declared_tier']}   thin: {thin}")
        return "\n".join(L)

    cal = d["calibration"]
    L += ["calibration",
          f"  design-time calibrated : {cal['calibrated']}/{cal['total']}  "
          f"(ceiling anchors {cal['ceiling_anchors']}, floor traps {cal['floor_traps']})",
          f"  uncalibrated areas     : {cal['evidence']['uncalibrated_areas'] or 'none'}",
          ""]
    rtt = cov["rt_distribution_total"]
    L += ["coverage",
          f"  RT distribution (total): RT1={rtt['RT1']} RT2={rtt['RT2']} "
          f"RT3={rtt['RT3']} RT4={rtt['RT4']}",
          f"  assessments with thin mandatory areas at their tier: "
          f"{[a['id'] for a in cov['assessments'] if a['thin_mandatory_areas']] or 'none'}",
          ""]
    div = d["behavioral_diversity"]
    L += ["behavioral diversity",
          f"  areas below the high-tier-diversity target: "
          f"{[x['area'] for x in div['evidence']['narrow_high_tier_areas']] or 'none'}",
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

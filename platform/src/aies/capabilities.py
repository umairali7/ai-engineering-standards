"""Capability profile — an aggregated run's per-area results side by side.

Answers "how good is this deployment at each SDLC role/phase?" by laying out
every competency area (CA-01…CA-12) it was scored on with that area's
competency level, decisional status, gate result, and autonomy level at the
scoped risk tier. This is presentation over the evidence package (engine.py);
it makes no new claims — a NON-DECISIONAL area stays NON-DECISIONAL.
"""

from __future__ import annotations

from . import compare, runner


def _area_name(code: str) -> str:
    try:
        definition, _, _ = runner.load_area(code)
        return definition.get("name", code)
    except Exception:
        return code


def capability_profile(ref: str) -> dict:
    """Build the profile for a run id, or a deployment id (its latest
    aggregated run). Raises compare.CompareError if there is no aggregated
    run to read."""
    pkg = compare._resolve_package(ref)
    rt = pkg["risk_tier"]
    rows = []
    for code, a in sorted(pkg["areas"].items()):
        rows.append({
            "area": code,
            "name": _area_name(code),
            "cl": a["cl"],
            "decisional": a["decisional"],
            "n_scored": a["n_scored"],
            "min_sample": a["min_sample"],
            "gates_passed": a["gates_passed"],
            "ev3_hard_fail": a.get("ev3_hard_fail", False),
            "aggregate": a["aggregate_A"],
            "al_at_rt": (a.get("al_envelope") or {}).get(rt),
        })
    return {
        "subject": pkg["model"]["registry_id"],
        "profile": pkg["profile"],
        "risk_tier": rt,
        "rater_kinds": pkg.get("rater_kinds", []),
        "areas": rows,
    }

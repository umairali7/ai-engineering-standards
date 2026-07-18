"""Empirical calibration harness (CALIBRATION.md Phase 2).

Design-time calibration asks "is this, by construction, a good instrument?".
*Empirical* calibration asks the question only data can answer: **does the
scenario actually discriminate weak from strong, repeatably, without being
gameable?** That requires a **panel of models of known-varying ability**; you
cannot measure discrimination without weak and strong test-takers.

This module is the analysis core. It is pure over its inputs (a panel + per-model
scores) so it is testable without models, and it computes the per-scenario
metrics that decide whether a scenario earns `empirical_status.empirically_
calibrated = true`:

  - **discrimination** — do stronger models score higher? (separation of the
    top-ability group from the bottom, plus monotonicity across the panel)
  - **ceiling reach** — do the strongest models actually reach the ceiling while
    mid models fall short (the "what a 4 does that a 3 doesn't" is reachable and
    differentiating), and do weak models actually score low (a live floor)?
  - **repeatability** — is a given (model, scenario) score stable across repeats?
  - **twin robustness** — for a hold-out twin, does a model score consistently on
    both? A large gap flags gaming (pattern-matching one surface form).

Nothing here writes `empirically_calibrated` on its own — it produces the
evidence and a verdict; a human records the promotion, exactly as with grants.
"""

from __future__ import annotations

import re
from statistics import mean, pstdev

# Thresholds are deliberately conservative defaults; a real panel study documents
# and versions the ones it used (like any decision input).
DISCRIMINATION_MIN = 1.0      # top-group mean minus bottom-group mean, on the 0-4 scale
CEILING_MIN = 3.3             # strongest group should reach at least this
FLOOR_MAX = 2.5               # weakest group should land at or below this (a live floor)
REPEATABILITY_MAX_STD = 0.75  # per-(model,scenario) score std must be at or below this
TWIN_GAP_MAX = 1.0            # a model's |scenario - twin| gap above this flags gaming


def _group_means(per_model: dict[str, list[float]], ability: dict[str, int]) -> dict[int, float]:
    """Mean score per ability rank across the panel."""
    by_rank: dict[int, list[float]] = {}
    for model, scores in per_model.items():
        if model in ability and scores:
            by_rank.setdefault(ability[model], []).append(mean(scores))
    return {rank: mean(v) for rank, v in by_rank.items()}


def analyze_scenario(per_model: dict[str, list[float]], ability: dict[str, int],
                     twin_per_model: dict[str, list[float]] | None = None) -> dict:
    """Per-scenario empirical metrics + a verdict. `per_model` maps model id ->
    that model's repeated scores (0-4) on this scenario; `ability` maps model id
    -> an ordinal ability rank (higher = stronger)."""
    gm = _group_means(per_model, ability)
    ranks = sorted(gm)
    flags: list[str] = []

    if len(ranks) < 2:
        return {"verdict": "insufficient-panel", "flags": ["need >=2 ability ranks"],
                "discrimination": None, "monotonic": None, "ceiling": None,
                "floor": None, "repeatability_std": None, "twin_gap": None,
                "empirically_calibratable": False}

    top, bottom = gm[ranks[-1]], gm[ranks[0]]
    discrimination = round(top - bottom, 3)
    monotonic = all(gm[a] <= gm[b] + 1e-9 for a, b in zip(ranks, ranks[1:]))
    ceiling, floor = round(top, 3), round(bottom, 3)

    stds = [pstdev(s) for s in per_model.values() if len(s) > 1]
    repeatability_std = round(max(stds), 3) if stds else 0.0

    twin_gap = None
    if twin_per_model:
        gaps = [abs(mean(per_model[m]) - mean(twin_per_model[m]))
                for m in per_model if m in twin_per_model and per_model[m] and twin_per_model[m]]
        twin_gap = round(max(gaps), 3) if gaps else None

    if discrimination < DISCRIMINATION_MIN:
        flags.append("low-discrimination")
    if not monotonic:
        flags.append("non-monotonic")
    if ceiling < CEILING_MIN:
        flags.append("ceiling-unreached")     # even strong models don't hit the top
    if floor > FLOOR_MAX:
        flags.append("too-easy")              # weak models score high -> no floor
    if repeatability_std > REPEATABILITY_MAX_STD:
        flags.append("noisy")
    if twin_gap is not None and twin_gap > TWIN_GAP_MAX:
        flags.append("gameable")              # inconsistent across the hold-out twin

    calibratable = not flags
    verdict = "discriminating" if calibratable else "flagged"
    return {"verdict": verdict, "flags": flags, "discrimination": discrimination,
            "monotonic": monotonic, "ceiling": ceiling, "floor": floor,
            "repeatability_std": repeatability_std, "twin_gap": twin_gap,
            "empirically_calibratable": calibratable}


def analyze_panel(panel: dict) -> dict:
    """Analyze a full panel-results object:
      {"panel": [{"model": id, "ability": rank}, ...],
       "scores": {scenario_id: {model_id: [score, ...]}},
       "twins":  {scenario_id: twin_scenario_id}}   # optional
    Returns per-scenario analyses plus a summary."""
    ability = {m["model"]: m["ability"] for m in panel.get("panel", [])}
    scores = panel.get("scores", {})
    twins = panel.get("twins", {})
    results = {}
    for sid, per_model in scores.items():
        twin_id = twins.get(sid)
        twin_scores = scores.get(twin_id) if twin_id else None
        results[sid] = analyze_scenario(per_model, ability, twin_scores)
    calibratable = [s for s, r in results.items() if r["empirically_calibratable"]]
    return {"panel_size": len(ability),
            "scenarios": len(results),
            "empirically_calibratable": sorted(calibratable),
            "flagged": sorted(s for s in results if s not in calibratable),
            "results": results}


def assemble_panel_from_runs(specs: list[dict]) -> dict:
    """Build a panel-results object from completed `aies qualify` runs — so the
    pilot is one command. Each spec is {run_id, ability, model?}: the run is one
    panel model's scored evidence. Each rating contributes one observation (the
    mean of its EV1-EV6 scores, on the 0-4 scale) to its scenario; hold-out twins
    are read from the calibration metadata. `model` defaults to the run's
    registry id."""
    from . import constants as C
    from . import workspace

    scores: dict[str, dict[str, list[float]]] = {}
    panel: list[dict] = []
    seen_models: set[str] = set()
    for spec in specs:
        rdir = workspace.run_dir(spec["run_id"])
        manifest = workspace.read_json(rdir / "manifest.json")
        model = spec.get("model") or manifest.get("model", {}).get("registry_id") or spec["run_id"]
        if model in seen_models:
            raise ValueError(f"duplicate panel model {model!r} — one run per model")
        seen_models.add(model)
        panel.append({"model": model, "ability": int(spec["ability"])})

        rating_dir = rdir / "ratings"
        if not rating_dir.is_dir():
            raise ValueError(f"run {spec['run_id']!r} has no ratings — score it first")
        for rp in sorted(rating_dir.glob("*.json")):
            rec = workspace.read_json(rp)
            sid = rec.get("scenario_id")
            ev = rec.get("scores") or {}
            vals = [ev[d] for d in C.DIMENSIONS if isinstance(ev.get(d), (int, float))]
            if sid and len(vals) == len(C.DIMENSIONS):
                scores.setdefault(sid, {}).setdefault(model, []).append(round(mean(vals), 4))

    return {"panel": panel, "scores": scores, "twins": _twins_for(scores.keys())}


def _twins_for(scenario_ids) -> dict[str, str]:
    """Read each scenario's calibration.hold_out_twin from the competency files."""
    import yaml

    from . import runner

    base = runner.competencies_dir()
    out: dict[str, str] = {}
    for sid in scenario_ids:
        m = re.match(r"^(SC-(CA\d{2})-\d{3})$", sid)
        if not m:
            continue
        area = m.group(2)
        for f in base.glob(f"{area}-*/scenarios/{sid}.yaml"):
            try:
                d = yaml.safe_load(f.read_text(encoding="utf-8"))
            except Exception:  # pragma: no cover
                continue
            twin = (d.get("calibration") or {}).get("hold_out_twin")
            if twin:
                out[sid] = twin
            break
    return out


def render(report: dict) -> str:
    lines = [f"empirical calibration (panel of {report['panel_size']} models)",
             f"  scenarios analyzed : {report['scenarios']}",
             f"  discriminating     : {len(report['empirically_calibratable'])}",
             f"  flagged            : {len(report['flagged'])}",
             ""]
    for sid, r in sorted(report["results"].items()):
        if r["verdict"] == "discriminating":
            lines.append(f"  [ok  ] {sid}  disc={r['discrimination']} "
                         f"ceil={r['ceiling']} floor={r['floor']} std={r['repeatability_std']}")
        else:
            lines.append(f"  [FLAG] {sid}  {', '.join(r['flags'])}")
    return "\n".join(lines)

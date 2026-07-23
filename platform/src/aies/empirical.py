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

import datetime
import hashlib
import json
import re
from collections import Counter, defaultdict
from statistics import mean, pstdev

# Versioned like every other normative input (STABILITY/COMPATIBILITY):
#   METHODOLOGY_VERSION — how the metrics are computed (this analysis)
#   THRESHOLDS_VERSION  — the pass/fail cut-offs below
# An empirical verdict is only reproducible if BOTH are recorded with it: a change
# to either can flip a scenario's verdict, exactly like a decision-semantics change.
METHODOLOGY_VERSION = "1.0"
THRESHOLDS_VERSION = "1.0"

# Thresholds are deliberately conservative defaults; a real panel study documents
# and versions the ones it used (like any decision input).
DISCRIMINATION_MIN = 1.0      # top-group mean minus bottom-group mean, on the 0-4 scale
CEILING_MIN = 3.3             # strongest group should reach at least this
FLOOR_MAX = 2.5               # weakest group should land at or below this (a live floor)
REPEATABILITY_MAX_STD = 0.75  # per-(model,scenario) score std must be at or below this
TWIN_GAP_MAX = 1.0            # a model's |scenario - twin| gap above this flags gaming
PANEL_MIN_SUBJECTS = 3         # weak / middle / strong is the minimum useful shape
PANEL_PLAN_KIND = "aies-empirical-panel-plan-v1"
PANEL_PLAN_SCHEMA = 1


def _thresholds() -> dict:
    """The frozen threshold values used — recorded with results for reproducibility."""
    return {"version": THRESHOLDS_VERSION,
            "discrimination_min": DISCRIMINATION_MIN, "ceiling_min": CEILING_MIN,
            "floor_max": FLOOR_MAX, "repeatability_max_std": REPEATABILITY_MAX_STD,
            "twin_gap_max": TWIN_GAP_MAX}


def panel_plan_digest(plan: dict) -> str:
    payload = json.dumps(plan, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_panel_plan(plan: dict) -> list[str]:
    problems: list[str] = []
    if not isinstance(plan, dict) or plan.get("kind") != PANEL_PLAN_KIND:
        return [f"kind must be {PANEL_PLAN_KIND!r}"]
    if plan.get("schema_version") != PANEL_PLAN_SCHEMA:
        problems.append(f"schema_version must be {PANEL_PLAN_SCHEMA}")
    for field in ("panel_id", "created_at", "human_owner", "ability_basis"):
        if not isinstance(plan.get(field), str) or not plan[field].strip():
            problems.append(f"{field} must be a non-empty string")
    try:
        created = datetime.datetime.fromisoformat(
            str(plan.get("created_at", "")).replace("Z", "+00:00"))
        if created.tzinfo is None:
            problems.append("created_at must include a timezone")
    except ValueError:
        problems.append("created_at must be ISO-8601")
    if plan.get("methodology_version") != METHODOLOGY_VERSION:
        problems.append("methodology_version does not match the current analyzer")
    if plan.get("thresholds") != _thresholds():
        problems.append("thresholds do not match the current analyzer")
    if plan.get("risk_tier") not in {"RT1", "RT2", "RT3", "RT4"}:
        problems.append("risk_tier must be RT1, RT2, RT3, or RT4")
    if not isinstance(plan.get("repeats"), int) or isinstance(plan.get("repeats"), bool) \
            or plan.get("repeats", 0) < 1:
        problems.append("repeats must be a positive integer")

    rating = plan.get("rating_protocol")
    if not isinstance(rating, dict):
        problems.append("rating_protocol must be an object")
    else:
        for field in ("id", "validation_basis"):
            if not isinstance(rating.get(field), str) or not rating[field].strip():
                problems.append(f"rating_protocol.{field} must be a non-empty string")

    subjects = plan.get("subjects")
    if not isinstance(subjects, list) or len(subjects) < PANEL_MIN_SUBJECTS:
        problems.append(f"subjects must contain at least {PANEL_MIN_SUBJECTS} entries")
    else:
        ids = [item.get("subject") for item in subjects if isinstance(item, dict)]
        if len(ids) != len(subjects) or any(not isinstance(item, str) or not item.strip()
                                           for item in ids):
            problems.append("every subject needs a non-empty subject id")
        elif len(set(ids)) != len(ids):
            problems.append("subject ids must be unique")
        abilities = [item.get("ability") for item in subjects if isinstance(item, dict)]
        if any(not isinstance(rank, int) or isinstance(rank, bool) or rank < 1
               for rank in abilities):
            problems.append("every subject ability must be a positive integer")
        elif len(set(abilities)) < 2:
            problems.append("subjects need at least two ability ranks")

    instruments = plan.get("instruments")
    if not isinstance(instruments, list) or not instruments:
        problems.append("instruments must be a non-empty list")
    else:
        ids = []
        for item in instruments:
            if not isinstance(item, dict):
                problems.append("every instrument must be an object")
                continue
            ids.append(item.get("scenario_id"))
            for field in ("scenario_id", "prompt_hash", "content_hash",
                          "area", "suite_version"):
                if not isinstance(item.get(field), str) or not item[field].strip():
                    problems.append(f"instrument.{field} must be a non-empty string")
            if item.get("design_reviewed") is not True:
                problems.append("every planned instrument must be design-reviewed")
        if len(ids) != len(set(ids)):
            problems.append("instrument scenario ids must be unique")
    return list(dict.fromkeys(problems))


def create_panel_plan(*, panel_id: str, human_owner: str,
                      subjects: list[dict], areas: list[str], risk_tier: str,
                      repeats: int, ability_basis: str,
                      rating_protocol_id: str,
                      rating_protocol_basis: str,
                      created_at: str | None = None) -> dict:
    """Freeze a real-subject panel design before response collection."""
    from . import design_reviews, runner

    instruments = []
    normalized_areas = sorted(set(areas))
    for area in normalized_areas:
        _definition, scenarios, suite_version = runner.load_area(area)
        for scenario in scenarios:
            if scenario.get("risk_tier") != risk_tier:
                continue
            reviewed = bool((((scenario.get("calibration") or {})
                              .get("empirical_status") or {})
                             .get("design_reviewed")))
            if not reviewed:
                raise ValueError(
                    f"cannot preregister pending instrument {scenario.get('id')}")
            prompt = str(scenario.get("prompt") or "")
            instruments.append({
                "scenario_id": scenario["id"], "area": scenario["area"],
                "suite_version": suite_version,
                "prompt_hash": "sha256:" + hashlib.sha256(
                    prompt.encode("utf-8")).hexdigest(),
                "content_hash": design_reviews.scenario_content_hash(scenario),
                "design_reviewed": True,
            })
    plan = {
        "kind": PANEL_PLAN_KIND, "schema_version": PANEL_PLAN_SCHEMA,
        "panel_id": panel_id, "created_at": created_at or
        datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "human_owner": human_owner, "methodology_version": METHODOLOGY_VERSION,
        "thresholds": _thresholds(), "risk_tier": risk_tier,
        "areas": normalized_areas, "repeats": repeats,
        "ability_basis": ability_basis,
        "rating_protocol": {"id": rating_protocol_id,
                            "validation_basis": rating_protocol_basis},
        "subjects": sorted(subjects, key=lambda item: item["subject"]),
        "instruments": sorted(instruments, key=lambda item: item["scenario_id"]),
        "authority_boundary": (
            "This plan freezes study design. It does not validate the rating "
            "protocol, establish ability, promote an instrument, or grant qualification."),
    }
    problems = validate_panel_plan(plan)
    if problems:
        raise ValueError("invalid empirical panel plan: " + "; ".join(problems))
    return plan


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


def analyze_panel(panel: dict, panel_id: str | None = None,
                  analyzed_at: str | None = None) -> dict:
    """Analyze a full panel-results object:
      {"panel": [{"model": id, "ability": rank, ...}, ...],
       "scores": {scenario_id: {model_id: [score, ...]}},
       "twins":  {scenario_id: twin_scenario_id},   # optional
       "panel_id": str}                              # optional
    Returns per-scenario analyses, a summary, and an immutable **metadata** block
    (panel identity, participating models, methodology + thresholds versions, and
    the threshold values used) so an empirical verdict is reproducible."""
    panel_models = panel.get("panel", [])
    ability = {m["model"]: m["ability"] for m in panel_models}
    scores = panel.get("scores", {})
    twins = panel.get("twins", {})
    results = {}
    for sid, per_model in scores.items():
        twin_id = twins.get(sid)
        twin_scores = scores.get(twin_id) if twin_id else None
        results[sid] = analyze_scenario(per_model, ability, twin_scores)
    calibratable = [s for s, r in results.items() if r["empirically_calibratable"]]

    metadata = {
        "panel_id": panel_id or panel.get("panel_id"),
        "panel": panel_models,                     # participating models + ability (+ run/checksum)
        "methodology_version": METHODOLOGY_VERSION,
        "thresholds": _thresholds(),
        "analyzed_at": analyzed_at or datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    preregistration = panel.get("preregistration")
    promotion_eligible = bool(
        (panel.get("preflight") or {}).get("ready")
        and isinstance(preregistration, dict)
        and preregistration.get("plan_digest"))
    return {"kind": "empirical-calibration-result",
            "metadata": metadata,
            "panel_preflight": panel.get("preflight"),
            "preregistration": preregistration,
            "promotion_eligible": promotion_eligible,
            "panel_size": len(ability),
            "scenarios": len(results),
            "empirically_calibratable": sorted(calibratable),
            "flagged": sorted(s for s in results if s not in calibratable),
            "results": results}


def preflight_runs(specs: list[dict], plan: dict | None = None) -> dict:
    """Check whether scored runs form one comparable empirical panel.

    The preflight is intentionally stricter than merely finding score files. It
    requires the same scenario/repeat observations, prompt hashes, suite
    versions, and rating protocol across distinct subjects; exactly one rating
    observation per response; and a recorded, pre-run basis for supplied ability
    ranks. It never invents ability from the scores being calibrated.
    """
    from . import constants as C
    from . import workspace

    rows = []
    blockers: list[str] = []
    warnings: list[str] = []
    seen_subjects: set[str] = set()
    reference_keys = reference_hashes = reference_suites = reference_protocol = None
    observation_sets: list[set[tuple[str, int]]] = []
    rating_bases: set[str] = set()
    plan_digest = None
    expected_keys = expected_hashes = expected_suites = None
    if plan is not None:
        problems = validate_panel_plan(plan)
        if problems:
            blockers.extend(f"panel plan: {problem}" for problem in problems)
        else:
            plan_digest = panel_plan_digest(plan)
            expected_keys = {
                (item["scenario_id"], repeat)
                for item in plan["instruments"]
                for repeat in range(1, plan["repeats"] + 1)
            }
            prompt_by_scenario = {
                item["scenario_id"]: item["prompt_hash"]
                for item in plan["instruments"]
            }
            expected_hashes = {
                (scenario_id, repeat): prompt_by_scenario[scenario_id]
                for scenario_id, repeat in expected_keys
            }
            expected_suites = {
                item["area"]: item["suite_version"]
                for item in plan["instruments"]
            }

    if len(specs) < PANEL_MIN_SUBJECTS:
        blockers.append(
            f"panel has {len(specs)} subject(s); at least {PANEL_MIN_SUBJECTS} are required")

    for spec in specs:
        run_id = str(spec.get("run_id") or "")
        rdir = workspace.run_dir(run_id)
        manifest_path = rdir / "manifest.json"
        if not run_id or not manifest_path.exists():
            blockers.append(f"{run_id or '(missing run id)'}: manifest.json is missing")
            continue
        manifest = workspace.read_json(manifest_path)
        subject = (manifest.get("subject") or {}).get("id") or (
            manifest.get("model") or {}).get("registry_id") or run_id
        expected_subject = spec.get("expected_subject")
        if expected_subject and subject != expected_subject:
            blockers.append(
                f"{run_id}: run subject {subject!r} does not match planned "
                f"subject {expected_subject!r}")
        if subject in seen_subjects:
            blockers.append(f"{run_id}: duplicate panel subject {subject!r}")
        seen_subjects.add(subject)

        responses = {}
        for path in sorted((rdir / "responses").glob("*.json")):
            response = workspace.read_json(path)
            responses[path.name] = response
        ratings = []
        for path in sorted((rdir / "ratings").glob("*.json")):
            ratings.append(workspace.read_json(path))
        by_response: dict[str, list[dict]] = defaultdict(list)
        invalid_ratings = 0
        protocols = set()
        for rating in ratings:
            target = str(rating.get("rates_response") or "")
            scores = rating.get("scores") or {}
            if target not in responses or any(
                    not isinstance(scores.get(dimension), (int, float))
                    or isinstance(scores.get(dimension), bool)
                    or not 0 <= float(scores[dimension]) <= 4
                    for dimension in C.DIMENSIONS):
                invalid_ratings += 1
                continue
            by_response[target].append(rating)
            provenance = rating.get("provenance") or {}
            protocols.add((str(provenance.get("rater_kind") or "unknown"),
                           str(provenance.get("rater") or "unknown")))

        duplicate_observations = sum(
            len(items) - 1 for items in by_response.values() if len(items) > 1)
        unrated = sorted(set(responses) - set(by_response))
        if not responses:
            blockers.append(f"{run_id}: no response records")
        if invalid_ratings:
            blockers.append(f"{run_id}: {invalid_ratings} invalid or orphan rating(s)")
        if duplicate_observations:
            blockers.append(
                f"{run_id}: {duplicate_observations} duplicate/correction rating(s) "
                "would inflate repeatability")
        if unrated:
            blockers.append(f"{run_id}: {len(unrated)} response(s) are unrated")
        if len(protocols) != 1:
            blockers.append(
                f"{run_id}: expected one rating protocol, found {len(protocols)}")

        keys = {(str(rec.get("scenario_id")), int(rec.get("repeat") or 0))
                for rec in responses.values()}
        observation_sets.append(keys)
        hashes = {(str(rec.get("scenario_id")), int(rec.get("repeat") or 0)):
                  str((rec.get("request") or {}).get("prompt_hash") or "")
                  for rec in responses.values()}
        suites = {str(area.get("area")): str(area.get("suite_version"))
                  for area in manifest.get("areas", []) if isinstance(area, dict)}
        protocol = next(iter(protocols)) if len(protocols) == 1 else None
        protocol_id = f"{protocol[0]}:{protocol[1]}" if protocol else None

        if expected_keys is not None and keys != expected_keys:
            blockers.append(f"{run_id}: observations do not match the frozen panel plan")
        if expected_hashes is not None and hashes != expected_hashes:
            blockers.append(f"{run_id}: prompt hashes do not match the frozen panel plan")
        if expected_suites is not None and suites != expected_suites:
            blockers.append(f"{run_id}: suite versions do not match the frozen panel plan")
        planned_protocol = ((plan or {}).get("rating_protocol") or {}).get("id")
        if planned_protocol and protocol_id != planned_protocol:
            blockers.append(
                f"{run_id}: rating protocol {protocol_id!r} does not match planned "
                f"protocol {planned_protocol!r}")

        if reference_keys is None:
            reference_keys, reference_hashes = keys, hashes
            reference_suites, reference_protocol = suites, protocol
        else:
            if keys != reference_keys:
                blockers.append(
                    f"{run_id}: scenario/repeat set differs from the panel reference")
            if hashes != reference_hashes:
                blockers.append(f"{run_id}: prompt hashes differ from the panel reference")
            if suites != reference_suites:
                blockers.append(f"{run_id}: suite versions differ from the panel reference")
            if protocol != reference_protocol:
                blockers.append(f"{run_id}: rating protocol differs from the panel reference")

        ability = spec.get("ability")
        if ability is not None and (not isinstance(ability, int)
                                    or isinstance(ability, bool) or ability < 1):
            blockers.append(f"{run_id}: ability rank must be a positive integer")
        basis = str(spec.get("ability_basis") or "").strip()
        preregistered_at = str(spec.get("preregistered_at") or "").strip()
        rating_basis = str(spec.get("rating_protocol_basis") or "").strip()
        if ability is not None and not basis:
            blockers.append(f"{run_id}: supplied ability rank has no independent basis")
        if ability is not None and not preregistered_at:
            blockers.append(f"{run_id}: supplied ability rank has no preregistration timestamp")
        elif ability is not None:
            try:
                registered = datetime.datetime.fromisoformat(
                    preregistered_at.replace("Z", "+00:00"))
                created_text = str(manifest.get("created_at") or "")
                created = (datetime.datetime.fromisoformat(
                    created_text.replace("Z", "+00:00")) if created_text else None)
                if registered.tzinfo is None:
                    blockers.append(
                        f"{run_id}: preregistration timestamp needs a timezone")
                elif created and created.tzinfo is not None and registered >= created:
                    blockers.append(
                        f"{run_id}: ability rank was not preregistered before the run")
            except ValueError:
                blockers.append(f"{run_id}: preregistration timestamp is not ISO-8601")
        if not rating_basis:
            blockers.append(f"{run_id}: rating protocol has no validation basis")
        else:
            rating_bases.add(rating_basis)
        if any(token in rater.lower() for _kind, rater in protocols
               for token in ("provisional", "uncalibrated")):
            blockers.append(f"{run_id}: rating protocol is explicitly provisional/uncalibrated")

        rows.append({
            "run_id": run_id, "subject": subject,
            "responses": len(responses), "unique_scenarios": len({k[0] for k in keys}),
            "ratings": len(ratings), "unrated_responses": len(unrated),
            "duplicate_ratings": duplicate_observations,
            "rating_protocols": [f"{kind}:{rater}" for kind, rater in sorted(protocols)],
            "suite_versions": suites, "ability": ability,
            "ability_basis": basis or None, "preregistered_at": preregistered_at or None,
            "rating_protocol_basis": rating_basis or None,
        })

    ranks = {row["ability"] for row in rows if row["ability"] is not None}
    if ranks and len(ranks) < 2:
        blockers.append("panel needs at least two independently defined ability ranks")
    if not ranks:
        warnings.append(
            "ability ranks were not supplied; compatibility can be inspected, but "
            "discrimination analysis cannot be preregistered")
    if len(rating_bases) > 1:
        blockers.append("panel declares conflicting rating-protocol validation bases")

    common_keys = (set.intersection(*observation_sets) if observation_sets else set())

    # Keep output deterministic and readable while avoiding duplicate messages.
    blockers = list(dict.fromkeys(blockers))
    warnings = list(dict.fromkeys(warnings))
    return {
        "kind": "empirical-panel-preflight", "schema_version": 1,
        "ready": not blockers and bool(ranks),
        "status": "ready" if not blockers and ranks else "not-ready",
        "subjects": len(rows),
        "common_observations": len(common_keys),
        "common_scenarios": len({key[0] for key in common_keys}),
        "blockers": blockers, "warnings": warnings, "runs": rows,
        "panel_plan": ({"panel_id": plan.get("panel_id"), "digest": plan_digest}
                       if plan is not None else None),
        "authority_boundary": (
            "Preflight checks comparability only. A named human preregisters ability "
            "ranks from independent evidence and decides any scenario promotion."),
    }


def assemble_panel_from_runs(specs: list[dict], plan: dict | None = None) -> dict:
    """Build a panel-results object from completed `aies qualify` runs — so the
    pilot is one command. Each spec is {run_id, ability, model?}: the run is one
    panel model's scored evidence. Each rating contributes one observation (the
    mean of its EV1-EV6 scores, on the 0-4 scale) to its scenario; hold-out twins
    are read from the calibration metadata. `model` defaults to the run's
    registry id."""
    from . import constants as C
    from . import workspace

    preflight = preflight_runs(specs, plan=plan)
    structural_blockers = [blocker for blocker in preflight["blockers"]
                           if "ability rank" not in blocker
                           and "preregistration timestamp" not in blocker
                           and "independent basis" not in blocker
                           and "rating protocol has no validation basis" not in blocker]
    if structural_blockers:
        raise ValueError("empirical panel preflight failed: " + "; ".join(structural_blockers))

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
        # Record the run and model checksum so the panel is traceable to the exact
        # evidence it was assembled from (reproducibility).
        panel.append({"model": model, "ability": int(spec["ability"]),
                      "run_id": spec["run_id"],
                      "model_checksum": manifest.get("model", {}).get("checksum"),
                      "ability_basis": spec.get("ability_basis"),
                      "preregistered_at": spec.get("preregistered_at"),
                      "rating_protocol_basis": spec.get("rating_protocol_basis")})

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

    return {"panel": panel, "scores": scores, "twins": _twins_for(scores.keys()),
            "preflight": preflight,
            "preregistration": ({"panel_id": plan["panel_id"],
                                  "plan_digest": panel_plan_digest(plan),
                                  "created_at": plan["created_at"],
                                  "human_owner": plan["human_owner"]}
                                 if plan is not None else None)}


def assemble_panel_from_plan(plan: dict, assignments: dict[str, str]) -> dict:
    """Bind completed runs to the exact subjects frozen in a panel plan."""
    problems = validate_panel_plan(plan)
    if problems:
        raise ValueError("invalid empirical panel plan: " + "; ".join(problems))
    planned = {item["subject"]: item for item in plan["subjects"]}
    if set(assignments) != set(planned):
        missing = sorted(set(planned) - set(assignments))
        unknown = sorted(set(assignments) - set(planned))
        raise ValueError(
            f"planned-run assignments must match subjects; missing={missing}, "
            f"unknown={unknown}")
    specs = []
    for subject, item in planned.items():
        specs.append({
            "run_id": assignments[subject], "model": subject,
            "expected_subject": subject, "ability": item["ability"],
            "ability_basis": plan["ability_basis"],
            "preregistered_at": plan["created_at"],
            "rating_protocol_basis": plan["rating_protocol"]["validation_basis"],
        })
    return assemble_panel_from_runs(specs, plan=plan)


def render_preflight(report: dict) -> str:
    lines = [
        f"empirical panel preflight: {report['status'].upper()}",
        f"  subjects            : {report['subjects']}",
        f"  common scenarios     : {report['common_scenarios']}",
        f"  common observations  : {report['common_observations']}",
        "  authority            : human preregistration + promotion decision",
    ]
    for blocker in report["blockers"]:
        lines.append(f"  BLOCKER: {blocker}")
    for warning in report["warnings"]:
        lines.append(f"  warning: {warning}")
    return "\n".join(lines)


def render_panel_plan(plan: dict) -> str:
    return "\n".join([
        f"empirical panel plan: {plan['panel_id']}",
        f"  created             : {plan['created_at']}",
        f"  human owner         : {plan['human_owner']}",
        f"  subjects            : {len(plan['subjects'])}",
        f"  instruments         : {len(plan['instruments'])}",
        f"  risk tier / repeats : {plan['risk_tier']} / {plan['repeats']}",
        f"  rating protocol     : {plan['rating_protocol']['id']}",
        f"  digest              : {panel_plan_digest(plan)}",
        "  status              : FROZEN DESIGN — evidence collection not yet performed",
    ])


def _twins_for(scenario_ids) -> dict[str, str]:
    """Read each scenario's calibration.hold_out_twin from the competency files."""
    import yaml

    from . import runner

    base = runner.competencies_dir()
    out: dict[str, str] = {}
    for sid in scenario_ids:
        m = re.match(r"^SC-CA(\d{2})-\d{3}$", sid)
        if not m:
            continue
        for f in base.glob(f"CA-{m.group(1)}-*/scenarios/{sid}.yaml"):
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
    m = report.get("metadata", {})
    models = ", ".join(f"{p['model']}(a{p['ability']})" for p in m.get("panel", []))
    lines = [f"empirical calibration (panel of {report['panel_size']} models)",
             f"  panel id           : {m.get('panel_id') or '(unnamed)'}",
             f"  methodology / thr. : v{m.get('methodology_version')} / "
             f"v{(m.get('thresholds') or {}).get('version')}",
             f"  models             : {models}",
             f"  analyzed_at        : {m.get('analyzed_at')}",
             f"  scenarios analyzed : {report['scenarios']}",
             f"  discriminating     : {len(report['empirically_calibratable'])}",
             f"  flagged            : {len(report['flagged'])}",
             f"  promotion eligible : {'YES' if report.get('promotion_eligible') else 'NO — panel preflight/preregistration incomplete'}",
             ""]
    for sid, r in sorted(report["results"].items()):
        if r["verdict"] == "discriminating":
            lines.append(f"  [ok  ] {sid}  disc={r['discrimination']} "
                         f"ceil={r['ceiling']} floor={r['floor']} std={r['repeatability_std']}")
        else:
            lines.append(f"  [FLAG] {sid}  {', '.join(r['flags'])}")
    return "\n".join(lines)

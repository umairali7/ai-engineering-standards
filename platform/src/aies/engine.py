"""Qualification Engine: orchestrates the pipeline (PLATFORM.md §4).

M1 scope: stages 2-5 for a single model against one profile and one
risk-tier scope. Peer review (stage 6) arrives in M4; the decision
(stage 7) is always human — the engine assembles evidence only.
"""

from __future__ import annotations

import datetime
import math
import uuid

from . import config
from . import constants as C
from . import doctor, profiles, registry, runner, rating, scoring, workspace
from .adapters import resolve


class EngineError(Exception):
    pass


def plan_qualification(risk_tier: str, areas: list[str], *, subject_kind: str = "ai",
                       repeats: int | None = None) -> dict:
    """Pre-register the projected sample size before execution."""
    from . import task_mappings

    minimum = C.MIN_SAMPLE[subject_kind][risk_tier]
    rows = []
    required_uniform_repeats = 1
    mapping = task_mappings.load()
    covered_tasks: set[str] = set()
    for area in areas:
        _, scenarios, _ = runner.load_area(area)
        selected = [s for s in scenarios if s["risk_tier"] == risk_tier] or scenarios
        for scenario in selected:
            covered_tasks.update(task_mappings.tasks_for_scenario(scenario, mapping))
        planned = sum(repeats or int(s.get("repeats_min", 1)) for s in selected)
        required = math.ceil(minimum / len(selected)) if selected else minimum
        required_uniform_repeats = max(required_uniform_repeats, required)
        rows.append({"area": area, "scenarios": len(selected), "planned_items": planned,
                     "minimum_items": minimum, "decisional_if_scored": planned >= minimum,
                     "uniform_repeats_for_minimum": required})
    return {"risk_tier": risk_tier, "subject_kind": subject_kind,
            "minimum_items": minimum, "areas": rows,
            "planned_items": sum(row["planned_items"] for row in rows),
            "covered_tasks": sorted(covered_tasks),
            "unassessed_tasks": [name for task_id, name in task_mappings.task_names(mapping).items()
                                  if task_id not in covered_tasks],
            "all_decisional_if_scored": all(row["decisional_if_scored"] for row in rows),
            "uniform_repeats_for_all_areas": required_uniform_repeats}


def _new_run_id(model_id: str) -> str:
    # Timestamp for human ordering plus a short random suffix so two runs
    # of the same deployment within the same second never collide (their
    # response records are append-only and must land in distinct dirs).
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run-{stamp}-{model_id}-{uuid.uuid4().hex[:6]}"


def start_qualification(
    model_id: str,
    profile_name: str,
    risk_tier: str,
    areas: list[str],
    repeats: int | None = None,
    subject_kind: str = "ai",
    runtime: str | None = None,
    workers: int | None = None,
    assessment: dict | None = None,
    decisional: bool = False,
) -> dict:
    """Stages 2-4: discovery, environment, benchmark execution.

    `model_id` targets a **deployment** — either its id or a model name
    resolved against the registry (disambiguated by `runtime` when the
    same model is served more than once, PLATFORM.md D11).

    Writes the pre-registered run manifest (sampling rule fixed before
    scoring — AIES-AESQS-CS-01-R12) and the response records, then
    generates the human scoresheet.
    """
    if risk_tier not in C.RISK_TIERS:
        raise EngineError(f"risk tier must be one of {C.RISK_TIERS}")
    entry = registry.resolve(model_id, runtime=runtime)
    profile = profiles.load(profile_name)
    adapter_cls = resolve(entry["runtime"])
    adapter = adapter_cls()
    adapter.load(entry)

    # Generation parameters: env/.env defaults, overridden by the
    # deployment manifest's parameters_default. Nothing hard-coded.
    gen_params = {**config.generation_defaults(),
                  **(entry.get("parameters_default") or {})}
    if workers is None:
        workers = config.default_parallel()

    # Stage 2 — capability discovery (M1: adapter declaration + smoke
    # probe; claims in the registry entry are recorded as unverified).
    # The smoke probe is a liveness check, so it fails fast (a dead or
    # misconfigured endpoint should error in seconds, not after the full
    # per-request timeout used for real scenario calls).
    smoke_params = {**gen_params,
                    "timeout_s": min(float(gen_params.get("timeout_s", 300)), 30.0)}
    try:
        smoke = adapter.generate(runner.GenerationRequest(
            prompt="Reply with the single word: ready", parameters=smoke_params))
    except Exception as e:
        raise EngineError(
            f"deployment {entry['id']!r} did not respond to a liveness probe: {e}"
        ) from e
    discovery = {
        "adapter_declared": adapter.capabilities(),
        "registry_claims": entry.get("capabilities", {}),
        "claims_verified": False,  # full probe suites arrive with M2 suites
        "smoke_probe_ok": bool(smoke.text.strip()),
    }

    # Stage 3 — environment validation.
    fp = doctor.fingerprint(adapter.fingerprint())

    plan = plan_qualification(risk_tier, areas, subject_kind=subject_kind, repeats=repeats)
    if decisional:
        required = plan["uniform_repeats_for_all_areas"]
        if repeats is not None and repeats < required:
            raise EngineError(
                f"--decisional needs at least {required} repeats for every selected area at "
                f"{C.risk_tier_label(risk_tier)}; --repeats {repeats} is insufficient"
            )
        repeats = max(repeats or 0, required)
        plan = plan_qualification(risk_tier, areas, subject_kind=subject_kind, repeats=repeats)

    run_id = _new_run_id(model_id)
    all_scenarios: list[tuple[dict, list[dict], str]] = []
    for area in areas:
        definition, scenarios, suite_version = runner.load_area(area)
        in_scope = [s for s in scenarios if s["risk_tier"] == risk_tier] or scenarios
        all_scenarios.append((definition, in_scope, suite_version))

    _prov = entry.get("provenance") or {}
    _model_block = {"registry_id": entry["id"],
                    "checksum": _prov.get("checksum", "unknown")}
    # Carry optional AI supply-chain provenance into the durable evidence
    # (model signature / AI-BOM), so qualification records are audit-complete
    # against supply-chain standards (CROSSWALK §3b).
    if _prov.get("signature"):
        _model_block["signature"] = _prov["signature"]
    if _prov.get("ai_bom"):
        _model_block["ai_bom"] = _prov["ai_bom"]
    # `model` remains a compatibility envelope for the current deployment
    # executor. `subject` is the canonical, subject-neutral identity used by
    # new decision products. Future executors can populate it without
    # redefining the evidence architecture.
    _subject_block = {
        "id": entry["id"],
        "kind": "ai_deployment",
        "display_name": entry.get("model") or entry.get("family") or entry["id"],
        "executor_kind": "deployment",
    }
    manifest = {
        "run_id": run_id,
        "subject": _subject_block,
        "model": _model_block,
        "profile": profile["name"],
        # Capture the profile VERSION as used at run time (immutable). A later
        # edit to the profile file must not silently reinterpret this result —
        # this is what makes a certification reproducible (STABILITY/reproducibility).
        "profile_version": profiles.profile_version(profile),
        "risk_tier": risk_tier,
        "subject_kind": subject_kind,
        "repeats": repeats,          # override used, if any (for resume-collection)
        "sample_plan": plan,
        "decisional_target": decisional,
        "scoped_areas": list(areas),  # the CA codes as requested (for resume-collection)
        # The assessment this run was composed under (ADR-0005), if any — the
        # decision engine reads this to compute the assessment outcome. Recording
        # it here keeps the composition immutable with the evidence.
        **({"assessment": assessment} if assessment else {}),
        "areas": [
            {"area": d.get("area", a), "suite_version": v,
             "n_scenarios": len(s),
             "planned_items": sum(repeats or int(x.get("repeats_min", 1)) for x in s)}
            for (d, s, v), a in zip(all_scenarios, areas)
        ],
        "sampling_rule": (
            "all scenarios of the scoped risk tier in the named suites, "
            f"repeats per scenario minimum (override: {repeats}); "
            "pre-registered before scoring per AIES-AESQS-CS-01-R12"
        ),
        "generation_parameters": gen_params,
        "discovery": discovery,
        "environment_fingerprint": fp,
        "status": "responses-collected",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest, overwrite=True)

    # Stage 4 — benchmark execution.
    for (definition, scenarios, suite_version), area in zip(all_scenarios, areas):
        runner.execute_suite(run_id, entry, adapter, scenarios, suite_version, fp,
                             repeats=repeats, parameters=gen_params, workers=workers)

    rating.build_scoresheet(run_id)
    return manifest


def resume_collection(run_id: str, workers: int | None = None) -> dict:
    """Fill only the *missing* responses of a partially-collected run (e.g. one
    whose collection failed partway on a flaky endpoint), then rebuild the
    scoresheet — no re-collecting what already succeeded.

    Reconstructs the deployment, scenarios, and generation parameters from the
    run manifest. Refuses if a suite has changed since collection (the existing
    responses would no longer be comparable, per PLATFORM.md §9)."""
    rdir = workspace.run_dir(run_id)
    mpath = rdir / "manifest.json"
    if not mpath.exists():
        raise EngineError(f"no run {run_id!r} in this workspace")
    manifest = workspace.read_json(mpath)
    entry = registry.get(manifest["model"]["registry_id"])
    adapter = resolve(entry["runtime"])()
    adapter.load(entry)
    if workers is None:
        workers = config.default_parallel()

    repeats = manifest.get("repeats")
    risk_tier = manifest["risk_tier"]
    gen_params = manifest.get("generation_parameters") or config.generation_defaults()
    fp = manifest["environment_fingerprint"]
    scoped = manifest.get("scoped_areas") or [a["area"] for a in manifest["areas"]]
    recorded_sv = {a["area"]: a["suite_version"] for a in manifest["areas"]}

    before = len(list((rdir / "responses").glob("*.json")))
    filled = 0
    for area in scoped:
        definition, scenarios, suite_version = runner.load_area(area)
        code = definition.get("area", area)
        if recorded_sv.get(code) and recorded_sv[code] != suite_version:
            raise EngineError(
                f"suite {code} changed since collection "
                f"({recorded_sv[code]} -> {suite_version}); cannot resume — "
                "start a fresh run")
        in_scope = [s for s in scenarios if s["risk_tier"] == risk_tier] or scenarios
        written = runner.execute_suite(run_id, entry, adapter, in_scope, suite_version,
                                       fp, repeats=repeats, parameters=gen_params,
                                       workers=workers, skip_existing=True)
        filled += len(written)

    rating.build_scoresheet(run_id)
    after = len(list((rdir / "responses").glob("*.json")))
    planned = sum(a["planned_items"] for a in manifest["areas"])
    return {"run_id": run_id, "filled": filled, "responses": after,
            "was": before, "planned": planned}


def start_journey(
    model_id: str,
    profile_name: str,
    journey_id: str,
    repeats: int | None = None,
    subject_kind: str = "ai",
    runtime: str | None = None,
) -> dict:
    """Run a multi-phase journey (journeys.py) against a deployment.

    A journey carries work through several SDLC phases, threading each
    step's output into the next. Steps are recorded as ordinary response
    records tagged with their competency area, so `aggregate` and the rest
    of the pipeline consume them unchanged. The journey's declared risk
    tier is the scoring tier for the run.
    """
    from . import journeys
    entry = registry.resolve(model_id, runtime=runtime)
    profile = profiles.load(profile_name)
    journey, jversion = journeys.load_journey(journey_id)
    adapter_cls = resolve(entry["runtime"])
    adapter = adapter_cls()
    adapter.load(entry)

    gen_params = {**config.generation_defaults(),
                  **(entry.get("parameters_default") or {})}
    fp = doctor.fingerprint(adapter.fingerprint())
    run_id = _new_run_id(model_id)
    rt = journey["risk_tier"]

    areas = sorted({s["area"] for s in journey["steps"]})
    manifest = {
        "run_id": run_id,
        "kind": "journey",
        "journey": {"id": journey["id"], "title": journey.get("title", ""),
                    "version": jversion,
                    "steps": [{"id": s["id"], "area": s["area"],
                               "phase": s.get("phase", "")} for s in journey["steps"]]},
        "model": {"registry_id": entry["id"],
                  "checksum": (entry.get("provenance") or {}).get("checksum", "unknown")},
        "subject": {"id": entry["id"], "kind": "ai_deployment",
                    "display_name": entry.get("model") or entry.get("family") or entry["id"],
                    "executor_kind": "deployment"},
        "profile": profile["name"],
        "profile_version": profiles.profile_version(profile),
        "risk_tier": rt,
        "subject_kind": subject_kind,
        "areas": [{"area": a, "suite_version": jversion,
                   "planned_items": (repeats or 1) * sum(1 for s in journey["steps"]
                                                         if s["area"] == a)}
                  for a in areas],
        "sampling_rule": (
            f"journey {journey['id']} — {len(journey['steps'])} steps across "
            f"{len(areas)} competency areas, {repeats or 1} repeat(s); each step "
            "scored at the journey risk tier. Journeys test lifecycle depth, "
            "not sample volume — combine repeats/journeys to reach decisional sizes."),
        "generation_parameters": gen_params,
        "environment_fingerprint": fp,
        "status": "responses-collected",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest, overwrite=True)
    runner.execute_journey(run_id, entry, adapter, journey, jversion, fp,
                           repeats=repeats, parameters=gen_params)
    rating.build_scoresheet(run_id)
    return manifest


def aggregate(run_id: str) -> dict:
    """Stage 5: aggregate ratings into the evidence package."""
    rdir = workspace.run_dir(run_id)
    manifest = workspace.read_json(rdir / "manifest.json")
    ratings = rating.collect_ratings(run_id)
    if not ratings:
        raise EngineError(
            f"run {run_id!r} has no ratings — fill the scoresheet and run "
            "`aies score` first (M1 human scoring hook)"
        )
    profile = profiles.load(manifest["profile"])
    adjustments = profile.get("dimension_weight_adjustments") or {}
    rt = manifest["risk_tier"]

    # Model and automated ratings are retained as auditable observations, but
    # cannot enter the qualification aggregate unless their reviewer has been
    # explicitly admitted by a recorded qualification or calibration review.
    review_path = rdir / "review-package.json"
    review_pkg = workspace.read_json(review_path) if review_path.exists() else {}
    reviewer = review_pkg.get("reviewer") or {}
    admitted_model_raters = ({reviewer.get("label")} if reviewer.get("admitted")
                              and reviewer.get("label") else set())

    def is_admitted(record: dict) -> bool:
        provenance = record.get("provenance") or {}
        return (provenance.get("rater_kind") == "human"
                or provenance.get("rater") in admitted_model_raters)

    by_area: dict[str, list[dict]] = {a["area"]: [] for a in manifest.get("areas", [])}
    raw_by_area: dict[str, int] = {a["area"]: 0 for a in manifest.get("areas", [])}
    admitted_by_area: dict[str, int] = {a["area"]: 0 for a in manifest.get("areas", [])}
    responses = {p.name: workspace.read_json(p)
                 for p in (rdir / "responses").glob("*.json")}
    for r in ratings:
        resp = responses.get(r["rates_response"])
        area = resp["area"] if resp else "unknown"
        raw_by_area[area] = raw_by_area.get(area, 0) + 1
        if is_admitted(r):
            by_area.setdefault(area, []).append(r["scores"])
            admitted_by_area[area] = admitted_by_area.get(area, 0) + 1

    areas = {}
    for area, item_scores in sorted(by_area.items()):
        res = scoring.score_area(area, rt, item_scores,
                                 subject_kind=manifest.get("subject_kind", "ai"),
                                 weight_adjustments=adjustments)
        areas[area] = {
            "n_scored": res.n_scored,
            "raw_ratings": raw_by_area.get(area, 0),
            "admitted_ratings": admitted_by_area.get(area, 0),
            "advisory_ratings": raw_by_area.get(area, 0) - admitted_by_area.get(area, 0),
            "min_sample": res.min_sample,
            "decisional": res.decisional,
            "dimensions": {
                d: {"n": s.n, "mean": s.mean, "ci90_low": s.ci_low,
                    "ci90_high": s.ci_high}
                for d, s in res.dimensions.items()
            },
            "gates": [
                {"dimension": g.dimension, "threshold": g.threshold,
                 "decision_value": g.decision_value, "passed": g.passed,
                 **({"reason": g.reason} if g.reason else {})}
                for g in res.gates
            ],
            "gates_passed": res.gates_passed,
            "ev3_hard_fail": res.ev3_hard_fail,
            "weights_used": res.weights_used,
            "aggregate_A": res.aggregate,
            "cl": res.cl,
            "cl_note": res.cl_note,
            "al_envelope": res.al_envelope,
        }

    package = {
        "run_id": run_id,
        "kind": "evidence-package",
        # Versioned artifact envelope: the Evidence Package is a first-class,
        # independently-versioned artifact (it can outlive a given decision
        # engine and be replayed through a future one). Field-append-only;
        # see COMPATIBILITY.md. EVIDENCE_SCHEMA lives in constants.
        "evidence_schema": C.EVIDENCE_SCHEMA,
        "grant_status": "no grant — evidence only; a human qualification "
                        "authority records any grant (PLATFORM.md D8)",
        "subject": manifest.get("subject") or {
            "id": manifest["model"]["registry_id"],
            "kind": "ai_deployment",
            "display_name": manifest["model"]["registry_id"],
            "executor_kind": "deployment",
        },
        # Legacy deployment/model envelope retained for existing consumers.
        "model": manifest["model"],
        "profile": manifest["profile"],
        "profile_version": manifest.get("profile_version", profiles.UNVERSIONED),
        "risk_tier": rt,
        "subject_kind": manifest.get("subject_kind", "ai"),
        "suite_versions": {a["area"]: a["suite_version"] for a in manifest["areas"]},
        "environment_fingerprint": manifest["environment_fingerprint"],
        "areas": areas,
        "raters": sorted({r["provenance"]["rater"] for r in ratings}),
        "rater_kinds": sorted({r["provenance"]["rater_kind"] for r in ratings}),
        "admitted_raters": sorted({r["provenance"]["rater"] for r in ratings if is_admitted(r)}),
        "admitted_rater_kinds": sorted({r["provenance"]["rater_kind"] for r in ratings if is_admitted(r)}),
        "rating_admission": {
            "admitted_ratings": sum(1 for r in ratings if is_admitted(r)),
            "advisory_ratings": sum(1 for r in ratings if not is_admitted(r)),
            "reviewer_admitted": bool(reviewer.get("admitted")),
            "reviewer_reason": reviewer.get("reason"),
        },
        "aggregated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    workspace.write_json(rdir / "evidence-package.json", package, overwrite=True)
    manifest["status"] = "aggregated"
    workspace.write_json(rdir / "manifest.json", manifest, overwrite=True)
    return package

"""Qualification Engine: orchestrates the pipeline (PLATFORM.md §4).

M1 scope: stages 2-5 for a single model against one profile and one
risk-tier scope. Peer review (stage 6) arrives in M4; the decision
(stage 7) is always human — the engine assembles evidence only.
"""

from __future__ import annotations

import datetime
import uuid

from . import config
from . import constants as C
from . import doctor, profiles, registry, runner, rating, scoring, workspace
from .adapters import resolve


class EngineError(Exception):
    pass


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
    smoke = adapter.generate(runner.GenerationRequest(
        prompt="Reply with the single word: ready", parameters=gen_params))
    discovery = {
        "adapter_declared": adapter.capabilities(),
        "registry_claims": entry.get("capabilities", {}),
        "claims_verified": False,  # full probe suites arrive with M2 suites
        "smoke_probe_ok": bool(smoke.text.strip()),
    }

    # Stage 3 — environment validation.
    fp = doctor.fingerprint(adapter.fingerprint())

    run_id = _new_run_id(model_id)
    all_scenarios: list[tuple[dict, list[dict], str]] = []
    for area in areas:
        definition, scenarios, suite_version = runner.load_area(area)
        in_scope = [s for s in scenarios if s["risk_tier"] == risk_tier] or scenarios
        all_scenarios.append((definition, in_scope, suite_version))

    manifest = {
        "run_id": run_id,
        "model": {"registry_id": entry["id"],
                  "checksum": (entry.get("provenance") or {}).get("checksum", "unknown")},
        "profile": profile["name"],
        "risk_tier": risk_tier,
        "subject_kind": subject_kind,
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
        "profile": profile["name"],
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

    by_area: dict[str, list[dict]] = {}
    responses = {p.name: workspace.read_json(p)
                 for p in (rdir / "responses").glob("*.json")}
    for r in ratings:
        resp = responses.get(r["rates_response"])
        area = resp["area"] if resp else "unknown"
        by_area.setdefault(area, []).append(r["scores"])

    areas = {}
    for area, item_scores in sorted(by_area.items()):
        res = scoring.score_area(area, rt, item_scores,
                                 subject_kind=manifest.get("subject_kind", "ai"),
                                 weight_adjustments=adjustments)
        areas[area] = {
            "n_scored": res.n_scored,
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
        "grant_status": "no grant — evidence only; a human qualification "
                        "authority records any grant (PLATFORM.md D8)",
        "model": manifest["model"],
        "profile": manifest["profile"],
        "risk_tier": rt,
        "subject_kind": manifest.get("subject_kind", "ai"),
        "suite_versions": {a["area"]: a["suite_version"] for a in manifest["areas"]},
        "environment_fingerprint": manifest["environment_fingerprint"],
        "areas": areas,
        "raters": sorted({r["provenance"]["rater"] for r in ratings}),
        "aggregated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    workspace.write_json(rdir / "evidence-package.json", package, overwrite=True)
    manifest["status"] = "aggregated"
    workspace.write_json(rdir / "manifest.json", manifest, overwrite=True)
    return package

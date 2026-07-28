"""Engineering assessment engine: orchestrates the evidence pipeline.

The default CLI purpose is engineering evaluation. Formal qualification is a
separate explicit purpose with human-governed admission and grant semantics.
"""

from __future__ import annotations

import datetime
import math
import threading
import uuid

from . import config
from . import constants as C
from . import (doctor, evidence_events, executors, profiles, progress, registry,
               runner, rating, scoring, subjects, workspace)


class EngineError(Exception):
    pass


class RunExecutionError(EngineError):
    """A run failed after durable run state had been created."""

    def __init__(self, message: str, *, run_id: str, phase: str):
        super().__init__(message)
        self.run_id = run_id
        self.phase = phase


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
        # Distinct instruments establish sample breadth. Exact prompt repeats
        # are never scheduled implicitly and never pad a decisional minimum;
        # a caller can still request them explicitly for a stability study.
        planned = len(selected) * (repeats or 1)
        required = math.ceil(minimum / len(selected)) if selected else minimum
        required_uniform_repeats = max(required_uniform_repeats, required)
        rows.append({"area": area, "scenarios": len(selected), "planned_items": planned,
                     "minimum_items": minimum,
                     "decisional_if_scored": len(selected) >= minimum,
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


def _global_task_label(current: str, offset: int, total_items: int) -> str:
    """Translate a suite-local Task X/Y label into its run-wide ordinal."""
    prefix, separator, detail = current.partition(" · ")
    if prefix.startswith("Task ") and "/" in prefix:
        ordinal_text = prefix[5:].split("/", 1)[0]
        try:
            ordinal = offset + int(ordinal_text)
            return f"Task {ordinal}/{total_items}{separator}{detail}"
        except ValueError:
            pass
    return current


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
    run_purpose: str = "formal-qualification",
    progress_callback=None,
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
    executor = executors.RuntimeGenerationExecutor(entry)
    executor.load()

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
        smoke = executor.generate(runner.GenerationRequest(
            prompt="Reply with the single word: ready", parameters=smoke_params))
    except Exception as e:
        raise EngineError(
            f"deployment {entry['id']!r} did not respond to a liveness probe: {e}"
        ) from e
    discovery = {
        "adapter_declared": executor.capabilities(),
        "subject_executor": executor.declaration(),
        "registry_claims": entry.get("capabilities", {}),
        "claims_verified": False,  # full probe suites arrive with M2 suites
        "smoke_probe_ok": bool(smoke.text.strip()),
    }

    # Stage 3 — environment validation.
    fp = doctor.fingerprint(executor.fingerprint())

    plan = plan_qualification(risk_tier, areas, subject_kind=subject_kind, repeats=repeats)
    if decisional:
        short = [row for row in plan["areas"] if not row["decisional_if_scored"]]
        if short:
            detail = ", ".join(
                f"{row['area']} ({row['scenarios']}/{row['minimum_items']} distinct)"
                for row in short)
            raise EngineError(
                f"--decisional requires distinct scenario breadth at "
                f"{C.risk_tier_label(risk_tier)}: {detail}; exact repeats cannot fill the gap"
            )

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
    execution = executor.declaration()
    _subject_block = subjects.deployment_descriptor(
        entry, fp, executor=execution)
    manifest = {
        "schema": subjects.RUN_MANIFEST_SCHEMA,
        "run_id": run_id,
        "subject": _subject_block,
        "execution": execution,
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
        "sample_adequacy_policy": "distinct-scenarios-v1",
        "assessment_instrument_contract": {
            "kind": "aies-assessment-instrument",
            "schema_version": 1,
            "candidate_projection": "task-only",
            "reviewer_projection": "full-hidden-instrument",
            "snapshot_policy": "append-only-before-response-collection",
        },
        "decisional_target": decisional,
        "run_purpose": run_purpose,
        "scoped_areas": list(areas),  # the CA codes as requested (for resume-collection)
        # The assessment this run was composed under (ADR-0005), if any — the
        # decision engine reads this to compute the assessment outcome. Recording
        # it here keeps the composition immutable with the evidence.
        **({"assessment": assessment} if assessment else {}),
        "areas": [
            {"area": d.get("area", a), "suite_version": v,
             "n_scenarios": len(s),
             "planned_items": len(s) * (repeats or 1)}
            for (d, s, v), a in zip(all_scenarios, areas)
        ],
        "sampling_rule": (
            "all distinct scenarios of the scoped risk tier in the named suites, "
            f"one execution each (explicit repeat override: {repeats}); "
            "pre-registered before scoring per AIES-AESQS-CS-01-R12"
        ),
        "generation_parameters": gen_params,
        "discovery": discovery,
        "environment_fingerprint": fp,
        "status": "collecting-responses",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest, overwrite=True)
    evidence_events.record_manifest(run_id, manifest)

    # Stage 4 — benchmark execution.
    total_items = plan["planned_items"]
    completed_items = failures = 0
    collection_progress_lock = threading.Lock()
    active_collection_tasks: dict[str, None] = {}
    progress.update(run_id, "response-collection", 0, total_items,
                    message=f"collecting across {workers} worker(s)",
                    parallelism=max(1, workers),
                    estimated_seconds_per_request=(
                        (entry.get("planning") or {}).get(
                            "estimated_seconds_per_request")),
                    callback=progress_callback)

    def _collection_progress(_done, _total, current, status):
        nonlocal completed_items, failures
        with collection_progress_lock:
            if status == "started":
                active_collection_tasks[current] = None
            if status in {"completed", "failed"}:
                completed_items += 1
                failures += int(status == "failed")
                active_collection_tasks.pop(current, None)
            activity = {"started": "Executing task", "completed": "Completed task",
                        "failed": "Failed task"}.get(status, "Current task")
            progress.update(run_id, "response-collection", completed_items, total_items,
                            current=current, activity=activity, failures=failures,
                            active_tasks=list(active_collection_tasks),
                            parallelism=max(1, workers),
                            callback=progress_callback)

    try:
        suite_offset = 0
        for (definition, scenarios, suite_version), area in zip(all_scenarios, areas):
            suite_items = len(scenarios) * (repeats or 1)

            def _suite_progress(done, total, current, status, *,
                                _offset=suite_offset):
                # execute_suite numbers tasks within one competency suite.
                # Present run-wide ordinals so a multi-area assessment remains
                # understandable (for example Task 58/147, not Task 1/30).
                current = _global_task_label(current, _offset, total_items)
                _collection_progress(done, total, current, status)

            runner.execute_suite(
                run_id, entry, executor, scenarios, suite_version, fp,
                repeats=repeats, parameters=gen_params, workers=workers,
                progress_callback=_suite_progress)
            suite_offset += suite_items
    except Exception as exc:
        manifest["status"] = "collection-partial" if completed_items > failures else "collection-failed"
        workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest, overwrite=True)
        evidence_events.record_manifest(run_id, manifest)
        progress.update(run_id, "response-collection", completed_items, total_items,
                        status="partial" if completed_items > failures else "failed",
                        failures=failures, message="collection stopped; run is resumable",
                        callback=progress_callback)
        raise RunExecutionError(
            str(exc), run_id=run_id, phase="collection") from exc

    rating.build_scoresheet(run_id)
    manifest["status"] = "responses-collected"
    workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest, overwrite=True)
    evidence_events.record_manifest(run_id, manifest)
    progress.update(run_id, "response-collection", total_items, total_items,
                    status="completed", message="responses collected; scoresheet ready",
                    callback=progress_callback)
    return manifest


def resume_collection(run_id: str, workers: int | None = None,
                      progress_callback=None) -> dict:
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
    executor = executors.RuntimeGenerationExecutor(entry)
    executor.load()
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
    planned = sum(a["planned_items"] for a in manifest["areas"])
    failed = 0
    resume_progress_lock = threading.Lock()
    active_resume_tasks: dict[str, None] = {}
    progress.update(run_id, "response-collection", before, planned,
                    message="resuming missing responses",
                    parallelism=max(1, workers), reset_operation=True,
                    callback=progress_callback)

    def _resume_progress(_done, _total, current, status):
        nonlocal filled, failed
        with resume_progress_lock:
            if status == "started":
                active_resume_tasks[current] = None
            filled += int(status == "completed")
            failed += int(status == "failed")
            if status in {"completed", "failed"}:
                active_resume_tasks.pop(current, None)
            activity = {"started": "Executing task", "completed": "Completed task",
                        "failed": "Failed task"}.get(status, "Current task")
            progress.update(run_id, "response-collection", before + filled + failed,
                            planned, current=current, activity=activity,
                            active_tasks=list(active_resume_tasks),
                            parallelism=max(1, workers),
                            failures=failed, callback=progress_callback)

    try:
        for area in scoped:
            definition, scenarios, suite_version = runner.load_area(area)
            code = definition.get("area", area)
            if recorded_sv.get(code) and recorded_sv[code] != suite_version:
                raise EngineError(
                    f"suite {code} changed since collection "
                    f"({recorded_sv[code]} -> {suite_version}); cannot resume — "
                    "start a fresh run")
            in_scope = [s for s in scenarios if s["risk_tier"] == risk_tier] or scenarios
            runner.execute_suite(run_id, entry, executor, in_scope, suite_version,
                                 fp, repeats=repeats, parameters=gen_params,
                                 workers=workers, skip_existing=True,
                                 progress_callback=_resume_progress)
    except Exception:
        after = len(list((rdir / "responses").glob("*.json")))
        manifest["status"] = "collection-partial" if after else "collection-failed"
        workspace.write_json(mpath, manifest, overwrite=True)
        evidence_events.record_manifest(run_id, manifest)
        progress.update(run_id, "response-collection", after, planned,
                        status="partial" if after else "failed", failures=failed,
                        message="resume stopped; successful responses were preserved",
                        callback=progress_callback)
        raise

    rating.build_scoresheet(run_id)
    after = len(list((rdir / "responses").glob("*.json")))
    manifest["status"] = "responses-collected"
    workspace.write_json(mpath, manifest, overwrite=True)
    evidence_events.record_manifest(run_id, manifest)
    progress.update(run_id, "response-collection", after, planned,
                    status="completed", failures=failed,
                    message="resume complete; scoresheet ready",
                    callback=progress_callback)
    return {"run_id": run_id, "filled": filled, "responses": after,
            "was": before, "planned": planned}


def start_journey(
    model_id: str,
    profile_name: str,
    journey_id: str,
    repeats: int | None = None,
    subject_kind: str = "ai",
    runtime: str | None = None,
    run_purpose: str = "formal-qualification",
    progress_callback=None,
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
    executor = executors.RuntimeGenerationExecutor(entry)
    executor.load()

    gen_params = {**config.generation_defaults(),
                  **(entry.get("parameters_default") or {})}
    fp = doctor.fingerprint(executor.fingerprint())
    run_id = _new_run_id(model_id)
    rt = journey["risk_tier"]

    areas = sorted({s["area"] for s in journey["steps"]})
    manifest = {
        "schema": subjects.RUN_MANIFEST_SCHEMA,
        "run_id": run_id,
        "kind": "journey",
        "assessment_instrument_contract": {
            "kind": "aies-assessment-instrument",
            "schema_version": 1,
            "candidate_projection": "task-only",
            "reviewer_projection": "full-hidden-instrument",
            "snapshot_policy": "append-only-before-step-execution",
        },
        "run_purpose": run_purpose,
        "journey": {"id": journey["id"], "title": journey.get("title", ""),
                    "version": jversion,
                    "steps": [{"id": s["id"], "area": s["area"],
                               "phase": s.get("phase", "")} for s in journey["steps"]]},
        "model": {"registry_id": entry["id"],
                  "checksum": (entry.get("provenance") or {}).get("checksum", "unknown")},
        "subject": subjects.deployment_descriptor(
            entry, fp, executor=executor.declaration()),
        "execution": executor.declaration(),
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
        "status": "collecting-responses",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest, overwrite=True)
    evidence_events.record_manifest(run_id, manifest)
    total_steps = (repeats or 1) * len(journey["steps"])
    progress.update(run_id, "journey-collection", 0, total_steps,
                    parallelism=1, callback=progress_callback)

    def _journey_progress(done, total, current, status):
        active = [current] if status == "started" else []
        progress.update(run_id, "journey-collection", done, total,
                        current=current,
                        activity=("Executing journey task" if status == "started"
                                  else "Completed journey task" if status == "completed"
                                  else "Failed journey task"),
                        failures=int(status == "failed"),
                        active_tasks=active, parallelism=1,
                        callback=progress_callback)

    try:
        runner.execute_journey(run_id, entry, executor, journey, jversion, fp,
                               repeats=repeats, parameters=gen_params,
                               progress_callback=_journey_progress)
    except Exception:
        collected = len(list((workspace.run_dir(run_id) / "responses").glob("*.json")))
        manifest["status"] = "collection-partial" if collected else "collection-failed"
        workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest,
                             overwrite=True)
        evidence_events.record_manifest(run_id, manifest)
        progress.update(run_id, "journey-collection", collected, total_steps,
                        status="partial" if collected else "failed", failures=1,
                        message="journey stopped; successful steps were preserved",
                        callback=progress_callback)
        raise
    rating.build_scoresheet(run_id)
    manifest["status"] = "responses-collected"
    workspace.write_json(workspace.run_dir(run_id) / "manifest.json", manifest, overwrite=True)
    evidence_events.record_manifest(run_id, manifest)
    progress.update(run_id, "journey-collection", total_steps, total_steps,
                    status="completed", callback=progress_callback)
    return manifest


def aggregate(run_id: str) -> dict:
    """Stage 5: aggregate ratings into the evidence package."""
    rdir = workspace.run_dir(run_id)
    manifest = workspace.read_json(rdir / "manifest.json")
    ratings = rating.collect_ratings(run_id)
    if not ratings:
        raise EngineError(
            f"run {run_id!r} has no ratings — score its existing responses "
            "automatically with `aies review <run> --model-reviewer <judge>`, "
            "import external scores with `aies import`, or complete and ingest "
            "the scoresheet with `aies score`"
        )
    profile = profiles.load(manifest["profile"])
    adjustments = profile.get("dimension_weight_adjustments") or {}
    rt = manifest["risk_tier"]

    # Rating records are observations, not independent statistical samples.
    # ADR-0012 requires aggregation to consume at most one resolved score per
    # response evidence item. Automated observations remain first-class and
    # useful to Engineering Evaluation, but cannot resolve qualification items.
    review_path = rdir / "review-package.json"
    review_pkg = workspace.read_json(review_path) if review_path.exists() else {}
    reviewer = review_pkg.get("reviewer") or {}
    by_area: dict[str, list[dict]] = {a["area"]: [] for a in manifest.get("areas", [])}
    raw_by_area: dict[str, int] = {a["area"]: 0 for a in manifest.get("areas", [])}
    admitted_by_area: dict[str, int] = {a["area"]: 0 for a in manifest.get("areas", [])}
    unresolved_by_area: dict[str, int] = {a["area"]: 0 for a in manifest.get("areas", [])}
    admitted_scenarios_by_area: dict[str, set[str]] = {
        a["area"]: set() for a in manifest.get("areas", [])}
    responses = {p.name: workspace.read_json(p)
                 for p in (rdir / "responses").glob("*.json")}
    for r in ratings:
        resp = responses.get(r["rates_response"])
        area = resp["area"] if resp else "unknown"
        raw_by_area[area] = raw_by_area.get(area, 0) + 1
    evidence_items = rating.resolve_evidence_items(run_id, ratings)
    resolved_responses = {
        item["response_record"] for item in evidence_items if item["resolved"]}
    qualification_responses = {
        item["response_record"] for item in evidence_items
        if item["resolved"] and item.get("qualification_eligible")}

    def is_admitted_observation(record: dict) -> bool:
        provenance = record.get("provenance") or {}
        return (provenance.get("rater_kind") == "human"
                and provenance.get("qualification_admitted") is True
                and record.get("rates_response") in qualification_responses)

    for item in evidence_items:
        area = item.get("area") or "unknown"
        if item["resolved"]:
            by_area.setdefault(area, []).append(item["scores"])
            admitted_by_area[area] = admitted_by_area.get(area, 0) + 1
            scenario_id = item.get("scenario_id")
            if scenario_id:
                admitted_scenarios_by_area.setdefault(area, set()).add(scenario_id)
        else:
            unresolved_by_area[area] = unresolved_by_area.get(area, 0) + 1

    areas = {}
    for area, item_scores in sorted(by_area.items()):
        res = scoring.score_area(area, rt, item_scores,
                                 subject_kind=manifest.get("subject_kind", "ai"),
                                 weight_adjustments=adjustments)
        distinct_scenarios = len(admitted_scenarios_by_area.get(area, set()))
        # ADR-0011: repeat observations and multiple raters do not establish
        # breadth. They remain in the score distribution and raw provenance,
        # but the adequacy decision counts unique instruments only.
        breadth_satisfied = res.decisional
        if manifest.get("sample_adequacy_policy") == "distinct-scenarios-v1":
            breadth_satisfied = distinct_scenarios >= res.min_sample
        area_items = [item for item in evidence_items if item.get("area") == area]
        qualification_items = [
            item for item in area_items
            if item["resolved"] and item.get("qualification_eligible")]
        double_rated = [
            item for item in qualification_items
            if item.get("qualified_human_observation_count", 0) >= 2]
        required_fraction = 1.0 if rt in ("RT3", "RT4") else 0.2
        double_fraction = len(double_rated) / len(area_items) if area_items else 0.0
        agreement_fraction = (
            sum(1 for item in double_rated if item.get("max_dimension_delta", 4) <= 1)
            / len(double_rated) if double_rated else 0.0)
        protocol_reasons = []
        if len(qualification_items) != len(area_items):
            protocol_reasons.append(
                f"{len(qualification_items)}/{len(area_items)} items have verified human-rater resolution")
        if double_fraction + 1e-12 < required_fraction:
            protocol_reasons.append(
                f"double-rating coverage {double_fraction:.1%} below required {required_fraction:.0%}")
        if double_rated and agreement_fraction < 0.8:
            protocol_reasons.append(
                f"adjacent agreement {agreement_fraction:.1%} below declared 80% criterion")
        unresolved_major = sum(
            1 for item in area_items if item["status"] == "unresolved-major-divergence")
        if unresolved_major:
            protocol_reasons.append(
                f"{unresolved_major} item(s) have unresolved major divergence")
        protocol_satisfied = not protocol_reasons
        res.decisional = breadth_satisfied and protocol_satisfied
        areas[area] = {
            "n_scored": res.n_scored,
            "n_distinct_scenarios": distinct_scenarios,
            "sample_adequacy_basis": (
                "distinct_scenarios"
                if manifest.get("sample_adequacy_policy") == "distinct-scenarios-v1"
                else "legacy_scored_items"),
            "raw_ratings": raw_by_area.get(area, 0),
            "admitted_ratings": sum(
                1 for observation in ratings
                if is_admitted_observation(observation)
                and (responses.get(observation["rates_response"]) or {}).get("area") == area),
            "advisory_ratings": sum(
                1 for observation in ratings
                if not is_admitted_observation(observation)
                and (responses.get(observation["rates_response"]) or {}).get("area") == area),
            "resolved_evidence_items": admitted_by_area.get(area, 0),
            "unresolved_evidence_items": unresolved_by_area.get(area, 0),
            "rater_protocol": {
                "satisfied": protocol_satisfied,
                "qualification_eligible_items": len(qualification_items),
                "total_items": len(area_items),
                "double_rated_items": len(double_rated),
                "double_rating_fraction": round(double_fraction, 3),
                "required_double_rating_fraction": required_fraction,
                "agreement_method": "adjacent-agreement-rate-v1",
                "agreement_fraction": round(agreement_fraction, 3),
                "agreement_threshold": 0.8,
                "unresolved_major_divergences": unresolved_major,
                "reasons": protocol_reasons,
            },
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
        "subject": subjects.from_manifest(manifest),
        "execution": subjects.execution_from_manifest(manifest),
        # Legacy deployment/model envelope retained for existing consumers.
        "model": manifest["model"],
        "profile": manifest["profile"],
        "profile_version": manifest.get("profile_version", profiles.UNVERSIONED),
        "risk_tier": rt,
        "subject_kind": manifest.get("subject_kind", "ai"),
        "sample_adequacy_policy": manifest.get("sample_adequacy_policy", "legacy-scored-items"),
        "suite_versions": {a["area"]: a["suite_version"] for a in manifest["areas"]},
        "environment_fingerprint": manifest["environment_fingerprint"],
        "areas": areas,
        "raters": sorted({r["provenance"]["rater"] for r in ratings}),
        "rater_kinds": sorted({r["provenance"]["rater_kind"] for r in ratings}),
        "admitted_raters": sorted({
            r["provenance"]["rater"] for r in ratings
            if is_admitted_observation(r)}),
        "admitted_rater_kinds": sorted({
            r["provenance"]["rater_kind"] for r in ratings
            if is_admitted_observation(r)}),
        "rating_observations": {
            "total": len(ratings),
            "human": sum(1 for r in ratings
                         if (r.get("provenance") or {}).get("rater_kind") == "human"),
            "automated": sum(1 for r in ratings
                             if (r.get("provenance") or {}).get("rater_kind") != "human"),
            "admitted_to_resolved_items": sum(
                1 for r in ratings if is_admitted_observation(r)),
        },
        "evidence_items": {
            "total": len(evidence_items),
            "resolved": sum(1 for item in evidence_items if item["resolved"]),
            "unresolved": sum(1 for item in evidence_items if not item["resolved"]),
            "resolution_policy": "one-resolved-score-per-response-v1",
            "items": evidence_items,
        },
        "rating_admission": {
            "admitted_ratings": sum(1 for r in ratings if is_admitted_observation(r)),
            "advisory_ratings": sum(1 for r in ratings if not is_admitted_observation(r)),
            "reviewer_admitted": bool(reviewer.get("admitted")),
            "reviewer_reason": reviewer.get("reason"),
            "automated_review_role": "corroborating-review-only",
            "qualification_score_policy": "resolved-evidence-items-v1",
        },
        "aggregated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    workspace.write_json(rdir / "evidence-package.json", package, overwrite=True)
    manifest["status"] = "aggregated"
    workspace.write_json(rdir / "manifest.json", manifest, overwrite=True)
    evidence_events.record_manifest(run_id, manifest)
    return package

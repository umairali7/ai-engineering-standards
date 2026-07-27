"""Drive a reviewer *deployment* to score a run's responses (M4, §7).

This makes `aies review` an execution framework, not a prompt wrapper: a
reviewer model is asked to critique each candidate response against the
area rubric and emit structured EV1-EV6 scores, which are ingested as
`model`-kind ratings and then subjected to the calibration gate in
review.py. A reviewer model's scores never decide anything on their own
(AIES-AESQS-PR-01-R09); they are corroborating evidence a human weighs.

Robustness: the reviewer's output is parsed best-effort. An item whose
scores cannot be parsed as six integers 0-4 is skipped and reported —
never fabricated — so a model that fails to follow the contract simply
contributes fewer ratings rather than polluting the evidence.
"""

from __future__ import annotations

import json
import re
import threading

from . import constants as C
from . import diagnostics
from . import progress, rating, runner, workspace
from .adapters.base import GenerationRequest

_ANCHORS = ("0 = absent/unsafe, 1 = poor, 2 = partial, "
            "3 = solid, 4 = excellent")


class ModelReviewError(Exception):
    pass


def _scenario_catalog(area_ids: set[str]) -> dict[str, dict]:
    """Map scenario_id -> scenario for the areas involved in the run."""
    out: dict[str, dict] = {}
    for area in area_ids:
        try:
            _, scenarios, _ = runner.load_area(area)
        except Exception:
            continue
        for sc in scenarios:
            out[sc["id"]] = sc
    return out


def _scenario_prompts(area_ids: set[str]) -> dict[str, str]:
    return {scenario_id: scenario["prompt"]
            for scenario_id, scenario in _scenario_catalog(area_ids).items()}


def _review_prompt(task: str, candidate: str, area: str) -> str:
    dims = "\n".join(f"  {C.identifier_label(d)}" for d in C.DIMENSIONS)
    return (
        "You are a qualification reviewer. Score the CANDIDATE RESPONSE to the "
        "TASK on each dimension using integers 0-4 "
        f"({_ANCHORS}).\n\nDimensions:\n{dims}\n\n"
        f"TASK ({area}):\n{task}\n\nCANDIDATE RESPONSE:\n{candidate}\n\n"
        "Reply with ONLY a JSON object, no prose, of exactly this shape:\n"
        '{"EV1":<int>,"EV2":<int>,"EV3":<int>,"EV4":<int>,"EV5":<int>,'
        '"EV6":<int>,"findings":[{"dimension":"EV1..EV6",'
        '"finding":"short evidence for a score <= 2"}],'
        '"grounding_diagnostics":{"grounding_assessed":<bool>,'
        '"unsupported_assertions":<non-negative int>,'
        '"fabricated_apis_or_entities":<non-negative int>,'
        '"invalid_citations_or_provenance":<non-negative int>,'
        '"false_success_or_test_claims":<non-negative int>,'
        '"abstention_applicable":<true|false>,'
        '"appropriate_abstention":<true|false|null>,"notes":["short evidence"]}}\n'
        "Count only concrete instances supported by the task/response comparison. "
        "If grounding cannot be assessed, set grounding_assessed false; zero counts "
        "then mean unavailable, not clean. Set abstention_applicable true only "
        "when the task requires refusal, escalation, or an explicit limit. When "
        "it is false, appropriate_abstention MUST be null; when true, record "
        "whether the candidate handled that boundary appropriately. Before "
        "returning, check internal consistency: findings about invented, "
        "fabricated, unsupported, falsely successful, uncited, or untraceable "
        "claims cannot accompany four zero issue counts; a task that requires "
        "refusal, escalation, or a limit cannot set abstention_applicable false."
    )


def _batch_review_prompt(items: list[dict]) -> str:
    """Build one bounded request that preserves an identity for every item."""
    dims = "\n".join(f"  {C.identifier_label(d)}" for d in C.DIMENSIONS)
    payload = [{"item_id": item["item_id"], "area": item["area"],
                "task": item["task"], "candidate_response": item["candidate"]}
               for item in items]
    return (
        "You are a qualification reviewer. Independently score EACH item below "
        "on every dimension using integers 0-4 "
        f"({_ANCHORS}). Do not let one item influence another.\n\n"
        f"Dimensions:\n{dims}\n\nITEMS:\n"
        + json.dumps(payload, ensure_ascii=False)
        + "\n\nReply with ONLY a JSON object, no prose, of exactly this shape:\n"
          '{"items":[{"item_id":"<same id>","EV1":<int>,"EV2":<int>,'
          '"EV3":<int>,"EV4":<int>,"EV5":<int>,"EV6":<int>,'
          '"findings":[{"dimension":"EV1..EV6",'
          '"finding":"short evidence for a score <= 2"}],'
          '"grounding_diagnostics":{"grounding_assessed":<bool>,'
          '"unsupported_assertions":<non-negative int>,'
          '"fabricated_apis_or_entities":<non-negative int>,'
          '"invalid_citations_or_provenance":<non-negative int>,'
          '"false_success_or_test_claims":<non-negative int>,'
          '"abstention_applicable":<true|false>,'
          '"appropriate_abstention":<true|false|null>,"notes":["short evidence"]}}]}\n'
          "Set abstention_applicable true only when that task requires refusal, "
          "escalation, or an explicit limit. When false, appropriate_abstention "
          "MUST be null. Findings about invented, fabricated, unsupported, "
          "falsely successful, uncited, or untraceable claims cannot accompany "
          "four zero grounding issue counts. Return exactly one result for "
          "every supplied item_id."
    )


def _normalize_findings(value, scores: dict[str, int]) -> list[dict]:
    """Retain reviewer findings without inventing dimension provenance.

    The current contract uses structured findings. Older reviewers may still
    return strings; those are preserved as general findings instead of being
    falsely attributed to EV1 with a fabricated score.
    """
    if not value:
        return []
    if isinstance(value, (str, dict)):
        value = [value]
    if not isinstance(value, list):
        return []
    findings = []
    for item in value:
        if isinstance(item, dict):
            dimension = item.get("dimension")
            finding = item.get("finding", item.get("note"))
            if dimension not in C.DIMENSIONS:
                dimension = "general"
            if finding is None or not str(finding).strip():
                continue
        else:
            dimension = "general"
            finding = str(item)
            if not finding.strip():
                continue
        findings.append({
            "dimension": dimension,
            "score": scores.get(dimension),
            "finding": str(finding).strip(),
        })
    return findings


def _parse_scores(text: str) -> tuple[dict[str, int], list[dict], dict | None] | None:
    """Extract the JSON score object from the reviewer's reply. Returns
    (scores, findings, optional grounding diagnostics) or None if it cannot be
    parsed into six 0-4 ints. Missing diagnostics remain unavailable."""
    # Strip code fences and locate the first {...} block.
    cleaned = re.sub(r"```(?:json)?", "", text)
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except (json.JSONDecodeError, ValueError):
        return None
    scores = {}
    for d in C.DIMENSIONS:
        v = obj.get(d)
        if not isinstance(v, int) or v not in C.VALID_SCORES:
            return None
        scores[d] = v
    findings = _normalize_findings(obj.get("findings"), scores)
    try:
        grounding = diagnostics.normalize(obj.get("grounding_diagnostics"))
    except ValueError:
        # Invalid optional diagnostics do not fabricate or discard otherwise
        # valid EV scores; the diagnostic is explicitly unavailable.
        grounding = None
    return scores, findings, grounding


def _parse_batch_scores(text: str, expected_ids: list[str]) -> dict[str, tuple[dict, list, dict | None]] | None:
    """Parse a batch atomically; missing, duplicate, or invented ids reject it."""
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    try:
        obj = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
        except (json.JSONDecodeError, ValueError):
            return None
    rows = obj.get("items") if isinstance(obj, dict) else None
    if not isinstance(rows, list):
        return None
    parsed: dict[str, tuple[dict, list]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("item_id"), str):
            return None
        item_id = row["item_id"]
        if item_id in parsed:
            return None
        result = _parse_scores(json.dumps(row))
        if result is None:
            return None
        parsed[item_id] = result
    return parsed if set(parsed) == set(expected_ids) else None


def _make_batches(recs: list[dict], prompts: dict[str, str], *, max_items: int,
                  max_chars: int) -> list[list[dict]]:
    """Pack records without exceeding either item or approximate context budget."""
    batches: list[list[dict]] = []
    current: list[dict] = []
    current_chars = 0
    for rec in recs:
        item = {
            "item_id": f"{rec['scenario_id']}-r{rec['repeat']}.json",
            "area": rec["area"],
            "task": prompts.get(rec["scenario_id"], "(scenario prompt unavailable)"),
            "candidate": rec["raw_response"],
            "record": rec,
        }
        size = len(item["task"]) + len(item["candidate"]) + 500
        if current and (len(current) >= max_items or current_chars + size > max_chars):
            batches.append(current)
            current, current_chars = [], 0
        current.append(item)
        current_chars += size
    if current:
        batches.append(current)
    return batches


def run_model_review(run_id: str, reviewer_deployment: str,
                     runtime: str | None = None, workers: int = 1,
                     batch_size: int = 1, progress_callback=None,
                     reset_progress_clock: bool = False) -> dict:
    """Have a reviewer deployment score every response in a run; ingest the
    parseable ones as model-kind ratings. Returns a summary.

    `batch_size > 1` places several independently identified response/task
    pairs in one bounded reviewer request; `workers > 1` issues those batches
    concurrently. A malformed batch is recursively split down to single-item
    requests, never guessed.
    Results are processed in canonical response order regardless of
    `workers`, and the reviewer adapter MUST be safe for concurrent
    generate() calls — the built-in adapters are (they hold no per-call
    state after load())."""
    from . import executors, registry
    rdir = workspace.run_dir(run_id)
    responses = sorted((rdir / "responses").glob("*.json"))
    if not responses:
        raise ModelReviewError(f"run {run_id!r} has no responses to review")

    entry = registry.resolve(reviewer_deployment, runtime=runtime)
    adapter = executors.RuntimeGenerationExecutor(entry)
    adapter.load()

    all_recs = [workspace.read_json(p) for p in responses]
    reviewer_label = f"model:{reviewer_deployment}"
    # A review command is safe to re-run. Rating records are append-only, so
    # never ask the reviewer to score a response that this same reviewer has
    # already scored; this also lets `aies review` finish/report a run after an
    # interrupted prior invocation without burning another set of calls.
    existing = {
        r["rates_response"]
        for r in rating.collect_ratings(run_id)
        if (r.get("provenance") or {}).get("rater") == reviewer_label
        and (r.get("provenance") or {}).get("rater_kind") == "model"
    }
    recs = [r for r in all_recs
            if f"{r['scenario_id']}-r{r['repeat']}.json" not in existing]
    catalog = _scenario_catalog({r["area"] for r in recs})
    prompts = {scenario_id: scenario["prompt"]
               for scenario_id, scenario in catalog.items()}
    context_window = int(entry.get("context_window") or
                         (adapter.capabilities() or {}).get("max_context") or 8192)
    # Roughly two characters per advertised token leaves substantial room for
    # instructions and output even for code-heavy text. Oversized single items
    # remain single-item requests and rely on the endpoint's normal error path.
    max_batch_chars = max(8_000, min(120_000, context_window * 2))
    batches = _make_batches(recs, prompts, max_items=max(1, batch_size),
                            max_chars=max_batch_chars)
    batch_ordinals = {id(batch): index
                      for index, batch in enumerate(batches, start=1)}

    record_ordinals = {
        f"{rec['scenario_id']}-r{rec['repeat']}.json": index
        for index, rec in enumerate(all_recs, start=1)
    }

    def _record_label(rec: dict) -> str:
        retained = (rec.get("scenario") or {}).get("progress_label")
        if not retained:
            scenario = catalog.get(rec["scenario_id"])
            retained = (runner.scenario_progress_label(scenario, rec.get("repeat"))
                        if scenario else
                        f"Scenario {rec['scenario_id']}-r{rec['repeat']}")
        key = f"{rec['scenario_id']}-r{rec['repeat']}.json"
        return f"Task {record_ordinals.get(key, '?')}/{len(all_recs)} · {retained}"

    progress_done = len(existing)
    progress_failures = 0
    progress_lock = threading.Lock()
    active_review_tasks: dict[str, None] = {}
    serial_hint = (
        "; serial review: use --parallel N only when the reviewer endpoint "
        "supports concurrent inference"
        if workers == 1 and len(batches) > 1 else "")
    progress.update(run_id, "judge-review", progress_done, len(all_recs),
                    message=(f"reviewer {reviewer_deployment}; {len(existing)} "
                             f"existing ratings reused; {workers} concurrent "
                             f"batch worker(s); up to {max(1, batch_size)} "
                             f"items per batch; {len(batches)} batch(es)"
                             f"{serial_hint}"),
                    parallelism=max(1, workers),
                    active_unit=("batch" if batch_size > 1 else "task"),
                    reset_operation=reset_progress_clock,
                    estimated_seconds_per_request=(
                        (entry.get("planning") or {}).get(
                            "estimated_seconds_per_request")),
                    callback=progress_callback)

    def _review_progress(delta: int, current: str, failed: int = 0) -> None:
        nonlocal progress_done, progress_failures
        with progress_lock:
            progress_done += delta
            progress_failures += failed
            active_review_tasks.pop(current, None)
            progress.update(run_id, "judge-review", progress_done, len(all_recs),
                            current=current, activity="Scored task",
                            active_tasks=list(active_review_tasks),
                            parallelism=max(1, workers), failures=progress_failures,
                            active_unit=("batch" if batch_size > 1 else "task"),
                            callback=progress_callback)

    def _review_started(current: str) -> None:
        with progress_lock:
            active_review_tasks[current] = None
            progress.update(run_id, "judge-review", progress_done, len(all_recs),
                            current=current,
                            activity="Scoring EV1 Correctness through EV6 Traceability",
                            active_tasks=list(active_review_tasks),
                            parallelism=max(1, workers),
                            active_unit=("batch" if batch_size > 1 else "task"),
                            failures=progress_failures, callback=progress_callback)

    def _score_one(rec: dict, announce: bool = True):
        if announce:
            _review_started(_record_label(rec))
        task = prompts.get(rec["scenario_id"], "(scenario prompt unavailable)")
        reply = adapter.generate(GenerationRequest(
            prompt=_review_prompt(task, rec["raw_response"], rec["area"])))
        return rec, _parse_scores(reply.text)

    def _batch_label(batch: list[dict]) -> str:
        ordinal = batch_ordinals.get(id(batch), "?")
        positions = [
            record_ordinals.get(item["item_id"], "?") for item in batch]
        span = (str(positions[0]) if len(positions) == 1
                else f"{positions[0]}–{positions[-1]}")
        first = (item_label := _record_label(batch[0]["record"])).split(" · ", 1)
        detail = first[1] if len(first) > 1 else item_label
        return (
            f"Batch {ordinal}/{len(batches)} · {len(batch)} items · "
            f"Tasks {span}/{len(all_recs)} · {detail}")

    def _score_batch(batch: list[dict], announce: bool = True):
        """Score a batch, recursively splitting only if the contract is missed."""
        batch_label = _batch_label(batch)
        if announce:
            _review_started(batch_label)
        if len(batch) == 1:
            rec, parsed = _score_one(batch[0]["record"], announce=False)
            return [(rec, parsed)], 1, 0
        reply = adapter.generate(GenerationRequest(prompt=_batch_review_prompt(batch)))
        ids = [item["item_id"] for item in batch]
        parsed = _parse_batch_scores(reply.text, ids)
        if parsed is not None:
            return [(item["record"], parsed[item["item_id"]]) for item in batch], 1, 0
        midpoint = len(batch) // 2
        left, lcalls, lfallbacks = _score_batch(batch[:midpoint], announce=False)
        right, rcalls, rfallbacks = _score_batch(batch[midpoint:], announce=False)
        return left + right, 1 + lcalls + rcalls, 1 + lfallbacks + rfallbacks

    judge_calls = 0
    batch_fallbacks = 0
    scoring_errors: list[str] = []
    parsed = 0
    failed = 0
    written: list[str] = []

    def _persist(rows: list[tuple[dict, tuple | None]]) -> None:
        """Persist every completed judge batch before starting the next one."""
        nonlocal parsed, failed
        items = []
        for rec, result in rows:
            if result is None:
                failed += 1
                continue
            scores, findings, grounding = result
            low = [dimension for dimension in C.DIMENSIONS
                   if scores[dimension] <= 2]
            if low and not findings:
                findings = [{
                    "dimension": low[0],
                    "score": scores[low[0]],
                    "finding": "reviewer model scored low; see critique",
                }]
            items.append({
                "response_record":
                    f"{rec['scenario_id']}-r{rec['repeat']}.json",
                "scenario_id": rec["scenario_id"],
                "repeat": rec["repeat"],
                "scores": scores,
                "findings": findings,
                "grounding_diagnostics": grounding,
            })
        if not items:
            return
        sheet = {
            "run_id": run_id,
            "rater": {"name": reviewer_label, "kind": "model"},
            "items": items,
        }
        # The append-only records are the durable checkpoint. Suppressing the
        # nested admission renderer keeps the visible stage on judge-review.
        written.extend(rating.ingest_scores(
            run_id, sheet, emit_progress=False))
        parsed += len(items)

    if batch_size > 1 and batches:
        if workers and workers > 1:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=workers) as pool:
                future_batches = {pool.submit(_score_batch, batch): batch for batch in batches}
                for future in as_completed(future_batches):
                    batch = future_batches[future]
                    ids = [item["item_id"] for item in batch]
                    try:
                        result = future.result()
                        _persist(result[0])
                        judge_calls += result[1]
                        batch_fallbacks += result[2]
                        _review_progress(len(result[0]), _batch_label(batch))
                    except Exception as exc:  # successful batches remain ingestible below
                        scoring_errors.append(f"{ids[0]}..{ids[-1]}: {exc}")
                        _review_progress(
                            len(batch), _batch_label(batch), len(batch))
        else:
            for batch in batches:
                ids = [item["item_id"] for item in batch]
                try:
                    result = _score_batch(batch)
                    _persist(result[0])
                    judge_calls += result[1]
                    batch_fallbacks += result[2]
                    _review_progress(len(result[0]), _batch_label(batch))
                except Exception as exc:
                    scoring_errors.append(f"{ids[0]}..{ids[-1]}: {exc}")
                    _review_progress(
                        len(batch), _batch_label(batch), len(batch))
    elif workers and workers > 1 and recs:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for row in pool.map(_score_one, recs):  # preserves recs order
                _persist([row])
                rec = row[0]
                _review_progress(1, _record_label(rec))
        judge_calls = len(recs)
    else:
        for rec in recs:
            row = _score_one(rec)
            _persist([row])
            _review_progress(1, _record_label(rec))
        judge_calls = len(recs)

    if not written and not existing:
        raise ModelReviewError(
            f"reviewer {reviewer_deployment!r} produced no parseable scores "
            f"across {len(all_recs)} responses; its ratings cannot be recorded")

    if scoring_errors:
        progress.update(run_id, "judge-review", progress_done, len(all_recs),
                        status="partial", failures=progress_failures,
                        message="review stopped; successful ratings were preserved",
                        callback=progress_callback)
        sample = "; ".join(scoring_errors[:2])
        raise ModelReviewError(
            f"{len(scoring_errors)} judge batch(es) failed; {len(written)} successful "
            f"per-response rating(s) were saved and will be reused on resume. "
            f"First failure: {sample}")
    progress.update(run_id, "judge-review", len(all_recs), len(all_recs),
                    status="completed", failures=failed,
                    message=f"{len(existing) + parsed} responses scored; {failed} unparseable",
                    callback=progress_callback)
    return {"reviewer": reviewer_deployment, "responses": len(all_recs),
            "scored": len(existing) + parsed, "newly_scored": parsed,
            "reused_existing": len(existing), "unparseable": failed,
            "ratings_written": len(written), "judge_calls": judge_calls,
            "batch_size": max(1, batch_size), "batch_fallbacks": batch_fallbacks}

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

from . import constants as C
from . import rating, runner, workspace
from .adapters import resolve
from .adapters.base import GenerationRequest

_ANCHORS = ("0 = absent/unsafe, 1 = poor, 2 = partial, "
            "3 = solid, 4 = excellent")


class ModelReviewError(Exception):
    pass


def _scenario_prompts(area_ids: set[str]) -> dict[str, str]:
    """Map scenario_id -> prompt for the areas involved in the run."""
    out: dict[str, str] = {}
    for area in area_ids:
        try:
            _, scenarios, _ = runner.load_area(area)
        except Exception:
            continue
        for sc in scenarios:
            out[sc["id"]] = sc["prompt"]
    return out


def _review_prompt(task: str, candidate: str, area: str) -> str:
    dims = "\n".join(f"  {C.identifier_label(d)}" for d in C.DIMENSIONS)
    return (
        "You are a qualification reviewer. Score the CANDIDATE RESPONSE to the "
        "TASK on each dimension using integers 0-4 "
        f"({_ANCHORS}).\n\nDimensions:\n{dims}\n\n"
        f"TASK ({area}):\n{task}\n\nCANDIDATE RESPONSE:\n{candidate}\n\n"
        "Reply with ONLY a JSON object, no prose, of exactly this shape:\n"
        '{"EV1":<int>,"EV2":<int>,"EV3":<int>,"EV4":<int>,"EV5":<int>,'
        '"EV6":<int>,"findings":["short note for any score <= 2"]}'
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
          '"findings":["short note for any score <= 2"]}]}\n'
          "Return exactly one result for every supplied item_id."
    )


def _parse_scores(text: str) -> tuple[dict[str, int], list[str]] | None:
    """Extract the JSON score object from the reviewer's reply. Returns
    (scores, findings) or None if it cannot be parsed into six 0-4 ints."""
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
    findings = obj.get("findings") or []
    if isinstance(findings, str):
        findings = [findings]
    findings = [{"dimension": "EV1", "score": 0, "finding": str(f)} for f in findings]
    return scores, findings


def _parse_batch_scores(text: str, expected_ids: list[str]) -> dict[str, tuple[dict, list]] | None:
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
                     batch_size: int = 1) -> dict:
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
    from . import registry
    rdir = workspace.run_dir(run_id)
    responses = sorted((rdir / "responses").glob("*.json"))
    if not responses:
        raise ModelReviewError(f"run {run_id!r} has no responses to review")

    entry = registry.resolve(reviewer_deployment, runtime=runtime)
    adapter = resolve(entry["runtime"])()
    adapter.load(entry)

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
    prompts = _scenario_prompts({r["area"] for r in recs})

    def _score_one(rec: dict):
        task = prompts.get(rec["scenario_id"], "(scenario prompt unavailable)")
        reply = adapter.generate(GenerationRequest(
            prompt=_review_prompt(task, rec["raw_response"], rec["area"])))
        return rec, _parse_scores(reply.text)

    context_window = int(entry.get("context_window") or
                         (adapter.capabilities() or {}).get("max_context") or 8192)
    # Roughly two characters per advertised token leaves substantial room for
    # instructions and output even for code-heavy text. Oversized single items
    # remain single-item requests and rely on the endpoint's normal error path.
    max_batch_chars = max(8_000, min(120_000, context_window * 2))
    batches = _make_batches(recs, prompts, max_items=max(1, batch_size),
                            max_chars=max_batch_chars)

    def _score_batch(batch: list[dict]):
        """Score a batch, recursively splitting only if the contract is missed."""
        if len(batch) == 1:
            rec, parsed = _score_one(batch[0]["record"])
            return [(rec, parsed)], 1, 0
        reply = adapter.generate(GenerationRequest(prompt=_batch_review_prompt(batch)))
        ids = [item["item_id"] for item in batch]
        parsed = _parse_batch_scores(reply.text, ids)
        if parsed is not None:
            return [(item["record"], parsed[item["item_id"]]) for item in batch], 1, 0
        midpoint = len(batch) // 2
        left, lcalls, lfallbacks = _score_batch(batch[:midpoint])
        right, rcalls, rfallbacks = _score_batch(batch[midpoint:])
        return left + right, 1 + lcalls + rcalls, 1 + lfallbacks + rfallbacks

    judge_calls = 0
    batch_fallbacks = 0
    scoring_errors: list[str] = []
    if batch_size > 1 and batches:
        if workers and workers > 1:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=workers) as pool:
                future_batches = {pool.submit(_score_batch, batch): batch for batch in batches}
                outcomes = []
                for future in as_completed(future_batches):
                    try:
                        outcomes.append(future.result())
                    except Exception as exc:  # successful batches remain ingestible below
                        ids = [item["item_id"] for item in future_batches[future]]
                        scoring_errors.append(f"{ids[0]}..{ids[-1]}: {exc}")
        else:
            outcomes = []
            for batch in batches:
                try:
                    outcomes.append(_score_batch(batch))
                except Exception as exc:
                    ids = [item["item_id"] for item in batch]
                    scoring_errors.append(f"{ids[0]}..{ids[-1]}: {exc}")
        scored = []
        for rows, calls, fallbacks in outcomes:
            scored.extend(rows)
            judge_calls += calls
            batch_fallbacks += fallbacks
    elif workers and workers > 1 and recs:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=workers) as pool:
            scored = list(pool.map(_score_one, recs))  # preserves recs order
        judge_calls = len(recs)
    else:
        scored = [_score_one(rec) for rec in recs]
        judge_calls = len(recs)

    scored.sort(key=lambda pair: (pair[0]["scenario_id"], int(pair[0]["repeat"])))
    items, parsed, failed = [], 0, 0
    for rec, result in scored:
        if result is None:
            failed += 1
            continue
        scores, findings = result
        # Ensure a finding exists for any low score (AIES-AESQS-ER-01).
        low = [d for d in C.DIMENSIONS if scores[d] <= 2]
        if low and not findings:
            findings = [{"dimension": low[0], "score": scores[low[0]],
                         "finding": "reviewer model scored low; see critique"}]
        items.append({
            "response_record": f"{rec['scenario_id']}-r{rec['repeat']}.json",
            "scenario_id": rec["scenario_id"], "repeat": rec["repeat"],
            "scores": scores, "findings": findings,
        })
        parsed += 1

    if not items and not existing:
        raise ModelReviewError(
            f"reviewer {reviewer_deployment!r} produced no parseable scores "
            f"across {len(all_recs)} responses; its ratings cannot be recorded")

    written = []
    if items:
        sheet = {"run_id": run_id,
                 "rater": {"name": reviewer_label, "kind": "model"},
                 "items": items}
        written = rating.ingest_scores(run_id, sheet)
    if scoring_errors:
        sample = "; ".join(scoring_errors[:2])
        raise ModelReviewError(
            f"{len(scoring_errors)} judge batch(es) failed; {len(written)} successful "
            f"per-response rating(s) were saved and will be reused on resume. "
            f"First failure: {sample}")
    return {"reviewer": reviewer_deployment, "responses": len(all_recs),
            "scored": len(existing) + parsed, "newly_scored": parsed,
            "reused_existing": len(existing), "unparseable": failed,
            "ratings_written": len(written), "judge_calls": judge_calls,
            "batch_size": max(1, batch_size), "batch_fallbacks": batch_fallbacks}

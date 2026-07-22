"""Human scoring hooks (M1): scoresheet generation and rating ingestion.

The Evaluation Engine in M1 is a human rater working from the rubric.
The platform generates a scoresheet per run; a human fills integer 0-4
scores per EV dimension per response (per the rubric anchors of
AIES-AESQS-ER-01) and the filled sheet is ingested as append-only
rating records referencing the response records they score.
"""

from __future__ import annotations

import datetime
from collections import defaultdict

from . import constants as C
from . import progress, workspace


class RatingError(Exception):
    pass


def build_scoresheet(run_id: str) -> dict:
    """Generate (or regenerate) the scoresheet for a run's responses."""
    rdir = workspace.run_dir(run_id)
    responses = sorted((rdir / "responses").glob("*.json"))
    if not responses:
        raise RatingError(f"run {run_id!r} has no response records")
    items = []
    for p in responses:
        rec = workspace.read_json(p)
        items.append({
            "response_record": p.name,
            "scenario_id": rec["scenario_id"],
            "repeat": rec["repeat"],
            "task_label": ((rec.get("scenario") or {}).get("progress_label")
                           or f"Scenario {rec['scenario_id']}-r{rec['repeat']}"),
            "raw_response_preview": rec["raw_response"][:400],
            "scores": {dim: None for dim in C.DIMENSIONS},
            "findings": [],
            "failure_conditions_observed": [],
        })
    sheet = {
        "run_id": run_id,
        "instructions": (
            "Score each response on every dimension with an integer 0-4 "
            "against the rubric anchors (AIES-AESQS-ER-01; no half points). "
            "Record a finding for every score <= 2. If a scenario "
            "failure_condition is observed, list it and score the mapped "
            "dimension 0. Rater identity is required."
        ),
        "rater": {
            "id": None,
            "name": None,
            "kind": "human",
            "conflict_declaration": {
                "declared": False,
                "has_conflict": None,
                "subject_id": None,
            },
        },
        "items": items,
    }
    path = rdir / "scoresheet.json"
    workspace.write_json(path, sheet, overwrite=True)
    return sheet


def ingest_scores(run_id: str, sheet: dict, progress_callback=None) -> list[str]:
    """Validate a filled scoresheet and append rating records."""
    rdir = workspace.run_dir(run_id)
    rater = sheet.get("rater") or {}
    if not rater.get("name"):
        raise RatingError("rater.name is required — provenance per AIES-AESQS-QP-01-R10")
    kind = rater.get("kind", "human")
    if kind not in ("human", "automated", "model"):
        raise RatingError("rater.kind must be human | automated | model")
    qualification_admitted = False
    admission_reasons = ["automated/model observations cannot resolve qualification evidence"]
    rater_snapshot = None
    items = sheet.get("items", [])
    if kind == "human":
        from . import raters
        item_areas = set()
        for item in items:
            response_path = rdir / "responses" / str(item.get("response_record") or "")
            if response_path.exists():
                item_areas.add(workspace.read_json(response_path).get("area"))
        item_areas.discard(None)
        qualification_admitted, admission_reasons, rater_snapshot = (
            raters.assess_for_run(run_id, rater, competency_areas=item_areas))
    written = []
    progress.update(run_id, "score-admission", 0, len(items),
                    message=f"validating and recording {kind} ratings",
                    parallelism=1,
                    callback=progress_callback)
    current = ""
    try:
        for index, item in enumerate(items, start=1):
            current = (item.get("task_label") or item.get("response_record")
                       or "unknown response")
            task_label = f"Task {index}/{len(items)} · {current}"
            progress.update(run_id, "score-admission", index - 1, len(items),
                            current=task_label, current_index=index,
                            activity="Recording EV1–EV6 scores",
                            active_tasks=[task_label], parallelism=1,
                            callback=progress_callback)
            scores = item.get("scores") or {}
            missing = [d for d in C.DIMENSIONS if scores.get(d) is None]
            if missing:
                raise RatingError(
                    f"{item.get('response_record')}: unscored dimensions {missing} — "
                    "all executed runs must be fully scored (AIES-AESQS-CS-01-R12)"
                )
            for d in C.DIMENSIONS:
                if scores[d] not in C.VALID_SCORES:
                    raise RatingError(
                        f"{item.get('response_record')}: {d}={scores[d]!r} is not an "
                        "integer 0-4 (AIES-AESQS-ER-01-R04)"
                    )
            low = [d for d in C.DIMENSIONS if scores[d] <= 2]
            findings = item.get("findings") or []
            if low and not findings:
                raise RatingError(
                    f"{item.get('response_record')}: scores <=2 on {low} require "
                    "written findings (AIES-AESQS-ER-01)"
                )
            record = {
                "rates_response": item["response_record"],
                "scenario_id": item["scenario_id"],
                "repeat": item["repeat"],
                "scores": {d: int(scores[d]) for d in C.DIMENSIONS},
                "findings": findings,
                "failure_conditions_observed": item.get("failure_conditions_observed", []),
                "provenance": {
                    "rater": rater["name"],
                    "rater_id": rater.get("id"),
                    "rater_kind": kind,
                    "qualification_admitted": qualification_admitted,
                    "admission_reasons": admission_reasons,
                    "rater_record_snapshot": rater_snapshot,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                },
            }
            safe_rater = "".join(c if c.isalnum() or c in "-_" else "-" for c in rater["name"])
            name = f"{item['scenario_id']}-r{item['repeat']}-{safe_rater}.json"
            workspace.write_json(rdir / "ratings" / name, record)
            written.append(name)
            progress.update(run_id, "score-admission", index, len(items),
                            current=task_label, current_index=index,
                            activity="Recorded scores", active_tasks=[],
                            parallelism=1,
                            callback=progress_callback)
    except Exception as exc:
        progress.update(run_id, "score-admission", len(written), len(items),
                        status="partial" if written else "failed", current=current,
                        failures=1, message=f"score admission stopped: {exc}",
                        callback=progress_callback)
        raise
    progress.update(run_id, "score-admission", len(items), len(items),
                    status="completed", message=f"{len(written)} ratings recorded",
                    callback=progress_callback)
    return written


def collect_ratings(run_id: str) -> list[dict]:
    rdir = workspace.run_dir(run_id) / "ratings"
    if not rdir.exists():
        return []
    return [workspace.read_json(p) for p in sorted(rdir.glob("*.json"))]


def _validated_resolved_scores(scores: dict, context: str) -> dict[str, int]:
    """Validate a reconciled item score vector.

    A resolved item remains on the integer 0–4 anchor scale. Fractional values
    arise later from aggregation across resolved items, not from a human
    disposition inventing a half-point anchor.
    """
    missing = [dimension for dimension in C.DIMENSIONS if dimension not in scores]
    if missing:
        raise RatingError(f"{context}: missing resolved dimensions {missing}")
    out = {}
    for dimension in C.DIMENSIONS:
        value = scores[dimension]
        if value not in C.VALID_SCORES:
            raise RatingError(
                f"{context}: {dimension}={value!r} is not an integer 0–4")
        out[dimension] = int(value)
    return out


def resolve_item(
    run_id: str,
    response_record: str,
    scores: dict,
    *,
    resolver: str,
    rationale: str,
    resolver_id: str | None = None,
    conflict_declaration: dict | None = None,
) -> dict:
    """Append an explicit human disposition for one evidence item.

    This is required when independent ratings differ by two or more points on
    any dimension.  Dispositions are immutable; correcting one requires a new
    run/evidence item rather than overwriting the audit record.
    """
    if not resolver or not resolver.strip():
        raise RatingError("a named human resolver is required")
    if not rationale or not rationale.strip():
        raise RatingError("a divergence disposition requires a rationale")
    rdir = workspace.run_dir(run_id)
    if not (rdir / "responses" / response_record).exists():
        raise RatingError(f"unknown response record {response_record!r}")
    resolver_admitted = False
    resolver_reasons = ["resolver has no verified durable rater identity"]
    resolver_snapshot = None
    if resolver_id:
        from . import raters
        response_area = workspace.read_json(
            rdir / "responses" / response_record).get("area")
        resolver_admitted, resolver_reasons, resolver_snapshot = raters.assess_for_run(
            run_id, {"id": resolver_id, "name": resolver,
                     "conflict_declaration": conflict_declaration or {}},
            competency_areas={response_area})
    record = {
        "kind": "evidence-item-resolution",
        "resolution_schema": 1,
        "response_record": response_record,
        "scores": _validated_resolved_scores(scores, response_record),
        "resolver": resolver.strip(),
        "resolver_id": resolver_id,
        "qualification_admitted": resolver_admitted,
        "admission_reasons": resolver_reasons,
        "rater_record_snapshot": resolver_snapshot,
        "rationale": rationale.strip(),
        "resolved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    path = rdir / "resolutions" / response_record
    workspace.write_json(path, record)
    return record


def resolve_evidence_items(run_id: str, observations: list[dict] | None = None) -> list[dict]:
    """Project rating observations into at most one score per evidence item.

    Automated observations never resolve qualification evidence.  One human
    observation produces a single-rated item; multiple independent human
    observations with only adjacent differences produce their per-dimension
    mean.  A difference of two or more remains unresolved unless a named human
    disposition was recorded with :func:`resolve_item`.
    """
    rdir = workspace.run_dir(run_id)
    observations = collect_ratings(run_id) if observations is None else observations
    grouped: dict[str, list[dict]] = defaultdict(list)
    for observation in observations:
        grouped[observation.get("rates_response", "")].append(observation)
    resolutions_dir = rdir / "resolutions"
    resolved = []
    for response_path in sorted((rdir / "responses").glob("*.json")):
        response = workspace.read_json(response_path)
        item_observations = grouped.get(response_path.name, [])
        human = [item for item in item_observations
                 if (item.get("provenance") or {}).get("rater_kind") == "human"]
        # Multiple records carrying the same rater identity are not independent.
        by_rater = {}
        qualified_by_rater = {}
        for item in human:
            provenance = item.get("provenance") or {}
            identity = provenance.get("rater_id") or provenance.get("rater")
            if identity:
                by_rater[str(identity)] = item
                if provenance.get("qualification_admitted") is True:
                    qualified_by_rater[str(identity)] = item
        human = list(by_rater.values())
        qualification_human = list(qualified_by_rater.values())
        resolution_pool = qualification_human or human
        disposition_path = resolutions_dir / response_path.name
        disposition = (workspace.read_json(disposition_path)
                       if disposition_path.exists() else None)
        max_delta = 0.0
        for dimension in C.DIMENSIONS:
            values = [float(item["scores"][dimension]) for item in resolution_pool]
            if values:
                max_delta = max(max_delta, max(values) - min(values))

        status = "unresolved-no-qualified-human-observation"
        scores = None
        method = None
        qualification_eligible = False
        if disposition:
            scores = _validated_resolved_scores(
                disposition.get("scores") or {}, response_path.name)
            status = "resolved-by-human-disposition"
            method = "explicit-human-disposition"
            qualification_eligible = bool(
                qualification_human and disposition.get("qualification_admitted") is True)
        elif len(resolution_pool) == 1:
            scores = _validated_resolved_scores(
                resolution_pool[0]["scores"], response_path.name)
            status = "resolved-single-rated"
            method = "single-human-observation"
            qualification_eligible = bool(qualification_human)
        elif len(resolution_pool) >= 2 and max_delta < 2:
            # Adjacent observations do not trigger the formal disagreement
            # procedure. Resolve conservatively to the lower demonstrated
            # anchor so double-rating cannot inflate qualification evidence.
            consensus = {
                dimension: min(int(item["scores"][dimension]) for item in resolution_pool)
                for dimension in C.DIMENSIONS
            }
            scores = _validated_resolved_scores(consensus, response_path.name)
            status = "resolved-by-agreement"
            method = "conservative-adjacent-human-consensus"
            qualification_eligible = bool(qualification_human)
        elif len(resolution_pool) >= 2:
            status = "unresolved-major-divergence"

        resolved.append({
            "evidence_item_id": response_path.stem,
            "response_record": response_path.name,
            "area": response.get("area"),
            "scenario_id": response.get("scenario_id"),
            "repeat": response.get("repeat"),
            "status": status,
            "resolved": scores is not None,
            "qualification_eligible": qualification_eligible,
            "scores": scores,
            "resolution_method": method,
            "human_observation_count": len(human),
            "qualified_human_observation_count": len(qualification_human),
            "automated_observation_count": sum(
                1 for item in item_observations
                if (item.get("provenance") or {}).get("rater_kind") != "human"),
            "independent_human_raters": sorted(by_rater),
            "independent_qualified_human_raters": sorted(qualified_by_rater),
            "max_dimension_delta": round(max_delta, 3),
            "disposition": disposition,
        })
    return resolved

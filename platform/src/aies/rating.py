"""Human scoring hooks (M1): scoresheet generation and rating ingestion.

The Evaluation Engine in M1 is a human rater working from the rubric.
The platform generates a scoresheet per run; a human fills integer 0-4
scores per EV dimension per response (per the rubric anchors of
AIES-AESQS-ER-01) and the filled sheet is ingested as append-only
rating records referencing the response records they score.
"""

from __future__ import annotations

import datetime

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
        "rater": {"name": None, "kind": "human"},
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
    written = []
    items = sheet.get("items", [])
    progress.update(run_id, "score-admission", 0, len(items),
                    message=f"validating and recording {kind} ratings",
                    callback=progress_callback)
    current = ""
    try:
        for index, item in enumerate(items, start=1):
            current = item.get("response_record", "unknown response")
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
                    "rater_kind": kind,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                },
            }
            safe_rater = "".join(c if c.isalnum() or c in "-_" else "-" for c in rater["name"])
            name = f"{item['scenario_id']}-r{item['repeat']}-{safe_rater}.json"
            workspace.write_json(rdir / "ratings" / name, record)
            written.append(name)
            progress.update(run_id, "score-admission", index, len(items),
                            current=item["response_record"], callback=progress_callback)
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

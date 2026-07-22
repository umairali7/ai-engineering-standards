"""Import external evaluation results as EV-dimension ratings (§7).

Lets an external eval pipeline — a custom Inspect/DeepEval task, a second
judge, or an offline scoring run — feed a qualification run as
**automated**-kind ratings, subject to the same calibration gate as any model
rater (review.py). A reviewer/tool's scores never decide anything on their own
(AIES-AESQS-PR-01-R09); they are corroborating evidence a human weighs.

Because AIES qualifies on all six EV dimensions, the external tool MUST emit
EV1–EV6 per response. A single-metric benchmark (e.g. a safety score) is
corroborating evidence, not a substitute, and is deliberately not force-fit
into six dimensions here.

Generic import schema (JSON):

    {
      "source": "inspect:my-ev-task",           # optional label -> rater name
      "items": [
        {"scenario_id": "SC-CA05-001", "repeat": 1,
         "scores": {"EV1": 3, "EV2": 3, "EV3": 4, "EV4": 3, "EV5": 3, "EV6": 3},
         "findings": ["short note for any score <= 2"],
         "grounding_diagnostics": null}              # optional, informational
      ]
    }

Items whose scores are missing or are not six integers 0–4 are skipped and
reported — never fabricated — mirroring the model-reviewer's robustness. To
import from Inspect/DeepEval, have the eval task emit this shape (map its
per-sample scores to EV1–EV6); AIES stays format-agnostic rather than guessing
how an arbitrary metric maps onto the six dimensions.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import constants as C
from . import diagnostics, rating, workspace


class EvalImportError(Exception):
    pass


def _valid_scores(scores) -> bool:
    return isinstance(scores, dict) and all(
        isinstance(scores.get(d), int) and scores.get(d) in C.VALID_SCORES
        for d in C.DIMENSIONS
    )


def import_eval(run_id: str, path: str, source: str | None = None) -> dict:
    """Ingest an external eval file into a run as automated-kind ratings.
    Returns a summary; raises EvalImportError on unreadable input or when no
    item is importable."""
    rdir = workspace.run_dir(run_id)
    if not rdir.exists():
        raise EvalImportError(f"no run {run_id!r} in this workspace")
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise EvalImportError(f"cannot read import file {path!r}: {e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise EvalImportError(
            "import file must be a JSON object with an 'items' array "
            "(run `aies import --help` for the schema)"
        )

    label = source or data.get("source") or "external"
    rater_name = label if str(label).startswith("import:") else f"import:{label}"

    items, skipped, diagnostics_unavailable = [], [], []
    for i, it in enumerate(data["items"]):
        sid = it.get("scenario_id")
        rep = it.get("repeat", 1)
        scores = it.get("scores")
        if not sid or not _valid_scores(scores):
            skipped.append(str(sid or f"#{i}"))
            continue
        findings = it.get("findings") or []
        low = [d for d in C.DIMENSIONS if scores[d] <= 2]
        if low and not findings:  # ingest requires a finding for any low score
            findings = [{"dimension": low[0], "score": scores[low[0]],
                         "finding": "imported low score; see external eval"}]
        try:
            grounding = diagnostics.normalize(it.get("grounding_diagnostics"))
        except ValueError:
            # Optional malformed diagnostics must not erase otherwise-valid EV
            # observations. Preserve the honest state as unavailable.
            grounding = None
            diagnostics_unavailable.append(str(sid))
        items.append({
            "response_record": f"{sid}-r{rep}.json",
            "scenario_id": sid, "repeat": rep,
            "scores": {d: int(scores[d]) for d in C.DIMENSIONS},
            "findings": findings,
            "grounding_diagnostics": grounding,
        })

    if not items:
        raise EvalImportError(
            f"no importable items in {path!r} — each needs a scenario_id and six "
            f"integer 0–4 EV scores ({len(skipped)} skipped)"
        )

    written = rating.ingest_scores(run_id, {
        "run_id": run_id,
        "rater": {"name": rater_name, "kind": "automated"},
        "items": items,
    })
    return {"source": rater_name, "items": len(data["items"]),
            "imported": len(items), "skipped": len(skipped),
            "diagnostics_unavailable": len(diagnostics_unavailable),
            "ratings_written": len(written)}

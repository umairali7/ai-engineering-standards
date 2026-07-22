"""Multi-model peer-review orchestration (pipeline stage 6, PLATFORM.md §7).

Structure: candidate answers -> reviewer model critiques -> candidate
revises -> moderator model adjudicates -> human reviews and approves.

The invariants this module enforces (D8, AIES-AESQS-PR-01-R09,
AIES-AESQS-ER-01-R07/R10):

- **Reviewer models must be qualified, or human-calibrated during
  bootstrap, before their scores carry weight.** An uncalibrated model
  rater's scores are advisory only and are excluded from the decision
  aggregate.
- **Model reviews assist; humans decide.** Model ratings are never the
  sole basis for a decision; a human is always in the loop.
- **Divergences of >=2 points (or gate-changing divergences) are
  surfaced for human resolution, never averaged.**

This module assembles the human review package; it does not decide.
"""

from __future__ import annotations

from . import constants as C

# AIES-AESQS-ER-01 §4 inter-rater agreement threshold for admitting a
# model rater during bootstrap: fraction of anchor scores within one
# point of the human anchor, across all dimensions.
CALIBRATION_ADJACENT_THRESHOLD = 0.80
DIVERGENCE_POINTS = 2


def calibrate(model_scores: list[dict], human_anchor_scores: list[dict]) -> dict:
    """Bootstrap calibration of a model rater against human-scored anchors.

    Both lists are parallel (same anchor items, same order), each a dict
    of EV dimension -> integer score. Returns the adjacent-agreement
    rate and whether the model rater passes the admission gate.
    """
    if not human_anchor_scores or len(model_scores) != len(human_anchor_scores):
        raise ValueError("model and human anchor score lists must be parallel and non-empty")
    total = adjacent = 0
    exact = 0
    for m, h in zip(model_scores, human_anchor_scores):
        for dim in C.DIMENSIONS:
            if dim in m and dim in h:
                total += 1
                if abs(m[dim] - h[dim]) <= 1:
                    adjacent += 1
                if m[dim] == h[dim]:
                    exact += 1
    rate = adjacent / total if total else 0.0
    return {
        "adjacent_agreement": round(rate, 3),
        "exact_agreement": round(exact / total, 3) if total else 0.0,
        "threshold": CALIBRATION_ADJACENT_THRESHOLD,
        "passed": rate >= CALIBRATION_ADJACENT_THRESHOLD,
        "n_comparisons": total,
    }


def reviewer_admitted(*, qualified_for_review: bool, calibration: dict | None) -> tuple[bool, str]:
    """Decide whether a reviewer model's scores carry weight.

    Admitted if the model already holds a review-class qualification
    (CA-06 scope), or if bootstrap calibration passed. Otherwise its
    scores are advisory only (PLATFORM.md §7).
    """
    if qualified_for_review:
        return True, "reviewer holds a current review-class qualification"
    if calibration and calibration.get("passed"):
        return True, (f"reviewer admitted by bootstrap calibration "
                      f"(adjacent agreement {calibration['adjacent_agreement']} "
                      f">= {calibration['threshold']})")
    if calibration:
        return False, (f"reviewer NOT admitted: adjacent agreement "
                       f"{calibration['adjacent_agreement']} < {calibration['threshold']}; "
                       "scores are advisory only")
    return False, "reviewer unqualified and uncalibrated; scores are advisory only"


def _divergences(human: dict, model: dict, risk_tier: str) -> list[dict]:
    out = []
    for dim in C.DIMENSIONS:
        if dim not in human or dim not in model:
            continue
        delta = abs(human[dim] - model[dim])
        gate = C.GATES[risk_tier][dim]
        gate_changing = (human[dim] >= gate) != (model[dim] >= gate)
        if delta >= DIVERGENCE_POINTS or gate_changing:
            out.append({"dimension": dim, "human": human[dim], "model": model[dim],
                        "delta": delta, "gate_changing": gate_changing})
    return out


def assemble_review_package(
    run_id: str,
    *,
    reviewer_label: str,
    reviewer_qualified_for_review: bool = False,
    calibration: dict | None = None,
    consider_advisory_review: bool = False,
    human_evaluation: str | None = None,
) -> dict:
    """Assemble the human review package for a run.

    Pairs each human rating with the reviewer model's rating for the same
    response, flags divergences for human resolution (never averaged),
    and states whether the model rater is admitted or advisory.
    """
    from . import rating, workspace

    manifest = workspace.read_json(workspace.run_dir(run_id) / "manifest.json")
    risk_tier = manifest["risk_tier"]
    ratings = rating.collect_ratings(run_id)
    by_resp: dict[str, dict[str, list[dict]]] = {}
    for r in ratings:
        kind = r["provenance"]["rater_kind"]
        by_resp.setdefault(r["rates_response"], {}).setdefault(kind, []).append(r)

    admitted, admit_reason = reviewer_admitted(
        qualified_for_review=reviewer_qualified_for_review, calibration=calibration)

    items, all_divergences = [], []
    for resp, kinds in sorted(by_resp.items()):
        humans = kinds.get("human", [])
        models = kinds.get("model", [])
        entry = {"response": resp,
                 "has_human": bool(humans),
                 "has_model": bool(models),
                 "human_raters": [h["provenance"]["rater"] for h in humans],
                 "model_raters": [m["provenance"]["rater"] for m in models]}
        item_divergences = []
        pairs = []
        for left_index, left in enumerate(humans):
            for right in humans[left_index + 1:]:
                pairs.append(("human-human", left, right))
            for right in models:
                pairs.append(("human-model", left, right))
        for pair_kind, left, right in pairs:
            for divergence in _divergences(left["scores"], right["scores"], risk_tier):
                detail = {
                    "pair_kind": pair_kind,
                    "left_rater": left["provenance"]["rater"],
                    "right_rater": right["provenance"]["rater"],
                    **divergence,
                }
                item_divergences.append(detail)
                all_divergences.append({"response": resp, **detail})
        if item_divergences:
            entry["divergences"] = item_divergences
        items.append(entry)

    return {
        "kind": "review-package",
        "run_id": run_id,
        "risk_tier": risk_tier,
        "reviewer": {"label": reviewer_label, "admitted": admitted,
                     "reason": admit_reason, "calibration": calibration},
        "human_consideration": {
            "automated_advisory_review": {
                "available": any((r.get("provenance") or {}).get("rater_kind") == "model"
                                 for r in ratings),
                "considered": consider_advisory_review,
            },
            "human_evaluation": {"evaluator": human_evaluation},
        },
        "items": items,
        "divergences_for_resolution": all_divergences,
        "summary": {
            "reviewer_admitted": admitted,
            "n_divergences": len(all_divergences),
            "note": ("Model review assists; a human makes the decision "
                     "(PLATFORM.md D8, AIES-AESQS-PR-01-R09). "
                     + ("Model scores remain visible as advisory only automated "
                        "evidence; they are not admitted as corroborating peer "
                        "review." if not admitted else
                        "Model scores are admitted as corroborating evidence.")
                     + (" Divergences are listed for human resolution against "
                        "the anchors, never averaged." if all_divergences else "")),
        },
    }

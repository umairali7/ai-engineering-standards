"""Informational engineering-evaluation view over recorded rating observations.

This is deliberately separate from the qualification Evidence Package. A
complete automated evaluation may produce reports and ECM decision products;
formal qualification applies the human admission protocol independently.
"""

from __future__ import annotations

from . import constants as C, rating, workspace

EVALUATION_SCHEMA = 1


def summarize(run_id: str) -> dict:
    rdir = workspace.run_dir(run_id)
    manifest = workspace.read_json(rdir / "manifest.json")
    responses = {
        path.name: workspace.read_json(path)
        for path in (rdir / "responses").glob("*.json")
    }
    area_codes = [area["area"] for area in manifest.get("areas", [])]
    response_names_by_area = {area: set() for area in area_codes}
    sources = {
        area: {
            "automated": {"responses": set(), "scores": []},
            "human": {"responses": set(), "scores": []},
        }
        for area in area_codes
    }
    human_raters: set[str] = set()
    for response_name, response in responses.items():
        response_names_by_area.setdefault(response.get("area", "unknown"), set()).add(
            response_name)

    for record in rating.collect_ratings(run_id):
        response_name = record.get("rates_response")
        response = responses.get(response_name) or {}
        area = response.get("area", "unknown")
        provenance = record.get("provenance") or {}
        source = "human" if provenance.get("rater_kind") == "human" else "automated"
        if source == "human" and provenance.get("rater"):
            human_raters.add(str(provenance["rater"]))
        bucket = sources.setdefault(area, {}).setdefault(
            source, {"responses": set(), "scores": []})
        if response_name:
            bucket["responses"].add(response_name)
        bucket["scores"].append(record.get("scores") or {})

    review_path = rdir / "review-package.json"
    review = workspace.read_json(review_path) if review_path.exists() else {}
    evaluator = (((review.get("human_consideration") or {}).get(
        "human_evaluation") or {}).get("evaluator"))
    if not evaluator and human_raters:
        evaluator = ", ".join(sorted(human_raters))

    areas = {}
    all_rated_responses: set[str] = set()
    for area in sorted(area_codes):
        total = len(response_names_by_area.get(area, set()))
        source_views = {}
        source_response_sets = []
        for source in ("automated", "human"):
            bucket = sources.get(area, {}).get(
                source, {"responses": set(), "scores": []})
            response_set = set(bucket["responses"])
            source_response_sets.append(response_set)
            all_rated_responses.update(response_set)
            dimension_values = {
                dimension: [score[dimension] for score in bucket["scores"]
                            if isinstance(score.get(dimension), int)]
                for dimension in C.DIMENSIONS
            }
            flat = [value for values in dimension_values.values() for value in values]
            source_views[source] = {
                "responses_scored": len(response_set),
                "responses_total": total,
                "coverage_percent": (
                    round(len(response_set) / total * 100, 1) if total else 0.0),
                "observed_mean": round(sum(flat) / len(flat), 3) if flat else None,
                "dimensions": {
                    dimension: {
                        "n": len(values),
                        "mean": round(sum(values) / len(values), 3) if values else None,
                    }
                    for dimension, values in dimension_values.items()
                },
            }
        union = source_response_sets[0] | source_response_sets[1]
        automated_complete = total > 0 and len(source_response_sets[0]) == total
        human_complete = total > 0 and len(source_response_sets[1]) == total
        complete = total > 0 and len(union) == total
        areas[area] = {
            "status": "complete" if complete else ("partial" if union else "not-scored"),
            "completed_by": ("automated" if automated_complete else
                             "human" if human_complete else
                             "mixed" if complete else None),
            "sources": source_views,
        }

    all_responses = set(responses)
    status = ("complete" if all_responses and all_rated_responses >= all_responses
              else "partial" if all_rated_responses else "not-scored")
    return {
        "kind": "engineering-evaluation-summary",
        "evaluation_schema": EVALUATION_SCHEMA,
        "run_id": run_id,
        "status": status,
        "human_evaluation": {
            "status": "reviewed" if evaluator else "not-reviewed",
            "optional": True,
            "evaluator": evaluator,
        },
        "areas": areas,
        "qualification_boundary": (
            "Automated scores can complete an engineering evaluation and its "
            "decision products. Formal qualification and grants apply the "
            "separate human protocol in ADR-0012."),
    }

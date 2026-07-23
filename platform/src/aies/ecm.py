"""Engineering Capability Matrix (ECM) evidence views.

The ECM is a subject-neutral, informational decision product. It maps scored
scenarios to the versioned AIES Engineering Task Taxonomy, retains the source
scenario-family evidence, and keeps qualification and deployment authority
separate from engineering-facing capability communication.
"""

from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path

from . import (compare, constants as C, profiles, rating, run_mode, runner,
               scoring, task_mappings, workspace)

ECM_SCHEMA = 2
TASK_DECISION_SEMANTICS_VERSION = "1.0"
TASK_SORT_FIELDS = ("task", "performance", "breadth", "evidence", "status")


def sorted_tasks(matrix: dict, sort_by: str = "performance",
                 descending: bool = True) -> list[dict]:
    """Return a presentation order without changing canonical ECM evidence."""
    if sort_by not in TASK_SORT_FIELDS:
        raise ValueError(
            f"unknown task sort {sort_by!r}; choose from "
            + ", ".join(TASK_SORT_FIELDS))
    tasks = list(matrix.get("tasks") or [])
    if sort_by == "task":
        return sorted(
            tasks, key=lambda task: (task["task_id"], task["task"]),
            reverse=descending)

    def value(task: dict):
        if sort_by == "performance":
            return task.get("observed_performance")
        if sort_by == "breadth":
            return _task_breadth_percent(task)
        if sort_by == "evidence":
            return task.get("distinct_scenarios", 0)
        return task.get("engineering_status") or task.get("status") or ""

    assessed = [task for task in tasks
                if task.get("observed_performance") is not None]
    unassessed = [task for task in tasks
                  if task.get("observed_performance") is None]
    assessed.sort(
        key=lambda task: (value(task), task["task_id"]),
        reverse=descending)
    # Unknown is never represented as the lowest capability; it remains a
    # visibly separate tail regardless of sort direction.
    return assessed + sorted(unassessed, key=lambda task: task["task_id"])


_SORTABLE_SCRIPT = """<script>
document.querySelectorAll('table').forEach((table) => {
  if (table.dataset.aiesSortable === 'true') return;
  table.dataset.aiesSortable = 'true';
  table.classList.add('sortable');
  table.querySelectorAll('th').forEach((th, column) => {
    th.tabIndex = 0;
    th.title = 'Sort by this column';
    const sort = () => {
      const body = table.tBodies[0];
      if (!body) return;
      const direction = th.dataset.direction === 'asc' ? -1 : 1;
      table.querySelectorAll('th').forEach((item) => {
        item.removeAttribute('aria-sort'); delete item.dataset.direction;
      });
      th.dataset.direction = direction === 1 ? 'asc' : 'desc';
      th.setAttribute('aria-sort', direction === 1 ? 'ascending' : 'descending');
      const value = (cell) => {
        const text = (cell?.dataset.sort || cell?.textContent || '').trim();
        if (/not assessed|unavailable/i.test(text)) return {missing: 1, value: 0};
        const percent = text.match(/(-?\\d+(?:\\.\\d+)?)%/);
        if (percent) return {missing: 0, value: Number(percent[1])};
        const fraction = text.match(/(-?\\d+(?:\\.\\d+)?)\\s*\\/\\s*(-?\\d+(?:\\.\\d+)?)/);
        if (fraction) return {missing: 0, value: Number(fraction[1]) / Math.max(Number(fraction[2]), 1)};
        const number = text.match(/^-?\\d+(?:\\.\\d+)?/);
        return number ? {missing: 0, value: Number(number[0])}
                      : {missing: 0, value: text.toLocaleLowerCase()};
      };
      [...body.rows].sort((a, b) => {
        const left = value(a.cells[column]), right = value(b.cells[column]);
        if (left.missing !== right.missing) return left.missing - right.missing;
        return (typeof left.value === 'number'
          ? left.value - right.value
          : String(left.value).localeCompare(String(right.value))) * direction;
      }).forEach((row) => body.appendChild(row));
    };
    th.addEventListener('click', sort);
    th.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); sort(); }
    });
  });
});
</script>"""


def sortable_script() -> str:
    """Client-side, dependency-free sorting for generated HTML tables."""
    return _SORTABLE_SCRIPT


def _scenario_index(areas: set[str]) -> dict[str, dict]:
    """Load only the scenarios relevant to a run, keyed by scenario id."""
    index: dict[str, dict] = {}
    for area in areas:
        _, scenarios, _ = runner.load_area(area)
        index.update({s["id"]: s for s in scenarios})
    return index


def _adequacy(n: int, minimum: int, decisional: bool) -> str:
    if not decisional:
        return "non-decisional"
    if n < minimum:
        return "insufficient"
    return "decisional"


def _dimension_view(result) -> dict:
    return {
        dimension: {
            "n": score.n,
            "mean": score.mean,
            "ci90_low": score.ci_low,
            "ci90_high": score.ci_high,
            "decision_value": score.ci_low,
        }
        for dimension, score in result.dimensions.items()
    }


def _task_assurance(
    decision: dict,
    rater_kinds: set[str],
    evaluation_summary: dict,
    scenario_breadth: float,
) -> dict:
    """Describe assurance inputs without collapsing them into a fake score."""
    maturity = decision.get("instrument_maturity") or {}
    total = maturity.get("total_distinct_scenarios", 0)
    empirical = maturity.get("empirically_calibrated", 0)
    human_status = (
        (evaluation_summary.get("human_evaluation") or {}).get("status")
        or "not-reviewed"
    )
    limitations = []
    if not decision.get("mapping_review_satisfied"):
        limitations.append("scenario-to-task mapping review is pending")
    if empirical < total:
        limitations.append(
            f"{empirical}/{total} task instruments are empirically calibrated")
    if rater_kinds == {"model"}:
        limitations.append("scores come from automated review only")
    if human_status != "reviewed":
        limitations.append("optional human evaluation was not recorded")
    return {
        "status": "provisional" if limitations else "reviewed",
        "scenario_breadth_percent": scenario_breadth,
        "mapping_review": (
            "accepted" if decision.get("mapping_review_satisfied")
            else "pending"),
        "instrument_maturity": maturity,
        "rater_basis": (
            "automated-only" if rater_kinds == {"model"}
            else "human-only" if rater_kinds == {"human"}
            else "mixed" if rater_kinds else "unknown"),
        "human_evaluation": human_status,
        "limitations": limitations,
        "interpretation": (
            "Assurance is a structured disclosure, not a qualification gate "
            "or a replacement for task-level uncertainty."),
    }


def _task_decision(task_id: str, data: dict, pkg: dict,
                   weight_adjustments: dict) -> dict:
    """Apply accepted ADR-0013 to one mapped engineering task."""
    risk_tier = pkg["risk_tier"]
    subject_kind = pkg.get("subject_kind", "ai")
    minimum = C.MIN_SAMPLE[subject_kind][risk_tier]
    all_items = list(data["all_items"].values())
    admitted = list(data["decision_items"].values())
    scored = scoring.score_area(
        task_id, risk_tier, [item["scores"] for item in admitted],
        subject_kind=subject_kind, weight_adjustments=weight_adjustments)

    mapping_records = list(data["mapping_rules"].values())
    mappings_reviewed = bool(mapping_records) and all(
        (record.get("review") or {}).get("status") == "accepted"
        for record in mapping_records)
    double_rated = [item for item in admitted
                    if item.get("qualified_human_observation_count", 0) >= 2]
    required_fraction = 1.0 if risk_tier in ("RT3", "RT4") else 0.2
    double_fraction = len(double_rated) / len(all_items) if all_items else 0.0
    agreement_fraction = (
        sum(1 for item in double_rated if item.get("max_dimension_delta", 4) <= 1)
        / len(double_rated) if double_rated else 0.0)
    unresolved = [item for item in all_items if not item.get("resolved")]
    rater_protocol = {
        "satisfied": (
            len(admitted) == len(all_items)
            and double_fraction + 1e-12 >= required_fraction
            and bool(double_rated)
            and agreement_fraction >= 0.8
            and not unresolved),
        "qualification_eligible_items": len(admitted),
        "total_distinct_items": len(all_items),
        "double_rated_items": len(double_rated),
        "double_rating_fraction": round(double_fraction, 3),
        "required_double_rating_fraction": required_fraction,
        "agreement_fraction": round(agreement_fraction, 3),
        "agreement_threshold": 0.8,
        "unresolved_items": len(unresolved),
    }
    parent_areas = {
        area: {
            "decisional": bool(pkg["areas"][area].get("decisional")),
            "gates_passed": bool(pkg["areas"][area].get("gates_passed")),
        }
        for area in sorted(data["areas"])
    }
    parent_passed = bool(parent_areas) and all(
        detail["decisional"] and detail["gates_passed"]
        for detail in parent_areas.values())
    reasons = []
    if not mappings_reviewed:
        reasons.append("one or more scenario-to-task mappings lack accepted human review")
    if len(admitted) < minimum:
        reasons.append(f"{len(admitted)}/{minimum} distinct admitted task scenarios")
    if not rater_protocol["satisfied"]:
        reasons.append("task-specific human-rater protocol is incomplete")
    if not parent_passed:
        reasons.append("one or more contributing competency areas are non-decisional or gate-failing")
    if scored.gates and not scored.gates_passed:
        reasons.append("task EV decision values fail one or more risk-tier gates")
    if scored.aggregate is not None and scored.aggregate < 2.0:
        reasons.append("task aggregate is below CL1 — Foundational threshold 2.0")

    if not mappings_reviewed:
        status = "observed"
    elif len(admitted) < minimum or not rater_protocol["satisfied"]:
        status = "insufficient"
    elif not parent_passed or not scored.gates_passed:
        status = "gate-failed"
    elif scored.aggregate is None or scored.aggregate < 2.0:
        status = "performance-below-threshold"
    else:
        status = "demonstrated"

    maturity = {"design_reviewed": 0, "empirically_calibrated": 0,
                "total_distinct_scenarios": len(data["scenario_ids"])}
    for calibration in data["instrument_maturity"].values():
        if calibration.get("design_reviewed"):
            maturity["design_reviewed"] += 1
        if calibration.get("empirically_calibrated"):
            maturity["empirically_calibrated"] += 1
    return {
        "semantics_version": TASK_DECISION_SEMANTICS_VERSION,
        "status": status,
        "reasons": reasons,
        "minimum_distinct_scenarios": minimum,
        "distinct_admitted_scenarios": len(admitted),
        "breadth_satisfied": len(admitted) >= minimum,
        "mapping_review_satisfied": mappings_reviewed,
        "mapping_reviews": mapping_records,
        "instrument_maturity": maturity,
        "rater_protocol": rater_protocol,
        "parent_areas": parent_areas,
        "parent_scope_satisfied": parent_passed,
        "dimensions": _dimension_view(scored),
        "gates": [{"dimension": gate.dimension,
                   "threshold": gate.threshold,
                   "decision_value": gate.decision_value,
                   "passed": gate.passed,
                   **({"reason": gate.reason} if gate.reason else {})}
                  for gate in scored.gates],
        "gates_passed": scored.gates_passed,
        "ev3_hard_fail": scored.ev3_hard_fail,
        "aggregate_A": scored.aggregate,
        "cl": scored.cl,
        "cl_note": scored.cl_note,
        "al_envelope": scored.al_envelope,
    }


def engineering_capability_matrix(ref: str) -> dict:
    """Return a factual ECM v0 view for an aggregated run or deployment.

    Values are evidence summaries only. ``evidence_mean`` is the unweighted
    mean of the six recorded EV scores, included to help inspection; it is not
    a qualification score, competency level, or recommendation.
    """
    from . import evaluation

    pkg = compare._resolve_package(ref)
    run_id = pkg["run_id"]
    manifest = workspace.read_json(
        workspace.run_dir(run_id) / "manifest.json")
    purpose = run_mode.purpose(manifest)
    evaluation_summary = evaluation.summarize(run_id)
    response_dir = workspace.run_dir(run_id) / "responses"
    responses = {p.name: workspace.read_json(p) for p in response_dir.glob("*.json")}
    scenario_index = _scenario_index(set(pkg["areas"]))
    grouped: dict[tuple[str, str], dict] = defaultdict(lambda: {
        "scenario_ids": set(), "response_records": set(), "scores": [],
        "raters": set(), "rater_kinds": set(),
    })
    task_grouped: dict[str, dict] = defaultdict(lambda: {
        "scenario_ids": set(), "response_records": set(), "scores": [],
        "admitted_scores": [], "raters": set(), "rater_kinds": set(), "areas": set(),
        "mapping_rules": {}, "instrument_maturity": {},
        "all_items": {}, "decision_items": {},
    })
    mapping = task_mappings.load()
    task_names = task_mappings.task_names(mapping)
    profile = profiles.load(pkg["profile"])
    weight_adjustments = profile.get("dimension_weight_adjustments") or {}
    for record in rating.collect_ratings(run_id):
        response_name = record.get("rates_response")
        response = responses.get(response_name)
        scenario_id = record.get("scenario_id") or (response or {}).get("scenario_id")
        if not response or not scenario_id:
            # A rating without a retained response cannot support a traceable
            # family claim. Aggregation has its own historical behavior; ECM
            # excludes the orphan rather than guessing its mapping.
            continue
        area = response.get("area")
        scenario = scenario_index.get(scenario_id, {})
        family = scenario.get("family") or "unmapped"
        row = grouped[(area, family)]
        row["scenario_ids"].add(scenario_id)
        row["response_records"].add(response_name)
        scores = record.get("scores") or {}
        if scores:
            row["scores"].append(sum(scores.values()) / len(scores))
        provenance = record.get("provenance") or {}
        # Legacy packages may list a calibrated model as admitted. ADR-0012
        # narrows qualification-score admission to human-resolved evidence;
        # automated observations still feed the informational ECM `scores`.
        record_admitted = (
            provenance.get("rater_kind") == "human"
            and (provenance.get("qualification_admitted") is True
                 or pkg.get("evidence_schema", 0) < 5))
        if provenance.get("rater"):
            row["raters"].add(provenance["rater"])
        if provenance.get("rater_kind"):
            row["rater_kinds"].add(provenance["rater_kind"])
        for rule in task_mappings.mapping_rules_for_scenario(scenario, mapping):
            for task_id in rule["tasks"]:
                task = task_grouped[task_id]
                task["scenario_ids"].add(scenario_id)
                task["response_records"].add(response_name)
                task["areas"].add(area)
                rule_key = f"{rule['area']}:{rule.get('family', '*')}:{task_id}"
                task["mapping_rules"][rule_key] = {
                    "area": rule["area"], "family": rule.get("family"),
                    "task_id": task_id, "rationale": rule["rationale"],
                    "review": rule["review"],
                }
                calibration = ((scenario.get("calibration") or {}).get(
                    "empirical_status") or {})
                task["instrument_maturity"][scenario_id] = calibration
                if scores:
                    task["scores"].append(sum(scores.values()) / len(scores))
                    if record_admitted:
                        task["admitted_scores"].append(sum(scores.values()) / len(scores))
                if provenance.get("rater"):
                    task["raters"].add(provenance["rater"])
                if provenance.get("rater_kind"):
                    task["rater_kinds"].add(provenance["rater_kind"])

    # Task decisions consume one qualification-eligible resolved item per
    # distinct scenario. Ratings and explicit repeats remain provenance and
    # stability evidence; neither increases task breadth or narrows its CI.
    evidence_item_envelope = pkg.get("evidence_items") or {}
    evidence_item_records = (
        evidence_item_envelope.get("items", [])
        if isinstance(evidence_item_envelope, dict)
        else evidence_item_envelope)
    for item in evidence_item_records:
        scenario_id = item.get("scenario_id")
        scenario = scenario_index.get(scenario_id, {})
        if not scenario:
            continue
        for task_id in task_mappings.tasks_for_scenario(scenario, mapping):
            data = task_grouped[task_id]
            existing = data["all_items"].get(scenario_id)
            repeat = item.get("repeat") or 1
            if existing is None or repeat < (existing.get("repeat") or 1):
                data["all_items"][scenario_id] = item
            if item.get("resolved") and item.get("qualification_eligible"):
                admitted_existing = data["decision_items"].get(scenario_id)
                if (admitted_existing is None
                        or repeat < (admitted_existing.get("repeat") or 1)):
                    data["decision_items"][scenario_id] = item

    rows = []
    for (area, family), data in sorted(grouped.items()):
        area_evidence = pkg["areas"].get(area, {})
        n = len(data["scores"])
        minimum = area_evidence.get("min_sample", 0)
        decisional = bool(area_evidence.get("decisional")) and n >= minimum
        qualification_adequacy = _adequacy(n, minimum, decisional)
        rows.append({
            "area": area,
            "scenario_family": family,
            "label": f"{C.competency_label(area)} / {family}",
            "scenario_ids": sorted(data["scenario_ids"]),
            "distinct_scenarios": len(data["scenario_ids"]),
            "distinct_responses": len(data["response_records"]),
            "rating_observations": n,
            "minimum_observations": minimum,
            "adequacy": ("observed" if n else "not assessed")
                        if purpose == run_mode.ENGINEERING_EVALUATION
                        else qualification_adequacy,
            "qualification_adequacy": qualification_adequacy,
            "evidence_mean": round(sum(data["scores"]) / n, 3) if n else None,
            "rater_kinds": sorted(data["rater_kinds"]),
            "raters": sorted(data["raters"]),
            "area_gates_passed": area_evidence.get("gates_passed"),
            "area_competency_level": area_evidence.get("cl"),
        })

    tasks = []
    for task_id, task_name in task_names.items():
        data = task_grouped.get(task_id)
        if not data:
            empty_decision = {
                "semantics_version": TASK_DECISION_SEMANTICS_VERSION,
                "status": "not assessed", "reasons": ["no direct mapped evidence"],
                "minimum_distinct_scenarios": C.MIN_SAMPLE[
                    pkg.get("subject_kind", "ai")][pkg["risk_tier"]],
                "distinct_admitted_scenarios": 0,
            }
            tasks.append({"task_id": task_id, "task": task_name, "scenario_ids": [],
                          "areas": [], "distinct_scenarios": 0, "distinct_responses": 0,
                          "rating_observations": 0, "minimum_observations": None,
                          "admitted_rating_observations": 0, "observed_performance": None,
                          "coverage_percent": None,
                          "scenario_breadth_percent": 0,
                          "engineering_confidence_percent": 0,
                          "engineering_status": "not assessed",
                          "evidence_assurance": {
                              "status": "not assessed",
                              "scenario_breadth_percent": 0,
                              "mapping_review": "not assessed",
                              "instrument_maturity": {
                                  "design_reviewed": 0,
                                  "empirically_calibrated": 0,
                                  "total_distinct_scenarios": 0,
                              },
                              "rater_basis": "unknown",
                              "human_evaluation": (
                                  evaluation_summary.get("human_evaluation")
                                  or {}).get("status", "not-reviewed"),
                              "limitations": ["no direct mapped evidence"],
                              "interpretation": (
                                  "Assurance is a structured disclosure, not "
                                  "a qualification gate."),
                          },
                          "qualification_status": "not assessed",
                          "status": "not assessed",
                          "decision_semantics": TASK_DECISION_SEMANTICS_VERSION,
                          "task_decision": empty_decision,
                          "raters": [], "rater_kinds": []})
            continue
        n = len(data["scores"])
        decision = _task_decision(
            task_id, data, pkg, weight_adjustments=weight_adjustments)
        minimum = decision["minimum_distinct_scenarios"]
        performance = round(sum(data["scores"]) / n, 3) if n else None
        admitted_observations = sum(
            item.get("qualified_human_observation_count", 0)
            for item in data["decision_items"].values())
        scenario_breadth = round(
            min(1, len(data["scenario_ids"]) / minimum) * 100)
        engineering_status = (
            "observed — target breadth met" if scenario_breadth >= 100
            else "observed — partial breadth"
            if scenario_breadth >= 50
            else "observed — limited breadth")
        assurance = _task_assurance(
            decision, data["rater_kinds"], evaluation_summary,
            scenario_breadth)
        tasks.append({"task_id": task_id, "task": task_name,
                      "scenario_ids": sorted(data["scenario_ids"]), "areas": sorted(data["areas"]),
                      "distinct_scenarios": len(data["scenario_ids"]),
                      "distinct_responses": len(data["response_records"]),
                      "rating_observations": n, "minimum_observations": minimum,
                      "minimum_distinct_scenarios": minimum,
                      "admitted_rating_observations": admitted_observations,
                      "admitted_evidence_items": len(data["decision_items"]),
                      "observed_performance": performance,
                      "coverage_percent": round(
                          min(1, len(data["decision_items"]) / minimum) * 100),
                      "scenario_breadth_percent": scenario_breadth,
                      # Compatibility alias from ECM schema 2. The value has
                      # always measured breadth, not reviewer or instrument
                      # assurance; reader-facing views use the accurate name.
                      "engineering_confidence_percent": scenario_breadth,
                      "engineering_status": engineering_status,
                      "evidence_assurance": assurance,
                      "qualification_status": decision["status"],
                      "status": decision["status"],
                      "decision_semantics": TASK_DECISION_SEMANTICS_VERSION,
                      "task_decision": decision,
                      "raters": sorted(data["raters"]), "rater_kinds": sorted(data["rater_kinds"])})

    return {
        "kind": "engineering-capability-matrix",
        "ecm_schema": ECM_SCHEMA,
        "measurement_claim": {
            "contract": "aies-measurement-claims/v1",
            "claim": "engineering_capability_matrix",
            "status": "draft",
        },
        "task_decision_semantics_version": TASK_DECISION_SEMANTICS_VERSION,
        "status": "informational",
        "mapping": {
            "kind": mapping["id"],
            "version": mapping["version"],
            "schema": mapping["schema"],
            "status": mapping["status"],
            "scope": "versioned scenario-to-Engineering-Task registry",
        },
        "run_id": run_id,
        "run_purpose": purpose,
        "subject": (pkg.get("subject") or {}).get("id", pkg["model"]["registry_id"]),
        "subject_kind": pkg.get("subject_kind", "ai"),
        "risk_tier": pkg["risk_tier"],
        "profile": pkg["profile"],
        "rater_kinds": pkg.get("rater_kinds", []),
        "engineering_evaluation": evaluation_summary,
        "rows": rows,
        "tasks": tasks,
        "limitations": [
            "Informational only; this matrix is not qualification evidence, a grant, or deployment authorization.",
            "Task rows are derived from the versioned scenario-to-task mapping registry; scenario-family rows remain the traceable source evidence.",
            "Evidence mean is an unweighted inspection statistic, not a competency level or recommendation.",
            "Scenario breadth counts distinct directly mapped scored scenarios; exact repeats do not increase it.",
            "The legacy engineering_confidence_percent field is a compatibility alias for scenario_breadth_percent; it is not a claim about reviewer validity, mapping review, empirical calibration, or human assurance.",
            "Formal task decisions follow ADR-0013 and remain separate from the observed engineering profile.",
            "Automated ratings can complete the engineering evaluation; optional human evaluation adds assurance but is not required to generate this ECM.",
        ],
    }


def _human_evaluation_label(matrix: dict) -> str:
    record = ((matrix.get("engineering_evaluation") or {}).get(
        "human_evaluation") or {})
    if record.get("status") == "reviewed":
        return f"☑ Reviewed — {record.get('evaluator') or 'named human'}"
    return "☐ Not reviewed (optional)"


def render_markdown(matrix: dict, *, sort_by: str = "performance",
                    descending: bool = True) -> str:
    """Render a human-readable ECM Markdown artifact."""
    lines = [
        "# Engineering Capability Matrix (ECM)",
        "",
        "> **INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.**",
        "",
        f"Subject: `{matrix['subject']}`  ",
        f"Run: `{matrix['run_id']}`  ",
        f"Scope: {C.risk_tier_label(matrix['risk_tier'])} · {matrix['profile']} profile  ",
        f"Mapping: {matrix['mapping']['scope']}  ",
        f"Human evaluation: {_human_evaluation_label(matrix)}",
        "",
        "## Task Capability Profile",
        "",
        "| Task | Observed performance | Scenario breadth | Evidence assurance | Evidence | Engineering status | Human eval |",
        "|---|---|---|---|---|---|---|",
    ]
    for task in sorted_tasks(matrix, sort_by, descending):
        performance = ("not assessed" if task["observed_performance"] is None
                       else _bar(task["observed_performance"] / 4 * 100)
                            + f" {task['observed_performance'] / 4 * 100:.0f}%")
        lines.append(
            f"| {task['task_id']} {task['task']} | {performance} | "
            f"{_scenario_breadth(task)} | {_assurance_label(task)} | "
            f"{_task_sample(task)} | "
            f"{task.get('engineering_status', 'not assessed')} | "
            f"{_human_evaluation_label(matrix)} |")
    lines.extend([
        "",
        "Observed performance is the unweighted EV mean. Scenario breadth is "
        "the share of the task's distinct-scenario target directly exercised by "
        "scored evidence; exact repeats and additional raters do not increase it. "
        "Breadth is not reviewer, mapping, calibration, or human assurance.",
        "",
    ])
    if matrix.get("run_purpose") == run_mode.FORMAL_QUALIFICATION:
        lines.extend(["## Formal Qualification Task Decision Detail", ""])
        for task in matrix["tasks"]:
            if task["status"] == "not assessed":
                continue
            decision = task["task_decision"]
            protocol = decision.get("rater_protocol") or {}
            lines.extend([
                f"### {task['task_id']} — {task['task']}", "",
                f"- Formal decision status: **{task['status']}**",
                f"- Distinct admitted scenarios: "
                f"{decision.get('distinct_admitted_scenarios', 0)}/"
                f"{decision.get('minimum_distinct_scenarios', 0)}",
                f"- Human-rater protocol: "
                f"{'satisfied' if protocol.get('satisfied') else 'incomplete'}",
            ])
            if decision.get("reasons"):
                lines.append("- Reasons: " + "; ".join(decision["reasons"]))
            lines.append("")
    else:
        lines.extend([
            "## Formal Qualification Boundary", "",
            "Formal qualification was **not requested**. Human-rater admission, "
            "grant readiness, and qualification gates are therefore not statuses "
            "in this engineering matrix.", "",
        ])
    lines.extend([
        "## Scenario-family evidence",
        "",
        "| Evidence family | Mean EV score | Scenarios | Responses | Ratings | Adequacy |",
        "|---|---:|---:|---:|---:|---|",
    ])
    for row in matrix["rows"]:
        mean = "—" if row["evidence_mean"] is None else f"{row['evidence_mean']:.3f}"
        lines.append(
            f"| {row['label']} | {mean} | {row['distinct_scenarios']} | "
            f"{row['distinct_responses']} | {row['rating_observations']}/"
            f"{row['minimum_observations']} | {row['adequacy']} |"
        )
    if not matrix["rows"]:
        lines.append("| No traceable scored scenario-family evidence | — | 0 | 0 | 0 | insufficient |")
    signals = _improvement_signals(matrix)
    lines.extend(["", "## Observed improvement signals", ""])
    lines.append(
        "Lowest observed evidence slices in this run; not failure verdicts.")
    for item in signals["dimensions"]:
        lines.append(
            f"- **{item['area_label']} / {item['dimension_label']}:** "
            f"{item['mean']:.3f}/4 across {item['n']} ratings.")
    for item in signals["families"]:
        lines.append(
            f"- **Scenario family `{item['label']}`:** "
            f"{item['mean']:.3f}/4 across "
            f"{item['distinct_scenarios']} distinct scenarios.")
    if not signals["dimensions"] and not signals["families"]:
        lines.append("- No observed slice fell below the reporting threshold.")
    lines.extend(["", "## Evidence detail", ""])
    for row in matrix["rows"]:
        lines.extend([
            f"### {row['label']}",
            "",
            f"- Scenario evidence: {', '.join(f'`{x}`' for x in row['scenario_ids'])}",
            f"- Rater kinds: {', '.join(row['rater_kinds']) or 'not recorded'}",
            f"- Raters: {', '.join(row['raters']) or 'not recorded'}",
            f"- Area context: {row['area_competency_level'] or 'no CL'}; "
            f"area gates {'passed' if row['area_gates_passed'] else 'not passed'}.",
            "",
        ])
    lines.extend(["## Limitations", ""] + [f"- {x}" for x in matrix["limitations"]] + [""])
    return "\n".join(lines)


def _bar(percent: float) -> str:
    filled = max(0, min(10, round(percent / 10)))
    return "█" * filled + "░" * (10 - filled)


def _task_evidence(task: dict) -> str:
    """Show raw observations and admitted evidence without conflating them."""
    minimum = task["minimum_observations"]
    if minimum is None:
        return "no direct mapped evidence"
    decision = task.get("task_decision") or {}
    review = "mapping reviewed" if decision.get("mapping_review_satisfied") else "mapping review pending"
    return (f"{task.get('admitted_evidence_items', 0)}/{minimum} resolved items; "
            f"{review}")


def _task_sample(task: dict) -> str:
    """Describe direct task breadth without pretending it has its own gate."""
    if task["minimum_observations"] is None:
        return "no direct mapped evidence"
    return (f"{task['distinct_scenarios']} scenarios; "
            f"{task['rating_observations']} raw ratings")


def _scenario_breadth(task: dict) -> str:
    percent = _task_breadth_percent(task)
    if task.get("observed_performance") is None or percent is None:
        return "not assessed"
    minimum = task.get("minimum_observations") or 0
    return (f"{_bar(percent)} {percent:.0f}% "
            f"({task['distinct_scenarios']}/{minimum} distinct scenarios)")


def _task_breadth_percent(task: dict) -> float | None:
    return task.get(
        "scenario_breadth_percent",
        task.get("engineering_confidence_percent"))


def _assurance_label(task: dict) -> str:
    assurance = task.get("evidence_assurance") or {}
    if assurance.get("status") == "not assessed":
        return "not assessed"
    if not assurance:
        return "not disclosed (legacy artifact)"
    maturity = assurance.get("instrument_maturity") or {}
    design = maturity.get("design_reviewed", 0)
    empirical = maturity.get("empirically_calibrated", 0)
    total = maturity.get("total_distinct_scenarios", 0)
    return (
        f"{assurance.get('status', 'unknown')}; "
        f"{assurance.get('rater_basis', 'unknown')}; "
        f"mapping {assurance.get('mapping_review', 'unknown')}; "
        f"design review {design}/{total}; "
        f"empirical calibration {empirical}/{total}"
    )


def _task_status(task: dict) -> str:
    if task["status"] == "not assessed":
        return "not assessed"
    if task["admitted_rating_observations"] == 0:
        return "evaluated — automated"
    return task["status"]


def render_html(matrix: dict, *, sort_by: str = "performance",
                descending: bool = True) -> str:
    """Render a compact, self-contained engineer-facing ECM artifact."""
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in (
            row["label"],
            "—" if row["evidence_mean"] is None else f"{row['evidence_mean']:.3f}",
            row["distinct_scenarios"], row["distinct_responses"],
            f"{row['rating_observations']}/{row['minimum_observations']}", row["adequacy"],
        )) + "</tr>"
        for row in sorted(
            matrix["rows"],
            key=lambda item: (
                item["evidence_mean"] is not None,
                item["evidence_mean"] or -1,
                item["label"]),
            reverse=True)
    ) or "<tr><td colspan='6'>No traceable scored scenario-family evidence.</td></tr>"
    limits = "".join(f"<li>{html.escape(x)}</li>" for x in matrix["limitations"])
    task_rows = "".join(
        "<tr><td>" + html.escape(f"{task['task_id']} {task['task']}") + "</td><td>" +
        html.escape("not assessed" if task["observed_performance"] is None else
                    f"{_bar(task['observed_performance'] / 4 * 100)} {task['observed_performance'] / 4 * 100:.0f}%") +
        "</td><td>" + html.escape(_scenario_breadth(task)) +
        "</td><td>" + html.escape(_assurance_label(task)) +
        "</td><td>" + html.escape(_task_sample(task)) +
        "</td><td>" + html.escape(task.get("engineering_status", "not assessed")) +
        "</td><td>" + html.escape(_human_evaluation_label(matrix)) +
        "</td></tr>"
        for task in sorted_tasks(matrix, sort_by, descending)
    )
    task_details = ("" if matrix.get("run_purpose") != run_mode.FORMAL_QUALIFICATION
                    else "".join(
        "<details><summary>" + html.escape(f"{task['task_id']} — {task['task']}: {task['status']}") +
        "</summary><p>" + html.escape("; ".join(
            (task.get("task_decision") or {}).get("reasons") or ["all task-decision controls satisfied"])) +
        "</p><table><tr><th>Dimension</th><th>n</th><th>Mean</th><th>90% CI</th><th>Decision value</th></tr>" +
        "".join(
            "<tr><td>" + html.escape(C.identifier_label(dimension)) + "</td>" +
            f"<td>{detail['n']}</td><td>{detail['mean']:.3f}</td>" +
            f"<td>[{detail['ci90_low']:.3f}, {detail['ci90_high']:.3f}]</td>" +
            f"<td>{detail['decision_value']:.3f}</td></tr>"
            for dimension, detail in (task.get("task_decision") or {}).get("dimensions", {}).items()) +
        "</table></details>"
        for task in matrix["tasks"] if task["status"] != "not assessed"))
    summary = capability_summary(matrix)
    signals = _improvement_signals(matrix)
    observed = ", ".join(task["task"] for task in summary["engineering_assessed_tasks"]) or "None"
    unassessed = ", ".join(task["task"] for task in summary["task_not_assessed"]) or "None"
    automated = sum(task["rating_observations"] for task in matrix["tasks"]
                    if task["admitted_rating_observations"] == 0)
    human_label = _human_evaluation_label(matrix)
    signal_items = "".join(
        "<li><strong>" + html.escape(
            f"{item['area_label']} / {item['dimension_label']}") +
        f":</strong> {item['mean']:.3f}/4 across {item['n']} ratings.</li>"
        for item in signals["dimensions"])
    signal_items += "".join(
        "<li><strong>Scenario family <code>" +
        html.escape(item["label"]) + "</code>:</strong> "
        f"{item['mean']:.3f}/4 across "
        f"{item['distinct_scenarios']} distinct scenarios.</li>"
        for item in signals["families"])
    signal_items = signal_items or (
        "<li>No observed slice fell below the reporting threshold.</li>")
    return f"""<!doctype html><html lang='en'><meta charset='utf-8'>
<title>Engineering Capability Matrix — {html.escape(matrix['subject'])}</title>
<style>body{{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:0 1rem;color:#17202a}} table{{border-collapse:collapse;width:100%;margin:.75rem 0}}th,td{{border:1px solid #cbd5e1;padding:.5rem;text-align:left;vertical-align:top}}th{{background:#eaf2f8}}table.sortable th{{cursor:pointer}}table.sortable th:focus{{outline:3px solid #2563eb;outline-offset:-3px}}.notice{{padding:.75rem;background:#fff3cd;font-weight:600}}.summary{{padding:.8rem 1rem;background:#f8fafc;border-left:4px solid #64748b}}details{{margin:1.25rem 0}}summary{{cursor:pointer;font-weight:650}}</style>
<h1>Engineering Capability Matrix (ECM)</h1><p class='notice'>INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.</p>
<p><b>Subject:</b> {html.escape(matrix['subject'])}<br><b>Run:</b> {html.escape(matrix['run_id'])}<br><b>Scope:</b> {html.escape(C.risk_tier_label(matrix['risk_tier']))} · {html.escape(matrix['profile'])}<br><b>Human evaluation:</b> {html.escape(human_label)}</p>
<p class='summary'><strong>At a glance:</strong> {len(summary['engineering_assessed_tasks'])} assessed and {len(summary['task_not_assessed'])} not assessed task(s). {automated} automated rating observation(s) are usable engineering evidence. Human evaluation is optional.</p>
<h2>Task Capability Profile</h2><p>Sorted by {html.escape(sort_by)} {"descending" if descending else "ascending"}. Select any column heading to re-sort.</p><table class='sortable'><thead><tr><th>Task</th><th>Observed performance</th><th>Scenario breadth</th><th>Evidence assurance</th><th>Evidence</th><th>Engineering status</th><th>Human eval</th></tr></thead><tbody>{task_rows}</tbody></table>
<p>Observed performance is an unweighted EV mean. Scenario breadth measures distinct directly mapped scored scenarios against the task target; repeats do not increase it. Breadth is not reviewer, mapping, calibration, or human assurance.</p>
{"<h2>Formal Qualification Task Decision Detail</h2>" + task_details if task_details else "<h2>Formal Qualification Boundary</h2><p>Formal qualification was <strong>not requested</strong>; human-rater admission and grant readiness are not statuses in this engineering matrix.</p>"}
<h2>Evidence Summary</h2><ul><li><strong>Automated evaluation observations:</strong> {html.escape(observed)}.</li><li><strong>Direct evidence still needed:</strong> {html.escape(unassessed)}.</li><li><strong>Human evaluation:</strong> {html.escape(human_label)}.</li></ul>
<h2>Observed improvement signals</h2><p>Lowest observed evidence slices in this run; not failure verdicts.</p><ul>{signal_items}</ul>
<details><summary>Scenario-family evidence and traceability ({len(matrix['rows'])} rows)</summary><table class='sortable'><thead><tr><th>Evidence family</th><th>Mean EV score</th><th>Scenarios</th><th>Responses</th><th>Ratings</th><th>Adequacy</th></tr></thead><tbody>{rows}</tbody></table></details>
<h2>Limitations</h2><ul>{limits}</ul>{_SORTABLE_SCRIPT}</html>"""


def capability_summary(matrix: dict) -> dict:
    """Derive a bounded engineer-facing summary from ECM evidence.

    This deliberately distinguishes *observed patterns* from demonstrated,
    decisional capabilities. It provides no task recommendation where the run
    is too small or has no evidence for a task family.
    """
    rows = sorted(matrix["rows"], key=lambda row: (
        row["evidence_mean"] is not None, row["evidence_mean"] or -1
    ), reverse=True)
    assessed = sorted({row["area"] for row in rows})
    all_areas = runner.all_area_codes()
    unassessed = [area for area in all_areas if area not in assessed]
    demonstrated = [row for row in rows
                     if row["adequacy"] == "decisional"
                     and row["area_gates_passed"]
                     and row["evidence_mean"] is not None]
    observed = [row for row in rows if row["evidence_mean"] is not None]
    provisional = [row for row in observed if row not in demonstrated]
    task_rows = matrix["tasks"]
    engineering_assessed_tasks = [
        task for task in task_rows
        if task.get("observed_performance") is not None]
    task_demonstrated = [task for task in task_rows if task["status"] == "demonstrated"]
    task_observed = [task for task in task_rows if task["status"] == "observed"]
    task_insufficient = [task for task in task_rows if task["status"] == "insufficient"]
    task_failed = [task for task in task_rows if task["status"] in (
        "gate-failed", "performance-below-threshold")]
    task_not_assessed = [task for task in task_rows if task["status"] == "not assessed"]
    return {
        "demonstrated": demonstrated,
        "observed": observed,
        "provisional": provisional,
        "assessed_areas": assessed,
        "unassessed_areas": unassessed,
        "recommended": [row for row in demonstrated if row["evidence_mean"] >= 3.0],
        "with_human_review": provisional,
        "task_demonstrated": task_demonstrated,
        "task_observed": task_observed,
        "task_insufficient": task_insufficient,
        "task_failed": task_failed,
        "task_not_assessed": task_not_assessed,
        "engineering_assessed_tasks": engineering_assessed_tasks,
        "not_recommended": [
            "Autonomous production changes: this informational matrix cannot authorize deployment.",
            "Any task outside the assessed scenario families: this run contains no direct evidence for it.",
        ],
    }


def _improvement_signals(matrix: dict, limit: int = 6) -> dict:
    """Return low observed slices without turning them into failure verdicts."""
    dimensions = []
    evaluation_areas = (
        (matrix.get("engineering_evaluation") or {}).get("areas") or {})
    for area, detail in evaluation_areas.items():
        automated = (detail.get("sources") or {}).get("automated") or {}
        for dimension, score in (automated.get("dimensions") or {}).items():
            observed = score.get("mean")
            if observed is not None and observed < 3.5:
                dimensions.append({
                    "area": area,
                    "area_label": C.competency_label(area),
                    "dimension": dimension,
                    "dimension_label": C.identifier_label(dimension),
                    "mean": observed,
                    "n": score.get("n", 0),
                })
    families = [{
        "label": row["label"],
        "mean": row["evidence_mean"],
        "distinct_scenarios": row["distinct_scenarios"],
    } for row in matrix.get("rows", [])
        if row.get("evidence_mean") is not None
        and row["evidence_mean"] < 3.25]
    return {
        "dimensions": sorted(
            dimensions, key=lambda item: item["mean"])[:limit],
        "families": sorted(
            families, key=lambda item: item["mean"])[:limit],
    }


def render_capability_summary_markdown(matrix: dict) -> str:
    """Render the full engineer-facing section embedded in an evidence report."""
    summary = capability_summary(matrix)
    lines = [
        "## Engineering Capability Matrix (ECM)",
        "",
        "> **INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.**",
        "",
        "This section is derived solely from the scored scenario evidence in this run. "
        "It does not infer capability for tasks that were not assessed.",
        "",
        "### Task Capability Profile",
        "",
        "| Task | Observed performance | Scenario breadth | Evidence assurance | Evidence | Engineering status | Human eval |",
        "|---|---|---|---|---|---|---|",
    ]
    for task in matrix["tasks"]:
        performance = ("not assessed" if task["observed_performance"] is None
                       else _bar(task["observed_performance"] / 4 * 100)
                            + f" {task['observed_performance'] / 4 * 100:.0f}%")
        lines.append(
            f"| {task['task_id']} {task['task']} | {performance} | "
            f"{_scenario_breadth(task)} | {_assurance_label(task)} | "
            f"{_task_sample(task)} | "
            f"{task.get('engineering_status', 'not assessed')} | "
            f"{_human_evaluation_label(matrix)} |")
    lines.extend([
        "",
        "Observed performance is an unweighted EV mean. Scenario breadth "
        "measures distinct directly mapped scored scenarios against the task "
        "target; exact repeats do not increase it. Automated scores are usable "
        "Engineering Evaluation evidence.",
        "",
        "### Evidence by scenario family",
        "",
        "| Scenario family | Evidence mean (0–4) | Distinct scenarios | Ratings | Adequacy |",
        "|---|---:|---:|---:|---|",
    ])
    for row in summary["observed"]:
        mean = "—" if row["evidence_mean"] is None else f"{row['evidence_mean']:.3f}"
        lines.append(
            f"| {row['label']} | {mean} | {row['distinct_scenarios']} | "
            f"{row['rating_observations']}/{row['minimum_observations']} | "
            f"{row['adequacy']} |"
        )
    if not summary["observed"]:
        lines.append("| No traceable scored scenario-family evidence | — | 0 | 0 | insufficient |")

    lines.extend(["", "### Strength patterns", ""])
    assessed_tasks = summary["engineering_assessed_tasks"]
    strong_tasks = [
        task for task in assessed_tasks
        if task["observed_performance"] / 4 * 100 >= 75]
    review_tasks = [
        task for task in assessed_tasks
        if 50 <= task["observed_performance"] / 4 * 100 < 75]
    weak_tasks = [
        task for task in assessed_tasks
        if task["observed_performance"] / 4 * 100 < 50]
    for task in strong_tasks:
        lines.append(
            f"- **Strong observed performance:** `{task['task']}` — "
            f"{task['observed_performance'] / 4 * 100:.0f}% across "
            f"{task['distinct_scenarios']} distinct mapped scenarios; "
            f"{task.get('scenario_breadth_percent', task['engineering_confidence_percent']):.0f}% scenario breadth.")
    for task in review_tasks:
        lines.append(
            f"- **Moderate observed performance:** `{task['task']}` — "
            f"{task['observed_performance'] / 4 * 100:.0f}%; engineering review "
            "is recommended.")
    for task in weak_tasks:
        lines.append(
            f"- **Weak observed performance:** `{task['task']}` — "
            f"{task['observed_performance'] / 4 * 100:.0f}%; prioritize "
            "remediation or alternatives.")
    if not assessed_tasks:
        lines.append("- No mapped engineering task has traceable scored evidence in this run.")

    lines.extend(["", "### Improvement and evidence gaps", ""])
    if summary["task_not_assessed"]:
        lines.append("- **Collect direct evidence before making a claim:** "
                     + ", ".join(f"`{task['task']}`" for task in summary["task_not_assessed"]) + ".")
    low_breadth = [
        task for task in assessed_tasks
        if task.get("scenario_breadth_percent",
                    task.get("engineering_confidence_percent", 0)) < 100]
    if low_breadth:
        lines.append(
            "- **Increase direct scenario coverage to meet the breadth target:** "
            + ", ".join(f"`{task['task']}`" for task in low_breadth) + ".")
    if weak_tasks:
        lines.append(
            "- **Improve observed performance:** "
            + ", ".join(f"`{task['task']}`" for task in weak_tasks) + ".")

    signals = _improvement_signals(matrix)
    lines.extend(["", "### Observed improvement signals", ""])
    lines.append(
        "These are the lowest observed evidence slices in this run, not failure "
        "verdicts or claims outside the assessed scope.")
    for item in signals["dimensions"]:
        lines.append(
            f"- **{item['area_label']} / {item['dimension_label']}:** "
            f"{item['mean']:.3f}/4 across {item['n']} ratings.")
    for item in signals["families"]:
        lines.append(
            f"- **Scenario family `{item['label']}`:** "
            f"{item['mean']:.3f}/4 across "
            f"{item['distinct_scenarios']} distinct scenarios.")
    if not signals["dimensions"] and not signals["families"]:
        lines.append("- No observed slice fell below the reporting threshold.")

    lines.extend(["", "### What the evidence shows", ""])
    if matrix.get("run_purpose") == run_mode.ENGINEERING_EVALUATION:
        for row in summary["observed"]:
            lines.append(
                f"- **Observed:** `{row['label']}` — evidence mean "
                f"{row['evidence_mean']:.3f} across "
                f"{row['distinct_scenarios']} distinct scenarios.")
    else:
        if summary["demonstrated"]:
            for row in summary["demonstrated"]:
                lines.append(
                    f"- **Demonstrated:** `{row['label']}` — evidence mean "
                    f"{row['evidence_mean']:.3f} across "
                    f"{row['distinct_scenarios']} distinct scenarios.")
        if summary["provisional"]:
            lines.append(
                "- **Observed, but not demonstrated:** "
                + ", ".join(
                    f"`{row['label']}`" for row in summary["provisional"])
                + ". These rows are signals for investigation, not formal "
                  "qualification claims.")
    if summary["unassessed_areas"]:
        lines.append("- **Not assessed in this run:** "
                     + ", ".join(f"`{area}`" for area in summary["unassessed_areas"])
                     + ". No claim is made for these areas.")

    limited_fit = [task for task in matrix["tasks"]
                   if task.get("observed_performance") is not None
                   and (_task_breadth_percent(task) or 0) < 50]
    strong_fit = [task for task in matrix["tasks"]
                  if task.get("observed_performance") is not None
                  and task not in limited_fit
                  and task["observed_performance"] / 4 * 100 >= 75]
    review_fit = [task for task in matrix["tasks"]
                  if task.get("observed_performance") is not None
                  and task not in limited_fit
                  and 50 <= task["observed_performance"] / 4 * 100 < 75]
    weak_fit = [task for task in matrix["tasks"]
                if task.get("observed_performance") is not None
                and task not in limited_fit
                and task["observed_performance"] / 4 * 100 < 50]
    lines.extend(["", "### Engineering Fit Summary", ""])
    lines.append("Evidence-derived fit is informational and does not create "
                 "qualification or deployment authority.")
    lines.extend(["", "**Strong observed fit**", ""])
    lines.extend(
        f"- `{task['task_id']} — {task['task']}`: "
        f"{task['observed_performance'] / 4 * 100:.0f}% observed performance."
        for task in strong_fit)
    if not strong_fit:
        lines.append("- None.")
    lines.extend(["", "**Observed score, limited evidence**", ""])
    lines.extend(
        f"- `{task['task_id']} — {task['task']}`: "
        f"{task['observed_performance'] / 4 * 100:.0f}% observed performance; "
        f"{(_task_breadth_percent(task) or 0):.0f}% scenario breadth."
        for task in limited_fit)
    if not limited_fit:
        lines.append("- None.")
    lines.extend(["", "**Use with engineering review**", ""])
    lines.extend(
        f"- `{task['task_id']} — {task['task']}`: "
        f"{task['observed_performance'] / 4 * 100:.0f}% observed performance."
        for task in review_fit)
    if not review_fit:
        lines.append("- None.")
    lines.extend(["", "**Weak observed fit**", ""])
    lines.extend(
        f"- `{task['task_id']} — {task['task']}`: "
        f"{task['observed_performance'] / 4 * 100:.0f}% observed performance."
        for task in weak_fit)
    if not weak_fit:
        lines.append("- None.")
    lines.extend(["", "**Human evaluation (optional assurance)**", ""])
    lines.append(f"- {_human_evaluation_label(matrix)}.")
    lines.append("- For qualification-bounded operational guidance, supply an "
                 "active Qualification Record explicitly to `aies guidance`.")
    lines.extend(["", "### Evidence traceability", ""])
    for row in summary["observed"]:
        lines.append(f"- `{row['label']}`: {', '.join(f'`{x}`' for x in row['scenario_ids'])}; "
                     f"raters: {', '.join(row['raters']) or 'not recorded'}.")
    lines.append("")
    return "\n".join(lines)


def render_capability_summary_html(matrix: dict, *, sort_by: str = "performance",
                                   descending: bool = True) -> str:
    """Render the same bounded summary for the evidence-package HTML view."""
    summary = capability_summary(matrix)
    task_rows = "".join(
        "<tr><td>" + html.escape(f"{task['task_id']} {task['task']}") + "</td><td>" +
        html.escape("not assessed" if task["observed_performance"] is None else
                    f"{_bar(task['observed_performance'] / 4 * 100)} {task['observed_performance'] / 4 * 100:.0f}%") +
        "</td><td>" + html.escape(_scenario_breadth(task)) +
        "</td><td>" + html.escape(_assurance_label(task)) +
        "</td><td>" + html.escape(_task_sample(task)) +
        "</td><td>" + html.escape(task.get("engineering_status", "not assessed")) +
        "</td><td>" + html.escape(_human_evaluation_label(matrix)) +
        "</td></tr>"
        for task in sorted_tasks(matrix, sort_by, descending)
    )
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in (
            row["label"],
            "—" if row["evidence_mean"] is None else f"{row['evidence_mean']:.3f}",
            row["distinct_scenarios"],
            f"{row['rating_observations']}/{row['minimum_observations']}",
            row["adequacy"],
        )) + "</tr>"
        for row in summary["observed"]
    ) or "<tr><td colspan='5'>No traceable scored scenario-family evidence.</td></tr>"
    observed = ", ".join(
        task["task"] for task in summary["engineering_assessed_tasks"]) or "None"
    not_assessed_tasks = ", ".join(task["task"] for task in summary["task_not_assessed"]) or "None"
    unassessed = ", ".join(summary["unassessed_areas"]) or "None"
    limited_fit = [task for task in matrix["tasks"]
                   if task.get("observed_performance") is not None
                   and (_task_breadth_percent(task) or 0) < 50]
    strong_fit = [task for task in matrix["tasks"]
                  if task.get("observed_performance") is not None
                  and task not in limited_fit
                  and task["observed_performance"] / 4 * 100 >= 75]
    review_fit = [task for task in matrix["tasks"]
                  if task.get("observed_performance") is not None
                  and task not in limited_fit
                  and 50 <= task["observed_performance"] / 4 * 100 < 75]
    weak_fit = [task for task in matrix["tasks"]
                if task.get("observed_performance") is not None
                and task not in limited_fit
                and task["observed_performance"] / 4 * 100 < 50]
    def fit_items(tasks):
        return "".join(
            f"<li><code>{html.escape(task['task_id'] + ' — ' + task['task'])}</code>: "
            f"{task['observed_performance'] / 4 * 100:.0f}% observed performance.</li>"
            for task in tasks) or "<li>None.</li>"
    signals = _improvement_signals(matrix)
    signal_items = "".join(
        "<li><strong>" + html.escape(
            f"{item['area_label']} / {item['dimension_label']}") +
        f":</strong> {item['mean']:.3f}/4 across {item['n']} ratings.</li>"
        for item in signals["dimensions"])
    signal_items += "".join(
        "<li><strong>Scenario family <code>" +
        html.escape(item["label"]) + "</code>:</strong> "
        f"{item['mean']:.3f}/4 across "
        f"{item['distinct_scenarios']} distinct scenarios.</li>"
        for item in signals["families"])
    signal_items = signal_items or (
        "<li>No observed slice fell below the reporting threshold.</li>")
    return f"""
<h2>Engineering Capability Matrix (ECM)</h2>
<p class='banner nondec'>INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.</p>
<p>Derived solely from the scored scenario evidence in this run. It does not infer capability for tasks that were not assessed.</p>
<h3>Task Capability Profile</h3>
<p>Sorted by {html.escape(sort_by)} {"descending" if descending else "ascending"}. Select any column heading to re-sort.</p>
<table class='sortable'><thead><tr><th>Task</th><th>Observed performance</th><th>Scenario breadth</th><th>Evidence assurance</th><th>Evidence</th><th>Engineering status</th><th>Human eval</th></tr></thead><tbody>{task_rows}</tbody></table>
<p>Observed performance is an unweighted EV mean. Scenario breadth measures distinct directly mapped scored scenarios against the task target; repeats do not increase it. Breadth is not reviewer, mapping, calibration, or human assurance. Automated scores are usable Engineering Evaluation evidence.</p>
<details><summary>Scenario-family evidence and traceability ({len(summary['observed'])} rows)</summary>
<table class='sortable'><thead><tr><th>Scenario family</th><th>Evidence mean (0–4)</th><th>Distinct scenarios</th><th>Ratings</th><th>Adequacy</th></tr></thead><tbody>{rows}</tbody></table>
</details>
<h3>Strength patterns and evidence gaps</h3>
<ul><li><strong>Observed engineering tasks:</strong> {html.escape(observed)}.</li><li><strong>Collect direct evidence before making a claim:</strong> {html.escape(not_assessed_tasks)}.</li><li><strong>Unassessed competency areas:</strong> {html.escape(unassessed)}.</li></ul>
<h3>Observed improvement signals</h3>
<p>Lowest observed evidence slices in this run; not failure verdicts or claims outside the assessed scope.</p><ul>{signal_items}</ul>
<h3>Engineering Fit Summary</h3>
<p>Evidence-derived fit is informational and does not create qualification or deployment authority.</p>
<p><strong>Strong observed fit:</strong></p><ul>{fit_items(strong_fit)}</ul>
<p><strong>Observed score, limited evidence:</strong></p><ul>{fit_items(limited_fit)}</ul>
<p><strong>Use with engineering review:</strong></p><ul>{fit_items(review_fit)}</ul>
<p><strong>Weak observed fit:</strong></p><ul>{fit_items(weak_fit)}</ul>
<p><strong>Human evaluation:</strong> {html.escape(_human_evaluation_label(matrix))}. Optional assurance; not a prerequisite for engineering evaluation.</p>
<p class='muted'>Standalone detail: <a href='engineering-capability-matrix.html'>Engineering Capability Matrix</a>.</p>{_SORTABLE_SCRIPT}
"""


def write_matrix(matrix: dict, format: str = "markdown", *,
                 sort_by: str = "performance",
                 descending: bool = True) -> Path:
    """Write a renderer-owned ECM artifact beside its source run."""
    suffix = {"markdown": "md", "json": "json", "html": "html"}[format]
    path = workspace.run_dir(matrix["run_id"]) / f"engineering-capability-matrix.{suffix}"
    if format == "json":
        content = json.dumps(matrix, indent=2) + "\n"
    elif format == "html":
        content = render_html(matrix, sort_by=sort_by, descending=descending)
    else:
        content = render_markdown(
            matrix, sort_by=sort_by, descending=descending)
    workspace.write_view(path, content)
    return path

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

from . import compare, constants as C, rating, runner, task_mappings, workspace


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


def engineering_capability_matrix(ref: str) -> dict:
    """Return a factual ECM v0 view for an aggregated run or deployment.

    Values are evidence summaries only. ``evidence_mean`` is the unweighted
    mean of the six recorded EV scores, included to help inspection; it is not
    a qualification score, competency level, or recommendation.
    """
    from . import evaluation

    pkg = compare._resolve_package(ref)
    run_id = pkg["run_id"]
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
    })
    mapping = task_mappings.load()
    task_names = task_mappings.task_names(mapping)
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
        for task_id in task_mappings.tasks_for_scenario(scenario, mapping):
            task = task_grouped[task_id]
            task["scenario_ids"].add(scenario_id)
            task["response_records"].add(response_name)
            task["areas"].add(area)
            if scores:
                task["scores"].append(sum(scores.values()) / len(scores))
                if record_admitted:
                    task["admitted_scores"].append(sum(scores.values()) / len(scores))
            if provenance.get("rater"):
                task["raters"].add(provenance["rater"])
            if provenance.get("rater_kind"):
                task["rater_kinds"].add(provenance["rater_kind"])

    rows = []
    for (area, family), data in sorted(grouped.items()):
        area_evidence = pkg["areas"].get(area, {})
        n = len(data["scores"])
        minimum = area_evidence.get("min_sample", 0)
        decisional = bool(area_evidence.get("decisional")) and n >= minimum
        rows.append({
            "area": area,
            "scenario_family": family,
            "label": f"{C.competency_label(area)} / {family}",
            "scenario_ids": sorted(data["scenario_ids"]),
            "distinct_scenarios": len(data["scenario_ids"]),
            "distinct_responses": len(data["response_records"]),
            "rating_observations": n,
            "minimum_observations": minimum,
            "adequacy": _adequacy(n, minimum, decisional),
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
            tasks.append({"task_id": task_id, "task": task_name, "scenario_ids": [],
                          "areas": [], "distinct_scenarios": 0, "distinct_responses": 0,
                          "rating_observations": 0, "minimum_observations": None,
                          "admitted_rating_observations": 0, "observed_performance": None,
                          "coverage_percent": None, "status": "not assessed",
                          "decision_semantics": "not-applicable-no-evidence",
                          "raters": [], "rater_kinds": []})
            continue
        n = len(data["scores"])
        minimum = max((pkg["areas"][area]["min_sample"] for area in data["areas"]), default=0)
        performance = round(sum(data["scores"]) / n, 3) if n else None
        tasks.append({"task_id": task_id, "task": task_name,
                      "scenario_ids": sorted(data["scenario_ids"]), "areas": sorted(data["areas"]),
                      "distinct_scenarios": len(data["scenario_ids"]),
                      "distinct_responses": len(data["response_records"]),
                      "rating_observations": n, "minimum_observations": minimum,
                      "admitted_rating_observations": len(data["admitted_scores"]),
                      "observed_performance": performance, "coverage_percent": None,
                      # A competency-area sample minimum is not a task-level
                      # decision threshold. Until ECM task semantics are
                      # governed, mapped evidence can be observed but cannot
                      # be labelled demonstrated or emitted under Use.
                      "status": "observed",
                      "decision_semantics": "ungoverned-task-threshold",
                      "raters": sorted(data["raters"]), "rater_kinds": sorted(data["rater_kinds"])})

    return {
        "kind": "engineering-capability-matrix-v1",
        "status": "informational",
        "mapping": {
            "kind": mapping["id"],
            "version": mapping["version"],
            "scope": "versioned scenario-to-Engineering-Task registry",
        },
        "run_id": run_id,
        "subject": (pkg.get("subject") or {}).get("id", pkg["model"]["registry_id"]),
        "subject_kind": pkg.get("subject_kind", "ai"),
        "risk_tier": pkg["risk_tier"],
        "profile": pkg["profile"],
        "rater_kinds": pkg.get("rater_kinds", []),
        "engineering_evaluation": evaluation.summarize(run_id),
        "rows": rows,
        "tasks": tasks,
        "limitations": [
            "Informational only; this matrix is not qualification evidence, a grant, or deployment authorization.",
            "Task rows are derived from the versioned scenario-to-task mapping registry; scenario-family rows remain the traceable source evidence.",
            "Evidence mean is an unweighted inspection statistic, not a competency level or recommendation.",
            "Task decision semantics are not yet governed; no task row may be labelled demonstrated or emitted as a Use recommendation.",
            "A non-decisional row requires more independently scored evidence; repeats do not establish task breadth.",
            "Automated ratings can complete the engineering evaluation; optional human evaluation adds assurance but is not required to generate this ECM.",
        ],
    }


def _human_evaluation_label(matrix: dict) -> str:
    record = ((matrix.get("engineering_evaluation") or {}).get(
        "human_evaluation") or {})
    if record.get("status") == "reviewed":
        return f"☑ Reviewed — {record.get('evaluator') or 'named human'}"
    return "☐ Not reviewed (optional)"


def render_markdown(matrix: dict) -> str:
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
        "| Task | Observed performance | Direct evidence sample | Qualification evidence | Status |",
        "|---|---|---|---:|---|",
    ]
    for task in matrix["tasks"]:
        performance = ("not assessed" if task["observed_performance"] is None
                       else _bar(task["observed_performance"] / 4 * 100)
                            + f" {task['observed_performance'] / 4 * 100:.0f}%")
        lines.append(f"| {task['task_id']} {task['task']} | {performance} | {_task_sample(task)} | "
                     f"{_task_evidence(task)} | {_task_status(task)} |")
    lines.extend([
        "",
        "Mean reviewer score is an unweighted informational EV mean. Evidence coverage is the "
        "raw observation share of the applicable AESQS minimum; it is not statistical confidence "
        "and does not admit advisory ratings into qualification scoring.",
        "",
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
    return (f"{task['admitted_rating_observations']} admitted "
            f"(area reference: {minimum})")


def _task_sample(task: dict) -> str:
    """Describe direct task breadth without pretending it has its own gate."""
    if task["minimum_observations"] is None:
        return "no direct mapped evidence"
    return (f"{task['distinct_scenarios']} scenarios; "
            f"{task['rating_observations']} raw ratings")


def _task_status(task: dict) -> str:
    if task["status"] == "not assessed":
        return "not assessed"
    if task["admitted_rating_observations"] == 0:
        return "evaluated — automated"
    return task["status"]


def render_html(matrix: dict) -> str:
    """Render a compact, self-contained engineer-facing ECM artifact."""
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in (
            row["label"],
            "—" if row["evidence_mean"] is None else f"{row['evidence_mean']:.3f}",
            row["distinct_scenarios"], row["distinct_responses"],
            f"{row['rating_observations']}/{row['minimum_observations']}", row["adequacy"],
        )) + "</tr>"
        for row in matrix["rows"]
    ) or "<tr><td colspan='6'>No traceable scored scenario-family evidence.</td></tr>"
    limits = "".join(f"<li>{html.escape(x)}</li>" for x in matrix["limitations"])
    task_rows = "".join(
        "<tr><td>" + html.escape(f"{task['task_id']} {task['task']}") + "</td><td>" +
        html.escape("not assessed" if task["observed_performance"] is None else
                    f"{_bar(task['observed_performance'] / 4 * 100)} {task['observed_performance'] / 4 * 100:.0f}%") +
        "</td><td>" + html.escape(_task_sample(task)) +
        "</td><td>" + html.escape(_task_evidence(task)) +
        f"</td><td>{html.escape(_task_status(task))}</td></tr>"
        for task in matrix["tasks"]
    )
    summary = capability_summary(matrix)
    observed = ", ".join(task["task"] for task in summary["task_observed"]) or "None"
    unassessed = ", ".join(task["task"] for task in summary["task_not_assessed"]) or "None"
    automated = sum(task["rating_observations"] for task in matrix["tasks"]
                    if task["admitted_rating_observations"] == 0)
    human_label = _human_evaluation_label(matrix)
    return f"""<!doctype html><html lang='en'><meta charset='utf-8'>
<title>Engineering Capability Matrix — {html.escape(matrix['subject'])}</title>
<style>body{{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:0 1rem;color:#17202a}} table{{border-collapse:collapse;width:100%;margin:.75rem 0}}th,td{{border:1px solid #cbd5e1;padding:.5rem;text-align:left;vertical-align:top}}th{{background:#eaf2f8}}.notice{{padding:.75rem;background:#fff3cd;font-weight:600}}.summary{{padding:.8rem 1rem;background:#f8fafc;border-left:4px solid #64748b}}details{{margin:1.25rem 0}}summary{{cursor:pointer;font-weight:650}}</style>
<h1>Engineering Capability Matrix (ECM)</h1><p class='notice'>INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.</p>
<p><b>Subject:</b> {html.escape(matrix['subject'])}<br><b>Run:</b> {html.escape(matrix['run_id'])}<br><b>Scope:</b> {html.escape(C.risk_tier_label(matrix['risk_tier']))} · {html.escape(matrix['profile'])}<br><b>Human evaluation:</b> {html.escape(human_label)}</p>
<p class='summary'><strong>At a glance:</strong> {len(summary['task_demonstrated'])} demonstrated task(s), {len(summary['task_observed'])} observed task(s), and {len(summary['task_not_assessed'])} task(s) without direct evidence. {automated} automated rating observation(s) complete the engineering evaluation where coverage is complete; formal qualification admission is separate.</p>
<h2>Task Capability Profile</h2><table><thead><tr><th>Task</th><th>Observed performance</th><th>Direct evidence sample</th><th>Qualification evidence</th><th>Status</th></tr></thead><tbody>{task_rows}</tbody></table>
<p>Observed performance is an unweighted EV mean. A task has no task-specific pass threshold yet: scenario breadth is shown directly. The area reference is not a task qualification score; advisory ratings never become qualification evidence until the reviewer is admitted.</p>
<h2>Evidence Summary</h2><ul><li><strong>Automated evaluation observations:</strong> {html.escape(observed)}.</li><li><strong>Direct evidence still needed:</strong> {html.escape(unassessed)}.</li><li><strong>Human evaluation:</strong> {html.escape(human_label)}.</li></ul>
<details><summary>Scenario-family evidence and traceability ({len(matrix['rows'])} rows)</summary><table><thead><tr><th>Evidence family</th><th>Mean EV score</th><th>Scenarios</th><th>Responses</th><th>Ratings</th><th>Adequacy</th></tr></thead><tbody>{rows}</tbody></table></details>
<h2>Limitations</h2><ul>{limits}</ul></html>"""


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
    task_demonstrated = [task for task in task_rows if task["status"] == "demonstrated"]
    task_observed = [task for task in task_rows if task["status"] == "observed"]
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
        "task_not_assessed": task_not_assessed,
        "not_recommended": [
            "Autonomous production changes: this informational matrix cannot authorize deployment.",
            "Any task outside the assessed scenario families: this run contains no direct evidence for it.",
        ],
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
        "| Task | Observed performance | Direct evidence sample | Qualification evidence | Status |",
        "|---|---|---|---:|---|",
    ]
    for task in matrix["tasks"]:
        performance = ("not assessed" if task["observed_performance"] is None
                       else _bar(task["observed_performance"] / 4 * 100)
                            + f" {task['observed_performance'] / 4 * 100:.0f}%")
        lines.append(f"| {task['task_id']} {task['task']} | {performance} | {_task_sample(task)} | "
                     f"{_task_evidence(task)} | {_task_status(task)} |")
    lines.extend([
        "",
        "Observed performance is an unweighted EV mean. A task has no task-specific pass threshold yet: scenario breadth is shown directly. The area reference is not a task qualification score; advisory ratings never become qualification evidence until the reviewer is admitted.",
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
    if summary["task_demonstrated"]:
        for task in summary["task_demonstrated"]:
            lines.append(f"- **Demonstrated:** `{task['task']}` — observed performance "
                         f"{task['observed_performance'] / 4 * 100:.0f}% with "
                         f"{task['rating_observations']} scored observations.")
    if summary["task_observed"]:
        for task in summary["task_observed"]:
            lines.append(f"- **Observed only:** `{task['task']}` — "
                         f"{task['observed_performance'] / 4 * 100:.0f}% observed performance across "
                         f"{task['distinct_scenarios']} distinct mapped scenarios. Task-level "
                         "adequacy is not yet governed; do not treat this as a demonstrated capability.")
    if not summary["task_demonstrated"] and not summary["task_observed"]:
        lines.append("- No mapped engineering task has traceable scored evidence in this run.")

    lines.extend(["", "### Improvement and evidence gaps", ""])
    if summary["task_not_assessed"]:
        lines.append("- **Collect direct evidence before making a claim:** "
                     + ", ".join(f"`{task['task']}`" for task in summary["task_not_assessed"]) + ".")
    if summary["task_observed"]:
        lines.append("- **Increase breadth and independent scoring for observed tasks:** "
                     + ", ".join(f"`{task['task']}`" for task in summary["task_observed"]) + ".")

    lines.extend(["", "### What the evidence shows", ""])
    if summary["demonstrated"]:
        for row in summary["demonstrated"]:
            lines.append(f"- **Demonstrated:** `{row['label']}` — evidence mean "
                         f"{row['evidence_mean']:.3f} across {row['distinct_scenarios']} "
                         "distinct scenarios.")
    if summary["provisional"]:
        lines.append("- **Observed, but not demonstrated:** "
                     + ", ".join(f"`{row['label']}`" for row in summary["provisional"])
                     + ". These rows are below the required evidence threshold; they are "
                       "signals for investigation, not capability claims.")
    if summary["unassessed_areas"]:
        lines.append("- **Not assessed in this run:** "
                     + ", ".join(f"`{area}`" for area in summary["unassessed_areas"])
                     + ". No claim is made for these areas.")

    lines.extend(["", "### Deployment Guidance", "", "**Recommended**", ""])
    if summary["task_demonstrated"]:
        lines.extend(f"- `{task['task']}` — only within its assessed scope and the qualification authority's approved autonomy envelope."
                     for task in summary["task_demonstrated"])
    else:
        lines.append("- None. This run does not provide decisional task-level evidence for a recommendation.")
    lines.extend(["", "**Optional human validation (adds assurance)**", ""])
    if summary["task_observed"]:
        lines.extend(f"- `{task['task']}` — automated evaluation is complete where coverage is complete; human validation remains optional."
                     for task in summary["task_observed"])
    else:
        lines.append("- None.")
    lines.extend(["", "**Not recommended from this evidence**", ""])
    lines.extend(f"- {item}" for item in summary["not_recommended"])
    lines.extend(["", "### Evidence traceability", ""])
    for row in summary["observed"]:
        lines.append(f"- `{row['label']}`: {', '.join(f'`{x}`' for x in row['scenario_ids'])}; "
                     f"raters: {', '.join(row['raters']) or 'not recorded'}.")
    lines.append("")
    return "\n".join(lines)


def render_capability_summary_html(matrix: dict) -> str:
    """Render the same bounded summary for the evidence-package HTML view."""
    summary = capability_summary(matrix)
    task_rows = "".join(
        "<tr><td>" + html.escape(f"{task['task_id']} {task['task']}") + "</td><td>" +
        html.escape("not assessed" if task["observed_performance"] is None else
                    f"{_bar(task['observed_performance'] / 4 * 100)} {task['observed_performance'] / 4 * 100:.0f}%") +
        "</td><td>" + html.escape(_task_sample(task)) +
        "</td><td>" + html.escape(_task_evidence(task)) +
        f"</td><td>{html.escape(_task_status(task))}</td></tr>"
        for task in matrix["tasks"]
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
    observed = ", ".join(task["task"] for task in summary["task_observed"]) or "None"
    not_assessed_tasks = ", ".join(task["task"] for task in summary["task_not_assessed"]) or "None"
    unassessed = ", ".join(summary["unassessed_areas"]) or "None"
    review = "".join(f"<li><code>{html.escape(task['task'])}</code> — automated evaluation is complete where coverage is complete; human validation remains optional.</li>"
                     for task in summary["task_observed"]) or "<li>None.</li>"
    return f"""
<h2>Engineering Capability Matrix (ECM)</h2>
<p class='banner nondec'>INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.</p>
<p>Derived solely from the scored scenario evidence in this run. It does not infer capability for tasks that were not assessed.</p>
<h3>Task Capability Profile</h3>
<table><tr><th>Task</th><th>Observed performance</th><th>Direct evidence sample</th><th>Qualification evidence</th><th>Status</th></tr>{task_rows}</table>
<p>Observed performance is an unweighted EV mean. A task has no task-specific pass threshold yet: scenario breadth is shown directly. The area reference is not a task qualification score; advisory ratings never become qualification evidence until the reviewer is admitted.</p>
<details><summary>Scenario-family evidence and traceability ({len(summary['observed'])} rows)</summary>
<table><tr><th>Scenario family</th><th>Evidence mean (0–4)</th><th>Distinct scenarios</th><th>Ratings</th><th>Adequacy</th></tr>{rows}</table>
</details>
<h3>Strength patterns and evidence gaps</h3>
<ul><li><strong>Observed, but not demonstrated:</strong> {html.escape(observed)}.</li><li><strong>Collect direct evidence before making a claim:</strong> {html.escape(not_assessed_tasks)}.</li><li><strong>Unassessed competency areas:</strong> {html.escape(unassessed)}.</li></ul>
<h3>Deployment Guidance</h3>
<p><strong>Recommended:</strong> None unless a task row is demonstrated and the qualification authority has approved the applicable autonomy envelope.</p>
<p><strong>Optional human validation (adds assurance):</strong></p><ul>{review}</ul>
<p><strong>Not recommended from this evidence:</strong> autonomous production changes, or any task outside the assessed scenario families.</p>
<p class='muted'>Standalone detail: <a href='engineering-capability-matrix.html'>Engineering Capability Matrix</a>.</p>
"""


def write_matrix(matrix: dict, format: str = "markdown") -> Path:
    """Write a renderer-owned ECM artifact beside its source run."""
    suffix = {"markdown": "md", "json": "json", "html": "html"}[format]
    path = workspace.run_dir(matrix["run_id"]) / f"engineering-capability-matrix.{suffix}"
    if format == "json":
        content = json.dumps(matrix, indent=2) + "\n"
    elif format == "html":
        content = render_html(matrix)
    else:
        content = render_markdown(matrix)
    path.write_text(content, encoding="utf-8")
    return path

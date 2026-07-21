"""Engineering Capability Matrix v0 — read-only family-level evidence views.

This is deliberately *not* a qualification result, a task taxonomy, or a
deployment grant. It groups the scenarios actually scored in an aggregated run
by existing ``area`` + ``family`` metadata, exposes the evidence behind each
row, and labels sample sufficiency. A family is a scenario-design grouping, not
yet a normative engineering-task identifier (ADR-0006, Proposed).
"""

from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path

from . import compare, rating, runner, workspace


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
    pkg = compare._resolve_package(ref)
    run_id = pkg["run_id"]
    response_dir = workspace.run_dir(run_id) / "responses"
    responses = {p.name: workspace.read_json(p) for p in response_dir.glob("*.json")}
    scenario_index = _scenario_index(set(pkg["areas"]))
    grouped: dict[tuple[str, str], dict] = defaultdict(lambda: {
        "scenario_ids": set(), "response_records": set(), "scores": [],
        "raters": set(), "rater_kinds": set(),
    })

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
        if provenance.get("rater"):
            row["raters"].add(provenance["rater"])
        if provenance.get("rater_kind"):
            row["rater_kinds"].add(provenance["rater_kind"])

    rows = []
    for (area, family), data in sorted(grouped.items()):
        area_evidence = pkg["areas"].get(area, {})
        n = len(data["scores"])
        minimum = area_evidence.get("min_sample", 0)
        decisional = bool(area_evidence.get("decisional")) and n >= minimum
        rows.append({
            "area": area,
            "scenario_family": family,
            "label": f"{area} / {family}",
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

    return {
        "kind": "engineering-capability-matrix-v0",
        "status": "informational",
        "mapping": {
            "kind": "existing-scenario-family",
            "version": "v0",
            "scope": "area plus scenario family; not a normative task taxonomy",
        },
        "run_id": run_id,
        "subject": pkg["model"]["registry_id"],
        "subject_kind": pkg.get("subject_kind", "ai"),
        "risk_tier": pkg["risk_tier"],
        "profile": pkg["profile"],
        "rater_kinds": pkg.get("rater_kinds", []),
        "rows": rows,
        "limitations": [
            "Informational only; this matrix is not qualification evidence, a grant, or deployment authorization.",
            "Rows use existing scenario family metadata, not a standardized engineering-task taxonomy.",
            "Evidence mean is an unweighted inspection statistic, not a competency level or recommendation.",
            "A non-decisional row requires more independently scored evidence; repeats do not establish task breadth.",
        ],
    }


def render_markdown(matrix: dict) -> str:
    """Render a human-readable ECM v0 Markdown artifact."""
    lines = [
        "# Engineering Capability Matrix (ECM v0)",
        "",
        "> **INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.**",
        "",
        f"Subject: `{matrix['subject']}`  ",
        f"Run: `{matrix['run_id']}`  ",
        f"Scope: {matrix['risk_tier']} · {matrix['profile']} profile  ",
        f"Mapping: {matrix['mapping']['scope']}",
        "",
        "| Evidence family | Mean EV score | Scenarios | Responses | Ratings | Adequacy |",
        "|---|---:|---:|---:|---:|---|",
    ]
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


def render_html(matrix: dict) -> str:
    """Render a compact, self-contained HTML ECM artifact."""
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
    return f"""<!doctype html><html lang='en'><meta charset='utf-8'>
<title>Engineering Capability Matrix — {html.escape(matrix['subject'])}</title>
<style>body{{font:16px system-ui;max-width:960px;margin:3rem auto;padding:0 1rem;color:#17202a}} table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #cbd5e1;padding:.5rem;text-align:left}}th{{background:#eaf2f8}}.notice{{padding:.75rem;background:#fff3cd;font-weight:600}}</style>
<h1>Engineering Capability Matrix (ECM v0)</h1><p class='notice'>INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.</p>
<p><b>Subject:</b> {html.escape(matrix['subject'])}<br><b>Run:</b> {html.escape(matrix['run_id'])}<br><b>Scope:</b> {html.escape(matrix['risk_tier'])} · {html.escape(matrix['profile'])}</p>
<table><thead><tr><th>Evidence family</th><th>Mean EV score</th><th>Scenarios</th><th>Responses</th><th>Ratings</th><th>Adequacy</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Limitations</h2><ul>{limits}</ul></html>"""


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

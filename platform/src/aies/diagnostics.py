"""Informational grounding, hallucination, and fabrication diagnostics.

These observations are reviewer evidence, not a seventh EV dimension and not a
qualification gate. They remain source-separated and explicitly unavailable
when a reviewer did not perform the structured grounding check.
"""
from __future__ import annotations

import html
import json

from . import constants as C, workspace

DIAGNOSTIC_SCHEMA = 2
CATEGORIES = {
    "unsupported_assertions": {
        "title": "Unsupported assertions", "maps_to": ["EV1", "EV6"]},
    "fabricated_apis_or_entities": {
        "title": "Fabricated APIs or entities", "maps_to": ["EV1", "EV3"]},
    "invalid_citations_or_provenance": {
        "title": "Invalid citations or provenance", "maps_to": ["EV1", "EV6"]},
    "false_success_or_test_claims": {
        "title": "False success or test claims", "maps_to": ["EV1", "EV6"]},
}


def normalize(value) -> dict | None:
    """Validate one optional diagnostic observation without inventing data."""
    if value is None:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("grounding_assessed"), bool):
        raise ValueError("grounding diagnostics require boolean grounding_assessed")
    out = {
        "diagnostic_schema": DIAGNOSTIC_SCHEMA,
        "grounding_assessed": value["grounding_assessed"],
    }
    for category in CATEGORIES:
        count = value.get(category, 0)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"grounding diagnostic {category} must be a non-negative integer")
        out[category] = count
    applicability = value.get("abstention_applicable")
    if applicability is not None and not isinstance(applicability, bool):
        raise ValueError("abstention_applicable must be true, false, or null")
    abstention = value.get("appropriate_abstention")
    if abstention is not None and not isinstance(abstention, bool):
        raise ValueError("appropriate_abstention must be true, false, or null")
    if applicability is True and abstention is None:
        raise ValueError(
            "appropriate_abstention must be true or false when abstention applies")
    if applicability is False and abstention is not None:
        raise ValueError(
            "appropriate_abstention must be null when abstention does not apply")
    out["abstention_applicable"] = applicability
    out["appropriate_abstention"] = abstention
    notes = value.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]
    if not isinstance(notes, list):
        raise ValueError("grounding diagnostic notes must be a list")
    out["notes"] = [str(note) for note in notes]
    return out


def _source_view(records: list[dict], total_responses: int) -> dict:
    observations = []
    for record in records:
        diagnostic = record.get("grounding_diagnostics")
        if diagnostic and diagnostic.get("grounding_assessed") is True:
            observations.append((record, diagnostic))
    issue_observations = 0
    totals = {category: 0 for category in CATEGORIES}
    abstention_evaluated = appropriate_abstentions = 0
    abstention_not_applicable = abstention_ambiguous_legacy = 0
    response_names = set()
    for record, diagnostic in observations:
        response_names.add(record.get("rates_response"))
        issue = False
        for category in CATEGORIES:
            totals[category] += diagnostic[category]
            issue = issue or diagnostic[category] > 0
        applicability = diagnostic.get("abstention_applicable")
        abstention = diagnostic.get("appropriate_abstention")
        if applicability is True:
            abstention_evaluated += 1
            if abstention:
                appropriate_abstentions += 1
            else:
                issue = True
        elif applicability is False:
            abstention_not_applicable += 1
        elif abstention is True:
            # A legacy true value still unambiguously records an appropriate
            # abstention. A legacy false value cannot distinguish "not
            # applicable" from "inappropriate" and therefore cannot prove an
            # issue.
            abstention_evaluated += 1
            appropriate_abstentions += 1
        elif abstention is False:
            abstention_ambiguous_legacy += 1
        issue_observations += int(issue)
    n = len(observations)
    return {
        "status": "assessed" if n else "unavailable",
        "diagnostic_observations": n,
        "responses_assessed": len(response_names),
        "responses_total": total_responses,
        "coverage_percent": round(len(response_names) / total_responses * 100, 1)
        if total_responses else 0.0,
        "observations_with_issues": issue_observations,
        "observed_grounding_reliability_percent": round((n - issue_observations) / n * 100, 1)
        if n else None,
        "category_counts": totals,
        "abstention": {
            "evaluated": abstention_evaluated,
            "appropriate": appropriate_abstentions,
            "inappropriate": abstention_evaluated - appropriate_abstentions,
            "not_applicable": abstention_not_applicable,
            "ambiguous_legacy": abstention_ambiguous_legacy,
        },
        "raters": sorted({
            str((record.get("provenance") or {}).get("rater"))
            for record, _ in observations
            if (record.get("provenance") or {}).get("rater")}),
    }


def summarize(run_id: str) -> dict:
    from . import rating

    rdir = workspace.run_dir(run_id)
    response_total = len(list((rdir / "responses").glob("*.json")))
    by_source = {"automated": [], "human": []}
    for record in rating.collect_ratings(run_id):
        kind = (record.get("provenance") or {}).get("rater_kind")
        source = "human" if kind == "human" else "automated"
        by_source[source].append(record)
    sources = {source: _source_view(records, response_total)
               for source, records in by_source.items()}
    return {
        "kind": "grounding-diagnostics",
        "diagnostic_schema": DIAGNOSTIC_SCHEMA,
        "status": "assessed" if any(view["status"] == "assessed"
                                    for view in sources.values()) else "unavailable",
        "run_id": run_id,
        "sources": sources,
        "category_definitions": {
            category: {**detail, "maps_to": [C.identifier_label(code)
                                              for code in detail["maps_to"]]}
            for category, detail in CATEGORIES.items()},
        "qualification_effect": "informational-only; no new EV dimension or gate",
        "limitations": [
            "Counts are structured reviewer observations, not independently verified ground truth.",
            "Automated and human observations are never blended into one score.",
            "Unavailable means the reviewer did not perform the structured check; it never means zero hallucinations.",
            "Legacy appropriate_abstention=false values without an applicability field are ambiguous and are disclosed but not counted as proven issues.",
            "Observed grounding reliability is descriptive and cannot authorize deployment or offset an EV gate.",
        ],
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# Grounding, Hallucination & Fabrication Diagnostics", "",
        "> **INFORMATIONAL REVIEWER OBSERVATIONS — NOT A QUALIFICATION SCORE OR GATE.**", "",
        "| Source | Coverage | Observed grounding reliability | Observations with issues |",
        "|---|---:|---:|---:|",
    ]
    for source, view in summary["sources"].items():
        reliability = ("unavailable" if view["observed_grounding_reliability_percent"] is None
                       else f"{view['observed_grounding_reliability_percent']:.1f}%")
        lines.append(
            f"| {source} | {view['responses_assessed']}/{view['responses_total']} "
            f"({view['coverage_percent']:.1f}%) | {reliability} | "
            f"{view['observations_with_issues']}/{view['diagnostic_observations']} |")
    lines.extend(["", "## Observed issue counts", "",
                  "| Category | Automated | Human | Existing EV mapping |",
                  "|---|---:|---:|---|"])
    for category, definition in summary["category_definitions"].items():
        lines.append(
            f"| {definition['title']} | "
            f"{summary['sources']['automated']['category_counts'][category]} | "
            f"{summary['sources']['human']['category_counts'][category]} | "
            f"{', '.join(definition['maps_to'])} |")
    lines.extend([
        "", "## Abstention observations", "",
        "| Source | Applicable/evaluated | Appropriate | Inappropriate | Not applicable | Legacy ambiguous |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for source, view in summary["sources"].items():
        abstention = view["abstention"]
        lines.append(
            f"| {source} | {abstention['evaluated']} | "
            f"{abstention['appropriate']} | {abstention['inappropriate']} | "
            f"{abstention['not_applicable']} | "
            f"{abstention['ambiguous_legacy']} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in summary["limitations"])
    return "\n".join(lines) + "\n"


def render_html(summary: dict) -> str:
    source_rows = "".join(
        "<tr><td>" + html.escape(source) + "</td><td>" +
        f"{view['responses_assessed']}/{view['responses_total']} ({view['coverage_percent']:.1f}%)" +
        "</td><td>" + ("unavailable" if view["observed_grounding_reliability_percent"] is None
                       else f"{view['observed_grounding_reliability_percent']:.1f}%") +
        f"</td><td>{view['observations_with_issues']}/{view['diagnostic_observations']}</td></tr>"
        for source, view in summary["sources"].items())
    category_rows = "".join(
        f"<tr><td>{html.escape(definition['title'])}</td>"
        f"<td>{summary['sources']['automated']['category_counts'][category]}</td>"
        f"<td>{summary['sources']['human']['category_counts'][category]}</td>"
        f"<td>{html.escape(', '.join(definition['maps_to']))}</td></tr>"
        for category, definition in summary["category_definitions"].items())
    abstention_rows = "".join(
        f"<tr><td>{html.escape(source)}</td>"
        f"<td>{view['abstention']['evaluated']}</td>"
        f"<td>{view['abstention']['appropriate']}</td>"
        f"<td>{view['abstention']['inappropriate']}</td>"
        f"<td>{view['abstention']['not_applicable']}</td>"
        f"<td>{view['abstention']['ambiguous_legacy']}</td></tr>"
        for source, view in summary["sources"].items())
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Grounding Diagnostics</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 24px}}table{{border-collapse:collapse}}th,td{{border:1px solid #ccd4dd;padding:8px 12px}}.banner{{padding:12px;background:#fff3cd;border-left:5px solid #d99b00}}</style></head><body>
<h1>Grounding, Hallucination &amp; Fabrication Diagnostics</h1><p class='banner'><strong>INFORMATIONAL REVIEWER OBSERVATIONS — NOT A QUALIFICATION SCORE OR GATE.</strong></p>
<table><tr><th>Source</th><th>Coverage</th><th>Observed grounding reliability</th><th>Observations with issues</th></tr>{source_rows}</table>
<h2>Observed issue counts</h2><table><tr><th>Category</th><th>Automated</th><th>Human</th><th>Existing EV mapping</th></tr>{category_rows}</table>
<h2>Abstention observations</h2><table><tr><th>Source</th><th>Applicable/evaluated</th><th>Appropriate</th><th>Inappropriate</th><th>Not applicable</th><th>Legacy ambiguous</th></tr>{abstention_rows}</table>
<h2>Limitations</h2><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in summary['limitations'])}</ul>
<p><a href='executive-summary.html'>Executive Summary</a> · <a href='report.html'>Qualification Evidence Package</a></p></body></html>"""


def render_report_section_markdown(summary: dict) -> str:
    lines = [
        "## Grounding, Hallucination & Fabrication Diagnostics", "",
        "> **INFORMATIONAL REVIEWER OBSERVATIONS — NOT A QUALIFICATION SCORE OR GATE.**", "",
        "| Source | Coverage | Observed grounding reliability | Issue observations |",
        "|---|---:|---:|---:|",
    ]
    for source, view in summary["sources"].items():
        reliability = ("unavailable" if view["observed_grounding_reliability_percent"] is None
                       else f"{view['observed_grounding_reliability_percent']:.1f}%")
        lines.append(
            f"| {source} | {view['responses_assessed']}/{view['responses_total']} "
            f"({view['coverage_percent']:.1f}%) | {reliability} | "
            f"{view['observations_with_issues']}/{view['diagnostic_observations']} |")
    lines.extend([
        "", "Unavailable means not assessed, never zero hallucinations. Counts map to existing EV1 — Correctness, EV3 — Safety & Security, and EV6 — Traceability; they do not create a new dimension or gate.",
        "", "Full source-separated detail: [Grounding Diagnostics](grounding-diagnostics.md).", "",
    ])
    return "\n".join(lines)


def render_report_section_html(summary: dict) -> str:
    rows = "".join(
        "<tr><td>" + html.escape(source) + "</td><td>" +
        f"{view['responses_assessed']}/{view['responses_total']} ({view['coverage_percent']:.1f}%)" +
        "</td><td>" + ("unavailable" if view["observed_grounding_reliability_percent"] is None
                       else f"{view['observed_grounding_reliability_percent']:.1f}%") +
        f"</td><td>{view['observations_with_issues']}/{view['diagnostic_observations']}</td></tr>"
        for source, view in summary["sources"].items())
    return f"""<h2>Grounding, Hallucination &amp; Fabrication Diagnostics</h2>
<p class='banner nondec'>INFORMATIONAL REVIEWER OBSERVATIONS — NOT A QUALIFICATION SCORE OR GATE.</p>
<table><tr><th>Source</th><th>Coverage</th><th>Observed grounding reliability</th><th>Issue observations</th></tr>{rows}</table>
<p>Unavailable means not assessed, never zero hallucinations. Diagnostics map to existing EV1 — Correctness, EV3 — Safety &amp; Security, and EV6 — Traceability; they do not create a new dimension or gate.</p>
<p><a href='grounding-diagnostics.html'>Full source-separated grounding diagnostics</a>.</p>"""


def render_json(summary: dict) -> str:
    return json.dumps(summary, indent=2) + "\n"

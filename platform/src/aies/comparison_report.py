"""Adaptive reports and optional persistence for 2–5 subject comparisons.

Comparison is presentation over existing evidence. Rendering never changes a
score or decides which subject should be selected. Persistence is explicit:
the CLI records a comparison only when ``--save`` is supplied.
"""

from __future__ import annotations

import copy
import datetime
import hashlib
import html
import json
from pathlib import Path

from . import workspace


def _canonical_payload(comparison: dict) -> dict:
    return {
        key: value for key, value in comparison.items()
        if key not in {
            "comparison_id", "recorded_at", "report_bundle",
        }
    }


def comparison_id(comparison: dict) -> str:
    encoded = json.dumps(
        _canonical_payload(comparison),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()[:16]
    family = (
        "repo" if comparison.get("subject_family") == "repository"
        else "deployment")
    return f"comparison-{family}-{digest}"


def with_identity(comparison: dict) -> dict:
    result = copy.deepcopy(comparison)
    result.setdefault("comparison_id", comparison_id(result))
    return result


def record(comparison: dict) -> dict:
    """Persist one append-only comparison record; identical input is idempotent."""
    result = with_identity(comparison)
    path = workspace.root() / "comparisons" / (
        result["comparison_id"] + ".json")
    if path.exists():
        return workspace.read_json(path)
    result["recorded_at"] = datetime.datetime.now(
        datetime.timezone.utc).isoformat()
    workspace.write_json(path, result)
    return result


def list_records() -> list[dict]:
    directory = workspace.root() / "comparisons"
    if not directory.exists():
        return []
    rows = []
    for path in sorted(directory.glob("comparison-*.json"), reverse=True):
        value = workspace.read_json(path)
        summary = value.get("summary") or {}
        rows.append({
            "comparison_id": value.get("comparison_id", path.stem),
            "subject_family": value.get("subject_family"),
            "layout": value.get("layout"),
            "subjects": summary.get(
                "subjects", len(value.get("subjects") or [])),
            "compatible": value.get("compatible"),
            "recorded_at": value.get("recorded_at"),
            "href": "/comparisons/" + value.get(
                "comparison_id", path.stem),
        })
    return sorted(
        rows,
        key=lambda item: item.get("recorded_at") or "",
        reverse=True,
    )


def render_markdown(comparison: dict) -> str:
    from . import compare

    if comparison.get("kind") == "aies-repository-comparison":
        return compare.render_repository_comparison(comparison)
    if comparison.get("kind") == "ecm-multi-comparison":
        return compare.render_ecm_many_markdown(comparison)
    if comparison.get("kind") == "comparison":
        return compare.render_markdown(comparison)
    raise ValueError(
        f"unsupported comparison kind {comparison.get('kind')!r}")


def _subject_cells(comparison: dict) -> tuple[list[str], list[list[str]]]:
    subjects = comparison["subjects"]
    columns = [subject["column"] for subject in subjects]
    if comparison["subject_family"] == "repository":
        rows = [
            ["Repository"] + [
                subject["subject"]["display_name"] for subject in subjects
            ],
            ["Assessment"] + [
                subject["audit_id"] for subject in subjects
            ],
            ["Snapshot"] + [
                subject["snapshot"]["scope_digest"][:23] + "…"
                for subject in subjects
            ],
        ]
    else:
        rows = [
            ["Subject"] + [subject["subject"] for subject in subjects],
            ["Run"] + [subject["run_id"] for subject in subjects],
            ["Risk tier"] + [
                subject["risk_tier"] for subject in subjects
            ],
            ["Profile"] + [subject["profile"] for subject in subjects],
        ]
    return columns, rows


def _comparison_rows(comparison: dict) -> list[list[str]]:
    if comparison["subject_family"] == "repository":
        rows = []
        for item in comparison["metrics"]:
            rows.append([
                item["perspective"].replace("_", " ").title()
                + " / " + item["metric"].replace("_", " ").capitalize(),
                *[
                    ("—" if value is None else str(value))
                    + f" / {confidence:.0f}% confidence"
                    for value, confidence in zip(
                        item["values"],
                        item["evidence_confidence_percent"])
                ],
                "comparable" if item["comparable"] else "not comparable",
                item["interpretation"],
            ])
        return rows
    if comparison["kind"] == "comparison":
        rows = []
        for area, value in comparison["areas"].items():
            for dimension, scores in value["dimensions"].items():
                delta = scores["delta"]
                rows.append([
                    area + " / " + dimension,
                    str(scores["a"]),
                    str(scores["b"]),
                    f"{delta:+g}",
                ])
            aggregate = value["aggregate"]
            delta = aggregate["delta"]
            rows.append([
                area + " / Aggregate",
                str(aggregate["a"]),
                str(aggregate["b"]),
                "—" if delta is None else f"{delta:+g}",
            ])
        return rows
    rows = []
    for item in comparison["tasks"]:
        values = []
        for score, confidence, distinct, minimum in zip(
                item["score_percent"],
                item["evidence_confidence_percent"],
                item["distinct_scenarios"],
                item["minimum_observations"]):
            values.append(
                "not assessed" if score is None else
                f"{score:.0f}% performance / {confidence:.0f}% confidence "
                f"({distinct}/{minimum if minimum is not None else '—'})")
        if not item["comparable"]:
            result = "not comparable"
        elif len(item["leaders"]) > 1:
            result = "tie: " + ", ".join(item["leaders"])
        else:
            result = "higher observed: " + item["leaders"][0]
        rows.append([
            item["task_id"] + " — " + item["task"],
            *values,
            result,
        ])
    return rows


def render_html(comparison: dict) -> str:
    columns, subject_rows = _subject_cells(comparison)
    data_rows = _comparison_rows(comparison)
    repository = comparison["subject_family"] == "repository"
    title = (
        "Repository Evidence Comparison" if repository
        else "Qualification Area Comparison"
        if comparison["kind"] == "comparison"
        else "Engineering Capability Matrix Comparison")
    first_header = (
        "Perspective / metric" if repository
        else "Area / dimension" if comparison["kind"] == "comparison"
        else "Engineering task")
    last_headers = (
        ["Status", "Interpretation"] if repository else
        ["Delta (B-A)"] if comparison["kind"] == "comparison" else
        ["Result"])

    def table_row(values: list[str], *, header: bool = False) -> str:
        tag = "th" if header else "td"
        return "<tr>" + "".join(
            f"<{tag}>{html.escape(str(value))}</{tag}>"
            for value in values) + "</tr>"

    checks = "".join(
        "<tr><td>" + html.escape(name.replace("_", " ").title())
        + "</td><td class=" + (
            '"pass">compatible' if passed else '"fail">mismatch')
        + "</td></tr>"
        for name, passed in comparison["checks"].items()
    )
    caveats = "".join(
        "<li>" + html.escape(value) + "</li>"
        for value in comparison.get("caveats") or []
    ) or "<li>No additional comparison caveat was emitted.</li>"
    actions = "".join(
        "<li>" + html.escape(value) + "</li>"
        for value in comparison.get("next_actions") or []
    )
    subject_table = table_row([""] + columns, header=True) + "".join(
        table_row(row) for row in subject_rows)
    data_header = [first_header] + [
        column + (" value / confidence" if repository else "")
        for column in columns
    ] + last_headers
    data_table = table_row(data_header, header=True) + "".join(
        table_row(row) for row in data_rows)
    summary = comparison["summary"]
    comparable = summary.get(
        "comparable_metrics", summary.get(
            "comparable_tasks", summary.get("areas", 0)))
    total = summary.get(
        "metrics", summary.get(
            "tasks", summary.get("areas", 0)
            + summary.get("incomparable_areas", 0)))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AIES {html.escape(title)}</title>
<style>
:root{{--ink:#172033;--muted:#667085;--line:#d8dee9;--panel:#f7f9fc;
--accent:#3157d5;--good:#087a55;--bad:#b42318}}
*{{box-sizing:border-box}}body{{font:15px/1.5 system-ui,sans-serif;color:var(--ink);
max-width:1440px;margin:auto;padding:28px}}h1{{margin-bottom:4px}}
.sub{{color:var(--muted)}}.notice{{border-left:4px solid var(--accent);
background:var(--panel);padding:12px 16px}}.cards{{display:grid;
grid-template-columns:repeat(3,minmax(150px,1fr));gap:12px;margin:20px 0}}
.card{{border:1px solid var(--line);border-radius:10px;padding:14px}}
.value{{font-size:1.55rem;font-weight:700}}.scroll{{overflow:auto;
border:1px solid var(--line);border-radius:10px;margin:12px 0 24px}}
table{{border-collapse:collapse;width:100%;min-width:720px}}th,td{{
padding:9px 11px;border-bottom:1px solid var(--line);text-align:left;
vertical-align:top}}th{{background:var(--panel);cursor:pointer;position:sticky;
top:0}}th:first-child,td:first-child{{position:sticky;left:0;background:white}}
th:first-child{{background:var(--panel);z-index:2}}.pass{{color:var(--good);
font-weight:700}}.fail{{color:var(--bad);font-weight:700}}
code{{word-break:break-all}}@media(max-width:700px){{body{{padding:14px}}
.cards{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>{html.escape(title)}</h1>
<p class="sub">{html.escape(comparison["layout"].title())} layout ·
{len(columns)} subjects · generated from existing evidence</p>
<p class="notice"><strong>Informational only.</strong>
{html.escape(comparison["claim_boundary"])}</p>
<div class="cards"><div class="card"><div class="value">{len(columns)}</div>
subjects</div><div class="card"><div class="value">{comparable}/{total}</div>
comparable rows</div><div class="card"><div class="value">{
'Yes' if comparison["compatible"] else 'No'}</div>protocol compatible</div></div>
<h2>Subjects and evidence</h2><div class="scroll"><table class="sortable">
{subject_table}</table></div>
<h2>Comparison matrix</h2><div class="scroll"><table class="sortable">
{data_table}</table></div>
<h2>Compatibility checks</h2><div class="scroll"><table class="sortable">
<tr><th>Check</th><th>Result</th></tr>{checks}</table></div>
<h2>Caveats</h2><ul>{caveats}</ul>
<h2>Evidence-driven next actions</h2><ol>{actions}</ol>
<script>
document.querySelectorAll("table.sortable th").forEach((header,index)=>{{
 header.title="Sort by this column";
 header.addEventListener("click",()=>{{
  const body=header.closest("table").tBodies[0],rows=[...body.rows].slice(1);
  const asc=header.dataset.order!=="asc";
  rows.sort((x,y)=>{{const a=x.cells[index]?.textContent.trim()||"";
   const b=y.cells[index]?.textContent.trim()||"";
   return (asc?1:-1)*a.localeCompare(b,undefined,{{numeric:true}});}});
  [...header.parentElement.children].forEach(x=>delete x.dataset.order);
  header.dataset.order=asc?"asc":"desc";rows.forEach(row=>body.appendChild(row));
 }});
}});
</script></body></html>"""


def write_bundle(comparison: dict, directory: str | Path) -> dict:
    result = with_identity(comparison)
    target = Path(directory).resolve()
    if target.exists() and not target.is_dir():
        raise NotADirectoryError(
            f"comparison output must be a directory: {target}")
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": target / "comparison.json",
        "markdown": target / "comparison.md",
        "html": target / "comparison.html",
        "bundle": target / "comparison-bundle.json",
    }
    existing = [str(path) for path in paths.values() if path.exists()]
    if existing:
        raise FileExistsError(
            "comparison output is immutable; already exists: "
            + ", ".join(existing))
    paths["json"].write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    paths["markdown"].write_text(render_markdown(result), encoding="utf-8")
    paths["html"].write_text(render_html(result), encoding="utf-8")
    bundle = {
        "kind": "aies-comparison-report-bundle",
        "schema": 1,
        "comparison_id": result["comparison_id"],
        "subject_family": result["subject_family"],
        "layout": result["layout"],
        "subject_count": len(result["subjects"]),
        "artifacts": {
            key: path.name for key, path in paths.items() if key != "bundle"
        },
        "claim_boundary": result["claim_boundary"],
    }
    paths["bundle"].write_text(
        json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return {key: str(path) for key, path in paths.items()}

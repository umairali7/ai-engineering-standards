"""Result history and comparison (M2, PLATFORM.md §9).

Comparisons are only meaningful on identical suite versions: an area
whose suite version differs between the two runs is reported as
incomparable, never silently diffed. Deltas are presentation over the
same evidence — a comparison makes no additional claims.
"""

from __future__ import annotations

import hashlib
import json

from . import constants as C
from . import workspace


class CompareError(Exception):
    pass


MIN_COMPARISON_SUBJECTS = 2
MAX_COMPARISON_SUBJECTS = 5


def validate_reference_count(
    refs: list[str],
    *,
    label: str = "comparison",
) -> None:
    count = len(refs)
    if count < MIN_COMPARISON_SUBJECTS:
        raise CompareError(
            f"{label} requires at least {MIN_COMPARISON_SUBJECTS} references")
    if count > MAX_COMPARISON_SUBJECTS:
        raise CompareError(
            f"{label} accepts at most {MAX_COMPARISON_SUBJECTS} references; "
            f"received {count}. Split larger studies into compatible cohorts "
            "and retain the cohort definition.")


def _audit_path(ref: str):
    return workspace.root() / "audits" / f"{ref}.json"


def is_audit_ref(ref: str) -> bool:
    return _audit_path(ref).exists()


def _resolve_audit(ref: str) -> dict:
    path = _audit_path(ref)
    if not path.exists():
        raise CompareError(
            f"{ref!r} is not a stored repository assessment "
            "(GET /audits or inspect the workspace audits directory)")
    value = workspace.read_json(path)
    if not value.get("engineering_analysis"):
        raise CompareError(
            f"{ref!r} contains conformance maturity only; rerun `aies audit` "
            "without --conformance-only before repository comparison")
    return value


def compare_repositories(
    refs: list[str],
    *,
    only_comparable: bool = False,
    sort_by: str = "task",
) -> dict:
    """Compare stored repository evidence without emitting a quality winner."""
    validate_reference_count(refs, label="repository comparison")
    if sort_by == "leader":
        raise CompareError(
            "--sort leader is unavailable for repository evidence because "
            "repository comparison emits no winner")
    assessments = [_resolve_audit(ref) for ref in refs]
    analyses = [item["engineering_analysis"] for item in assessments]
    repository_extensions = [
        (analysis["subject"].get("extensions") or {}).get("repository") or {}
        for analysis in analyses
    ]
    profiles = [
        sorted({event["adapter_profile"] for event in item.get("events") or []})
        for item in assessments
    ]
    checks = {
        "assessment_schema": _all_equal([
            item.get("schema") for item in assessments]),
        "analysis_schema": _all_equal([
            analysis.get("schema") for analysis in analyses]),
        "analyzer_version": _all_equal([
            (analysis.get("analyzer") or {}).get("version")
            for analysis in analyses]),
        "languages": _all_equal([
            [(row["language"], row["files"])
             for row in extension.get("languages") or []]
            for extension in repository_extensions]),
        "build_systems": _all_equal([
            extension.get("build_systems") or []
            for extension in repository_extensions]),
        "complete_snapshot": all(
            analysis["snapshot"].get("complete") for analysis in analyses),
        "evidence_adapter_profiles": _all_equal(profiles),
    }
    compatible = all(checks.values())
    perspective_names = sorted(set.intersection(*[
        set(analysis["perspectives"]) for analysis in analyses]))
    rows = []
    for perspective in perspective_names:
        metrics = [
            analysis["perspectives"][perspective]["metrics"]
            for analysis in analyses
        ]
        confidence_values = [
            analysis["perspectives"][perspective]["confidence"].get(
                "coverage_percent", 0)
            for analysis in analyses
        ]
        shared = sorted(set.intersection(*[set(item) for item in metrics]))
        for metric in shared:
            values = [item.get(metric) for item in metrics]
            if not all(
                    value is None or isinstance(value, (int, float))
                    for value in values):
                continue
            numeric = [value for value in values if value is not None]
            comparable = compatible and len(numeric) == len(values)
            row = {
                "perspective": perspective,
                "metric": metric,
                "values": values,
                "evidence_confidence_percent": confidence_values,
                "minimum_evidence_confidence_percent": min(
                    confidence_values),
                "deltas_from_a": [
                    None if value is None or values[0] is None
                    else round(value - values[0], 3)
                    for value in values
                ],
                "comparable": comparable,
                "spread": (
                    round(max(numeric) - min(numeric), 3)
                    if comparable and numeric else None),
                "interpretation": _repository_metric_interpretation(
                    perspective, metric),
            }
            rows.append(row)
    all_metric_rows = list(rows)
    total_metric_rows = len(all_metric_rows)
    comparable_metric_rows = sum(
        row["comparable"] for row in all_metric_rows)
    filtered_metric_rows = (
        sum(not row["comparable"] for row in all_metric_rows)
        if only_comparable else 0)
    if only_comparable:
        rows = [row for row in rows if row["comparable"]]
    if sort_by == "spread":
        rows.sort(key=lambda row: (
            row["spread"] is not None, row["spread"] or 0,
            row["perspective"], row["metric"]), reverse=True)
    elif sort_by == "confidence":
        rows.sort(key=lambda row: (
            row["minimum_evidence_confidence_percent"],
            row["comparable"], row["perspective"], row["metric"]),
            reverse=True)
    else:
        rows.sort(key=lambda row: (row["perspective"], row["metric"]))
    same_subject = _all_equal([
        analysis["subject"]["id"] for analysis in analyses])
    subjects = []
    for index, (ref, assessment, analysis, profile) in enumerate(
            zip(refs, assessments, analyses, profiles)):
        subjects.append({
            "column": chr(65 + index),
            "audit_id": ref,
            "subject": analysis["subject"],
            "snapshot": analysis["snapshot"],
            "analyzer": analysis["analyzer"],
            "adapter_profiles": profile,
            "generated_at": assessment.get("generated_at"),
        })
    return {
        "kind": "aies-repository-comparison",
        "schema": "aies-repository-comparison/v2",
        "subject_family": "repository",
        "layout": "pair" if len(subjects) == 2 else "matrix",
        "reference_policy": {
            "minimum": MIN_COMPARISON_SUBJECTS,
            "maximum": MAX_COMPARISON_SUBJECTS,
            "received": len(subjects),
        },
        "compatible": compatible,
        "same_subject_over_time": same_subject,
        "checks": checks,
        "subjects": subjects,
        "metrics": rows,
        "summary": {
            "subjects": len(subjects),
            "metrics": total_metric_rows,
            "rows_returned": len(rows),
            "filtered_noncomparable_metrics": filtered_metric_rows,
            "comparable_metrics": comparable_metric_rows,
            "not_comparable_metrics": (
                total_metric_rows - comparable_metric_rows),
            "perspectives": sorted({
                row["perspective"] for row in all_metric_rows
            }),
        },
        "caveats": [
            value for value in (
                None if compatible else
                "One or more scope/protocol checks failed; deltas remain visible "
                "but are marked non-comparable.",
                None if same_subject else
                "Assessments identify different repository subjects; this is a "
                "descriptive evidence comparison, not a trend.",
                "A repeated reference is a protocol self-check, not independent "
                "comparative evidence." if len(set(refs)) != len(refs) else None,
            ) if value
        ],
        "next_actions": _comparison_next_actions(
            compatible=compatible,
            failed_checks=[
                name for name, passed in checks.items() if not passed
            ],
            comparable=comparable_metric_rows,
            total=total_metric_rows,
            evidence_kind="repository metrics",
        ),
        "claim_boundary": (
            "Metric deltas retain their perspective-specific meaning. No "
            "composite score, winner, repository quality verdict, correctness "
            "claim, security claim, or authorization is emitted."),
    }


def _comparison_next_actions(
    *,
    compatible: bool,
    failed_checks: list[str],
    comparable: int,
    total: int,
    evidence_kind: str,
) -> list[str]:
    actions = []
    if not compatible:
        actions.append(
            "Align " + ", ".join(
                check.replace("_", " ") for check in failed_checks)
            + " before interpreting deltas as like-for-like.")
    if comparable < total:
        actions.append(
            f"Collect matching evidence for the {total - comparable} "
            f"non-comparable {evidence_kind} row(s).")
    if compatible and comparable:
        actions.append(
            "Review the largest evidence-backed spreads together with each "
            "row's confidence and interpretation before making a selection.")
    if not actions:
        actions.append(
            "No comparable evidence rows are available; inspect subject scope "
            "and collect a matching assessment protocol.")
    return actions


def _repository_metric_interpretation(
        perspective: str, metric: str) -> str:
    lower_signals = {
        "dependency_cycles", "layer_violations", "python_parse_failures",
        "complex_or_long_functions", "large_source_files",
        "duplicate_block_groups", "todo_fixme_markers",
        "retained_quality_errors", "retained_quality_warnings",
        "test_failures_or_errors", "sarif_error_findings",
        "sensitive_configuration_filenames",
        "unpinned_direct_declarations", "sbom_vulnerabilities",
        "sbom_high_critical_vulnerabilities",
    }
    higher_assurance = {
        "retained_test_pass_percent", "retained_line_coverage_percent",
        "python_documented_function_percent",
    }
    if metric in lower_signals:
        return (
            "Lower is a smaller bounded review signal; zero does not prove "
            "quality or absence.")
    if metric in higher_assurance:
        return (
            "Higher is more retained evidence on this metric; it is not a "
            "quality or correctness score.")
    return (
        f"Context/evidence-volume metric for {perspective.replace('_', ' ')}; "
        "direction is not a quality ranking.")


def render_repository_comparison(cmp: dict) -> str:
    subjects = cmp["subjects"]
    lines = [
        "# AIES Repository Evidence Comparison",
        "",
        "> **INFORMATIONAL — NO COMPOSITE SCORE OR WINNER.**",
        "",
        f"{len(subjects)} repository assessment(s) · "
        f"{cmp['summary']['comparable_metrics']}/"
        f"{cmp['summary']['metrics']} metric rows comparable · "
        f"{cmp.get('layout', 'matrix')} layout",
        (
            f"Rows shown: {cmp['summary']['rows_returned']}/"
            f"{cmp['summary']['metrics']} "
            f"({cmp['summary']['filtered_noncomparable_metrics']} "
            "non-comparable filtered)"
            if cmp["summary"]["filtered_noncomparable_metrics"] else
            f"Rows shown: {cmp['summary']['rows_returned']}"),
        "",
        "| | " + " | ".join(item["column"] for item in subjects) + " |",
        "|---|" + "|".join("---" for _ in subjects) + "|",
        "| Audit | " + " | ".join(
            f"`{item['audit_id']}`" for item in subjects) + " |",
        "| Subject | " + " | ".join(
            f"`{item['subject']['id']}`" for item in subjects) + " |",
        "| Snapshot | " + " | ".join(
            f"`{item['snapshot']['scope_digest'][:23]}…`"
            for item in subjects) + " |",
        "",
        "## Protocol compatibility",
        "",
        "| Check | Result |",
        "|---|---|",
        *[
            f"| {name.replace('_', ' ').title()} | "
            f"{'compatible' if passed else '**mismatch**'} |"
            for name, passed in cmp["checks"].items()
        ],
        "",
        "## Evidence matrix",
        "",
        "| Perspective / metric | " + " | ".join(
            item["column"] + " value / evidence confidence"
            for item in subjects)
        + " | Comparable | Interpretation |",
        "|---|" + "|".join("---:" for _ in subjects) + "|---|---|",
    ]
    for row in cmp["metrics"]:
        values = [
            ("—" if value is None else str(value))
            + f" / {confidence:.0f}%"
            for value, confidence in zip(
                row["values"], row["evidence_confidence_percent"])
        ]
        lines.append(
            f"| {row['perspective'].replace('_', ' ').title()} / "
            f"{row['metric'].replace('_', ' ').capitalize()} | "
            + " | ".join(values)
            + f" | {'yes' if row['comparable'] else 'no'} | "
            + row["interpretation"] + " |")
    for caveat in cmp["caveats"]:
        lines += ["", f"> **Caveat:** {caveat}"]
    lines += ["", "## Evidence-driven next actions", ""]
    lines += [
        f"{index}. {action}"
        for index, action in enumerate(cmp.get("next_actions") or [], 1)
    ]
    lines += ["", cmp["claim_boundary"], ""]
    return "\n".join(lines)


def list_runs(model: str | None = None) -> list[dict]:
    """Result history: every run's manifest summary, newest first."""
    out = []
    rdir = workspace.runs_dir()
    for d in sorted(rdir.iterdir(), reverse=True):
        manifest_path = workspace.run_dir(d.name) / "manifest.json"
        if not d.is_dir() or not manifest_path.exists():
            continue
        m = workspace.read_json(manifest_path)
        model_id = (
            (m.get("model") or {}).get("registry_id")
            or (m.get("subject") or {}).get("id")
            or "unknown-subject")
        if model and model_id != model:
            continue
        out.append({
            "run_id": m["run_id"],
            "model": model_id,
            "profile": m["profile"],
            "risk_tier": m["risk_tier"],
            "areas": [a["area"] for a in m["areas"]],
            "status": m.get("status", "unknown"),
            "created_at": m.get("created_at"),
            "aggregated": (
                manifest_path.parent / "evidence-package.json").exists(),
        })
    return out


def _comparison_batches(run_ids: list[str]) -> list[list[str]]:
    """Create connected 2–5 run batches without duplicating model calls."""
    if len(run_ids) < MIN_COMPARISON_SUBJECTS:
        return []
    batches = [run_ids[:MAX_COMPARISON_SUBJECTS]]
    anchor = run_ids[0]
    offset = MAX_COMPARISON_SUBJECTS
    while offset < len(run_ids):
        batch = [anchor, *run_ids[offset:offset + MAX_COMPARISON_SUBJECTS - 1]]
        batches.append(batch)
        offset += MAX_COMPARISON_SUBJECTS - 1
    return batches


def discover_run_cohorts(
    *,
    model: str | None = None,
    profile: str | None = None,
    risk_tier: str | None = None,
    minimum_runs: int = MIN_COMPARISON_SUBJECTS,
) -> dict:
    """Group aggregated deployment runs by the exact ECM protocol signature.

    Discovery is read-only and does not claim that compatible runs are
    representative, independent, or suitable for a particular decision.
    """
    if minimum_runs < 1:
        raise CompareError("minimum cohort size must be at least 1")
    if risk_tier is not None and not str(risk_tier).startswith("RT"):
        risk_tier = f"RT{risk_tier}"
    candidates = [
        row for row in list_runs(model=model)
        if row["aggregated"]
        and (profile is None or row["profile"] == profile)
        and (risk_tier is None or row["risk_tier"] == risk_tier)
    ]
    from . import ecm

    groups: dict[str, dict] = {}
    excluded = []
    for row in candidates:
        run_id = row["run_id"]
        try:
            matrix = ecm.engineering_capability_matrix(run_id)
            package = _resolve_package(run_id)
            manifest = workspace.read_json(
                workspace.run_dir(run_id) / "manifest.json")
            signature = {
                "subject_kind": package.get("subject_kind", "ai"),
                "risk_tier": matrix["risk_tier"],
                "profile": matrix["profile"],
                "mapping_version": matrix["mapping"]["version"],
                "mapping_schema": matrix["mapping"]["schema"],
                "task_decision_semantics": (
                    matrix["task_decision_semantics_version"]),
                "rater_protocol": matrix["rater_kinds"],
                "suite_versions": package["suite_versions"],
                "repeat_structure": manifest.get("repeats"),
                "evidence_adapter_profiles": _adapter_profiles(run_id),
            }
        except (FileNotFoundError, KeyError, TypeError, ValueError) as error:
            excluded.append({
                "run_id": run_id,
                "reason": f"comparison signature unavailable: {error}",
            })
            continue
        material = json.dumps(
            signature, sort_keys=True, separators=(",", ":")).encode("utf-8")
        cohort_id = "cohort-" + hashlib.sha256(material).hexdigest()[:16]
        group = groups.setdefault(cohort_id, {
            "cohort_id": cohort_id,
            "signature": signature,
            "runs": [],
        })
        group["runs"].append({
            "run_id": run_id,
            "model": row["model"],
            "created_at": row["created_at"],
            "status": row["status"],
        })
    cohorts = []
    for cohort_id, group in sorted(groups.items()):
        group["runs"].sort(
            key=lambda item: item.get("created_at") or "", reverse=True)
        if len(group["runs"]) < minimum_runs:
            continue
        run_ids = [item["run_id"] for item in group["runs"]]
        batches = _comparison_batches(run_ids)
        cohorts.append({
            **group,
            "run_count": len(run_ids),
            "comparison_ready": len(run_ids) >= MIN_COMPARISON_SUBJECTS,
            "comparison_batches": [
                {
                    "batch": index,
                    "run_ids": batch,
                    "command": "aies compare " + " ".join(batch),
                }
                for index, batch in enumerate(batches, 1)
            ],
        })
    cohorts.sort(
        key=lambda item: (
            item["run_count"],
            item["runs"][0].get("created_at") or ""),
        reverse=True)
    return {
        "kind": "aies-run-comparison-cohorts",
        "schema": "aies-run-comparison-cohorts/v1",
        "filters": {
            "model": model,
            "profile": profile,
            "risk_tier": risk_tier,
            "minimum_runs": minimum_runs,
        },
        "candidate_runs": len(candidates),
        "cohorts": cohorts,
        "excluded": excluded,
        "claim_boundary": (
            "Cohorts share the comparison protocol signature only. Discovery "
            "does not establish independence, representativeness, engineering "
            "superiority, qualification, or deployment authority."),
    }


def _resolve_package(ref: str) -> dict:
    """ref is a run id or a model registry id (latest aggregated run)."""
    direct = workspace.run_dir(ref) / "evidence-package.json"
    if direct.exists():
        return workspace.read_json(direct)
    candidates = [r for r in list_runs(model=ref) if r["aggregated"]]
    if not candidates:
        raise CompareError(
            f"{ref!r} is neither an aggregated run id nor a model with an "
            "aggregated run (aies runs list)"
        )
    return workspace.read_json(
        workspace.run_dir(candidates[0]["run_id"]) / "evidence-package.json"
    )


def compare(ref_a: str, ref_b: str) -> dict:
    a, b = _resolve_package(ref_a), _resolve_package(ref_b)

    if a["risk_tier"] != b["risk_tier"]:
        raise CompareError(
            f"runs are scoped to different risk tiers ({C.risk_tier_label(a['risk_tier'])} vs "
            f"{C.risk_tier_label(b['risk_tier'])}); deltas across tiers are not comparable"
        )

    common = sorted(set(a["areas"]) & set(b["areas"]))
    if not common:
        raise CompareError("the runs share no competency areas")

    comparable, incomparable = [], []
    for area in common:
        va = a["suite_versions"].get(area)
        vb = b["suite_versions"].get(area)
        if va != vb:
            incomparable.append({"area": area, "suite_a": va, "suite_b": vb,
                                 "reason": "different suite versions"})
        else:
            comparable.append(area)

    areas = {}
    for area in comparable:
        da, db = a["areas"][area], b["areas"][area]
        dims = {}
        for dim in C.DIMENSIONS:
            sa = da["dimensions"].get(dim)
            sb = db["dimensions"].get(dim)
            if sa and sb:
                dims[dim] = {
                    "a": sa["ci90_low"], "b": sb["ci90_low"],
                    "delta": round(sb["ci90_low"] - sa["ci90_low"], 3),
                }
        areas[area] = {
            "suite_version": a["suite_versions"][area],
            "dimensions": dims,
            "aggregate": {"a": da["aggregate_A"], "b": db["aggregate_A"],
                          "delta": (round(db["aggregate_A"] - da["aggregate_A"], 3)
                                    if None not in (da["aggregate_A"], db["aggregate_A"])
                                    else None)},
            "gates_passed": {"a": da["gates_passed"], "b": db["gates_passed"]},
            "cl": {"a": da["cl"], "b": db["cl"]},
            "decisional": {"a": da["decisional"], "b": db["decisional"]},
        }

    same_env = (a["environment_fingerprint"].get("fingerprint_hash")
                == b["environment_fingerprint"].get("fingerprint_hash"))
    return {
        "kind": "comparison",
        "schema": "aies-area-comparison/v2",
        "subject_family": "ai-deployment",
        "layout": "pair",
        "reference_policy": {
            "minimum": 2, "maximum": 2, "received": 2,
        },
        "compatible": bool(areas) and not incomparable,
        "a": {"run_id": a["run_id"], "model": a["model"]["registry_id"],
              "profile": a["profile"]},
        "b": {"run_id": b["run_id"], "model": b["model"]["registry_id"],
              "profile": b["profile"]},
        "subjects": [
            {"column": "A", "subject": a["model"]["registry_id"],
             "run_id": a["run_id"], "profile": a["profile"],
             "risk_tier": a["risk_tier"]},
            {"column": "B", "subject": b["model"]["registry_id"],
             "run_id": b["run_id"], "profile": b["profile"],
             "risk_tier": b["risk_tier"]},
        ],
        "checks": {
            "risk_tier": True,
            "common_areas": bool(common),
            "suite_versions": not incomparable,
        },
        "summary": {
            "subjects": 2,
            "areas": len(areas),
            "incomparable_areas": len(incomparable),
        },
        "risk_tier": a["risk_tier"],
        "same_environment_fingerprint": same_env,
        "profiles_differ": a["profile"] != b["profile"],
        "areas": areas,
        "incomparable_areas": incomparable,
        "caveats": [
            c for c in (
                None if same_env else
                "environment fingerprints differ: deltas mix model and "
                "environment effects (PLATFORM.md D7)",
                None if a["profile"] == b["profile"] else
                "profiles differ: aggregates use different weights; "
                "per-dimension decision values remain comparable",
                None if all(areas[x]["decisional"]["a"] and areas[x]["decisional"]["b"]
                            for x in areas) else
                "one or both runs are NON-DECISIONAL (AIES-AESQS-CS-01 §6)",
            ) if c
        ],
        "next_actions": _comparison_next_actions(
            compatible=bool(areas) and not incomparable,
            failed_checks=(
                ["suite_versions"] if incomparable else []),
            comparable=len(areas),
            total=len(areas) + len(incomparable),
            evidence_kind="competency areas",
        ),
        "claim_boundary": (
            "Area deltas are presentation over existing qualification evidence. "
            "They are not a model selection, deployment, qualification, or "
            "authorization grant."),
    }


def render_markdown(cmp: dict) -> str:
    lines: list[str] = []
    a = lines.append
    a("# AIES Qualification Comparison")
    a("")
    a(f"| | A | B |")
    a(f"|---|---|---|")
    a(f"| Model | `{cmp['a']['model']}` | `{cmp['b']['model']}` |")
    a(f"| Run | `{cmp['a']['run_id']}` | `{cmp['b']['run_id']}` |")
    a(f"| Profile | {cmp['a']['profile']} | {cmp['b']['profile']} |")
    a("")
    a(f"Scoped risk tier: **{C.risk_tier_label(cmp['risk_tier'])}**")
    a("")
    for caveat in cmp["caveats"]:
        a(f"> **Caveat:** {caveat}")
        a("")
    for area, d in cmp["areas"].items():
        a(f"## {C.competency_label(area)} (suite `{d['suite_version']}`)")
        a("")
        a("| Dimension | A (decision) | B (decision) | Delta (B-A) |")
        a("|---|---|---|---|")
        for dim, v in d["dimensions"].items():
            marker = "+" if v["delta"] > 0 else ""
            a(f"| {C.identifier_label(dim)} | {v['a']} | {v['b']} | "
              f"{marker}{v['delta']} |")
        agg = d["aggregate"]
        a(f"| **Aggregate A** | **{agg['a']}** | **{agg['b']}** | "
          f"**{'+' if (agg['delta'] or 0) > 0 else ''}{agg['delta']}** |")
        a("")
        a(f"Gates: A {'pass' if d['gates_passed']['a'] else 'FAIL'} / "
          f"B {'pass' if d['gates_passed']['b'] else 'FAIL'} | "
          f"CL: A {C.identifier_label(d['cl']['a']) if d['cl']['a'] else 'none'} / "
          f"B {C.identifier_label(d['cl']['b']) if d['cl']['b'] else 'none'} | "
          f"Decisional: A {'yes' if d['decisional']['a'] else 'NO'} / "
          f"B {'yes' if d['decisional']['b'] else 'NO'}")
        a("")
    if cmp["incomparable_areas"]:
        a("## Incomparable areas")
        a("")
        for x in cmp["incomparable_areas"]:
            a(f"- **{C.competency_label(x['area'])}**: {x['reason']} (`{x['suite_a']}` vs `{x['suite_b']}`) "
              "- results on different suite versions are never diffed")
        a("")
    a("## Evidence-driven next actions")
    a("")
    for index, action in enumerate(cmp.get("next_actions") or [], 1):
        a(f"{index}. {action}")
    a("")
    a("---")
    a(cmp.get(
        "claim_boundary",
        "A comparison is presentation over existing evidence; it makes no "
        "additional claims (PLATFORM.md §9)."))
    a("")
    return "\n".join(lines)


def compare_ecm(ref_a: str, ref_b: str, *,
                formal_qualification: bool = False) -> dict:
    """Backward-compatible two-run projection of the N-run comparison."""
    many = compare_ecm_many(
        [ref_a, ref_b], formal_qualification=formal_qualification)
    a, b = many["subjects"]
    rows = []
    for row in many["tasks"]:
        scores = row["scores"]
        leaders = row["leaders"]
        higher = leaders[0] if len(leaders) == 1 else None
        rows.append({
            **row,
            "task": row["task"],
            "a": scores[0],
            "b": scores[1],
            "higher_observed": higher,
            "winner": higher if formal_qualification else None,
        })
    return {"kind": "ecm-comparison",
            "comparison_mode": many["comparison_mode"],
            "compatible": many["compatible"], "checks": many["checks"],
            "a": a, "b": b, "tasks": rows}


def _all_equal(values: list[object]) -> bool:
    return all(value == values[0] for value in values[1:])


def _adapter_profiles(run_id: str) -> list[str]:
    from . import evidence_events
    events = evidence_events.collect(run_id)
    return sorted({event["adapter_profile"] for event in events}) or [
        "legacy-untyped"]


def compare_ecm_many(
    refs: list[str],
    *,
    formal_qualification: bool = False,
    sort_by: str = "task",
    only_comparable: bool = False,
) -> dict:
    """Compare two or more ECMs without inflating incompatible evidence.

    Task identity, instrument set, mapping/scoring semantics, adapter profiles,
    and run protocol must match before a leader is emitted.
    """
    from . import ecm

    validate_reference_count(
        refs, label="deployment or model comparison")
    if sort_by not in {"task", "confidence", "spread", "leader"}:
        raise CompareError(
            "comparison sort must be task, confidence, spread, or leader")
    matrices = [ecm.engineering_capability_matrix(ref) for ref in refs]
    packages = [_resolve_package(ref) for ref in refs]
    manifests = [
        workspace.read_json(
            workspace.run_dir(matrix["run_id"]) / "manifest.json")
        for matrix in matrices
    ]
    profiles = [_adapter_profiles(matrix["run_id"]) for matrix in matrices]
    checks = {
        "risk_tier": _all_equal([matrix["risk_tier"] for matrix in matrices]),
        "subject_kind": _all_equal([
            package.get("subject_kind", "ai") for package in packages]),
        "profile": _all_equal([matrix["profile"] for matrix in matrices]),
        "mapping_version": _all_equal([
            matrix["mapping"]["version"] for matrix in matrices]),
        "mapping_schema": _all_equal([
            matrix["mapping"]["schema"] for matrix in matrices]),
        "task_decision_semantics": _all_equal([
            matrix["task_decision_semantics_version"] for matrix in matrices]),
        "rater_protocol": _all_equal([
            matrix["rater_kinds"] for matrix in matrices]),
        "suite_versions": _all_equal([
            package["suite_versions"] for package in packages]),
        "repeat_structure": _all_equal([
            manifest.get("repeats") for manifest in manifests]),
        "evidence_adapter_profiles": _all_equal(profiles),
    }
    compatible = all(checks.values())
    task_maps = [
        {task["task_id"]: task for task in matrix["tasks"]}
        for matrix in matrices
    ]
    task_ids = sorted(set().union(*(set(mapping) for mapping in task_maps)))
    rows = []
    for task_id in task_ids:
        task_items = [mapping.get(task_id) for mapping in task_maps]
        present = [item for item in task_items if item is not None]
        decisions = [(item.get("task_decision") or {}) if item else {}
                     for item in task_items]
        scores = [
            item.get("observed_performance") if item else None
            for item in task_items
        ]
        confidences = [
            (item.get("scenario_breadth_percent",
                      item.get("engineering_confidence_percent", 0)) if item else 0)
            for item in task_items
        ]
        task_checks = {
            "present_for_all_subjects": len(present) == len(matrices),
            "observed_for_all_subjects": all(score is not None for score in scores),
            "same_scenarios": _all_equal([
                item.get("scenario_ids") if item else None
                for item in task_items]),
            "instrument_maturity": _all_equal([
                decision.get("instrument_maturity") for decision in decisions]),
        }
        if formal_qualification:
            task_checks.update({
                "demonstrated_for_all_subjects": all(
                    item and item.get("status") == "demonstrated"
                    for item in task_items),
                "human_rater_protocol_for_all_subjects": all(
                    (decision.get("rater_protocol") or {}).get("satisfied") is True
                    for decision in decisions),
            })
        task_comparable = compatible and all(task_checks.values())
        numeric = [value for value in scores if value is not None]
        leaders = []
        if task_comparable and numeric:
            best = max(numeric)
            leaders = [
                chr(65 + index) for index, value in enumerate(scores)
                if value == best
            ]
        rows.append({
            "task_id": task_id,
            "task": present[0]["task"] if present else task_id,
            "scores": scores,
            "score_percent": [
                None if score is None else round(score / 4 * 100, 1)
                for score in scores
            ],
            "evidence_confidence_percent": confidences,
            "distinct_scenarios": [
                item.get("distinct_scenarios", 0) if item else 0
                for item in task_items
            ],
            "minimum_observations": [
                item.get("minimum_observations") if item else None
                for item in task_items
            ],
            "comparable": task_comparable,
            "checks": task_checks,
            "leaders": leaders,
            "spread": (
                round(max(numeric) - min(numeric), 3)
                if task_comparable and numeric else None),
        })
    all_task_rows = list(rows)
    total_task_rows = len(all_task_rows)
    comparable_task_rows = sum(
        row["comparable"] for row in all_task_rows)
    filtered_task_rows = (
        sum(not row["comparable"] for row in all_task_rows)
        if only_comparable else 0)
    if only_comparable:
        rows = [row for row in rows if row["comparable"]]
    if sort_by == "confidence":
        rows.sort(key=lambda row: (
            min(row["evidence_confidence_percent"]), row["task_id"]),
                  reverse=True)
    elif sort_by == "spread":
        rows.sort(key=lambda row: (
            row["spread"] is not None, row["spread"] or 0, row["task_id"]),
                  reverse=True)
    elif sort_by == "leader":
        rows.sort(key=lambda row: (
            bool(row["leaders"]), row["leaders"], row["task_id"]), reverse=True)
    else:
        rows.sort(key=lambda row: row["task_id"])
    leader_counts = {chr(65 + index): 0 for index in range(len(matrices))}
    for row in rows:
        if len(row["leaders"]) == 1:
            leader_counts[row["leaders"][0]] += 1
    subject_rows = []
    for index, (ref, matrix, package, adapter_profiles) in enumerate(
            zip(refs, matrices, packages, profiles)):
        subject_rows.append({
            **matrix,
            "column": chr(65 + index),
            "reference": ref,
            "subject_descriptor": package.get("subject"),
            "adapter_profiles": adapter_profiles,
        })
    return {
        "kind": "ecm-multi-comparison",
        "schema": "aies-engineering-comparison/v2",
        "subject_family": "ai-deployment",
        "layout": "pair" if len(subject_rows) == 2 else "matrix",
        "reference_policy": {
            "minimum": MIN_COMPARISON_SUBJECTS,
            "maximum": MAX_COMPARISON_SUBJECTS,
            "received": len(subject_rows),
        },
        "comparison_mode": (
            "formal-qualification" if formal_qualification
            else "engineering-observed"),
        "compatible": compatible,
        "checks": checks,
        "subjects": subject_rows,
        "tasks": rows,
        "summary": {
            "subjects": len(subject_rows),
            "tasks": total_task_rows,
            "rows_returned": len(rows),
            "filtered_noncomparable_tasks": filtered_task_rows,
            "comparable_tasks": comparable_task_rows,
            "not_comparable_tasks": total_task_rows - comparable_task_rows,
            "sole_leads": leader_counts,
            "assessed_tasks_by_subject": {
                subject_rows[index]["column"]: sum(
                    row["scores"][index] is not None
                    for row in all_task_rows)
                for index in range(len(subject_rows))
            },
            "evidence_gaps_by_subject": {
                subject_rows[index]["column"]: sum(
                    row["scores"][index] is None
                    for row in all_task_rows)
                for index in range(len(subject_rows))
            },
        },
        "caveats": [
            value for value in (
                "A repeated reference is a protocol self-check, not independent "
                "comparative evidence." if len(set(refs)) != len(refs) else None,
                None if compatible else
                "At least one protocol-level compatibility check failed; "
                "task leaders are suppressed.",
            ) if value
        ],
        "next_actions": _comparison_next_actions(
            compatible=compatible,
            failed_checks=[
                name for name, passed in checks.items() if not passed
            ],
            comparable=comparable_task_rows,
            total=total_task_rows,
            evidence_kind="engineering tasks",
        ),
        "claim_boundary": (
            "Leaders identify higher compatible observed scores only. They are "
            "not a selection, deployment, qualification, or authorization grant."),
    }


def render_ecm_markdown(cmp: dict) -> str:
    lines = ["# Engineering Capability Matrix Comparison", "",
             "> **INFORMATIONAL — NOT A QUALIFICATION OR SELECTION GRANT.**", "",
             f"Mode: **{cmp.get('comparison_mode', 'formal-qualification')}**", "",
             f"A: `{cmp['a']['subject']}` · B: `{cmp['b']['subject']}`", "",
             "| Task | A observed performance | B observed performance | Comparison |",
             "|---|---:|---:|---|"]
    for row in cmp["tasks"]:
        av = "—" if row["a"] is None else f"{row['a'] / 4 * 100:.0f}%"
        bv = "—" if row["b"] is None else f"{row['b'] / 4 * 100:.0f}%"
        if row["winner"]:
            result = f"formally comparable; winner {row['winner']}"
        elif row.get("higher_observed"):
            result = (
                f"compatible observed scores; higher {row['higher_observed']}")
        elif row["comparable"]:
            result = "compatible observed scores; tie"
        else:
            result = "not comparable for this task"
        lines.append(f"| {row['task']} | {av} | {bv} | {result} |")
    if not cmp["compatible"]:
        failed = ", ".join(name for name, ok in cmp["checks"].items() if not ok)
        lines += ["", f"Protocol mismatch ({failed}): no task winner is emitted."]
    return "\n".join(lines) + "\n"


def render_ecm_many_markdown(cmp: dict) -> str:
    subjects = cmp["subjects"]
    lines = [
        "# Engineering Capability Matrix Comparison",
        "",
        "> **INFORMATIONAL — NOT A QUALIFICATION, SELECTION, OR DEPLOYMENT GRANT.**",
        "",
        f"Mode: **{cmp['comparison_mode']}** · "
        f"{len(subjects)} subjects · "
        f"{cmp['summary']['comparable_tasks']}/{cmp['summary']['tasks']} "
        f"tasks comparable · {cmp.get('layout', 'matrix')} layout",
        (
            f"Rows shown: {cmp['summary']['rows_returned']}/"
            f"{cmp['summary']['tasks']} "
            f"({cmp['summary']['filtered_noncomparable_tasks']} "
            "non-comparable filtered)"
            if cmp["summary"]["filtered_noncomparable_tasks"] else
            f"Rows shown: {cmp['summary']['rows_returned']}"),
        "",
        "| | " + " | ".join(subject["column"] for subject in subjects) + " |",
        "|---|" + "|".join("---" for _ in subjects) + "|",
        "| Subject | " + " | ".join(
            f"`{subject['subject']}`" for subject in subjects) + " |",
        "| Run | " + " | ".join(
            f"`{subject['run_id']}`" for subject in subjects) + " |",
        "| Evidence adapters | " + " | ".join(
            ", ".join(subject["adapter_profiles"]) for subject in subjects) + " |",
        "",
        "## Coverage summary",
        "",
        "| | " + " | ".join(
            subject["column"] for subject in subjects) + " |",
        "|---|" + "|".join("---:" for _ in subjects) + "|",
        "| Assessed tasks | " + " | ".join(
            str(cmp["summary"]["assessed_tasks_by_subject"][
                subject["column"]])
            for subject in subjects) + " |",
        "| Evidence gaps | " + " | ".join(
            str(cmp["summary"]["evidence_gaps_by_subject"][
                subject["column"]])
            for subject in subjects) + " |",
        "| Sole higher-observed rows | " + " | ".join(
            str(cmp["summary"]["sole_leads"][subject["column"]])
            for subject in subjects) + " |",
        "",
        "## Task matrix",
        "",
        "| Engineering task | " + " | ".join(
            f"{subject['column']} performance / confidence"
            for subject in subjects) + " | Result |",
        "|---|" + "|".join("---:" for _ in subjects) + "|---|",
    ]
    for row in cmp["tasks"]:
        cells = []
        for score, confidence, distinct, minimum in zip(
                row["score_percent"], row["evidence_confidence_percent"],
                row["distinct_scenarios"], row["minimum_observations"]):
            if score is None:
                cells.append("not assessed")
            else:
                denominator = "—" if minimum is None else str(minimum)
                cells.append(
                    f"{score:.0f}% / {confidence:.0f}% "
                    f"({distinct}/{denominator} scenarios)")
        if not row["comparable"]:
            result = "not comparable"
        elif len(row["leaders"]) > 1:
            result = "tie: " + ", ".join(row["leaders"])
        else:
            result = "higher observed: " + row["leaders"][0]
        lines.append(
            f"| {row['task_id']} — {row['task']} | "
            + " | ".join(cells) + f" | {result} |")
    failed = [name for name, ok in cmp["checks"].items() if not ok]
    if failed:
        lines += [
            "",
            "**Protocol mismatch:** " + ", ".join(failed)
            + ". No task leader is emitted until evidence is compatible.",
        ]
    for caveat in cmp.get("caveats") or []:
        lines += ["", f"> **Caveat:** {caveat}"]
    lines += ["", "## Evidence-driven next actions", ""]
    lines += [
        f"{index}. {action}"
        for index, action in enumerate(cmp.get("next_actions") or [], 1)
    ]
    lines += ["", cmp["claim_boundary"], ""]
    return "\n".join(lines)

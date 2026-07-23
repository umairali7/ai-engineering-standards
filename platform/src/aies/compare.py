"""Result history and comparison (M2, PLATFORM.md §9).

Comparisons are only meaningful on identical suite versions: an area
whose suite version differs between the two runs is reported as
incomparable, never silently diffed. Deltas are presentation over the
same evidence — a comparison makes no additional claims.
"""

from __future__ import annotations

from . import constants as C
from . import workspace


class CompareError(Exception):
    pass


def list_runs(model: str | None = None) -> list[dict]:
    """Result history: every run's manifest summary, newest first."""
    out = []
    rdir = workspace.runs_dir()
    for d in sorted(rdir.iterdir(), reverse=True):
        manifest_path = d / "manifest.json"
        if not d.is_dir() or not manifest_path.exists():
            continue
        m = workspace.read_json(manifest_path)
        if model and m["model"]["registry_id"] != model:
            continue
        out.append({
            "run_id": m["run_id"],
            "model": m["model"]["registry_id"],
            "profile": m["profile"],
            "risk_tier": m["risk_tier"],
            "areas": [a["area"] for a in m["areas"]],
            "status": m.get("status", "unknown"),
            "created_at": m.get("created_at"),
            "aggregated": (d / "evidence-package.json").exists(),
        })
    return out


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
        "a": {"run_id": a["run_id"], "model": a["model"]["registry_id"],
              "profile": a["profile"]},
        "b": {"run_id": b["run_id"], "model": b["model"]["registry_id"],
              "profile": b["profile"]},
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
    a("---")
    a("A comparison is presentation over existing evidence; it makes no "
      "additional claims (PLATFORM.md §9).")
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

    if len(refs) < 2:
        raise CompareError("compare requires at least two run or deployment references")
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
        "comparison_mode": (
            "formal-qualification" if formal_qualification
            else "engineering-observed"),
        "compatible": compatible,
        "checks": checks,
        "subjects": subject_rows,
        "tasks": rows,
        "summary": {
            "subjects": len(subject_rows),
            "tasks": len(rows),
            "comparable_tasks": sum(row["comparable"] for row in rows),
            "not_comparable_tasks": sum(
                not row["comparable"] for row in rows),
            "sole_leads": leader_counts,
        },
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
        "tasks comparable",
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
    lines += ["", cmp["claim_boundary"], ""]
    return "\n".join(lines)

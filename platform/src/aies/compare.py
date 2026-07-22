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


def compare_ecm(ref_a: str, ref_b: str) -> dict:
    """Compare task evidence only when protocol metadata is compatible."""
    from . import ecm
    a, b = ecm.engineering_capability_matrix(ref_a), ecm.engineering_capability_matrix(ref_b)
    pa, pb = _resolve_package(ref_a), _resolve_package(ref_b)
    ma = workspace.read_json(workspace.run_dir(a["run_id"]) / "manifest.json")
    mb = workspace.read_json(workspace.run_dir(b["run_id"]) / "manifest.json")
    checks = {
        "risk_tier": a["risk_tier"] == b["risk_tier"],
        "profile": a["profile"] == b["profile"],
        "mapping_version": a["mapping"]["version"] == b["mapping"]["version"],
        "mapping_schema": a["mapping"]["schema"] == b["mapping"]["schema"],
        "task_decision_semantics": (
            a["task_decision_semantics_version"]
            == b["task_decision_semantics_version"]),
        "rater_protocol": a["rater_kinds"] == b["rater_kinds"],
        "suite_versions": pa["suite_versions"] == pb["suite_versions"],
        "repeat_structure": ma.get("repeats") == mb.get("repeats"),
    }
    compatible = all(checks.values())
    rows = []
    for left, right in zip(a["tasks"], b["tasks"]):
        left_decision = left.get("task_decision") or {}
        right_decision = right.get("task_decision") or {}
        task_checks = {
            "same_scenarios": left.get("scenario_ids") == right.get("scenario_ids"),
            "demonstrated": left["status"] == right["status"] == "demonstrated",
            "rater_protocol": (
                (left_decision.get("rater_protocol") or {}).get("satisfied") is True
                and (right_decision.get("rater_protocol") or {}).get("satisfied") is True),
            "instrument_maturity": (
                left_decision.get("instrument_maturity")
                == right_decision.get("instrument_maturity")),
        }
        comparable = compatible and all(task_checks.values())
        winner = None if not comparable or left["observed_performance"] == right["observed_performance"] else (
            "A" if left["observed_performance"] > right["observed_performance"] else "B")
        rows.append({"task": left["task"], "a": left["observed_performance"],
                     "b": right["observed_performance"], "comparable": comparable,
                     "checks": task_checks, "winner": winner})
    return {"kind": "ecm-comparison", "compatible": compatible, "checks": checks,
            "a": a, "b": b, "tasks": rows}


def render_ecm_markdown(cmp: dict) -> str:
    lines = ["# Engineering Capability Matrix Comparison", "",
             "> **INFORMATIONAL — NOT A QUALIFICATION OR SELECTION GRANT.**", "",
             f"A: `{cmp['a']['subject']}` · B: `{cmp['b']['subject']}`", "",
             "| Task | A observed performance | B observed performance | Comparison |",
             "|---|---:|---:|---|"]
    for row in cmp["tasks"]:
        av = "—" if row["a"] is None else f"{row['a'] / 4 * 100:.0f}%"
        bv = "—" if row["b"] is None else f"{row['b'] / 4 * 100:.0f}%"
        result = (f"comparable; winner {row['winner']}" if row["winner"] else
                  ("comparable; tie" if row["comparable"] else "incomparable / insufficient evidence"))
        lines.append(f"| {row['task']} | {av} | {bv} | {result} |")
    if not cmp["compatible"]:
        failed = ", ".join(name for name, ok in cmp["checks"].items() if not ok)
        lines += ["", f"Protocol mismatch ({failed}): no task winner is emitted."]
    return "\n".join(lines) + "\n"

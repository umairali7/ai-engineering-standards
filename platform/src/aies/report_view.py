"""Shared factual model for every per-run report representation.

The model is presentation-only. It derives readable facts from the stored
Evidence Package and rating records, but never changes scoring, admission,
assessment outcomes, qualification records, or deployment authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from . import __version__, constants as C, workspace


KIND = "aies-run-report-view"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ReportContext:
    """One immutable calculation shared by Markdown, HTML, and JSON renderers."""

    view: dict
    package: dict
    manifest: dict
    matrix: dict
    source_observations: dict


def area_verdict(area: dict) -> tuple[str, str]:
    protocol = area.get("rater_protocol") or {}
    if protocol and not protocol.get("satisfied"):
        reasons = protocol.get("reasons") or [
            "verified human-rater protocol incomplete"]
        return "BLOCKED", "rater protocol incomplete: " + "; ".join(reasons)
    if not area["decisional"]:
        distinct = area.get("sample_adequacy_basis") == "distinct_scenarios"
        count = (area.get("n_distinct_scenarios", area["n_scored"])
                 if distinct else area["n_scored"])
        unit = "distinct scenarios" if distinct else "scored items"
        return "BLOCKED", (
            f"non-decisional ({count}/{area['min_sample']} {unit})")
    if area.get("ev3_hard_fail"):
        return "BLOCKED", "EV3 safety hard gate failed"
    if not area.get("gates_passed", True):
        failed = [
            gate["dimension"] for gate in area["gates"]
            if not gate["passed"]]
        return "BLOCKED", f"gate failure: {', '.join(failed)}"
    return (
        "THRESHOLD MET",
        "admitted evidence informs a human grant review up to "
        f"{area.get('cl') or 'CL?'}",
    )


def gate_status(area: dict) -> str:
    if not area.get("n_scored") or not area.get("dimensions"):
        return "NOT EVALUATED"
    if (area.get("rater_protocol") or {}).get("satisfied") is False:
        return "NOT ADMITTED"
    return ("PASS" if area.get("gates_passed")
            and not area.get("ev3_hard_fail") else "FAIL")


def overall_readiness(verdicts: dict[str, str]) -> tuple[str, list[str]]:
    blocked = [
        area for area, verdict in verdicts.items()
        if verdict != "THRESHOLD MET"]
    return ("READY" if not blocked else "BLOCKED", blocked)


def _source_observations(
    run_id: str,
) -> dict[str, dict[str, dict[str, list[int]]]]:
    from . import rating

    rdir = workspace.run_dir(run_id)
    response_areas = {
        path.name: workspace.read_json(path).get("area", "unknown")
        for path in (rdir / "responses").glob("*.json")
    }
    output: dict[str, dict[str, dict[str, list[int]]]] = {}
    for record in rating.collect_ratings(run_id):
        kind = (record.get("provenance") or {}).get(
            "rater_kind", "unknown")
        source = "human" if kind == "human" else "automated"
        area = response_areas.get(
            record.get("rates_response"), "unknown")
        buckets = output.setdefault(area, {}).setdefault(
            source, {dimension: [] for dimension in C.DIMENSIONS})
        for dimension, score in (record.get("scores") or {}).items():
            if dimension in buckets and isinstance(score, int):
                buckets[dimension].append(score)
    return output


def _source_stat(observations: dict, source: str, dimension: str) -> dict:
    values = observations.get(source, {}).get(dimension, [])
    return {
        "n": len(values),
        "mean": round(mean(values), 3) if values else None,
    }


def source_display(stat: dict) -> str:
    return (
        f"{stat['mean']} (n={stat['n']})"
        if stat.get("mean") is not None else "—")


def _human_review(run_id: str) -> dict | None:
    path = workspace.run_dir(run_id) / "review-package.json"
    if not path.exists():
        return None
    return workspace.read_json(path).get("human_consideration") or None


def human_evaluation_label(evaluation: dict) -> str:
    record = evaluation.get("human_evaluation") or {}
    if record.get("status") == "reviewed":
        return f"☑ Reviewed — {record.get('evaluator') or 'named human'}"
    return "☐ Not reviewed (optional)"


def _residual_risks(package: dict) -> list[dict]:
    risks: list[dict] = []
    if (package.get("rating_admission") or {}).get("advisory_ratings", 0):
        risks.append({
            "kind": "automated-review-calibration",
            "area": None,
            "dimension": None,
            "message": (
                "Scores are judge-produced and remain advisory until the judge "
                "is calibrated against human anchors "
                "(AIES-AESQS-PR-01-R09)."),
        })
    for area_code, area in package["areas"].items():
        if not area["decisional"]:
            protocol = area.get("rater_protocol") or {}
            if protocol and not protocol.get("satisfied"):
                remedy = (
                    "complete verified human-rater admission, independence, "
                    "agreement, and double-rating coverage")
            elif area.get("sample_adequacy_basis") == "distinct_scenarios":
                remedy = (
                    "collect more distinct scenarios; exact repeats do not "
                    "repair breadth")
            else:
                remedy = "collect more independently admissible evidence"
            risks.append({
                "kind": "non-decisional",
                "area": area_code,
                "dimension": None,
                "message": (
                    f"{C.competency_label(area_code)} is non-decisional — "
                    f"{remedy}."),
            })
        for gate in area["gates"]:
            decision_value = gate.get("decision_value")
            threshold = gate.get("threshold")
            if (gate.get("passed") and decision_value is not None
                    and threshold is not None
                    and decision_value - threshold < 0.5):
                suffix = (
                    " This is the safety gate."
                    if gate["dimension"] == "EV3" else "")
                risks.append({
                    "kind": "thin-gate-margin",
                    "area": area_code,
                    "dimension": gate["dimension"],
                    "message": (
                        f"{C.competency_label(area_code)} "
                        f"{C.identifier_label(gate['dimension'])} passed by a "
                        f"thin margin (decision value {decision_value} vs "
                        f"threshold {threshold}).{suffix}"),
                })
    if not risks:
        risks.append({
            "kind": "none-elevated",
            "area": None,
            "dimension": None,
            "message": (
                "No elevated residual risk was flagged by the platform; a "
                "named human still owns the grant decision (D8)."),
        })
    return risks


def _area_view(
    code: str,
    area: dict,
    package: dict,
    source_observations: dict,
) -> dict:
    gates = {gate["dimension"]: gate for gate in area["gates"]}
    dimensions = []
    for dimension in C.DIMENSIONS:
        resolved = area["dimensions"].get(dimension)
        gate = gates.get(dimension, {})
        dimensions.append({
            "code": dimension,
            "label": C.identifier_label(dimension),
            "sources": {
                "automated": _source_stat(
                    source_observations, "automated", dimension),
                "human": _source_stat(
                    source_observations, "human", dimension),
            },
            "resolved": ({
                "n": resolved["n"],
                "mean": resolved["mean"],
                "ci90_low": resolved["ci90_low"],
                "ci90_high": resolved["ci90_high"],
                "decision_value": resolved["ci90_low"],
            } if resolved else None),
            "gate": {
                "threshold": gate.get("threshold"),
                "passed": bool(gate.get("passed")),
                "status": "PASS" if gate.get("passed") else "FAIL",
                "reason": gate.get("reason"),
            },
        })
    verdict, reason = area_verdict(area)
    return {
        "code": code,
        "label": C.competency_label(code),
        "suite_version": package["suite_versions"].get(code, "unknown"),
        "evidence": {
            "resolved_items": area["n_scored"],
            "admitted_observations": area.get("admitted_ratings", 0),
            "distinct_scenarios": area.get(
                "n_distinct_scenarios", area["n_scored"]),
            "minimum": area["min_sample"],
            "adequacy_basis": area.get(
                "sample_adequacy_basis", "legacy_scored_items"),
            "advisory_automated_ratings": area.get("advisory_ratings", 0),
            "decisional": area["decisional"],
        },
        "rater_protocol": area.get("rater_protocol") or {},
        "dimensions": dimensions,
        "aggregate": area.get("aggregate_A"),
        "competency_level": {
            "code": area.get("cl"),
            "label": (
                C.identifier_label(area["cl"]) if area.get("cl") else None),
            "note": area.get("cl_note"),
        },
        "ev3_hard_fail": bool(area.get("ev3_hard_fail")),
        "readiness": {
            "verdict": verdict,
            "reason": reason,
            "gate_status": gate_status(area),
        },
        "autonomy_envelope": [
            {
                "risk_tier": tier,
                "risk_tier_label": C.risk_tier_label(tier),
                "autonomy_level": autonomy,
                "autonomy_level_label": C.autonomy_level_label(autonomy),
            }
            for tier, autonomy in area["al_envelope"].items()
        ],
    }


def build_context(run_id: str, *, matrix: dict | None = None) -> ReportContext:
    from . import diagnostics, ecm, evaluation, run_mode, subjects

    workspace.validate_run_id(run_id)
    rdir = workspace.run_dir(run_id)
    package_path = rdir / "evidence-package.json"
    manifest_path = rdir / "manifest.json"
    if not package_path.exists() or not manifest_path.exists():
        raise FileNotFoundError(
            f"run {run_id!r} requires manifest.json and evidence-package.json")
    package = workspace.read_json(package_path)
    manifest = workspace.read_json(manifest_path)
    formal = run_mode.is_formal(manifest)
    evaluation_summary = evaluation.summarize(run_id)
    diagnostic_summary = diagnostics.summarize(run_id)
    matrix = matrix or ecm.engineering_capability_matrix(run_id)
    observations = _source_observations(run_id)
    human_review = _human_review(run_id)
    areas = [
        _area_view(
            code, area, package, observations.get(code, {}))
        for code, area in package["areas"].items()
    ]
    verdicts = {
        area["code"]: area["readiness"]["verdict"] for area in areas}
    readiness, blocked = overall_readiness(verdicts)
    threshold_met = sum(
        area["readiness"]["verdict"] == "THRESHOLD MET"
        for area in areas)
    subject = subjects.from_manifest(manifest)
    execution = subjects.execution_from_manifest(manifest)
    evaluation_scope = run_mode.scope(manifest)
    model = package.get("model") or {}
    environment = package.get("environment_fingerprint") or {}
    view = {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "platform_version": __version__,
        "authority": "informational-read-only",
        "run_id": run_id,
        "run_purpose": run_mode.purpose(manifest),
        "formal_qualification_requested": formal,
        "title": (
            "AIES Qualification Evidence Package" if formal
            else "AIES Engineering Evaluation Report"),
        "subject": {
            "id": subject.get("id", model.get("registry_id")),
            "display_name": subject.get("display_name"),
            "kind": subject.get("kind", "ai_deployment"),
            "descriptor_schema": subject.get("schema"),
            "privacy": subject.get("privacy"),
            "executor_kind": execution.get("executor_id", "runtime-generation"),
            "executor_contract": execution.get("contract"),
            "deployment_evidence": model.get("registry_id"),
            "checksum": model.get("checksum"),
        },
        "scope": {
            "profile": package.get("profile"),
            "profile_version": package.get("profile_version"),
            "profile_role": evaluation_scope["profile_role"],
            "composition": evaluation_scope,
            "risk_tier": package.get("risk_tier"),
            "risk_tier_label": C.risk_tier_label(package.get("risk_tier")),
            "subject_kind": package.get("subject_kind"),
            "subject_kind_label": C.identifier_label(
                package.get("subject_kind")),
        },
        "status": {
            "engineering_evaluation": evaluation_summary.get("status"),
            "human_evaluation": evaluation_summary.get("human_evaluation"),
            "human_evaluation_label": human_evaluation_label(
                evaluation_summary),
            "grant_status": package.get("grant_status"),
        },
        "engineering_evaluation": evaluation_summary,
        "grounding_diagnostics": diagnostic_summary,
        "human_review": human_review,
        "qualification": {
            "requested": formal,
            "rating_admission": package.get("rating_admission") or {},
            "nondecisional_areas": [
                area["code"] for area in areas
                if not area["evidence"]["decisional"]],
            "readiness": {
                "status": readiness if formal else "NOT REQUESTED",
                "blocked_areas": blocked if formal else [],
                "threshold_met_areas": threshold_met,
                "total_areas": len(areas),
            },
            "residual_risks": _residual_risks(package) if formal else [],
        },
        "environment": environment,
        "areas": areas,
        "engineering_capability_matrix": matrix,
        "provenance": {
            "raters": package.get("raters") or [],
            "aggregated_at": package.get("aggregated_at"),
            "suite_versions": package.get("suite_versions") or {},
            "evidence_schema": package.get("evidence_schema"),
            "canonical_evidence_artifact": "evidence-package.json",
        },
        "artifacts": {
            "canonical_evidence": "evidence-package.json",
            "legacy_report_json": "report.json",
            "report_view": "report-view.json",
            "engineering_capability_matrix": (
                "engineering-capability-matrix.json"),
            "grounding_diagnostics": "grounding-diagnostics.json",
            "assessment_coverage": "assessment-coverage.json",
            "evidence_remediation_plan": "evidence-remediation-plan.json",
            "standards_traceability": "standards-traceability.json",
        },
        "limitations": [
            "This report view is informational and cannot qualify, grant, or "
            "authorize deployment.",
            "The Evidence Package remains the canonical evidence artifact; "
            "this view does not replace or rewrite it.",
            "Automated and human observations remain separate, and unavailable "
            "evidence never means a passing or zero-issue result.",
            "A weighting profile does not imply that its same-named declarative "
            "assessment composition was executed.",
        ],
    }
    return ReportContext(
        view=view,
        package=package,
        manifest=manifest,
        matrix=matrix,
        source_observations=observations,
    )


def build(run_id: str, *, matrix: dict | None = None) -> dict:
    return build_context(run_id, matrix=matrix).view

"""Competency-suite validation for the shipped AIES benchmark corpus."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .constants import DIMENSIONS, RISK_TIERS
from .runner import (SCENARIO_REQUIRED, SuiteError, competencies_dir, load_area,
                     load_scenario_documents)

AREA_RE = re.compile(r"^CA-(\d{2})")
SCENARIO_RE = re.compile(r"^SC-(CA\d{2})-(\d{3})$")


class SuiteValidationError(Exception):
    pass


def validate(root: Path | None = None) -> dict[str, Any]:
    base = root or competencies_dir()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    applicability: list[dict[str, str]] = []
    areas: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}

    if not base.exists():
        errors.append(_issue(base, "competencies directory does not exist"))
        return _report(base, areas, errors, warnings, applicability=applicability)

    for area_dir in sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith("CA-")):
        area_code = _area_code(area_dir.name)
        if area_code is None:
            warnings.append(_issue(area_dir, "directory is not named with a CA-## prefix"))
            continue
        area_report = _validate_area(area_dir, area_code, seen_ids, errors, warnings,
                                     applicability)
        areas.append(area_report)

    if not areas:
        errors.append(_issue(base, "no competency area directories found"))

    assessments = _validate_assessments(errors)
    from . import task_mappings
    try:
        mapping_problems = task_mappings.validate(task_mappings.load())
    except Exception as exc:  # pragma: no cover - malformed registry is surfaced
        mapping_problems = [str(exc)]
    for problem in mapping_problems:
        errors.append(_issue(task_mappings.registry_path(), f"task mapping: {problem}"))

    review_status = None
    if root is None:
        from . import design_reviews

        scenarios = []
        for area in areas:
            try:
                scenarios.extend(load_area(area["area"])[1])
            except SuiteError as exc:  # already represented by area validation
                errors.append(_issue(base, f"could not verify design reviews: {exc}"))
        review_status = design_reviews.ledger_status(scenarios)
        if review_status["stale"]:
            warnings.append(_issue(
                design_reviews.default_ledger_path(),
                f"{review_status['stale']} accepted design-review binding(s) are stale; "
                "changed instruments have returned to pending review"))
        if review_status["unknown"]:
            warnings.append(_issue(
                design_reviews.default_ledger_path(),
                f"{review_status['unknown']} accepted design-review binding(s) reference "
                "scenario IDs not present in the corpus"))

    report = _report(base, areas, errors, warnings, assessments, applicability)
    report["design_review_ledger"] = review_status
    return report


def _validate_assessments(errors: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Validate the shipped declarative assessments (ADR-0005) as part of the
    same gate CI runs, so a broken assessment file cannot ship silently. Import
    is local to keep the suite validator usable even if the assessment module or
    its data directory is absent."""
    from . import assessments as A

    out: list[dict[str, Any]] = []
    d = A.assessments_dir()
    if not d.exists():
        return out
    for path in sorted(d.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            problems = A.validate(data)
        except Exception as exc:  # pragma: no cover - malformed YAML
            problems = [f"could not parse: {exc}"]
            data = None
        for problem in problems:
            errors.append(_issue(path, problem))
        out.append({
            "id": (data or {}).get("id", path.stem) if isinstance(data, dict) else path.stem,
            "path": str(path),
            "valid": not problems,
            "problems": problems,
        })
    return out


def render(report: dict[str, Any]) -> str:
    summary = report["summary"]
    status = "PASS" if report["valid"] else "FAIL"
    lines = [
        f"suite validation: {status}",
        f"  root     : {report['root']}",
        f"  areas    : {summary['areas']}",
        f"  scenarios: {summary['scenarios']}",
        f"  assessmnt: {summary.get('assessments', 0)}",
        f"  warnings : {len(report['warnings'])}",
        f"  declared : {len(report.get('declared_non_applicable', []))}",
        f"  errors   : {len(report['errors'])}",
    ]
    review_status = report.get("design_review_ledger")
    if review_status:
        lines.append(
            f"  reviews  : {review_status['accepted']} hash-bound accepted, "
            f"{review_status['stale']} stale, {review_status['unknown']} unknown")
    for issue in report["errors"][:20]:
        lines.append(f"  error   : {issue['file']}: {issue['message']}")
    if len(report["errors"]) > 20:
        lines.append(f"  error   : ... {len(report['errors']) - 20} more")
    for issue in report["warnings"][:10]:
        lines.append(f"  warning : {issue['file']}: {issue['message']}")
    if len(report["warnings"]) > 10:
        lines.append(f"  warning : ... {len(report['warnings']) - 10} more")
    return "\n".join(lines)


def calibrate(root: Path | None = None) -> dict[str, Any]:
    """Calibration-coverage report (CALIBRATION.md): per area, how far each
    scenario has progressed as a *measurement instrument* — does it carry
    calibration metadata, a ceiling anchor, a floor trap, a refuse/escalate case,
    a hold-out twin, and what maturity does it claim (design-time vs empirical).
    Advisory: it surfaces where the design-time calibration pass should go; it
    never fails a build."""
    base = root or competencies_dir()
    areas: list[dict[str, Any]] = []
    if not base.exists():
        return {"root": str(base), "areas": areas, "totals": {}}

    for area_dir in sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith("CA-")):
        area_code = _area_code(area_dir.name)
        if area_code is None:
            continue
        scen_dir = area_dir / "scenarios"
        files = sorted(scen_dir.glob("*.yaml")) if scen_dir.exists() else []
        expanded: list[dict] = []
        for f in files:
            try:
                expanded.extend(load_scenario_documents(f))
            except (OSError, yaml.YAMLError, SuiteError):
                continue
        row = {"area": area_code, "scenarios": len(expanded), "calibrated": 0,
               "ceiling_anchor": 0, "floor_trap": 0, "refuse_case": 0,
               "hold_out_twins": 0, "design_reviewed": 0, "empirically_calibrated": 0,
               "rt3_rt4": 0, "families": 0, "high_tier_families": 0,
               "rt": {"RT1": 0, "RT2": 0, "RT3": 0, "RT4": 0}}
        families: set[str] = set()
        high_families: set[str] = set()
        for sc in expanded:
            if sc.get("risk_tier") in row["rt"]:
                row["rt"][sc["risk_tier"]] += 1
            fam = sc.get("family")
            if fam:
                families.add(fam)
            if sc.get("risk_tier") in ("RT3", "RT4"):
                row["rt3_rt4"] += 1
                if fam:
                    high_families.add(fam)
            if sc.get("failure_conditions"):
                row["floor_trap"] += 1
            cal = sc.get("calibration")
            if isinstance(cal, dict) and cal:
                row["calibrated"] += 1
                if cal.get("ceiling_anchor"):
                    row["ceiling_anchor"] += 1
                if cal.get("expected_refusal"):
                    row["refuse_case"] += 1
                if cal.get("hold_out_twin"):
                    row["hold_out_twins"] += 1
                es = cal.get("empirical_status") or {}
                if es.get("design_reviewed"):
                    row["design_reviewed"] += 1
                if es.get("empirically_calibrated"):
                    row["empirically_calibrated"] += 1
        row["families"] = len(families)
        # behavioral diversity at the high tiers: distinct KINDS of decision, not
        # distinct prompts — a thin high_tier_families count is a coverage gap even
        # when rt3_rt4 looks healthy (CALIBRATION.md §5).
        row["high_tier_families"] = len(high_families)
        areas.append(row)

    keys = ("scenarios", "calibrated", "ceiling_anchor", "floor_trap", "refuse_case",
            "hold_out_twins", "design_reviewed", "empirically_calibrated", "rt3_rt4")
    totals = {k: sum(a[k] for a in areas) for k in keys}
    return {"root": str(base), "areas": areas, "totals": totals}


def render_calibration(report: dict[str, Any]) -> str:
    t = report["totals"]
    n = t.get("scenarios", 0) or 1
    lines = [
        "calibration coverage (design-time; empirical requires a model panel)",
        f"  scenarios          : {t.get('scenarios', 0)}",
        f"  with metadata      : {t.get('calibrated', 0)}/{t.get('scenarios', 0)}",
        f"  ceiling anchor      : {t.get('ceiling_anchor', 0)}   (what a 4 does that a 3 doesn't)",
        f"  floor trap          : {t.get('floor_trap', 0)}",
        f"  refuse/escalate case: {t.get('refuse_case', 0)}",
        f"  hold-out twins      : {t.get('hold_out_twins', 0)}",
        f"  RT3 — Significant / RT4 — Critical scenarios: {t.get('rt3_rt4', 0)}",
        f"  design-reviewed     : {t.get('design_reviewed', 0)}",
        f"  empirically calib.  : {t.get('empirically_calibrated', 0)}   (0 until a model panel exists)",
        "",
        "  behavioral diversity: 'fam' = distinct decision kinds; 'hi-fam' = distinct",
        "  kinds among RT3 — Significant / RT4 — Critical (a thin high-tier family is a coverage gap even if totals look adequate)",
        "",
        "  area    scen  calib  ceil  trap  refuse  twin  high-tier  fam  hi-fam",
    ]
    for a in report["areas"]:
        lines.append(f"  {a['area']:6} {a['scenarios']:5} {a['calibrated']:6} "
                     f"{a['ceiling_anchor']:5} {a['floor_trap']:5} {a['refuse_case']:7} "
                     f"{a['hold_out_twins']:5} {a['rt3_rt4']:6} {a.get('families', 0):4} "
                     f"{a.get('high_tier_families', 0):6}")
    return "\n".join(lines)


def _validate_area(
    area_dir: Path,
    area_code: str,
    seen_ids: dict[str, str],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
    applicability: list[dict[str, str]],
) -> dict[str, Any]:
    definition = _load_yaml(area_dir / "definition.yaml", errors)
    rubric = _load_yaml(area_dir / "rubric.yaml", errors)
    scenario_dir = area_dir / "scenarios"
    scenario_files = sorted(scenario_dir.glob("*.yaml")) if scenario_dir.exists() else []

    if not scenario_dir.exists():
        errors.append(_issue(scenario_dir, "missing scenarios directory"))
    if not scenario_files:
        errors.append(_issue(scenario_dir, "no scenario YAML files found"))

    if isinstance(definition, dict):
        _expect_equal(definition.get("area"), area_code, area_dir / "definition.yaml", "area", errors)
        if not definition.get("scenario_families"):
            warnings.append(_issue(area_dir / "definition.yaml", "scenario_families is empty or missing"))
    if isinstance(rubric, dict):
        _expect_equal(rubric.get("area"), area_code, area_dir / "rubric.yaml", "area", errors)
        sub_criteria = rubric.get("sub_criteria")
        if not isinstance(sub_criteria, dict):
            errors.append(_issue(area_dir / "rubric.yaml", "sub_criteria must be a mapping"))
        else:
            missing = [dim for dim in DIMENSIONS if dim not in sub_criteria]
            unknown = [dim for dim in sub_criteria if dim not in DIMENSIONS]
            if missing:
                errors.append(_issue(area_dir / "rubric.yaml", f"missing sub_criteria dimensions {missing}"))
            if unknown:
                errors.append(_issue(area_dir / "rubric.yaml", f"unknown sub_criteria dimensions {unknown}"))

    valid_scenarios = 0
    expanded_count = 0
    for path in scenario_files:
        try:
            scenarios = load_scenario_documents(path)
        except (OSError, yaml.YAMLError, SuiteError) as exc:
            errors.append(_issue(path, f"could not load scenario document: {exc}"))
            continue
        packed = len(scenarios) > 1
        expanded_count += len(scenarios)
        for scenario in scenarios:
            before = len(errors)
            _validate_scenario(path, scenario, area_code, seen_ids, errors, warnings,
                               applicability, packed=packed)
            if len(errors) == before:
                valid_scenarios += 1

    if expanded_count < 10:
        warnings.append(_issue(scenario_dir, "fewer than 10 scenarios; target suites need broad coverage"))

    return {
        "area": area_code,
        "path": str(area_dir),
        "scenarios": expanded_count,
        "valid_scenarios": valid_scenarios,
    }


def _validate_scenario(
    path: Path,
    scenario: dict[str, Any],
    area_code: str,
    seen_ids: dict[str, str],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
    applicability: list[dict[str, str]] | None = None,
    packed: bool = False,
) -> None:
    applicability = applicability if applicability is not None else []
    missing = [field for field in SCENARIO_REQUIRED if field not in scenario]
    if missing:
        errors.append(_issue(path, f"missing required fields {missing}"))

    scenario_id = scenario.get("id")
    if not isinstance(scenario_id, str) or not SCENARIO_RE.match(scenario_id):
        errors.append(_issue(path, "id must match SC-CA##-###"))
    else:
        expected_area = scenario_id[3:7].replace("CA", "CA-")
        if expected_area != area_code:
            errors.append(_issue(path, f"id prefix {expected_area} does not match directory {area_code}"))
        if not packed and path.stem != scenario_id:
            errors.append(_issue(path, "file name must match scenario id"))
        if scenario_id in seen_ids:
            errors.append(_issue(path, f"duplicate scenario id also used by {seen_ids[scenario_id]}"))
        else:
            seen_ids[scenario_id] = str(path)

    _expect_equal(scenario.get("area"), area_code, path, "area", errors)
    if scenario.get("risk_tier") not in RISK_TIERS:
        errors.append(_issue(path, f"risk_tier must be one of {list(RISK_TIERS)}"))
    if not _non_empty_string(scenario.get("prompt")):
        errors.append(_issue(path, "prompt must be a non-empty string"))
    if not _non_empty_list(scenario.get("expected_qualities")):
        errors.append(_issue(path, "expected_qualities must be a non-empty list"))

    rubric = scenario.get("rubric")
    if not isinstance(rubric, dict) or not rubric:
        errors.append(_issue(path, "rubric must be a non-empty mapping"))
    else:
        unknown = [dim for dim in rubric if dim not in DIMENSIONS]
        declared = _validate_rubric_applicability(path, scenario, rubric, errors)
        for dim in declared:
            applicability.append({
                "file": str(path), "scenario_id": scenario.get("id", ""),
                "dimension": dim,
                "rationale": scenario["rubric_applicability"][dim]["rationale"],
            })
        missing = [dim for dim in DIMENSIONS if dim not in rubric and dim not in declared]
        if unknown:
            errors.append(_issue(path, f"rubric has unknown dimensions {unknown}"))
        if missing:
            warnings.append(_issue(path, f"rubric does not cover dimensions {missing}"))
        for dim, anchors in rubric.items():
            if dim in DIMENSIONS and not _non_empty_list(anchors):
                errors.append(_issue(path, f"rubric.{dim} must be a non-empty list"))

    if "weight" in scenario and not _positive_number(scenario["weight"]):
        errors.append(_issue(path, "weight must be a positive number"))
    if "repeats_min" in scenario and not _positive_int(scenario["repeats_min"]):
        errors.append(_issue(path, "repeats_min must be a positive integer"))
    if "failure_conditions" in scenario and not isinstance(scenario["failure_conditions"], list):
        errors.append(_issue(path, "failure_conditions must be a list when present"))

    if "calibration" in scenario:
        _validate_calibration(path, scenario, area_code, errors, warnings)


_APPLICABILITY_KEYS = {"status", "rationale"}


def _validate_rubric_applicability(path, scenario, rubric, errors) -> set[str]:
    """Validate ADR-0007 declarations and return valid excluded dimensions."""
    data = scenario.get("rubric_applicability")
    if data is None:
        return set()
    if not isinstance(data, dict) or not data:
        errors.append(_issue(path, "rubric_applicability must be a non-empty mapping when present"))
        return set()
    declared: set[str] = set()
    for dim, declaration in data.items():
        if dim not in DIMENSIONS:
            errors.append(_issue(path, f"rubric_applicability has unknown dimension {dim!r}"))
            continue
        if dim in rubric:
            errors.append(_issue(path, f"rubric_applicability.{dim} conflicts with a covered rubric dimension"))
            continue
        if not isinstance(declaration, dict):
            errors.append(_issue(path, f"rubric_applicability.{dim} must be a mapping"))
            continue
        unknown = [key for key in declaration if key not in _APPLICABILITY_KEYS]
        if unknown:
            errors.append(_issue(path, f"rubric_applicability.{dim} has unknown keys {unknown}"))
        if declaration.get("status") != "not_applicable":
            errors.append(_issue(path, f"rubric_applicability.{dim}.status must be 'not_applicable'"))
        rationale = declaration.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(_issue(path, f"rubric_applicability.{dim}.rationale must be a non-empty string"))
        if not unknown and declaration.get("status") == "not_applicable" and isinstance(rationale, str) and rationale.strip():
            declared.add(dim)
    return declared


# Calibration metadata (CALIBRATION.md): a scenario is a measurement instrument;
# this block records WHY it exists and how well it measures. Optional today
# (advisory), so the corpus can be migrated incrementally — but validated when
# present, and surfaced by `aies suites calibrate`.
_CALIBRATION_KEYS = {"objective", "target_competency", "ceiling_anchor",
                     "floor_anchor", "gaming_rationale", "expected_refusal",
                     "hold_out_twin", "empirical_status"}
_CALIBRATION_REQUIRED = ("objective", "ceiling_anchor", "empirical_status")
_EMPIRICAL_STATUS_KEYS = {"design_reviewed", "empirically_calibrated"}


def _validate_calibration(path, scenario, area_code, errors, warnings) -> None:
    cal = scenario.get("calibration")
    if not isinstance(cal, dict) or not cal:
        errors.append(_issue(path, "calibration must be a non-empty mapping when present"))
        return
    for k in cal:
        if k not in _CALIBRATION_KEYS:
            errors.append(_issue(path, f"calibration has unknown key {k!r}"))
    for req in _CALIBRATION_REQUIRED:
        if not cal.get(req):
            errors.append(_issue(path, f"calibration.{req} is required (the ceiling "
                                 "anchor — 'what a 4 does that a 3 does not' — is "
                                 "the load-bearing design-time criterion)"))
    tc = cal.get("target_competency")
    if tc is not None and tc != area_code:
        errors.append(_issue(path, f"calibration.target_competency {tc!r} != area {area_code}"))
    if "expected_refusal" in cal and not isinstance(cal["expected_refusal"], bool):
        errors.append(_issue(path, "calibration.expected_refusal must be a boolean"))
    twin = cal.get("hold_out_twin")
    if twin is not None and not (isinstance(twin, str) and SCENARIO_RE.match(twin)):
        errors.append(_issue(path, "calibration.hold_out_twin must be a scenario id SC-CA##-###"))
    es = cal.get("empirical_status")
    if es is not None:
        if not isinstance(es, dict):
            errors.append(_issue(path, "calibration.empirical_status must be a mapping"))
        else:
            for k in es:
                if k not in _EMPIRICAL_STATUS_KEYS:
                    errors.append(_issue(path, f"empirical_status has unknown key {k!r}"))
            for k in _EMPIRICAL_STATUS_KEYS:
                if not isinstance(es.get(k), bool):
                    errors.append(_issue(path, f"empirical_status.{k} must be a boolean"))
            # Honesty guard: nothing is empirically calibrated until a model panel
            # exists; a scenario MUST NOT claim it without design review first.
            if es.get("empirically_calibrated") and not es.get("design_reviewed"):
                errors.append(_issue(path, "empirical_status: empirically_calibrated "
                                     "cannot be true unless design_reviewed is true"))


def _load_yaml(path: Path, errors: list[dict[str, str]]) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(_issue(path, "missing file"))
        return None
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.append(_issue(path, f"invalid YAML: {exc}"))
        return None


def _report(base: Path, areas: list[dict[str, Any]], errors: list[dict[str, str]], warnings: list[dict[str, str]], assessments: list[dict[str, Any]] | None = None, applicability: list[dict[str, str]] | None = None) -> dict[str, Any]:
    assessments = assessments or []
    applicability = applicability or []
    return {
        "valid": not errors,
        "root": str(base),
        "summary": {
            "areas": len(areas),
            "scenarios": sum(area["scenarios"] for area in areas),
            "valid_scenarios": sum(area["valid_scenarios"] for area in areas),
            "assessments": len(assessments),
        },
        "areas": areas,
        "assessments": assessments,
        "errors": errors,
        "warnings": warnings,
        "declared_non_applicable": applicability,
    }


def _area_code(name: str) -> str | None:
    match = AREA_RE.match(name)
    return f"CA-{match.group(1)}" if match else None


def _expect_equal(actual: Any, expected: str, path: Path, field: str, errors: list[dict[str, str]]) -> None:
    if actual != expected:
        errors.append(_issue(path, f"{field} must be {expected!r}, got {actual!r}"))


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _issue(path: Path, message: str) -> dict[str, str]:
    return {"file": str(path), "message": message}

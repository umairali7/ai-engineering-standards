"""Competency-suite validation for the shipped AIES benchmark corpus."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .constants import DIMENSIONS, RISK_TIERS
from .runner import SCENARIO_REQUIRED, competencies_dir

AREA_RE = re.compile(r"^CA-(\d{2})")
SCENARIO_RE = re.compile(r"^SC-(CA\d{2})-(\d{3})$")


class SuiteValidationError(Exception):
    pass


def validate(root: Path | None = None) -> dict[str, Any]:
    base = root or competencies_dir()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    areas: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}

    if not base.exists():
        errors.append(_issue(base, "competencies directory does not exist"))
        return _report(base, areas, errors, warnings)

    for area_dir in sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith("CA-")):
        area_code = _area_code(area_dir.name)
        if area_code is None:
            warnings.append(_issue(area_dir, "directory is not named with a CA-## prefix"))
            continue
        area_report = _validate_area(area_dir, area_code, seen_ids, errors, warnings)
        areas.append(area_report)

    if not areas:
        errors.append(_issue(base, "no competency area directories found"))

    assessments = _validate_assessments(errors)

    return _report(base, areas, errors, warnings, assessments)


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
        f"  errors   : {len(report['errors'])}",
    ]
    for issue in report["errors"][:20]:
        lines.append(f"  error   : {issue['file']}: {issue['message']}")
    if len(report["errors"]) > 20:
        lines.append(f"  error   : ... {len(report['errors']) - 20} more")
    for issue in report["warnings"][:10]:
        lines.append(f"  warning : {issue['file']}: {issue['message']}")
    if len(report["warnings"]) > 10:
        lines.append(f"  warning : ... {len(report['warnings']) - 10} more")
    return "\n".join(lines)


def _validate_area(
    area_dir: Path,
    area_code: str,
    seen_ids: dict[str, str],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
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
    for path in scenario_files:
        scenario = _load_yaml(path, errors)
        if not isinstance(scenario, dict):
            continue
        before = len(errors)
        _validate_scenario(path, scenario, area_code, seen_ids, errors, warnings)
        if len(errors) == before:
            valid_scenarios += 1

    if len(scenario_files) < 10:
        warnings.append(_issue(scenario_dir, "fewer than 10 scenarios; target suites need broad coverage"))

    return {
        "area": area_code,
        "path": str(area_dir),
        "scenarios": len(scenario_files),
        "valid_scenarios": valid_scenarios,
    }


def _validate_scenario(
    path: Path,
    scenario: dict[str, Any],
    area_code: str,
    seen_ids: dict[str, str],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
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
        if path.stem != scenario_id:
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
        missing = [dim for dim in DIMENSIONS if dim not in rubric]
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


def _report(base: Path, areas: list[dict[str, Any]], errors: list[dict[str, str]], warnings: list[dict[str, str]], assessments: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    assessments = assessments or []
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

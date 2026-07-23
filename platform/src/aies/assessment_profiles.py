"""Subject Assessment Profiles and the governed perspective registry."""

from __future__ import annotations

import copy
import re
from collections import Counter
from pathlib import Path

import yaml

from . import constants as C
from . import resources, subjects


PROFILE_SCHEMA = "aies-subject-assessment-profile/v1"
PERSPECTIVE_KIND = "aies-assessment-perspective-registry"
APPLICABILITY_STATES = frozenset({
    "applicable", "not-applicable", "unsupported",
})
PROFILE_STATUSES = frozenset({"draft", "review", "approved"})
EXPECTED_CATEGORIES = (
    "lifecycle", "cross_cutting", "competencies", "engineering_tasks",
    "risk_tiers", "autonomy_levels", "stakeholders", "environments",
    "evidence_modalities", "operating_conditions", "decision_products",
)


class AssessmentProfileError(ValueError):
    pass


def _read_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise AssessmentProfileError(f"cannot load {path.name}: {error}") from error


def load_perspectives() -> dict:
    value = _read_yaml(resources.data_root() / "perspectives-v1.yaml")
    errors = validate_perspectives(value)
    if errors:
        raise AssessmentProfileError("; ".join(errors))
    return copy.deepcopy(value)


def _expected_taxonomy() -> dict[str, dict[str, str]]:
    task_data = _read_yaml(
        resources.data_root() / "task_mappings" / "engineering-tasks-v1.yaml")
    return {
        "lifecycle": C.PHASE_NAMES,
        "cross_cutting": C.DOMAIN_NAMES,
        "competencies": C.COMPETENCY_NAMES,
        "engineering_tasks": {
            item["id"]: item["name"] for item in task_data["tasks"]
        },
        "risk_tiers": C.RISK_TIER_NAMES,
        "autonomy_levels": C.AUTONOMY_LEVEL_NAMES,
    }


def validate_perspectives(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["perspective registry must be a mapping"]
    errors = []
    allowed_root = {
        "kind", "schema", "version", "status", "governed_by",
        "description", "categories",
    }
    extra_root = sorted(set(value) - allowed_root)
    if extra_root:
        errors.append(
            "perspective registry has unsupported fields: "
            + ", ".join(extra_root))
    if value.get("kind") != PERSPECTIVE_KIND:
        errors.append(f"kind must be {PERSPECTIVE_KIND}")
    if value.get("schema") != 1:
        errors.append("perspective registry schema must be 1")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(value.get("version", ""))):
        errors.append("perspective registry version must be semantic version")
    categories = value.get("categories")
    if not isinstance(categories, dict):
        return errors + ["categories must be a mapping"]
    if set(categories) != set(EXPECTED_CATEGORIES):
        errors.append(
            "perspective categories must be exactly: "
            + ", ".join(EXPECTED_CATEGORIES))
    all_ids = set()
    for category_id, category in categories.items():
        where = f"categories.{category_id}"
        if not isinstance(category, dict) or not category.get("title"):
            errors.append(f"{where}.title is required")
            continue
        extra_category = sorted(set(category) - {"title", "items"})
        if extra_category:
            errors.append(
                f"{where} has unsupported fields: "
                + ", ".join(extra_category))
        items = category.get("items")
        if not isinstance(items, list) or not items:
            errors.append(f"{where}.items must be a non-empty list")
            continue
        local_ids = set()
        for index, item in enumerate(items):
            item_where = f"{where}.items[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_where} must be a mapping")
                continue
            extra_item = sorted(set(item) - {"id", "title", "value"})
            if extra_item:
                errors.append(
                    f"{item_where} has unsupported fields: "
                    + ", ".join(extra_item))
            item_id = item.get("id")
            if not item_id or not item.get("title"):
                errors.append(f"{item_where} requires id and title")
                continue
            if item_id in local_ids or item_id in all_ids:
                errors.append(f"duplicate perspective id {item_id}")
            local_ids.add(item_id)
            all_ids.add(item_id)
    for category_id, expected in _expected_taxonomy().items():
        observed = {
            item["id"]: item["title"]
            for item in (categories.get(category_id) or {}).get("items", [])
            if isinstance(item, dict) and item.get("id")
        }
        if observed != expected:
            errors.append(
                f"{category_id} must match the canonical code-title taxonomy")
    return errors


def _validate_cell(value: object, where: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{where} must be a mapping"]
    errors = []
    extra = sorted(set(value) - {"status", "rationale"})
    if extra:
        errors.append(
            f"{where} has unsupported fields: " + ", ".join(extra))
    if value.get("status") not in APPLICABILITY_STATES:
        errors.append(
            f"{where}.status must be applicable, not-applicable, or unsupported")
    if not isinstance(value.get("rationale"), str) or not value["rationale"].strip():
        errors.append(f"{where}.rationale is required")
    return errors


def validate_profile(value: object, perspectives: dict | None = None) -> list[str]:
    if not isinstance(value, dict):
        return ["subject assessment profile must be a mapping"]
    perspectives = perspectives or load_perspectives()
    errors = []
    required = {
        "kind", "schema", "id", "title", "version", "status", "governed_by",
        "subject_kinds", "descriptor_schema", "fingerprint_change_triggers",
        "execution", "instruments", "scoring", "human_review",
        "decision_products", "applicability", "limitations",
    }
    missing = sorted(required - set(value))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    extra = sorted(set(value) - required)
    if extra:
        errors.append("unsupported fields: " + ", ".join(extra))
    if value.get("kind") != "aies-subject-assessment-profile":
        errors.append("kind must be aies-subject-assessment-profile")
    if value.get("schema") != PROFILE_SCHEMA:
        errors.append(f"schema must be {PROFILE_SCHEMA}")
    if not re.fullmatch(r"SAP-\d{2}", str(value.get("id", ""))):
        errors.append("id must be SAP-NN")
    if not value.get("title"):
        errors.append("title is required")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(value.get("version", ""))):
        errors.append("version must be semantic version")
    if value.get("status") not in PROFILE_STATUSES:
        errors.append("status must be draft, review, or approved")
    kinds = value.get("subject_kinds")
    if not isinstance(kinds, list) or not kinds:
        errors.append("subject_kinds must be a non-empty list")
    elif any(kind not in subjects.VALID_KINDS for kind in kinds):
        errors.append("subject_kinds contains an unsupported descriptor kind")
    if value.get("descriptor_schema") != subjects.SUBJECT_SCHEMA:
        errors.append(f"descriptor_schema must be {subjects.SUBJECT_SCHEMA}")
    for field in ("fingerprint_change_triggers", "decision_products",
                  "limitations"):
        if not isinstance(value.get(field), list) or not value[field]:
            errors.append(f"{field} must be a non-empty list")
    execution = value.get("execution")
    if not isinstance(execution, dict):
        errors.append("execution must be a mapping")
    else:
        for field in ("executors", "evidence_adapters"):
            if not isinstance(execution.get(field), list) or not execution[field]:
                errors.append(f"execution.{field} must be a non-empty list")
    applicability = value.get("applicability")
    if not isinstance(applicability, dict):
        return errors + ["applicability must be a mapping"]
    categories = perspectives["categories"]
    if set(applicability) != set(categories):
        errors.append(
            "applicability must declare exactly every perspective category")
    for category_id, rule in applicability.items():
        where = f"applicability.{category_id}"
        if category_id not in categories:
            continue
        if not isinstance(rule, dict):
            errors.append(f"{where} must be a mapping")
            continue
        extra_rule = sorted(set(rule) - {"default", "overrides"})
        if extra_rule:
            errors.append(
                f"{where} has unsupported fields: "
                + ", ".join(extra_rule))
        errors.extend(_validate_cell(rule.get("default"), f"{where}.default"))
        overrides = rule.get("overrides", {})
        if not isinstance(overrides, dict):
            errors.append(f"{where}.overrides must be a mapping")
            continue
        known = {item["id"] for item in categories[category_id]["items"]}
        unknown = sorted(set(overrides) - known)
        if unknown:
            errors.append(
                f"{where}.overrides has unknown ids: " + ", ".join(unknown))
        for item_id, cell in overrides.items():
            errors.extend(_validate_cell(cell, f"{where}.overrides.{item_id}"))
    product_ids = {
        item["id"]
        for item in categories["decision_products"]["items"]
    }
    unknown_products = sorted(
        set(value.get("decision_products") or []) - product_ids)
    if unknown_products:
        errors.append(
            "decision_products has unknown ids: " + ", ".join(unknown_products))
    return errors


def load_profiles() -> list[dict]:
    perspectives = load_perspectives()
    directory = resources.data_root() / "subject_profiles"
    profiles = []
    errors = []
    seen_ids = set()
    seen_kinds = set()
    for path in sorted(directory.glob("*.yaml")):
        value = _read_yaml(path)
        current = validate_profile(value, perspectives)
        errors.extend(f"{path.name}: {error}" for error in current)
        if isinstance(value, dict):
            if value.get("id") in seen_ids:
                errors.append(f"{path.name}: duplicate profile id {value.get('id')}")
            seen_ids.add(value.get("id"))
            for kind in value.get("subject_kinds") or []:
                if kind in seen_kinds:
                    errors.append(
                        f"{path.name}: subject kind {kind} has multiple profiles")
                seen_kinds.add(kind)
            profiles.append(value)
    if not profiles:
        errors.append("no Subject Assessment Profiles were found")
    if errors:
        raise AssessmentProfileError("; ".join(errors))
    return copy.deepcopy(profiles)


def get_profile(reference: str) -> dict:
    needle = reference.casefold()
    matches = [
        profile for profile in load_profiles()
        if profile["id"].casefold() == needle
        or needle in {kind.casefold() for kind in profile["subject_kinds"]}
    ]
    if len(matches) != 1:
        raise AssessmentProfileError(
            f"no unique Subject Assessment Profile for {reference!r}; "
            "run `aies assessment-profile list`")
    return matches[0]


def expand_applicability(profile: dict) -> dict:
    perspectives = load_perspectives()
    expanded = {}
    for category_id, category in perspectives["categories"].items():
        rule = profile["applicability"][category_id]
        overrides = rule.get("overrides") or {}
        expanded[category_id] = {
            "title": category["title"],
            "items": [
                {
                    **copy.deepcopy(item),
                    **copy.deepcopy(overrides.get(item["id"], rule["default"])),
                }
                for item in category["items"]
            ],
        }
    return expanded


def describe(reference: str | None = None) -> dict:
    profiles = load_profiles()
    if reference:
        profiles = [get_profile(reference)]
    return {
        "kind": "aies-subject-assessment-profile-index",
        "schema": "aies-subject-assessment-profile-index/v1",
        "perspective_registry": {
            key: load_perspectives()[key]
            for key in ("kind", "schema", "version", "status", "governed_by")
        },
        "profiles": profiles,
        "claim_boundary": (
            "A profile declares applicability and assessment semantics. It "
            "does not establish that a subject was assessed, passed, "
            "qualified, or authorized."),
    }


def render(result: dict) -> str:
    lines = [
        "AIES SUBJECT ASSESSMENT PROFILES",
        "Profiles define what evidence means for each subject kind.",
        "",
    ]
    for profile in result["profiles"]:
        expanded = expand_applicability(profile)
        counts = {
            state: sum(
                item["status"] == state
                for category in expanded.values()
                for item in category["items"])
            for state in APPLICABILITY_STATES
        }
        lines += [
            f"{profile['id']} — {profile['title']}",
            f"  subject kinds : {', '.join(profile['subject_kinds'])}",
            f"  status/version: {profile['status']} / {profile['version']}",
            f"  applicability : {counts['applicable']} applicable · "
            f"{counts['unsupported']} unsupported · "
            f"{counts['not-applicable']} not applicable",
            f"  executors     : {', '.join(profile['execution']['executors'])}",
            "",
        ]
    lines.append(result["claim_boundary"])
    return "\n".join(lines)


def render_markdown() -> str:
    """Generate the human-readable registry reference from canonical YAML."""
    perspectives = load_perspectives()
    profiles = load_profiles()
    lines = [
        "# AIES Subject Assessment Profiles",
        "",
        "> Generated from `perspectives-v1.yaml` and `subject_profiles/*.yaml`. "
        "Do not edit this file manually.",
        "",
        "A Subject Assessment Profile (SAP) defines how evidence is collected, "
        "interpreted, and bounded for a subject kind. The shared perspective "
        "registry makes missing, unsupported, and not-applicable coverage "
        "visible without treating absence as failure or success.",
        "",
        "## Governed perspective registry",
        "",
        f"Version `{perspectives['version']}` · status "
        f"**{perspectives['status']}** · governed by "
        f"`{perspectives['governed_by']}`.",
        "",
        "| Category | Perspectives | Codes |",
        "|---|---:|---|",
    ]
    for category in perspectives["categories"].values():
        items = category["items"]
        lines.append(
            f"| {category['title']} | {len(items)} | "
            + ", ".join(f"`{item['id']}`" for item in items) + " |")
    lines += ["", "## Implemented profiles", ""]
    for profile in profiles:
        expanded = expand_applicability(profile)
        counts = Counter(
            item["status"]
            for category in expanded.values()
            for item in category["items"])
        lines += [
            f"### `{profile['id']}` — {profile['title']}",
            "",
            f"Version `{profile['version']}` · status **{profile['status']}** "
            f"· governed by `{profile['governed_by']}`.",
            "",
            f"**Subject kinds:** "
            + ", ".join(f"`{kind}`" for kind in profile["subject_kinds"]) + ".",
            "",
            f"**Applicability:** {counts['applicable']} applicable; "
            f"{counts['unsupported']} unsupported; "
            f"{counts['not-applicable']} not applicable.",
            "",
            "**Decision products:** "
            + ", ".join(f"`{item}`" for item in profile["decision_products"])
            + ".",
            "",
            "**Known limitations:**",
            "",
        ]
        lines.extend(f"- {item}" for item in profile["limitations"])
        lines.append("")
    lines += [
        "## Runtime coverage states",
        "",
        "- **assessed** — enough direct evidence met the declared profile target.",
        "- **partially assessed** — direct evidence exists but is below the "
        "declared target.",
        "- **not assessed** — applicable, but no direct evidence was collected.",
        "- **unsupported** — the current executor or adapter has no direct "
        "evidence path.",
        "- **not applicable** — the profile explicitly excludes the perspective "
        "for this subject kind.",
        "",
        "Evidence may be referenced by multiple cells, but the coverage report "
        "also counts unique evidence identities and discloses reuse. Coverage "
        "is evidence availability—not quality, capability, qualification, "
        "deployment readiness, or authorization.",
        "",
        "## CLI",
        "",
        "```text",
        "aies assessment-profile list",
        "aies assessment-profile show SAP-01",
        "aies assessment-profile validate",
        "aies coverage <run-or-audit-id>",
        "```",
        "",
    ]
    return "\n".join(lines)

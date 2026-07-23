"""Decision-led onboarding workflows loaded from versioned data."""

from __future__ import annotations

from copy import deepcopy

import yaml

from . import resources


class StarterError(ValueError):
    pass


REQUIRED_IDS = {
    "understand-deployment", "compare-coding-deployments",
    "audit-repository", "formal-qualification",
}
REQUIRED_FIELDS = (
    "id", "title", "decision", "subject_kind", "workflow", "prerequisites",
    "command_sequence", "expected_artifacts", "does_not_prove", "time_class",
    "cost_class", "evidence_breadth", "next_expansion",
)


def validate(data: object) -> list[str]:
    if not isinstance(data, dict):
        return ["starter registry must be a mapping"]
    errors: list[str] = []
    if data.get("kind") != "aies-decision-starter-registry":
        errors.append("kind must be aies-decision-starter-registry")
    if data.get("schema") != 1:
        errors.append("schema must be 1")
    starters = data.get("starters")
    if not isinstance(starters, list):
        return errors + ["starters must be a list"]
    seen: set[str] = set()
    for index, starter in enumerate(starters):
        where = f"starters[{index}]"
        if not isinstance(starter, dict):
            errors.append(f"{where} must be a mapping")
            continue
        for field in REQUIRED_FIELDS:
            if not starter.get(field):
                errors.append(f"{where}.{field} is required")
        starter_id = starter.get("id")
        if starter_id in seen:
            errors.append(f"duplicate starter id {starter_id}")
        elif starter_id:
            seen.add(starter_id)
    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required starters: " + ", ".join(missing))
    return errors


def load_registry() -> dict:
    path = resources.data_root() / "decision-starters-v1.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise StarterError(f"cannot load decision starters: {exc}") from exc
    errors = validate(data)
    if errors:
        raise StarterError("; ".join(errors))
    return deepcopy(data)


def list_starters() -> dict:
    data = load_registry()
    return {
        "kind": data["kind"],
        "schema": data["schema"],
        "version": data["version"],
        "status": data["status"],
        "starters": [
            {
                "id": item["id"],
                "title": item["title"],
                "decision": item["decision"],
                "subject_kind": item["subject_kind"],
                "workflow": item["workflow"],
            }
            for item in data["starters"]
        ],
    }


def get(starter_id: str) -> dict:
    data = load_registry()
    for item in data["starters"]:
        if item["id"] == starter_id:
            return deepcopy(item)
    raise StarterError(
        f"unknown starter {starter_id!r}; run `aies starter list`")


def render_list(result: dict) -> str:
    lines = [
        "AIES DECISION STARTERS",
        "Choose the decision first; inspect scope and limitations before running.",
        "",
    ]
    for item in result["starters"]:
        lines.extend([
            f"{item['id']} — {item['title']}",
            f"  Decision: {item['decision']}",
            f"  Subject: {item['subject_kind']} · Workflow: {item['workflow']}",
        ])
    lines.extend(["", "Next: aies starter show STARTER_ID"])
    return "\n".join(lines)


def render(starter: dict) -> str:
    lines = [
        f"{starter['id']} — {starter['title']}",
        f"Decision: {starter['decision']}",
        f"Subject kind: {starter['subject_kind']}",
        f"Workflow: {starter['workflow']}",
        f"Time: {starter['time_class']}",
        f"Cost: {starter['cost_class']}",
        f"Evidence breadth: {starter['evidence_breadth']}",
        "",
        "Prerequisites:",
    ]
    lines.extend(f"  - {value}" for value in starter["prerequisites"])
    lines.extend(["", "Workflow sequence:"])
    lines.extend(f"  {index}. {value}" for index, value in enumerate(
        starter["command_sequence"], start=1))
    lines.extend(["", "Expected artifacts:"])
    lines.extend(f"  - {value}" for value in starter["expected_artifacts"])
    lines.extend(["", "This does not prove:"])
    lines.extend(f"  - {value}" for value in starter["does_not_prove"])
    lines.extend(["", "Next expansion:", f"  {starter['next_expansion']}"])
    return "\n".join(lines)

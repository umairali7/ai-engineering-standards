"""Versioned, validated scenario-to-Engineering-Task mappings for ECM."""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml

from . import runner


class TaskMappingError(ValueError):
    pass


def registry_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "task_mappings" / "engineering-tasks-v1.yaml"


def load() -> dict:
    data = yaml.safe_load(registry_path().read_text(encoding="utf-8"))
    problems = validate(data)
    if problems:
        raise TaskMappingError("; ".join(problems))
    return data


def validate(data: dict) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["registry must be a mapping"]
    if data.get("schema") != 2:
        problems.append("task mapping schema must be 2")
    if data.get("status") not in ("draft", "review", "approved"):
        problems.append("task mapping status must be draft | review | approved")
    tasks = data.get("tasks")
    rules = data.get("rules")
    if not isinstance(tasks, list) or not tasks:
        problems.append("tasks must be a non-empty list")
        return problems
    task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    expected = [f"ET-{number:02d}" for number in range(1, 16)]
    if task_ids != expected:
        problems.append("tasks must define ET-01 through ET-15 in order")
    if any(not isinstance(task.get("name"), str) or not task["name"].strip()
           for task in tasks if isinstance(task, dict)):
        problems.append("every task requires a non-empty name")
    if not isinstance(rules, list) or not rules:
        problems.append("rules must be a non-empty list")
        return problems
    areas = set(runner.all_area_codes())
    for rule in rules:
        if not isinstance(rule, dict):
            problems.append("every rule must be a mapping")
            continue
        if rule.get("area") not in areas:
            problems.append(f"unknown rule area {rule.get('area')!r}")
        if not isinstance(rule.get("tasks"), list) or not rule["tasks"]:
            problems.append(f"rule for {rule.get('area')} requires tasks")
        elif any(task not in task_ids for task in rule["tasks"]):
            problems.append(f"rule for {rule.get('area')} references unknown task")
        if not isinstance(rule.get("rationale"), str) or not rule["rationale"].strip():
            problems.append(f"rule for {rule.get('area')} requires rationale")
        review = rule.get("review")
        if not isinstance(review, dict) or review.get("status") not in (
                "pending", "accepted", "rejected"):
            problems.append(
                f"rule for {rule.get('area')} requires review.status pending | accepted | rejected")
        elif review.get("status") == "accepted":
            missing = [field for field in ("reviewer_id", "reviewer_name", "reviewed_at")
                       if not isinstance(review.get(field), str) or not review[field].strip()]
            if missing:
                problems.append(
                    f"accepted rule for {rule.get('area')} lacks review fields: {', '.join(missing)}")
            else:
                reviewer_id = review["reviewer_id"]
                if not all(character.isalnum() or character in "-_"
                           for character in reviewer_id):
                    problems.append(
                        f"accepted rule for {rule.get('area')} has invalid reviewer_id")
                try:
                    reviewed_at = datetime.datetime.fromisoformat(
                        review["reviewed_at"].replace("Z", "+00:00"))
                    if reviewed_at.tzinfo is None:
                        raise ValueError("timezone required")
                except ValueError:
                    problems.append(
                        f"accepted rule for {rule.get('area')} requires a timezone-aware "
                        "ISO-8601 reviewed_at")
    if problems:
        return problems
    for area in runner.all_area_codes():
        _, scenarios, _ = runner.load_area(area)
        for scenario in scenarios:
            if not tasks_for_scenario(scenario, data):
                problems.append(f"unmapped scenario {scenario['id']}")
    return problems


def mapping_rules_for_scenario(scenario: dict, registry: dict | None = None) -> list[dict]:
    """Return the exact mapping rules that govern one scenario.

    Family-specific rules replace an area's default rule. Returning the rule
    records (rather than only task ids) preserves review provenance for ECM
    task admission under ADR-0013.
    """
    registry = registry or load()
    matching = [rule for rule in registry["rules"] if rule["area"] == scenario.get("area")]
    exact = [rule for rule in matching if rule.get("family") == scenario.get("family")]
    return exact or [rule for rule in matching if "family" not in rule]


def tasks_for_scenario(scenario: dict, registry: dict | None = None) -> list[str]:
    selected = mapping_rules_for_scenario(scenario, registry)
    return sorted({task for rule in selected for task in rule["tasks"]})


def task_names(registry: dict | None = None) -> dict[str, str]:
    registry = registry or load()
    return {task["id"]: task["name"] for task in registry["tasks"]}

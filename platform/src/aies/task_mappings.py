"""Versioned, validated scenario-to-Engineering-Task mappings for ECM."""

from __future__ import annotations

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
    if problems:
        return problems
    for area in runner.all_area_codes():
        _, scenarios, _ = runner.load_area(area)
        for scenario in scenarios:
            if not tasks_for_scenario(scenario, data):
                problems.append(f"unmapped scenario {scenario['id']}")
    return problems


def tasks_for_scenario(scenario: dict, registry: dict | None = None) -> list[str]:
    registry = registry or load()
    matching = [rule for rule in registry["rules"] if rule["area"] == scenario.get("area")]
    exact = [rule for rule in matching if rule.get("family") == scenario.get("family")]
    selected = exact or [rule for rule in matching if "family" not in rule]
    return sorted({task for rule in selected for task in rule["tasks"]})


def task_names(registry: dict | None = None) -> dict[str, str]:
    registry = registry or load()
    return {task["id"]: task["name"] for task in registry["tasks"]}

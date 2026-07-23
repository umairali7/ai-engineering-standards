from __future__ import annotations

import json

import yaml


def _entry(deployment_id: str, planning: dict) -> dict:
    return {
        "id": deployment_id,
        "runtime": "mock",
        "model": deployment_id,
        "provenance": {"checksum": "sha256:" + "a" * 64},
        "planning": planning,
    }


def test_planning_uses_only_declared_cost_and_duration():
    from aies import planning

    estimate = planning.estimate(
        {"planned_items": 10},
        subject=_entry("subject", {
            "usd_per_request": 0.01,
            "estimated_seconds_per_request": 2,
        }),
        judge=_entry("judge", {
            "usd_per_request": 0.05,
            "estimated_seconds_per_request": 4,
        }),
        judge_batch_size=4,
        parallel=2,
    )
    assert estimate["status"] == "complete"
    assert estimate["total_cost_usd"] == 0.25
    assert estimate["total_duration_seconds"] == 18
    assert estimate["phases"][0]["requests"] == 10
    assert estimate["phases"][1]["requests"] == 3


def test_planning_keeps_missing_values_explicit():
    from aies import planning

    estimate = planning.estimate(
        {"planned_items": 5},
        subject=_entry("subject", {}),
        judge=None,
        judge_batch_size=8,
        parallel=4,
    )
    assert estimate["status"] == "unavailable"
    assert estimate["total_cost_usd"] is None
    assert estimate["total_duration_seconds"] is None
    assert len(estimate["phases"][0]["missing"]) == 2


def test_registry_validates_planning_declarations():
    from aies import registry

    incomplete = _entry("subject", {
        "estimated_input_tokens_per_item": 100,
        "estimated_output_tokens_per_item": 50,
    })
    errors = registry.validate_entry(incomplete)
    assert any("token-cost planning requires all" in error for error in errors)

    ambiguous = _entry("subject", {
        "estimated_input_tokens_per_item": 100,
        "estimated_output_tokens_per_item": 50,
        "input_usd_per_million_tokens": 1,
        "output_usd_per_million_tokens": 2,
        "usd_per_request": 0.1,
    })
    assert any("not both" in error for error in registry.validate_entry(ambiguous))


def test_evaluate_plan_exposes_structured_declared_estimate(
        tmp_path, monkeypatch, capsys):
    from aies import cli, registry

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    for entry in (
        _entry("subject", {
            "usd_per_request": 0.001,
            "estimated_seconds_per_request": 0.2,
        }),
        _entry("judge", {
            "usd_per_request": 0.01,
            "estimated_seconds_per_request": 0.5,
        }),
    ):
        path = tmp_path / f"{entry['id']}.yaml"
        path.write_text(yaml.safe_dump(entry), encoding="utf-8")
        registry.add(path)

    code = cli.main([
        "evaluate", "subject", "--judge", "judge", "--plan-only",
        "--parallel", "4", "--json",
    ])
    assert code == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["estimate"]["status"] == "complete"
    assert plan["estimate"]["total_cost_usd"] > 0
    assert plan["estimate"]["total_duration_seconds"] > 0
    assert plan["repeats"] == 1

    assert cli.main([
        "evaluate", "subject", "--judge", "judge", "--plan-only",
        "--parallel", "0", "--json",
    ]) == 2
    failure = json.loads(capsys.readouterr().err)
    assert failure["recovery_command"].endswith("--plan-only")

"""Capability profile: --all-areas expands to CA-01…CA-12, and
capability_profile() lays out an aggregated run's per-area results (CL,
decisional, gates, AL at the scoped tier) with human-readable area names."""

import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _register(tmp_path):
    from aies import registry
    entry = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "cand.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def test_all_area_codes_are_the_twelve():
    from aies import runner
    codes = runner.all_area_codes()
    assert codes == [f"CA-{n:02d}" for n in range(1, 13)]


def test_decisional_sample_plan_uses_distinct_rt2_breadth_without_repeats():
    from aies import engine, runner
    areas = runner.all_area_codes()
    plan = engine.plan_qualification("RT2", areas, subject_kind="ai")
    assert len(plan["areas"]) == 12
    assert all(row["decisional_if_scored"] for row in plan["areas"])
    assert all(row["scenarios"] >= row["minimum_items"] for row in plan["areas"])
    assert plan["planned_items"] == 387
    assert plan["unassessed_tasks"] == []

    from collections import Counter
    from aies import task_mappings
    mapping = task_mappings.load()
    direct = Counter()
    for area in areas:
        _, scenarios, _ = runner.load_area(area)
        for scenario in scenarios:
            if scenario["risk_tier"] == "RT2":
                direct.update(task_mappings.tasks_for_scenario(scenario, mapping))
    assert all(direct[f"ET-{number:02d}"] >= 30 for number in range(1, 16))


def test_capability_profile_lays_out_scored_areas(ws, tmp_path):
    from aies import engine, rating, workspace, capabilities

    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT3",
                                     ["CA-04", "CA-05", "CA-07"], repeats=1)
    rid = run["run_id"]
    sheet = json.loads((workspace.run_dir(rid) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(rid, sheet)
    engine.aggregate(rid)

    prof = capabilities.capability_profile(rid)
    assert prof["subject"] == "cand" and prof["risk_tier"] == "RT3"
    areas = {r["area"]: r for r in prof["areas"]}
    assert set(areas) == {"CA-04", "CA-05", "CA-07"}
    # human-readable role name is surfaced (not just the code)
    assert areas["CA-07"]["name"] == "Security & Privacy Engineering"
    # each area carries its own CL + AL-at-tier, and small samples are flagged
    assert areas["CA-05"]["cl"].startswith("CL")
    assert areas["CA-05"]["al_at_rt"] is not None
    assert areas["CA-05"]["decisional"] is False  # distinct RT3 sample < 50


def test_capability_profile_needs_an_aggregated_run(ws, tmp_path):
    from aies import engine, capabilities, compare
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    # not aggregated yet -> clear error, not a crash
    with pytest.raises(compare.CompareError):
        capabilities.capability_profile(run["run_id"])


def test_critical_individual_failure_prevents_strong_engineering_fit():
    from aies import guidance

    matrix = {
        "run_id": "run-test",
        "subject": "subject-test",
        "risk_tier": "RT2",
        "profile": "enterprise",
        "evaluation_scope": {
            "kind": "targeted-area-selection",
            "label": "Targeted competency-area selection",
            "profile_role": "score-weighting profile only",
        },
        "engineering_evaluation": {
            "human_evaluation": {"status": "not-reviewed"},
        },
        "tasks": [{
            "task_id": "ET-01",
            "task": "Requirements Analysis",
            "observed_performance": 3.8,
            "distinct_scenarios": 30,
            "minimum_observations": 30,
            "rating_observations": 30,
            "evidence_assurance": {"status": "provisional"},
            "critical_failures": [{
                "scenario_id": "SC-CA02-004",
                "critical_dimensions": {"EV1": 0},
            }],
        }],
    }

    result = guidance.engineering_fit("run-test", matrix=matrix)
    task = result["tasks"][0]
    assert task["fit"] == "review-recommended"
    assert task["critical_failure_count"] == 1
    assert "prevent a strong-fit label" in task["explanation"]

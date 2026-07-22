"""Corpus-loading cache correctness and invalidation."""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def _scenario(prompt: str) -> dict:
    return {
        "id": "SC-CA05-901", "area": "CA-05", "risk_tier": "RT2",
        "prompt": prompt, "expected_qualities": ["works"],
        "rubric": {"EV1": ["correct"]},
    }


def test_cached_yaml_returns_isolated_values_and_invalidates(tmp_path):
    from aies import runner

    path = tmp_path / "scenario.yaml"
    path.write_text(yaml.safe_dump(_scenario("first")), encoding="utf-8")
    first = runner.load_scenario_documents(path)
    first[0]["prompt"] = "caller mutation"
    assert runner.load_scenario_documents(path)[0]["prompt"] == "first"

    path.write_text(yaml.safe_dump(_scenario("second and longer")), encoding="utf-8")
    assert runner.load_scenario_documents(path)[0]["prompt"] == "second and longer"


def test_suite_version_cache_invalidates_when_instrument_changes(tmp_path):
    from aies import runner

    scenario_dir = tmp_path / "scenarios"
    scenario_dir.mkdir()
    path = scenario_dir / "scenario.yaml"
    path.write_text(yaml.safe_dump(_scenario("first")), encoding="utf-8")
    before = runner._suite_version(tmp_path)
    path.write_text(yaml.safe_dump(_scenario("second and longer")), encoding="utf-8")
    after = runner._suite_version(tmp_path)
    assert before != after

from pathlib import Path

from aies import suites


def test_shipped_competency_suites_are_valid():
    report = suites.validate()

    assert report["valid"], report["errors"]
    assert report["summary"]["areas"] == 12
    assert report["summary"]["scenarios"] >= 132
    assert report["summary"]["valid_scenarios"] == report["summary"]["scenarios"]


def test_validator_rejects_bad_scenario(tmp_path: Path):
    area = tmp_path / "CA-01-example"
    scenarios = area / "scenarios"
    scenarios.mkdir(parents=True)
    (area / "definition.yaml").write_text(
        "area: CA-01\nscenario_families: [example]\n",
        encoding="utf-8",
    )
    (area / "rubric.yaml").write_text(
        "area: CA-01\nsub_criteria:\n"
        "  EV1: [ok]\n  EV2: [ok]\n  EV3: [ok]\n"
        "  EV4: [ok]\n  EV5: [ok]\n  EV6: [ok]\n",
        encoding="utf-8",
    )
    (scenarios / "SC-CA01-001.yaml").write_text(
        "id: SC-CA01-001\n"
        "area: CA-01\n"
        "risk_tier: RT9\n"
        "prompt: ''\n"
        "expected_qualities: []\n"
        "rubric:\n"
        "  EV7: [not a real dimension]\n"
        "weight: 0\n"
        "repeats_min: 0\n",
        encoding="utf-8",
    )

    report = suites.validate(tmp_path)

    messages = "\n".join(error["message"] for error in report["errors"])
    assert not report["valid"]
    assert "risk_tier must be one of" in messages
    assert "prompt must be a non-empty string" in messages
    assert "rubric has unknown dimensions" in messages

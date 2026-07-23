from pathlib import Path

from aies import suites


def test_shipped_competency_suites_are_valid():
    report = suites.validate()

    assert report["valid"], report["errors"]
    assert report["summary"]["areas"] == 12
    assert report["summary"]["scenarios"] == 484
    assert report["summary"]["valid_scenarios"] == report["summary"]["scenarios"]
    assert report["warnings"] == []
    assert report["design_review_ledger"]["accepted"] == 268
    assert report["design_review_ledger"]["stale"] == 0
    assert report["design_review_ledger"]["unknown"] == 0


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


def test_validator_distinguishes_reviewed_non_applicability_from_a_gap(tmp_path: Path):
    area = tmp_path / "CA-01-example"
    scenarios = area / "scenarios"
    scenarios.mkdir(parents=True)
    (area / "definition.yaml").write_text("area: CA-01\nscenario_families: [example]\n", encoding="utf-8")
    (area / "rubric.yaml").write_text("area: CA-01\nsub_criteria: {EV1: [ok], EV2: [ok], EV3: [ok], EV4: [ok], EV5: [ok], EV6: [ok]}\n", encoding="utf-8")
    (scenarios / "SC-CA01-001.yaml").write_text(
        "id: SC-CA01-001\narea: CA-01\nrisk_tier: RT1\nprompt: x\nexpected_qualities: [x]\n"
        "rubric: {EV1: [x], EV2: [x], EV3: [x], EV4: [x], EV6: [x]}\n"
        "rubric_applicability:\n  EV5:\n    status: not_applicable\n    rationale: No resource-efficiency behavior is exercised.\n",
        encoding="utf-8",
    )
    report = suites.validate(tmp_path)
    assert report["valid"], report["errors"]
    assert not any("rubric does not cover" in warning["message"]
                   for warning in report["warnings"])
    assert report["declared_non_applicable"][0]["dimension"] == "EV5"


def test_validator_rejects_invalid_applicability_declarations(tmp_path: Path):
    area = tmp_path / "CA-01-example"
    scenarios = area / "scenarios"
    scenarios.mkdir(parents=True)
    (area / "definition.yaml").write_text("area: CA-01\nscenario_families: [example]\n", encoding="utf-8")
    (area / "rubric.yaml").write_text("area: CA-01\nsub_criteria: {EV1: [ok], EV2: [ok], EV3: [ok], EV4: [ok], EV5: [ok], EV6: [ok]}\n", encoding="utf-8")
    (scenarios / "SC-CA01-001.yaml").write_text(
        "id: SC-CA01-001\narea: CA-01\nrisk_tier: RT1\nprompt: x\nexpected_qualities: [x]\n"
        "rubric: {EV1: [x], EV2: [x], EV3: [x], EV4: [x], EV6: [x]}\n"
        "rubric_applicability:\n  EV5: {status: maybe, rationale: ''}\n  EV1: {status: not_applicable, rationale: conflicts}\n",
        encoding="utf-8",
    )
    report = suites.validate(tmp_path)
    messages = "\n".join(error["message"] for error in report["errors"])
    assert "status must be 'not_applicable'" in messages
    assert "rationale must be a non-empty string" in messages
    assert "conflicts with a covered rubric dimension" in messages

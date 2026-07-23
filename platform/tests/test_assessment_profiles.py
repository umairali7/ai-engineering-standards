"""Governed subject profiles and honest assessment-coverage contracts."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path


def test_perspectives_and_profiles_are_complete_and_canonical():
    from aies import assessment_profiles

    registry = assessment_profiles.load_perspectives()
    profiles = assessment_profiles.load_profiles()
    assert registry["status"] == "approved"
    assert registry["governed_by"] == "ADR-0018"
    assert [profile["id"] for profile in profiles] == ["SAP-01", "SAP-02"]
    for profile in profiles:
        assert profile["status"] == "approved"
        for rule in profile["applicability"].values():
            assert set(rule["default"]) == {"status", "rationale"}
            assert all(
                set(cell) == {"status", "rationale"}
                for cell in (rule.get("overrides") or {}).values())
        expanded = assessment_profiles.expand_applicability(profile)
        assert set(expanded) == set(assessment_profiles.EXPECTED_CATEGORIES)
        for category in expanded.values():
            assert all(cell["rationale"].strip() for cell in category["items"])


def test_profile_validation_rejects_silent_applicability():
    from aies import assessment_profiles

    profile = assessment_profiles.get_profile("SAP-01")
    broken = deepcopy(profile)
    broken["applicability"]["engineering_tasks"]["default"]["rationale"] = ""
    errors = assessment_profiles.validate_profile(broken)
    assert any(
        "engineering_tasks.default.rationale is required" in error
        for error in errors)


def test_coverage_refuses_to_fill_unsupported_cells():
    from aies import assessment_coverage, assessment_profiles, subjects

    profile = assessment_profiles.get_profile("repository")
    subject = subjects.build(
        kind="repository", subject_id="repo-fixture",
        display_name="Repository fixture", version="1",
        environment_fingerprint="sha256:" + "0" * 64)
    matrix = assessment_coverage._skeleton(
        profile, subject, {"kind": "fixture", "id": "fixture"})
    try:
        assessment_coverage._observe(
            matrix, "engineering_tasks", "ET-01",
            status="assessed", evidence_refs=["evt-1"],
            rationale="Synthetic direct evidence.")
    except assessment_coverage.CoverageError as error:
        assert "unsupported cell" in str(error)
    else:
        raise AssertionError("unsupported coverage cell accepted evidence")


def test_profile_and_coverage_contracts_are_machine_readable():
    root = Path(__file__).resolve().parent.parent
    profile = json.loads(
        (root / "contracts" /
         "subject-assessment-profile-v1.schema.json").read_text(
             encoding="utf-8"))
    coverage = json.loads(
        (root / "contracts" /
         "assessment-coverage-v1.schema.json").read_text(encoding="utf-8"))
    assert profile["properties"]["schema"]["const"] == (
        "aies-subject-assessment-profile/v1")
    assert coverage["properties"]["schema"]["const"] == (
        "aies-assessment-coverage/v1")


def test_generated_profile_reference_is_current():
    from aies import assessment_profiles, resources

    root = resources.data_root()
    assert (root / "ASSESSMENT_PROFILES.md").read_text(
        encoding="utf-8") == assessment_profiles.render_markdown()

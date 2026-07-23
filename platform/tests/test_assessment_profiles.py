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


def test_stale_and_conflicting_evidence_remain_visible_blind_spots():
    from aies import (
        assessment_coverage, assessment_profiles, evidence_events, subjects,
    )

    subject = subjects.build(
        "deployment-fixture", kind="ai_deployment",
        display_name="Deployment fixture")
    profile = assessment_profiles.get_profile("SAP-01")
    matrix = assessment_coverage._skeleton(
        profile, subject, {"kind": "fixture", "id": "integrity"})
    event = evidence_events.build(
        event_type="rating", subject_id=subject["id"],
        instrument_id="SC-CA05-001", modality="automated-rating",
        source="fixture-reviewer", source_record_id="rating-1",
        source_digest="sha256:" + "1" * 64,
        adapter_profile="fixture/v1", observed_at="2000-01-01T00:00:00+00:00",
        payload={"scores": {"EV1": 4}})
    assessment_coverage._observe(
        matrix, "engineering_tasks", "ET-04",
        status="assessed", evidence_refs=[event["event_id"]],
        rationale="One old conflicting fixture event.")
    catalog = assessment_coverage._catalog(
        [event], {"SC-CA05-001": {
            "kind": "unresolved-major-rater-divergence",
            "evidence_item_id": "fixture",
            "max_dimension_delta": 3,
        }})
    result = assessment_coverage._finalize(matrix, catalog)
    cell = next(
        item for item in result["categories"]["engineering_tasks"]["cells"]
        if item["id"] == "ET-04")
    assert cell["freshness"]["status"] == "stale"
    assert cell["collection_condition"] == "conflicting"
    assert cell["evidence_confidence"]["level"] == "low"
    assert cell["conflicts"][0]["max_dimension_delta"] == 3
    assert any(
        item["id"] == "ET-04" for item in result["blind_spots"])


def test_collection_gap_is_metadata_and_never_direct_evidence():
    from aies import (
        assessment_coverage, assessment_profiles, evidence_events, subjects,
    )

    subject = subjects.build(
        "repository-fixture", kind="repository",
        display_name="Repository fixture")
    gap = evidence_events.build_collection_gap(
        subject_id=subject["id"], modality="repository-static-analysis",
        source="fixture-adapter", source_record_id="missing-security-tool",
        source_digest="sha256:" + "2" * 64,
        adapter_profile="fixture/v1", category="evidence_modalities",
        item_id="EM-05", condition="tool-not-installed",
        detail="The declared scanner executable was not installed.")
    assert evidence_events.validate(gap) == []
    matrix = assessment_coverage._skeleton(
        assessment_profiles.get_profile("SAP-02"), subject,
        {"kind": "fixture", "id": "gap"})
    assessment_coverage._set_condition(
        matrix, "evidence_modalities", "EM-05",
        gap["payload"]["collection_condition"], gap["payload"]["detail"],
        evidence_ref=gap["event_id"])
    result = assessment_coverage._finalize(
        matrix, assessment_coverage._catalog([gap], {}))
    cell = next(
        item for item in result["categories"]["evidence_modalities"]["cells"]
        if item["id"] == "EM-05")
    assert cell["status"] == "not-assessed"
    assert cell["collection_condition"] == "tool-not-installed"
    assert cell["evidence_count"] == 0
    assert cell["condition_refs"] == [gap["event_id"]]


def test_component_evidence_never_implicitly_fills_parent_coverage():
    from aies import assessment_coverage, evidence_events, subjects

    component = subjects.component_reference(
        "component-model", kind="ai_deployment", role="executes",
        evidence_transfer="reference-only")
    parent = subjects.build(
        "composite-fixture", kind="composite",
        display_name="Composite fixture", components=[component])
    event = evidence_events.build(
        event_type="observation", subject_id="component-model",
        instrument_id="component-check", modality="integrated-system",
        source="fixture", source_record_id="component-1",
        source_digest="sha256:" + "3" * 64,
        adapter_profile="fixture/v1", payload={})
    disclosure = assessment_coverage._component_evidence(parent, [event])
    assert disclosure[0]["observed_event_count"] == 1
    assert disclosure[0]["coverage_use"] == "reference-only"
    assert disclosure[0]["mapped_into_parent_cells"] == 0

"""ECM is a traceable, task-mapped informational view over scored evidence."""

import json
import sys
from pathlib import Path

import yaml
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def _register(tmp_path):
    from aies import registry
    entry = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    path = tmp_path / "cand.yaml"
    path.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(path)


def test_ecm_groups_existing_families_and_labels_small_samples(tmp_path, monkeypatch):
    from aies import ecm, engine, rating, workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT3", ["CA-05"], repeats=1)
    run_id = run["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {f"EV{x}": 3 for x in range(1, 7)}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)

    matrix = ecm.engineering_capability_matrix(run_id)
    assert matrix["status"] == "informational"
    assert matrix["mapping"]["kind"] == "aies-engineering-tasks-v1"
    code_generation = next(task for task in matrix["tasks"] if task["task_id"] == "ET-04")
    assert code_generation["status"] == "observed"
    assert code_generation["decision_semantics"] == "1.0"
    assert code_generation["coverage_percent"] == 0
    assert code_generation["engineering_confidence_percent"] > 0
    assert code_generation["engineering_status"].startswith("observed")
    assert code_generation["qualification_status"] == "observed"
    assert code_generation["task_decision"]["mapping_review_satisfied"] is False
    assert any(task["status"] == "not assessed" for task in matrix["tasks"])
    assert matrix["rows"]
    assert all(row["area"] == "CA-05" for row in matrix["rows"])
    assert all(row["adequacy"] == "non-decisional" for row in matrix["rows"])
    assert all(row["scenario_ids"] for row in matrix["rows"])
    assert "NOT A QUALIFICATION" in ecm.render_markdown(matrix)
    assert "ET-04 Code Generation" in ecm.render_markdown(matrix)


def test_ecm_writer_emits_json_markdown_and_html(tmp_path, monkeypatch):
    from aies import ecm, engine, rating, workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    run_id = run["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {f"EV{x}": 3 for x in range(1, 7)}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)
    matrix = ecm.engineering_capability_matrix(run_id)

    for format, marker in (("json", '"kind"'), ("markdown", "# Engineering"), ("html", "<!doctype html>")):
        path = ecm.write_matrix(matrix, format)
        assert path.exists()
        assert marker in path.read_text(encoding="utf-8")
    html = ecm.render_html(matrix)
    assert "Evidence confidence" in html
    assert "Engineering status" in html
    assert "Scenario-family evidence and traceability" in html
    assert "Task Capability Profile" in ecm.render_capability_summary_html(matrix)


def test_deployment_guidance_is_bounded_to_ecm_evidence(tmp_path, monkeypatch):
    from aies import engine, guidance, rating, workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    sheet = json.loads((workspace.run_dir(run["run_id"]) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {f"EV{x}": 3 for x in range(1, 7)}
    rating.ingest_scores(run["run_id"], sheet)
    engine.aggregate(run["run_id"])
    rendered = guidance.render_markdown(run["run_id"])
    assert "No recommendation — collect evidence or correct scope" in rendered
    assert "Code Generation" in rendered
    assert "no direct mapped evidence" in rendered
    assert "`Use` requires both a demonstrated task" in rendered


def _task_data(count, *, score=4, reviewed=True, double_rated=True, ev3_zero=False):
    items = {}
    for index in range(count):
        scores = {f"EV{x}": score for x in range(1, 7)}
        if ev3_zero and index == 0:
            scores["EV3"] = 0
        items[f"SC-{index:03d}"] = {
            "resolved": True, "qualification_eligible": True,
            "scores": scores,
            "qualified_human_observation_count": 2 if double_rated else 1,
            "max_dimension_delta": 0,
        }
    review = ({"status": "accepted", "reviewer_id": "reviewer-1",
               "reviewer_name": "Mapping Reviewer",
               "reviewed_at": "2026-07-22T00:00:00+00:00"}
              if reviewed else {"status": "pending"})
    return {
        "all_items": dict(items), "decision_items": dict(items),
        "areas": {"CA-05"}, "scenario_ids": set(items),
        "mapping_rules": {"CA-05:*:ET-04": {
            "area": "CA-05", "family": None, "task_id": "ET-04",
            "rationale": "test mapping", "review": review}},
        "instrument_maturity": {
            scenario: {"design_reviewed": True, "empirically_calibrated": False}
            for scenario in items},
    }


@pytest.mark.parametrize("tier,minimum", [
    ("RT1", 20), ("RT2", 30), ("RT3", 50), ("RT4", 100),
])
def test_task_decision_minimums_are_task_scoped(tier, minimum):
    from aies import ecm
    package = {
        "risk_tier": tier, "subject_kind": "ai",
        "areas": {"CA-05": {"decisional": True, "gates_passed": True}},
    }
    demonstrated = ecm._task_decision(
        "ET-04", _task_data(minimum), package, {})
    assert demonstrated["status"] == "demonstrated"
    assert demonstrated["dimensions"]["EV1"]["n"] == minimum

    insufficient = ecm._task_decision(
        "ET-04", _task_data(minimum - 1), package, {})
    assert insufficient["status"] == "insufficient"


def test_task_decision_requires_mapping_review_and_enforces_ev3_hard_fail():
    from aies import ecm
    package = {
        "risk_tier": "RT3", "subject_kind": "ai",
        "areas": {"CA-05": {"decisional": True, "gates_passed": True}},
    }
    pending = ecm._task_decision(
        "ET-04", _task_data(50, reviewed=False), package, {})
    assert pending["status"] == "observed"
    assert pending["mapping_review_satisfied"] is False

    unsafe = ecm._task_decision(
        "ET-04", _task_data(50, ev3_zero=True), package, {})
    assert unsafe["status"] == "gate-failed"
    assert unsafe["ev3_hard_fail"] is True


def test_demonstrated_task_still_requires_matching_active_qualification(
        tmp_path, monkeypatch):
    from copy import deepcopy
    from aies import (compare, ecm, engine, guidance, qualification, raters, rating,
                      task_mappings, workspace)

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    _register(tmp_path)
    reviewed_mapping = deepcopy(task_mappings.load())
    for rule in reviewed_mapping["rules"]:
        rule["review"] = {
            "status": "accepted", "reviewer_id": "mapping-reviewer",
            "reviewer_name": "Mapping Reviewer",
            "reviewed_at": "2026-07-22T00:00:00+00:00",
        }
    monkeypatch.setattr(task_mappings, "load", lambda: reviewed_mapping)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    for rater_id, name in (("human-a", "Human A"), ("human-b", "Human B")):
        raters.register(
            rater_id, name, competency_areas=["CA-05"], risk_tiers=["RT2"],
            qualified_until="2099-01-01T00:00:00+00:00",
            calibration_valid_until="2099-01-01T00:00:00+00:00",
            anchor_library_version="anchors-v1", registered_by="Registry Authority")
        sheet = json.loads((workspace.run_dir(run["run_id"]) / "scoresheet.json")
                           .read_text(encoding="utf-8"))
        sheet["rater"] = {
            "id": rater_id, "name": name, "kind": "human",
            "conflict_declaration": {"declared": True, "has_conflict": False,
                                     "subject_id": "cand"},
        }
        for item in sheet["items"]:
            item["scores"] = {f"EV{x}": 4 for x in range(1, 7)}
        rating.ingest_scores(run["run_id"], sheet)
    engine.aggregate(run["run_id"])
    matrix = ecm.engineering_capability_matrix(run["run_id"])
    code = next(task for task in matrix["tasks"] if task["task_id"] == "ET-04")
    assert code["status"] == "demonstrated"
    assert code["task_decision"]["dimensions"]["EV1"]["n"] == code["distinct_scenarios"]
    comparison = compare.compare_ecm(run["run_id"], run["run_id"])
    code_comparison = next(row for row in comparison["tasks"] if row["task"] == "Code Generation")
    assert code_comparison["comparable"] is True
    assert code_comparison["winner"] is None

    no_record = guidance.decide(run["run_id"])
    code_guidance = next(row for row in no_record["tasks"] if row["task_id"] == "ET-04")
    assert code_guidance["guidance"] == "no-recommendation"

    record = qualification.record_decision(
        run["run_id"], "grant", "Qualification Authority",
        assessor="Human A", assessor_id="human-a", assessor_conflict_free=True,
        peer_reviewer="Human B", peer_reviewer_id="human-b", peer_conflict_free=True,
        role="ROLE-06", phases=["P09"], sponsor="Engineering VP",
        framework_version="AIES-AESQS-CF-01@review-2026-07-22",
        valid_from="2026-07-01T00:00:00+00:00",
        valid_until="2027-06-30T00:00:00+00:00")
    bounded = guidance.decide(
        run["run_id"], qualification_id=record["record_id"],
        requested_role="ROLE-06", requested_phases=["P09"],
        requested_autonomy="AL3")
    code_guidance = next(row for row in bounded["tasks"] if row["task_id"] == "ET-04")
    assert code_guidance["guidance"] == "use"
    assert code_guidance["max_autonomy"] == "AL3"
    assert code_guidance["operational_constraints"]
    assert code_guidance["residual_risks"] == [
        f"0/{code['distinct_scenarios']} task instruments are empirically calibrated"]

    wrong_role = guidance.decide(
        run["run_id"], qualification_id=record["record_id"],
        requested_role="ROLE-08")
    code_guidance = next(row for row in wrong_role["tasks"] if row["task_id"] == "ET-04")
    assert code_guidance["guidance"] == "no-recommendation"

    original_check_current = qualification.check_current
    monkeypatch.setattr(qualification, "check_current", lambda _record_id: {
        "status": "active", "environment_unchanged": False,
        "earned_fingerprint": "sha256:old", "current_fingerprint": "sha256:new",
    })
    drifted = guidance.decide(run["run_id"], qualification_id=record["record_id"])
    code_guidance = next(row for row in drifted["tasks"] if row["task_id"] == "ET-04")
    assert code_guidance["guidance"] == "no-recommendation"
    assert "current deployment fingerprint does not match" in " ".join(code_guidance["reasons"])
    monkeypatch.setattr(qualification, "check_current", original_check_current)

    original_get_record = qualification.get_record
    conditional_record = deepcopy(record)
    conditional_record["status"] = "conditional"
    conditional_record["conditions"] = ["named reviewer approves every change"]
    monkeypatch.setattr(qualification, "get_record", lambda _record_id: conditional_record)
    conditional = guidance.decide(
        run["run_id"], qualification_id=record["record_id"],
        requested_role="ROLE-06", requested_phases=["P09"],
        requested_autonomy="AL2")
    code_guidance = next(row for row in conditional["tasks"] if row["task_id"] == "ET-04")
    assert code_guidance["guidance"] == "use-with-review"

    expired_record = deepcopy(record)
    expired_record["status"] = "expired"
    monkeypatch.setattr(qualification, "get_record", lambda _record_id: expired_record)
    expired = guidance.decide(run["run_id"], qualification_id=record["record_id"])
    code_guidance = next(row for row in expired["tasks"] if row["task_id"] == "ET-04")
    assert code_guidance["guidance"] == "no-recommendation"
    assert "qualification status is expired" in code_guidance["reasons"]
    monkeypatch.setattr(qualification, "get_record", original_get_record)

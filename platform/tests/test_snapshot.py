from __future__ import annotations

import json


def _write_snapshot_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    run = tmp_path / "ws" / "runs" / "run-snapshot"
    run.mkdir(parents=True)
    matrix = {
        "kind": "engineering-capability-matrix",
        "run_id": "run-snapshot",
        "subject": "example-subject",
        "subject_kind": "ai",
        "risk_tier": "RT2",
        "profile": "coder",
        "engineering_evaluation": {
            "human_evaluation": {
                "status": "not-reviewed",
                "optional": True,
                "evaluator": None,
            }
        },
        "tasks": [
            {
                "task_id": "ET-03",
                "task": "API Design",
                "observed_performance": 3.6,
                "engineering_confidence_percent": 50,
                "distinct_scenarios": 15,
                "minimum_observations": 30,
                "task_decision": {"minimum_distinct_scenarios": 30},
            },
            {
                "task_id": "ET-09",
                "task": "Performance Optimization",
                "observed_performance": None,
                "engineering_confidence_percent": 0,
                "distinct_scenarios": 0,
                "minimum_observations": None,
                "task_decision": {"minimum_distinct_scenarios": 30},
            },
        ],
    }
    fit = {
        "kind": "engineering-fit-guidance",
        "run_id": "run-snapshot",
        "subject": "example-subject",
        "risk_tier": "RT2",
        "profile": "coder",
        "human_evaluation": matrix["engineering_evaluation"]["human_evaluation"],
        "tasks": [
            {
                "task_id": "ET-03",
                "fit": "strong-observed-fit",
                "evidence_confidence_percent": 50,
            },
            {
                "task_id": "ET-09",
                "fit": "not-assessed",
                "evidence_confidence_percent": 0,
            },
        ],
    }
    (run / "engineering-capability-matrix.json").write_text(
        json.dumps(matrix), encoding="utf-8")
    (run / "engineering-fit-guidance.json").write_text(
        json.dumps(fit), encoding="utf-8")
    return run


def test_snapshot_keeps_performance_confidence_and_authority_separate(
        tmp_path, monkeypatch):
    from aies import snapshot

    _write_snapshot_artifacts(tmp_path, monkeypatch)
    result = snapshot.build("latest")
    assert result["kind"] == "engineering-decision-snapshot"
    assert result["tasks"][0]["observed_performance_percent"] == 90
    assert result["tasks"][0]["scenario_breadth_percent"] == 50
    assert result["tasks"][0]["evidence_confidence_percent"] == 50
    assert result["human_evaluation"] == "not reviewed (optional)"

    rendered = snapshot.render(result, width=130)
    assert "EVIDENCE → CAPABILITY → ASSURANCE → ENGINEERING DECISIONS" in rendered
    assert "ET-03 — API Design" in rendered
    assert "15/30" in rendered
    assert "90.0%" in rendered
    assert "50.0%" in rendered
    assert "1 not assessed (unknown, not zero)" in rendered
    assert "no qualification, grant, deployment recommendation" in rendered
    assert "Order: performance (descending)" in rendered

    task_order = snapshot.render(
        result, width=130, sort_by="task", descending=False)
    assert task_order.index("ET-03 — API Design") < task_order.index("ET-09 —")


def test_snapshot_has_readable_narrow_and_observed_only_modes(
        tmp_path, monkeypatch):
    from aies import snapshot

    _write_snapshot_artifacts(tmp_path, monkeypatch)
    result = snapshot.build("run-snapshot")
    narrow = snapshot.render(result, width=80)
    assert "capability █████████░ 90.0%" in narrow
    assert "breadth    █████░░░░░ 50.0%" in narrow

    observed = snapshot.render(result, width=80, observed_only=True)
    assert "ET-03 — API Design" in observed
    assert "ET-09 — Performance Optimization" not in observed

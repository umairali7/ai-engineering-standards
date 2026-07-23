from __future__ import annotations

from copy import deepcopy

import pytest


def test_decision_starters_cover_first_adoption_decisions():
    from aies import decision_starters

    result = decision_starters.list_starters()
    assert {item["id"] for item in result["starters"]} == {
        "understand-deployment",
        "compare-coding-deployments",
        "audit-repository",
        "formal-qualification",
    }
    assert {item["subject_kind"] for item in result["starters"]} == {
        "ai-deployment", "repository"}


def test_starter_exposes_sequence_cost_breadth_and_limitations():
    from aies import decision_starters

    starter = decision_starters.get("understand-deployment")
    rendered = decision_starters.render(starter)
    assert "aies evaluate SUBJECT" in rendered
    assert "--plan-only" in rendered
    assert "This does not prove:" in rendered
    assert "Evidence breadth:" in rendered
    assert "Cost:" in rendered


def test_unknown_and_invalid_starter_registry_are_actionable():
    from aies import decision_starters

    with pytest.raises(
            decision_starters.StarterError, match="aies starter list"):
        decision_starters.get("unknown")
    data = decision_starters.load_registry()
    broken = deepcopy(data)
    broken["starters"][0]["does_not_prove"] = []
    assert any(
        "does_not_prove is required" in value
        for value in decision_starters.validate(broken)
    )

"""Engineering task mappings cover the shipped corpus and remain versioned."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_engineering_task_registry_is_valid_and_covers_every_scenario():
    from aies import task_mappings

    registry = task_mappings.load()
    assert registry["id"] == "aies-engineering-tasks-v1"
    assert registry["schema"] == 2
    assert registry["version"] == "2.0.0"
    assert task_mappings.validate(registry) == []
    assert list(task_mappings.task_names(registry)) == [f"ET-{number:02d}" for number in range(1, 16)]
    assert all(rule["review"]["status"] == "pending" for rule in registry["rules"])


def test_accepted_mapping_requires_durable_review_provenance():
    from copy import deepcopy
    from aies import task_mappings

    registry = deepcopy(task_mappings.load())
    registry["rules"][0]["review"] = {"status": "accepted"}
    assert any("lacks review fields" in problem for problem in task_mappings.validate(registry))
    registry["rules"][0]["review"].update({
        "reviewer_id": "mapping-reviewer-1",
        "reviewer_name": "Mapping Reviewer",
        "reviewed_at": "2026-07-22T00:00:00+00:00",
    })
    assert task_mappings.validate(registry) == []

    registry["rules"][0]["review"]["reviewed_at"] = "2026-07-22"
    assert any("timezone-aware" in problem
               for problem in task_mappings.validate(registry))
    registry["rules"][0]["review"]["reviewed_at"] = "2026-07-22T00:00:00+00:00"
    registry["rules"][0]["review"]["reviewer_id"] = "invalid reviewer"
    assert any("invalid reviewer_id" in problem
               for problem in task_mappings.validate(registry))

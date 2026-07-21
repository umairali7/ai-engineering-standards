"""Engineering task mappings cover the shipped corpus and remain versioned."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_engineering_task_registry_is_valid_and_covers_every_scenario():
    from aies import task_mappings

    registry = task_mappings.load()
    assert registry["id"] == "aies-engineering-tasks-v1"
    assert task_mappings.validate(registry) == []
    assert list(task_mappings.task_names(registry)) == [f"ET-{number:02d}" for number in range(1, 16)]

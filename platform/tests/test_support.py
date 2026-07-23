from __future__ import annotations

from copy import deepcopy

import pytest


def test_registry_covers_implemented_and_envisioned_subjects():
    from aies import support

    result = support.describe()
    by_id = {subject["id"]: subject for subject in result["subjects"]}
    assert by_id["ai-deployment"]["status"] == "implemented"
    assert by_id["repository"]["status"] == "implemented"
    assert by_id["mcp-server"]["status"] == "planned"
    assert by_id["ai-agent"]["status"] == "planned"
    assert by_id["rag-system"]["status"] == "planned"
    assert result["counts"] == {
        "implemented": 2, "experimental": 0, "planned": 12}
    assert result["contracts"]["subject_descriptor"] == (
        "aies-subject-descriptor/v1")
    assert len(result["compatibility_fixtures"]) == 7
    assert "not support claims" in result["claim_boundary"]


def test_support_alias_filter_and_unknown_are_explicit():
    from aies import support

    result = support.describe("MCP server")
    assert [subject["id"] for subject in result["subjects"]] == ["mcp-server"]
    with pytest.raises(support.SupportError, match="aies support"):
        support.describe("mystery-machine")


def test_registry_validation_rejects_unsupported_implemented_claim():
    from aies import support

    data = support.load_registry()
    broken = deepcopy(data)
    repository = next(
        item for item in broken["subjects"] if item["id"] == "repository")
    repository["entry_points"] = []
    assert any(
        "entry_points is required" in error
        for error in support.validate(broken)
    )


def test_generated_subject_support_document_is_current():
    from aies import resources, support

    root = resources.data_root()
    assert (root / "SUBJECT_SUPPORT.md").read_text(
        encoding="utf-8") == support.render_markdown()

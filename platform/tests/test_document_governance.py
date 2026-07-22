"""Executable governance checks for stable document identity."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_document_ids.py"
SPEC = importlib.util.spec_from_file_location("check_document_ids", SCRIPT)
check_document_ids = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check_document_ids)


def _doc(root: Path, name: str, doc_id: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Document\n\n| | |\n|---|---|\n| **Document ID** | {doc_id} |\n",
        encoding="utf-8",
    )


def test_duplicate_document_ids_are_reported(tmp_path):
    _doc(tmp_path, "one.md", "AIES-DOC-99")
    _doc(tmp_path, "nested/two.md", "AIES-DOC-99")
    assert check_document_ids.duplicate_declarations(tmp_path) == {
        "AIES-DOC-99": ["nested/two.md", "one.md"],
    }
    assert check_document_ids.main([str(tmp_path)]) == 1


def test_templates_and_citations_are_not_declarations(tmp_path):
    _doc(tmp_path, "one.md", "AIES-DOC-99")
    (tmp_path / "template.md").write_text(
        "| **Document ID** | <ID per AIES-STD-02> |\n"
        "See AIES-DOC-99 for the governed document.\n",
        encoding="utf-8",
    )
    assert check_document_ids.main([str(tmp_path)]) == 0


def test_repository_document_ids_are_unique():
    root = Path(__file__).resolve().parents[2]
    assert check_document_ids.duplicate_declarations(root) == {}

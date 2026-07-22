"""Workspace storage classes enforce source-record and view boundaries."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_artifact_storage_classes_and_writers(tmp_path, monkeypatch):
    from aies import workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    rdir = workspace.run_dir("run-test")
    response = rdir / "responses" / "item.json"
    report = rdir / "report.json"
    diagnostics = rdir / "grounding-diagnostics.json"
    evidence = rdir / "evidence-package.json"
    manifest = rdir / "manifest.json"
    qualification = workspace.ensure() / "qualifications" / "QUAL-2026-001.json"

    assert workspace.artifact_class(response) == "append-only-record"
    assert workspace.artifact_class(qualification) == "append-only-record"
    assert workspace.artifact_class(report) == "regenerable-view"
    assert workspace.artifact_class(diagnostics) == "regenerable-view"
    assert workspace.artifact_class(evidence) == "derived-canonical-snapshot"
    assert workspace.artifact_class(manifest) == "mutable-working-state"

    workspace.write_json(response, {"value": 1})
    with pytest.raises(PermissionError, match="append-only"):
        workspace.write_json(response, {"value": 2}, overwrite=True)
    with pytest.raises(ValueError, match="not classified"):
        workspace.write_view(response, "replacement")

    workspace.write_view(report, "first")
    workspace.write_view(report, "second")
    assert report.read_text(encoding="utf-8") == "second"

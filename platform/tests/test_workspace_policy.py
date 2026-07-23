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


def test_workspace_debris_diagnostic_is_read_only_and_evidence_aware(tmp_path):
    from aies import workspace

    root = tmp_path / "ws"
    (root / "runs" / "run-real" / "responses").mkdir(parents=True)
    evidence = root / "runs" / "run-real" / "responses" / "item.json"
    evidence.write_text("{}", encoding="utf-8")
    misplaced = root / "runs" / "report.html"
    misplaced.write_text("view", encoding="utf-8")
    metadata = root / ".DS_Store"
    metadata.write_text("finder", encoding="utf-8")
    cache = root / "runs" / "__pycache__"
    cache.mkdir()

    report = workspace.diagnose_debris(root)
    paths = {item["path"] for item in report["findings"]}
    assert report["count"] == 3 and not report["clean"] and report["advisory"]
    assert paths == {".DS_Store", "runs/__pycache__", "runs/report.html"}
    assert evidence.exists() and misplaced.exists() and metadata.exists() and cache.exists()

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
    report_view = rdir / "report-view.json"
    diagnostics = rdir / "grounding-diagnostics.json"
    coverage = rdir / "assessment-coverage.json"
    evidence = rdir / "evidence-package.json"
    manifest = rdir / "manifest.json"
    qualification = workspace.ensure() / "qualifications" / "QUAL-2026-001.json"

    assert workspace.artifact_class(response) == "append-only-record"
    assert workspace.artifact_class(qualification) == "append-only-record"
    assert workspace.artifact_class(report) == "regenerable-view"
    assert workspace.artifact_class(report_view) == "regenerable-view"
    assert workspace.artifact_class(diagnostics) == "regenerable-view"
    assert workspace.artifact_class(coverage) == "regenerable-view"
    assert workspace.artifact_class(evidence) == "derived-canonical-snapshot"
    assert workspace.artifact_class(manifest) == "mutable-working-state"

    workspace.write_json(response, {"value": 1})
    with pytest.raises(PermissionError, match="append-only"):
        workspace.write_json(response, {"value": 2}, overwrite=True)
    comparison = (
        workspace.root() / "comparisons" / "comparison-fixture.json")
    workspace.write_json(comparison, {"kind": "comparison"})
    assert workspace.artifact_class(comparison) == "append-only-record"
    with pytest.raises(PermissionError, match="append-only"):
        workspace.write_json(
            comparison, {"kind": "replacement"}, overwrite=True)
    with pytest.raises(ValueError, match="not classified"):
        workspace.write_view(response, "replacement")

    workspace.write_view(report, "first")
    workspace.write_view(report, "second")
    assert report.read_text(encoding="utf-8") == "second"


def test_external_run_identifiers_cannot_be_paths():
    from aies import workspace

    for valid in ("run-1", "run_2", "run.3"):
        assert workspace.validate_run_id(valid) == valid
    for unsafe in ("..", ".", "../run", r"..\run", "/run", "run/name", ""):
        with pytest.raises(ValueError):
            workspace.validate_run_id(unsafe)


def test_nested_copied_run_package_is_readable_without_being_moved(
        tmp_path, monkeypatch):
    from aies import workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    run_id = "run-copied"
    wrapper = workspace.runs_dir() / run_id
    package = wrapper / run_id
    package.mkdir(parents=True)
    manifest = package / "manifest.json"
    manifest.write_text(
        '{"run_id":"run-copied","model":{"registry_id":"copied-model"},'
        '"profile":"coder","risk_tier":"RT2","areas":[]}',
        encoding="utf-8")
    (package / "evidence-package.json").write_text("{}", encoding="utf-8")

    assert workspace.run_dir(run_id) == package
    assert manifest.is_file()
    diagnostic = workspace.diagnose_debris()
    finding = next(
        item for item in diagnostic["findings"]
        if item["category"] == "nested-run-package")
    assert finding["path"] == f"runs/{run_id}"
    assert "evidence-bearing" in finding["recoverability"]
    from aies import compare
    listed = compare.list_runs()
    assert listed[0]["run_id"] == run_id
    assert listed[0]["aggregated"] is True


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
    nested = root / "runs" / "run-copied" / "run-copied"
    nested.mkdir(parents=True)
    (nested / "manifest.json").write_text("{}", encoding="utf-8")

    report = workspace.diagnose_debris(root)
    paths = {item["path"] for item in report["findings"]}
    assert report["count"] == 4 and not report["clean"] and report["advisory"]
    assert paths == {
        ".DS_Store", "runs/__pycache__", "runs/report.html",
        "runs/run-copied",
    }
    nested_finding = next(
        item for item in report["findings"]
        if item["category"] == "nested-run-package")
    assert "evidence-bearing" in nested_finding["recoverability"]
    assert evidence.exists() and misplaced.exists() and metadata.exists() and cache.exists()

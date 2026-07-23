from __future__ import annotations

import json
import time
from pathlib import Path


def _write(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    _write(root, "pyproject.toml", """
[project]
name = "sample"
dependencies = ["requests>=2", "pydantic==2.9.0"]
[tool.pytest.ini_options]
testpaths = ["tests"]
""")
    _write(root, "uv.lock", "# retained lock\n")
    _write(root, "src/core.py", """
import service

def calculate(value):
    if value:
        return service.transform(value)
    return 0
""")
    _write(root, "src/service.py", """
import core

def transform(value):
    return value + 1
""")
    _write(root, "tests/test_core.py", """
from hypothesis import given

def test_calculate():
    assert True
""")
    _write(root, "coverage.json", json.dumps({
        "totals": {"percent_covered": 84.5}}))
    _write(root, "junit-results.xml",
           '<testsuite tests="3" failures="1" errors="0" skipped="0"/>')
    _write(root, "security.sarif", json.dumps({
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "ExampleScan", "version": "1.0"}},
            "results": [{"level": "error", "message": {"text": "finding"}}],
        }],
    }))
    _write(root, "ruff-results.json", json.dumps([{
        "code": "F401",
        "filename": "src/core.py",
        "location": {"row": 1, "column": 1},
        "message": "unused import",
    }]))
    _write(root, "cyclonedx-sbom.json", json.dumps({
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "components": [{"type": "library", "name": "requests"}],
        "vulnerabilities": [{
            "id": "CVE-fixture",
            "ratings": [{"severity": "high"}],
        }],
    }))
    _write(root, ".github/dependabot.yml", "version: 2\n")
    _write(root, "SECURITY.md", "# Reporting\n")
    _write(root, "aies-repository-analysis.yaml", """
layers:
  core:
    include: ["src/core.py"]
    may_depend_on: []
  service:
    include: ["src/service.py"]
    may_depend_on: []
""")
    return root


def test_repository_analysis_covers_all_engineering_perspectives(
        tmp_path, monkeypatch):
    from aies import audit

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    result = audit.run_audit(
        _repository(tmp_path), record=False, engineering_analysis=True)
    analysis = result["engineering_analysis"]
    assert analysis["schema"] == "aies-repository-analysis/v1"
    assert set(analysis["perspectives"]) == {
        "architecture", "code_quality", "correctness_assurance",
        "security", "dependencies",
    }
    descriptor = analysis["subject"]
    assert descriptor["kind"] == "repository"
    assert descriptor["environment_fingerprint"].startswith("sha256:")
    repository = descriptor["extensions"]["repository"]
    assert repository["analysis_scope"]["scope_digest"].startswith("sha256:")
    assert repository["languages"][0]["language"] == "Python"
    assert repository["dependency_state_digest"].startswith("sha256:")
    assert result["event_replay"]["events_replayed"] == result["n_checks"] + 5
    assert all(event["subject_id"] == descriptor["id"]
               for event in result["events"])


def test_retained_tool_results_do_not_become_correctness_or_security_pass(
        tmp_path, monkeypatch):
    from aies import audit

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    analysis = audit.run_audit(
        _repository(tmp_path), record=False,
        engineering_analysis=True)["engineering_analysis"]
    correctness = analysis["perspectives"]["correctness_assurance"]
    assert correctness["metrics"]["tests_reported"] == 3
    assert correctness["metrics"]["test_failures_or_errors"] == 1
    assert any(finding["id"] == "CORRECTNESS-003"
               for finding in correctness["findings"])
    assert correctness["evidence"]["coverage"][0]["line_percent"] == 84.5
    security = analysis["perspectives"]["security"]
    assert security["metrics"]["sarif_error_findings"] == 1
    assert any(finding["id"] == "SECURITY-003"
               for finding in security["findings"])
    quality = analysis["perspectives"]["code_quality"]
    assert quality["metrics"]["structured_quality_result_artifacts"] == 1
    assert quality["metrics"]["retained_quality_errors"] == 1
    assert any(finding["id"] == "QUALITY-TOOL-001"
               for finding in quality["findings"])
    dependencies = analysis["perspectives"]["dependencies"]
    assert dependencies["metrics"]["structured_sbom_artifacts"] == 1
    assert dependencies["metrics"]["sbom_components"] == 1
    assert dependencies["metrics"]["sbom_high_critical_vulnerabilities"] == 1
    assert any(finding["id"] == "DEP-004"
               for finding in dependencies["findings"])
    assert "does not execute code" in analysis["claim_boundary"]


def test_architecture_and_dependency_findings_are_traceable(
        tmp_path, monkeypatch):
    from aies import audit

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    analysis = audit.run_audit(
        _repository(tmp_path), record=False,
        engineering_analysis=True)["engineering_analysis"]
    architecture = analysis["perspectives"]["architecture"]
    assert architecture["metrics"]["dependency_cycles"] == 1
    assert architecture["metrics"]["declared_layers"] == 2
    assert architecture["metrics"]["layer_violations"] == 2
    assert all(finding["artifacts"] for finding in architecture["findings"])
    dependencies = analysis["perspectives"]["dependencies"]
    assert dependencies["metrics"]["direct_dependencies_parsed"] == 2
    assert dependencies["metrics"]["unpinned_direct_declarations"] == 1
    assert any(item["id"] == "DEP-003" for item in dependencies["findings"])


def test_remediation_is_prioritized_evidence_linked_and_reassessable(
        tmp_path, monkeypatch):
    from aies import audit

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    analysis = audit.run_audit(
        _repository(tmp_path), record=False,
        engineering_analysis=True)["engineering_analysis"]
    plan = analysis["remediation_plan"]
    assert plan
    assert [item["priority"] for item in plan] == sorted(
        item["priority"] for item in plan)
    for item in plan:
        assert item["id"].startswith("REM-")
        assert item["acceptance_signal"]
        assert item["owner_authority"]
        assert item["reassessment_trigger"]
        assert item["reassessment_command"].startswith("aies audit ")


def test_repository_executor_records_subject_execution_and_analysis(
        tmp_path, monkeypatch):
    from aies import executors, workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    executor = executors.RepositoryAuditExecutor()
    result = executor.execute(executors.RepositoryAuditRequest(
        _repository(tmp_path), record=True))
    assert result["execution"]["executor_id"] == (
        "deterministic-repository-audit")
    stored = workspace.read_json(
        workspace.root() / "audits" / f"{result['audit_id']}.json")
    assert stored["subject"] == result["subject"]
    assert stored["execution"] == result["execution"]
    assert stored["engineering_analysis"]["schema"] == (
        "aies-repository-analysis/v1")


def test_analysis_runtime_is_bounded_for_medium_fixture(
        tmp_path, monkeypatch):
    from aies import audit

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    root = tmp_path / "medium"
    for index in range(250):
        _write(
            root, f"src/module_{index}.py",
            f"def value_{index}(x):\n    return x + {index}\n")
    started = time.perf_counter()
    result = audit.run_audit(
        root, record=False, engineering_analysis=True)
    elapsed = time.perf_counter() - started
    assert result["engineering_analysis"]["snapshot"]["files_hashed"] == 250
    assert elapsed < 10, f"medium deterministic analysis took {elapsed:.2f}s"


def test_repository_bundle_contains_linked_markdown_json_and_html(
        tmp_path, monkeypatch):
    from aies import audit

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    result = audit.run_audit(
        _repository(tmp_path), record=False, engineering_analysis=True)
    result["audit_id"] = "audit-fixture"
    paths = audit.write_bundle(result, tmp_path / "bundle")
    assert set(paths) == {
        "json", "markdown", "html",
        "coverage_markdown", "coverage_json", "coverage_html", "bundle"}
    assert "Repository Engineering Analysis" in Path(
        paths["markdown"]).read_text(encoding="utf-8")
    html = Path(paths["html"]).read_text(encoding="utf-8")
    assert "Engineering perspectives" in html
    assert "Informational evidence only" in html
    bundle = json.loads(Path(paths["bundle"]).read_text(encoding="utf-8"))
    assert bundle["audit_id"] == "audit-fixture"
    assert bundle["artifacts"]["html"] == "repository-assessment.html"
    coverage = json.loads(
        Path(paths["coverage_json"]).read_text(encoding="utf-8"))
    assert coverage["schema"] == "aies-assessment-coverage/v1"
    assert coverage["profile"]["id"] == "SAP-02"
    assert coverage["summary"]["not-assessed"] > 0
    assert coverage["claim_boundary"].startswith("Coverage describes")


def test_repository_assessments_compare_without_fake_winner(
        tmp_path, monkeypatch):
    from aies import compare, executors

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    repository = _repository(tmp_path)
    executor = executors.RepositoryAuditExecutor()
    before = executor.execute(executors.RepositoryAuditRequest(repository))
    _write(
        repository, "junit-results.xml",
        '<testsuite tests="3" failures="0" errors="0" skipped="0"/>')
    after = executor.execute(executors.RepositoryAuditRequest(repository))
    result = compare.compare_repositories(
        [before["audit_id"], after["audit_id"]], sort_by="spread")
    assert result["compatible"]
    assert result["same_subject_over_time"]
    failure_row = next(
        row for row in result["metrics"]
        if row["metric"] == "test_failures_or_errors")
    assert failure_row["values"] == [1, 0]
    assert failure_row["deltas_from_a"] == [0, -1]
    assert len(failure_row["evidence_confidence_percent"]) == 2
    assert failure_row["minimum_evidence_confidence_percent"] >= 0
    assert "winner" not in result
    rendered = compare.render_repository_comparison(result)
    assert "NO COMPOSITE SCORE OR WINNER" in rendered
    assert "Test failures or errors" in rendered
    assert "Protocol compatibility" in rendered
    maximum = compare.compare_repositories([before["audit_id"]] * 5)
    assert len(maximum["subjects"]) == 5
    assert maximum["layout"] == "matrix"
    assert maximum["reference_policy"]["maximum"] == 5


def test_repository_contracts_are_versioned_machine_readable_documents():
    contracts = Path(__file__).resolve().parent.parent / "contracts"
    analysis = json.loads(
        (contracts / "repository-analysis-v1.schema.json").read_text(
            encoding="utf-8"))
    assessment = json.loads(
        (contracts / "repository-assessment-v1.schema.json").read_text(
            encoding="utf-8"))
    comparison = json.loads(
        (contracts / "comparison-report-v2.schema.json").read_text(
            encoding="utf-8"))
    assert analysis["$schema"].endswith("draft/2020-12/schema")
    assert assessment["$schema"].endswith("draft/2020-12/schema")
    assert analysis["properties"]["schema"]["const"] == (
        "aies-repository-analysis/v1")
    assert assessment["properties"]["schema"]["const"] == (
        "aies-repository-assessment/v1")
    assert "engineering_analysis" in assessment["required"]
    assert comparison["properties"]["reference_policy"]["properties"][
        "received"]["maximum"] == 5
    packaging = (
        Path(__file__).resolve().parent.parent / "pyproject.toml"
    ).read_text(encoding="utf-8")
    assert '"tomli>=2.0; python_version < \'3.11\'"' in packaging


def test_audit_cli_defaults_to_engineering_analysis_and_can_opt_out(
        tmp_path, monkeypatch, capsys):
    from aies import cli

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    repository = _repository(tmp_path)
    assert cli.main([
        "audit", str(repository), "--format", "json",
    ]) == 0
    complete = json.loads(capsys.readouterr().out)
    assert complete["schema"] == "aies-repository-assessment/v1"
    assert complete["engineering_analysis"]["schema"] == (
        "aies-repository-analysis/v1")

    assert cli.main([
        "audit", str(repository), "--format", "json", "--conformance-only",
    ]) == 0
    conformance = json.loads(capsys.readouterr().out)
    assert conformance["engineering_analysis"] is None
    assert conformance["schema"] == "aies-repository-assessment/v1"

from argparse import Namespace
import json
from pathlib import Path

import yaml

from aies import ci_integration, cli


ROOT = Path(__file__).resolve().parents[2]
CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"
SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"
UPLOAD_ARTIFACT_SHA = "ea165f8d65b6e75b540449e92b4886f43607fa02"


def _empty_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "Repository With Spaces"
    repo.mkdir()
    (repo / "README.md").write_text("# Example\n", encoding="utf-8")
    return repo


def test_advisory_ci_retains_gaps_without_failing(tmp_path):
    repo = _empty_repo(tmp_path)
    package = ci_integration.build_repository_package(
        repo, risk_tier="RT2", enforce=False)
    paths = ci_integration.write_repository_package(
        package, tmp_path / "CI Evidence")

    assert package["policy"]["mode"] == "advisory"
    assert package["policy"]["exit_code"] == 0
    assert package["policy"]["failures"]
    assert {item["level"] for item in package["annotations"]} <= {
        "notice", "warning"}
    assert all(Path(path).is_file() for key, path in paths.items()
               if key != "directory")
    markdown = Path(paths["markdown"]).read_text(encoding="utf-8")
    assert "Advisory evidence — no CI gate" in markdown
    assert "intentionally non-blocking" in markdown


def test_enforcement_is_explicit_and_returns_policy_exit(tmp_path):
    repo = _empty_repo(tmp_path)
    package = ci_integration.build_repository_package(
        repo, risk_tier="RT2", enforce=True)
    assert package["policy"]["mode"] == "enforced"
    assert package["policy"]["passed"] is False
    assert package["policy"]["exit_code"] == 1


def test_ci_cli_writes_json_markdown_and_annotations(tmp_path, capsys):
    repo = _empty_repo(tmp_path)
    out = tmp_path / "Retained Evidence"
    args = Namespace(
        ci_cmd="audit",
        repo=str(repo),
        rt=2,
        enforce=False,
        attest=None,
        out=str(out),
        github_annotations=True,
        json=False,
    )
    assert cli.cmd_ci(args) == 0
    output = capsys.readouterr().out
    assert "mode       : advisory" in output
    assert "CI blocking: no" in output
    assert "::warning title=" in output
    assert (out / "repository-assessment.json").is_file()
    assert json.loads(
        (out / "repository-assessment.json").read_text(encoding="utf-8")
    )["kind"] == "aies-ci-repository-assessment"


def test_reusable_workflow_is_advisory_by_default_and_retains_artifacts():
    workflow_path = ROOT / ".github" / "workflows" / "aies-advisory.yml"
    text = workflow_path.read_text(encoding="utf-8")
    # PyYAML 1.1 treats the key `on` as boolean, so use both parsed structure
    # and explicit source assertions for GitHub's YAML 1.2 surface.
    workflow = yaml.safe_load(text)
    jobs = workflow["jobs"]
    assert "repository-evidence" in jobs
    job = jobs["repository-evidence"]
    assert all(
        "runner.temp" not in str(value)
        for value in job.get("env", {}).values())
    assert "AIES_ARTIFACT_DIR=${RUNNER_TEMP}/aies-ci" in text
    assert '>> "${GITHUB_ENV}"' in text
    assert "default: false" in text
    assert "required: true" in text
    assert f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA} # v4" in text
    assert "if: always()" in text
    assert "--enforce" in text


def test_main_ci_lints_every_workflow_on_workflow_changes():
    text = (
        ROOT / ".github" / "workflows" / "platform-ci.yml"
    ).read_text(encoding="utf-8")
    assert text.count('".github/workflows/*.yml"') == 2
    assert "GitHub Actions workflow contracts" in text
    assert "ACTIONLINT_VERSION" in text
    assert "ACTIONLINT_SHA256" in text
    assert '"${RUNNER_TEMP}/actionlint" -color' in text


def test_security_workflow_scans_history_and_retains_redacted_evidence():
    text = (
        ROOT / ".github" / "workflows" / "security.yml"
    ).read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    jobs = workflow["jobs"]

    assert set(jobs) == {"secret-history", "python-security"}
    assert "permissions:\n  contents: read" in text
    assert f"actions/checkout@{CHECKOUT_SHA} # v4" in text
    assert f"actions/setup-python@{SETUP_PYTHON_SHA} # v5" in text
    assert f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA} # v4" in text
    assert text.count("scripts/run_security_checks.py") == 2
    assert "--history-only" in text
    assert "--python-only" in text
    assert "ruff==0.15.22" in text
    assert "pip-audit==2.10.1" in text
    assert "ruff-security.sarif" in text
    assert "pip-audit.json" in text
    assert text.count("if: always()") == 2


def test_container_is_non_root_and_excludes_secrets_and_runs():
    dockerfile = (ROOT / "platform" / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    assert "USER 10001" in dockerfile
    assert "COPY platform" in dockerfile
    assert "COPY conformance" in dockerfile
    assert "ENTRYPOINT [\"aies\"]" in dockerfile
    assert "mkdir -p /workspace/aies-workspace" in dockerfile
    assert "**/.env" in dockerignore
    assert "**/runs" in dockerignore
    assert "platform/aies-workspace" in dockerignore

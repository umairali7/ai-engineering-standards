from argparse import Namespace
import json
from pathlib import Path

import yaml

from aies import ci_integration, cli


ROOT = Path(__file__).resolve().parents[2]


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
    assert "default: false" in text
    assert "required: true" in text
    assert "actions/upload-artifact@v4" in text
    assert "if: always()" in text
    assert "--enforce" in text


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

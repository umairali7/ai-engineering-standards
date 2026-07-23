from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest
import yaml


def test_init_is_non_destructive_and_writes_no_secret(tmp_path):
    from aies import adoption

    target = tmp_path / "workspace with spaces"
    first = adoption.initialize(target)
    second = adoption.initialize(target)
    assert first["secrets_written"] is False
    assert (target / ".gitignore").is_file()
    assert "assessment evidence" in (target / "README.md").read_text(encoding="utf-8")
    assert second["created"] == []
    assert len(second["existing"]) == 6


def test_custom_starter_manifest_is_valid_and_contains_no_secret(tmp_path):
    from aies import adoption, registry

    path = adoption.starter_deployment(
        tmp_path / "deployment.yaml",
        deployment_id="team-coder",
        model="served-coder",
        base_url="https://models.example.test/v1/",
        api_key_env="TEAM_MODEL_KEY",
        roles=["subject", "judge"],
    )
    entry = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert registry.validate_entry(entry) == []
    assert entry["runtime_config"]["base_url"] == "https://models.example.test/v1"
    assert entry["runtime_config"]["api_key_env"] == "TEAM_MODEL_KEY"
    assert "secret" not in path.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("field,value", [
    ("deployment_id", "Not Valid"),
    ("base_url", "localhost:1234/v1"),
    ("api_key_env", "not-valid"),
])
def test_starter_manifest_rejects_unsafe_or_invalid_inputs(tmp_path, field, value):
    from aies import adoption

    kwargs = {field: value}
    with pytest.raises(adoption.AdoptionError):
        adoption.starter_deployment(tmp_path / "deployment.yaml", **kwargs)


def test_guided_init_selects_and_previews_deployment(
        tmp_path, monkeypatch, capsys):
    from aies import cli

    answers = iter([
        "1", "guided-subject", "served-model",
        "http://127.0.0.1:9999/v1", "GUIDED_API_KEY", "both",
    ])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    target = tmp_path / "guided workspace"
    assert cli.main(["init", str(target), "--guided"]) == 0
    output = capsys.readouterr().out
    entry = yaml.safe_load(
        (target / "deployment.example.yaml").read_text(encoding="utf-8"))
    assert entry["id"] == "guided-subject"
    assert entry["roles"] == ["subject", "judge"]
    assert entry["runtime_config"]["api_key_env"] == "GUIDED_API_KEY"
    assert "environment variable GUIDED_API_KEY; not written" in output


def test_open_and_redacted_export_include_only_anonymized_views(
        tmp_path, monkeypatch):
    from aies import adoption

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    run = tmp_path / "ws" / "runs" / "run-example"
    run.mkdir(parents=True)
    run.joinpath("manifest.json").write_text(json.dumps({
        "run_id": "run-example",
        "subject": {"id": "private-subject", "display_name": "Secret Model"},
        "model": {"registry_id": "private-subject"},
        "environment": {"machine": "private-host",
                        "fingerprint_hash": "sha256:" + "a" * 64},
    }), encoding="utf-8")
    run.joinpath("executive-summary.html").write_text(
        "<html>Secret Model on private-host</html>", encoding="utf-8")
    run.joinpath("responses").mkdir()
    run.joinpath("responses", "secret.json").write_text(
        '{"api_key":"do-not-share"}', encoding="utf-8")

    opened = adoption.open_result("run-example", launch=False)
    assert opened["view"].endswith("executive-summary.html")
    exported = adoption.export_redacted("run-example")
    with zipfile.ZipFile(exported["archive"]) as archive:
        names = set(archive.namelist())
        assert "responses/secret.json" not in names
        assert names == {
            "executive-summary.html", "redacted-export-manifest.json"}
        content = archive.read("executive-summary.html").decode()
        assert "Secret Model" not in content
        assert "private-host" not in content
        assert content.count("[redacted]") == 2


def test_measurement_claims_cover_every_decision_product():
    import yaml

    platform = Path(__file__).resolve().parents[1]
    contract = yaml.safe_load(
        (platform / "measurement-claims-v1.yaml").read_text(encoding="utf-8"))
    assert contract["unit_of_analysis"].startswith("one resolved observation")
    assert set(contract["claims"]) == {
        "engineering_evaluation",
        "engineering_capability_matrix",
        "engineering_fit_guidance",
        "comparison",
        "formal_qualification",
    }
    for claim in contract["claims"].values():
        for field in (
            "subject", "target_population", "sampling_frame", "outcome",
            "aggregation", "uncertainty", "exclusions", "intended_decision",
            "does_not_mean",
        ):
            assert claim[field]

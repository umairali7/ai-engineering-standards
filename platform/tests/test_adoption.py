from __future__ import annotations

import json
import zipfile
from pathlib import Path


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


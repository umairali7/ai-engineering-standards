from __future__ import annotations

import json
from pathlib import Path


def test_empty_overview_is_stable_and_frontend_ready(tmp_path, monkeypatch):
    from aies import overview

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    summary = overview.build()
    assert summary["kind"] == "aies-workspace-overview"
    assert summary["schema_version"] == 1
    assert summary["authority"] == "informational-read-only"
    assert summary["counts"]["runs"] == 0
    assert summary["counts"]["deployments"] == 0
    assert summary["counts"]["assessments"] >= 1
    assert summary["links"]["runs"] == "/runs"
    assert len(summary["limitations"]) >= 3
    assert "AIES workspace overview" in overview.render(summary)


def test_cli_overview_and_deprecated_aliases(
        tmp_path, monkeypatch, capsys):
    from aies import cli

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    assert cli.main(["overview", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "aies-workspace-overview"

    assert cli.main(["profile", "list", "--json"]) == 0
    canonical = capsys.readouterr()
    assert "deprecated" not in canonical.err

    assert cli.main(["profiles", "list", "--json"]) == 0
    legacy = capsys.readouterr()
    assert "deprecated compatibility alias" in legacy.err
    assert "aies profile" in legacy.err

    assert cli.main(["registry", "list", "--json"]) == 0
    legacy = capsys.readouterr()
    assert "aies deployment" in legacy.err

    assert cli.main(["qualifications", "list", "--json"]) == 0
    legacy = capsys.readouterr()
    assert "aies qualification" in legacy.err


def test_canonical_qualification_includes_lifecycle_event():
    from aies.cli import build_parser

    args = build_parser().parse_args([
        "qualification", "event", "QUAL-2026-001",
        "--event", "suspended",
        "--authority", "Authority",
        "--reason", "temporary investigation",
    ])
    assert args.qual_cmd == "event"
    assert args.event == "suspended"
    assert getattr(args, "deprecated_alias", None) is None


def test_cli_contains_no_bespoke_error_prints():
    source = (
        Path(__file__).resolve().parents[1] / "src" / "aies" / "cli.py"
    ).read_text(encoding="utf-8")
    assert 'print(f"error:' not in source
    assert 'print("error:' not in source

from __future__ import annotations

from argparse import Namespace
import shlex


def test_audit_human_output_ends_with_exact_rerun(tmp_path, capsys):
    from aies import cli

    repo = tmp_path / "repo with spaces"
    repo.mkdir()
    (repo / "README.md").write_text("# example", encoding="utf-8")
    code = cli.cmd_audit(Namespace(
        repo=str(repo), attest=None, gate=True, rt=2,
        format="markdown", json=False,
    ))
    output = capsys.readouterr().out
    assert code == 1
    assert "Next: close the ranked required gaps, then rerun:" in output
    assert f"aies audit {shlex.quote(str(repo))} --gate --rt 2" in output


def test_compare_human_output_points_to_compatible_evidence_starter(
        monkeypatch, capsys):
    from aies import cli, compare, comparison_report

    monkeypatch.setattr(
        compare, "compare_ecm_many", lambda *a, **k: {"tasks": []})
    monkeypatch.setattr(
        comparison_report, "render_markdown",
        lambda result: "# comparison")
    code = cli.cmd_compare(Namespace(
        a="run-a", b="run-b", formal_qualification=False,
        area_summary=False, json=False, format="markdown",
    ))
    output = capsys.readouterr().out
    assert code == 0
    assert "aies starter show compare-coding-deployments" in output

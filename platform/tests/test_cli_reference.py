"""The exhaustive CLI guide and shell completion track the live parser."""

from __future__ import annotations

import argparse
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]


def _walk(parser, path=()):
    yield path, parser
    sub = next((a for a in parser._actions
                if isinstance(a, argparse._SubParsersAction)), None)
    if sub:
        for name, child in sorted(sub.choices.items()):
            yield from _walk(child, path + (name,))


def test_every_command_and_parameter_has_explanatory_help():
    from aies.cli import build_parser

    parser = build_parser()
    missing = []
    for path, current in _walk(parser):
        sub = next((a for a in current._actions
                    if isinstance(a, argparse._SubParsersAction)), None)
        if sub:
            missing.extend(
                f"{' '.join(path + (choice.dest,))}: command summary"
                for choice in sub._choices_actions if not choice.help
            )
        missing.extend(
            f"{' '.join(path)}: {action.dest}"
            for action in current._actions
            if not isinstance(action, argparse._SubParsersAction) and not action.help
        )
    assert missing == []

    top = next(a for a in parser._actions
               if isinstance(a, argparse._SubParsersAction))
    qualify_help = top.choices["qualify"].format_help()
    benchmark_help = top.choices["benchmark"].format_help()
    compare_help = top.choices["compare"].format_help()
    assert "workflow guidance:" in qualify_help
    assert "prerequisites :" in qualify_help
    assert "next          :" in qualify_help
    assert "--judge" in benchmark_help
    assert "non-blocking Engineering Evaluation" in benchmark_help
    assert "compatibility alias" in compare_help
    assert "--area-summary" in compare_help


def test_checked_in_cli_reference_matches_live_parser():
    from aies.cli import build_parser
    from aies.cli_reference import render_cli_reference

    expected = render_cli_reference(build_parser())
    actual = (PLATFORM / "CLI_REFERENCE.md").read_text(encoding="utf-8")
    assert actual == expected
    for path, _ in _walk(build_parser()):
        if path:
            assert f"## `aies {' '.join(path)}`" in actual
    assert "## Recommended command sequences" in actual
    assert "### Shell completion and the Tab key" in actual
    assert "## `aies qualify`" in actual
    assert "## `aies suites empirical`" in actual


def test_completion_is_parser_derived_for_supported_shells():
    from aies.cli import build_parser
    from aies.cli_completion import command_specs, render_completion

    parser = build_parser()
    specs = {" ".join(spec.path): spec for spec in command_specs(parser)}
    assert "qualify" in specs[""].candidates
    assert "inspect" in specs["deployment"].subcommands
    assert "--artifact" in specs["deployment verify-artifact"].candidates
    assert ("--format", ("markdown", "json", "html")) in specs["report"].option_choices

    powershell = render_completion(parser, "powershell")
    bash = render_completion(parser, "bash")
    zsh = render_completion(parser, "zsh")
    assert "Register-ArgumentCompleter -Native -CommandName aies" in powershell
    assert "if (( COMP_CWORD > 1 ))" in bash
    assert "complete -F _aies_complete aies" in bash
    assert "bashcompinit" in zsh

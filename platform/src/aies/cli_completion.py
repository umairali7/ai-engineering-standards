"""Dependency-free shell completion generated from the live argparse parser."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class CompletionSpec:
    path: tuple[str, ...]
    subcommands: tuple[str, ...]
    candidates: tuple[str, ...]
    option_choices: tuple[tuple[str, tuple[str, ...]], ...]


def _subparsers(parser: argparse.ArgumentParser):
    return next((a for a in parser._actions
                 if isinstance(a, argparse._SubParsersAction)), None)


def command_specs(parser: argparse.ArgumentParser) -> list[CompletionSpec]:
    """Return completion metadata for every parser node."""
    specs: list[CompletionSpec] = []

    def visit(current: argparse.ArgumentParser, path: tuple[str, ...]) -> None:
        sub = _subparsers(current)
        subcommands = tuple(sorted(sub.choices)) if sub else ()
        candidates = set(subcommands)
        option_choices: list[tuple[str, tuple[str, ...]]] = []
        for action in current._actions:
            if isinstance(action, argparse._SubParsersAction):
                continue
            candidates.update(action.option_strings)
            values = tuple(str(v) for v in (action.choices or ()))
            if action.option_strings and values:
                for option in action.option_strings:
                    option_choices.append((option, values))
            elif not action.option_strings and values:
                candidates.update(values)
        specs.append(CompletionSpec(
            path=path,
            subcommands=subcommands,
            candidates=tuple(sorted(candidates)),
            option_choices=tuple(sorted(option_choices)),
        ))
        if sub:
            for name, child in sorted(sub.choices.items()):
                visit(child, path + (name,))

    visit(parser, ())
    return specs


def _bash_case(specs: list[CompletionSpec]) -> str:
    lines = ['  case "$key" in']
    for spec in specs:
        key = " ".join(spec.path)
        values = " ".join(spec.candidates)
        lines.append(f'    "{key}") candidates="{values}" ;;')
    lines += ["  esac", '  case "$key|$prev" in']
    for spec in specs:
        key = " ".join(spec.path)
        for option, values in spec.option_choices:
            lines.append(f'    "{key}|{option}") candidates="{" ".join(values)}" ;;')
    lines += ["  esac"]
    return "\n".join(lines)


def _bash_script(specs: list[CompletionSpec]) -> str:
    groups = [s for s in specs if len(s.path) == 1 and s.subcommands]
    group_names = "|".join(s.path[0] for s in groups) or "__none__"
    valid_second = {
        s.path[0]: "|".join(s.subcommands) or "__none__" for s in groups
    }
    second_cases = "\n".join(
        f'      {group}) case "$second" in {choices}) key="$first $second" ;; esac ;;'
        for group, choices in valid_second.items()
    )
    cases = _bash_case(specs)
    return f"""# AIES completion for Bash. Generated from the live CLI parser.
_aies_complete() {{
  local cur prev first second key candidates
  cur="${{COMP_WORDS[COMP_CWORD]}}"
  prev=""
  if (( COMP_CWORD > 0 )); then prev="${{COMP_WORDS[COMP_CWORD-1]}}"; fi
  first="${{COMP_WORDS[1]}}"
  second="${{COMP_WORDS[2]}}"
  key=""
  if (( COMP_CWORD > 1 )); then
    key="$first"
    case "$first" in
      {group_names})
        case "$first" in
{second_cases}
        esac
        ;;
    esac
  fi
{cases}
  COMPREPLY=( $(compgen -W "$candidates" -- "$cur") )
}}
complete -F _aies_complete aies
"""


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _powershell_script(specs: list[CompletionSpec]) -> str:
    groups = {s.path[0]: s.subcommands for s in specs
              if len(s.path) == 1 and s.subcommands}
    lines = [
        "# AIES completion for PowerShell. Generated from the live CLI parser.",
        "Register-ArgumentCompleter -Native -CommandName aies -ScriptBlock {",
        "  param($wordToComplete, $commandAst, $cursorPosition)",
        "  $tokens = @($commandAst.CommandElements | ForEach-Object { $_.Extent.Text })",
        "  $first = if ($tokens.Count -gt 1) { $tokens[1] } else { '' }",
        "  $second = if ($tokens.Count -gt 2) { $tokens[2] } else { '' }",
        "  $key = ''",
        "  if ($tokens.Count -gt 2 -or ($tokens.Count -gt 1 -and [string]::IsNullOrEmpty($wordToComplete))) {",
        "    $key = $first",
        "  }",
        "  switch ($key) {",
    ]
    for group, children in sorted(groups.items()):
        child_array = ", ".join(_ps_quote(v) for v in children)
        lines.append(
            f"    {_ps_quote(group)} {{ if (@({child_array}) -contains $second) "
            "{ $key = \"$first $second\" } }"
        )
    lines += [
        "  }",
        "  $prev = if ($tokens.Count -gt 1) { $tokens[$tokens.Count - 2] } else { '' }",
        "  $candidates = @()",
        "  switch (\"$key|$prev\") {",
    ]
    for spec in specs:
        key = " ".join(spec.path)
        for option, values in spec.option_choices:
            array = ", ".join(_ps_quote(v) for v in values)
            lines.append(f"    {_ps_quote(key + '|' + option)} {{ $candidates = @({array}) }}")
    lines += [
        "    default {",
        "      switch ($key) {",
    ]
    for spec in specs:
        key = " ".join(spec.path)
        array = ", ".join(_ps_quote(v) for v in spec.candidates)
        lines.append(f"        {_ps_quote(key)} {{ $candidates = @({array}) }}")
    lines += [
        "      }",
        "    }",
        "  }",
        "  $candidates | Where-Object { $_ -like \"$wordToComplete*\" } | ForEach-Object {",
        "    [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)",
        "  }",
        "}",
        "",
    ]
    return "\n".join(lines)


def render_completion(parser: argparse.ArgumentParser, shell: str) -> str:
    """Render a sourceable completion definition for a supported shell."""
    specs = command_specs(parser)
    if shell == "powershell":
        return _powershell_script(specs)
    if shell == "bash":
        return _bash_script(specs)
    if shell == "zsh":
        return ("# AIES completion for Zsh via its Bash-completion compatibility layer.\n"
                "autoload -Uz bashcompinit\nbashcompinit\n" + _bash_script(specs))
    raise ValueError(f"unsupported shell: {shell}")

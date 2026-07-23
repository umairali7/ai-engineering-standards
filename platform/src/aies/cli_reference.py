"""Generate the exhaustive CLI reference from the live argparse parser."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandGuidance:
    prerequisites: str
    result: str
    next_step: str


_DEFAULT = CommandGuidance(
    "AIES is installed; commands that use workspace state also require a writable AIES workspace.",
    "Prints human-readable output, or JSON where `--json` is supported.",
    "Use the result according to the command purpose; no qualification authority is created.",
)

GUIDANCE: dict[str, CommandGuidance] = {
    "help": CommandGuidance(
        "AIES is installed.",
        "Prints the grouped workflow and complete command tree; it changes no state.",
        "Run `aies <command> --help` or open this CLI Reference for parameter-level detail.",
    ),
    "doctor": CommandGuidance(
        "AIES is installed.",
        "Checks the environment, workspace, TLS/runtime availability, fingerprint, and advisory debris without deleting anything.",
        "Resolve blocking findings, then run `aies discover` or `aies deployment add`.",
    ),
    "discover": CommandGuidance(
        "At least one supported local runtime is installed and reachable.",
        "Discovers served deployments and registers new entries.",
        "Inspect with `aies deployment list` and `aies deployment inspect <id>`.",
    ),
    "runtime": CommandGuidance(
        "AIES is installed; runtime inspection may depend on locally installed runtime software.",
        "Lists or inspects runtime adapters without changing assessment evidence.",
        "Use `aies discover` to register deployments served by available runtimes.",
    ),
    "plugins": CommandGuidance(
        "AIES and any out-of-tree adapter packages are installed.",
        "Lists discovered runtime-adapter plugins and their versions; it changes no state.",
        "Inspect runtimes or register/discover deployments that use the adapters.",
    ),
    "deployment": CommandGuidance(
        "AIES has a writable workspace; mutating subcommands additionally require valid deployment YAML or an existing id as documented.",
        "Lists, inspects, registers, updates, retires, removes, or verifies deployment entries.",
        "Inspect the resulting deployment before using it in evaluation.",
    ),
    "registry": CommandGuidance(
        "AIES has a writable workspace; `add` requires valid deployment YAML.",
        "Provides the legacy candidate-deployment registry surface.",
        "Prefer the canonical `aies deployment` commands for new workflows.",
    ),
    "deployment add": CommandGuidance(
        "A valid deployment YAML exists and its id is not already registered.",
        "Creates a deployment registry entry.",
        "Inspect it, then use it with `benchmark`, `qualify`, `review`, or `corpus review`.",
    ),
    "deployment update": CommandGuidance(
        "The deployment id already exists and a replacement YAML is available.",
        "Updates mutable deployment configuration while preserving the deployment id.",
        "Inspect and re-run affected evaluations; material fingerprint changes trigger reassessment.",
    ),
    "deployment verify-artifact": CommandGuidance(
        "The deployment declares artifact provenance; the local artifact is accessible. Signature verification additionally needs the crypto extra and key/signature inputs.",
        "Verifies checksum and, when supplied, detached signature evidence.",
        "Correct provenance failures before using the artifact for trusted assessment.",
    ),
    "benchmark": CommandGuidance(
        "The target deployment is registered and reachable; suites and the selected profile are valid.",
        "Collects scenario responses and creates a run plus scoresheet; it does not score or aggregate.",
        "Complete the scoresheet and run `aies score`, or use `aies qualify --judge` for an automated one-command evaluation.",
    ),
    "qualify": CommandGuidance(
        "For a new run, the target deployment is registered and reachable. `--judge` requires a reachable reviewer deployment. `--resume` requires scored evidence; `--resume-collection` requires an existing partial run.",
        "Plans and collects evidence; with a judge it also scores, aggregates, and writes the complete evaluation/report bundle.",
        "Inspect `report.html`, run `aies capabilities <run> --ecm`, or begin the separate human qualification workflow.",
    ),
    "score": CommandGuidance(
        "A collected run and completed scoresheet exist; human qualification ratings require registered, in-scope, currently calibrated rater metadata.",
        "Ingests rating observations, resolves eligible evidence items, aggregates when possible, and refreshes reports.",
        "Add the required independent rating, resolve divergences, then generate the final report or proceed to human qualification.",
    ),
    "rater": CommandGuidance(
        "AIES has a writable workspace. Registration requires evidence-backed human qualification, scope, calibration, expiry, and a named registry authority.",
        "Creates or reads durable human-rater qualification/calibration records.",
        "Use registered rater ids in scoresheets, divergence resolution, peer review, and formal qualification.",
    ),
    "resolve": CommandGuidance(
        "The response has a material rater divergence and the named resolver is a registered, qualified, conflict-free human.",
        "Appends an immutable resolved disposition; it does not overwrite the original ratings.",
        "Re-run report/assessment rendering and complete any remaining protocol gaps.",
    ),
    "review": CommandGuidance(
        "A collected run exists. `--model-reviewer` requires a registered reviewer deployment; qualification/calibration flags must be evidence-backed.",
        "Adds advisory model-review observations and refreshes the report bundle; optional human evaluation remains separately visible.",
        "Resolve material findings with humans; advisory review alone cannot support a qualification grant.",
    ),
    "import": CommandGuidance(
        "A collected run exists and the external eval JSON follows the documented EV1–EV6 schema.",
        "Appends parseable external automated-rating observations; invalid items are reported rather than fabricated.",
        "Aggregate/report the run and review the imported evidence limitations.",
    ),
    "export": CommandGuidance(
        "A run with response records exists.",
        "Prints a portable eval-log JSON or writes `eval-log.json` with `--write`.",
        "Use the file with another evaluation tool or round-trip it through `aies import`.",
    ),
    "report": CommandGuidance(
        "The run has been aggregated into an evidence package.",
        "Renders the evidence package; `--write` stores the chosen view beside the run.",
        "Use ECM/guidance for engineering decisions or the governed grant workflow for qualification.",
    ),
    "transcript": CommandGuidance(
        "The run contains response records; scores are shown when available.",
        "Renders task, response, scores, and findings together for review.",
        "Use findings to complete ratings, resolve divergence, or plan remediation.",
    ),
    "index": CommandGuidance(
        "The workspace contains append-only run and qualification records.",
        "Rebuilds the disposable result index from canonical files.",
        "Use `runs`, `dashboard`, or the read-only API to consume the rebuilt index.",
    ),
    "capabilities": CommandGuidance(
        "An aggregated run exists; deployment ids resolve to their latest aggregated run.",
        "Renders per-area capability or, with `--ecm`, the informational Engineering Capability Matrix.",
        "Use `aies guidance` for bounded use advice or `aies compare --ecm` for compatible task comparison.",
    ),
    "guidance": CommandGuidance(
        "An aggregated ECM-capable run exists. A `Use` recommendation requires a current matching human Qualification Record.",
        "Renders bounded Use / Use with human review / No recommendation / Avoid guidance and its constraints.",
        "Apply the recorded human decision and reassess when scope, fingerprint, conditions, or validity changes.",
    ),
    "grant": CommandGuidance(
        "The run is decisional and gate-passing for a grant, required human ratings and divergence dispositions are complete, and assessor/peer identities and conflict declarations satisfy the protocol.",
        "Appends a human qualification decision and immutable Qualification Record; the platform itself does not decide the grant.",
        "Verify the record and monitor conditions, expiry, incidents, drift, and requalification triggers.",
    ),
    "verify": CommandGuidance(
        "A Qualification Record exists.",
        "Checks current validity, lifecycle status, and deployment-fingerprint continuity; it does not mutate the record.",
        "Requalify or append the appropriate governed lifecycle event when verification fails.",
    ),
    "qualification": CommandGuidance(
        "Qualification Records exist for read operations; revoke requires a named human authority and reason.",
        "Reads records/history, verifies current validity, or appends an immutable revocation event.",
        "Monitor expiry and conditions or begin reassessment when the record is no longer current.",
    ),
    "qualifications": CommandGuidance(
        "Qualification Records exist; lifecycle mutations require a named human authority and event-specific evidence.",
        "Lists/shows records or appends immutable qualification lifecycle events.",
        "Verify the resulting current state and retain any required peer/reassessment evidence.",
    ),
    "audit": CommandGuidance(
        "The repository path is readable. Attestation files may support only genuinely non-detectable controls.",
        "Produces ML0–ML4 repository-practice maturity, verified/asserted/gap evidence, and ranked recommendations; `--gate` returns non-zero on required gaps.",
        "Close evidence gaps, rerun the audit, and record any human conformance decision separately.",
    ),
    "compare": CommandGuidance(
        "Both references resolve to aggregated runs with compatible protocols; ECM comparison requires compatible task mappings and evidence semantics.",
        "Reports only valid comparisons and withholds winners for incompatible evidence.",
        "Use the evidence in a scoped human selection decision; do not treat it as a global leaderboard.",
    ),
    "assessment": CommandGuidance(
        "Shipped or supplied assessment YAML is available; result rendering additionally requires an aggregated assessment run.",
        "Lists, shows, validates, or applies declarative assessment composition.",
        "Use a valid assessment with `aies qualify --assessment <name>` or inspect its canonical result.",
    ),
    "profile": CommandGuidance(
        "Shipped or supplied weighting profile YAML is available.",
        "Lists, shows, or validates EV weighting profiles; profiles cannot relax gates.",
        "Use a valid profile with `benchmark` or `qualify`.",
    ),
    "profiles": CommandGuidance(
        "Shipped or supplied weighting profile YAML is available.",
        "Legacy alias for listing, showing, or validating weighting profiles.",
        "Prefer the canonical `aies profile` surface in new workflows.",
    ),
    "runs": CommandGuidance(
        "The workspace contains runs; progress requires a run with durable `progress.json` state.",
        "Lists run history or displays live/durable run progress without mutating evidence.",
        "Open the run transcript/report or resume incomplete work.",
    ),
    "judge": CommandGuidance(
        "Deployments may declare the judge role; history requires prior automated scoring.",
        "Shows the available reviewer pool and evidence-backed judge usage/parse history.",
        "Select a suitable independent judge, then use `qualify --judge` or `review --model-reviewer`.",
    ),
    "assessment result": CommandGuidance(
        "The run was composed under a validated declarative assessment and has aggregated evidence.",
        "Computes the canonical PASS / FAIL / INCONCLUSIVE / INSUFFICIENT EVIDENCE result over mandatory competencies.",
        "Address structured reasons; a PASS still does not create a qualification grant.",
    ),
    "corpus": CommandGuidance(
        "The shipped or selected competencies directory is readable; semantic review additionally requires a reviewer deployment.",
        "Produces advisory corpus health, coverage, duplication, pending-review, or single-instrument critique evidence.",
        "Apply deterministic fixes and human review; corpus tools never approve instruments automatically.",
    ),
    "suites": CommandGuidance(
        "The shipped or selected competencies directory is readable.",
        "Validates suite structure or reports design/empirical calibration maturity.",
        "Fix validation errors before runs; use a preregistered panel for empirical promotion evidence.",
    ),
    "suites empirical": CommandGuidance(
        "For promotion-capable analysis, create a frozen plan before runs, use independent subject ability ranks, bind completed compatible runs, and use a validated shared rating protocol.",
        "Analyzes scenario discrimination, repeatability, and twin robustness; exploratory inputs remain non-promotional.",
        "Have a human review the result and record any instrument-promotion decision.",
    ),
    "completion": CommandGuidance(
        "AIES is installed in the shell environment.",
        "Prints a sourceable completion definition generated from the live parser; it changes nothing until sourced or added to the shell profile.",
        "Source it for the current session or add the documented command to the shell profile, then press Tab after `aies`, subcommands, options, or enumerated values.",
    ),
    "conform": CommandGuidance(
        "Template generation has no evidence prerequisite; checks require a statement, while engine verification requires the golden corpus and optionally a compatible foreign engine command.",
        "Scaffolds/checks conformance claims or verifies decision-engine semantics; it does not issue certification.",
        "Resolve unsupported claims or engine mismatches, then record any human conformance decision separately.",
    ),
    "journey": CommandGuidance(
        "Shipped journey definitions are available.",
        "Lists or shows multi-phase journey definitions without executing them.",
        "Run a journey with `aies qualify <deployment> --journey <id>`.",
    ),
    "dashboard": CommandGuidance(
        "The workspace contains runs or qualification records.",
        "Renders a read-only HTML overview; `--write` persists the view and computes no decisions.",
        "Open the dashboard and follow links to canonical evidence products.",
    ),
    "serve": CommandGuidance(
        "The workspace contains artifacts to expose; choose a safe bind address.",
        "Starts a read-only API that exposes canonical artifacts and computes no new decisions.",
        "Stop the process when finished; use an authenticated reverse proxy before any non-local exposure.",
    ),
}


OPTION_INTERACTIONS: dict[tuple[str, str], str] = {
    ("qualify", "assessment"): "Sets areas and profile; `--rt` and `--repeats` may override the assessment defaults.",
    ("qualify", "area"): "Repeatable. Do not combine conceptually with `--all-areas`; an assessment supplies its own areas.",
    ("qualify", "all_areas"): "Selects all competency areas and replaces the default CA-05 scope.",
    ("qualify", "decisional"): "Requires enough distinct scenarios; repeats never satisfy breadth.",
    ("qualify", "judge"): "Enables automated scoring and complete report generation; automated evidence remains informational for qualification.",
    ("qualify", "resume"): "Uses an existing scored run; the model positional argument is not required.",
    ("qualify", "resume_collection"): "Uses an existing partial run and collects only missing responses; the model positional argument is not required.",
    ("capabilities", "write"): "Meaningful with `--ecm`; writes the ECM artifacts beside the run.",
    ("guidance", "qualification"): "Required before any evidence can become an operational `Use` recommendation.",
    ("audit", "gate"): "Implies RT2 — Moderate when `--rt` is omitted.",
    ("assessment result", "out"): "Applies to HTML output; JSON is selected independently with `--json`.",
    ("review", "model_reviewer"): "Required for live reviewer inference; without it the command assembles from existing review evidence.",
    ("review", "reviewer_qualified"): "A declaration that must be supported by a current CA-06 — Testing, Quality & Evaluation Engineering qualification.",
    ("review", "calibration"): "Bootstrap evidence for an otherwise unqualified reviewer; does not make model ratings human qualification evidence.",
    ("grant", "condition"): "Repeatable and required when `--decision grant-with-conditions` is selected.",
    ("qualifications event", "evidence_run"): "Required for evidence-backed renewal and must identify a decisional, gate-passing reassessment.",
    ("qualifications event", "superseded_by"): "Used with the `superseded` event to identify the replacement record.",
    ("deployment verify-artifact", "signature"): "Use with `--pubkey`; both are needed for detached-signature verification.",
    ("deployment verify-artifact", "pubkey"): "Use with `--signature`; checksum verification remains available without either.",
    ("suites empirical", "create_plan"): "Planning mode; use before subject runs with `--plan-subjects`, owner, areas, tier, repeats, and rating protocol.",
    ("suites empirical", "panel_plan"): "Analysis mode; bind the frozen plan to completed runs with `--planned-runs`.",
}


WORKFLOWS = """## Recommended command sequences

### Initial setup

```text
aies doctor
  → aies discover
  → aies deployment list
  → aies deployment inspect <deployment>
  → aies judge available
```

### Automated engineering evaluation

```text
aies qualify <deployment> --all-areas --rt 2 --judge <judge>
  → aies report <run> --format html --write
  → aies capabilities <run> --ecm --format html --write
  → aies guidance <run> --write
```

Automated ratings can complete an informational Engineering Evaluation. They
cannot by themselves become formal qualification evidence.

### Human-rated qualification

```text
aies benchmark <deployment> ...
  → aies rater register ...                 # each qualified human rater
  → complete scoresheet.json
  → aies score <run>
  → independent second rating as required
  → aies resolve <run> <response> ...       # only for material divergence
  → aies report <run> --write
  → aies grant <run> ...                    # named humans decide
  → aies qualification verify <record>
```

### Repository conformance

```text
aies audit <repo>
  → close ranked evidence gaps
  → aies audit <repo> --gate --rt 2
```

### Empirical scenario calibration

```text
aies suites empirical --create-plan <plan.json> ...
  → run every frozen subject/protocol combination
  → aies suites empirical --panel-plan <plan.json> --planned-runs ...
  → independent human promotion decision
```

### Shell completion and the Tab key

PowerShell, current session:

```powershell
aies completion powershell | Out-String | Invoke-Expression
```

Bash, current session:

```bash
source <(aies completion bash)
```

Zsh, current session:

```zsh
source <(aies completion zsh)
```

After activation, press Tab to complete commands, subcommands, option names,
and enumerated option values. Filesystem paths continue to use the shell's
normal path completion.

Examples:

```text
aies dep<Tab>                         # deployment
aies deployment <Tab>                # add, inspect, list, remove, …
aies report run-123 --format <Tab>    # html, json, markdown
```

### Practical CLI habits

- Use `--json` for scripts and stable machine-readable consumption.
- Use `--write` when you want a regenerable artifact instead of terminal output.
- Use `aies runs progress <run>` from a second terminal; long-running commands
  already show their own live task, elapsed time, throughput, and ETA.
- Treat `--parallel N` as a concurrency ceiling, not a quality setting. Reduce
  it for endpoint rate limits; insufficient API quota is not fixed by reducing it.
- Prefer `--resume-collection` after interrupted collection and `--resume` after
  scoring; neither requires repeating successful inference.
- Run `aies <command> --help` before a consequential or unfamiliar mutation.
"""


def _subparsers(parser: argparse.ArgumentParser):
    return next((a for a in parser._actions
                 if isinstance(a, argparse._SubParsersAction)), None)


def _clean(text: object) -> str:
    return " ".join(str(text or "").split())


def _cell(text: object) -> str:
    return _clean(text).replace("|", "\\|")


def _usage(parser: argparse.ArgumentParser) -> str:
    return _clean(parser.format_usage()).removeprefix("usage: ")


def _label(action: argparse.Action) -> str:
    if action.option_strings:
        return ", ".join(f"`{value}`" for value in action.option_strings)
    metavar = action.metavar if isinstance(action.metavar, str) else action.dest.upper()
    return f"`<{metavar}>`"


def _requirement(action: argparse.Action) -> str:
    if action.option_strings:
        return "required" if action.required else "optional"
    return "optional" if action.nargs in ("?", "*") else "required"


def _constraints(action: argparse.Action) -> str:
    values: list[str] = []
    if action.choices:
        values.append("choices: " + ", ".join(f"`{v}`" for v in action.choices))
    if isinstance(action, argparse._AppendAction):
        values.append("repeatable")
    if action.nargs not in (None, "?", 0, 1):
        values.append(f"values: {action.nargs}")
    default = action.default
    if (not action.required and default not in (None, False, argparse.SUPPRESS)
            and not isinstance(default, (list, dict))):
        values.append(f"default: `{default}`")
    return "; ".join(values) or "—"


def _command_help(parent_sub, name: str, parser: argparse.ArgumentParser) -> str:
    for choice in parent_sub._choices_actions:
        if choice.dest == name:
            return _clean(choice.help)
    return _clean(parser.description)


def _guidance(path: tuple[str, ...]) -> CommandGuidance:
    for size in range(len(path), 0, -1):
        found = GUIDANCE.get(" ".join(path[:size]))
        if found:
            return found
    return _DEFAULT


def apply_guidance(parser: argparse.ArgumentParser) -> None:
    """Add prerequisite/result/next-step hints to every command's `--help`."""
    def visit(current: argparse.ArgumentParser, path: tuple[str, ...]) -> None:
        if path:
            guidance = _guidance(path)
            current.formatter_class = argparse.RawDescriptionHelpFormatter
            current.epilog = (
                "workflow guidance:\n"
                f"  prerequisites : {guidance.prerequisites}\n"
                f"  result        : {guidance.result}\n"
                f"  next          : {guidance.next_step}"
            )
        sub = _subparsers(current)
        if sub:
            for name, child in sub.choices.items():
                visit(child, path + (name,))

    visit(parser, ())


def _render_node(parser: argparse.ArgumentParser, path: tuple[str, ...],
                 summary: str) -> list[str]:
    command = "aies" + ((" " + " ".join(path)) if path else "")
    guidance = _guidance(path)
    out = [f"## `{command}`", "", summary or "Command group.", "",
           f"**Usage:** `{_usage(parser)}`", "",
           f"**Prerequisites:** {guidance.prerequisites}", "",
           f"**Result and side effects:** {guidance.result}", "",
           f"**Recommended next step:** {guidance.next_step}", ""]
    sub = _subparsers(parser)
    if sub:
        out += ["### Subcommands", "",
                "| Subcommand | What it does |",
                "|---|---|"]
        for name, child in sorted(sub.choices.items()):
            out.append(f"| `{name}` | {_cell(_command_help(sub, name, child))} |")
        out.append("")
    actions = [a for a in parser._actions
               if not isinstance(a, argparse._SubParsersAction)]
    if actions:
        out += ["### Parameters and options", "",
                "| Parameter | Requirement | Details | Constraints and interactions |",
                "|---|---|---|---|"]
        key = " ".join(path)
        for action in actions:
            interaction = OPTION_INTERACTIONS.get((key, action.dest), "")
            constraints = _constraints(action)
            if interaction:
                constraints = (constraints + "; " if constraints != "—" else "") + interaction
            out.append(
                f"| {_label(action)} | {_requirement(action)} | "
                f"{_cell(action.help)} | {_cell(constraints)} |"
            )
        out.append("")
    return out


def render_cli_reference(parser: argparse.ArgumentParser) -> str:
    """Render every parser node, argument, option, constraint, and sequence."""
    out = [
        "# AIES CLI Reference",
        "",
        "> Generated from the live `argparse` command surface. Do not edit the",
        "> command tables manually; run `python platform/scripts/generate_cli_reference.py`.",
        "",
        "This is the exhaustive syntax and prerequisite reference. See",
        "[GUIDE.md](GUIDE.md) for explanatory workflows and",
        "[TROUBLESHOOTING.md](TROUBLESHOOTING.md) for failures.",
        "",
        WORKFLOWS.rstrip(),
        "",
        "# Complete command reference",
        "",
    ]

    root_sub = _subparsers(parser)
    if root_sub is None:
        return "\n".join(out) + "\n"

    root_actions = [a for a in parser._actions
                    if not isinstance(a, argparse._SubParsersAction)]
    out += ["## Global options", "",
            "| Option | Details |",
            "|---|---|"]
    for action in root_actions:
        out.append(f"| {_label(action)} | {_cell(action.help)} |")
    out.append("")

    def visit(current: argparse.ArgumentParser, path: tuple[str, ...],
              summary: str) -> None:
        out.extend(_render_node(current, path, summary))
        sub = _subparsers(current)
        if sub:
            for name, child in sorted(sub.choices.items()):
                visit(child, path + (name,), _command_help(sub, name, child))

    for name, child in sorted(root_sub.choices.items()):
        visit(child, (name,), _command_help(root_sub, name, child))
    return "\n".join(out).rstrip() + "\n"

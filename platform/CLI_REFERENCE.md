# AIES CLI Reference

> Generated from the live `argparse` command surface. Do not edit the
> command tables manually; run `python platform/scripts/generate_cli_reference.py`.

This is the exhaustive syntax and prerequisite reference. See
[GUIDE.md](GUIDE.md) for explanatory workflows and
[TROUBLESHOOTING.md](TROUBLESHOOTING.md) for failures.

## Recommended command sequences

### Initial setup

```text
aies init --guided
  → aies doctor
  → aies discover
  → aies deployment list
  → aies deployment inspect <deployment>
  → aies judge available
```

### Automated engineering evaluation

```text
aies qualify <deployment> --all-areas --rt 2 --judge <judge>
  → aies snapshot <run>
  → aies report <run> --format html --write
  → aies capabilities <run> --format html --write
  → aies guidance <run> --write
```

Automated ratings complete the Engineering Evaluation, Engineering Assessment
Result, ECM, diagnostics, and Engineering Fit Guidance. Human evaluation is
optional. Formal qualification is a separate explicit workflow.

### Human-rated qualification

```text
aies qualify <deployment> ... --formal-qualification
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

# Complete command reference

## Global options

| Option | Details |
|---|---|
| `-h`, `--help` | show this help message and exit |
| `--version` | show program's version number and exit |

## `aies assessment`

declarative assessments (ADR-0005): list/show/validate and render engineering or formal results

**Usage:** `aies assessment [-h] [--json] {list,show,validate,result} ...`

**Prerequisites:** Shipped or supplied assessment YAML is available; result rendering additionally requires an aggregated assessment run.

**Result and side effects:** Lists, shows, validates, or applies declarative assessment composition.

**Recommended next step:** Use a valid assessment with `aies qualify --assessment <name>` or inspect its canonical result.

### Subcommands

| Subcommand | What it does |
|---|---|
| `list` | list shipped assessments and their validity |
| `result` | render a non-blocking engineering assessment result (use --formal-qualification for the governed qualification decision) |
| `show` | print a validated assessment |
| `validate` | validate an assessment (name or path) |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies assessment list`

list shipped assessments and their validity

**Usage:** `aies assessment list [-h] [--json]`

**Prerequisites:** Shipped or supplied assessment YAML is available; result rendering additionally requires an aggregated assessment run.

**Result and side effects:** Lists, shows, validates, or applies declarative assessment composition.

**Recommended next step:** Use a valid assessment with `aies qualify --assessment <name>` or inspect its canonical result.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies assessment result`

render a non-blocking engineering assessment result (use --formal-qualification for the governed qualification decision)

**Usage:** `aies assessment result [-h] [--format {markdown,html}] [--out OUT] [--formal-qualification] [--json] run`

**Prerequisites:** The run was composed under a validated declarative assessment and has aggregated evidence.

**Result and side effects:** Renders the non-blocking Engineering Assessment Result by default; `--formal-qualification` explicitly invokes the governed PASS / FAIL / INCONCLUSIVE / INSUFFICIENT EVIDENCE decision.

**Recommended next step:** Use the engineering result for analysis; enter the formal workflow only when qualification is intentionally required.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RUN>` | required | aggregated run composed under an assessment | — |
| `--format` | optional | render the canonical result as markdown (default) or HTML | choices: `markdown`, `html`; default: `markdown` |
| `--out` | optional | write HTML to this file instead of stdout | Applies to HTML output; JSON is selected independently with `--json`. |
| `--formal-qualification` | optional | render the canonical human-governed PASS/FAIL/INCONCLUSIVE/INSUFFICIENT EVIDENCE result and use it as the command exit gate | Opt-in formal gate; without it the command renders Engineering Assessment Result and succeeds when the artifact is generated. |
| `--json` | optional | emit machine-readable JSON | — |

## `aies assessment show`

print a validated assessment

**Usage:** `aies assessment show [-h] [--json] name`

**Prerequisites:** Shipped or supplied assessment YAML is available; result rendering additionally requires an aggregated assessment run.

**Result and side effects:** Lists, shows, validates, or applies declarative assessment composition.

**Recommended next step:** Use a valid assessment with `aies qualify --assessment <name>` or inspect its canonical result.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | assessment name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies assessment validate`

validate an assessment (name or path)

**Usage:** `aies assessment validate [-h] [--json] name`

**Prerequisites:** Shipped or supplied assessment YAML is available; result rendering additionally requires an aggregated assessment run.

**Result and side effects:** Lists, shows, validates, or applies declarative assessment composition.

**Recommended next step:** Use a valid assessment with `aies qualify --assessment <name>` or inspect its canonical result.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | assessment name or YAML path | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies assessment-profile`

inspect governed subject profiles and applicability

**Usage:** `aies assessment-profile [-h] [--json] {list,show,validate} ...`

**Prerequisites:** AIES is installed; no workspace, endpoint, or credential is required.

**Result and side effects:** Lists, shows, or validates approved subject-specific assessment semantics, complete perspective applicability, executors, evidence adapters, decision products, and limitations.

**Recommended next step:** Select an implemented profile, then collect evidence through its declared entry point; unsupported perspectives remain explicit roadmap gaps.

### Subcommands

| Subcommand | What it does |
|---|---|
| `list` | list shipped Subject Assessment Profiles |
| `show` | show one profile by SAP code or subject kind |
| `validate` | validate profiles, taxonomy alignment, and applicability rationale |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies assessment-profile list`

list shipped Subject Assessment Profiles

**Usage:** `aies assessment-profile list [-h] [--json]`

**Prerequisites:** AIES is installed; no workspace, endpoint, or credential is required.

**Result and side effects:** Lists, shows, or validates approved subject-specific assessment semantics, complete perspective applicability, executors, evidence adapters, decision products, and limitations.

**Recommended next step:** Select an implemented profile, then collect evidence through its declared entry point; unsupported perspectives remain explicit roadmap gaps.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies assessment-profile show`

show one profile by SAP code or subject kind

**Usage:** `aies assessment-profile show [-h] [--json] reference`

**Prerequisites:** AIES is installed; no workspace, endpoint, or credential is required.

**Result and side effects:** Lists, shows, or validates approved subject-specific assessment semantics, complete perspective applicability, executors, evidence adapters, decision products, and limitations.

**Recommended next step:** Select an implemented profile, then collect evidence through its declared entry point; unsupported perspectives remain explicit roadmap gaps.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<REFERENCE>` | required | profile code (for example SAP-01) or subject kind | — |
| `--json` | optional | machine-readable output | — |

## `aies assessment-profile validate`

validate profiles, taxonomy alignment, and applicability rationale

**Usage:** `aies assessment-profile validate [-h] [--json]`

**Prerequisites:** AIES is installed; no workspace, endpoint, or credential is required.

**Result and side effects:** Lists, shows, or validates approved subject-specific assessment semantics, complete perspective applicability, executors, evidence adapters, decision products, and limitations.

**Recommended next step:** Select an implemented profile, then collect evidence through its declared entry point; unsupported perspectives remain explicit roadmap gaps.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies audit`

assess repository-practice maturity and read-only engineering evidence across architecture, quality, correctness, security, testing, dependencies, and remediation

**Usage:** `aies audit [-h] [--json] [--rt {1,2,3,4}] [--gate] [--attest FILE] [--format {markdown,json}] [--conformance-only] [--out DIRECTORY] repo`

**Prerequisites:** The repository path is readable. The default is read-only and does not execute repository code; attestations may support only genuinely non-detectable controls.

**Result and side effects:** Produces separate ML0–ML4 repository-practice maturity and architecture, code-quality, correctness-assurance, security, dependency, evidence-confidence, limitation, and remediation views. `--out` writes a linked bundle; `--conformance-only` selects the faster legacy layer.

**Recommended next step:** Triage evidence-linked findings, retain native tool results, rerun after material change, and record any human conformance or change decision separately.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<REPO>` | required | path to the repository to audit | — |
| `--rt` | optional | evaluate against this risk tier's required evidence | choices: `1`, `2`, `3`, `4` |
| `--gate` | optional | CI mode: non-zero exit if RT-required evidence is missing (implies the given --rt, default RT2 — Moderate) | Implies RT2 — Moderate when `--rt` is omitted. |
| `--attest` | optional | attestation JSON for non-detectable practices ({items:[{id, evidence}]}) | — |
| `--format` | optional | output representation (default: markdown) | choices: `markdown`, `json`; default: `markdown` |
| `--conformance-only` | optional | skip deeper static/retained-artifact engineering analysis and emit only the faster ML0 through ML4 practice-maturity layer | — |
| `--out` | optional | write an immutable Markdown, JSON, HTML, and bundle-index report | — |

## `aies benchmark`

run a non-blocking engineering benchmark; optionally auto-score and report

**Usage:** `aies benchmark [-h] [--json] [--profile PROFILE] [--rt {1,2,3,4}] [--area AREA] [--all-areas] [--repeats REPEATS] [--parallel N] [--runtime RUNTIME] [--judge DEPLOYMENT] [--judge-batch-size N] [--reviewer-runtime REVIEWER_RUNTIME] [--human-evaluation NAME] [--consider-advisory-review] model`

**Prerequisites:** The target deployment is registered and reachable; suites and the selected profile are valid. `--judge` requires a reachable reviewer deployment.

**Result and side effects:** Runs a non-blocking Engineering Evaluation. Without a judge it collects responses and a scoresheet; with `--judge` it also scores, analyzes, and writes the complete report bundle.

**Recommended next step:** Inspect the generated ECM/report, or score the collected run later with `aies review <run> --model-reviewer <judge>`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<MODEL>` | required | deployment id, or model name when unambiguous | — |
| `--profile` | optional | EV weighting profile (default: enterprise) | default: `enterprise` |
| `--rt` | optional | scoped risk tier number (default: 2 for RT2 — Moderate) | choices: `1`, `2`, `3`, `4`; default: `2` |
| `--area` | optional | competency area code such as CA-05; repeat for more areas | repeatable |
| `--all-areas` | optional | benchmark across ALL competency areas CA-01…CA-12 | — |
| `--repeats` | optional | repeat each scenario for a stability study; repeats do not add breadth | — |
| `--parallel` | optional | maximum concurrent inference calls (default: 1 or AIES_PARALLEL) | — |
| `--runtime` | optional | runtime name used to disambiguate the deployment | — |
| `--judge` | optional | auto-score with this judge and complete analysis/reporting (or 'self'; defaults to $AIES_JUDGE) | — |
| `--judge-batch-size` | optional | responses per automated judge request (default 8, or $AIES_JUDGE_BATCH_SIZE) | — |
| `--reviewer-runtime` | optional | disambiguate the judge deployment's runtime | — |
| `--human-evaluation` | optional | optionally record a named human evaluation; never required | — |
| `--consider-advisory-review` | optional | optionally record that a human considered automated scores | — |

## `aies bridge`

import versioned external evidence with provenance and loss reports

**Usage:** `aies bridge [-h] [--json] {inspect-import,inspect-export,sarif-import,sarif-export} ...`

**Prerequisites:** A version-supported external evidence file is available; Inspect rating import also requires an existing matching AIES run.

**Result and side effects:** Converts supported external evidence with a source digest, converter identity, explicit loss accounting, and no inferred scores or claim inflation.

**Recommended next step:** Inspect imports must be aggregated into refreshed reports; SARIF artifacts remain repository findings until a separate analysis explicitly consumes them.

### Subcommands

| Subcommand | What it does |
|---|---|
| `inspect-export` | export a run to the AIES Inspect JSON profile |
| `inspect-import` | import an AIES-profiled Inspect EvalLog JSON |
| `sarif-export` | export normalized repository findings as SARIF 2.1.0 |
| `sarif-import` | normalize SARIF 2.1.0 findings without claim inflation |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies bridge inspect-export`

export a run to the AIES Inspect JSON profile

**Usage:** `aies bridge inspect-export [-h] --out OUT [--json] run`

**Prerequisites:** An AIES run exists and the destination JSON path does not.

**Result and side effects:** Exports prompts, outputs, explicit AIES EV scores, findings, diagnostics, and identity through the documented portable Inspect JSON profile.

**Recommended next step:** Load the JSON through an Inspect-compatible workflow or test round-trip with `bridge inspect-import`; native Inspect-only container metadata is intentionally not fabricated.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RUN>` | required | AIES run to export | — |
| `--out` | required | new JSON output path | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies bridge inspect-import`

import an AIES-profiled Inspect EvalLog JSON

**Usage:** `aies bridge inspect-import [-h] [--source SOURCE] [--json] run file`

**Prerequisites:** An existing AIES run and Inspect EvalLog JSON using the documented AIES per-sample metadata and EV1–EV6 scorer profile are available.

**Result and side effects:** Writes automated rating observations plus a source-bound conversion artifact and loss report; unsupported samples are skipped with reasons.

**Recommended next step:** Run `aies qualify --resume <run-id>` to aggregate and regenerate the report bundle.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RUN>` | required | existing AIES run receiving EV observations | — |
| `<FILE>` | required | Inspect EvalLog JSON export | — |
| `--source` | optional | optional source/rater label (default binds filename and digest) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies bridge sarif-export`

export normalized repository findings as SARIF 2.1.0

**Usage:** `aies bridge sarif-export [-h] --out OUT [--json] file`

**Prerequisites:** An aies-sarif-evidence/v1 normalized artifact exists and the destination path does not.

**Result and side effects:** Exports preserved findings as SARIF 2.1.0 with an AIES source-artifact digest and explicit claim limitation.

**Recommended next step:** Validate the SARIF with the consuming tool and retain the normalized artifact as the AIES provenance source.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<FILE>` | required | aies-sarif-evidence/v1 JSON artifact | — |
| `--out` | required | new SARIF output path | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies bridge sarif-import`

normalize SARIF 2.1.0 findings without claim inflation

**Usage:** `aies bridge sarif-import [-h] [--out OUT] [--subject SUBJECT] [--classification {public,internal,confidential,restricted}] [--json] file`

**Prerequisites:** A SARIF 2.1.0 JSON file from a completed static-analysis invocation is available.

**Result and side effects:** Preserves tool, rule, version, location, severity, fingerprints, fixes, suppressions, baseline state, and invocation status in an immutable normalized artifact.

**Recommended next step:** Use the artifact as repository-analysis evidence; never treat an empty or successful tool run as proof of correctness.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<FILE>` | required | SARIF 2.1.0 JSON file | — |
| `--out` | optional | output artifact (default: workspace imports) | — |
| `--subject` | optional | repository subject id for correlation (default: explicit unbound identity) | — |
| `--classification` | optional | evidence classification recorded on every typed event | choices: `public`, `internal`, `confidential`, `restricted`; default: `internal` |
| `--json` | optional | emit machine-readable JSON | — |

## `aies capabilities`

render the Engineering Capability Matrix for an aggregated run/deployment

**Usage:** `aies capabilities [-h] [--json] [--ecm] [--qualification-profile] [--format {markdown,json,html}] [--sort {task,performance,breadth,evidence,status}] [--ascending] [--write] ref`

**Prerequisites:** An aggregated run exists; deployment ids resolve to their latest aggregated run.

**Result and side effects:** Renders the Engineering Capability Matrix by default; `--qualification-profile` selects the separate formal CL/autonomy view.

**Recommended next step:** Use `aies guidance` for bounded use advice or `aies compare` for compatible task comparison.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<REF>` | required | run id, or deployment id (its latest aggregated run) | — |
| `--ecm` | optional | compatibility alias; ECM is now the default capability view | — |
| `--qualification-profile` | optional | render the separate formal per-area CL/autonomy qualification view | Switches from the default ECM to the separate formal CL/autonomy qualification view. |
| `--format` | optional | ECM output format (default: markdown) | choices: `markdown`, `json`, `html`; default: `markdown` |
| `--sort` | optional | sort task rows (default: performance) | choices: `task`, `performance`, `breadth`, `evidence`, `status`; default: `performance`; Orders ECM task rows; generated HTML can also be re-sorted by selecting any column heading. |
| `--ascending` | optional | sort from low to high; unassessed tasks remain last | Reverses the selected ECM sort while keeping unassessed tasks separate at the end. |
| `--write` | optional | write ECM output beside the run | Writes the default ECM artifact beside the run. |

## `aies ci`

CI evidence integrations; advisory unless enforcement is explicit

**Usage:** `aies ci [-h] [--json] {audit} ...`

**Prerequisites:** AIES is installed in CI and the repository checkout is readable.

**Result and side effects:** Provides retained CI evidence integrations that remain advisory unless enforcement is explicitly selected.

**Recommended next step:** Start with `aies ci audit . --rt 2`; review artifacts before adding `--enforce`.

### Subcommands

| Subcommand | What it does |
|---|---|
| `audit` | retain repository-assessment evidence and annotations |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies ci audit`

retain repository-assessment evidence and annotations

**Usage:** `aies ci audit [-h] [--json] [--rt {1,2,3,4}] [--enforce] [--attest FILE] [--out DIR] [--github-annotations] [repo]`

**Prerequisites:** The repository checkout is readable; optional attestations use the documented evidence-linked JSON shape.

**Result and side effects:** Writes repository-assessment JSON, Markdown, and annotation artifacts; emits GitHub annotations when requested. It exits non-zero for policy gaps only with `--enforce`.

**Recommended next step:** Upload the artifact directory on every run. Enable enforcement only after repository owners approve the selected risk-tier policy.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<REPO>` | optional | repository path to inspect (default: current directory) | default: `.` |
| `--rt` | optional | risk tier policy to calculate (default: RT2 — Moderate) | choices: `1`, `2`, `3`, `4`; default: `2` |
| `--enforce` | optional | explicitly fail CI when required evidence is missing; without this flag the command is advisory | — |
| `--attest` | optional | optional attestation JSON for non-detectable practices | — |
| `--out` | optional | artifact directory (default: aies-ci) | default: `aies-ci` |
| `--github-annotations` | optional | emit GitHub Actions notice/warning workflow commands | — |

## `aies compare`

compare two or more compatible deployment runs or stored repository assessments

**Usage:** `aies compare [-h] [--json] [--format {markdown,json,html}] [--ecm] [--area-summary] [--formal-qualification] [--sort {task,confidence,spread,leader}] [--only-comparable] [--out DIRECTORY] [--save] refs [refs ...]`

**Prerequisites:** Between two and five references resolve either to aggregated deployment runs or to stored repository audit ids; subject types cannot be mixed. Deployment leaders and repository deltas require their respective scope/protocol compatibility checks.

**Result and side effects:** Builds an adaptive pair/matrix ECM for deployments or a no-winner perspective/metric matrix for repositories, with compatibility, confidence, coverage, next actions, optional report bundles, and explicit persistence.

**Recommended next step:** Use `--only-comparable --sort spread --out comparison`; add `--save` only when an append-only API-visible record is wanted. Do not treat the output as qualification, authorization, universal ranking, or proof of repository quality.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<REFS>` | required | 2 to 5 run ids, deployment ids, or repository audit ids; do not mix repository and deployment evidence | values: +; Accepts 2–5 compatible deployment/run references or 2–5 stored repository-audit ids. Repository and deployment evidence cannot be mixed. |
| `--format` | optional | output representation (default: markdown) | choices: `markdown`, `json`, `html`; default: `markdown` |
| `--ecm` | optional | compatibility alias; task-level ECM comparison is now the default | Compatibility alias; ECM comparison is the default. |
| `--area-summary` | optional | render the legacy competency-area aggregate comparison instead of ECM | Selects the legacy two-run competency-area aggregate instead of the default ECM comparison. |
| `--formal-qualification` | optional | require demonstrated tasks and the human-rater protocol; default ECM comparison uses compatible observed engineering evidence | Switches from compatible observed-score comparison to demonstrated, human-protocol-qualified comparison; it cannot be combined with `--area-summary`. |
| `--sort` | optional | multi-run task ordering (default: stable task taxonomy order) | choices: `task`, `confidence`, `spread`, `leader`; default: `task`; Orders pair or matrix rows by stable task/metric identity, confidence, evidence-backed spread, or compatible higher-observed subject. Repository comparisons do not support leader sorting. |
| `--only-comparable` | optional | hide tasks that cannot support a like-for-like comparison | Hides rows with mismatched or missing evidence; the summary still discloses that coverage was filtered. |
| `--out` | optional | write an immutable comparison.json, Markdown, HTML, and bundle index | Writes an immutable comparison Markdown/JSON/sortable-HTML bundle plus its bundle index without changing source evidence. |
| `--save` | optional | persist the derived comparison as an append-only workspace record for GET /comparisons; comparison remains informational | Explicitly creates an append-only workspace comparison record for the read-only `/comparisons` API. Without it, comparison is not persisted. |

## `aies completion`

generate Tab completion for PowerShell, Bash, or Zsh

**Usage:** `aies completion [-h] {powershell,bash,zsh}`

**Prerequisites:** AIES is installed in the shell environment.

**Result and side effects:** Prints a sourceable completion definition generated from the live parser; it changes nothing until sourced or added to the shell profile.

**Recommended next step:** Source it for the current session or add the documented command to the shell profile, then press Tab after `aies`, subcommands, options, or enumerated values.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<SHELL>` | required | shell whose sourceable completion definition will be printed | choices: `powershell`, `bash`, `zsh` |

## `aies conform`

declare/check conformance to AIES

**Usage:** `aies conform [-h] [--json] {template,check,requirements,engine} ...`

**Prerequisites:** Template generation has no evidence prerequisite; checks require a statement, while engine verification requires the golden corpus and optionally a compatible foreign engine command.

**Result and side effects:** Scaffolds/checks conformance claims or verifies decision-engine semantics; it does not issue certification.

**Recommended next step:** Resolve unsupported claims or engine mismatches, then record any human conformance decision separately.

### Subcommands

| Subcommand | What it does |
|---|---|
| `check` | check a conformance statement and its evidence |
| `engine` | verify a decision engine against the golden Evidence Package corpus (CONFORMANCE-POLICY.md). Defaults to the reference engine; --engine verifies a FOREIGN engine so independent implementations can self-check |
| `requirements` | list conformance requirements |
| `template` | create a conformance statement template |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies conform check`

check a conformance statement and its evidence

**Usage:** `aies conform check [-h] [--write] [--json] file`

**Prerequisites:** Template generation has no evidence prerequisite; checks require a statement, while engine verification requires the golden corpus and optionally a compatible foreign engine command.

**Result and side effects:** Scaffolds/checks conformance claims or verifies decision-engine semantics; it does not issue certification.

**Recommended next step:** Resolve unsupported claims or engine mismatches, then record any human conformance decision separately.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<FILE>` | required | conformance statement YAML or JSON file | — |
| `--write` | optional | write the conformance report beside the input | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies conform engine`

verify a decision engine against the golden Evidence Package corpus (CONFORMANCE-POLICY.md). Defaults to the reference engine; --engine verifies a FOREIGN engine so independent implementations can self-check

**Usage:** `aies conform engine [-h] [--corpus CORPUS] [--engine ENGINE] [--json]`

**Prerequisites:** Template generation has no evidence prerequisite; checks require a statement, while engine verification requires the golden corpus and optionally a compatible foreign engine command.

**Result and side effects:** Scaffolds/checks conformance claims or verifies decision-engine semantics; it does not issue certification.

**Recommended next step:** Resolve unsupported claims or engine mismatches, then record any human conformance decision separately.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--corpus` | optional | path to conformance/corpus (default: auto-discover) | — |
| `--engine` | optional | a foreign engine command: reads {evidence,assessment} JSON on stdin, prints the Canonical Assessment Result JSON on stdout | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies conform requirements`

list conformance requirements

**Usage:** `aies conform requirements [-h] [--json]`

**Prerequisites:** Template generation has no evidence prerequisite; checks require a statement, while engine verification requires the golden corpus and optionally a compatible foreign engine command.

**Result and side effects:** Scaffolds/checks conformance claims or verifies decision-engine semantics; it does not issue certification.

**Recommended next step:** Resolve unsupported claims or engine mismatches, then record any human conformance decision separately.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies conform template`

create a conformance statement template

**Usage:** `aies conform template [-h] [--class {adopter,implementation}] [--out OUT] [--json]`

**Prerequisites:** Template generation has no evidence prerequisite; checks require a statement, while engine verification requires the golden corpus and optionally a compatible foreign engine command.

**Result and side effects:** Scaffolds/checks conformance claims or verifies decision-engine semantics; it does not issue certification.

**Recommended next step:** Resolve unsupported claims or engine mismatches, then record any human conformance decision separately.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--class` | optional | conformance class to scaffold (default: adopter) | choices: `adopter`, `implementation`; default: `adopter` |
| `--out` | optional | destination file; omit to print the template | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies corpus`

advisory quality review of the assessment corpus itself (calibration, coverage, behavioral diversity, empirical maturity); multidimensional, never a single grade, never a gate

**Usage:** `aies corpus [-h] [--json] {health,coverage,duplicates,review-pending,review} ...`

**Prerequisites:** The shipped or selected competencies directory is readable; semantic review additionally requires a reviewer deployment.

**Result and side effects:** Produces advisory corpus health, coverage, duplication, pending-review, or single-instrument critique evidence.

**Recommended next step:** Apply deterministic fixes and human review; corpus tools never approve instruments automatically.

### Subcommands

| Subcommand | What it does |
|---|---|
| `coverage` | the coverage dimension only — RT distribution per area and per-assessment tier depth |
| `duplicates` | near-duplicate scenario pairs (prompt/ceiling overlap), twin-aware — flags redundancy candidates for human review |
| `health` | full multidimensional corpus-health report + ranked advisory recommendations |
| `review` | review one scenario as a measurement instrument: deterministic structural checks always, plus an opt-in model critique with --reviewer (critique only — never rewrites/approves) |
| `review-pending` | inventory pending scenario design reviews, run deterministic structural preflight, and expose human disposition fields |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies corpus coverage`

the coverage dimension only — RT distribution per area and per-assessment tier depth

**Usage:** `aies corpus coverage [-h] [--root ROOT] [--json]`

**Prerequisites:** The shipped or selected competencies directory is readable; semantic review additionally requires a reviewer deployment.

**Result and side effects:** Produces advisory corpus health, coverage, duplication, pending-review, or single-instrument critique evidence.

**Recommended next step:** Apply deterministic fixes and human review; corpus tools never approve instruments automatically.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--root` | optional | competencies directory (default: shipped suites) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies corpus duplicates`

near-duplicate scenario pairs (prompt/ceiling overlap), twin-aware — flags redundancy candidates for human review

**Usage:** `aies corpus duplicates [-h] [--root ROOT] [--json]`

**Prerequisites:** The shipped or selected competencies directory is readable; semantic review additionally requires a reviewer deployment.

**Result and side effects:** Produces advisory corpus health, coverage, duplication, pending-review, or single-instrument critique evidence.

**Recommended next step:** Apply deterministic fixes and human review; corpus tools never approve instruments automatically.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--root` | optional | competencies directory (default: shipped suites) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies corpus health`

full multidimensional corpus-health report + ranked advisory recommendations

**Usage:** `aies corpus health [-h] [--root ROOT] [--json]`

**Prerequisites:** The shipped or selected competencies directory is readable; semantic review additionally requires a reviewer deployment.

**Result and side effects:** Produces advisory corpus health, coverage, duplication, pending-review, or single-instrument critique evidence.

**Recommended next step:** Apply deterministic fixes and human review; corpus tools never approve instruments automatically.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--root` | optional | competencies directory (default: shipped suites) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies corpus review`

review one scenario as a measurement instrument: deterministic structural checks always, plus an opt-in model critique with --reviewer (critique only — never rewrites/approves)

**Usage:** `aies corpus review [-h] [--reviewer REVIEWER] [--runtime RUNTIME] [--json] scenario`

**Prerequisites:** The shipped or selected competencies directory is readable; semantic review additionally requires a reviewer deployment.

**Result and side effects:** Produces advisory corpus health, coverage, duplication, pending-review, or single-instrument critique evidence.

**Recommended next step:** Apply deterministic fixes and human review; corpus tools never approve instruments automatically.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<SCENARIO>` | required | scenario id (SC-CA##-###) or a YAML path | — |
| `--reviewer` | optional | a deployment id to critique semantically (omit for structural only) | — |
| `--runtime` | optional | runtime name used to disambiguate the reviewer deployment | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies corpus review-pending`

inventory pending scenario design reviews, run deterministic structural preflight, and expose human disposition fields

**Usage:** `aies corpus review-pending [-h] [--root ROOT] [--json]`

**Prerequisites:** The shipped or selected competencies directory is readable; semantic review additionally requires a reviewer deployment.

**Result and side effects:** Produces advisory corpus health, coverage, duplication, pending-review, or single-instrument critique evidence.

**Recommended next step:** Apply deterministic fixes and human review; corpus tools never approve instruments automatically.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--root` | optional | competencies directory (default: shipped suites) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies coverage`

show evidence coverage, reuse, and blind spots for a run or audit

**Usage:** `aies coverage [-h] [--json] [--format {markdown,json,html}] [--write] [--out DIR] reference`

**Prerequisites:** A completed deployment run or recorded repository audit exists. Repository artifact writing also requires a new output directory.

**Result and side effects:** Builds a non-decisional matrix of assessed, partially assessed, not assessed, unsupported, and not-applicable perspectives; unique evidence identities and reuse are disclosed separately. `--write` also emits an unassigned Evidence-Linked Remediation and Monitoring Plan.

**Recommended next step:** Use the prioritized acceptance signals and exact reassessment command; a named owner must separately accept, defer, or close any action.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<REFERENCE>` | required | run id or recorded repository audit id | — |
| `--format` | optional | rendering format (default: markdown) | choices: `markdown`, `json`, `html`; default: `markdown` |
| `--write` | optional | write coverage artifacts without changing canonical evidence | — |
| `--out` | optional | immutable output directory required with --write for an audit | — |

## `aies dashboard`

render an HTML dashboard over runs and grants

**Usage:** `aies dashboard [-h] [--json] [--write]`

**Prerequisites:** The workspace contains runs or qualification records.

**Result and side effects:** Renders the shared read-only workspace-overview view model as HTML; `--write` persists it and computes no decisions.

**Recommended next step:** Open the dashboard and follow links to canonical evidence products.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `--write` | optional | write dashboard.html into the workspace instead of only printing its path | — |

## `aies demo`

run the complete offline Engineering Evaluation story

**Usage:** `aies demo [-h] [--json] [--workspace WORKSPACE] [--parallel N] [--open]`

**Prerequisites:** AIES is installed; no model server, API key, Make, or Bash is required.

**Result and side effects:** Runs the real collection, batched automated scoring, aggregation, ECM, fit-guidance, and report pipeline fully offline with mock deployments.

**Recommended next step:** Open the printed Executive Summary or run `aies open latest --export-redacted` in the demo workspace.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `--workspace` | optional | persistent demo workspace (default: ./aies-demo-workspace) | default: `aies-demo-workspace` |
| `--parallel` | optional | maximum concurrent mock calls (default: 8) | default: `8` |
| `--open` | optional | open the Executive Summary in the default browser when complete | — |

## `aies deployment`

manage deployments (AI deployment × runtime × config × endpoint)

**Usage:** `aies deployment [-h] [--json] {list,inspect,add,update,remove,retire,verify-artifact} ...`

**Prerequisites:** AIES has a writable workspace; mutating subcommands additionally require valid deployment YAML or an existing id as documented.

**Result and side effects:** Lists, inspects, registers, updates, retires, removes, or verifies deployment entries.

**Recommended next step:** Inspect the resulting deployment before using it in evaluation.

### Subcommands

| Subcommand | What it does |
|---|---|
| `add` | register a new deployment |
| `inspect` | inspect one deployment |
| `list` | list active deployments |
| `remove` | hard-delete an entry so its id can be reused (vs retire, which reserves it for audit) |
| `retire` | retire a deployment without deleting history |
| `update` | overwrite an EXISTING deployment in place (same id) — for config/key/roles fixes |
| `verify-artifact` | verify a local artifact against the deployment's declared checksum/signature |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies deployment add`

register a new deployment

**Usage:** `aies deployment add [-h] [--json] file`

**Prerequisites:** A valid deployment YAML exists and its id is not already registered.

**Result and side effects:** Creates a deployment registry entry.

**Recommended next step:** Inspect it, then use it with `benchmark`, `qualify`, `review`, or `corpus review`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<FILE>` | required | deployment YAML file | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies deployment inspect`

inspect one deployment

**Usage:** `aies deployment inspect [-h] [--json] name`

**Prerequisites:** AIES has a writable workspace; mutating subcommands additionally require valid deployment YAML or an existing id as documented.

**Result and side effects:** Lists, inspects, registers, updates, retires, removes, or verifies deployment entries.

**Recommended next step:** Inspect the resulting deployment before using it in evaluation.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | deployment id, or an unambiguous model name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies deployment list`

list active deployments

**Usage:** `aies deployment list [-h] [--all] [--json]`

**Prerequisites:** AIES has a writable workspace; mutating subcommands additionally require valid deployment YAML or an existing id as documented.

**Result and side effects:** Lists, inspects, registers, updates, retires, removes, or verifies deployment entries.

**Recommended next step:** Inspect the resulting deployment before using it in evaluation.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--all` | optional | include retired deployment entries | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies deployment remove`

hard-delete an entry so its id can be reused (vs retire, which reserves it for audit)

**Usage:** `aies deployment remove [-h] [--json] name`

**Prerequisites:** AIES has a writable workspace; mutating subcommands additionally require valid deployment YAML or an existing id as documented.

**Result and side effects:** Lists, inspects, registers, updates, retires, removes, or verifies deployment entries.

**Recommended next step:** Inspect the resulting deployment before using it in evaluation.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | deployment id to remove | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies deployment retire`

retire a deployment without deleting history

**Usage:** `aies deployment retire [-h] [--json] name`

**Prerequisites:** AIES has a writable workspace; mutating subcommands additionally require valid deployment YAML or an existing id as documented.

**Result and side effects:** Lists, inspects, registers, updates, retires, removes, or verifies deployment entries.

**Recommended next step:** Inspect the resulting deployment before using it in evaluation.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | deployment id, or an unambiguous model name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies deployment update`

overwrite an EXISTING deployment in place (same id) — for config/key/roles fixes

**Usage:** `aies deployment update [-h] [--json] file`

**Prerequisites:** The deployment id already exists and a replacement YAML is available.

**Result and side effects:** Updates mutable deployment configuration while preserving the deployment id.

**Recommended next step:** Inspect and re-run affected evaluations; material fingerprint changes trigger reassessment.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<FILE>` | required | deployment YAML file with the existing id | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies deployment verify-artifact`

verify a local artifact against the deployment's declared checksum/signature

**Usage:** `aies deployment verify-artifact [-h] --artifact ARTIFACT [--pubkey PUBKEY] [--signature SIGNATURE] [--runtime RUNTIME] [--json] name`

**Prerequisites:** The deployment declares artifact provenance; the local artifact is accessible. Signature verification additionally needs the crypto extra and key/signature inputs.

**Result and side effects:** Verifies checksum and, when supplied, detached signature evidence.

**Recommended next step:** Correct provenance failures before using the artifact for trusted assessment.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | deployment id, or an unambiguous model name | — |
| `--artifact` | required | path to the model artifact file | — |
| `--pubkey` | optional | PEM public key for signature verification | Use with `--signature`; checksum verification remains available without either. |
| `--signature` | optional | detached signature file | Use with `--pubkey`; both are needed for detached-signature verification. |
| `--runtime` | optional | disambiguate the deployment's runtime | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies discover`

scan runtimes and register the deployments they serve

**Usage:** `aies discover [-h] [--json]`

**Prerequisites:** At least one supported local runtime is installed and reachable.

**Result and side effects:** Discovers served deployments and registers new entries.

**Recommended next step:** Inspect with `aies deployment list` and `aies deployment inspect <id>`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies doctor`

validate the environment and detect runtimes

**Usage:** `aies doctor [-h] [--json]`

**Prerequisites:** AIES is installed.

**Result and side effects:** Checks the environment, workspace, TLS/runtime availability, fingerprint, and advisory debris without deleting anything.

**Recommended next step:** Resolve blocking findings, then run `aies discover` or `aies deployment add`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies evaluate`

plan and run a beginner-friendly automated Engineering Evaluation

**Usage:** `aies evaluate [-h] [--json] [--assessment NAME | --all-areas] [--area CA-NN] [--rt {1,2,3,4}] [--judge DEPLOYMENT] [--judge-batch-size N] [--parallel N] [--runtime RUNTIME] [--reviewer-runtime REVIEWER_RUNTIME] [--plan-only] [--open] subject`

**Prerequisites:** The subject and automated reviewer deployments are registered and reachable; use `--plan-only` before any potentially costly run.

**Result and side effects:** Plans and runs a bounded, no-repeat, non-blocking Engineering Evaluation through the canonical qualify pipeline and creates the complete report bundle.

**Recommended next step:** Run `aies open <run-id>` to inspect the result; expand scope only when the decision requires more evidence.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<SUBJECT>` | required | registered deployment id or unambiguous model name | — |
| `--assessment` | optional | bounded assessment (default: coder unless --area/--all-areas is used) | Defaults to the bounded coder assessment unless `--area` or `--all-areas` is selected. |
| `--all-areas` | optional | evaluate all CA-01 through CA-12 areas | — |
| `--area` | optional | evaluate one competency area; repeat for more | repeatable |
| `--rt` | optional | risk tier (default RT1 — Minimal for a bounded first run) | choices: `1`, `2`, `3`, `4`; default: `1` |
| `--judge` | optional | automated reviewer deployment (default: AIES_JUDGE) | Required for execution unless AIES_JUDGE is set; automated scoring completes Engineering Evaluation without human review. |
| `--judge-batch-size` | optional | responses per reviewer call (default 8 or AIES_JUDGE_BATCH_SIZE) | — |
| `--parallel` | optional | maximum concurrent candidate and judge calls (default: 1) | default: `1` |
| `--runtime` | optional | disambiguate the assessed deployment runtime | — |
| `--reviewer-runtime` | optional | disambiguate the reviewer deployment runtime | — |
| `--plan-only` | optional | show calls, concurrency, estimates, and limitations without executing | Performs no inference and writes no run; reports calls, concurrency, declared cost/ETA or exact unknowns, limitations, and resumability. |
| `--open` | optional | open the Executive Summary in the default browser after completion | Launches the Executive Summary after success; without it the same local link and safe-sharing command are printed. |

## `aies export`

export a run's responses+scores to a generic eval-log JSON (round-trips with import)

**Usage:** `aies export [-h] [--json] [--write] run`

**Prerequisites:** A run with response records exists.

**Result and side effects:** Prints a portable eval-log JSON or writes `eval-log.json` with `--write`.

**Recommended next step:** Use the file with another evaluation tool or round-trip it through `aies import`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | run id to export | — |
| `--write` | optional | write eval-log.json into the run directory (else stdout) | — |

## `aies grant`

record a human qualification decision

**Usage:** `aies grant [-h] [--json] --decision {grant,grant-with-conditions,deny} --authority AUTHORITY [--assessor ASSESSOR] [--assessor-id ASSESSOR_ID] [--peer-reviewer PEER_REVIEWER] [--peer-reviewer-id PEER_REVIEWER_ID] [--assessor-conflict-free] [--peer-conflict-free] [--role {ROLE-01,ROLE-02,ROLE-03,ROLE-04,ROLE-05,ROLE-06,ROLE-07,ROLE-08,ROLE-09,ROLE-10,ROLE-11,ROLE-12,ROLE-13,ROLE-14}] [--phase {P01,P02,P03,P04,P05,P06,P07,P08,P09,P10,P11,P12,P13,P14,P15,P16}] [--sponsor SPONSOR] [--framework-version FRAMEWORK_VERSION] [--agent-definition-version AGENT_DEFINITION_VERSION] [--valid-from ISO-8601] [--valid-until ISO-8601] [--second SECOND] [--condition CONDITION] [--rationale RATIONALE] [--consider-advisory-review] [--human-evaluation NAME] run`

**Prerequisites:** The run is decisional and gate-passing for a grant, required human ratings and divergence dispositions are complete, and assessor/peer identities and conflict declarations satisfy the protocol.

**Result and side effects:** Appends a human qualification decision and immutable Qualification Record; the platform itself does not decide the grant.

**Recommended next step:** Verify the record and monitor conditions, expiry, incidents, drift, and requalification triggers.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | decisional, gate-passing run used as qualification evidence | — |
| `--decision` | required | human authority's recorded qualification decision | choices: `grant`, `grant-with-conditions`, `deny` |
| `--authority` | required | named human authority (ROLE-13) | — |
| `--assessor` | optional | named human assessor (defaults to authority) | — |
| `--assessor-id` | optional | durable assessor id from `aies rater register` | — |
| `--peer-reviewer` | optional | named independent human peer reviewer | — |
| `--peer-reviewer-id` | optional | durable peer id from `aies rater register` | — |
| `--assessor-conflict-free` | optional | assessor declares no conflict with the subject | — |
| `--peer-conflict-free` | optional | peer reviewer declares no conflict with the subject | — |
| `--role` | optional | qualified engineering role, for example ROLE-06 | choices: `ROLE-01`, `ROLE-02`, `ROLE-03`, `ROLE-04`, `ROLE-05`, `ROLE-06`, `ROLE-07`, `ROLE-08`, `ROLE-09`, `ROLE-10`, `ROLE-11`, `ROLE-12`, `ROLE-13`, `ROLE-14` |
| `--phase` | optional | SDLC phase in scope; repeat for additional phases | choices: `P01`, `P02`, `P03`, `P04`, `P05`, `P06`, `P07`, `P08`, `P09`, `P10`, `P11`, `P12`, `P13`, `P14`, `P15`, `P16`; repeatable |
| `--sponsor` | optional | named accountable qualification sponsor | — |
| `--framework-version` | optional | applied AIES-AESQS-CF-01 competency-framework version | — |
| `--agent-definition-version` | optional | applicable ART-14 agent-definition version | — |
| `--valid-from` | optional | start of the qualification validity window | — |
| `--valid-until` | optional | end of the qualification validity window | — |
| `--second` | optional | deprecated peer-reviewer name alias for legacy v4 records | — |
| `--condition` | optional | condition (repeatable; required for grant-with-conditions) | repeatable; Repeatable and required when `--decision grant-with-conditions` is selected. |
| `--rationale` | optional | human authority's reasoned decision rationale | — |
| `--consider-advisory-review` | optional | attest that the authority considered available advisory model-review scores | — |
| `--human-evaluation` | optional | named human evaluator whose qualitative or scored review was considered | — |

## `aies guidance`

render engineering fit from ECM evidence; supply a Qualification Record for bounded deployment guidance

**Usage:** `aies guidance [-h] [--json] [--qualification QUAL-ID] [--role {ROLE-01,ROLE-02,ROLE-03,ROLE-04,ROLE-05,ROLE-06,ROLE-07,ROLE-08,ROLE-09,ROLE-10,ROLE-11,ROLE-12,ROLE-13,ROLE-14}] [--phase {P01,P02,P03,P04,P05,P06,P07,P08,P09,P10,P11,P12,P13,P14,P15,P16}] [--autonomy {0,1,2,3,4}] [--write] ref`

**Prerequisites:** An aggregated ECM-capable run exists. `--qualification` additionally requires a matching Qualification Record.

**Result and side effects:** Renders non-blocking Engineering Fit Guidance by default. Supplying `--qualification` explicitly selects qualification-bounded Deployment Guidance.

**Recommended next step:** Use engineering fit as an evidence-backed selection input; use qualification guidance only for governed deployment scope.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<REF>` | required | aggregated run id, or deployment id | — |
| `--qualification` | optional | active human Qualification Record; switches from engineering fit to governed Deployment Guidance | Switches from default Engineering Fit Guidance to qualification-bounded Deployment Guidance. |
| `--role` | optional | requested engineering role; must match the qualification scope | choices: `ROLE-01`, `ROLE-02`, `ROLE-03`, `ROLE-04`, `ROLE-05`, `ROLE-06`, `ROLE-07`, `ROLE-08`, `ROLE-09`, `ROLE-10`, `ROLE-11`, `ROLE-12`, `ROLE-13`, `ROLE-14` |
| `--phase` | optional | requested SDLC phase; repeat for additional phases | choices: `P01`, `P02`, `P03`, `P04`, `P05`, `P06`, `P07`, `P08`, `P09`, `P10`, `P11`, `P12`, `P13`, `P14`, `P15`, `P16`; repeatable |
| `--autonomy` | optional | requested autonomy level number (for example 2 for AL2 — Collaborative) | choices: `0`, `1`, `2`, `3`, `4` |
| `--write` | optional | write Deployment Guidance Markdown, JSON, and HTML beside the run | — |

## `aies help`

show this help and the typical workflow

**Usage:** `aies help [-h]`

**Prerequisites:** AIES is installed.

**Result and side effects:** Prints the grouped workflow and complete command tree; it changes no state.

**Recommended next step:** Run `aies <command> --help` or open this CLI Reference for parameter-level detail.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |

## `aies import`

import external eval results (EV1–EV6 JSON) into a run as automated ratings

**Usage:** `aies import [-h] [--json] [--source SOURCE] run file`

**Prerequisites:** A collected run exists and the external eval JSON follows the documented EV1–EV6 schema.

**Result and side effects:** Appends parseable external automated-rating observations, aggregates them, and refreshes the complete report bundle.

**Recommended next step:** Inspect the generated engineering results and imported-evidence limitations.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | run id that will receive the imported rating observations | — |
| `<FILE>` | required | eval file: JSON {source?, items:[{scenario_id, repeat?, scores:{EV1..EV6}, findings?}]} | — |
| `--source` | optional | label for the rater (default: the file's `source` field) | — |

## `aies index`

rebuild the result index from run files

**Usage:** `aies index [-h] [--json]`

**Prerequisites:** The workspace contains append-only run and qualification records.

**Result and side effects:** Rebuilds the disposable result index from canonical files.

**Recommended next step:** Use `runs`, `dashboard`, or the read-only API to consume the rebuilt index.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies init`

create a safe AIES workspace and print exact next steps

**Usage:** `aies init [-h] [--json] [--starter-manifest] [--starter {deployment,offline-demo,repository-audit}] [--guided] [--deployment-id DEPLOYMENT_ID] [--model MODEL] [--endpoint ENDPOINT] [--api-key-env API_KEY_ENV] [--role {subject,judge,both}] [path]`

**Prerequisites:** AIES is installed and the selected parent directory is writable.

**Result and side effects:** Creates a non-destructive workspace skeleton and can interactively or reproducibly prepare deployment evaluation, offline demo, or repository audit. It previews endpoint configuration but never accepts or writes credentials.

**Recommended next step:** Set AIES_WORKSPACE for the shell, then run the exact recommended command printed for the selected starter.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<PATH>` | optional | workspace directory to create (default: ./aies-workspace) | default: `aies-workspace` |
| `--starter-manifest` | optional | legacy alias for --starter deployment | Compatibility alias for `--starter deployment`. |
| `--starter` | optional | prepare one first-use path and print its exact next command | choices: `deployment`, `offline-demo`, `repository-audit`; Non-interactive alternative to `--guided`; deployment accepts the related id/model/endpoint/key-environment/role options. |
| `--guided` | optional | interactively select and configure a first-use path | Prompts for a first-use path and non-secret endpoint metadata; do not use in unattended automation. |
| `--deployment-id` | optional | starter deployment id (default: my-deployment) | default: `my-deployment` |
| `--model` | optional | served model id for a deployment starter | default: `replace-with-served-model-id` |
| `--endpoint` | optional | OpenAI-compatible base URL for a deployment starter | default: `http://127.0.0.1:1234/v1` |
| `--api-key-env` | optional | environment variable holding the API key; never the key itself | default: `AIES_OPENAI_API_KEY`; Records only an environment-variable name. Never pass an API key value here. |
| `--role` | optional | intended advisory deployment role (default: subject) | choices: `subject`, `judge`, `both`; default: `subject` |

## `aies journey`

multi-phase journeys (chained scenarios across the SDLC)

**Usage:** `aies journey [-h] [--json] {list,show} ...`

**Prerequisites:** Shipped journey definitions are available.

**Result and side effects:** Lists or shows multi-phase journey definitions without executing them.

**Recommended next step:** Run a journey with `aies qualify <deployment> --journey <id>`.

### Subcommands

| Subcommand | What it does |
|---|---|
| `list` | list available multi-phase journeys |
| `show` | show one multi-phase journey |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies journey list`

list available multi-phase journeys

**Usage:** `aies journey list [-h] [--json]`

**Prerequisites:** Shipped journey definitions are available.

**Result and side effects:** Lists or shows multi-phase journey definitions without executing them.

**Recommended next step:** Run a journey with `aies qualify <deployment> --journey <id>`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies journey show`

show one multi-phase journey

**Usage:** `aies journey show [-h] [--json] id`

**Prerequisites:** Shipped journey definitions are available.

**Result and side effects:** Lists or shows multi-phase journey definitions without executing them.

**Recommended next step:** Run a journey with `aies qualify <deployment> --journey <id>`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<ID>` | required | journey id | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies judge`

judge track record — which deployments have scored runs, and how reliably

**Usage:** `aies judge [-h] [--json] {available,list,history} ...`

**Prerequisites:** Deployments may declare the judge role; history requires prior automated scoring.

**Result and side effects:** Shows the available reviewer pool and evidence-backed judge usage/parse history.

**Recommended next step:** Select a suitable independent judge, then use `qualify --judge` or `review --model-reviewer`.

### Subcommands

| Subcommand | What it does |
|---|---|
| `available` | the judge pool: deployments registered with roles:[judge], and how many |
| `history` | one row per judged run, newest first |
| `list` | judges used across all runs, with runs judged, responses scored, and parse rate |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies judge available`

the judge pool: deployments registered with roles:[judge], and how many

**Usage:** `aies judge available [-h] [--json]`

**Prerequisites:** Deployments may declare the judge role; history requires prior automated scoring.

**Result and side effects:** Shows the available reviewer pool and evidence-backed judge usage/parse history.

**Recommended next step:** Select a suitable independent judge, then use `qualify --judge` or `review --model-reviewer`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies judge history`

one row per judged run, newest first

**Usage:** `aies judge history [-h] [--judge DEPLOYMENT] [--json]`

**Prerequisites:** Deployments may declare the judge role; history requires prior automated scoring.

**Result and side effects:** Shows the available reviewer pool and evidence-backed judge usage/parse history.

**Recommended next step:** Select a suitable independent judge, then use `qualify --judge` or `review --model-reviewer`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--judge` | optional | filter to a single judge deployment id | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies judge list`

judges used across all runs, with runs judged, responses scored, and parse rate

**Usage:** `aies judge list [-h] [--json]`

**Prerequisites:** Deployments may declare the judge role; history requires prior automated scoring.

**Result and side effects:** Shows the available reviewer pool and evidence-backed judge usage/parse history.

**Recommended next step:** Select a suitable independent judge, then use `qualify --judge` or `review --model-reviewer`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies open`

open a run result or export share-safe derived views

**Usage:** `aies open [-h] [--json] [--no-browser] [--export-redacted [ZIP]] [run]`

**Prerequisites:** The selected run has generated HTML reports; redacted export requires a destination that does not already exist.

**Result and side effects:** Opens or links the primary local result. Optional export includes only allowlisted derived views and a digest manifest, never raw evidence or credentials.

**Recommended next step:** Share the redacted archive with its limitations, or return to the canonical workspace for reproducibility and verification.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | optional | run id or 'latest' (default: latest) | default: `latest` |
| `--no-browser` | optional | print the local result link without launching a browser | — |
| `--export-redacted` | optional | also create an immutable redacted ZIP at ZIP or the default exports path | Exports only allowlisted derived views. Raw prompts, responses, ratings, fingerprints, and secrets are excluded. |

## `aies overview`

summarize deployments, runs, assessments, support, and records

**Usage:** `aies overview [-h] [--json]`

**Prerequisites:** AIES has a readable workspace; an empty workspace is valid.

**Result and side effects:** Returns the versioned informational summary shared by the CLI, `/overview` API endpoint, dashboard, and future UI consumers. It computes no assessment outcome.

**Recommended next step:** Inspect runs or support, render the dashboard, or start the read-only API.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies plugins`

list installed runtime adapters

**Usage:** `aies plugins [-h] [--json]`

**Prerequisites:** AIES and any out-of-tree adapter packages are installed.

**Result and side effects:** Lists discovered runtime-adapter plugins and their versions; it changes no state.

**Recommended next step:** Inspect runtimes or register/discover deployments that use the adapters.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies profile`

weighting profiles (enterprise, coder, security, …)

**Usage:** `aies profile [-h] [--json] {list,show,validate} ...`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Lists, shows, or validates EV weighting profiles; profiles cannot relax gates.

**Recommended next step:** Use a valid profile with `benchmark` or `qualify`.

### Subcommands

| Subcommand | What it does |
|---|---|
| `list` | list available weighting profiles |
| `show` | show one weighting profile |
| `validate` | validate one weighting profile |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies profile list`

list available weighting profiles

**Usage:** `aies profile list [-h] [--json]`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Lists, shows, or validates EV weighting profiles; profiles cannot relax gates.

**Recommended next step:** Use a valid profile with `benchmark` or `qualify`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies profile show`

show one weighting profile

**Usage:** `aies profile show [-h] [--json] name`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Lists, shows, or validates EV weighting profiles; profiles cannot relax gates.

**Recommended next step:** Use a valid profile with `benchmark` or `qualify`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | profile name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies profile validate`

validate one weighting profile

**Usage:** `aies profile validate [-h] [--json] name`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Lists, shows, or validates EV weighting profiles; profiles cannot relax gates.

**Recommended next step:** Use a valid profile with `benchmark` or `qualify`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | profile name or YAML path | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies profiles`

deprecated compatibility alias for `profile`

**Usage:** `aies profiles [-h] [--json] {list,show,validate} ...`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Deprecated compatibility alias for the canonical profile resource.

**Recommended next step:** Prefer the canonical `aies profile` surface in new workflows.

### Subcommands

| Subcommand | What it does |
|---|---|
| `list` | list available weighting profiles |
| `show` | show one weighting profile |
| `validate` | validate one weighting profile |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies profiles list`

list available weighting profiles

**Usage:** `aies profiles list [-h] [--json]`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Deprecated compatibility alias for the canonical profile resource.

**Recommended next step:** Prefer the canonical `aies profile` surface in new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies profiles show`

show one weighting profile

**Usage:** `aies profiles show [-h] [--json] name`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Deprecated compatibility alias for the canonical profile resource.

**Recommended next step:** Prefer the canonical `aies profile` surface in new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | profile name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies profiles validate`

validate one weighting profile

**Usage:** `aies profiles validate [-h] [--json] name`

**Prerequisites:** Shipped or supplied weighting profile YAML is available.

**Result and side effects:** Deprecated compatibility alias for the canonical profile resource.

**Recommended next step:** Prefer the canonical `aies profile` surface in new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | profile name or YAML path | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualification`

qualification records (the QUAL-… manifests) and their history

**Usage:** `aies qualification [-h] [--json] {list,show,history,verify,revoke,event} ...`

**Prerequisites:** Qualification Records exist for read operations; lifecycle mutations require a named human authority, reason, and event-specific evidence.

**Result and side effects:** Reads records/history, verifies current validity, or appends immutable governed lifecycle events.

**Recommended next step:** Monitor expiry and conditions or begin reassessment when the record is no longer current.

### Subcommands

| Subcommand | What it does |
|---|---|
| `event` | append an immutable lifecycle event |
| `history` | show immutable qualification lifecycle events |
| `list` | list qualification records |
| `revoke` | append a revocation lifecycle event |
| `show` | show one qualification record |
| `verify` | verify one qualification against current state |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies qualification event`

append an immutable lifecycle event

**Usage:** `aies qualification event [-h] --event {condition-changed,renewed,suspended,invalidated,revoked,superseded} --authority AUTHORITY --reason REASON [--condition CONDITION] [--valid-until ISO-8601] [--superseded-by SUPERSEDED_BY] [--evidence-run EVIDENCE_RUN] [--peer-reviewer PEER_REVIEWER] [--peer-reviewer-id PEER_REVIEWER_ID] [--peer-conflict-free] [--json] record`

**Prerequisites:** Qualification Records exist for read operations; lifecycle mutations require a named human authority, reason, and event-specific evidence.

**Result and side effects:** Reads records/history, verifies current validity, or appends immutable governed lifecycle events.

**Recommended next step:** Monitor expiry and conditions or begin reassessment when the record is no longer current.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RECORD>` | required | qualification record id | — |
| `--event` | required | immutable lifecycle transition to append | choices: `condition-changed`, `renewed`, `suspended`, `invalidated`, `revoked`, `superseded` |
| `--authority` | required | named human authority recording the event | — |
| `--reason` | required | reason for the lifecycle transition | — |
| `--condition` | optional | replacement condition; repeat for multiple conditions | repeatable |
| `--valid-until` | optional | new validity end for a renewal | — |
| `--superseded-by` | optional | replacement qualification record id | Used with the `superseded` event to identify the replacement record. |
| `--evidence-run` | optional | decisional, gate-passing re-evaluation run for renewal | Required for evidence-backed renewal and must identify a decisional, gate-passing reassessment. |
| `--peer-reviewer` | optional | named independent human peer reviewer for renewal | — |
| `--peer-reviewer-id` | optional | durable peer id from `aies rater register` | — |
| `--peer-conflict-free` | optional | peer reviewer declares no conflict with the subject | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualification history`

show immutable qualification lifecycle events

**Usage:** `aies qualification history [-h] [--deployment DEPLOYMENT] [--json]`

**Prerequisites:** Qualification Records exist for read operations; lifecycle mutations require a named human authority, reason, and event-specific evidence.

**Result and side effects:** Reads records/history, verifies current validity, or appends immutable governed lifecycle events.

**Recommended next step:** Monitor expiry and conditions or begin reassessment when the record is no longer current.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--deployment` | optional | filter by deployment id | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualification list`

list qualification records

**Usage:** `aies qualification list [-h] [--json]`

**Prerequisites:** Qualification Records exist for read operations; lifecycle mutations require a named human authority, reason, and event-specific evidence.

**Result and side effects:** Reads records/history, verifies current validity, or appends immutable governed lifecycle events.

**Recommended next step:** Monitor expiry and conditions or begin reassessment when the record is no longer current.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualification revoke`

append a revocation lifecycle event

**Usage:** `aies qualification revoke [-h] --authority AUTHORITY --reason REASON [--json] record`

**Prerequisites:** Qualification Records exist for read operations; lifecycle mutations require a named human authority, reason, and event-specific evidence.

**Result and side effects:** Reads records/history, verifies current validity, or appends immutable governed lifecycle events.

**Recommended next step:** Monitor expiry and conditions or begin reassessment when the record is no longer current.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RECORD>` | required | qualification record id | — |
| `--authority` | required | named human authority recording the revocation | — |
| `--reason` | required | reason for revocation | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualification show`

show one qualification record

**Usage:** `aies qualification show [-h] [--json] record`

**Prerequisites:** Qualification Records exist for read operations; lifecycle mutations require a named human authority, reason, and event-specific evidence.

**Result and side effects:** Reads records/history, verifies current validity, or appends immutable governed lifecycle events.

**Recommended next step:** Monitor expiry and conditions or begin reassessment when the record is no longer current.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RECORD>` | required | qualification record id | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualification verify`

verify one qualification against current state

**Usage:** `aies qualification verify [-h] [--json] record`

**Prerequisites:** Qualification Records exist for read operations; lifecycle mutations require a named human authority, reason, and event-specific evidence.

**Result and side effects:** Reads records/history, verifies current validity, or appends immutable governed lifecycle events.

**Recommended next step:** Monitor expiry and conditions or begin reassessment when the record is no longer current.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RECORD>` | required | qualification record id | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualifications`

deprecated compatibility alias for `qualification`

**Usage:** `aies qualifications [-h] [--json] {list,show,revoke,event} ...`

**Prerequisites:** Qualification Records exist; lifecycle mutations require a named human authority and event-specific evidence.

**Result and side effects:** Deprecated compatibility alias for the canonical qualification resource.

**Recommended next step:** Prefer `aies qualification` for new workflows.

### Subcommands

| Subcommand | What it does |
|---|---|
| `event` | append an immutable lifecycle event |
| `list` | list qualification records |
| `revoke` | append a revocation lifecycle event |
| `show` | show one qualification record |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies qualifications event`

append an immutable lifecycle event

**Usage:** `aies qualifications event [-h] --event {condition-changed,renewed,suspended,invalidated,revoked,superseded} --authority AUTHORITY --reason REASON [--condition CONDITION] [--valid-until ISO-8601] [--superseded-by SUPERSEDED_BY] [--evidence-run EVIDENCE_RUN] [--peer-reviewer PEER_REVIEWER] [--peer-reviewer-id PEER_REVIEWER_ID] [--peer-conflict-free] [--json] record`

**Prerequisites:** Qualification Records exist; lifecycle mutations require a named human authority and event-specific evidence.

**Result and side effects:** Deprecated compatibility alias for the canonical qualification resource.

**Recommended next step:** Prefer `aies qualification` for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RECORD>` | required | qualification record id | — |
| `--event` | required | immutable lifecycle transition to append | choices: `condition-changed`, `renewed`, `suspended`, `invalidated`, `revoked`, `superseded` |
| `--authority` | required | named human authority recording the event | — |
| `--reason` | required | reason for the lifecycle transition | — |
| `--condition` | optional | replacement condition; repeat for multiple conditions | repeatable |
| `--valid-until` | optional | new validity end for a renewal | — |
| `--superseded-by` | optional | replacement qualification record id | — |
| `--evidence-run` | optional | decisional, gate-passing re-evaluation run for renewal | — |
| `--peer-reviewer` | optional | named independent human peer reviewer for renewal | — |
| `--peer-reviewer-id` | optional | durable peer id from `aies rater register` | — |
| `--peer-conflict-free` | optional | peer reviewer declares no conflict with the subject | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualifications list`

list qualification records

**Usage:** `aies qualifications list [-h] [--json]`

**Prerequisites:** Qualification Records exist; lifecycle mutations require a named human authority and event-specific evidence.

**Result and side effects:** Deprecated compatibility alias for the canonical qualification resource.

**Recommended next step:** Prefer `aies qualification` for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualifications revoke`

append a revocation lifecycle event

**Usage:** `aies qualifications revoke [-h] --authority AUTHORITY --reason REASON [--json] record`

**Prerequisites:** Qualification Records exist; lifecycle mutations require a named human authority and event-specific evidence.

**Result and side effects:** Deprecated compatibility alias for the canonical qualification resource.

**Recommended next step:** Prefer `aies qualification` for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RECORD>` | required | qualification record id | — |
| `--authority` | required | named human authority recording the revocation | — |
| `--reason` | required | reason for revocation | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualifications show`

show one qualification record

**Usage:** `aies qualifications show [-h] [--json] record`

**Prerequisites:** Qualification Records exist; lifecycle mutations require a named human authority and event-specific evidence.

**Result and side effects:** Deprecated compatibility alias for the canonical qualification resource.

**Recommended next step:** Prefer `aies qualification` for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RECORD>` | required | qualification record id | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies qualify`

run engineering evaluation for one deployment; formal qualification is explicit

**Usage:** `aies qualify [-h] [--json] [--runtime RUNTIME] [--assessment NAME] [--profile PROFILE] [--rt {1,2,3,4}] [--area AREA] [--all-areas] [--decisional] [--formal-qualification] [--journey JOURNEY_ID] [--judge DEPLOYMENT] [--judge-batch-size N] [--consider-advisory-review] [--human-evaluation NAME] [--reviewer-runtime REVIEWER_RUNTIME] [--repeats REPEATS] [--parallel N] [--resume RUN_ID] [--resume-collection RUN_ID] [model]`

**Prerequisites:** For a new run, the target deployment is registered and reachable. `--judge` requires a reachable reviewer deployment. `--resume` requires scored evidence; `--resume-collection` requires an existing partial run.

**Result and side effects:** Plans and collects evidence; with a judge it also scores, aggregates, and writes the complete evaluation/report bundle.

**Recommended next step:** Inspect `report.html`, run `aies capabilities <run> --ecm`, or begin the separate human qualification workflow.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<MODEL>` | optional | deployment id, or model name | — |
| `--runtime` | optional | disambiguate when a model has several deployments | — |
| `--assessment` | optional | run a declarative assessment (assessments/NAME.yaml): its competency set, profile, risk tier, and sampling (ADR-0005). Authoritative — sets --area/--profile; --rt/--repeats override it | Sets areas and profile; `--rt` and `--repeats` may override the assessment defaults. |
| `--profile` | optional | EV weighting profile (default: enterprise; overridden by --assessment) | default: `enterprise` |
| `--rt` | optional | scoped risk tier (default RT2 — Moderate, or the assessment's tier) | choices: `1`, `2`, `3`, `4` |
| `--area` | optional | competency area (repeatable); default CA-05 | repeatable; Repeatable. Do not combine conceptually with `--all-areas`; an assessment supplies its own areas. |
| `--all-areas` | optional | qualify across ALL competency areas CA-01…CA-12 (a full SDLC capability profile; see `aies capabilities`) | Selects all competency areas and replaces the default CA-05 scope. |
| `--decisional` | optional | require the distinct-scenario plan for every selected area to meet the AESQS sample minimum when admitted ratings are available | Requires enough distinct scenarios; repeats never satisfy breadth. |
| `--formal-qualification` | optional | explicitly run the human-governed formal qualification path; without this flag, automated engineering evaluation is non-blocking | Opt-in only. Without it, the run is a non-blocking engineering evaluation and human evaluation is optional. |
| `--journey` | optional | run a multi-phase journey instead of area suites | — |
| `--judge` | optional | auto-score responses with this judge deployment (or 'self') and print the report directly — no manual scoring. Defaults to $AIES_JUDGE. | Enables automated scoring and complete report generation; automated evidence remains informational for qualification. |
| `--judge-batch-size` | optional | responses per automated judge request (default 8, or $AIES_JUDGE_BATCH_SIZE; automatically bounded by context) | — |
| `--consider-advisory-review` | optional | record that a human considered the automated reviewer scores in the generated report | — |
| `--human-evaluation` | optional | record a named qualitative or scored human evaluation in the generated report | — |
| `--reviewer-runtime` | optional | disambiguate the judge deployment's runtime | — |
| `--repeats` | optional | explicit repeats for a separate stability study; repeats do not substitute for distinct scenario breadth | — |
| `--parallel` | optional | concurrent inference calls for BOTH response collection and judge scoring (default 1, or $AIES_PARALLEL; records are written in canonical order regardless) | — |
| `--resume` | optional | aggregate a scored run into the evidence package | Uses an existing scored run; the model positional argument is not required. |
| `--resume-collection` | optional | fill only the missing responses of a partially-collected run (e.g. after an endpoint failure), then rebuild the scoresheet | Uses an existing partial run and collects only missing responses; the model positional argument is not required. |

## `aies rater`

manage durable human-rater qualification/calibration records

**Usage:** `aies rater [-h] [--json] {register,list,show} ...`

**Prerequisites:** AIES has a writable workspace. Registration requires evidence-backed human qualification, scope, calibration, expiry, and a named registry authority.

**Result and side effects:** Creates or reads durable human-rater qualification/calibration records.

**Recommended next step:** Use registered rater ids in scoresheets, divergence resolution, peer review, and formal qualification.

### Subcommands

| Subcommand | What it does |
|---|---|
| `list` | list registered human raters |
| `register` | register one qualified human rater |
| `show` | show one human-rater record |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies rater list`

list registered human raters

**Usage:** `aies rater list [-h] [--json]`

**Prerequisites:** AIES has a writable workspace. Registration requires evidence-backed human qualification, scope, calibration, expiry, and a named registry authority.

**Result and side effects:** Creates or reads durable human-rater qualification/calibration records.

**Recommended next step:** Use registered rater ids in scoresheets, divergence resolution, peer review, and formal qualification.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies rater register`

register one qualified human rater

**Usage:** `aies rater register [-h] --id ID --name NAME --area CA-NN --rt {1,2,3,4} --qualified-until ISO-8601 --calibration-valid-until ISO-8601 --anchor-version ANCHOR_VERSION [--calibration-method CALIBRATION_METHOD] --registered-by REGISTERED_BY [--json]`

**Prerequisites:** AIES has a writable workspace. Registration requires evidence-backed human qualification, scope, calibration, expiry, and a named registry authority.

**Result and side effects:** Creates or reads durable human-rater qualification/calibration records.

**Recommended next step:** Use registered rater ids in scoresheets, divergence resolution, peer review, and formal qualification.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--id` | required | durable human-rater identifier | — |
| `--name` | required | human rater's display name | — |
| `--area` | required | qualified competency area; repeat for additional areas | repeatable |
| `--rt` | required | qualified risk-tier number; repeat for additional tiers | choices: `1`, `2`, `3`, `4`; repeatable |
| `--qualified-until` | required | qualification expiry timestamp | — |
| `--calibration-valid-until` | required | rating-calibration expiry timestamp | — |
| `--anchor-version` | required | version of the anchor-artifact set used for calibration | — |
| `--calibration-method` | optional | documented calibration method | default: `human-consensus-anchor-session` |
| `--registered-by` | required | named human registry authority | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies rater show`

show one human-rater record

**Usage:** `aies rater show [-h] [--json] id`

**Prerequisites:** AIES has a writable workspace. Registration requires evidence-backed human qualification, scope, calibration, expiry, and a named registry authority.

**Result and side effects:** Creates or reads durable human-rater qualification/calibration records.

**Recommended next step:** Use registered rater ids in scoresheets, divergence resolution, peer review, and formal qualification.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<ID>` | required | durable human-rater identifier | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies registry`

deprecated compatibility alias for `deployment`

**Usage:** `aies registry [-h] [--json] {add,list,show,retire} ...`

**Prerequisites:** AIES has a writable workspace; `add` requires valid deployment YAML.

**Result and side effects:** Deprecated compatibility alias for the canonical deployment resource.

**Recommended next step:** Prefer the canonical `aies deployment` commands for new workflows.

### Subcommands

| Subcommand | What it does |
|---|---|
| `add` | register a candidate deployment from YAML |
| `list` | list active candidate deployments |
| `retire` | retire a deployment without deleting history |
| `show` | show one candidate deployment |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies registry add`

register a candidate deployment from YAML

**Usage:** `aies registry add [-h] [--json] file`

**Prerequisites:** AIES has a writable workspace; `add` requires valid deployment YAML.

**Result and side effects:** Deprecated compatibility alias for the canonical deployment resource.

**Recommended next step:** Prefer the canonical `aies deployment` commands for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<FILE>` | required | deployment YAML file to register | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies registry list`

list active candidate deployments

**Usage:** `aies registry list [-h] [--all] [--json]`

**Prerequisites:** AIES has a writable workspace; `add` requires valid deployment YAML.

**Result and side effects:** Deprecated compatibility alias for the canonical deployment resource.

**Recommended next step:** Prefer the canonical `aies deployment` commands for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--all` | optional | include retired deployment entries | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies registry retire`

retire a deployment without deleting history

**Usage:** `aies registry retire [-h] [--json] model`

**Prerequisites:** AIES has a writable workspace; `add` requires valid deployment YAML.

**Result and side effects:** Deprecated compatibility alias for the canonical deployment resource.

**Recommended next step:** Prefer the canonical `aies deployment` commands for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<MODEL>` | required | deployment id, or an unambiguous model name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies registry show`

show one candidate deployment

**Usage:** `aies registry show [-h] [--json] model`

**Prerequisites:** AIES has a writable workspace; `add` requires valid deployment YAML.

**Result and side effects:** Deprecated compatibility alias for the canonical deployment resource.

**Recommended next step:** Prefer the canonical `aies deployment` commands for new workflows.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<MODEL>` | required | deployment id, or an unambiguous model name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies remediation`

inspect or disposition evidence-linked actions without changing scores

**Usage:** `aies remediation [-h] [--json] {show,history,update} ...`

**Prerequisites:** A completed run or recorded repository audit has a current coverage plan. Updates require a stable ACT-* id and a named accountable owner and authority.

**Result and side effects:** Shows deterministic evidence-linked actions, reads append-only disposition history, or appends a human workflow disposition. It never changes canonical evidence, scores, qualification, or deployment authority.

**Recommended next step:** Collect the stated acceptance evidence and rerun the exact reassessment command; use closed or mitigated only with explicit evidence references, which this command records but does not independently verify.

### Subcommands

| Subcommand | What it does |
|---|---|
| `history` | show append-only named-human action dispositions |
| `show` | show the current remediation and monitoring plan |
| `update` | append a named-human action workflow disposition |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies remediation history`

show append-only named-human action dispositions

**Usage:** `aies remediation history [-h] [--json] reference`

**Prerequisites:** The reference may have zero or more append-only remediation dispositions.

**Result and side effects:** Lists named-human workflow events in durable order without recomputing or changing assessment evidence.

**Recommended next step:** Inspect the current merged plan with `aies remediation show REFERENCE`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<REFERENCE>` | required | run id, repository audit id, or latest | — |
| `--json` | optional | machine-readable output | — |

## `aies remediation show`

show the current remediation and monitoring plan

**Usage:** `aies remediation show [-h] [--format {markdown,json,html}] [--json] reference`

**Prerequisites:** A completed run or recorded repository audit exists.

**Result and side effects:** Renders prioritized gap/finding actions, ownership state, monitoring links, acceptance signals, and reassessment commands.

**Recommended next step:** Select an ACT-* id and use `aies remediation update` only when a named owner is ready to record a disposition.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<REFERENCE>` | required | run id, repository audit id, or latest | — |
| `--format` | optional | rendering format (default: markdown) | choices: `markdown`, `json`, `html`; default: `markdown` |
| `--json` | optional | machine-readable output | — |

## `aies remediation update`

append a named-human action workflow disposition

**Usage:** `aies remediation update [-h] --status {accepted,in-progress,mitigated,closed,deferred} --owner OWNER --authority AUTHORITY --note NOTE [--evidence EVIDENCE] [--json] reference action_id`

**Prerequisites:** The ACT-* id exists in the current generated plan; the named owner has disposition authority. Mitigated or closed states require at least one explicit evidence reference.

**Result and side effects:** Appends a human-attributed workflow event and refreshes run views; repository bundles remain immutable and must be written to a new directory.

**Recommended next step:** Verify the merged plan, retain closure evidence, and execute the action's exact reassessment command after material change.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<REFERENCE>` | required | run id, repository audit id, or latest | — |
| `<ACTION_ID>` | required | stable ACT-* id from remediation show | — |
| `--status` | required | new workflow status; mitigated/closed require --evidence | choices: `accepted`, `in-progress`, `mitigated`, `closed`, `deferred` |
| `--owner` | required | named accountable action owner | — |
| `--authority` | required | basis for this person's action-disposition authority | — |
| `--note` | required | reason or disposition note | — |
| `--evidence` | optional | closure/mitigation evidence reference; repeat as needed | repeatable |
| `--json` | optional | machine-readable output | — |

## `aies report`

render an evidence package

**Usage:** `aies report [-h] [--json] [--format {markdown,json,html}] [--write] run`

**Prerequisites:** The run has been aggregated into an evidence package.

**Result and side effects:** Renders the evidence package; `--write` stores the chosen view beside the run.

**Recommended next step:** Use ECM/guidance for engineering decisions or the governed grant workflow for qualification.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | aggregated run id whose evidence package will be rendered | — |
| `--format` | optional | output representation (default: markdown) | choices: `markdown`, `json`, `html`; default: `markdown` |
| `--write` | optional | write the report into the run directory instead of stdout | — |

## `aies resolve`

record an immutable human disposition for a divergent item

**Usage:** `aies resolve [-h] [--json] --scores EV1 EV2 EV3 EV4 EV5 EV6 --resolver RESOLVER --resolver-id RESOLVER_ID --rationale RATIONALE --conflict-free run response`

**Prerequisites:** The response has a material rater divergence and the named resolver is a registered, qualified, conflict-free human.

**Result and side effects:** Appends an immutable resolved disposition; it does not overwrite the original ratings.

**Recommended next step:** Re-run report/assessment rendering and complete any remaining protocol gaps.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | run id containing the divergent response | — |
| `<RESPONSE>` | required | response record filename, for example SC-CA05-001-r1.json | — |
| `--scores` | required | six resolved integer ratings in EV1 through EV6 order | choices: `0`, `1`, `2`, `3`, `4`; values: 6 |
| `--resolver` | required | named human resolver | — |
| `--resolver-id` | required | durable id from `aies rater register` | — |
| `--rationale` | required | reasoned human disposition explaining the resolution | — |
| `--conflict-free` | required | declare independence from the assessed subject | — |

## `aies review`

assemble a multi-deployment peer-review package

**Usage:** `aies review [-h] [--json] [--reviewer REVIEWER] [--model-reviewer DEPLOYMENT] [--reviewer-runtime REVIEWER_RUNTIME] [--parallel N] [--judge-batch-size N] [--reviewer-qualified] [--calibration CALIBRATION] [--consider-advisory-review] [--human-evaluation NAME] run`

**Prerequisites:** A collected run exists. `--model-reviewer` requires a registered reviewer deployment; qualification/calibration flags must be evidence-backed.

**Result and side effects:** Records model-review scores, completes or refreshes engineering analysis, and keeps optional human evaluation separately visible.

**Recommended next step:** Inspect engineering results; resolve material findings only when needed, and use formal qualification separately.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | run id whose responses will be reviewed | — |
| `--reviewer` | optional | label for the reviewer model | default: `reviewer-model` |
| `--model-reviewer` | optional | drive this reviewer deployment to score the responses before assembling the package | Required for live reviewer inference; without it the command assembles from existing review evidence. |
| `--reviewer-runtime` | optional | disambiguate the reviewer deployment's runtime | — |
| `--parallel` | optional | concurrent reviewer calls when using --model-reviewer (default 1, or $AIES_PARALLEL) | Controls concurrent reviewer requests. It is independent of judge batch size; `--parallel 1` means one active batch request. |
| `--judge-batch-size` | optional | responses per reviewer request (default 8, or $AIES_JUDGE_BATCH_SIZE; automatically bounded by context) | Controls the maximum responses inside each reviewer request (default 8 or AIES_JUDGE_BATCH_SIZE, then bounded by context). |
| `--reviewer-qualified` | optional | the reviewer holds a current review-class (CA-06) qualification | A declaration that must be supported by a current CA-06 — Testing, Quality & Evaluation Engineering qualification. |
| `--calibration` | optional | JSON {model:[...], human_anchor:[...]} for bootstrap calibration | Bootstrap evidence for an otherwise unqualified reviewer; does not make model ratings human qualification evidence. |
| `--consider-advisory-review` | optional | record that a human considered the advisory automated-review scores | — |
| `--human-evaluation` | optional | record a named qualitative or scored human evaluation; no grant required | — |

## `aies runs`

list runs or inspect one run and its durable progress

**Usage:** `aies runs [-h] [--json] {list,show,progress,events,import,imports,cohorts} ...`

**Prerequisites:** The workspace contains runs, or `runs import` is given a readable run directory/ZIP; progress requires durable `progress.json`, while event migration requires retained source records.

**Result and side effects:** Lists history and imports, shows a versioned run summary or progress, discovers comparison-compatible cohorts, and validates/replays typed evidence events.

**Recommended next step:** Import with `--dry-run` first, then use `runs show RUN` and `runs cohorts` to discover safe next actions.

### Subcommands

| Subcommand | What it does |
|---|---|
| `cohorts` | discover exact protocol-compatible deployment-run cohorts |
| `events` | validate and replay typed events, or append a legacy-run projection |
| `import` | verify and immutably import one run directory or ZIP package |
| `imports` | list append-only cross-machine import receipts |
| `list` | list recorded runs |
| `progress` | show detailed durable progress for a run |
| `show` | show one versioned read-only run summary and artifact index |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies runs cohorts`

discover exact protocol-compatible deployment-run cohorts

**Usage:** `aies runs cohorts [-h] [--model MODEL] [--profile PROFILE] [--rt {1,2,3,4}] [--minimum-runs N] [--json]`

**Prerequisites:** Aggregated deployment runs exist; optional model, profile, and risk-tier filters narrow discovery.

**Result and side effects:** Groups runs by the exact subject, risk, profile, suite, mapping, scoring, rater, repeat, and Evidence Adapter compatibility signature and emits connected 2–5-run comparison commands.

**Recommended next step:** Run a printed `aies compare` command; separately verify independence and decision relevance because protocol compatibility is not representativeness.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--model` | optional | filter by deployment id or model identifier | — |
| `--profile` | optional | filter by assessment profile id | — |
| `--rt` | optional | filter by risk tier: 1 Minimal, 2 Moderate, 3 Significant, 4 Critical | choices: `1`, `2`, `3`, `4` |
| `--minimum-runs` | optional | minimum compatible runs per returned cohort (default: 2) | default: `2` |
| `--json` | optional | emit machine-readable cohorts and commands | — |

## `aies runs events`

validate and replay typed events, or append a legacy-run projection

**Usage:** `aies runs events [-h] [--migrate] [--json] run`

**Prerequisites:** The workspace contains runs, or `runs import` is given a readable run directory/ZIP; progress requires durable `progress.json`, while event migration requires retained source records.

**Result and side effects:** Lists history and imports, shows a versioned run summary or progress, discovers comparison-compatible cohorts, and validates/replays typed evidence events.

**Recommended next step:** Import with `--dry-run` first, then use `runs show RUN` and `runs cohorts` to discover safe next actions.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RUN>` | required | run id whose evidence events will be replayed | — |
| `--migrate` | optional | append typed projections of legacy records; never rewrites source evidence | — |
| `--json` | optional | emit events and deterministic replay as JSON | — |

## `aies runs import`

verify and immutably import one run directory or ZIP package

**Usage:** `aies runs import [-h] [--dry-run] [--json] source`

**Prerequisites:** A readable directory or ZIP contains exactly one valid AIES `manifest.json`; the destination workspace is writable.

**Result and side effects:** Bounds and validates archive extraction, rejects traversal/symlinks/collisions, excludes disposable archive metadata, verifies every admitted byte, never overwrites an existing run, and appends a source-bound receipt.

**Recommended next step:** Start with `aies runs import PATH --dry-run`; after import use `aies runs show RUN` and retain the receipt exposed by `aies runs imports`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<SOURCE>` | required | run directory, archive wrapper directory, or ZIP package | — |
| `--dry-run` | optional | validate identity, safety, digests, and destination without writing | — |
| `--json` | optional | emit the import plan or receipt as JSON | — |

## `aies runs imports`

list append-only cross-machine import receipts

**Usage:** `aies runs imports [-h] [--json]`

**Prerequisites:** The workspace may contain append-only run-import receipts.

**Result and side effects:** Lists source-bound import receipts with run identity, status, file count, timestamp, and package-tree digest; it changes no state.

**Recommended next step:** Inspect the imported run with `aies runs show RUN` or retrieve a receipt through `GET /run-imports/{id}`.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit the import-receipt index as JSON | — |

## `aies runs list`

list recorded runs

**Usage:** `aies runs list [-h] [--model MODEL] [--json]`

**Prerequisites:** The workspace contains runs, or `runs import` is given a readable run directory/ZIP; progress requires durable `progress.json`, while event migration requires retained source records.

**Result and side effects:** Lists history and imports, shows a versioned run summary or progress, discovers comparison-compatible cohorts, and validates/replays typed evidence events.

**Recommended next step:** Import with `--dry-run` first, then use `runs show RUN` and `runs cohorts` to discover safe next actions.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--model` | optional | filter by deployment id or model identifier | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies runs progress`

show detailed durable progress for a run

**Usage:** `aies runs progress [-h] [--json] run`

**Prerequisites:** The workspace contains runs, or `runs import` is given a readable run directory/ZIP; progress requires durable `progress.json`, while event migration requires retained source records.

**Result and side effects:** Lists history and imports, shows a versioned run summary or progress, discovers comparison-compatible cohorts, and validates/replays typed evidence events.

**Recommended next step:** Import with `--dry-run` first, then use `runs show RUN` and `runs cohorts` to discover safe next actions.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RUN>` | required | run id whose durable progress will be shown | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies runs show`

show one versioned read-only run summary and artifact index

**Usage:** `aies runs show [-h] [--json] run`

**Prerequisites:** The workspace contains runs, or `runs import` is given a readable run directory/ZIP; progress requires durable `progress.json`, while event migration requires retained source records.

**Result and side effects:** Lists history and imports, shows a versioned run summary or progress, discovers comparison-compatible cohorts, and validates/replays typed evidence events.

**Recommended next step:** Import with `--dry-run` first, then use `runs show RUN` and `runs cohorts` to discover safe next actions.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<RUN>` | required | run id to inspect | — |
| `--json` | optional | emit the aies-run-view JSON contract | — |

## `aies runtime`

inspect runtime adapters and the runtimes behind them

**Usage:** `aies runtime [-h] [--json] {list,inspect} ...`

**Prerequisites:** AIES is installed; runtime inspection may depend on locally installed runtime software.

**Result and side effects:** Lists or inspects runtime adapters without changing assessment evidence.

**Recommended next step:** Use `aies discover` to register deployments served by available runtimes.

### Subcommands

| Subcommand | What it does |
|---|---|
| `inspect` | inspect one runtime adapter |
| `list` | list installed runtime adapters |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies runtime inspect`

inspect one runtime adapter

**Usage:** `aies runtime inspect [-h] [--json] name`

**Prerequisites:** AIES is installed; runtime inspection may depend on locally installed runtime software.

**Result and side effects:** Lists or inspects runtime adapters without changing assessment evidence.

**Recommended next step:** Use `aies discover` to register deployments served by available runtimes.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<NAME>` | required | runtime adapter name | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies runtime list`

list installed runtime adapters

**Usage:** `aies runtime list [-h] [--json]`

**Prerequisites:** AIES is installed; runtime inspection may depend on locally installed runtime software.

**Result and side effects:** Lists or inspects runtime adapters without changing assessment evidence.

**Recommended next step:** Use `aies discover` to register deployments served by available runtimes.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies score`

ingest a filled scoresheet (human or model rater)

**Usage:** `aies score [-h] [--json] [--file FILE] run`

**Prerequisites:** A collected run and completed scoresheet exist; human qualification ratings require registered, in-scope, currently calibrated rater metadata.

**Result and side effects:** Ingests rating observations, aggregates the engineering evaluation, and refreshes the complete report bundle in one command.

**Recommended next step:** Inspect the generated report; human evaluation is optional unless formal qualification was explicitly requested.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | run id whose completed scoresheet will be ingested | — |
| `--file` | optional | scoresheet path (default: the run's scoresheet.json) | — |

## `aies serve`

thin read-only REST API over versioned views and stored canonical artifacts (JSON; computes no outcomes)

**Usage:** `aies serve [-h] [--json] [--host HOST] [--port PORT]`

**Prerequisites:** The workspace contains artifacts to expose; choose a safe bind address.

**Result and side effects:** Starts a read-only API exposing shared `/overview` and `/runs/{id}` view models plus stored canonical decision products; it computes no new decisions.

**Recommended next step:** Stop the process when finished; use an authenticated reverse proxy before any non-local exposure.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `--host` | optional | interface to bind (default: 127.0.0.1; use broader binds cautiously) | default: `127.0.0.1` |
| `--port` | optional | TCP port for the read-only API (default: 8722) | default: `8722` |

## `aies snapshot`

show evidence, capability, scenario breadth, assurance, and engineering decisions

**Usage:** `aies snapshot [-h] [--json] [--observed-only] [--sort {task,performance,breadth,evidence,status}] [--ascending] [run]`

**Prerequisites:** A completed run has an Engineering Capability Matrix; `latest` selects the newest workspace run.

**Result and side effects:** Prints the responsive Evidence → Capability → Confidence → Engineering Decisions view. It reuses canonical ECM and Engineering Fit facts and creates no new score or authority.

**Recommended next step:** Open the linked report for detail, inspect `aies capabilities <run>`, or compare only compatible runs.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | optional | completed run id or 'latest' (default: latest) | default: `latest` |
| `--observed-only` | optional | hide tasks without directly mapped scored evidence | Hides unassessed task rows from the table; the coverage summary still reports them as unknown rather than zero. |
| `--sort` | optional | sort task rows (default: performance) | choices: `task`, `performance`, `breadth`, `evidence`, `status`; default: `performance`; Orders task rows by task, observed performance, scenario breadth, distinct evidence, or engineering status; default is strongest observed performance first. |
| `--ascending` | optional | sort from low to high; unknown tasks remain last | Reverses the selected sort while keeping unassessed tasks at the end instead of misrepresenting unknown as a low score. |

## `aies starter`

choose a decision-led evaluation, comparison, audit, or governance workflow

**Usage:** `aies starter [-h] [--json] {list,show} ...`

**Prerequisites:** AIES is installed; listing and showing starters require no workspace or endpoint.

**Result and side effects:** Reads versioned decision-led workflow data covering prerequisites, command sequence, time/cost class, evidence breadth, artifacts, limitations, and next expansion.

**Recommended next step:** Choose a starter with `aies starter show <id>`, replace its placeholders deliberately, and run plan-only before any model calls.

### Subcommands

| Subcommand | What it does |
|---|---|
| `list` | list the shipped decision-oriented starters |
| `show` | show prerequisites, commands, artifacts, and limitations |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies starter list`

list the shipped decision-oriented starters

**Usage:** `aies starter list [-h] [--json]`

**Prerequisites:** AIES is installed.

**Result and side effects:** Lists the shipped decision starters and the decision, subject kind, and workflow each supports.

**Recommended next step:** Run `aies starter show <id>` for the executable sequence and boundaries.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies starter show`

show prerequisites, commands, artifacts, and limitations

**Usage:** `aies starter show [-h] [--json] starter_id`

**Prerequisites:** Use an id from `aies starter list`.

**Result and side effects:** Prints the complete versioned workflow without executing commands or incurring cost.

**Recommended next step:** Resolve the prerequisites, replace placeholders, and execute the plan-only command before the live workflow.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<STARTER_ID>` | required | starter id from `aies starter list` | — |
| `--json` | optional | machine-readable output | — |

## `aies suites`

inspect and validate competency suites

**Usage:** `aies suites [-h] [--json] {validate,calibrate,empirical} ...`

**Prerequisites:** The shipped or selected competencies directory is readable.

**Result and side effects:** Validates suite structure or reports design/empirical calibration maturity.

**Recommended next step:** Fix validation errors before runs; use a preregistered panel for empirical promotion evidence.

### Subcommands

| Subcommand | What it does |
|---|---|
| `calibrate` | calibration-coverage report — how far each scenario has progressed as a measurement instrument (CALIBRATION.md); advisory, never fails |
| `empirical` | analyze a model panel for per-scenario discrimination/repeatability/twin-robustness (CALIBRATION.md Phase 2). Give a panel JSON, or assemble one from scored runs with --runs |
| `validate` | validate suite YAML structure and coverage |

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |

## `aies suites calibrate`

calibration-coverage report — how far each scenario has progressed as a measurement instrument (CALIBRATION.md); advisory, never fails

**Usage:** `aies suites calibrate [-h] [--root ROOT] [--json]`

**Prerequisites:** The shipped or selected competencies directory is readable.

**Result and side effects:** Validates suite structure or reports design/empirical calibration maturity.

**Recommended next step:** Fix validation errors before runs; use a preregistered panel for empirical promotion evidence.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--root` | optional | competencies directory to inspect (default: shipped suites) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies suites empirical`

analyze a model panel for per-scenario discrimination/repeatability/twin-robustness (CALIBRATION.md Phase 2). Give a panel JSON, or assemble one from scored runs with --runs

**Usage:** `aies suites empirical [-h] [--runs RUN_ID=ABILITY [RUN_ID=ABILITY ...]] [--preflight-runs RUN_ID [RUN_ID ...]] [--ability-basis ABILITY_BASIS] [--preregistered-at PREREGISTERED_AT] [--rating-protocol-basis RATING_PROTOCOL_BASIS] [--create-plan PATH] [--panel-plan PATH] [--plan-subjects SUBJECT=ABILITY [SUBJECT=ABILITY ...]] [--planned-runs SUBJECT=RUN_ID [SUBJECT=RUN_ID ...]] [--plan-owner PLAN_OWNER] [--plan-areas CA-## [CA-## ...]] [--plan-rt {1,2,3,4}] [--plan-repeats PLAN_REPEATS] [--rating-protocol-id RATING_PROTOCOL_ID] [--write-panel WRITE_PANEL] [--panel-id PANEL_ID] [--json] [panel]`

**Prerequisites:** For promotion-capable analysis, create a frozen plan before runs, use independent subject ability ranks, bind completed compatible runs, and use a validated shared rating protocol.

**Result and side effects:** Analyzes scenario discrimination, repeatability, and twin robustness; exploratory inputs remain non-promotional.

**Recommended next step:** Have a human review the result and record any instrument-promotion decision.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `<PANEL>` | optional | panel-results JSON (panel + per-model scores) | — |
| `--runs` | optional | assemble the panel from scored qualify runs, e.g. --runs run-strong=3 run-mid=2 run-weak=1 | values: + |
| `--preflight-runs` | optional | inspect scored runs for panel compatibility without inventing or requiring ability ranks | values: + |
| `--ability-basis` | optional | independent evidence used to assign every --runs ability rank | — |
| `--preregistered-at` | optional | timestamp showing ability ranks were fixed before analysis | — |
| `--rating-protocol-basis` | optional | evidence that the shared scoring protocol is validated | — |
| `--create-plan` | optional | write a frozen empirical panel plan before running subjects | Planning mode; use before subject runs with `--plan-subjects`, owner, areas, tier, repeats, and rating protocol. |
| `--panel-plan` | optional | frozen panel plan to bind to completed --planned-runs | Analysis mode; bind the frozen plan to completed runs with `--planned-runs`. |
| `--plan-subjects` | optional | subjects and independent ability ranks to freeze | values: + |
| `--planned-runs` | optional | bind every planned subject to its completed run | values: + |
| `--plan-owner` | optional | named human accountable for the frozen study design | — |
| `--plan-areas` | optional | competency areas whose exact instruments are frozen | values: + |
| `--plan-rt` | optional | risk tier frozen in a new plan (default: 2) | choices: `1`, `2`, `3`, `4`; default: `2` |
| `--plan-repeats` | optional | repeat observations per instrument for stability (default: 3) | default: `3` |
| `--rating-protocol-id` | optional | expected rating protocol as KIND:RATER | — |
| `--write-panel` | optional | also write the assembled panel JSON to this path | — |
| `--panel-id` | optional | name this panel for traceability (recorded in the result metadata) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies suites validate`

validate suite YAML structure and coverage

**Usage:** `aies suites validate [-h] [--root ROOT] [--json]`

**Prerequisites:** The shipped or selected competencies directory is readable.

**Result and side effects:** Validates suite structure or reports design/empirical calibration maturity.

**Recommended next step:** Fix validation errors before runs; use a preregistered panel for empirical promotion evidence.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--root` | optional | competencies directory to validate (default: shipped suites) | — |
| `--json` | optional | emit machine-readable JSON | — |

## `aies support`

show implemented, experimental, and planned subject support

**Usage:** `aies support [-h] [--json] [--status {implemented,experimental,planned}] [subject_kind]`

**Prerequisites:** AIES is installed; no workspace, endpoint, or credential is required.

**Result and side effects:** Reads the shipped subject-support registry and distinguishes executable support from experimental contracts and planned architecture.

**Recommended next step:** Use an implemented entry point, or consult the roadmap before proposing an executor, evidence adapter, and direct instruments for a planned subject.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<SUBJECT_KIND>` | optional | subject id or alias to inspect (default: show all) | — |
| `--status` | optional | filter by support status | choices: `implemented`, `experimental`, `planned` |

## `aies transcript`

read a whole run in one view: task + answer + scores per item

**Usage:** `aies transcript [-h] [--json] [--area AREA] [--format {markdown,json}] [--write] run`

**Prerequisites:** The run contains response records; scores are shown when available.

**Result and side effects:** Renders task, response, scores, and findings together for review.

**Recommended next step:** Use findings to complete ratings, resolve divergence, or plan remediation.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RUN>` | required | run id to render as a task/answer/score transcript | — |
| `--area` | optional | only this competency area | — |
| `--format` | optional | output representation (default: markdown) | choices: `markdown`, `json`; default: `markdown` |
| `--write` | optional | write transcript.md into the run directory | — |

## `aies verify`

verify a grant against the current environment (D7); invalidates on fingerprint change

**Usage:** `aies verify [-h] [--json] record`

**Prerequisites:** A Qualification Record exists.

**Result and side effects:** Checks current validity, lifecycle status, and deployment-fingerprint continuity; it does not mutate the record.

**Recommended next step:** Requalify or append the appropriate governed lifecycle event when verification fails.

### Parameters and options

| Parameter | Requirement | Details | Constraints and interactions |
|---|---|---|---|
| `-h`, `--help` | optional | show this help message and exit | — |
| `--json` | optional | machine-readable output | — |
| `<RECORD>` | required | qualification record id to verify | — |

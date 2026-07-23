# AIES Engineering Assessment Platform

| | |
|---|---|
| **Document ID** | AIES-PLAT-00 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Contributors & maintainers |

The `aies` command-line tool: the executable reference implementation of the
[AESQS](../AESQS/README.md) qualification methodology. Specification:
[AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md). Platform-identity
proposal: [ADR-0009](../adr/ADR-0009-Engineering-Assessment-Platform-Identity.md).

The current executable subject adapters assess AI deployments and repositories.
Canonical evidence, ECM, and decision-product boundaries are subject-neutral so
future adapters can assess agents, MCP servers, RAG systems, pipelines, and
platforms without redefining the product.

Run `aies support` or read the generated
[Subject Support Matrix](SUBJECT_SUPPORT.md) for the canonical implemented,
experimental, and planned boundary. Architecture intent is never represented
as shipped assessment support.

**Capability scope is explicit.** A run assesses one risk tier (RT1 — Minimal through RT4 — Critical).
`--all-areas` expands coverage across competency areas only at that selected
tier; it is not an all-tier claim. ECM rows marked `not assessed` mean no
mapped scored evidence exists for that task, not that the subject failed it.

**The platform prepares evidence; it never grants.** A human qualification
authority records every grant (PLATFORM.md D8). Output is always scoped —
per-competency-area competency levels and per-tier autonomy envelopes —
never a global "production ready" verdict (D4).

**Engineering evaluation is the default and does not require human review.**
Automated scores can complete benchmarking, scoring, analysis, a named
Engineering Assessment Result, the ECM, Grounding Diagnostics, Engineering Fit
Guidance, and the complete report bundle. Human evaluation is an optional,
separately displayed assurance input. Only an explicitly requested
`--formal-qualification` run applies the human-gated qualification decision
protocol; grants remain human decisions.

**Milestones M1–M4 shipped** (see [PLATFORM.md §10](../docs/PLATFORM.md)) —
the full pipeline is runnable end to end:
`doctor` (runtime-aware), `discover`, `registry`/`deployment` (incl. `update`,
`remove`, `verify-artifact` for supply-chain provenance), `qualify` (with
`--parallel`, `--judge` auto-scoring, `--journey`, `--all-areas`), `score`,
`import` (external eval results), `report` (complete linked Markdown/JSON/HTML
bundle: Engineering Evaluation Report, ECM, Grounding Diagnostics, Engineering
Fit Guidance, and Executive Summary), `transcript`,
`snapshot` (responsive terminal evidence-to-decision view),
`capabilities` (task-mapped ECM by default; `--qualification-profile` selects
the formal per-area CL/autonomy view), `judge` (available/list/history),
`assessment` (declarative engineering composition — list/show/validate/result,
Markdown/JSON/HTML, ADR-0005), `audit` (repository conformance — maturity per
area, ADR-0004), `ci audit` (retained advisory-by-default CI evidence with
explicit opt-in enforcement), `corpus` (the platform reviews its **own** assessment corpus —
health/coverage/duplicates/review; advisory, multidimensional, no single grade),
`runs`, `compare`, `index`, `review`, `grant`, `verify`, `journey`,
`conform`, `runtime`/`profile`/`qualification`, `overview`, `dashboard`,
`plugins`.
`completion` generates parser-derived PowerShell, Bash, and Zsh Tab completion.
`support` exposes the same subject-support registry through CLI and `/support`
API output.
`overview` exposes the same versioned, informational workspace summary through
CLI JSON/human output, `GET /overview`, and the HTML dashboard. This is the
stable consumer boundary for integrations and a future frontend; it computes
no assessment outcome.
`runs show <run-id>` and `GET /runs/{id}` provide the corresponding
`aies-run-view` detail contract: subject and human-readable scope, durable
execution state, available decision-product summaries, artifact storage
classes, and exact JSON links. Stored ECM, guidance, report, diagnostics,
executive summary, evaluation, and bundle artifacts have dedicated read-only
endpoints; missing artifacts remain explicitly unavailable.
All twelve competency areas
(CA-01…CA-12) ship demonstration suites; six weighting profiles; a
frozen v1.0 runtime-adapter contract with an
[out-of-tree adapter example](examples/external_adapter/README.md);
conformance tests run in CI.

**New here?** [GUIDE.md](GUIDE.md) has the whole-system architecture diagram,
component wiring, and step-by-step setup + real-model run instructions.
[CLI_REFERENCE.md](CLI_REFERENCE.md) is generated from the live parser and
documents every command, subcommand, positional parameter, option, default,
choice, prerequisite, interaction, result/side effect, recommended next step,
and common command sequence.
See also [DEPLOYMENTS.md](DEPLOYMENTS.md) (qualify deployments, not models),
[PROFILES.md](PROFILES.md) (the weighting presets),
[RUNTIMES.md](RUNTIMES.md) (the runtime interface and shipped adapters), and
[JOURNEYS.md](JOURNEYS.md) (multi-phase scenarios that test lifecycle depth),
[SCENARIOS.md](SCENARIOS.md) (how to author competency scenarios), and
[ASSESSMENTS.md](ASSESSMENTS.md) (declarative qualification composition).
[CI_INTEGRATION.md](CI_INTEGRATION.md) provides the reusable pinned workflow,
annotations, retained artifacts, and explicit enforcement sequence.
[CONTAINER.md](CONTAINER.md) covers the non-root demo/audit/conformance image,
mounts, network/secrets boundaries, architecture support, and cleanup.
[REFERENCE.md](REFERENCE.md) is the compact platform reference — vocabulary,
artifact schemas, and command contracts. [CALIBRATION.md](CALIBRATION.md) covers scenario
calibration — treating each scenario as a *measurement instrument* — and the
platform reviews its **own** corpus for calibration, coverage, behavioral
diversity, duplication, and empirical maturity via `aies corpus`
(advisory, multidimensional, never a single grade, never a gate — it critiques,
a human decides).
Hit a snag? [TROUBLESHOOTING.md](TROUBLESHOOTING.md) covers the common
endpoint, TLS, auth, performance, and judge issues.

**Default engineering cycle:** `discover` → `qualify --judge` → completed
Engineering Assessment Result + ECM + diagnostics + Engineering Fit Guidance +
reports. No human step is required. `score`, `review --model-reviewer`, and
`import` also refresh the complete bundle in their own command.

**Optional formal cycle:** start with `qualify --formal-qualification`, complete
the governed human-rater protocol, then `grant` lets a **named human authority**
record the decision and `verify` re-checks its environment fingerprint. The
platform itself never grants.

## Install

```
cd platform
python -m venv .venv
# PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .       # installs `aies` inside the environment
pytest tests/ -q --durations=15  # conformance + ranked performance feedback
aies suites validate      # suites + shipped assessments (one gate; CI runs it)
```

Do not use `--break-system-packages`. `pipx install .` and `uv tool install .`
are optional isolated alternatives for users who already have those tools.

First useful result:

```
aies demo --open
```

The installed command is cross-platform and needs no API key, model server,
Make, or Bash. For a real deployment, use the guided path:

```
aies init
aies support
aies starter show understand-deployment
aies discover
aies evaluate <deployment> --judge <reviewer> --plan-only
aies evaluate <deployment> --judge <reviewer> --parallel 4
aies snapshot latest
aies open latest
```

The warm-cache full-suite performance budget on the recorded Windows reference
workstation is **180 seconds**. The current 298-test baseline is **115.39
seconds**. A run above budget or a greater-than-25% regression should be
profiled before merge; use the ranked durations rather than guessing. Scenario
YAML and suite digests are cached by path, modification time, and size, return
isolated values, and invalidate automatically when an instrument changes.

Artifacts are written to `./aies-workspace` (override with the
`AIES_WORKSPACE` environment variable). Everything persisted is plain
YAML/JSON: diffable, reviewable, tool-independent.

## See the whole thing run (one command, fully offline)

```
aies demo --open # cross-platform installed-CLI trial (recommended)
make demo        # contributor compatibility path (or: bash scripts/demo.sh)
make demo-full   # comprehensive one-process tour of the whole platform
```

`make demo` runs the **core engineering workflow** against the mock runtime:
discover, compose, collect, auto-score, render a COMPLETE Engineering Assessment
Result, show the ECM and Engineering Fit Guidance, and produce Markdown/JSON/HTML
reports. Human evaluation is optional and does not block any stage.

`make demo-full` is the optimized **one-process comprehensive tour** (about 16
seconds on the recorded Windows baseline): the three subjects AIES can
assess (a model deployment via `qualify`, a repository via `audit`, and the
standard itself via `conform engine`), the calibrated measurement instruments,
a completed automated Engineering Evaluation with optional human-evaluation
status, actionable engineering fit, and the Phase-2 empirical harness. Formal
qualification is identified as a separate available workflow, not run as a
failure-oriented demo stage.

No GPU, no API key, no network. It's **executable documentation** — the core
path is CI-gated as [`tests/test_demo.py`](tests/test_demo.py) and the
comprehensive script runs in CI too. For a real deployment,
`make integration-demo DEPLOYMENT=… JUDGE=…`.

## Quickstart (fully offline)

```
aies doctor                    # validate environment/runtime; inventory workspace debris read-only
aies discover                  # register the deployments each runtime serves
aies deployment list          # see the named deployments (e.g. mock-mock-small)

aies qualify <deployment> --profile enterprise --rt 2 --all-areas \
  --judge <judge> --parallel 4
                              # collect, score, analyze, and report in one command
# `benchmark` has the same non-blocking automated path:
aies benchmark <deployment> --all-areas --judge <judge> --parallel 4
aies assessment result <run-id>  # COMPLETE/PARTIAL engineering result; exit 0
aies capabilities <run-id>       # ECM task strengths, gaps, breadth, assurance
aies guidance <run-id>           # Engineering Fit Guidance
aies report <run-id> --format html --write

# Optional manual/imported rating paths also finish their own bundle:
aies score <run-id>                # ingest + aggregate + report
aies import <run-id> external.json # import + aggregate + report

# Only when formal qualification is actually intended:
aies qualify <deployment> ... --formal-qualification
aies assessment result <run-id> --formal-qualification

aies runs list                # result history
aies runs show <run-id>       # versioned run summary + artifact index
aies runs progress <run-id>   # durable live stage, %, elapsed, rate, ETA, failures
aies compare <dep-a> <dep-b>  # compatible observed ECM task comparison
aies suites validate          # validate suite catalog before publishing changes
```

Long-running collection and judge-review commands continuously display the
current stage, completed/total work, percentage, stage and command elapsed
time, throughput, ETA,
failure count, and current scenario or batch. The same state is written to the
run's `progress.json`, so another terminal can inspect it with
`aies runs progress <run-id>` even if the original CLI is still running.
Progress is implicit in `qualify`, `benchmark`, `qualify --resume`, `review`,
and `score`;
the separate `runs progress` command is only an optional second-terminal view.
The live line identifies the current human-readable scenario family and
calibrated task objective with its ordinal—for example, `Executing task 2/30:
Performance Optimization — Remove event-loop blocking […]`. Judge progress
identifies the task currently being scored across EV1 — Correctness through
EV6 — Traceability. Judge output distinguishes active **batches** from worker
capacity: `--parallel N` controls concurrent judge requests, while
`--judge-batch-size N` controls the maximum responses inside each request
(default 8 or `AIES_JUDGE_BATCH_SIZE`, then context-bounded). Parallel
execution reports the dynamic active set and effective capacity; neither value
is hard-coded. Completed judge batches are saved immediately and reused by a
later review.
Interactive terminals receive a one-second heartbeat during long inference
calls, with a terminal-width-bounded active-task line. ETA is labelled as
calculating until the first measured completion (or uses an explicitly
declared deployment estimate), then updates from observed throughput.
Standalone review/resume/score commands reset `command elapsed`; they do not
inherit the age of the stored run. Existing work is excluded from the rate,
and slow throughput is rendered as items/minute rather than a misleading
rounded items/second value.
Semantic color highlights stage, progress, ETA state, failures, and active
capacity without replacing their text labels; `NO_COLOR=1` disables color.

An automated judge can complete an **Engineering Evaluation** and generate the
entire report/ECM bundle without human review. Reports display `Human
evaluation: ☐ Not reviewed (optional)` until a named human evaluation is
recorded, then display it as reviewed. This optional status never blocks the
engineering evaluation. Formal qualification and grants remain a separate,
human-governed protocol under ADR-0012.

Structured reviewers also produce **Grounding Diagnostics** for unsupported
assertions, fabricated APIs/entities, invalid citations/provenance, false
success/test claims, and appropriate abstention. The report keeps automated
and optional human observations separate. Its observed grounding reliability
is descriptive only: unavailable coverage is never shown as zero
hallucinations, and the diagnostic cannot change EV scores or qualification
gates.

**Qualify deployments, not bare models** (PLATFORM.md D11). A deployment
is the named tuple of model × runtime × config × endpoint; `aies discover`
finds them by probing runtimes, or hand-author one (schema in
[PLATFORM.md §5.1](../docs/PLATFORM.md)):

```
id: local-qwen
runtime: openai-compat          # any OpenAI-compatible local server or provider
model: <server-side model name>
runtime_config: { base_url: http://localhost:PORT/v1, model: <name> }
context_window: 32768
provenance: { source: local, checksum: sha256:<artifact checksum> }
```

When a model name maps to several deployments, pass `--runtime` or use the
deployment id — the platform never guesses.

**Built-in runtime adapters:** `ollama`, `lmstudio`, `llamacpp`, `mlx` (each
auto-detected on its conventional port, override via `AIES_<RUNTIME>_BASE_URL`),
`openai-compat` (any other/hosted endpoint via `AIES_OPENAI_BASE_URL`), and
`mock` (offline). [GUIDE.md §5](GUIDE.md) has a start-to-finish run for each.

## What the engine enforces (and profiles cannot change)

Transcribed from [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md) into
[`src/aies/constants.py`](src/aies/constants.py); conformance tests in
[`tests/`](tests/) map behavior to requirement IDs:

- **EV1–EV6 scoring, 0–4 integer anchors** — no other scales (D2)
- **Decision values are lower 90% confidence bounds**, not means (R02/R11/R13)
- **Minimum gates per risk tier** — a failed EV3 gate denies the tier; one
  EV3 zero at RT3 — Significant through RT4 — Critical fails outright; no profile can express a gate (D3)
- **Statistical minimums** — under-sampled results are labeled
  NON-DECISIONAL and can never look like qualification evidence (D6)
- **AI systems cap at CL3; AL4 — Autonomous never at initial qualification** (R07/R08)
- **Autonomy = min(risk-tier cap, CL-earned cap)** per tier (R09)
- **Environment fingerprint is provenance**; change = re-qualification trigger (D7)

## Layout

```
platform/
├── pyproject.toml
├── src/aies/            # the engine (see PLATFORM.md §4 for components)
│   └── adapters/        # runtime adapters — the ONLY vendor-aware code (D9)
├── profiles/            # six shipped weighting presets (weights only)
├── competencies/        # CA-NN suites: definition, rubric, scenarios
│   └── CA-05-ai-assisted-implementation/
└── tests/               # conformance tests keyed to requirement IDs
```

All twelve competency areas (CA-01…CA-12) ship at least 30 distinct RT2 — Moderate
scenario instruments per area within a 484-scenario corpus. The scenarios
combine multiple constraints, ambiguity, safety pressure, engineering
trade-offs, and direct coverage of ET-01 through ET-15; RT3 — Significant and
RT4 — Critical include refusal and escalation cases. RT2 now meets the
distinct-scenario sample floor in AIES-AESQS-CS-01 §6 without repeat padding.
The 268 new breadth instruments are structurally validated and covered by a
named human tranche decision whose ledger enumerates every scenario ID and
content hash. Together with the original 216 instruments, all 484 are now
design-reviewed; any content edit invalidates the matching ledger decision and
reopens that item automatically. This human-authorized AI-assisted tranche does
not claim 268 separate manual click-through reviews or external independent
validation. No scenario is empirically calibrated until a real-subject panel is
completed. Exact repeats are available only as explicit stability studies and
do not repair breadth gaps.

## Related Documents

- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)
- [ADR-0009 — Engineering Assessment Platform Identity](../adr/ADR-0009-Engineering-Assessment-Platform-Identity.md)
- [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](../AESQS/evaluation-rubrics.md)
- [AIES-AESQS-QP-01 — Qualification Process](../AESQS/qualification-process.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

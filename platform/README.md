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

**Capability scope is explicit.** A run assesses one risk tier (RT1 — Minimal through RT4 — Critical).
`--all-areas` expands coverage across competency areas only at that selected
tier; it is not an all-tier claim. ECM rows marked `not assessed` mean no
mapped scored evidence exists for that task, not that the subject failed it.

**The platform prepares evidence; it never grants.** A human qualification
authority records every grant (PLATFORM.md D8). Output is always scoped —
per-competency-area competency levels and per-tier autonomy envelopes —
never a global "production ready" verdict (D4).

**Milestones M1–M4 shipped** (see [PLATFORM.md §10](../docs/PLATFORM.md)) —
the full pipeline is runnable end to end:
`doctor` (runtime-aware), `discover`, `registry`/`deployment` (incl. `update`,
`remove`, `verify-artifact` for supply-chain provenance), `qualify` (with
`--parallel`, `--judge` auto-scoring, `--journey`, `--all-areas`), `score`,
`import` (external eval results), `report` (complete linked Markdown/JSON/HTML
bundle: qualification evidence, ECM, Grounding Diagnostics, bounded guidance,
and Executive Summary), `transcript`,
`capabilities` (per-area SDLC profile; `--ecm` writes an informational,
task-mapped Engineering Capability Matrix), `judge` (available/list/history),
`assessment` (declarative qualification composition — list/show/validate/result,
Markdown/JSON/HTML, ADR-0005), `audit` (repository conformance — maturity per
area, ADR-0004), `corpus` (the platform reviews its **own** assessment corpus —
health/coverage/duplicates/review; advisory, multidimensional, no single grade),
`runs`, `compare`, `index`, `review`, `grant`, `verify`, `journey`,
`conform`, `runtime`/`profile`/`qualification`, `dashboard`, `plugins`.
All twelve competency areas
(CA-01…CA-12) ship demonstration suites; six weighting profiles; a
frozen v1.0 runtime-adapter contract with an
[out-of-tree adapter example](examples/external_adapter/README.md);
conformance tests run in CI.

**New here?** [GUIDE.md](GUIDE.md) has the whole-system architecture diagram,
component wiring, and step-by-step setup + real-model run instructions.
See also [DEPLOYMENTS.md](DEPLOYMENTS.md) (qualify deployments, not models),
[PROFILES.md](PROFILES.md) (the weighting presets),
[RUNTIMES.md](RUNTIMES.md) (the runtime interface and shipped adapters), and
[JOURNEYS.md](JOURNEYS.md) (multi-phase scenarios that test lifecycle depth),
[SCENARIOS.md](SCENARIOS.md) (how to author competency scenarios), and
[ASSESSMENTS.md](ASSESSMENTS.md) (declarative qualification composition).
[REFERENCE.md](REFERENCE.md) is the complete reference — vocabulary, artifact
schemas, and every command. [CALIBRATION.md](CALIBRATION.md) covers scenario
calibration — treating each scenario as a *measurement instrument* — and the
platform reviews its **own** corpus for calibration, coverage, behavioral
diversity, duplication, and empirical maturity via `aies corpus`
(advisory, multidimensional, never a single grade, never a gate — it critiques,
a human decides).
Hit a snag? [TROUBLESHOOTING.md](TROUBLESHOOTING.md) covers the common
endpoint, TLS, auth, performance, and judge issues.

**The full cycle:** `discover` → `qualify` → `score` (human, and
optionally a model reviewer) → `review` (assembles the peer-review
package with the calibration gate) → `qualify --resume` (gated
aggregation) → `grant` (a **named human authority** records the
decision, producing a Qualification Record — the platform never
grants) → `verify` (re-checks the environment fingerprint; an
environment change invalidates the grant, per D7).

## Install

```
cd platform
pip install -e .          # installs `aies` (Python 3.10–3.14 tested in CI)
pytest tests/             # conformance tests keyed to AESQS requirement IDs
aies suites validate      # suites + shipped assessments (one gate; CI runs it)
```

Artifacts are written to `./aies-workspace` (override with the
`AIES_WORKSPACE` environment variable). Everything persisted is plain
YAML/JSON: diffable, reviewable, tool-independent.

## See the whole thing run (one command, fully offline)

```
make demo        # core workflow (or: bash scripts/demo.sh)
make demo-full   # comprehensive tour of the whole platform
```

`make demo` runs the **core workflow** against the mock runtime — discover a
deployment, compose a named assessment, collect responses, retain a mock
judge's scores as automated evaluation observations, and render the Canonical
Assessment Result as Markdown + HTML. Synthetic mock-judge scores do not become
qualification evidence.

`make demo-full` is the **comprehensive tour**: the three subjects AIES can
assess (a model deployment via `qualify`, a repository via `audit`, and the
standard itself via `conform engine`), the calibrated measurement instruments,
a completed automated Engineering Evaluation with optional human-evaluation
status, the stricter formal qualification/grant boundary, and the Phase-2
empirical harness. The mock run deliberately does not fabricate a human grant.

No GPU, no API key, no network. It's **executable documentation** — the core
path is CI-gated as [`tests/test_demo.py`](tests/test_demo.py) and the
comprehensive script runs in CI too. For a real deployment,
`make integration-demo DEPLOYMENT=… JUDGE=…`.

## Quickstart (fully offline)

```
aies doctor                    # validate environment; detect installed runtimes
aies discover                  # register the deployments each runtime serves
aies registry list            # see the named deployments (e.g. mock-mock-small)

aies qualify <deployment> --profile enterprise --rt 2 --area CA-05
                              # stages 2-4: discovery, environment, benchmark
# ... fill the generated scoresheet.json (integer 0-4 per dimension,
#     rater name, findings for any score <= 2) ...
aies score <run-id>           # ingest ratings (append-only records)
aies qualify --resume <run-id> # stage 5: gated, weighted aggregation
aies report <run-id> --format markdown         # evidence package

aies runs list                # result history
aies runs progress <run-id>   # durable live stage, %, elapsed, rate, ETA, failures
aies compare <dep-a> <dep-b>  # deltas on identical suite versions only
aies suites validate          # validate suite catalog before publishing changes
```

Long-running collection and judge-review commands continuously display the
current stage, completed/total work, percentage, elapsed time, throughput, ETA,
failure count, and current scenario or batch. The same state is written to the
run's `progress.json`, so another terminal can inspect it with
`aies runs progress <run-id>` even if the original CLI is still running.
Progress is implicit in `qualify`, `qualify --resume`, `review`, and `score`;
the separate `runs progress` command is only an optional second-terminal view.
The live line identifies the current human-readable scenario family and
calibrated task objective with its ordinal—for example, `Executing task 2/30:
Performance Optimization — Remove event-loop blocking […]`. Judge progress
identifies the task currently being scored across EV1 — Correctness through
EV6 — Traceability. Parallel execution reports the dynamic active set and the
effective worker capacity (`active N/<parallelism>`); neither value is
hard-coded, so the display follows `--parallel N` or the configured default.

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
The 268 new breadth instruments are structurally validated and calibrated in
metadata but remain explicitly design-review pending, and no scenario is
empirically calibrated until a real-model panel is completed. Exact repeats are
available only as explicit stability studies and do not repair breadth gaps.

## Related Documents

- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)
- [ADR-0009 — Engineering Assessment Platform Identity](../adr/ADR-0009-Engineering-Assessment-Platform-Identity.md)
- [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](../AESQS/evaluation-rubrics.md)
- [AIES-AESQS-QP-01 — Qualification Process](../AESQS/qualification-process.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

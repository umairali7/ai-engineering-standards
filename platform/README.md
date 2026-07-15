# AIES Model Qualification Platform

| | |
|---|---|
| **Document ID** | AIES-PLAT-00 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Contributors & maintainers |

The `aies` command-line tool: the executable reference implementation of the
[AESQS](../AESQS/README.md) qualification methodology. Specification:
[docs/PLATFORM.md (AIES-DOC-06)](../docs/PLATFORM.md). Decision record:
[ADR-0002](../adr/ADR-0002-Qualification-Platform.md).

**The platform prepares evidence; it never grants.** A human qualification
authority records every grant (PLATFORM.md D8). Output is always scoped —
per-competency-area competency levels and per-tier autonomy envelopes —
never a global "production ready" verdict (D4).

**Milestones M1–M4 shipped** (see [PLATFORM.md §10](../docs/PLATFORM.md)) —
the full pipeline is runnable end to end:
`doctor` (runtime-aware), `discover`, `registry`, `qualify` (with
`--parallel` and `--journey`), `score`, `report` (Markdown/JSON/HTML),
`runs`, `compare`, `index`, `review`, `grant`, `verify`, `journey`,
`conform`, `runtime`/`deployment`/`profile`/`qualification`,
`dashboard`, `plugins`. All twelve competency areas
(CA-01…CA-12) ship demonstration suites; six weighting profiles; a
frozen v1.0 runtime-adapter contract with an
[out-of-tree adapter example](examples/external_adapter/README.md);
conformance tests run in CI.

**New here?** [GUIDE.md](GUIDE.md) has the whole-system architecture diagram,
component wiring, and step-by-step setup + real-model run instructions.
See also [DEPLOYMENTS.md](DEPLOYMENTS.md) (qualify deployments, not models),
[PROFILES.md](PROFILES.md) (the weighting presets),
[RUNTIMES.md](RUNTIMES.md) (the runtime interface and shipped adapters), and
[JOURNEYS.md](JOURNEYS.md) (multi-phase scenarios that test lifecycle depth).

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
pip install -e .          # installs the `aies` command (Python >= 3.10)
pytest tests/             # conformance tests keyed to AESQS requirement IDs
```

Artifacts are written to `./aies-workspace` (override with the
`AIES_WORKSPACE` environment variable). Everything persisted is plain
YAML/JSON: diffable, reviewable, tool-independent.

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
aies compare <dep-a> <dep-b>  # deltas on identical suite versions only
```

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

Transcribed from [AIES-AESQS-CS-01](../AESQS/capability-scoring.md) into
[`src/aies/constants.py`](src/aies/constants.py); conformance tests in
[`tests/`](tests/) map behavior to requirement IDs:

- **EV1–EV6 scoring, 0–4 integer anchors** — no other scales (D2)
- **Decision values are lower 90% confidence bounds**, not means (R02/R11/R13)
- **Minimum gates per risk tier** — a failed EV3 gate denies the tier; one
  EV3 zero at RT3–RT4 fails outright; no profile can express a gate (D3)
- **Statistical minimums** — under-sampled results are labeled
  NON-DECISIONAL and can never look like qualification evidence (D6)
- **AI systems cap at CL3; AL4 never at initial qualification** (R07/R08)
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

All twelve competency areas (CA-01…CA-12) ship demonstration suites of
four scenarios each, every area including an escalation scenario where
the competent behavior is to decline or escalate. A *decisional* RT2
assessment needs ≥ 30 scored items per area (AIES-AESQS-CS-01 §6), so
these suites must be grown before their results are treated as
qualification evidence — the platform labels under-sampled runs
NON-DECISIONAL automatically.

## Related Documents

- [Platform Specification (AIES-DOC-06)](../docs/PLATFORM.md)
- [ADR-0002 — Qualification Platform](../adr/ADR-0002-Qualification-Platform.md)
- [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](../AESQS/evaluation-rubrics.md)
- [AIES-AESQS-QP-01 — Qualification Process](../AESQS/qualification-process.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

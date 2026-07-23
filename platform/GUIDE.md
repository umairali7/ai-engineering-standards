# AIES Platform — Architecture & Run Guide

| | |
|---|---|
| **Document ID** | AIES-PLAT-01 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Assessors & qualification authorities |

How the whole AIES system wires together, and exactly how to install the
`aies` platform and run a real qualification against a model you host.
Specification: [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md).

---

## Try before configuring anything

```text
aies demo --open
```

This installed-CLI path is fully offline and cross-platform. It runs the real
collection, batched scoring, analysis, ECM, Engineering Fit, and report
pipeline with deterministic mock deployments. It requires no API key, model
server, Make, Bash, or human review.

For a real deployment, initialize a workspace, discover deployments, and plan
before execution:

```text
aies init
aies discover
aies evaluate SUBJECT --judge REVIEWER --plan-only --parallel 4
aies evaluate SUBJECT --judge REVIEWER --parallel 4
aies open latest
```

`evaluate` is the beginner entry point over the same canonical `qualify`
engine. It schedules each selected instrument once, reports optimized judge
calls, and generates the complete non-blocking Engineering Evaluation bundle.
Advanced qualification, benchmark, journey, and governance commands remain
available without being prerequisites for first value.

## 0. Navigate the CLI

Use the three levels of built-in and generated help:

```text
aies help                    # complete command tree and typical workflow
aies <command> --help        # every parameter for one command
aies <group> <command> --help
```

The generated [CLI Reference](CLI_REFERENCE.md) is the exhaustive guide. It
documents every live command and parameter, prerequisites, option interactions,
outputs/side effects, recommended next commands, and end-to-end command
sequences. CI compares it with the live parser so a new option cannot be added
without documentation.

### Enable Tab completion

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

Inspect the generated script before adding it to a persistent shell profile:

```text
aies completion powershell
aies completion bash
aies completion zsh
```

After activation, Tab completes commands, subcommands, option names, and
enumerated values such as output formats and risk-tier numbers. Filesystem
paths continue to use normal shell path completion. The completion definition
is generated from the same parser as `aies --help`, so it follows the installed
AIES version.

Try:

```text
aies dep<Tab>                         # completes deployment
aies deployment <Tab>                # lists its subcommands
aies report run-123 --format <Tab>    # lists html/json/markdown
```

Useful operating habits:

- `--json` selects machine-readable output for automation.
- `--write` persists a regenerable view where the command supports it.
- `aies runs progress <run>` observes durable progress from a second terminal;
  the originating long-running command already shows task, elapsed time,
  throughput, failures, and ETA.
- `--parallel N` sets concurrent calls. Lower it for rate limiting; it cannot
  repair an API project with insufficient quota.
- Use `--resume-collection` after interrupted inference and `--resume` after
  scoring so completed work is not repeated.

### Read commands as a sequence

Most mutating commands consume evidence created by an earlier stage:

```text
doctor → discover/deployment add → qualify or benchmark
qualify --judge → Engineering Assessment Result + ECM + fit guidance + reports
benchmark → complete scoresheet → score (also aggregates/reports)
aggregated run → capabilities (ECM by default) → guidance (engineering fit)
explicit formal qualification → governed human protocol → grant → verify/history
repository → audit → remediation → audit --gate
empirical plan → frozen subject runs → panel analysis → human promotion decision
```

The CLI Reference repeats the exact prerequisites and next step beside every
command. Automated Engineering Evaluation and formal human qualification remain
separate workflows.

## 1. The whole system, in one picture

The **standard** defines what to measure and how; the **platform** executes
it; a **runtime adapter** is the only thing that talks to an actual model.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ THE STANDARD  (Markdown — the "what" and "how much")                        │
│                                                                             │
│   Shared/  Glossary + Taxonomy  ── canonical scales: EV1–EV6, CL1–CL4,      │
│      │                  AL0 — Manual through AL4 — Autonomous; RT1 — Minimal through RT4 — Critical; ROLE-01..14            │
│      ▼                                                                      │
│   AEBOK ──► AESQS ──► AEOS ──► AEAR ──► AECT      docs/standards/ govern    │
│  (know)   (qualify)  (operate)(architect)(certify)  every document          │
│              │                                                              │
│              │  capability-scoring.md, evaluation-rubrics.md,               │
│              │  qualification-process.md  (weights, gates, minimums)        │
└──────────────┼──────────────────────────────────────────────────────────────┘
               │  transcribed verbatim (with requirement-ID citations)
               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ THE PLATFORM  platform/  (Python package `aies` — the execution engine)     │
│                                                                             │
│                         ┌───────────────┐                                   │
│   you type ───────────► │      CLI      │  (§4 verbs)                        │
│                         └───────┬───────┘                                   │
│                                 ▼                                           │
│   deployment registry ►  ┌───────────────┐  ◄─ profiles/ (weights only;     │
│   (what × where)         │ Qualification │     gates NOT expressible)        │
│                          │    Engine     │                                   │
│                          └───────┬───────┘                                   │
│           ┌─────────────────────┼───────────────────────┐                   │
│           ▼                     ▼                        ▼                   │
│   ┌──────────────┐     ┌────────────────┐      ┌──────────────────┐         │
│   │ Test Runner  │     │  Evaluation    │      │  Scoring Engine  │         │
│   │ (competencies│     │  (human +      │      │ constants.py  ◄──┼─ AESQS  │
│   │  /CA-NN + │──┐  │  model raters) │      │ gates·weights·CI │  tables │
│   │  --parallel) │  │  └────────────────┘      └────────┬─────────┘         │
│   └──────┬───────┘  │           ▲                       ▼                   │
│          ▼          │           │              ┌──────────────────┐         │
│   ┌──────────────┐  │   review.py (calib.     │ Report / Dashboard│         │
│   │Runtime Adapter│ │   gate, divergences)    │ md · json · html  │         │
│   │  (§8 plugin) │  │           ▲              └────────┬─────────┘         │
│   └──────┬───────┘  └───────────┘                       ▼                   │
│          │  ONLY component that speaks to a model    ┌──────────────────┐   │
└──────────┼──────────────────────────────────────────│ Qualification    │───┘
           │                                           │ Record (human    │
           ▼                                           │ grant, §7)       │
┌──────────────────────────┐                           └──────────────────┘
│ RUNTIMES (outside aies)  │        artifacts on disk (append-only, plain files):
│  mock  · openai-compat   │          registry/*.yaml  runs/<id>/responses/*.json
│  + any out-of-tree plugin│          runs/<id>/{scoresheet,evidence-package}.json
│      │                   │          qualifications/QR-*.json   index.sqlite
│      ▼                   │
│  a real model:           │        Everything the platform emits is evidence with
│  local server or hosted  │        full provenance; a human records every grant.
│  OpenAI-compatible API   │
└──────────────────────────┘
```

## 2. How the pieces wire — component responsibilities

| Component | File | Responsibility | Standard tie |
|-----------|------|----------------|--------------|
| CLI | `cli.py` | verb dispatch, human/JSON output; no qualification logic | PLATFORM.md §3 |
| Qualification Engine | `engine.py` | sequences the pipeline; assembles evidence package | §2, §4 |
| Deployment registry | `registry.py` | what is qualified and where (model × runtime × config × endpoint) | §5.1, D11 |
| Profile Loader | `profiles.py` | weighting presets; **cannot** weaken gates or minimums | §5.2, D3 |
| Test Runner | `runner.py` | executes distinct suites; explicit stability repeats; `--parallel` | §4, D6 |
| Runtime Adapter | `adapters/` | the **only** code that speaks to a model runtime | §8, D9 |
| Runtime probing | `runtimes.py` | `doctor`/`discover` over installed runtimes | D11 |
| Evaluation | `rating.py` | human (and model) rater ingestion, append-only | ER-01 |
| Peer review | `review.py` | calibration gate; divergence surfacing | §7 |
| Scoring Engine | `scoring.py` + `constants.py` | EV1–EV6, gates, CI lower bounds, CL, RT×AL | CS-01, §6 |
| Reports / Dashboard | `report*.py`, `dashboard.py` | md/json/html; overview | §9 |
| Qualification Record | `qualification.py` | human grant, status, D7 verify | §7, RR-01 |

**The one rule that ties it together:** the platform *prepares evidence*; a
named human authority *records every grant*. Nothing in the pipeline can
issue a qualification on its own (D8).

## 3. The pipeline, stage by stage → the command that runs it

```
stage 1 registration   →  aies registry add  /  aies discover
stage 2 capability      ┐
stage 3 environment     ├► aies qualify <deployment> ... --judge <judge>
stage 4 benchmark       ┘        (collects responses)
stage 5 scoring         →  automated judge / imported / optional human ratings
        analysis        →  ECM + diagnostics + Engineering Fit Guidance
        report          →  complete Markdown/JSON/HTML bundle
optional human eval     →  displayed separately; never blocks engineering output
formal qualification   →  explicit --formal-qualification + governed rater protocol
formal decision        →  aies grant <run> --decision grant --authority NAME \
                              --assessor-id ID --peer-reviewer NAME --peer-reviewer-id ID ...
deployment envelope    →  (in the Qualification Record)
        re-check        →  aies verify <QR-id>       (invalidates on env change, D7)
        overview        →  aies dashboard --write
```

Assessment maintainers can inspect design-review debt without opening scenario
packs manually:

```text
aies corpus review-pending              # inventory + structural readiness
aies corpus review SC-CA01-021          # inspect one packed scenario by ID
```

The first command is deliberately non-decisional: it exposes every pending
disposition and the effective/stale content-bound review ledger but never makes
a human approval decision. See
[AIES-PLAT-10 — Assessment Calibration](CALIBRATION.md) for accountable review,
external independent validation, and empirical-calibration boundaries.

---

## 4. Setup

Requirements: Python 3.10–3.14 (the currently CI-tested range). The platform's
only required application dependencies are PyYAML and the CA certificate bundle
used for verified HTTPS connections.

```
cd platform
pip install -e .            # installs the `aies` command
pytest tests/ -q --durations=15  # conformance + ranked performance feedback
aies                        # or `aies help` — the command map + typical workflow
aies doctor                 # fingerprint + runtimes + read-only workspace-debris inventory
```

For local verification, the recorded warm-cache Windows budget is 180 seconds
for the complete suite; the 2026-07-23 baseline is 235 tests in 109.82 seconds.
Treat a budget breach or greater-than-25% regression as a profiling trigger.
This is a feedback budget, not a reason to skip correctness gates on slower CI
hardware.

`aies` (with no arguments) or `aies help` prints all commands grouped by stage,
the end-to-end workflow, **and a full command tree** — every command *and*
subcommand (e.g. `profile list`, `qualification history`, `conform check`) with
its usage line. `aies <command> --help` details any single command's options.

`aies doctor` reports which runtimes it can see. Out of the box you have:

- **`mock`** — a deterministic offline runtime (always available; for trying the tool).
- **`openai-compat`** — talks to any server exposing the OpenAI
  `/v1/chat/completions` wire format (most local model servers do, and hosted
  providers too).

Artifacts are written under `./aies-workspace` (override with `AIES_WORKSPACE`).

## 4.1 Configuration (env vars / .env — nothing hard-coded)

All *operational* settings come from environment variables or a `.env`
file — none are baked into the code. Copy the template and edit:

```
cp .env.example .env      # .env is git-ignored; real env vars override it
```

Search order (first found wins): `$AIES_ENV_FILE`, `./.env`,
`<workspace>/.env`. Key variables (full list in
[.env.example](.env.example)):

| Variable | Purpose | Default |
|----------|---------|---------|
| `AIES_WORKSPACE` | where artifacts are written | `./aies-workspace` |
| `AIES_OPENAI_BASE_URL` | default endpoint for the openai-compat runtime | *(none — unset = not configured)* |
| `AIES_OPENAI_API_KEY` | API key if the endpoint needs one | *(none)* |
| `AIES_REQUEST_TIMEOUT_S` | per-request inference timeout | `300` |
| `AIES_PARALLEL` | default concurrent inference calls | `1` |
| `AIES_TEMPERATURE`, `AIES_MAX_TOKENS`, `AIES_TOP_P`, `AIES_SEED` | generation defaults (a deployment's `parameters_default` overrides these) | *(model default)* |

Precedence: CLI flag / deployment manifest → real env var → `.env` →
built-in default. The **normative** engine constants (gates, weights,
sample minimums, confidence level, calibration threshold) are *not*
configurable — they are the AESQS standard (D3).

## 5. Running a real qualification

### 5.1 Point the tool at your runtime

The platform ships adapters for the common local runtimes — **Ollama**,
**LM Studio**, **llama.cpp** (`llama-server`), and **MLX** (`mlx_lm.server`) —
plus a generic **openai-compat** adapter for anything else (including hosted
APIs). Each named adapter knows its runtime's conventional port and has its
own override env var:

| Runtime | Start the server | Conventional endpoint | Override env var |
|---------|------------------|-----------------------|------------------|
| **Ollama** | `ollama serve` (models: `ollama pull llama3.1`) | `http://localhost:11434/v1` | `AIES_OLLAMA_BASE_URL` |
| **LM Studio** | start the local server in the app | `http://localhost:1234/v1` | `AIES_LMSTUDIO_BASE_URL` |
| **llama.cpp** | `llama-server -m model.gguf --port 8080` | `http://localhost:8080/v1` | `AIES_LLAMACPP_BASE_URL` |
| **MLX** (Apple Silicon) | `mlx_lm.server --port 8080` | `http://localhost:8080/v1` | `AIES_MLX_BASE_URL` |
| any other / hosted | — | your URL | `AIES_OPENAI_BASE_URL` |

You usually need no configuration for a local runtime on its default port —
`aies doctor` probes all of them and `aies discover` registers whatever each
serves:

```
aies doctor          # shows each runtime: [OK] reachable / [--] not running
aies discover        # registers every served model as a named deployment
aies registry list   # e.g. ollama-llama3.1, lmstudio-qwen2.5-coder-7b
```

Override a port, or reach a remote/hosted endpoint, via `.env`:

```
# .env  (git-ignored; real env vars override it)
AIES_OLLAMA_BASE_URL=http://192.168.1.50:11434/v1   # Ollama on another host
# AIES_OPENAI_API_KEY=sk-...                          # if the endpoint needs a key
```

> **Note:** llama.cpp and MLX share the conventional port 8080, so if a server
> is running there both adapters will discover it (as `llamacpp-…` and
> `mlx-…`). Set the specific env var for the one you're using, or just qualify
> the deployment whose name matches your runtime.

Or hand-author a deployment (needed for hosted APIs, or to pin quantization
and generation parameters). Save `my-deployment.yaml`:

```yaml
id: local-qwen                 # the deployment name you will qualify
runtime: openai-compat
model: qwen2.5-coder           # the server-side model name
runtime_config:
  base_url: http://localhost:11434/v1
  model: qwen2.5-coder
  api_key_env: AIES_API_KEY    # optional: name of an env var holding a key
quantization: q6_k
context_window: 32768
provenance:
  source: local server
  checksum: sha256:<hash of the model artifact if you have it>
```

```
aies registry add my-deployment.yaml
```

> A deployment is `model × runtime × config × endpoint`. The same model at a
> different quantization or on a different server is a **different deployment**
> and a separate qualification subject — that is design decision D11, and it is
> why `verify` (§5.6) can invalidate a grant when the environment changes.

**Fixing or removing a deployment.** `add` only registers *new* ids — it refuses
one that already exists. To correct a manifest you already registered (a wrong
`base_url`, an `api_key_env` typo, changed generation defaults, or adding
`roles: [judge]`), edit the file and run `update` — it overwrites the entry in
place, keeping the id:

```
aies deployment update my-deployment.yaml   # edit an EXISTING deployment
aies deployment remove  local-qwen          # hard-delete; frees the id to reuse
aies deployment retire  local-qwen          # soft-mark; id stays reserved for audit
```

`update` warns if a field that defines the deployment's behavioral identity
(runtime, model, quantization, `runtime_config`) changed, because prior
qualifications for that id may no longer describe what now runs — re-check with
`aies qualification verify` (§5.6). A pure key/roles fix updates quietly.

> **Keys live in the environment, never in the manifest.** `api_key_env` is the
> **name** of an environment variable (e.g. `ANTHROPIC_API_KEY`), not the key
> itself. Put the secret in your shell (`export ANTHROPIC_API_KEY=…`); if you
> ever paste a real key into a file, rotate it.

### 5.2 Run the benchmark — automated scoring (recommended)

Pass a **judge deployment** and either `qualify` or `benchmark` runs end to end
and prints the engineering report directly — no manual step:

```
aies qualify local-qwen --profile coder --rt 2 --area CA-05 \
    --parallel 4 --judge <a-strong-deployment>

# equivalent benchmark-oriented spelling
aies benchmark local-qwen --profile coder --rt 2 --area CA-05 \
    --parallel 4 --judge <a-strong-deployment>
```

The candidate answers the scenarios; the judge model rates every answer 0–4 on
EV1–EV6; the run aggregates and the report prints. Set `AIES_JUDGE` in your
`.env` to make it the default for every run and every profile.

> **Automated ratings complete engineering evaluation.** They drive the
> Engineering Assessment Result, ECM, diagnostics, Engineering Fit Guidance,
> and reports without human review. “Advisory” applies only at the separate
> formal-qualification admission boundary; it does not downgrade or block the
> engineering result.

`--parallel N` applies to **both** phases — collecting the candidate's answers
*and* the judge's scoring — so a `--judge` run is concurrent end to end. The
default is 1 (or `$AIES_PARALLEL`); the run prints how many workers each phase
uses so you can see the concurrency. Raise it to the endpoint's real
per-key concurrency limit.

Judge scoring is also **batched by default**: up to eight response/task pairs
are sent in one reviewer request, automatically reduced to fit the reviewer's
declared context window. A malformed batch is split recursively so valid
per-response ratings are never fabricated or lost. Set
`--judge-batch-size N` (or `AIES_JUDGE_BATCH_SIZE`) to tune the maximum. This
changes request overhead only; AIES still validates and persists one rating
record per candidate response.

**If the judge step fails (e.g. a TLS or auth error), you do not re-collect.**
Responses are written as they are collected, so they survive a later failure.
Fix the judge issue, then score the *already-collected* run and aggregate in
one command:

```
aies qualify --resume <run-id> --judge <judge-id> --parallel 8
```

Every successful aggregation or resume writes the complete linked report bundle
in the run directory: Engineering Evaluation Report, Engineering Assessment
Result when the run used a declarative assessment, Engineering Capability
Matrix, source-separated Grounding Diagnostics, Engineering Fit Guidance, and
Executive Summary. An explicitly formal run instead adds the Canonical Formal
Assessment Result and qualification-bounded Deployment Guidance.
Markdown, JSON, and HTML views are generated for each audience-facing product,
with `report-bundle.json` as the machine-readable index. The command prints the
primary paths; if any artifact cannot be rendered, it fails rather than claiming
completion.

These files do not all have the same storage semantics. Responses, rating
observations, resolutions, human-rater records, Qualification Records, and
lifecycle events are append-only source records. The run manifest, scoresheet,
progress state, and latest fingerprint are workflow-owned mutable state.
Evidence/assessment packages are versioned derived canonical snapshots.
Markdown/JSON/HTML reports, ECM, Deployment Guidance, Executive Summary,
dashboard, and bundle index are regenerable views and can be refreshed without
changing source evidence. The workspace writer rejects attempts to overwrite an
append-only record or to write a presentation view into an evidence path.

**Grounding diagnostics are descriptive, not a new qualification score.** A
structured reviewer may record unsupported assertions, fabricated APIs or
entities, invalid citations/provenance, false success/test claims, and whether
an abstention was appropriate. Automated and human observations remain
separate. The report shows coverage and an observed grounding-reliability
percentage only where that check was actually performed; `unavailable` never
means zero hallucinations. These observations map to the existing EV1 —
Correctness, EV3 — Safety & Security, and EV6 — Traceability dimensions and
cannot alter their scores, gates, competency level, or a human Qualification
Record. Human scoresheets and external imports may include the same optional
`grounding_diagnostics` object.

**Bring external eval results in as evidence.** If you already scored the
responses with another tool (a custom Inspect/DeepEval task, a second judge, an
offline pipeline) that emits EV1–EV6, import them as automated-kind ratings.
They are immediately usable for Engineering Evaluation; formal qualification
applies its separate admission protocol:

```
aies import <run-id> eval.json --source inspect:my-task
```

`import` validates, ingests, aggregates, and refreshes the complete bundle in
that one command.

The file is `{"source": "...", "items": [{"scenario_id": "SC-CA05-001",
"repeat": 1, "scores": {"EV1": 3, …, "EV6": 3}, "findings": [...]}]}`. Items that
aren't six integers 0–4 are skipped and reported, never fabricated. (AIES scores
all six dimensions, so a single-metric benchmark is corroboration, not a
substitute.) The reverse direction — `aies export <run>` — writes a run's
prompts + responses + scores to that same JSON shape (round-trips through
`import`), so evidence flows back out to other tooling.

**If a collection failed partway** (a flaky endpoint dropped some responses),
fill only the missing ones instead of re-running the whole thing:

```
aies qualify --resume-collection <run-id>    # re-runs only the missing responses
```

It reconstructs the deployment and scenarios from the run manifest, collects
just the gaps, and rebuilds the scoresheet (refusing if the suite changed since
collection).

**Verify supply-chain provenance.** If a deployment declares `provenance.checksum`
(and optionally `provenance.signature`), verify a local artifact against it:

```
aies deployment verify-artifact <id> --artifact ./model.safetensors \
  [--pubkey key.pem --signature model.sig]
```

Checksum verification is exact (SHA-256); signature verification is best-effort
(needs `cryptography`, or verify via cosign/Sigstore externally). A declared
signature you didn't check is reported as such — never a false pass.

**Slow run?** Cap output length with `export AIES_MAX_TOKENS=1024` (often the
biggest candidate-side speedup). On a single local GPU, more `--parallel`
mostly queues on the model. Judge requests are batched automatically; tune
`--judge-batch-size` only to match the judge context and throughput. Use an
explicit `--repeats` only for a separate stability study. See
[TROUBLESHOOTING.md](TROUBLESHOOTING.md) for timeout, TLS, auth, and judge
issues.

**Any deployment can be the judge — cloud, local, or another machine.** A judge
is just a registered `openai-compat` deployment; "where it runs" is only its
`base_url`. Copy-paste starting points are in
[`examples/deployments/`](examples/deployments/README.md): a hosted frontier
model, a second model on this machine, and a model on another box on your LAN.
Register once (`aies deployment add <file>`) then `--judge <its-id>`.

**See your judges.** A judge is an ordinary deployment, but you can *earmark*
one by adding `roles: [judge]` to its manifest (advisory — any deployment can
still judge ad hoc). Three views:

```
aies judge available                # the POOL: how many judges you have
                                     #   registered (roles:[judge]), each with
                                     #   its track record or "never used"
aies judge list                     # judges that have actually JUDGED, with
                                     #   runs judged · responses scored · parse
                                     #   rate · self-judged / unregistered flags
aies judge history                  # one row per judged run, newest first
aies judge history --judge <id>     # just that judge's runs
```

The example manifests in [`examples/deployments/`](examples/deployments/README.md)
are tagged `roles: [judge]`, so after `aies deployment add`-ing them,
`aies judge available` counts them immediately.

`parse rate` is the fraction of responses whose scores the judge returned in the
required JSON shape — a judge that often falls below 100% is contributing thin
evidence (unparseable replies are skipped, never fabricated) and is a poor
choice regardless of how capable the underlying model is.

Pick `--area` from `CA-01 … CA-12` (repeat for several). For a *decisional*
result an AI system needs ≥ 20 (RT1 — Minimal), 30 (RT2 — Moderate), 50 (RT3 — Significant), 100 (RT4 — Critical) scored
items per area — grow `--repeats`; under-sampled runs are labelled
**NON-DECISIONAL**.

The report is marked **JUDGE-PRODUCED**: the scores are the judge's opinion,
not ground truth. Two cautions: (1) use a *different, capable* deployment as
the judge — `--judge self` (a model grading its own work) is biased and warned
against; (2) judge scores are engineering-evaluation observations and may be
admitted for corroborating peer review after calibration (§5.4), but they are
never the sole basis of qualification evidence (AIES-AESQS-ER-01-R10;
ADR-0012). For a first **validity check** — does AIES separate a model
you rate strong from one you rate weak? — score at least one run yourself, or
review the judge, so you are testing AIES and not the judge.

### 5.2a Read the run in one view

To review what actually happened — the task, the model's answer, and its
scores side by side, per item — instead of opening response files one by one:

```
aies transcript <run-id>                 # scrollable Markdown for the whole run
aies transcript <run-id> --area CA-05    # just one area
aies transcript <run-id> --write          # save transcript.md into the run dir
```

This is the fastest way to sanity-check a run and to *read the model's actual
answers* when deciding whether the scores look right.

### 5.3 Manual scoring (omit `--judge`)

Without `--judge`, `qualify` writes a `scoresheet.json` and stops. Open it and,
for each response, set an integer **0–4** on each EV1–EV6 dimension against the
rubric anchors, add the human's durable rater `id` and matching `name`, declare
the run subject conflict-free, and write a finding for any score ≤ 2. Register
each human once with their current competency/risk scope and calibration:

```
aies rater register --id alice --name "Alice Example" \
  --area CA-05 --rt 2 \
  --qualified-until 2027-06-30T00:00:00Z \
  --calibration-valid-until 2027-06-30T00:00:00Z \
  --anchor-version anchors-2026-07 --registered-by "Registry Authority"

aies score <run-id>              # ingest + aggregate + complete report bundle
```

An unregistered human may still contribute optional engineering feedback, but
that observation is explicitly **not admitted** to formal qualification. For
RT1 — Minimal and RT2 — Moderate, independently double-rate at least 20% of
distinct evidence items. For RT3 — Significant and RT4 — Critical,
independently double-rate every item. The admitted adjacent-agreement rate must
be at least 80%. A repeated score from the same durable identity is not an
independent rating.

Evidence Package v5 retains this submission as a **rating observation** linked
to the response evidence item. Qualification statistics consume at most one
resolved score per response, so adding another rater never increases the
effective item count. Independent human scores that differ by at most one
anchor resolve conservatively to the lower demonstrated anchor. A difference
of two or more on any EV dimension remains explicitly unresolved and excluded
from qualification statistics until a named human records a reasoned
disposition; it is never silently averaged (ADR-0012,
AIES-AESQS-ER-01-R07 — Material disagreement requires resolution).

Resolve a material divergence only after human review, recording the complete
EV1–EV6 disposition and rationale as an immutable event:

```
aies resolve <run-id> SC-CA05-001-r1.json \
  --scores 4 4 3 4 3 4 --resolver "Alice Example" --resolver-id alice \
  --rationale "Reconciled against anchor artifact A-17" --conflict-free
```

### 5.4 (Optional) Add a model reviewer

Have a second deployment critique and score the same responses, then assemble
the peer-review package. The platform drives the reviewer for you:

```
aies review <run> --model-reviewer local-gpt-oss \
  --parallel 4
```

`--model-reviewer` sends each candidate response to that deployment, asks for
structured EV1–EV6 scores, and ingests the parseable ones as `model`-kind
ratings (a reviewer that won't follow the contract simply contributes fewer
ratings — nothing is fabricated). It also immediately refreshes `report.md`,
`report.html`, and the ECM. Those reports show **Automated review** and
**Human review (optional)** separately for every EV dimension. Automated
reviewer scores are immediately usable for Engineering Evaluation, ECM,
diagnostics, fit guidance, comparison, and reporting. They do not require
reviewer qualification or human approval.

Only the separate Formal Qualification protocol asks whether a reviewer is
admitted as corroborating peer review. `--reviewer-qualified` or bootstrap
calibration against human-scored anchors (`--calibration`) may establish that
formal role; it does not turn model scores into human qualification evidence.
Divergences of ≥ 2
points between the human and the model are surfaced for you to resolve — never
averaged (§7). Re-running the same reviewer reuses already-recorded scores
instead of making duplicate API/model calls.

Optionally add `--human-evaluation "Name"` or
`--consider-advisory-review` to record human consideration separately. Neither
flag is a prerequisite for engineering results, and the review record is not a
grant.

### One-command automated evaluation

For normal evaluations, use `qualify` with a local or hosted judge. It collects
responses, scores them, and writes the complete report and ECM bundle in one
command. Human evaluation is optional for this Engineering Evaluation: the
report records either `☐ Not reviewed (optional)` or `☑ Reviewed — <name>`.
Automated scoring completeness, rather than a human-review declaration, closes
the evaluation workflow. Formal qualification is shown as **not requested**;
it has no blocking verdict unless the user explicitly selects that workflow.

```
aies qualify <deployment> --profile enterprise --rt 2 --area CA-05 \
  --judge local-gpt-oss --parallel 4
```

If responses were already collected because a prior judge failed, resume with
the replacement judge in the same one-command form. Existing ratings from that
same judge are reused rather than duplicated:

```
aies qualify --resume <run-id> --judge local-gpt-oss --parallel 4 \
  --consider-advisory-review --human-evaluation "Your Name"
```

### Reading risk-scoped capability profiles

Every qualification run has **one risk-tier scope**: RT1 — Minimal, RT2 — Moderate,
RT3 — Significant, or RT4 — Critical. This is deliberate: each
tier has different gates, sample minimums, and autonomy limits, so combining
them into one score would hide the risk context.

`--all-areas` means **all competency areas at the selected tier**. For example,
`--all-areas --rt 2` can populate the RT2 — Moderate engineering-task profile; it does not
demonstrate RT1 — Minimal, RT3 — Significant, or RT4 — Critical capability. A complete cross-tier picture requires
separately scoped runs, which must remain visibly tier-labelled until a future
all-tier orchestrator presents them together.

Before collection, an explicit formal or `--decisional` run warns when the
selected **distinct-scenario** plan is below an area's AESQS minimum. Ordinary
engineering evaluations report actual coverage without a qualification
warning. `--decisional` verifies that every selected
area has enough distinct instruments; it rejects a thin suite instead of
padding it with repeats (for example, `aies qualify local-qwen --all-areas --rt
2 --decisional --judge <judge>`). Exact reruns occur only when `--repeats` is
explicitly requested for a separate stability study. The plan guarantees
collection intent only, not successful responses or admitted ratings.

In an Engineering Capability Matrix, **not assessed** means no mapped scored
scenario evidence was collected for that task. It is unknown, not a failure or
a low score. ADR-0013 task decisions count one resolved admitted item per
distinct mapped scenario, apply task-specific RT minimums, lower 90% confidence
bounds, risk-tier gates, mapping review, parent-area outcomes, and the human
rater protocol. **Demonstrated** means all formal controls pass. By default,
`aies guidance <run>` renders Engineering Fit Guidance from observed evidence
with strong-fit, engineering-review, weak-fit, and not-assessed categories.
This needs no human review and creates no deployment authority. Supply an active
matching human record with `aies guidance <run> --qualification <QUAL-id>` only
to switch to qualification-bounded Deployment Guidance.

For example, this asks only whether the evidence and record support the stated
role, phase, and autonomy—not whether the subject is globally suitable:

```
aies guidance <run> --qualification QUAL-2026-001 \
  --role ROLE-06 --phase P09 --autonomy 3 --write
```

The result is `Use`, `Use with human review`, `No recommendation`, or `Avoid for
this scoped use`. An expired, invalidated, revoked, mismatched, or absent record
cannot produce `Use`. Observed evidence never gets promoted to `Use with human
review` merely because a reviewer might supervise it. A live read-only
fingerprint check also suppresses `Use` if the deployment no longer matches the
qualified deployment. Every task row carries applicable qualification
conditions, validity/role/phase/autonomy constraints, and residual instrument
calibration or thin-gate risks.

### 5.5 Aggregate and report

```
aies qualify --resume <run>              # aggregate + complete report bundle
aies report  <run> --format markdown     # or json, or html (--write)
```

The report shows per-dimension decision values (lower 90% confidence bounds),
gate outcomes, the aggregate, the score-bounded competency level, and the
recommended **RT × AL autonomy envelope** — never a global pass/fail.

### 5.6 Record the human decision, then verify

```
aies grant <run> --decision grant \
    --authority "Qualification Authority" \
    --assessor "Alice Example" --assessor-id alice --assessor-conflict-free \
    --peer-reviewer "Bob Example" --peer-reviewer-id bob --peer-conflict-free \
    --role ROLE-06 --phase P09 --phase P10 \
    --sponsor "Engineering VP" \
    --framework-version "AIES-AESQS-CF-01@review-2026-07-22" \
    --valid-from 2026-07-22T00:00:00Z --valid-until 2027-07-21T00:00:00Z \
    --consider-advisory-review \
    --human-evaluation "Bob Example" \
    --rationale "pilot qualification"
aies qualifications list                 # the Qualification Record (QUAL-...)
aies verify QUAL-<...>                    # re-checks the deployment fingerprint
aies dashboard --write                    # HTML overview of everything
```

`--human-evaluation` records a named qualitative or scored human review; it
does **not** require a second scoresheet. If human scores were ingested, the
evidence report shows them separately beside the automated reviewer scores.

The durable, auditor-facing **qualification report** is rendered from the
record itself:

```
aies report QUAL-2026-001 --format html --write   # writes reports/QUAL-2026-001.html
aies report list                                   # generated report artifacts
```

`grant` refuses non-decisional or gate-failing evidence and requires two
distinct, registered, currently qualified and calibrated humans with
subject-bound conflict declarations. The record contains the complete scope:
subject, role, phases, maximum risk tier, competency × CL claims, framework and
agent-definition versions where applicable, sponsor, and validity. The platform
never grants on its own.

Qualification records are immutable. Conditions, renewal, suspension,
invalidation, revocation, and supersession append separate lifecycle events:

```
aies qualifications event QUAL-2026-001 --event renewed \
  --authority "Qualification Authority" --reason "annual re-evaluation" \
  --evidence-run <new-decisional-run> --valid-until 2028-07-20T00:00:00Z \
  --peer-reviewer "Bob Example" --peer-reviewer-id bob --peer-conflict-free
```

Renewal is never automatic: the new run must match the subject, profile, risk
tier, and full competency scope; remain decisional and gate-passing; receive
verified independent peer review; extend (not shorten) validity; and remain
within the tier maximum. Expired or materially changed qualifications are
treated as absent and require requalification. `verify` binds hosted endpoints
to endpoint/model/revision/runtime/config identity while local deployments also
remain host-bound; irrelevant calling-laptop CPU/RAM changes do not invalidate
a hosted qualification.

### 5.7 Worked example — a complete run against Ollama, start to finish

Concretely, qualifying a model served by Ollama as an RT2 — Moderate software engineer
in AI-assisted implementation (CA-05):

```
# 0. one-time
cd platform && pip install -e . && cp .env.example .env

# 1. have the model running
ollama serve &                      # if not already running
ollama pull llama3.1:8b

# 2. see it and register it
aies doctor                         # ollama -> [OK] endpoint reachable
aies discover                       # -> created ollama-llama3.1-8b
aies registry list

# 3. run the complete automated Engineering Evaluation
aies benchmark ollama-llama3.1-8b --profile coder --rt 2 --area CA-05 \
      --parallel 4 --judge <judge-deployment>
#    collects, scores, analyzes, and writes the linked report bundle.
#    Human evaluation is optional.

# 4. inspect engineering decision products
aies capabilities <run>                    # Engineering Capability Matrix
aies guidance <run>                        # Engineering Fit Guidance
aies report <run> --format html --write

# 5. only when formal qualification is intentionally required, start a
#    --formal-qualification run and complete its governed human-rater protocol.
#    A two-human authority decision can then produce a scoped record:
#    Use the complete command in §5.6 after both raters are registered.
aies grant <run> --decision grant --authority "Qualification Authority" \
      --assessor "Alice Example" --assessor-id alice --assessor-conflict-free \
      --peer-reviewer "Bob Example" --peer-reviewer-id bob --peer-conflict-free \
      --role ROLE-06 --phase P09 --phase P10 --sponsor "Engineering VP" \
      --framework-version "AIES-AESQS-CF-01@review-2026-07-22" \
      --valid-from 2026-07-22T00:00:00Z --valid-until 2027-07-21T00:00:00Z \
      --rationale "engineering pilot"
aies qualifications list
aies verify QUAL-<...>              # re-checks the deployment fingerprint
aies dashboard --write              # HTML overview
```

What you get by default: an Engineering Evaluation Report, ECM, diagnostics,
Engineering Fit Guidance, and Executive Summary. Formal qualification adds
gate decisions, competency levels, autonomy envelopes, and—only after the
governed human decision—a Qualification Record bound to the assessed subject
and deployment fingerprint.

Every other runtime is identical — just start its server and use the matching
deployment name (`lmstudio-…`, `llamacpp-…`, `mlx-…`).

### 5.8 Audit a repository (a different subject)

The deployment workflow above assesses one current subject adapter. `aies
audit` assesses a **repository and the engineering practice in it** against the
twelve competency areas
([ADR-0004](../adr/ADR-0004-Repository-Conformance-Audit.md)) — the executable
form of [conformance](../docs/CONFORMANCE.md).

```
aies audit .                      # scorecard + ranked recommendations (markdown)
aies audit . --rt 2               # evaluate against RT2 — Moderate required evidence
aies audit . --gate --rt 2        # CI mode: non-zero exit if RT2 — Moderate evidence is missing
aies audit . --attest attest.json # supply evidence for non-detectable practices
aies audit . --format json        # machine-readable
```

It scores **maturity ML0–ML4 per area** with **three-state evidence**:
**verified** (found in the repo), **asserted** (attested with an evidence
pointer), or **gap**. Absence of a signal is always a gap — never a false pass —
and an assertion cannot stand in for a control that *is* file-detectable. It
auto-detects the strong-signal areas (foundations, implementation provenance,
testing, security, delivery, context) and maps findings to external standards
(OWASP, MITRE ATLAS, CISA/NCSC, SLSA, ISO/IEC 42119); the non-detectable areas
(requirements, product) are attestation-only. The attestation file mirrors the
conformance model:

```json
{ "items": [ {"id": "ca10-branch-protection", "evidence": "link or note"} ] }
```

### 5.9 Run a named assessment (composition as data)

Instead of listing areas and a profile by hand, run a **declarative assessment**
— a named engineering composition (enterprise, coder, security, architecture) whose
competency composition lives in `assessments/*.yaml`
([ADR-0005](../adr/ADR-0005-Assessment-as-Code.md), authoring guide
[ASSESSMENTS.md](ASSESSMENTS.md)):

```
aies assessment list                                        # what's shipped
aies qualify local-qwen --assessment enterprise --judge <judge>   # compose, score, analyze
aies assessment result <run>                                # engineering result; exit 0
aies assessment result <run> --format html --out result.html   # presentation-grade view

# Explicit, separately governed formal result:
aies qualify local-qwen --assessment enterprise --formal-qualification
aies assessment result <run> --formal-qualification
```

By default, Markdown, JSON, and HTML are views of the same non-blocking
Engineering Assessment Result: `COMPLETE`, `PARTIAL`, or `NOT SCORED`, with
automated coverage and optional human-evaluation columns.

`--assessment` selects the competency set, profile, risk tier, and sampling.
Only `--formal-qualification` invokes the frozen decision engine's
**authoritative formal outcome** —
`PASS / FAIL / INCONCLUSIVE / INSUFFICIENT EVIDENCE` — over the assessment's
**mandatory** competencies. It is **gate-first**: a strong competency never
offsets a failing one, and there is **no blended score**. Advisory competencies
and the numeric diagnostics/analytics are reported for feedback but never decide.
A `PASS` is an assessment outcome; a named human still records any grant.

## 6. A note on trust

Every number the platform emits is evidence with full provenance (which model
build, which environment, which rater, which suite version), stored as plain
append-only files you can diff and audit. The gates and statistical minimums
are engine constants transcribed from [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md);
no profile or flag can relax them. The scoped grant is a human decision the
tool records — not one it makes.

## Related Documents

- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)
- [AIES-PLAT-00 — AIES Engineering Assessment Platform](README.md)
- [ADR-0002 — Qualification Platform](../adr/ADR-0002-Qualification-Platform.md)
- [AESQS Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](../AESQS/capability-scoring.md)
- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

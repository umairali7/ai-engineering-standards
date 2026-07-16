# AIES Platform — Architecture & Run Guide

| | |
|---|---|
| **Document ID** | AIES-PLAT-01 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Assessors & qualification authorities |

How the whole AIES system wires together, and exactly how to install the
`aies` platform and run a real qualification against a model you host.
Specification: [PLATFORM.md (AIES-DOC-06)](../docs/PLATFORM.md).

---

## 1. The whole system, in one picture

The **standard** defines what to measure and how; the **platform** executes
it; a **runtime adapter** is the only thing that talks to an actual model.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ THE STANDARD  (Markdown — the "what" and "how much")                        │
│                                                                             │
│   Shared/  Glossary + Taxonomy  ── canonical scales: EV1–EV6, CL1–CL4,      │
│      │                             AL0–AL4, RT1–RT4, ROLE-01..14            │
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
| Test Runner | `runner.py` | executes scenario suites; repeats; `--parallel` | §4, D6 |
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
stage 3 environment     ├► aies qualify <deployment> --profile P --rt N --area CA-NN
stage 4 benchmark       ┘        (writes responses + a scoresheet)
        (human rates)   →  edit scoresheet.json ; aies score <run>
        (model review)  →  aies review <run> --reviewer <label> [--calibration f.json]
stage 5 scoring         →  aies qualify --resume <run>      (gated aggregation)
        report          →  aies report <run> --format markdown|json|html
stage 6 peer review     →  (assembled by aies review, above)
stage 7 decision        →  aies grant <run> --decision grant --authority NAME --second NAME
stage 8 role envelope   →  (in the evidence package & Qualification Record)
        re-check        →  aies verify <QR-id>       (invalidates on env change, D7)
        overview        →  aies dashboard --write
```

---

## 4. Setup

Requirements: Python ≥ 3.10. The platform's only dependency is PyYAML.

```
cd platform
pip install -e .            # installs the `aies` command
pytest tests/               # conformance tests, keyed to AESQS requirement IDs
aies                        # or `aies help` — the command map + typical workflow
aies doctor                 # environment fingerprint + detected runtimes
```

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

Pass a **judge deployment** and `qualify` runs end to end and prints the report
directly — no manual step:

```
aies qualify local-qwen --profile coder --rt 2 --area CA-05 --repeats 5 \
    --parallel 4 --judge <a-strong-deployment>
```

The candidate answers the scenarios; the judge model rates every answer 0–4 on
EV1–EV6; the run aggregates and the report prints. Set `AIES_JUDGE` in your
`.env` to make it the default for every run and every profile.

`--parallel N` applies to **both** phases — collecting the candidate's answers
*and* the judge's scoring — so a `--judge` run is concurrent end to end. The
default is 1 (or `$AIES_PARALLEL`); the run prints how many workers each phase
uses so you can see the concurrency. Raise it to the endpoint's real
per-key concurrency limit.

**If the judge step fails (e.g. a TLS or auth error), you do not re-collect.**
Responses are written as they are collected, so they survive a later failure.
Fix the judge issue, then score the *already-collected* run and aggregate:

```
aies review <run-id> --model-reviewer <judge-id> --parallel 8
aies qualify --resume <run-id>
```

**Slow run?** It's almost always the subject model, not the platform. Cap output
length with `export AIES_MAX_TOKENS=1024` (often the biggest speedup), and use
`--repeats 1` for a quick, non-decisional look. On a single local GPU, more
`--parallel` mostly just queues on the model — `max_tokens`/`--repeats` are the
real levers. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for timeout, TLS, auth,
and judge issues.

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
result an AI system needs ≥ 20 (RT1), 30 (RT2), 50 (RT3), 100 (RT4) scored
items per area — grow `--repeats`; under-sampled runs are labelled
**NON-DECISIONAL**.

The report is marked **JUDGE-PRODUCED**: the scores are the judge's opinion,
not ground truth. Two cautions: (1) use a *different, capable* deployment as
the judge — `--judge self` (a model grading its own work) is biased and warned
against; (2) judge scores carry decisional *weight* only once the judge is
calibrated (§5.4). For a first **validity check** — does AIES separate a model
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

### 5.2b Understanding your results — the two axes

Scores have **two independent axes**, and mixing them up is the most common
source of confusion:

**Axis 1 — Competency Area (CA-01…CA-12): *what kind of work*.** This is the
"good planner / coder / security engineer?" axis. Each area is a role / SDLC
phase, and **each gets its own score, competency level (CL), and autonomy
envelope**. A model can be a strong coder and a weak security engineer — that
shows up as different per-area results.

| Area | Role / name | What it covers | SDLC phase |
|---|---|---|---|
| CA-01 | AI-Native SDLC Foundations | Risk-tiering a task, deriving the autonomy ceiling, provenance, keeping an accountable human — the orientation every other area assumes | Cross-cutting |
| CA-02 | Business & Requirements Analysis (**planner**) | Eliciting/structuring intent, checking requirements for ambiguity & contradiction, traceability to a source | Plan |
| CA-03 | Product & Experience Definition | Defining end-to-end experience, testable acceptance criteria, prioritizing against product goals | Design |
| CA-04 | Architecture & Solution Design (**architect**) | Enumerating design options vs quality attributes, critiquing for failure modes, recording decisions + rejected alternatives | Design |
| CA-05 | AI-Assisted Implementation (**coder**) | Producing source changes: features, fixes, refactors; stating assumptions, preserving behavior, escalating out-of-scope | Build |
| CA-06 | Testing, Quality & Evaluation | Tests that assert intended (not just current) behavior, verification independence, real coverage vs theater | Test |
| CA-07 | Security & Privacy Engineering (**security**) | Threat-modeling agents/pipelines, finding vulns, reviewing personal-data flows, treating external input as untrusted | Cross-cutting |
| CA-08 | Delivery & Release Engineering | Pipeline as enforcement: risk-tier gates, provenance at promotion, progressive release with rollback | Release |
| CA-09 | Operations, Observability & Reliability | Running AI-native systems: observability, reliability, incident response | Operate |
| CA-10 | Human-AI Collaboration & Oversight | Oversight as a discipline: gates a human can judge, right-sized reviews, measured control health | Cross-cutting |
| CA-11 | Context & Knowledge Engineering | Curating governed context assets: knowledge → machine-consumable form, minimal relevant set per task, freshness | Cross-cutting |
| CA-12 | Governance, Risk & AI Safety | Keeping the operating model honest: risk acceptance, evidence-driven autonomy change, guardrails, incident governance | Cross-cutting |

**Axis 2 — Evaluation Dimension (EV1–EV6): *how good* the answers are**, applied
*within* each area:

| | Dimension | Asks |
|---|---|---|
| EV1 | Correctness | Is it right? |
| EV2 | Completeness | Does it cover the task? |
| EV3 | Safety & Security | Is *this answer* safe? (the hard gate) |
| EV4 | Maintainability | Is it clean/readable? |
| EV5 | Efficiency | Is it economical? |
| EV6 | Traceability | Is it justified/auditable? |

So a run over **CA-05** with EV scores ~3.7/4 reads as: *"as a **coder**, its
answers were highly correct, complete, safe, … "* — it says **nothing** about
planning or security engineering, because those areas weren't tested.

> **EV3 ≠ CA-07.** EV3 (Safety & Security) asks whether *this particular answer*
> is safe — a quality check on every area. CA-07 (Security & Privacy
> Engineering) asks whether the model can *do security work* — a whole area. A
> high EV3 on a coding run does not make the model a good security engineer.

**To profile a model across the SDLC**, qualify several areas at once — pick them
with repeated `--area`, or `--all-areas` for the full CA-01…CA-12 sweep:

```
# selected roles:
aies qualify <deployment> --rt 2 --repeats 5 --judge <strong-independent-dep> \
  --area CA-02 --area CA-04 --area CA-05 --area CA-06 --area CA-07
# or the whole SDLC:
aies qualify <deployment> --rt 2 --repeats 5 --all-areas --judge <strong-dep>
```

Then read the whole capability profile in one table:

```
aies capabilities <run-id>        # or a deployment id (its latest aggregated run)
```

```
AREA   ROLE / SDLC PHASE                  CL   AGG   AL   GATES  SAMPLE
CA-04  Architecture & Solution Design     CL3  3.41  AL3  PASS   decisional
CA-05  AI-Assisted Implementation         CL3  3.46  AL3  PASS   decisional
CA-07  Security & Privacy Engineering     CL1  1.90  AL1  FAIL   decisional
```

That is the "how good at each phase" answer — *strong coder, weak security* — at
a glance. `aies compare` diffs two deployments area-by-area (same suite versions
only). **Reading the numbers within an area:** gates use the **lower 90 %
confidence bound** (the `decision_value`), not the mean; a result is only
**decisional** once the area has enough scored items (≥ 20/30/50/100 for
RT1–RT4), otherwise it is **NON-DECISIONAL** and cannot ground a grant.

### 5.3 Manual scoring (omit `--judge`)

Without `--judge`, `qualify` writes a `scoresheet.json` and stops. Open it and,
for each response, set an integer **0–4** on each EV1–EV6 dimension against the
rubric anchors, add your rater name, and write a finding for any score ≤ 2:

```
aies score <run-id>              # ingest the scores you wrote
aies qualify --resume <run-id>   # aggregate -> report
```

### 5.4 (Optional) Add a model reviewer

Have a second deployment critique and score the same responses, then assemble
the peer-review package. The platform drives the reviewer for you:

```
aies review <run> --model-reviewer local-gpt-oss --calibration anchors.json
```

`--model-reviewer` sends each candidate response to that deployment, asks for
structured EV1–EV6 scores, and ingests the parseable ones as `model`-kind
ratings (a reviewer that won't follow the contract simply contributes fewer
ratings — nothing is fabricated). The reviewer's scores only **count** if it is
qualified for review-class tasks (`--reviewer-qualified`) or passes bootstrap
calibration against human-scored anchors (`--calibration`); otherwise they are
**advisory only**. Divergences of ≥ 2 points between the human and the model
are surfaced for you to resolve — never averaged (§7).

### 5.5 Aggregate and report

```
aies qualify --resume <run>              # gated, weighted aggregation
aies report  <run> --format markdown     # or json, or html (--write)
```

The report shows per-dimension decision values (lower 90% confidence bounds),
gate outcomes, the aggregate, the score-bounded competency level, and the
recommended **RT × AL autonomy envelope** — never a global pass/fail.

### 5.6 Record the human decision, then verify

```
aies grant <run> --decision grant \
    --authority "Your Name (ROLE-13)" --second "Reviewer (ROLE-14)" \
    --rationale "pilot qualification"
aies qualifications list                 # the Qualification Record (QR-...)
aies verify QR-<...>                      # re-checks the environment fingerprint
aies dashboard --write                    # HTML overview of everything
```

The durable, auditor-facing **qualification report** is rendered from the
record itself:

```
aies report QUAL-2026-001 --format html --write   # writes reports/QUAL-2026-001.html
aies report list                                   # generated report artifacts
```

`grant` refuses non-decisional or gate-failing evidence and requires two named
humans — the platform never grants on its own. `verify` recomputes the
environment fingerprint through the deployment's adapter; if the model,
quantization, runtime, or host changed, the grant is **invalidated** and
re-qualification is required (D7), and `verify` exits non-zero so CI can gate
on it.

### 5.7 Worked example — a complete run against Ollama, start to finish

Concretely, qualifying a model served by Ollama as an RT2 software engineer
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

# 3. run the benchmark (RT2 needs >=30 scored items -> 8 repeats x 4 scenarios = 32)
aies qualify ollama-llama3.1-8b --profile coder --rt 2 --area CA-05 \
      --repeats 8 --parallel 4
#    prints a run id, e.g. run-YYYYMMDDT...-ollama-llama3.1-8b-ab12cd
#    and writes .../runs/<run>/scoresheet.json

# 4. score the responses (you, the human rater)
#    open scoresheet.json; for each item set EV1..EV6 to an integer 0-4
#    against the rubric, add "rater": {"name": "...", "kind": "human"},
#    and a finding for any score <= 2. then:
aies score <run>

# 5. aggregate and read the evidence
aies qualify --resume <run>
aies report <run> --format markdown         # or: --format html --write

# 6. (optional) add a second model as reviewer, then assemble the review
#    aies score <run> --file reviewer-scoresheet.json   # rater.kind = "model"
aies review <run> --reviewer some-reviewer-model

# 7. the human decision -> a Qualification Record
aies grant <run> --decision grant \
      --authority "Your Name (ROLE-13)" --second "Colleague (ROLE-14)" \
      --rationale "engineering pilot"
aies qualifications list
aies verify QR-<...>                # re-checks the environment fingerprint
aies dashboard --write              # HTML overview
```

What you get: a `report.md` with per-dimension decision values, gate results,
the aggregate, the score-bounded competency level, and the recommended RT×AL
envelope; and a Qualification Record (`QR-…`) recording the human grant, bound
to the exact model+environment it was earned on. Re-run `aies verify` any time
— if you swap the model, its quantization, or the runtime, the grant is
invalidated and you re-qualify.

Every other runtime is identical — just start its server and use the matching
deployment name (`lmstudio-…`, `llamacpp-…`, `mlx-…`).

## 6. Command cheatsheet — common recipes

Copy-paste starting points, grouped by task. Run `aies help` for the full
command tree (alphabetical) and `aies <command> --help` for every option.

**Setup & discovery**
```
aies doctor                              # which runtimes are reachable
aies discover                            # auto-register served models as deployments
aies runtime ollama                      # probe one runtime's endpoint
aies plugins list                        # installed runtime adapters + capabilities
```

**Register & fix deployments**
```
aies deployment add ./my-deployment.yaml     # register a NEW deployment
aies deployment add examples/deployments/claude-opus-4-8-native.yaml
aies deployment list                          # what is registered
aies deployment inspect local-qwen            # full manifest (base_url, api_key_env)
aies deployment update ./my-deployment.yaml   # fix an existing one in place (same id)
aies deployment remove local-qwen             # hard-delete; frees the id
aies deployment retire local-qwen             # soft-mark; id reserved for audit
```

**Run a qualification (automated judge)**
```
export AIES_MAX_TOKENS=1024                    # cap output → faster local runs
export ANTHROPIC_API_KEY=<key>                 # if the judge is a cloud model
aies qualify local-qwen --rt 2 --area CA-05 --repeats 5 \
  --judge claude-opus-4-8-native --parallel 8
aies qualify local-qwen --rt 2 --all-areas --repeats 5 \
  --judge claude-opus-4-8-native              # profile the whole SDLC
aies qualify local-qwen --rt 2 --area CA-05 --journey JOURNEY-01   # a multi-phase journey
```

**Run a qualification (manual human scoring)**
```
aies qualify local-qwen --rt 2 --area CA-05 --repeats 5    # writes scoresheet.json
# edit scoresheet.json: 0–4 per EV dimension, a rater, findings for ≤2
aies score run-2031                            # ingest your scores
aies qualify --resume run-2031                 # aggregate → report
```

**Re-score a run you already collected (e.g. the judge failed) — no re-collect**
```
aies review run-2031 --model-reviewer claude-opus-4-8-native --parallel 8
aies qualify --resume run-2031
```

**Read & interpret results**
```
aies transcript run-2031                       # whole run: task + answer + scores per item
aies transcript run-2031 --area CA-07          # just one area
aies capabilities run-2031                     # per-area profile: planner/coder/security/…
aies report run-2031 --format markdown         # the evidence report
aies runs                                      # result history
aies compare local-qwen other-model            # diff two deployments area-by-area
```

**Judges**
```
aies judge available                           # judges registered (roles:[judge]) + count
aies judge list                                # judges used, with parse rate
aies judge history --judge claude-opus-4-8-native
```

**Decision & audit (human)**
```
aies grant run-2031 --decision grant \
  --authority "Alex (ROLE-13)" --second "Sam (ROLE-14)"
aies qualification history                      # the QUAL-… records
aies verify QUAL-2026-001                        # re-check environment (D7)
aies conform check statement.yaml                # check a conformance claim
```

## 7. A note on trust

Every number the platform emits is evidence with full provenance (which model
build, which environment, which rater, which suite version), stored as plain
append-only files you can diff and audit. The gates and statistical minimums
are engine constants transcribed from [AIES-AESQS-CS-01](../AESQS/capability-scoring.md);
no profile or flag can relax them. The scoped grant is a human decision the
tool records — not one it makes.

## Related Documents

- [Platform Specification (AIES-DOC-06)](../docs/PLATFORM.md)
- [Platform README (AIES-PLAT-00)](README.md)
- [ADR-0002 — Qualification Platform](../adr/ADR-0002-Qualification-Platform.md)
- [AESQS Capability Scoring (AIES-AESQS-CS-01)](../AESQS/capability-scoring.md)
- [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

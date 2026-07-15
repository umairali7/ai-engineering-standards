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

### 5.2 Run the benchmark

```
aies qualify local-qwen --profile coder --rt 2 --area CA-05 --repeats 5 --parallel 4
```

This executes the CA-05 scenario suite against your model over real inference
calls and writes append-only response records plus a `scoresheet.json`. Pick
`--area` from `CA-01 … CA-12`; repeat for several areas. For a *decisional*
result an AI system needs ≥ 20 (RT1), 30 (RT2), 50 (RT3), 100 (RT4) scored
items per area — grow `--repeats` or the suites accordingly; under-sampled
runs are labelled **NON-DECISIONAL** and cannot be granted on.

### 5.3 Score the responses (human rater)

Open the printed `scoresheet.json` and, for each response, set an integer
**0–4** on each dimension EV1–EV6 against the rubric anchors, add your rater
name, and write a finding for any score ≤ 2. Then:

```
aies score local-qwen-run-id             # ingests your ratings as append-only records
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

## 6. A note on trust

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

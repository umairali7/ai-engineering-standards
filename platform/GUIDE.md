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

**Bring external eval results in as evidence.** If you already scored the
responses with another tool (a custom Inspect/DeepEval task, a second judge, an
offline pipeline) that emits EV1–EV6, import them as automated-kind ratings
(subject to the same calibration gate):

```
aies import <run-id> eval.json --source inspect:my-task
aies qualify --resume <run-id>
```

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

# 3. run the benchmark (RT2 needs >=30 scored items; CA-05 has ~10 distinct
#    RT2 scenarios, so 3 repeats x 10 = 30 — repeats now add variance, not padding)
aies qualify ollama-llama3.1-8b --profile coder --rt 2 --area CA-05 \
      --repeats 3 --parallel 4
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

### 5.8 Audit a repository (a different subject)

Everything above qualifies a **model**. `aies audit` assesses a **repository and
the engineering practice in it** against the twelve competency areas
([ADR-0004](../adr/ADR-0004-Repository-Conformance-Audit.md)) — the executable
form of [conformance](../docs/CONFORMANCE.md).

```
aies audit .                      # scorecard + ranked recommendations (markdown)
aies audit . --rt 2               # evaluate against RT2's required evidence
aies audit . --gate --rt 2        # CI mode: non-zero exit if RT2 evidence is missing
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
— a named qualification (enterprise, coder, security, architecture) whose
competency composition lives in `assessments/*.yaml`
([ADR-0005](../adr/ADR-0005-Assessment-as-Code.md), authoring guide
[ASSESSMENTS.md](ASSESSMENTS.md)):

```
aies assessment list                                        # what's shipped
aies qualify local-qwen --assessment enterprise --judge <judge>   # compose, score, decide
aies assessment result <run>                                # re-decide a run (no inference)
```

`--assessment` selects the competency set, profile, risk tier, and sampling. After
scoring, the platform decides an **authoritative outcome** —
`PASS / FAIL / INCONCLUSIVE / INSUFFICIENT EVIDENCE` — over the assessment's
**mandatory** competencies. It is **gate-first**: a strong competency never
offsets a failing one, and there is **no blended score**. Advisory competencies
and the numeric diagnostics/analytics are reported for feedback but never decide.
A `PASS` is an assessment outcome; a named human still records any grant.

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

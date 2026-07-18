# AIES Platform Reference

| | |
|---|---|
| **Document ID** | AIES-PLAT-09 |
| **Status** | Draft |
| **Audience** | Engineers · Integrators · Contributors |
| **Scope** | The vocabulary, the artifacts (with versions), and every `aies` command |

The single "explain everything" reference for the platform. For architecture and
setup see [GUIDE.md](GUIDE.md); for the specification see
[docs/PLATFORM.md](../docs/PLATFORM.md); for the contract freeze see
[STABILITY.md](../STABILITY.md).

---

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **Deployment** | The unit under assessment: model × runtime × config × endpoint (never a bare model — PLATFORM.md D11). Registered in the registry. |
| **Runtime / Adapter** | The vendor-aware code that talks to a deployment (`ollama`, `openai-compat`, `mock`, …). The **only** vendor-specific layer (D9); frozen contract v1.0 (semantic core stable, additive surface). |
| **Profile** | A weighting preset — per-area and per-dimension emphasis. Versioned (semver). Cannot express gates or minimums (D3). |
| **Assessment** | Declarative composition ([ADR-0005](../adr/ADR-0005-Assessment-as-Code.md)): which competencies compose a named qualification, mandatory vs advisory, weights, profile, risk tier, sampling. Data, not code. |
| **Competency Area (CA-01…CA-12)** | The twelve areas of AI-engineering capability (SDLC foundations, implementation, testing, security, governance, …). |
| **Risk Tier (RT1–RT4)** | The stakes of the scope. Higher tiers demand higher gates and larger samples. |
| **Dimension (EV1–EV6)** | The six scored qualities: Correctness, Completeness, Safety & Security, Maintainability, Efficiency, Traceability. 0–4 integer anchors. |
| **Competency Level (CL1–CL4)** | The competency a score supports at a tier. AI systems cap at CL3. |
| **Autonomy Level (AL0–AL4)** | How much independence a deployment may be granted; `min(risk-tier cap, CL-earned cap)`. |
| **Decision value** | The **lower bound** of a dimension's 90% confidence interval — never the mean (anti-optimism). |
| **Gate** | A hard per-dimension minimum (esp. EV3). A failed gate denies the tier; no profile can express or relax one. |
| **Decisional / NON-DECISIONAL** | Whether a result met the statistical minimum sample (20/30/50/100 for AI by tier). Under-sampled results can never look like qualification evidence. |
| **Evidence Package** | The aggregated, immutable record of a run's responses, ratings, and per-area results. Independently versioned (`evidence_schema`); can be replayed through a future engine. |
| **Canonical Assessment Result** | The single machine-readable object the decision engine produces: `{metadata, evidence, decisions, diagnostics, analytics}`. Versioned (`result_schema`). Every renderer is a view of it. |
| **Outcome** | `PASS` / `FAIL` / `INCONCLUSIVE` / `INSUFFICIENT EVIDENCE`, decided over **mandatory** competencies; precedence `FAIL > INCONCLUSIVE > INSUFFICIENT EVIDENCE > PASS`. No blended score. |
| **Reason kind** | Why a mandatory competency did not pass: `mandatory-gate`, `min-cl`, `insufficient-evidence`, `assessment-error`. |
| **Judge / Reviewer** | A model deployment that auto-scores another's responses. Its scores are advisory unless calibrated; never self-judge for a trustworthy read. |
| **Grant / Qualification Record** | The formal, revocable human decision recording a scoped qualification. **The platform never grants** — a named human authority does (D8). |
| **Conformance corpus** | Golden Evidence Packages + expected outcomes; the data-first arbiter that verifies any decision engine ([CONFORMANCE-POLICY.md](../CONFORMANCE-POLICY.md)). |

## 2. Artifacts (and their versions)

Every artifact carries a schema version; envelopes are field-append-only
([COMPATIBILITY.md](../COMPATIBILITY.md)).

| Artifact | Version field | Frozen at | Written by |
|---|---|---|---|
| Assessment | `schema` | `1` | authored (`assessments/*.yaml`) |
| Profile | `version` | semver | authored (`profiles/*.yaml`) |
| Evidence Package | `evidence_schema` | `1` | `qualify --resume` / `aggregate` |
| Canonical Assessment Result | `result_schema` | `1` | the decision engine |
| Decision semantics | `decision_semantics_version` | `1.0` (AESQS CS-01 §8) | the standard |

The result's `metadata` records both `decision_engine_version` (which software)
and `decision_semantics_version` (which policy), plus the `profile_version` and
`evidence_schema` it decided over — a certification is always traceable to its
exact inputs.

## 3. Commands

Every command supports `--json`. Commands that produce evidence write
append-only records. Grouped as in `aies --help`.

### Setup & discovery

| Command | Contract | Example |
|---|---|---|
| `doctor` | Validate + fingerprint the environment; detect installed runtimes | `aies doctor --json` |
| `discover` | Register the deployments each runtime serves (idempotent) | `aies discover` |
| `deployment` / `registry` | Manage deployment entries: add/show/update/remove/`verify-artifact` | `aies deployment verify-artifact local-qwen --artifact model.bin` |
| `runtime` | Inspect installed runtime adapters | `aies runtime list` |

### Qualification

| Command | Contract | Example |
|---|---|---|
| `qualify` | Full pipeline for a deployment → evidence package. `--assessment`, `--judge`, `--all-areas`, `--journey`, `--parallel`, `--repeats`, `--resume`, `--resume-collection` | `aies qualify local-qwen --assessment enterprise --judge gpt-oss` |
| `benchmark` | Execute scenario suites only (stage 4) | `aies benchmark acme-7b --area CA-05 --repeats 5` |
| `score` | Ingest a filled scoresheet (human/model rater) | `aies score run-2031` |
| `import` / `export` | Bring external eval results in as EV evidence / round-trip out | `aies import run-2031 eval.json` |
| `capabilities` | Per-area CL + autonomy + gate + decisional status, side by side | `aies capabilities run-2031` |
| `assessment` | `list` / `show` / `validate` / `result <run>` (Markdown/JSON/`--format html`) | `aies assessment result run-2031` |
| `review` | Multi-model peer review + calibration gate | `aies review run-2031 --model-reviewer rev` |
| `compare` | Deltas across runs on identical suite versions | `aies compare a b --profile coder` |
| `runs` / `transcript` | List runs / render a whole run (task + answer + scores) | `aies transcript run-2031` |

### Judging

| Command | Contract | Example |
|---|---|---|
| `judge available` | The deployments eligible to judge | `aies judge available` |
| `judge list` / `judge history` | Judge track record (runs judged, parse rate, self-judged flags) | `aies judge list` |

### Decision & audit

| Command | Contract | Example |
|---|---|---|
| `report` | Render an evidence package / record as Markdown, JSON, or HTML | `aies report run-2031 --format html --write` |
| `grant` | Record a formal, revocable human qualification decision | `aies grant run-2031 --decision grant --authority "…" --second "…"` |
| `qualification` | List/show/revoke Qualification Records | `aies qualification list` |
| `verify` | Re-check the environment fingerprint (D7); non-zero if invalidated | `aies verify QUAL-2026-001` |
| `audit` | Audit a *repository's* AIES engineering practice (maturity ML0–ML4) | `aies audit . --gate --rt 2` |
| `conform check` | Check a conformance *statement* against CONFORMANCE.md | `aies conform check statement.yaml` |
| `conform engine` | Verify the *decision engine* against the golden corpus | `aies conform engine` |
| `dashboard` | Render an HTML overview (a renderer — computes no outcomes) | `aies dashboard --write` |
| `serve` | Thin read-only REST API over the canonical artifacts | `aies serve --port 8722` |

### Reference

| Command | Contract | Example |
|---|---|---|
| `profiles` | List/show/validate/scaffold weighting profiles | `aies profiles show enterprise` |
| `suites validate` | Validate the suite catalog **and** the shipped assessments (CI gate); validates `calibration` blocks when present | `aies suites validate` |
| `suites calibrate` | Calibration-coverage report — how far each scenario has progressed as a measurement instrument ([CALIBRATION.md](CALIBRATION.md)); advisory | `aies suites calibrate` |
| `suites empirical` | Phase-2 empirical calibration — per-scenario discrimination/repeatability/twin-robustness. Give a panel JSON, or **auto-assemble** it from scored runs with `--runs RUN=ABILITY` | `aies suites empirical --runs run-strong=3 run-weak=1` |
| `corpus health` / `corpus coverage` | Advisory quality review of the assessment corpus *itself* — calibration, coverage, behavioral diversity, duplication, empirical maturity, each with evidence + ranked recommendations. **Multidimensional, no single grade, never a gate** | `aies corpus health` |
| `corpus duplicates` | Deterministic near-duplicate detection (prompt-shingle + ceiling overlap), **twin-aware** — flags non-twin redundancy candidates, and hold-out twins that are *too* similar on the surface | `aies corpus duplicates` |
| `journey` | Inspect multi-phase lifecycle scenarios | `aies journey list` |
| `index` | Rebuildable SQLite index over the append-only records | `aies index` |
| `plugins` | Installed runtime adapters + declared capabilities | `aies plugins list` |

## 4. REST API (read-only)

`aies serve` exposes the canonical artifacts as JSON. It is a **consumer, not a
decider** — it serves stored results verbatim and computes no outcome
(CONFORMANCE-POLICY.md §4). Endpoints:

```
GET /health                    service + version
GET /deployments               registered deployments
GET /runs                      run history
GET /runs/{id}/evidence        the Evidence Package
GET /runs/{id}/result          the Canonical Assessment Result (verbatim)
GET /assessments               shipped assessments
GET /qualifications            Qualification Records
GET /conformance               decision-engine conformance report
```

`POST` is refused (405): mutation goes through the CLI, and outcomes are decided
by the engine, never by a consumer.

## 5. Exit codes

| Code | Meaning |
|---|---|
| `0` | success (and, where applicable, PASS / conformant / substantiated) |
| `1` | a decided negative (e.g. `assessment result` outcome is not PASS) |
| `2` | usage / not-found / invalid input |
| `5` | a gate failed (unsupported conformance claim, non-conformant engine, audit gate) |

## Related Documents

- [GUIDE.md](GUIDE.md) — architecture + setup + real-model runs
- [ASSESSMENTS.md](ASSESSMENTS.md) · [PROFILES.md](PROFILES.md) · [RUNTIMES.md](RUNTIMES.md) · [SCENARIOS.md](SCENARIOS.md)
- [STABILITY.md](../STABILITY.md) · [COMPATIBILITY.md](../COMPATIBILITY.md) · [CONFORMANCE-POLICY.md](../CONFORMANCE-POLICY.md)
- [docs/PLATFORM.md](../docs/PLATFORM.md) — the platform specification

# AIES Platform Reference

| | |
|---|---|
| **Document ID** | AIES-PLAT-09 |
| **Status** | Draft |
| **Audience** | Engineers · Integrators · Contributors |
| **Scope** | The vocabulary, the artifacts (with versions), and every `aies` command |

The compact "explain the contracts" reference for the platform. For architecture
and setup see [GUIDE.md](GUIDE.md); for exhaustive command syntax,
prerequisites, parameter interactions, side effects, and sequences see the
generated [CLI Reference](CLI_REFERENCE.md); for the specification see
[docs/PLATFORM.md](../docs/PLATFORM.md); for the contract freeze see
[STABILITY.md](../STABILITY.md).

---

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **Deployment** | The unit under assessment: model × runtime × config × endpoint (never a bare model — PLATFORM.md D11). Registered in the registry. |
| **Runtime / Adapter** | The vendor-aware code that talks to a deployment (`ollama`, `openai-compat`, `mock`, …). The **only** vendor-specific layer (D9); frozen contract v1.0 (semantic core stable, additive surface). |
| **Profile** | A weighting preset — per-area and per-dimension emphasis. Versioned (semver). Cannot express gates or minimums (D3). |
| **Assessment** | Declarative composition ([ADR-0005](../adr/ADR-0005-Assessment-as-Code.md)): competencies, mandatory vs advisory status, weights, profile, risk tier, and sampling. It drives engineering evaluation by default and formal qualification only when explicitly requested. |
| **Competency Area (CA-01…CA-12)** | The twelve areas of AI-engineering capability (SDLC foundations, implementation, testing, security, governance, …). |
| **Risk Tier (RT1 — Minimal through RT4 — Critical)** | The stakes of the scope. Higher tiers demand higher gates and larger samples. |
| **Dimension (EV1–EV6)** | The six scored qualities: Correctness, Completeness, Safety & Security, Maintainability, Efficiency, Traceability. 0–4 integer anchors. |
| **Competency Level (CL1–CL4)** | The competency a score supports at a tier. AI systems cap at CL3. |
| **Autonomy Level (AL0 — Manual through AL4 — Autonomous)** | How much independence a deployment may be granted; `min(risk-tier cap, CL-earned cap)`. |
| **Decision value** | The **lower bound** of a dimension's 90% confidence interval — never the mean (anti-optimism). |
| **Gate** | A hard per-dimension minimum (esp. EV3). A failed gate denies the tier; no profile can express or relax one. |
| **Decisional / NON-DECISIONAL** | Whether a result met the statistical minimum sample (20/30/50/100 for AI by tier). Under-sampled results can never look like qualification evidence. |
| **Evidence Package** | The aggregated, immutable record of a run's responses, ratings, and per-area results. Independently versioned (`evidence_schema`); can be replayed through a future engine. |
| **Engineering Assessment Result** | Default non-blocking named-assessment artifact: `COMPLETE`, `PARTIAL`, or `NOT SCORED`, with automated coverage and optional human evaluation. |
| **Canonical Formal Assessment Result** | Explicit formal-qualification object from the decision engine: `{metadata, evidence, decisions, diagnostics, analytics}`. Versioned (`result_schema`). |
| **Outcome** | `PASS` / `FAIL` / `INCONCLUSIVE` / `INSUFFICIENT EVIDENCE`, decided over **mandatory** competencies; precedence `FAIL > INCONCLUSIVE > INSUFFICIENT EVIDENCE > PASS`. No blended score. |
| **Reason kind** | Why a mandatory competency did not pass: `mandatory-gate`, `min-cl`, `insufficient-evidence`, `assessment-error`. |
| **Judge / Reviewer** | A deployment that auto-scores another's responses. Its scores complete engineering evaluation; formal qualification admission is separately governed. Never self-judge for a trustworthy read. |
| **Grant / Qualification Record** | The formal, revocable human decision recording a scoped qualification. **The platform never grants** — a named human authority does (D8). |
| **Conformance corpus** | Golden Evidence Packages + expected outcomes; the data-first arbiter that verifies any decision engine ([CONFORMANCE-POLICY.md](../CONFORMANCE-POLICY.md)). |

## 2. Artifacts (and their versions)

Every artifact carries a schema version; envelopes are field-append-only
([COMPATIBILITY.md](../COMPATIBILITY.md)).

| Artifact | Version field | Frozen at | Written by |
|---|---|---|---|
| Assessment | `schema` | `1` | authored (`assessments/*.yaml`) |
| Profile | `version` | semver | authored (`profiles/*.yaml`) |
| Evidence Package | `evidence_schema` | `5` | `qualify --resume` / `aggregate` |
| Human Rater Record | `rater_schema` | `1` | `rater register` |
| Qualification Record | `qualification_schema` | `2` | `grant` (human authority) |
| Qualification Lifecycle Event | `event_schema` | `1` | `qualifications event` / `verify` |
| Engineering Evaluation Summary | `evaluation_schema` | `1` | every complete report bundle (`engineering-evaluation.json`) |
| Engineering Assessment Result | `engineering_assessment_schema` | `1` | default named engineering assessment |
| Canonical Formal Assessment Result | `result_schema` | `1` | explicit formal decision engine |
| Decision semantics | `decision_semantics_version` | `1.0` (AESQS CS-01 §8) | the standard |
| Engineering Task Mapping *(review-stage)* | `schema` | `2` | authored (`task_mappings/*.yaml`) |
| Engineering Capability Matrix *(review-stage)* | `ecm_schema` | `2` | `capabilities` / report bundle |
| ECM task-decision semantics *(review-stage)* | `task_decision_semantics_version` | `1.0` | ADR-0013 |
| Deployment Guidance *(review-stage)* | `guidance_schema` | `2` | `guidance` |
| Engineering Fit Guidance | `engineering_fit_schema` | `1` | default `guidance` / report bundle |
| Executive Summary | `executive_summary_schema` | `2` | complete report bundle |
| Grounding Diagnostics | `diagnostic_schema` | `1` | complete report bundle; structured reviewer observations |
| Report Bundle Index | `report_bundle_schema` | `1` | complete report bundle |

The result's `metadata` records both `decision_engine_version` (which software)
and `decision_semantics_version` (which policy), plus the `profile_version` and
`evidence_schema` it decided over — a certification is always traceable to its
exact inputs.

### 2.1 Workspace storage classes

The workspace distinguishes persistence semantics explicitly; “JSON file” does
not imply one universal mutation rule.

| Class | Examples | Mutation contract |
|---|---|---|
| Append-only record | responses, rating observations, resolutions, human-rater records, Qualification Records and lifecycle events, audit records | Created once; replacement is rejected. Corrections are new records or events. |
| Derived canonical snapshot | `evidence-package.json`, `assessment-result.json`, `review-package.json` | Recomputed only when its recorded source evidence changes; the schema and source provenance remain explicit. |
| Mutable working state | `manifest.json`, `scoresheet.json`, `progress.json`, latest fingerprint | May be replaced by its owning workflow while work progresses. |
| Regenerable view | Markdown/JSON/HTML reports, Engineering Assessment Result, ECM, Engineering Fit/Deployment Guidance, Executive Summary, Grounding Diagnostics, dashboard, bundle index | May be replaced at any time from canonical records; never treated as source evidence. |
| Mutable configuration | deployment registry entries | Updated only through the registry workflow; identity changes trigger qualification verification. |

`workspace.artifact_class`, `workspace.write_json`, and
`workspace.write_view` enforce the append-only/view boundary. Renderer code
cannot use the view writer to replace evidence records.

## 3. Commands

Every command supports `--json`. Commands that produce evidence write
append-only records. Grouped as in `aies --help`.

### Setup & discovery

| Command | Contract | Example |
|---|---|---|
| `doctor` | Validate and fingerprint the environment, detect installed runtimes, and report archive/cache/misplaced-view workspace debris without deleting anything | `aies doctor --json` |
| `discover` | Register the deployments each runtime serves (idempotent) | `aies discover` |
| `support` | Show implemented, experimental, and planned subject kinds from the shipped registry | `aies support mcp-server` |
| `starter list` / `starter show` | Choose a decision-led workflow and inspect its prerequisites, sequence, evidence, time/cost class, artifacts, and limitations without executing it | `aies starter show understand-deployment` |
| `deployment` / `registry` | Manage deployment entries: add/show/update/remove/`verify-artifact` | `aies deployment verify-artifact local-qwen --artifact model.bin` |
| `runtime` | Inspect installed runtime adapters | `aies runtime list` |

### Engineering evaluation and optional qualification

| Command | Contract | Example |
|---|---|---|
| `qualify` | Full pipeline for a deployment → engineering evaluation and evidence package. Live progress is implicit; an automated judge can complete the evaluation without human review. `--assessment`, `--judge`, `--all-areas`, `--journey`, `--parallel`, `--repeats`, `--resume`, `--resume-collection` | `aies qualify local-qwen --assessment enterprise --judge gpt-oss` |
| `benchmark` | Run a non-blocking engineering benchmark; without `--judge` it collects responses, while `--judge` also scores, analyzes, and writes the complete bundle | `aies benchmark acme-7b --area CA-05 --judge gpt-oss` |
| `score` | Ingest a filled scoresheet, aggregate, and refresh the complete engineering report bundle | `aies score run-2031` |
| `rater` | Register/list/show durable human identity, competency/risk scope, qualification, and calibration | `aies rater register --id alice --name "Alice" --area CA-05 --rt 2 ...` |
| `resolve` | Append a named, reasoned human disposition for a materially divergent evidence item | `aies resolve run-2031 SC-CA05-001-r1.json --scores 4 4 3 4 3 4 ...` |
| `import` / `export` | Import external EV results plus aggregate/report in one command / round-trip out | `aies import run-2031 eval.json` |
| `capabilities` | ECM task performance/evidence/confidence by default; `--qualification-profile` selects formal CL/autonomy/gates | `aies capabilities run-2031 --format html --write` |
| `snapshot` | Responsive terminal Evidence → Capability → Confidence → Engineering Decisions projection over canonical ECM/Fit facts | `aies snapshot latest` |
| `assessment` | `result <run>` renders non-blocking engineering status; `--formal-qualification` selects the formal outcome | `aies assessment result run-2031` |
| `review` | Automated review, optional human-evaluation record, implicit live progress, and refreshed report bundle | `aies review run-2031 --model-reviewer rev` |
| `compare` | Compatible observed ECM scores compare by default without human review; `--formal-qualification` additionally requires demonstrated status/protocol before a winner claim; `--area-summary` selects the legacy aggregate | `aies compare run-a run-b` |
| `guidance` | Engineering Fit Guidance by default; `--qualification QUAL-id` selects qualification-bounded Deployment Guidance | `aies guidance run-2031 --write` |
| `runs list` / `runs progress` / `transcript` | List runs, optionally observe another command's durable progress from a second terminal, or render a whole run. The originating command already shows stage and total timing, ETA, plus the current human-readable task and task ordinal. | `aies runs progress run-2031` |

### Judging

| Command | Contract | Example |
|---|---|---|
| `judge available` | The deployments eligible to judge | `aies judge available` |
| `judge list` / `judge history` | Judge track record (runs judged, parse rate, self-judged flags) | `aies judge list` |

### Decision & audit

| Command | Contract | Example |
|---|---|---|
| `report` | Render an evidence package / record as Markdown, JSON, or HTML | `aies report run-2031 --format html --write` |
| `grant` | Record a formal, scoped two-human qualification decision; v5 requires durable assessor/peer ids, conflict declarations, role/phases/sponsor/framework, and validity | `aies grant run-2031 --decision grant --authority "Authority" --assessor-id alice --peer-reviewer-id bob ...` |
| `qualifications` | List/show/revoke records or append governed condition/renewal/suspension/invalidation/revocation/supersession events | `aies qualifications event QUAL-2026-001 --event suspended --authority "Authority" --reason "incident"` |
| `verify` | Re-check expiry and the deployment fingerprint (D7); non-zero if expired or invalidated | `aies verify QUAL-2026-001` |
| `audit` | Audit a *repository's* AIES engineering practice (maturity ML0–ML4) | `aies audit . --gate --rt 2` |
| `conform check` | Check a conformance *statement* against CONFORMANCE.md | `aies conform check statement.yaml` |
| `conform engine` | Verify a *decision engine* against the golden corpus — the reference engine, or a **foreign** one via `--engine "<cmd>"` (reads evidence+assessment JSON on stdin, prints the result) so independent implementations self-check | `aies conform engine --engine "python conformance/example_engine.py"` |
| `dashboard` | Render an HTML overview (a renderer — computes no outcomes) | `aies dashboard --write` |
| `serve` | Thin read-only REST API over the canonical artifacts | `aies serve --port 8722` |

### Reference

| Command | Contract | Example |
|---|---|---|
| `profiles` | List/show/validate/scaffold weighting profiles | `aies profiles show enterprise` |
| `suites validate` | Validate the suite catalog **and** the shipped assessments (CI gate); validates `calibration` blocks when present | `aies suites validate` |
| `suites calibrate` | Calibration-coverage report — how far each scenario has progressed as a measurement instrument ([CALIBRATION.md](CALIBRATION.md)); advisory | `aies suites calibrate` |
| `suites empirical` | Phase-2 empirical calibration — create a content-addressed plan before runs with `--create-plan`; inspect legacy compatibility with `--preflight-runs`; bind completed runs with `--panel-plan … --planned-runs`. Promotion eligibility requires the frozen plan and rejects mismatched subjects, suites, prompts, samples, protocols, unrated responses, and duplicate/correction ratings. | `aies suites empirical --create-plan panel-plan.json …` |
| `corpus health` / `corpus coverage` | Advisory quality review of the assessment corpus *itself* — calibration, coverage, behavioral diversity, duplication, empirical maturity, each with evidence + ranked recommendations. **Multidimensional, no single grade, never a gate** | `aies corpus health` |
| `corpus duplicates` | Deterministic near-duplicate detection (prompt-shingle + ceiling overlap), **twin-aware** — flags non-twin redundancy candidates, and hold-out twins that are *too* similar on the surface | `aies corpus duplicates` |
| `corpus review` | Review one scenario as a measurement instrument — deterministic structural checks always, plus an **opt-in model critique** (`--reviewer <deployment>`). Critique only: never rewrites, approves, or scores | `aies corpus review SC-CA07-015 --reviewer gpt-oss` |
| `journey` | Inspect multi-phase lifecycle scenarios | `aies journey list` |
| `index` | Rebuildable SQLite index over the append-only records | `aies index` |
| `plugins` | Installed runtime adapters + declared capabilities | `aies plugins` |
| `completion` | Generate parser-derived Tab completion for PowerShell, Bash, or Zsh | `aies completion powershell` |

## 4. REST API (read-only)

`aies serve` exposes the canonical artifacts as JSON. It is a **consumer, not a
decider** — it serves stored results verbatim and computes no outcome
(CONFORMANCE-POLICY.md §4). Endpoints:

```
GET /health                    service + version
GET /support                   implemented/experimental/planned subject support
GET /deployments               registered deployments
GET /runs                      run history
GET /runs/{id}/evidence        the Evidence Package
GET /runs/{id}/result          primary Engineering or legacy Formal Result
GET /runs/{id}/formal-result   explicit Canonical Formal Assessment Result
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
| `1` | an explicitly requested formal/CI gate decided negative; default Engineering Assessment Result rendering does not use human readiness as an exit gate |
| `2` | usage / not-found / invalid input |
| `5` | a gate failed (unsupported conformance claim, non-conformant engine, audit gate) |

## Related Documents

- [GUIDE.md](GUIDE.md) — architecture + setup + real-model runs
- [ASSESSMENTS.md](ASSESSMENTS.md) · [PROFILES.md](PROFILES.md) · [RUNTIMES.md](RUNTIMES.md) · [SCENARIOS.md](SCENARIOS.md)
- [STABILITY.md](../STABILITY.md) · [COMPATIBILITY.md](../COMPATIBILITY.md) · [CONFORMANCE-POLICY.md](../CONFORMANCE-POLICY.md)
- [docs/PLATFORM.md](../docs/PLATFORM.md) — the platform specification

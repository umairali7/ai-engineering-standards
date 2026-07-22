# Engineering Assessment Platform Specification

| | |
|---|---|
| **Document ID** | AIES-DOC-06 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Contributors & maintainers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

This document specifies the **AIES Engineering Assessment Platform**: the `aies` command-line tool and Python package (under `platform/`) that prepares canonical evidence, qualification evidence, conformance evidence, and engineering decision products. The current executable adapters assess AI deployments and repositories; its subject-neutral evidence and ECM architecture is designed to extend to agents, MCP servers, RAG systems, pipelines, and platforms without rebranding the product. The original model-only platform decision is superseded by [ADR-0009](../adr/ADR-0009-Engineering-Assessment-Platform-Identity.md).

---

## 1. Purpose & Positioning

AESQS defines *how* to determine, with evidence, what an AI system may be trusted to do. The platform is the **execution engine of that standard** — it is to AESQS what `terraform` is to an infrastructure definition or `pytest` is to a test convention: the standard remains normative and tool-independent; the platform makes it runnable, repeatable, and cheap to apply.

The platform answers a practical question the standard alone cannot: *given this model, in this quantization, on this machine, under this runtime — what engineering work can it be trusted with, and at what autonomy?* It does so by driving the full AESQS pipeline — evidence generation, rubric scoring, gated aggregation, statistics, review orchestration — and emitting **Qualification Records**: evidence-grade, registry-ready artifacts with complete provenance (ART-15).

The platform is **local-first**: it MUST be able to run a complete qualification against a locally hosted model with no external network dependency. Remote (hosted) models are supported through the same plugin boundary (§8).

The platform prepares evidence; it does not grant qualifications. A human qualification authority (ROLE-13/ROLE-14 per [AIES-AESQS-QP-01-R01 — Qualification Process, requirement 01](../AESQS/qualification-process.md)) makes every grant. See §7 and §11 (D8).

## 2. The Qualification Pipeline

```
 ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
 │ 1. Model         │   │ 2. Capability    │   │ 3. Environment   │   │ 4. Benchmark     │
 │    Registration  ├──►│    Discovery     ├──►│    Validation    ├──►│    Execution     │
 │  (registry entry)│   │  (probe suite)   │   │  (fingerprint)   │   │  (scenario runs) │
 └─────────────────┘   └─────────────────┘   └─────────────────┘   └────────┬────────┘
                                                                            │
 ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌────────▼────────┐
 │ 8. Deployment-   │   │ 7. Qualification │   │ 6. Multi-Model   │   │ 5. Scoring       │
 │    Role          │◄──┤    Decision      │◄──┤    Peer Review   │◄──┤  (EV1–EV6, gates,│
 │    Recommendation│   │  (human grants)  │   │  (human-approved)│   │   statistics)    │
 └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

| # | Stage | What it does | AESQS / Taxonomy clauses implemented |
|---|-------|--------------|--------------------------------------|
| 1 | **Model Registration** | Records the candidate's identity and configuration as a registry entry (§5.1): family, parameters, quantization, runtime, license, context window, modalities, capability flags. The entry is the platform analogue of an agent-definition version (ART-14). | [AIES-AESQS-QP-01-R02 — Qualification Process, requirement 02](../AESQS/qualification-process.md) (subject identity), AIES-AESQS-QP-01 §7 (configuration-bound validity) |
| 2 | **Capability Discovery** | Runs automated probes (coding, reasoning, structured-output/schema adherence, function calling, long context, retrieval-grounded answering, query languages, planning, vision where claimed) to establish which competency areas are even in scope. Discovery narrows scope; it never awards scores. | AIES-AESQS-QP-01 §2 (scoping); [AIES-AESQS-QP-01-R05 — Qualification Process, requirement 05](../AESQS/qualification-process.md) (no vendor claims — capabilities are probed, not read from marketing) |
| 3 | **Environment Validation** | Fingerprints the execution environment (§5.5): machine, CPU/GPU, memory, runtime and version, OS, power/thermal state. Model behavior is a property of model × environment; the fingerprint is provenance and its change is a re-qualification trigger. | [AIES-AESQS-QP-01-R10 — Qualification Process, requirement 10](../AESQS/qualification-process.md) (full provenance), [AIES-AESQS-RR-01 — Revision and Revocation §2](../AESQS/revision-and-revocation.md) (model/context change triggers — see §11 D7) |
| 4 | **Benchmark Execution** | Executes versioned, held-out scenario suites grouped by competency area (12 areas × ~16 scenarios and growing, 189 total), including repeated runs for variance and refuse/escalate scenarios at RT3 — Significant through RT4 — Critical scope. Every run is recorded; none may be discarded. | [AIES-AESQS-QP-01-R08 — Qualification Process, requirement 08](../AESQS/qualification-process.md) (golden-task suites), [AIES-AESQS-CS-01-R10 — Minimum samples and repeated runs are required](../AESQS/capability-scoring.md) (repeats, anti-cherry-picking) |
| 5 | **Scoring** | Scores each evidence item on the EV1–EV6 rubrics with 0–4 anchors; aggregates with risk-tier weights and profile weights; enforces minimum gates and statistical minimums; computes confidence intervals whose lower bounds are the decision values. | [AIES-AESQS-ER-01 — Evaluation Rubrics §1–§2](../AESQS/evaluation-rubrics.md), [AIES-AESQS-CS-01 — Capability Scoring §1–§6](../AESQS/capability-scoring.md) |
| 6 | **Multi-Model Peer Review** | Orchestrates candidate → reviewer critique → candidate revision → moderator adjudication, producing a structured review package for the human reviewer. Model reviews inform; they do not decide (§7). | [AIES-AESQS-PR-01-R09 — Peer Review, requirement 09](../AESQS/peer-review.md) (AI assists at AL2 — Collaborative or below; conclusion is human), [AIES-AESQS-ER-01-R10 — Evaluation Rubrics, requirement 10](../AESQS/evaluation-rubrics.md) (calibrated automated raters, never sole basis) |
| 7 | **Qualification Decision** | Presents the assembled evidence, scores, gates, and review package to the human qualification authority, who records Grant / Grant-with-conditions / Deny. The platform writes the resulting Qualification Record and audit events. | [AIES-AESQS-QP-01-R12 — Qualification Process, requirement 12](../AESQS/qualification-process.md), [AIES-AESQS-00-R04 — Qualification Standard, requirement 04](../AESQS/README.md) (audit trail) |
| 8 | **Deployment-Role Recommendation** | Maps awarded CLs per competency area to deployment-role recommendations ([ROLE-01 — Planner through ROLE-14 — Governance Officer](../Shared/Taxonomy/README.md#5-ai-engineering-roles)), each with an RT×AL envelope computed as min(risk-tier cap, CL-earned cap). Never a global pass/fail. | [AIES-AESQS-CS-01 — Capability Scoring §4–§5](../AESQS/capability-scoring.md), [Taxonomy §3–§4](../Shared/Taxonomy/README.md) |

## 3. CLI Surface

The `aies` command exposes the pipeline as composable verbs:

| Verb | Contract (one line) | Example |
|------|---------------------|---------|
| `discover` | Scan installed runtimes and register the deployments they serve as named registry entries (§5.1, D11). Idempotent. | `aies discover` |
| `registry` / `deployment` | Manage deployment entries: add, inspect/show, update (edit in place), retire, remove, and `verify-artifact` (recompute a local artifact's SHA-256 vs the declared `provenance.checksum`, and verify a detached signature if a key is provided). IDs never reused. | `aies deployment verify-artifact local-qwen --artifact ./model.safetensors` |
| `doctor` | Validate and fingerprint the environment; **detect installed runtimes** and, per runtime, availability, version, and what it serves; report readiness; write the fingerprint used by later stages. | `aies doctor --json` |
| `qualify` | Run the full pipeline (stages 2–6) for one **deployment** (by id, or by model name disambiguated with `--runtime`) against a profile and scope, producing a decision-ready evidence package. With `--judge <deployment>` (or `$AIES_JUDGE`) the responses are auto-scored by a judge model and the report is produced directly — no manual scoring step; without it, a human scores the generated scoresheet. | `aies qualify local-qwen --profile enterprise --rt 2 --judge gpt-oss` |
| `benchmark` | Execute one or more scenario suites (stage 4 only), with repeat counts and parallelism, appending evidence records. | `aies benchmark acme-7b-q4 --area CA-05 --repeats 5` |
| `review` | Orchestrate multi-model peer review over an existing evidence package and assemble the human review package. | `aies review run-2031 --reviewer rev-model --moderator mod-model` |
| `compare` | Compare qualification results across models, runs, or environments on the same suite versions. | `aies compare acme-7b-q4 beta-13b-q5 --profile coder` |
| `report` | Render an evidence package or Qualification Record as Markdown, JSON, or self-contained HTML (PDF via browser print). Evidence-package generation also writes linked informational ECM Markdown/JSON/HTML companions. | `aies report run-2031 --format html --write` |
| `transcript` | Render a whole run in one readable view — per item the task, the model's answer, and its scores/findings — so a reviewer need not open per-response records. | `aies transcript run-2031` |
| `score` / `import` / `export` | `score` ingests a filled scoresheet (human/model rater); `import` ingests external eval results (EV1–EV6 JSON) into a run as **automated**-kind ratings; `export` writes a run's prompts+responses+scores to a generic eval-log JSON that round-trips through `import` — the ecosystem bridge. | `aies export run-2031 --write` |
| `qualify --resume-collection` | Fill only the **missing** responses of a partially-collected run (e.g. after an endpoint failure), then rebuild the scoresheet — no re-collecting what succeeded. | `aies qualify --resume-collection run-2031` |
| `capabilities` | Per-area capability profile of an aggregated run/deployment — every competency area (CA-01…CA-12) scored, with its CL, aggregate, autonomy level at the scoped tier, gate result, and decisional status, side by side. `--ecm` additionally renders the informational, task-mapped Engineering Capability Matrix: observed performance, evidence confidence, source scenario families, and explicit `not assessed` gaps. Every matrix is scoped to the source run's one risk tier; `not assessed` means unknown in that scope, not failed. It does not grant deployment authority. | `aies capabilities run-2031 --ecm --write` |
| `assessment` | Declarative qualification composition ([ADR-0005](../adr/ADR-0005-Assessment-as-Code.md)): `list`/`show`/`validate` the assessments (which competencies compose a named qualification, mandatory vs advisory, weights, profile), and `result <run>` to decide a run's outcome (Markdown/JSON/`--format html`). `qualify --assessment <name>` composes + scores + decides. Outcome is `PASS/FAIL/INCONCLUSIVE/INSUFFICIENT EVIDENCE` (gate-first, no blended score). Shipped assessments are validated by `aies suites validate` — the gate CI runs. | `aies qualify local-qwen --assessment enterprise --judge gpt-oss` |
| `audit` | Audit a **repository's** conformance to AIES engineering practices ([ADR-0004](../adr/ADR-0004-Repository-Conformance-Audit.md)) — a different subject from `qualify`. Scores maturity ML0–ML4 per competency area with three-state evidence (verified/asserted/gap, never false-green); ranked recommendations; `--gate --rt N` for CI; `--attest` for non-detectable practices. | `aies audit . --gate --rt 2` |
| `judge` | Judge track record derived from model-kind ratings across runs: `judge list` (deployments that have judged, runs judged, responses scored, parse rate, self-judged/unregistered flags) and `judge history` (one row per judged run). | `aies judge list` |
| `profiles` | List, show, validate, and scaffold weighting profiles (§5.2). | `aies profiles show enterprise` |
| `plugins` | List installed runtime plugins, their versions, and the capabilities each declares. | `aies plugins list` |
| `conform` | Scaffold and check conformance statements against the model in [CONFORMANCE.md (AIES-DOC-08 — Conformance Guide)](CONFORMANCE.md); verify evidence-backed claims against Qualification Records. | `aies conform check statement.yaml` |

Every verb MUST support `--json` output for automation, and every verb that produces evidence MUST write append-only records (§5.5).

## 4. Package Architecture

```
                       ┌───────────────┐
                       │      CLI      │  argument parsing, output rendering
                       └───────┬───────┘
                               ▼
                       ┌───────────────┐        ┌────────────────┐
                       │ Qualification │◄───────┤ Profile Loader │  profiles + immutable gates
                       │    Engine     │        └────────────────┘
                       └───────┬───────┘
                    ┌──────────┼─────────────────────┐
                    ▼          ▼                     ▼
            ┌────────────┐ ┌────────────┐    ┌──────────────┐
            │ Test Runner│ │ Evaluation │    │   Scoring    │
            │            │ │   Engine   │    │   Engine     │
            └─────┬──────┘ └────────────┘    └──────┬───────┘
                  ▼                                 ▼
            ┌────────────┐                   ┌──────────────┐    ┌────────────────┐
            │  Runtime   │                   │    Report    ├───►│ Qualification  │
            │  Plugin    │                   │  Generator   │    │    Record      │
            └────────────┘                   └──────────────┘    └────────────────┘
```

| Component | Responsibility |
|-----------|----------------|
| **CLI** | Verb dispatch, argument validation, human/JSON output. No qualification logic. |
| **Qualification Engine** | Orchestrates the pipeline: sequences stages, enforces preconditions (registered model, valid fingerprint, suite versions), assembles the evidence package and decision workflow. |
| **Profile Loader** | Loads and validates weighting profiles; guarantees gates and statistical minimums cannot be weakened by any profile (§5.2, §6). |
| **Test Runner** | Executes scenario suites against the candidate via a runtime plugin: prompt assembly, repeats, timeouts, parallel execution (M3), full raw capture. |
| **Runtime Plugin** | The only component that talks to a model runtime or provider (§8). Vendor- and runtime-specific code lives here and nowhere else. |
| **Evaluation Engine** | Applies test-case rubrics to raw responses, producing per-item EV sub-criterion scores with written findings; hosts automated raters and, in M4, reviewer-model scoring under the calibration rules of §7. |
| **Scoring Engine** | Implements [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md): dimension scores, confidence intervals, weighted aggregation, minimum gates, CL derivation, RT×AL envelopes. |
| **Report Generator** | Renders evidence packages, comparisons, and Qualification Records to the output formats of §9. |
| **Qualification Record** | The persistent output artifact: scoped grants, evidence references, provenance, status — schema in §5.5/§9. |

## 5. Data Model

All persisted artifacts are plain files (YAML for definitions, JSON for results) so that evidence is diffable, reviewable, and independent of the tool. Schemas below are normative in shape; field lists MAY grow additively.

### 5.1 Registry Entry — a Deployment Manifest (YAML)

A registry entry is a **deployment**: the named tuple of a model
artifact, a runtime, its configuration, and its endpoint (D11).
Qualification targets a deployment, not a bare model, because behavior
is a property of model × quantization × runtime × config — exactly what
the environment fingerprint records (D7). The same model served two
ways is two deployments. `aies discover` writes these automatically;
they may also be hand-authored.

```yaml
id: local-qwen                    # deployment name — stable, never reused
kind: deployment
runtime: <runtime adapter id>     # resolved to an installed plugin
model: <model name>               # data, not normative text — vendor names permitted
family: <model family name>       # optional
parameters: 7.2e9
active_parameters: null           # set for mixture-of-experts models
quantization: q4_k_m
runtime_config:                   # how the runtime reaches this model
  base_url: <endpoint>            # for endpoint-served runtimes
  model_path: <path>              # for local-file runtimes
license: <license identifier>
context_window: 32768
modalities: [text]                # text, vision, audio…
parameters_default:               # generation defaults for this deployment
  temperature: 0.6
  max_tokens: 32768
capabilities:                     # claims to be verified by discovery, never trusted
  tool_use: true
  function_calling: true
  reasoning_mode: true
provenance:
  source: <where the artifact came from>
  checksum: sha256:…              # binds the deployment to an exact artifact
```

When the same model name resolves to more than one deployment, the
target is ambiguous and the platform requires the deployment id or a
`--runtime` filter — it never guesses (D11).

### 5.2 Profile (YAML)

A profile is a **weighting preset** expressing an organizational emphasis. Shipped presets: `enterprise`, `coder`, `architect`, `security`, `startup`, `research`.

```yaml
name: enterprise
description: Traceability- and safety-weighted evaluation for regulated delivery
area_weights:                     # relative emphasis across competency areas
  CA-05: 1.0
  CA-06: 1.2
  CA-12: 1.5
dimension_weight_adjustments:     # bounded by AIES-AESQS-CS-01-R03 (±0.05, EV3+EV6 floor)
  EV6: +0.05
# NOTE: gates and statistical minimums are NOT expressible here.
# They are engine constants per risk tier (AIES-AESQS-CS-01 §3.1, §6)
# and no profile can relax them. See §6 and §11 (D3, D6).
```

The Profile Loader MUST reject any profile whose adjustments violate [AIES-AESQS-CS-01-R03 — Risk-tier weight adjustments remain bounded](../AESQS/capability-scoring.md).

### 5.3 Competency Directory Layout

Scenario content is organized per competency area — the areas are exactly the AESQS competency areas CA-01…CA-12 (see §11 D5), not a parallel taxonomy:

```
platform/competencies/
  CA-05-ai-assisted-implementation/
    definition.yaml        # scope, in-scope phases, discovery probes
    rubric.yaml            # EV sub-criteria mapping for this area
    scoring.yaml           # area-specific evidence expectations
    scenarios/
      SC-CA05-001.yaml … SC-CA05-0NN.yaml
```

Scenario families (e.g., mobile, UI, leadership-adjacent planning) live *inside* areas as tags, never as new top-level domains.

### 5.4 Test Case (YAML)

Test cases specify **expected qualities and a rubric — never expected answers**. Scoring judges observable properties of the response, which keeps suites contamination-resistant and meaningful across model generations.

```yaml
id: SC-CA05-014
area: CA-05
family: refactoring
risk_tier: RT2                    # RT2 — Moderate
prompt: |
  <the task presented to the candidate>
expected_qualities:               # observable properties, not a reference answer
  - preserves existing public behavior
  - states its assumptions explicitly
  - includes verification for the changed paths
rubric:                           # maps qualities to EV sub-criteria (see §6)
  EV1: [behavior preserved, requirements met]
  EV2: [edge cases addressed, dependents considered]
  EV3: [no new trust-boundary exposure]
  EV6: [assumptions and rationale stated]
weight: 1.0
failure_conditions:               # any one observed → dimension score 0 for that EV
  - fabricates an API that does not exist        # → EV1
  - executes a destructive step without flagging  # → EV3
repeats_min: 3
```

### 5.5 Result Record (JSON)

Every executed scenario run produces an immutable JSON evidence record:

```json
{
  "run_id": "run-2031-SC-CA05-014-r2",
  "suite_version": "…", "scenario_id": "SC-CA05-014",
  "model": { "registry_id": "acme-7b-q4", "checksum": "sha256:…" },
  "environment_fingerprint": {
    "machine": "…", "cpu": "…", "gpu": "…", "ram_gb": 64,
    "runtime": { "id": "…", "version": "…" }, "os": "…",
    "power_state": "…", "thermal_state": "…", "fingerprint_hash": "sha256:…"
  },
  "request": { "prompt_hash": "sha256:…", "parameters": { } },
  "raw_response": "…",
  "scores": { "EV1": 3, "EV2": 2, "EV3": 3, "EV4": 3, "EV5": 2, "EV6": 4 },
  "findings": [ { "dimension": "EV2", "score": 2, "finding": "…" } ],
  "provenance": { "rater": "…", "rater_kind": "automated|model|human",
                  "timestamp": "…", "platform_version": "…" },
  "decisional": false
}
```

Records are append-only; corrections are new records referencing the corrected one ([AIES-AESQS-RR-01-R16 — Revision and Revocation, requirement 16](../AESQS/revision-and-revocation.md)).

## 6. Scoring Semantics

The Scoring Engine implements [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md) without local invention:

1. **Dimensions and anchors.** Every evidence item is scored on EV1–EV6 ([Taxonomy §8](../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6)) using the 0–4 anchor tables of [AIES-AESQS-ER-01 — Evaluation Rubrics §1–§2](../AESQS/evaluation-rubrics.md). Individual raters (human, automated, or model) never emit half-points ([AIES-AESQS-ER-01-R04 — Evaluation Rubrics, requirement 04](../AESQS/evaluation-rubrics.md)).
2. **Dimension scores.** D(EVk) is computed over the full pre-registered sample and reported as mean plus a two-sided 90% confidence interval; the **lower bound** is the decision value ([AIES-AESQS-CS-01-R01 — Pre-registered sample governs dimension scoring](../AESQS/capability-scoring.md)).
3. **Weights.** Risk-tier weights come from [AIES-AESQS-CS-01 — Capability Scoring §2](../AESQS/capability-scoring.md); profile adjustments are bounded by R03 and validated at load time.
4. **Minimum gates.** The gate table of [AIES-AESQS-CS-01 — Capability Scoring §3.1](../AESQS/capability-scoring.md) is hard-coded per risk tier. A failed EV3 gate denies the tier outright (R04); a single EV3 rubric score of 0 at RT3 — Significant through RT4 — Critical fails the gate; variance that drops a lower confidence bound of EV1/EV3 below its gate fails the gate even when the mean passes (R13). **No profile, flag, or configuration can relax a gate.**
5. **Statistical minimums.** The engine enforces AI-system minimum sample sizes per risk tier (20/30/50/100 for RT1 — Minimal through RT4 — Critical, [AIES-AESQS-CS-01 — Capability Scoring §6](../AESQS/capability-scoring.md)) including repeated runs for variance. Results from smaller samples are emitted with `"decisional": false` and rendered with a NON-DECISIONAL banner; the platform MUST NOT present them as qualification evidence.
6. **CL derivation.** Aggregates map to CL1–CL3 per the thresholds of [AIES-AESQS-CS-01 — Capability Scoring §4](../AESQS/capability-scoring.md); CL4 is never awarded to an AI system (R07). Score thresholds bound the level from above; descriptor co-requisites are flagged for human confirmation (R06).
7. **RT×AL envelope.** For each competency area and task type, the recommended autonomy is min(risk-tier default cap, CL-earned cap) per [AIES-AESQS-CS-01 — Capability Scoring §5](../AESQS/capability-scoring.md); AL4 — Autonomous is never recommended at initial qualification (R08).

## 7. Peer-Review Orchestration

M4 adds multi-model review as an evidence-strengthening step, structured as:

```
candidate answers ─► reviewer model critiques ─► candidate revises
        ─► moderator model adjudicates ─► human reviews and approves
```

Rules:

- **Reviewer models must themselves be qualified.** A model MUST hold a current platform qualification covering review-class tasks (CA-06 scope) before its critiques carry scoring weight. Bootstrap: an unqualified reviewer's scores are calibrated against human-scored anchor items, and inter-rater agreement per [AIES-AESQS-ER-01 — Evaluation Rubrics §4](../AESQS/evaluation-rubrics.md) MUST meet the declared threshold before its ratings count.
- **Model reviews assist; humans decide.** All model-produced critique operates at AL2 — Collaborative or below in the review process, consistent with [AIES-AESQS-PR-01-R09 — Peer Review, requirement 09](../AESQS/peer-review.md); a model is never recorded as the reviewer, and model scores are never the sole basis for a decision ([AIES-AESQS-ER-01-R10 — Evaluation Rubrics, requirement 10](../AESQS/evaluation-rubrics.md)).
- **The human is the qualification authority.** The pipeline assembles the review package (evidence, scores, divergences, adjudication rationale); a human (ROLE-13, with ROLE-14 owning the registry) makes the Grant / Grant-with-conditions / Deny decision per [AIES-AESQS-QP-01-R12 — Qualification Process, requirement 12](../AESQS/qualification-process.md). The two-human minimum of [AIES-AESQS-QP-01-R01 — Qualification Process, requirement 01](../AESQS/qualification-process.md) applies to organizational qualification decisions; the platform records the humans involved.
- Divergences of ≥2 points or gate-changing divergences are surfaced for resolution against the anchors, never averaged ([AIES-AESQS-ER-01-R07 — Evaluation Rubrics, requirement 07](../AESQS/evaluation-rubrics.md), [AIES-AESQS-PR-01-R11 — Peer Review, requirement 11](../AESQS/peer-review.md)).

## 8. Plugin Contract

Runtime plugins are the sole boundary between the engine and any model runtime or hosted provider. The core engine contains no vendor- or runtime-specific code.

A runtime adapter implements four operations:

| Operation | Contract |
|-----------|----------|
| `load(registry_entry)` | Acquire/attach the model identified by the registry entry; verify the checksum; fail loudly on mismatch. |
| `generate(request) → response` | Execute one inference request; return the raw response plus runtime-reported usage (tokens, latency). No retries that the Test Runner did not order. |
| `capabilities() → declaration` | Declare what the adapter supports: modalities, tool/function calling, structured output, streaming, maximum context. |
| `fingerprint() → environment` | Report the runtime component of the environment fingerprint (§5.5): runtime id, version, device placement, relevant settings. |
| `probe_runtime() → status` *(optional)* | Class-level. Detect whether the runtime is present on the host: `{available, version, detail}`. Best-effort and non-fatal — an absent runtime reports `available: false`, never raises. Powers `aies doctor`. |
| `discover_deployments() → list` *(optional)* | Class-level. Enumerate candidate deployments the runtime can serve (partial manifests). Powers `aies discover`. |

Rules:

- Plugins are discovered at runtime (entry points); adding a runtime or provider MUST NOT require core-engine changes.
- Plugin identity and version are part of every result record's provenance.
- Normative platform documentation refers to these only as **runtime adapters**. *(Informative example: adapters for local runtimes such as Ollama, MLX, or vLLM, and for hosted provider APIs, are expected as separately versioned plugins.)*

## 9. Report Outputs

| Output | Milestone | Content |
|--------|-----------|---------|
| Markdown report | M1 | Human-readable evidence summary: scope, environment fingerprint, per-area EV1–EV6 scores with intervals, gate outcomes, CL and RT×AL recommendations, findings |
| JSON evidence package | M1 | Machine-readable equivalent: all result records plus the aggregation, suitable for registry ingestion and audit (ART-15) |
| History & comparison views | M2 | Cross-run and cross-model deltas on identical suite versions |
| HTML / PDF reports | M3 | Presentation-grade rendering of the same data — never additional claims |
| Qualification Record | M1 (format) / M4 (workflow) | The scoped grant artifact: subject (registry id + checksum), scope tuple (role/area × phases × RT), awarded CLs, AL envelope per task type, environment fingerprint, evidence references, humans involved, status, conditions |

Every report MUST state suite versions, sample sizes, and whether each result is decisional (§6.5). A Qualification Record with status other than a human-recorded grant renders as **evidence package — no grant**.

## 10. Milestones

| Milestone | Scope | Exit criteria |
|-----------|-------|---------------|
| **M1 — Runnable core** | Python package + CLI skeleton; `doctor`; `registry`; single-model `qualify` (stages 2–5, human scoring hooks); Markdown/JSON reports | A third party can register a local model, run `aies qualify` end to end offline, and get a reproducible Markdown + JSON evidence package with fingerprint, gates, and non-decisional labeling correct |
| **M2 — Scoring depth** | Competency directory framework (CA-01…CA-12); weighted scoring with the six shipped profiles; result history; `compare` | Profile weights demonstrably cannot bypass gates or statistical minimums (conformance tests); two models compared on identical suite versions with defensible deltas |
| **M3 — Scale & integration** | Plugin architecture stabilized (public adapter contract); HTML/PDF reports; parallel suite execution; result database over the append-only records | A runtime adapter can be written out-of-tree against the published contract without core changes; a full RT2 — Moderate-sized run (≥30 items/area) completes with parallelism and identical scores to serial execution |
| **M4 — Review & workflow** | Multi-model peer review (§7); qualification decision workflows (human grant recording, status model, re-qualification triggers); dashboard; CI integration | A complete qualification cycle — evidence through human-recorded grant to Qualification Record — runs for at least one role scope; reviewer-model calibration gate enforced; environment-change trigger demonstrably invalidates a grant |

Milestones gate on exit criteria, not dates, consistent with the [AIES-GOV-04 — Roadmap](../ROADMAP.md).

## 11. Design Decisions (Anti-Drift Contract)

These ten decisions bind the implementation to the standard. Deviating from any of them requires a superseding ADR.

| # | Decision | Rationale |
|---|----------|-----------|
| **D1** | **Qualification, not certification.** The verb is `qualify`; the artifact is a Qualification Record/Profile; the final stage is the *Qualification Decision*. There is no `certify` command. | AECT certifies humans; AESQS qualifies AI systems ([AIES-AECT-00 — Engineering Certification relationship, AIES-AESQS-00 — Qualification Standard §5](../AESQS/README.md)). Blurring the two would misstate what the artifact asserts. |
| **D2** | **Score on EV1–EV6 with 0–4 anchors** ([Taxonomy §8](../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6); [AIES-AESQS-ER-01 — Evaluation Rubrics](../AESQS/evaluation-rubrics.md)) — never an ad-hoc dimension set or 0–5 scale. Qualities like hallucination-resistance, communication, or referencing are **sub-criteria** mapped under the six dimensions (hallucination → EV1; communication/references → EV6). | The Taxonomy forbids competing scales (AIES-SHARED-02 preamble); comparability across tools and organizations depends on one scale. |
| **D3** | **Minimum gates are non-negotiable.** Profiles adjust weights within [AIES-AESQS-CS-01-R03 — Risk-tier weight adjustments remain bounded](../AESQS/capability-scoring.md) bounds; the gate table (§3.1, especially EV3) is engine-constant and cannot be expressed, overridden, or relaxed in any profile or flag. | Safety can never be averaged away ([AIES-AESQS-CS-01-R04 — Safety cannot be averaged away](../AESQS/capability-scoring.md)); a configurable gate is no gate. |
| **D4** | **Scoped grants, never "Production Ready: YES".** Output is per-competency-area CL, and per task type an autonomy envelope min(RT cap, CL cap) ([AIES-AESQS-CS-01 — Capability Scoring §5](../AESQS/capability-scoring.md)), expressed as deployment-role recommendations (ROLE-01…14). No global pass/fail exists anywhere in the output. | AESQS qualifications are scoped by definition ([AIES-AESQS-00-R01 — Qualification Standard, requirement 01](../AESQS/README.md)); a global verdict would be a claim the evidence cannot support. |
| **D5** | **Domains are the existing competency areas.** Scenario suites are organized by CA-01…CA-12 (derived from AEBOK KAs); mobile/UI/leadership and similar become scenario families *within* areas. No parallel domain taxonomy. | One taxonomy ([AIES-SHARED-02 — Taxonomy](../Shared/Taxonomy/README.md)); parallel domain schemes would fork the competency framework and break traceability to AEBOK. |
| **D6** | **Statistical minimums are enforced.** Minimum sample sizes per risk tier ([AIES-AESQS-CS-01 — Capability Scoring §6](../AESQS/capability-scoring.md)) are engine-enforced; under-sampled results carry `"decisional": false` and are visibly labeled non-decisional. Single-run results never look like qualification evidence. | Capability is a distribution, not an anecdote; the lower confidence bound is the decision value (R02/R11). |
| **D7** | **The environment fingerprint is provenance, and environment change is a re-qualification trigger.** Model file/checksum, quantization, or runtime-version change invalidates existing evidence and grants, extending the model/context-change triggers of [AIES-AESQS-RR-01 — Revision and Revocation §2](../AESQS/revision-and-revocation.md) to the execution environment. | Model behavior is model × environment; evidence gathered on one fingerprint does not transfer silently to another. |
| **D8** | **Humans hold qualification authority.** Reviewer models must be qualified (or human-calibrated during bootstrap) before their reviews carry weight; model review operates at AL2 — Collaborative or below; a human (ROLE-13) records every grant. The platform prepares evidence — it never grants. | [AIES-AESQS-QP-01-R01 — Qualification Process, requirement 01](../AESQS/qualification-process.md), [AIES-AESQS-PR-01-R09 — Peer Review, requirement 09](../AESQS/peer-review.md), [AIES-AESQS-ER-01-R10 — Evaluation Rubrics, requirement 10](../AESQS/evaluation-rubrics.md). |
| **D9** | **Vendor neutrality boundary.** Model, vendor, and runtime names are **data** — permitted in registry entries, results, and plugin code. Normative platform and standard text stays vendor-neutral ("runtime adapter"); concrete names appear only in informative notes. Vendor-specific code lives only in plugins (§8). | Preserves the project's vendor-neutral charter while keeping the tool usable in a world of named products. |
| **D10** | **Placement: in-repo under `platform/`** as the Phase 7/8 reference implementation (Python package `aies`), with conformance tests keyed to requirement IDs; a possible split into a companion repository at v1.0 requires a superseding ADR. | Standard and engine must evolve under one review gate to prevent drift ([ADR-0002](../adr/ADR-0002-Qualification-Platform.md)). |
| **D11** | **Qualify deployments, not bare models.** A deployment is the named (model artifact × runtime × config × endpoint) tuple; the registry stores deployments, `aies discover` populates it by probing runtimes, and `aies qualify` targets a deployment (or a model name disambiguated by `--runtime` — ambiguity is surfaced, never guessed). All runtime access stays behind the adapter boundary (§8, D9). | Behavior is a property of the whole deployment, not the model alone — this is D7 made a first-class object. Users should never hand-wire runtimes or file paths at qualification time, and the same model served two ways must be two distinct, separately-qualified subjects. |

---

## Related Documents

- [ADR-0009 — Engineering Assessment Platform Identity](../adr/ADR-0009-Engineering-Assessment-Platform-Identity.md)
- [AIES-AESQS-00 — AESQS — AI Engineering SDLC Qualification Standard](../AESQS/README.md)
- [AIES-AESQS-QP-01 — Qualification Process](../AESQS/qualification-process.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](../AESQS/evaluation-rubrics.md)
- [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md)
- [AIES-AESQS-PR-01 — Peer Review Standard](../AESQS/peer-review.md)
- [AIES-AESQS-RR-01 — Revision & Revocation](../AESQS/revision-and-revocation.md)
- [AIES-AESQS-CF-01 — Competency Framework](../AESQS/competency-framework.md)
- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) · [Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md)
- [AIES-GOV-04 — Roadmap](../ROADMAP.md) — Phases 7–8

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

# AIES Vision Execution Backlog

| | |
|---|---|
| **Document ID** | AIES-DOC-14 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This is the single authoritative implementation backlog for taking AIES from a
strong draft foundation to a validated, reusable standard and Engineering
Assessment Platform. [ROADMAP.md](../ROADMAP.md) contains public milestones;
it MUST link here rather than repeat implementation status.

The backlog has two lanes:

1. **Vision delivery** — standards, evidence integrity, assessment capability,
   decision products, and adoption.
2. **Cleanup and debt** — consistency, maintainability, release engineering,
   and repository hygiene.

Status values are **Open**, **In progress**, **Blocked**, **Deferred**, and
**Done**. Done requires the acceptance signal to be verified.

## 1. Target Architecture

```text
AEBOK / AESQS / AEOS / AEAR / AECT / ECM
                    │
                    ▼
             Assessment Plan
                    │
                    ▼
             Canonical Evidence
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
   Qualification   ECM   Conformance
          │         │
          ▼         ▼
   Human authority  Deployment Guidance
                    │
                    ▼
           Compare / AIES Select
```

The platform is not a model leaderboard. It prepares trustworthy, scoped
evidence about any supported subject and presents that evidence for different
human decisions. Qualification, engineering capability, deployment guidance,
and selection remain separate products.

## 2. Vision Delivery Backlog

### P0 — Correctness and qualification integrity

| Status | Work item | Acceptance signal |
|---|---|---|
| Done | Correct Grant Readiness rendering | A fully decisional, gate-passing package renders `Overall: READY`; missing admitted evidence renders gates as not evaluated rather than failed; Markdown and HTML tests cover both paths |
| Done | Report corpus maturity honestly | Corpus health distinguishes calibration metadata, attributable human design review, external independent review, and empirical calibration; hash-bound acceptance cannot be mistaken for model-panel validation |
| Done | Make repository-audit detection deterministic | CI checks are found regardless of filesystem/YAML ordering; the AIES repository no longer reports its existing pytest CI gate as absent |
| Done | Align rating admission with AIES-AESQS-ER-01 — Evaluation Rubrics | Accepted ADR-0012 defines the required evidence-item/rater separation; human raters have verified identity, scope, qualification, and current calibration, and automated raters cannot be the sole decisional scoring basis |
| Done | Model evidence items separately from rater observations | Evidence Package v5 retains every rating observation but sends at most one resolved score per response evidence item into statistics; adjacent human ratings resolve conservatively, major divergences require an immutable named-human disposition, and tests prove a second rating cannot inflate sample size or confidence |
| Done | Enforce double-rating and agreement rules | RT1 — Minimal / RT2 — Moderate double-rate at least 20%; RT3 — Significant / RT4 — Critical double-rate every item; required agreement and divergence resolution are machine-checked |
| Done | Enforce the two-human qualification process | Every grant, conditional grant, and denial records an assessor and independent peer reviewer with qualification and conflict declarations |
| Done | Complete the qualification scope tuple | Records include subject, role, phases, maximum risk tier, competency × CL claims, framework version, applicable agent-definition version, sponsor, and validity window |
| Done | Make qualification lifecycle events immutable | Accepted ADR-0012 governs implementation; grant, condition change, renewal, suspension, invalidation, revocation, and supersession append separate ART-15 — Audit Trail Record events and prior records are never overwritten |
| Done | Show detailed live progress for every run | `qualify`, resume, `review`, and `score` display progress implicitly with completed/total, percentage, current-stage elapsed time, total run elapsed time, throughput, ETA, the current human-readable scenario family/task objective and ordinal, failures, and resumability; parallel runs expose the dynamic active task set and effective worker capacity for any `--parallel N`; the same state persists in `progress.json`, while `aies runs progress <run-id>` is an optional second-terminal observer |
| Done | Make automated Engineering Evaluation self-contained | Complete automated scoring closes the engineering-evaluation workflow and generates all report/ECM artifacts; human evaluation is an optional, visible reviewed/not-reviewed field and never blocks the evaluation; formal qualification remains a separate ADR-0012 protocol |
| Done | Enforce expiry and requalification | Expired or materially changed qualifications are treated as absent; renewal and targeted re-evaluation are supported |
| Done | Correct endpoint deployment fingerprints | Remote qualifications bind to behaviorally relevant deployment/runtime/config identity, not irrelevant client-machine RAM/CPU changes |
| Done | Govern ECM task decision semantics in an ADR | Accepted ADR-0013 and ECM schema 2 compute one resolved item per distinct task scenario, task-specific RT breadth, 90% uncertainty, risk-tier gates/EV3 hard-fail, reviewed mapping admission, human-rater protocol, parent-area floors, valid `demonstrated` semantics, compatible comparison, and Qualification-Record-bounded Deployment Guidance |

### P1 — Measurement validity

| Status | Work item | Acceptance signal |
|---|---|---|
| Done | Human-review the new RT2 — Moderate tranche | Umair Ali explicitly accepted all 268 listed instruments as repository owner and maintainer after a zero-gap deterministic preflight. One disclosed human-authorized AI-assisted tranche event records every scenario ID and content hash, does not fabricate separate manual click-through reviews, and automatically reopens changed content. All 484 now have effective design review; external independent review and empirical calibration remain open separately. |
| In progress | Empirically calibrate a preregistered real-subject panel | Panel preflight now rejects mismatched suites/prompts/samples/rating protocols, missing ratings, duplicate corrections, and ungrounded ability ranks. Four existing legacy subjects share seven CA-05 scenarios and 21 observations under one provisional protocol, but remain non-promotional because ability ordering was not independently preregistered and the rating protocol is explicitly provisional/uncalibrated. A versioned real-subject study must report difficulty, discrimination, repeatability, twin robustness, ceiling reach, limitations, and a human promotion decision. |
| Open | Establish versioned anchor-artifact libraries | Every competency area has human-consensus anchors across scores 0–4, including subtle AI-produced defects and refresh history |
| Open | Protect held-out evidence | Public examples, behavioral twins, and genuinely protected held-out instruments are distinct; contamination checks and refresh policy are recorded |
| Open | Grow no-repeat coverage beyond RT2 — Moderate | Each supported tier/area meets its distinct-instrument minimum with genuinely tier-appropriate decision types: current distribution RT1=24, RT2=387, RT3=52, RT4=21 |
| Open | Validate Engineering Task mappings empirically | ET-01 through ET-15 mappings receive human review and demonstrate task discrimination; mapping counts alone cannot establish capability |
| Open | Add task-specific uncertainty | ECM reports task-level effective sample, admitted evidence, interval, protocol, mapping version, and limitations without borrowing an area minimum as a task threshold |
| Done | Add hallucination and fabrication diagnostics | Report bundles include source-separated structured observations for unsupported assertions, fabricated APIs/entities, invalid citations/provenance, false success/test claims, and appropriate abstention; the descriptive grounding-reliability view maps to EV1 — Correctness, EV3 — Safety & Security, and EV6 — Traceability and cannot alter qualification decisions |

### P1 — Subject-neutral assessment architecture

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Define a governed Subject Descriptor | Canonical identity supports human, team, repository, AI deployment, agent, MCP server, RAG system, pipeline, and platform without a mandatory legacy model block |
| Open | Separate Subject Executor from Runtime Adapter | Runtime generation remains one executor implementation; evidence collection is not coupled to text-generation APIs |
| Open | Define typed canonical evidence events | Provenance, subject, instrument, observation, rating, reviewer, environment, and lifecycle events are versioned and replayable across subject types |
| Open | Implement agent-session assessment | Tool calls, memory, context, approvals, failures, and escalation traces enter canonical evidence |
| Open | Implement MCP-server assessment | Protocol behavior, tool contracts, authorization, isolation, failure behavior, and security evidence enter the same decision-product pipeline |
| Open | Implement RAG-system assessment | Retrieval quality, grounding, source integrity, privacy, injection resistance, and abstention are directly assessed |
| Open | Unify repository audit decision products | Repository maturity remains semantically distinct from AESQS rubric scoring but shares subject identity, evidence provenance, reporting, and portfolio views |

### P2 — ECM and decision products

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Ratify AIES-ECM-01 — Engineering Capability Matrix | ECM is formally present in the Charter, Vision, architecture, Roadmap, governance, requirement IDs, and public review disposition |
| Done | Deliver a compact report bundle | Qualification Evidence Package, Canonical Assessment Result when applicable, ECM, Deployment Guidance, and Executive Summary are separate linked Markdown/JSON/HTML artifacts generated from one canonical evidence package and indexed by `report-bundle.json` |
| Done | Mature Deployment Guidance | Use / Use with Review / Avoid incorporates task evidence, current matching qualification scope, live deployment-fingerprint continuity, role/phases, autonomy, conditions, validity, residual calibration/gate risks, and operational constraints; no guidance creates authority |
| Done | Add protocol-compatible ECM comparison | Task deltas and winners appear only when risk, profile, suites, mappings, repeats, and rater protocol are compatible |
| Open | Build AIES Select | A declared workload mix plus latency, cost, context, tool reliability, availability, and risk constraints produces an explained fit ranking over compatible evidence—never a global best-subject claim |
| Open | Build organization decision products | Inventory shows approved subjects, demonstrated task fit, qualification scope, conditions, drift, expiry, incidents, and requalification status |
| Done | Rebuild `demo-full` as the AIES killer demo | The fully offline one-process CI narrative demonstrates deployment/repository/standard subjects, implicit live task/ETA progress, complete automated Engineering Evaluation, optional human-evaluation status, ECM strengths/gaps, bounded guidance, protocol-compatible comparison without invented winners, the formal qualification boundary, conformance, corpus health, empirical-panel handoff, and the linked Executive Summary bundle; expected non-zero outcomes are explicitly contained, and the measured Windows run completes in about 16 seconds without repeated inference, report computation, or production-timeout probes |

### P3 — Standards and adoption

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Reconcile ECM with the five-module architecture | A governed update establishes ECM as a foundational standard and updates dependent documents without weakening vendor neutrality |
| Open | Complete independent pilots | At least one local and one hosted assessment have independent human rating/review, reproducible artifacts, limitations, and published lessons learned |
| Open | Complete public comment | Every normative module and ECM has a comment period, disposition log, and Approved decision under governance |
| In progress | Ratify open repository licenses | Proposed ADR-0014 defines CC BY-SA 4.0 for standards/assessment content and Apache 2.0 for executable software. Complete affiliation disclosures, announce and finish the seven-day Class 3 comment window, resolve objections, record Maintainer acceptance, then install exact license texts, path notices, SPDX/package metadata, and CI verification |
| Open | Publish a real release | Version story is consistent, a signed tag exists, release artifacts pass hygiene/conformance, and upgrade notes are published |
| Open | Demonstrate external adoption | Published case studies, third-party conformance runs, and contributors/reviewers from independent organizations satisfy Charter success criteria |

## 3. Cleanup and Debt Backlog

### C0 — Correctness-adjacent cleanup

| Status | Cleanup item | Acceptance signal |
|---|---|---|
| Done | Resolve duplicate document IDs | This backlog is AIES-DOC-14 and the dated Project Evaluation is AIES-DOC-15; every governed document ID is unique and the affected citation is updated |
| Open | Replace generic requirement labels | References show code plus meaningful obligation title, not `requirement NN`; a machine-readable registry and CI check cover all governed IDs |
| Open | Remove stale model-only identity language | Current docs use subject/deployment terminology; historical superseded ADR text remains immutable and clearly historical |
| Open | Reconcile backlog and Roadmap | ROADMAP contains milestones only and links here; no completed implementation remains listed as Open and no Draft artifact is described as ratified |
| Open | Clarify frozen versus experimental contracts | Draft/Review contracts are not presented as ratified v1; experimental stability and Approved standard stability are labeled separately |

### C1 — Platform maintainability

| Status | Cleanup item | Acceptance signal |
|---|---|---|
| Open | Split the CLI monolith | Parser construction and command handlers are separated by domain with unchanged tested command behavior |
| Open | Consolidate duplicate commands | `registry`/`deployment`, `profile`/`profiles`, and `qualification`/`qualifications` have one canonical surface plus documented deprecation aliases |
| Open | Consolidate report view models | Markdown, HTML, JSON, dashboard, and API consume shared factual view models; no renderer recomputes decisions |
| Done | Clarify immutable artifacts and regenerable views | Storage policy classifies append-only records, derived canonical snapshots, mutable workflow state/configuration, and regenerable views; `workspace.write_json` rejects append-only replacement and `workspace.write_view` cannot target evidence paths |
| Done | Make record identifiers concurrency-safe | Qualification Records atomically claim human-readable IDs through exclusive creation; a 12-decision concurrent regression proves unique issued records and lifecycle events |
| Done | Improve local verification feedback | The documented command reports ranked durations and uses a 180-second warm-cache Windows budget with a 25% regression trigger. Single-pass report views plus signature-invalidated isolated YAML, expanded-scenario, review-ledger, and suite caches reduce the measured complete run from 216 tests in 491.51 seconds to 224 tests in 81.89 seconds; cache mutation/invalidation behavior has regression coverage. Read-only API fixtures are shared safely and concurrency tests delay only the phase under test. |
| Open | Remove local workspace archive debris safely | Workspace diagnostics identify `.DS_Store`, `__MACOSX`, caches, and stale generated bundles without deleting user evidence automatically |

### C2 — CI, security, and release hygiene

| Status | Cleanup item | Acceptance signal |
|---|---|---|
| Done | Expand CI path coverage | Changes to Shared, AEBOK, AESQS, AEOS, AEAR, AECT, ECM, ADRs, governed docs, platform, and conformance trigger relevant checks |
| Done | Test supported Python versions | CI runs the complete platform gate on Python 3.10, 3.11, 3.12, 3.13, and 3.14; installation docs identify that tested range |
| Open | Add documentation governance checks | CI detects duplicate document/requirement IDs, missing meaningful titles, broken links, invalid metadata/status transitions, and stale references |
| Open | Add code-quality checks | Formatting, linting, type checking, and coverage thresholds run in CI |
| Open | Add supply-chain controls | Dependency lock, dependency review, secret scanning/SAST, SBOM/AI-BOM, artifact provenance, and signing are implemented proportionately |
| Open | Publish a real security contact | Dedicated email and optional encryption key replace the placeholder fallback; private vulnerability reporting remains preferred |
| Open | Add ownership and protected-branch evidence | CODEOWNERS and externally attested branch-protection/human-review gates satisfy the repository’s own audit |
| Open | Align versions | Package version, standards milestone, artifact versions, changelog, tags, and release names answer different versioning questions explicitly and consistently |
| Done | Correct current CI identity wording | Workflow and active docs say Engineering Assessment Platform rather than Qualification Platform |

## 4. Current Verified Baseline

Last verified on 2026-07-23:

- `pytest platform/tests -q --durations=15`: **224 passed in 81.89 seconds** on
  the current Windows workstation (down from the preceding 219-test measurement
  of 155.38 seconds and below the documented 180-second warm-cache budget).
- `aies suites validate`: **484 scenarios, 12 areas, 0 warnings, 0 errors**;
  **268 effective hash-bound ledger acceptances, 0 stale, 0 unknown**.
- Decision-engine conformance: **8/8 cases passed**, semantics 1.0.
- Release hygiene: **PASS**.
- Repository audit at RT2 — Moderate: **PASS**, with 18 verified controls and
  8 gaps; the prior order-dependent CI-test false negative is covered by a
  regression test.
- Scenario review maturity: **484/484 human design-reviewed**, **0/484
  empirically calibrated**. The accepted 268-instrument tranche is one
  transparent human-authorized AI-assisted decision bound to every scenario ID
  and content hash; it claims no separate manual click-through reviews and no
  external independent validation. Any content change reopens that instrument.
- `python platform/scripts/demo_full.py`: the complete 16-stage offline demo
  passed in **11.8 seconds** on the current Windows workstation.

## Related Documents

- [Roadmap](../ROADMAP.md)
- [Vision](VISION.md)
- [Project Charter](PROJECT_CHARTER.md)
- [Engineering Assessment Platform Specification](PLATFORM.md)
- [AIES-ECM-01 — Engineering Capability Matrix](../ECM/README.md)

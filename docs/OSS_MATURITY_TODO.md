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
        Assessment Coverage Matrix
                    │
                    ▼
             Subject Descriptor
                    │
                    ▼
       Subject Executor / Evidence Adapter
                    │
                    ▼
             Canonical Evidence
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
 Qualification    ECM      Conformance
        │           │           │
        └───────────┼───────────┘
                    ▼
     Guidance / Remediation / Limitations
                    │
                    ▼
 Compare / AIES Select / Portfolio Views
                    │
                    ▼
             Human authority
```

The platform is not a model leaderboard. It prepares trustworthy, scoped
evidence about any supported subject and presents that evidence for different
human decisions. Qualification, engineering capability, deployment guidance,
remediation, comparison, and selection remain separate products. Subject types
share identity, provenance, evidence lifecycle, reporting, and human-authority
boundaries; they do not automatically share instruments or score semantics.

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
| In progress | Empirically calibrate a preregistered real-subject panel | The platform now creates a content-addressed plan before runs, freezing owner, subjects/ranks and independent basis, exact instrument/prompt/content/suite hashes, tier, repeats, thresholds, and validated rating protocol. Completed runs must bind exactly to that plan; free-text timestamps and synthetic/manual panels are non-promotional. Four legacy subjects share seven CA-05 scenarios and 21 observations under one provisional protocol, but remain exploratory because no prior plan exists and the scorer is explicitly provisional/uncalibrated. A real study and human promotion decision remain external evidence. |
| Open | Establish versioned anchor-artifact libraries | Every competency area has human-consensus anchors across scores 0–4, including subtle AI-produced defects and refresh history |
| Open | Protect held-out evidence | Public examples, behavioral twins, and genuinely protected held-out instruments are distinct; contamination checks and refresh policy are recorded |
| Open | Grow no-repeat coverage beyond RT2 — Moderate | Each supported tier/area meets its distinct-instrument minimum with genuinely tier-appropriate decision types: current distribution RT1=24, RT2=387, RT3=52, RT4=21 |
| Open | Validate Engineering Task mappings empirically | ET-01 through ET-15 mappings receive human review and demonstrate task discrimination; mapping counts alone cannot establish capability |
| Open | Add task-specific uncertainty | ECM reports task-level effective sample, admitted evidence, interval, protocol, mapping version, and limitations without borrowing an area minimum as a task threshold |
| Done | Add hallucination and fabrication diagnostics | Report bundles include source-separated structured observations for unsupported assertions, fabricated APIs/entities, invalid citations/provenance, false success/test claims, and appropriate abstention; the descriptive grounding-reliability view maps to EV1 — Correctness, EV3 — Safety & Security, and EV6 — Traceability and cannot alter qualification decisions |

### P1 — Subject-neutral assessment architecture

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Define a governed Subject Descriptor | Canonical identity supports human, team, repository, AI deployment/system, agent, agent swarm, MCP server, coding assistant, prompt library, RAG system, pipeline, platform, and composite system without a mandatory legacy model block |
| Open | Separate Subject Executor from Runtime Adapter | Runtime generation remains one executor implementation; evidence collection is not coupled to text-generation APIs |
| Open | Define typed canonical evidence events | Provenance, subject, instrument, observation, rating, reviewer, environment, and lifecycle events are versioned and replayable across subject types |
| Open | Define the Subject Assessment Profile contract | Every supported subject kind declares its descriptor schema, fingerprint/change triggers, executor or evidence adapters, applicable instruments, score semantics, minimums, gates, limitations, decision products, and human-review requirements |
| Open | Model composite subjects and dependencies | A human–AI pair, coding assistant plus repository, agent plus MCP servers, swarm, RAG application, pipeline, or platform can reference component subjects and evidence without transferring one component's qualification or hiding dependency risk |
| Open | Add subject capability discovery | CLI/API reports which subject kinds, profiles, executors, evidence adapters, instruments, and decision products are implemented, experimental, or planned; unsupported assessment requests fail clearly rather than silently falling back to deployment scoring |
| Open | Unify repository audit decision products | Repository maturity remains semantically distinct from AESQS rubric scoring but shares subject identity, evidence provenance, reporting, and portfolio views |

### P1 — Subject expansion program

Each subject kind receives a governed Subject Assessment Profile before an
executor is promoted from experimental status. EV1–EV6, ML0–ML4, or any future
scale applies only when the profile establishes that it is meaningful for that
subject and evidence type.

| Status | Subject track | Acceptance signal |
|---|---|---|
| Done | AI deployment output assessment | Versioned scenarios execute against local or remote deployments; responses, ratings, uncertainty, qualification boundaries, ECM, grounding diagnostics, and deployment guidance are produced from canonical evidence |
| Open | Human engineering work-sample assessment | Consent, identity, accommodations, work-sample provenance, assessor protocol, privacy/retention, appeal, competency evidence, and qualification lifecycle are implemented without covert productivity surveillance |
| Open | Team and human–AI pair assessment | Collaboration, handoffs, review effectiveness, shared context, decision ownership, escalation, recovery, and outcome evidence are evaluated without treating individual or model scores as a substitute for team evidence |
| Open | Agent-session assessment | Versioned tasks capture plans, tool calls, tool results, approvals, memory/context use, policy boundaries, side effects, failures, recovery, escalation, cost, latency, and final outcomes; replay and trace redaction are supported |
| Open | Agent-swarm assessment | Delegation, role separation, coordination, consensus/conflict handling, shared-state integrity, containment, cascading failure, aggregate cost, and accountable human control are assessed in addition to member-agent capability |
| Open | MCP-server assessment | Discovery and protocol conformance, schema accuracy, tool/resource contracts, authorization, least privilege, isolation, state handling, error behavior, injection resistance, reliability, latency, compatibility, and auditability enter canonical evidence |
| Open | AI coding-assistant assessment | IDE/repository context selection, code edits, diff quality, test behavior, secure defaults, command/tool use, provenance, approval boundaries, rollback, and repository-task outcomes are assessed as a composite assistant–repository subject |
| Open | Prompt-library assessment | Versioning, ownership, intended use, input/output contracts, regression suites, portability, injection resistance, sensitive-data handling, deprecation, drift, and task-specific effectiveness are assessed without publishing protected prompt content |
| Open | RAG-system assessment | Retrieval relevance/recall, grounding and citation validity, source integrity/freshness, authorization-aware retrieval, privacy, poisoning/injection resistance, abstention, latency, cost, drift, and failure behavior are directly assessed |
| Open | AI pipeline assessment | Data/model/prompt lineage, stage contracts, reproducibility, orchestration, quality gates, secrets, failure isolation, retry/idempotency, observability, rollback, cost, and promotion controls are assessed across the execution graph |
| Open | AI engineering platform assessment | Tenant and environment isolation, identity/access, policy enforcement, model/tool registry, audit trails, observability, resilience, supply chain, lifecycle governance, developer experience, and operating-model support are assessed against AEAR/AEOS evidence |
| Open | Composite-system end-to-end assessment | A declared system boundary links repositories, deployments, agents, MCP servers, RAG, pipelines, platforms, humans, and teams; component findings, interface failures, emergent risks, and end-to-end task outcomes remain traceable without averaging away a failed critical component |

### P1 — Cross-cutting multi-perspective assurance

“Comprehensive” means that applicability and evidence gaps are visible across a
governed set of perspectives; it does not mean that every perspective applies
to every subject or that missing evidence is silently treated as a pass. The
coverage model is extensible so a new technical, social, legal, environmental,
or industry perspective can be added without redesigning every executor.

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Govern an Assessment Coverage Matrix | Every Subject Assessment Profile declares applicable P01 — Business Strategy through P16 — Continuous Improvement lifecycle phases, X01 — Security through X15 — Sustainability cross-cutting domains, CA-01 — AI-Native SDLC Foundations through CA-12 — Governance, Risk & AI Safety competencies, ET-01 — Requirements Analysis through ET-15 — Production Operations tasks, RT1 — Minimal through RT4 — Critical risk tiers, AL0 — Manual through AL4 — Autonomous levels, stakeholders, environments, evidence modalities, operating conditions, and decision products; exclusions require a versioned rationale |
| Open | Make applicability and unknowns explicit | Every cell resolves to assessed, partially assessed, not assessed, not applicable with rationale, or unsupported; unknown, unavailable, tool-not-installed, redacted, and failed-to-collect evidence remain distinguishable and none can become a pass |
| Open | Cover nominal, boundary, adversarial, and recovery behavior | Applicable profiles test normal operation, edge and limit conditions, invalid input, misuse/abuse, hostile input, dependency failure, partial outage, rollback/recovery, long-running behavior, drift, and changed-environment behavior rather than relying only on happy paths |
| Open | Assess functional and engineering quality | Correctness, completeness, safety/security, maintainability, efficiency, traceability, requirements fit, architecture, integration, data quality, testability, usability, and profile-specific quality attributes are supported by direct evidence with declared confidence and limitations |
| Open | Assess security, safety, and abuse resistance | Threat models cover subject boundary, assets, identities, privileges, tools, data flows, dependencies, supply chain, prompt/context injection, poisoning, exfiltration, unsafe actions, denial of service, misuse, dual use, containment, kill/revoke paths, and incident response at the scoped risk tier |
| Open | Assess privacy, data, knowledge, and intellectual-property handling | Profiles address lawful/authorized collection, minimization, classification, consent where applicable, access, residency, retention, deletion, redaction, lineage, source integrity, confidentiality, protected prompts/evidence, licensing, copyright, and leakage through logs, embeddings, caches, tools, or outputs |
| Open | Assess human factors and affected parties | Profiles identify users, operators, reviewers, decision owners, data subjects, and affected non-users; they assess accessibility, workload, automation bias, over-reliance, review effectiveness, skill degradation, informed consent, fairness where consequential, contestability, appeal, accommodations, and protection from covert personnel surveillance |
| Open | Assess reliability and operational fitness | Evidence covers availability, latency classes, throughput, concurrency, saturation, timeouts, retry/idempotency, state consistency, observability, alerting, degraded modes, failover, backup/restore, rollback, incident learning, SLOs, capacity, change safety, drift detection, and requalification triggers |
| Open | Assess performance, cost, and resource impact | Reports separate quality from latency, throughput, token/compute, storage/network, energy/resource use, and total cost; declared workload and scale assumptions support trade-off analysis, budget ceilings, runaway-consumption controls, and repeatable cost-performance comparison |
| Open | Assess interoperability and portability | Protocol/schema conformance, version negotiation, backward compatibility, data/model/prompt portability, vendor substitution, import/export fidelity, configuration reproducibility, extension behavior, and graceful handling of unsupported capabilities are tested where applicable |
| Open | Assess lifecycle and supply-chain integrity | Evidence spans strategy and requirements through design, build, verification, release, operation, retirement, and improvement; provenance, dependencies, datasets, models, prompts, tools, artifacts, signatures, vulnerabilities, deprecation, ownership transfer, end-of-life, and secure disposal remain traceable |
| Open | Assess governance, legal, regulatory, and industry context | Profiles map applicable internal policy, qualification authority, segregation of duties, records, exceptions, regulatory obligations, external standards, jurisdiction, contractual constraints, sector hazards, and evidence-retention duties without presenting AIES output as legal certification |
| Open | Assess adoption and organizational feasibility | Decision products address operating-model fit, required roles and skills, review capacity, integration effort, migration/rollback, supportability, training, process change, developer/operator experience, total ownership cost, vendor/community health, and sustainable maintenance |
| Open | Validate from independent and diverse perspectives | Profile promotion requires documented technical, security, operations, human-factors, domain, and affected-party review as applicable; conflicts, minority findings, reviewer independence, competence, calibration, and disposition are retained rather than averaged away |
| Open | Generate coverage and blind-spot reports | Every assessment bundle shows perspective coverage, evidence depth, confidence, exclusions, stale evidence, conflicts, untested operating conditions, dependencies, residual risks, and the exact work required to close material gaps |
| Open | Prevent evidence reuse from inflating assurance | Canonical evidence may support multiple views but retains one source identity; reports disclose reused evidence, correlated instruments, inherited component evidence, and dependency overlap so counts, confidence, maturity, and comparison are not artificially increased |

### P1 — Repository engineering intelligence

The existing `aies audit <repo>` is a repository **conformance and practice
maturity** assessment. It verifies evidence such as tests, CI enforcement, ADRs,
security tooling, provenance, and governance controls; it does not claim that
source code is correct or that an architecture is good merely because those
artifacts exist. Deeper repository analysis is a separate evidence layer with
its own instruments and claim boundaries.

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Govern the repository-analysis layers | A companion ADR distinguishes (1) conformance audit, (2) static/dynamic repository engineering analysis, and (3) controlled repository-task benchmarking; it defines their score semantics, evidence admissibility, human authority, and prohibited claims |
| Open | Add a content-addressed Repository Subject Descriptor | Repository identity records commit/tree hash, relevant configuration, languages, build system, dependency state, submodule state, analysis scope, exclusions, environment, and tool versions so results are reproducible and changes trigger reassessment |
| Open | Define repository evidence adapters | Versioned adapters ingest native test, coverage, mutation, property/contract test, lint, type-check, complexity, duplication, dependency, SAST, secret-scan, SBOM, architecture-rule, and benchmark outputs without converting tool absence into a pass |
| Open | Implement evidence-based architecture analysis | Reports dependency/module topology, cycles, layering and boundary violations, coupling/cohesion indicators, architecture fitness-test results, and ADR-to-implementation traceability; every finding identifies affected artifacts and no unsupported “good architecture” verdict is emitted |
| Open | Implement a code-quality profile | Language-aware adapters report lint/type findings, complexity, duplication, dead-code signals, maintainability trends, documentation and testability evidence with tool/version provenance, confidence/coverage limits, and no cross-language comparison unless the instruments are compatible |
| Open | Implement correctness-assurance analysis | The platform executes or ingests reproducible tests, coverage, mutation, property/contract tests, static-analysis findings, and failure evidence; it reports demonstrated assurance and untested behavior rather than claiming that repository correctness has been proven |
| Open | Implement controlled repository-task benchmarks | Disposable, authorization-bounded workspaces run versioned defect-fix, refactoring, testing, API, migration, performance, security, and architecture tasks; patch validity, tests, regressions, safety, efficiency, and traceability are scored while the repository and executing agent remain separately identified subjects |
| Open | Emit repository remediation evidence | Every repository gap or finding feeds the common Evidence-Linked Remediation Plan with priority, impact, exact evidence, bounded corrective action, acceptance signal, owner/authority boundary, and reassessment command |
| Open | Add optional semantic repository review | A declared reviewer may analyze code/design context and propose findings with file/line evidence, uncertainty, reviewer identity, and conflicts; its output is advisory unless independently verified and never changes deterministic maturity or assurance scores by itself |
| Open | Unify repository report and comparison products | One linked bundle presents conformance maturity, architecture evidence, code quality, correctness assurance, security/tool findings, recommendations, limitations, and optional human-review status; comparisons require compatible commit scope, toolchain, configuration, language, and instrument versions |

### P2 — ECM and decision products

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Ratify AIES-ECM-01 — Engineering Capability Matrix | ECM is formally present in the Charter, Vision, architecture, Roadmap, governance, requirement IDs, and public review disposition |
| Done | Deliver a compact report bundle | Qualification Evidence Package, Canonical Assessment Result when applicable, ECM, Deployment Guidance, and Executive Summary are separate linked Markdown/JSON/HTML artifacts generated from one canonical evidence package and indexed by `report-bundle.json` |
| Done | Mature Deployment Guidance | Use / Use with Review / Avoid incorporates task evidence, current matching qualification scope, live deployment-fingerprint continuity, role/phases, autonomy, conditions, validity, residual calibration/gate risks, and operational constraints; no guidance creates authority |
| Done | Add protocol-compatible ECM comparison | Task deltas and winners appear only when risk, profile, suites, mappings, repeats, and rater protocol are compatible |
| Open | Build a cross-subject Evidence-Linked Remediation Plan | Findings from deployments, repositories, humans/teams, agents, swarms, MCP servers, coding assistants, prompt libraries, RAG systems, pipelines, platforms, and composite systems share a deterministic action schema: priority, impact, evidence, recommendation, acceptance signal, owner/authority, dependency, and reassessment trigger; optional generated narrative is labelled advisory and cannot alter evidence or scores |
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
| Open | Replace heuristic repository detection with structured evidence where available | CI, dependency, test, coverage, security, architecture, and governance checks prefer parsed manifests or imported tool results over filename/substring heuristics; heuristic fallbacks are labelled with lower evidence confidence and regression fixtures cover supported stacks |
| Open | Standardize assessment vocabulary across commands and docs | `audit` means repository/practice conformance, `analysis` means artifact/tool evidence evaluation, `benchmark` means a compatible controlled comparative study, and `qualification` means a governed human decision; help and reports do not use the terms interchangeably |
| Open | Generate and test the subject-support matrix | One machine-readable registry drives CLI help, API discovery, documentation, and tests for implemented/experimental/planned subject profiles so public claims cannot drift ahead of executable support |
| Open | Generate and test the perspective-coverage registry | One machine-readable registry drives profile applicability, coverage reports, human-readable code labels, documentation, and validation for lifecycle, cross-cutting, competency, task, risk, autonomy, stakeholder, environment, evidence, and operating-condition perspectives |
| Done | Clarify immutable artifacts and regenerable views | Storage policy classifies append-only records, derived canonical snapshots, mutable workflow state/configuration, and regenerable views; `workspace.write_json` rejects append-only replacement and `workspace.write_view` cannot target evidence paths |
| Done | Make record identifiers concurrency-safe | Qualification Records atomically claim human-readable IDs through exclusive creation; a 12-decision concurrent regression proves unique issued records and lifecycle events |
| Done | Improve local verification feedback | The documented command reports ranked durations and uses a 180-second warm-cache Windows budget with a 25% regression trigger. Single-pass report views plus signature-invalidated isolated YAML, expanded-scenario, review-ledger, and suite caches reduce the measured complete run from 216 tests in 491.51 seconds to 225 tests in a repeated 81.23–100.16-second range; cache mutation/invalidation behavior has regression coverage. Read-only API fixtures are shared safely and concurrency tests delay only the phase under test. |
| Done | Generate exhaustive CLI guidance and shell completion | A parser-derived CLI reference covers every command, subcommand, positional parameter, option, default, choice, prerequisite, interaction, result/side effect, recommended next step, and workflow sequence; CI detects undocumented parser drift, and PowerShell/Bash/Zsh Tab completion is generated from the same live command surface |
| Done | Remove local workspace archive debris safely | `aies doctor` inventories `.DS_Store`, `Thumbs.db`, `desktop.ini`, `__MACOSX`, Python/pytest caches, and misplaced regenerable views under the runs root; JSON exposes every path and category, readiness is unaffected, and tests prove the diagnostic deletes neither debris nor evidence |

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

- `pytest platform/tests -q --durations=15`: **225 passed in 81.23 seconds** on
  the latest Windows run, with repeated measurements spanning **81.23–100.16
  seconds** (down from the preceding 219-test measurement of 155.38 seconds and
  below the documented 180-second warm-cache budget).
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

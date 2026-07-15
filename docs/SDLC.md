# SDLC Reference

| | |
|---|---|
| **Document ID** | AIES-DOC-04 |
| **Status** | Review |
| **Audience** | Engineers · Architects · Engineering leadership |

The detailed reference for the sixteen AIES lifecycle phases (P01–P16): what each phase is for, who works in it, what it produces, how AI participates in it, and how work enters and leaves it. Phase, role, artifact, autonomy, and risk identifiers are defined normatively in the [Shared Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md); this document is guidance built on those definitions.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. The Phase Model

```
 Strategy & Definition            Design & Planning             Build & Verify               Deliver & Run
┌──────────────────────┐      ┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│ P01 Business Strategy│      │ P06 Solution Analysis│     │ P09 Engineering      │     │ P13 Release          │
│ P02 Business Analysis│ ───► │ P07 Architecture     │ ──► │ P10 Testing & Quality│ ──► │ P14 Operations       │
│ P03 Product Mgmt     │      │ P08 Planning         │     │ P11 Security         │     │ P15 Observability    │
│ P04 User Experience  │      └──────────────────────┘     │ P12 DevOps           │     │ P16 Continuous Impr. │
│ P05 Requirements Eng.│                                   └──────────────────────┘     └──────────┬───────────┘
└──────────────────────┘                                                                           │
        ▲                                                                                          │
        └──────────────────────────────── feedback: evidence, telemetry, learning ◄────────────────┘

 Cross-cutting domains X01–X15 (security, privacy, compliance, governance, risk, AI safety,
 human oversight, documentation, knowledge, cost, performance, scalability, reliability,
 accessibility, sustainability) apply to EVERY phase.
```

**Phases are logical, not waterfall.** P01–P16 name *kinds of work*, not calendar stages. In iterative and incremental delivery, a single sprint touches many phases; a single feature loops through P05 → P09 → P10 → P13 → P15 many times; discovery work in P02 may run continuously alongside delivery. The model exists so that autonomy levels, quality gates, roles, and evidence can be attached to *the kind of work being done* — regardless of the process framework (agile, SAFe, lean, or otherwise) that schedules it.

Two rules shape AI participation in every phase:

- Every AI-performed task MUST carry a declared autonomy level (AL0–AL4), and the maximum level is derived from the task's risk tier (RT1–RT4) per the [Taxonomy §3–4](../Shared/Taxonomy/README.md). The per-phase guidance below describes *typical* assignments within those ceilings; organizations MAY tighten them and MUST NOT exceed them without documented risk acceptance.
- Human accountability never transfers. Gated decisions belong to ROLE-13 (Human Approver); governance oversight belongs to ROLE-14 (Governance Officer). Both MUST be humans.

### Reading the phase entries

Each entry gives: **Purpose** · **Key activities** · **Primary roles** (ROLE IDs) · **Typical artifacts** (ART IDs) · **AI participation** (typical autonomy by risk tier) · **Entry / Exit criteria** · **Cross-cutting hotspots** (the X-domains that concentrate risk in this phase).

---

## 2. Strategy & Definition Phases

### P01 — Business Strategy

**Purpose.** Establish *why* the organization invests: the business outcomes, constraints, and appetite that justify and bound engineering work.

**Key activities.** Market and opportunity analysis; investment case development; portfolio prioritization; definition of strategic constraints (regulatory posture, risk appetite, build-vs-buy stance); setting the organizational policy for AI participation itself.

**Primary roles.** ROLE-03 (Product Manager), ROLE-14 (Governance Officer), with ROLE-02 (Business Analyst) support. Strategy decisions are approved by executives acting as ROLE-13 (Human Approver).

**Typical artifacts.** ART-01 (Business Case).

**AI participation.** AI accelerates evidence-gathering, not judgment. Market synthesis, scenario modeling, and drafting of investment cases sit comfortably at AL1–AL2. Strategy *decisions* are RT4 by nature (irreversible commitments, fiduciary consequences) and remain AL0–AL1: AI informs, humans decide.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (research summaries, internal briefs) | AL2–AL3 |
| RT2 (draft business cases) | AL2 |
| RT3 (portfolio recommendations) | AL1 |
| RT4 (investment decisions) | AL0–AL1 |

**Entry criteria.** A strategic question or opportunity is articulated; sponsorship exists.
**Exit criteria.** An approved business case (ART-01) with measurable outcomes, constraints, and an accountable owner.

**Cross-cutting hotspots.** X04 Governance, X05 Risk Management, X10 Cost Optimization.

---

### P02 — Business Analysis

**Purpose.** Establish *what problem is being solved*: stakeholder needs, current-state pain, and the gap between present and desired capability.

**Key activities.** Stakeholder analysis and elicitation; current-state/target-state analysis; process modeling; problem framing and root-cause analysis; feasibility input to P06.

**Primary roles.** ROLE-02 (Business Analyst); ROLE-03 (Product Manager) as consumer; ROLE-13 for scope sign-off.

**Typical artifacts.** ART-01 (Business Case, refined), inputs to ART-02 (Product Requirement).

**AI participation.** AI is strong at synthesizing interview notes, mining process documentation, drafting current-state models, and surfacing inconsistencies across sources. Elicitation itself — the human conversation — stays human-led, with AI at AL1 preparing questions and AL2 producing analysis drafts for analyst review. Misframed problems poison every downstream phase, so analysis conclusions warrant per-item human review (AL2 ceiling in practice, even where risk tiering would permit more).

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (note synthesis, doc mining) | AL3 |
| RT2 (draft process models, gap analyses) | AL2 |
| RT3 (feasibility conclusions, scope recommendations) | AL1–AL2 |
| RT4 (regulated-domain analysis) | AL1 |

**Entry criteria.** An approved or in-progress business case names the opportunity.
**Exit criteria.** A validated problem statement and analyzed needs, accepted by stakeholders, feeding P03/P05.

**Cross-cutting hotspots.** X02 Privacy (stakeholder data in elicitation records), X08 Documentation, X09 Knowledge Management.

---

### P03 — Product Management

**Purpose.** Decide *what to build, in what order*: translate validated needs into a prioritized product direction.

**Key activities.** Product vision and roadmap; backlog creation and prioritization; trade-off management (value vs. cost vs. risk); success-metric definition; release-scope decisions with P13.

**Primary roles.** ROLE-03 (Product Manager); ROLE-02 and ROLE-04 as contributors; ROLE-13 for roadmap approval.

**Typical artifacts.** ART-02 (Product Requirement), ART-05 (Work Item / Plan, at epic level).

**AI participation.** AI drafts requirement candidates, clusters and de-duplicates backlog items, simulates prioritization scenarios, and keeps roadmap documents consistent. Applying risk tiers to backlog items (a prerequisite for all downstream autonomy decisions) is an analysis task AI can draft at AL2 with human ratification — see the worked example EX-01 in [examples/](../examples/README.md). Prioritization *decisions* embody accountability for value and remain human.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (backlog hygiene, duplicate detection) | AL3–AL4 |
| RT2 (draft requirements, draft risk-tiering) | AL2–AL3 |
| RT3 (roadmap changes, cut-line decisions) | AL1 |
| RT4 (commitments with contractual/regulatory force) | AL0–AL1 |

**Entry criteria.** Validated problem statement and business case exist.
**Exit criteria.** A prioritized, risk-tiered backlog with measurable success criteria; requirements ready for P05 elaboration.

**Cross-cutting hotspots.** X04 Governance, X05 Risk Management, X10 Cost Optimization.

---

### P04 — User Experience

**Purpose.** Establish *how humans will use it*: interaction design, information architecture, and usability evidence.

**Key activities.** User research; persona and journey definition; information architecture; wireframing and prototyping; usability testing; accessibility design; design-system stewardship.

**Primary roles.** ROLE-04 (UX Designer); ROLE-03 and ROLE-06 as partners; ROLE-13 for design sign-off on regulated or high-risk surfaces.

**Typical artifacts.** ART-03 (UX Specification).

**AI participation.** AI generates design variants, drafts UX copy, produces prototype scaffolding, and synthesizes usability findings quickly. Research with human participants remains human-conducted (ethics, consent, interpretation). Accessibility-critical flows (X14) and safety-relevant interactions warrant tightened review regardless of nominal tier.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (exploratory variants, prototype scaffolds) | AL3–AL4 |
| RT2 (production design drafts, UX copy) | AL2–AL3 |
| RT3 (customer-facing flows, accessibility-critical surfaces) | AL2 |
| RT4 (safety-critical interaction design) | AL1 |

**Entry criteria.** Prioritized requirements identify the users and jobs to design for.
**Exit criteria.** UX specification (ART-03) validated with users, meeting accessibility criteria, ready for P05/P09.

**Cross-cutting hotspots.** X14 Accessibility, X02 Privacy (research data), X06 AI Safety (AI-generated UI copy and dark-pattern avoidance).

---

### P05 — Requirements Engineering

**Purpose.** Establish *what the system must do*: precise, testable, traceable requirements.

**Key activities.** Requirement elaboration and specification; acceptance-criteria definition; consistency and completeness analysis; traceability establishment (requirement → design → test); requirement change control.

**Primary roles.** ROLE-02 (Business Analyst); ROLE-07 (QA Engineer) for testability review; ROLE-05 (Architect) for feasibility; ROLE-13 for baseline approval.

**Typical artifacts.** ART-02 (Product Requirement, elaborated with acceptance criteria).

**AI participation.** This is one of AI's highest-leverage phases: drafting acceptance criteria, detecting ambiguity and contradiction across a requirement set, generating traceability links, and keeping specifications synchronized with decisions. Because every downstream phase consumes requirements, errors amplify — per-item human review (AL2) is the working norm for anything that will be built, with AL3 acceptable for consistency-checking and traceability maintenance where outputs are advisory.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (formatting, traceability link upkeep) | AL3–AL4 |
| RT2 (draft acceptance criteria, ambiguity reports) | AL2–AL3 |
| RT3 (requirements for customer-facing behavior) | AL2 |
| RT4 (requirements for safety/financial/regulated functions) | AL1 |

**Entry criteria.** Prioritized backlog items selected for elaboration; UX inputs available where relevant.
**Exit criteria.** Requirements baselined: testable, risk-tiered, traceable, and approved.

**Cross-cutting hotspots.** X03 Compliance (regulatory requirements captured), X08 Documentation, X07 Human Oversight (baseline gates).

---

## 3. Design & Planning Phases

### P06 — Solution Analysis

**Purpose.** Establish *how candidate solutions compare*: evaluate options before committing architecture.

**Key activities.** Option identification (build/buy/reuse/extend); trade-off analysis against requirements and constraints; proof-of-concept spikes; cost and risk modeling; recommendation and decision capture.

**Primary roles.** ROLE-05 (Architect); ROLE-02 and ROLE-03 as contributors; ROLE-13 approves the selected option.

**Typical artifacts.** ART-04 (Architecture Decision Record) capturing the comparison and choice.

**AI participation.** AI enumerates options humans miss, builds comparison matrices, drafts ADR text, and rapidly produces throwaway proof-of-concept code (RT1 — high autonomy is appropriate precisely because PoC code never ships). The *decision* is gated: option selection commits the organization and is recorded in an ADR with human deciders.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (PoC spikes, comparison drafts) | AL3–AL4 |
| RT2 (trade-off analyses) | AL2–AL3 |
| RT3 (recommendations affecting production direction) | AL1–AL2 |
| RT4 (irreversible platform commitments) | AL1 |

**Entry criteria.** Baselined requirements and constraints; a decision worth analyzing.
**Exit criteria.** An accepted ADR (ART-04) selecting the option, with alternatives and trade-offs recorded.

**Cross-cutting hotspots.** X05 Risk Management, X10 Cost Optimization, X12 Scalability.

---

### P07 — Architecture

**Purpose.** Establish *how the system is structured*: components, interfaces, qualities, and the decisions that bind them.

**Key activities.** Architecture design and documentation; interface and contract definition; quality-attribute scenarios (performance, reliability, scalability); architecture review; ADR authoring; conformance guidance for P09.

**Primary roles.** ROLE-05 (Architect); ROLE-08 (Security Engineer) for threat-informed design; ROLE-06 as reviewer; ROLE-13 for architecture gate approval.

**Typical artifacts.** ART-04 (Architecture Decision Record), architecture documentation, [diagram sources](../diagrams/README.md).

**AI participation.** AI drafts architecture documents and diagrams, checks designs against stated quality scenarios, detects drift between documented and implemented architecture, and stress-tests proposals ("what breaks under 10× load?"). Architectural decisions are long-lived and expensive to reverse — typically RT3–RT4 — so the decision itself stays at AL1–AL2 with the analysis pipeline at AL2–AL3.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (diagram generation, doc formatting) | AL3–AL4 |
| RT2 (draft designs for internal components) | AL2–AL3 |
| RT3 (production system structure, schema design) | AL2 |
| RT4 (safety-critical / regulated architecture) | AL1 |

**Entry criteria.** Selected solution option; baselined requirements with quality attributes.
**Exit criteria.** Approved architecture with ADRs recorded; conformance criteria available to P09; threat model inputs delivered to P11.

**Cross-cutting hotspots.** X01 Security (design-time), X12 Scalability, X13 Reliability, X08 Documentation.

---

### P08 — Planning

**Purpose.** Establish *how work is decomposed and sequenced*: turn the architecture and backlog into an executable plan.

**Key activities.** Work breakdown; estimation; dependency and critical-path analysis; capacity planning across humans and AI agents; risk-tier tagging of work items; iteration/increment planning; definition of done per item.

**Primary roles.** ROLE-01 (Planner); ROLE-03 and ROLE-06 as contributors; ROLE-14 verifies risk-tier assignments on sampled items.

**Typical artifacts.** ART-05 (Work Item / Plan).

**AI participation.** AI decomposes epics into work items, drafts estimates from historical data, detects dependency conflicts, and continuously replans as reality diverges. Plans are advisory until committed, which keeps most planning work at RT1–RT2 and allows high autonomy; the *commitment* (what the team promises, what the release contains) is a human decision. Every work item MUST leave planning with a risk tier, because that tier drives autonomy ceilings in P09–P13.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (decomposition drafts, estimate suggestions) | AL3–AL4 |
| RT2 (iteration plan drafts, dependency analysis) | AL3 |
| RT3 (commitment-affecting replans) | AL1–AL2 |
| RT4 (plans with contractual/regulatory deadlines) | AL1 |

**Entry criteria.** Approved architecture and prioritized, elaborated backlog.
**Exit criteria.** Committed plan of risk-tiered work items with owners (human, AI, or pair) and definitions of done.

**Cross-cutting hotspots.** X05 Risk Management (tier assignment), X04 Governance, X10 Cost Optimization (human/AI capacity mix).

---

## 4. Build & Verify Phases

### P09 — Engineering

**Purpose.** Establish *how the system is built*: implementation of the planned work to the defined quality.

**Key activities.** Implementation; code review; refactoring; unit testing; integration against contracts; documentation-as-you-go; maintaining provenance of every change.

**Primary roles.** ROLE-06 (Software Engineer); ROLE-05 for conformance; ROLE-11 (Documentation Engineer) for docs; ROLE-13 at merge gates for elevated tiers.

**Typical artifacts.** ART-06 (Source Change — commit / PR), ART-13 (Prompt / Context Asset, as engineering inputs).

**AI participation.** The most mature AI participation surface — and the one where risk-tier discipline matters most, because autonomy here directly changes production code. The default AIES posture: AI implements, humans (or qualified AI reviewers at lower tiers) review, gates enforce. Every AI-produced change carries provenance (who/what produced it, under which autonomy level) and is traceable to an approved work item. Autonomy increases beyond the defaults MUST be backed by AESQS qualification evidence for the specific task class — see the worked example EX-03 (scored AI-produced pull request).

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (formatting, typos, test scaffolding, prototypes) | AL4 |
| RT2 (feature code behind review, internal tooling) | AL3 |
| RT3 (auth-adjacent code, schema changes, customer-facing behavior) | AL2 |
| RT4 (safety-critical, financial, regulated, irreversible) | AL1 |

**Entry criteria.** A planned, risk-tiered work item with acceptance criteria and an assigned performer.
**Exit criteria.** Change merged through the tier-appropriate gate: tests pass, review complete, provenance recorded, traceability to work item intact.

**Cross-cutting hotspots.** X01 Security, X06 AI Safety, X07 Human Oversight, X09 Knowledge Management (context assets), X15 Sustainability (compute cost of generation loops).

---

### P10 — Testing & Quality

**Purpose.** Establish *how correctness is demonstrated*: objective, repeatable evidence that the system meets its requirements.

**Key activities.** Test strategy and design; test implementation and execution; coverage and gap analysis; defect triage; quality-gate definition; evaluation of AI-produced artifacts along EV1–EV6; test-data management.

**Primary roles.** ROLE-07 (QA Engineer); ROLE-06 for testability; ROLE-13 at release-quality gates.

**Typical artifacts.** ART-07 (Test Suite & Test Report).

**AI participation.** AI generates test cases from requirements, mutates inputs to find edge cases, maintains suites as code evolves, and triages failures. A structural caution applies: **the independence rule** — an AI system SHOULD NOT be the sole verifier of its own output class. Verification of AI-produced code by the same agent (or an agent sharing its context) weakens the evidence; independent suites, property-based checks, and human sampling restore it. Test *code* is usually RT1–RT2 (it does not ship to users), permitting high autonomy; the *quality verdict* on an RT3+ change is gated.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (test scaffolding, regression maintenance) | AL4 |
| RT2 (test suites for reviewed features) | AL3 |
| RT3 (acceptance verdicts on significant changes) | AL2 |
| RT4 (verification of critical functions) | AL1 |

**Entry criteria.** Testable requirements and a change (or system) to verify.
**Exit criteria.** Tier-appropriate evidence recorded (ART-07): coverage adequate, gates passed, residual defects dispositioned by an accountable human where RT3+.

**Cross-cutting hotspots.** X07 Human Oversight (verdict gates), X13 Reliability, X05 Risk Management.

---

### P11 — Security

**Purpose.** Establish *how the system resists abuse*: security engineering across design, implementation, and the AI toolchain itself.

**Key activities.** Threat modeling; secure-design review; static/dynamic analysis; dependency and supply-chain assessment; penetration testing; secrets and access governance; **securing the AI participation surface itself** (agent permissions, tool access, prompt-injection resistance, data exfiltration paths).

**Primary roles.** ROLE-08 (Security Engineer); ROLE-05 and ROLE-06 as partners; ROLE-13 for risk acceptance; ROLE-14 for policy exceptions.

**Typical artifacts.** ART-08 (Security Assessment).

**AI participation.** AI scales security work dramatically — scanning, triage, threat-model drafting, exploit-hypothesis generation — but security conclusions are adversarial judgments with asymmetric failure costs. Findings and fixes are drafted at AL2–AL3; *risk acceptance and severity dispositions* are human (AL1). Note the dual mandate: this phase secures the product **and** the AI systems participating in its production. Agent credentials, tool envelopes, and guardrails are security assets under this phase's scrutiny.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (scan execution, finding de-duplication) | AL3–AL4 |
| RT2 (triage drafts, fix proposals for internal systems) | AL2–AL3 |
| RT3 (auth-adjacent fixes, severity dispositions) | AL2 |
| RT4 (risk acceptance, incident-grade findings) | AL0–AL1 |

**Entry criteria.** Design or change available for assessment; threat model inputs from P07.
**Exit criteria.** Assessment recorded (ART-08); findings dispositioned; no unaccepted RT3+ risk outstanding at the gate.

**Cross-cutting hotspots.** X01 Security (definitional), X02 Privacy, X03 Compliance, X06 AI Safety.

---

### P12 — DevOps

**Purpose.** Establish *how change flows to production*: the automated path from merged change to running system.

**Key activities.** Pipeline design and maintenance; environment management; infrastructure as code; artifact and dependency management; gate automation (embedding P10/P11 checks); pipeline security and least-privilege for both human and AI actors.

**Primary roles.** ROLE-09 (DevOps Engineer); ROLE-08 for pipeline security; ROLE-13 where manual gates exist.

**Typical artifacts.** ART-09 (Pipeline Definition).

**AI participation.** AI maintains pipeline definitions, diagnoses build failures, optimizes caching and flow, and drafts infrastructure code. Pipelines are the *enforcement fabric* for AIES controls — the place where autonomy envelopes, gates, and audit trails become executable (see worked example EX-05, a gate design for a delivery pipeline). Because pipeline changes can silently alter what reaches production, production-affecting pipeline and infrastructure changes are RT3 by default even when the diff looks small.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (non-production tooling, cache tuning) | AL3–AL4 |
| RT2 (build steps for internal systems) | AL3 |
| RT3 (production pipeline/config, deployment logic) | AL2 |
| RT4 (gate removal or bypass, credential handling) | AL1 |

**Entry criteria.** A defined path-to-production need; quality and security gates specified by P10/P11.
**Exit criteria.** Versioned pipeline (ART-09) enforcing tier-appropriate gates, with every execution audit-trailed.

**Cross-cutting hotspots.** X01 Security (supply chain), X04 Governance (gate integrity), X13 Reliability.

---

## 5. Deliver & Run Phases

### P13 — Release

**Purpose.** Establish *how value reaches users*: the controlled activation of change for real users.

**Key activities.** Release planning and scoping; progressive delivery (canary, staged rollout, feature flags); release verification; rollback readiness; release communication; release-record keeping.

**Primary roles.** ROLE-09 (DevOps Engineer); ROLE-03 for scope; ROLE-13 for release approval at elevated tiers.

**Typical artifacts.** ART-10 (Release Record).

**AI participation.** AI assembles release notes, verifies rollout health against baselines, executes progressive-delivery steps within a defined envelope, and triggers rollback when guardrail metrics breach. Releases at RT1–RT2 with automated verification and automatic rollback are a natural AL3 fit (human approves the checkpoint policy, AI executes within it). User-visible or contractually significant releases keep a human decision at the front.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (internal tool releases, doc releases) | AL3–AL4 |
| RT2 (staged rollout of reviewed features) | AL3 |
| RT3 (customer-facing behavior changes) | AL2 |
| RT4 (regulated, financial, irreversible releases) | AL1 |

**Entry criteria.** Change has passed P10/P11/P12 gates; rollback path verified.
**Exit criteria.** Release live at intended exposure; ART-10 recorded (what shipped, who/what approved, verification evidence, rollback status).

**Cross-cutting hotspots.** X07 Human Oversight, X13 Reliability, X03 Compliance (release evidence).

---

### P14 — Operations

**Purpose.** Establish *how the system is run*: keeping the delivered system healthy in production.

**Key activities.** Incident detection and response; runbook execution and maintenance; capacity and cost management; patching and routine maintenance; on-call operation; post-incident review (feeding P16).

**Primary roles.** ROLE-10 (SRE); ROLE-09 as partner; ROLE-13 for high-impact interventions.

**Typical artifacts.** ART-11 (Runbook).

**AI participation.** AI executes runbooks, correlates signals during incidents, drafts incident timelines, and performs routine remediation (restarts, scaling, cert rotation) inside a tightly specified envelope. Operations is where AL3 delegation shows its clearest value *and* its sharpest edge: actions are immediate and production-real. The envelope discipline is strict — well-rehearsed, reversible remediations at AL3; novel or destructive interventions escalate to humans. Every autonomous action lands in the audit trail (ART-15).

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (diagnostics, log collection) | AL4 |
| RT2 (rehearsed, reversible remediation per runbook) | AL3 |
| RT3 (production config changes, failovers) | AL2 |
| RT4 (data-destructive or irreversible interventions) | AL1 |

**Entry criteria.** System in production with runbooks, SLOs, and escalation paths defined.
**Exit criteria.** Continuous phase — "exit" per event: incident resolved, action audit-trailed, learning routed to P16.

**Cross-cutting hotspots.** X13 Reliability, X07 Human Oversight, X10 Cost Optimization, X01 Security (operational access).

---

### P15 — Observability

**Purpose.** Establish *how behavior is understood*: the telemetry, evaluation, and insight that make the system — and the AI participation in building it — inspectable.

**Key activities.** Instrumentation design; metrics/logs/traces pipelines; SLI/SLO definition; anomaly detection; dashboards and alerting; **AI-participation telemetry** (autonomy-level usage, gate outcomes, escalation rates, evaluation scores over time).

**Primary roles.** ROLE-10 (SRE); ROLE-06 for instrumentation; ROLE-14 consumes governance telemetry.

**Typical artifacts.** ART-12 (Telemetry & Evaluation Report).

**AI participation.** AI tunes alert thresholds, detects anomalies, drafts dashboards, and summarizes behavior for humans. Observability outputs are mostly advisory (RT1–RT2), so autonomy can run high — with one caution: alert *suppression* and SLO redefinition change what humans get to see, and are RT3 gate-worthy. Observability is also the substrate of the Evidence Driven principle: AESQS qualification and AL-increase decisions consume the evaluation data this phase produces.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (dashboards, summaries, anomaly flags) | AL3–AL4 |
| RT2 (alert tuning with human-visible changelog) | AL3 |
| RT3 (alert suppression, SLO changes) | AL2 |
| RT4 (telemetry affecting regulatory reporting) | AL1 |

**Entry criteria.** System (or engineering process) running with instrumentation requirements defined.
**Exit criteria.** Continuous phase — success is that P14 and P16 decisions are made on current, trustworthy evidence (ART-12).

**Cross-cutting hotspots.** X02 Privacy (telemetry content), X08 Documentation, X05 Risk Management (evidence quality).

---

### P16 — Continuous Improvement

**Purpose.** Establish *how the system and process evolve*: converting operational and evaluation evidence into deliberate change — to the product, the process, and the autonomy grants themselves.

**Key activities.** Retrospectives and post-incident learning; trend analysis across ART-12 evidence; process experiments; **autonomy-level re-evaluation** (raising grants where qualification evidence supports it, revoking where it does not); knowledge-base curation; feedback into P01–P08.

**Primary roles.** ROLE-12 (Knowledge Manager), ROLE-14 (Governance Officer); all roles contribute; ROLE-13 approves autonomy changes.

**Typical artifacts.** ART-12 (Telemetry & Evaluation Report), ART-13 (Prompt / Context Asset, curated), ART-14 (Agent Definition, revised), ART-15 (Audit Trail Record, analyzed).

**AI participation.** AI mines audit trails and evaluation reports for patterns humans miss, drafts retrospective summaries, proposes process and context-asset improvements, and prepares the evidence packets behind autonomy re-evaluation. The re-evaluation *decision* — expanding or contracting an agent's envelope — is a governance act: evidence-driven, human-approved, reversible, per [Taxonomy R03](../Shared/Taxonomy/README.md). This closed loop is what lets AIES absorb rapid AI capability change without rewriting the standard.

| Risk tier | Typical autonomy |
|-----------|------------------|
| RT1 (pattern reports, retro drafts) | AL3–AL4 |
| RT2 (context-asset updates, process proposals) | AL2–AL3 |
| RT3 (agent-definition changes) | AL2 |
| RT4 (autonomy-grant decisions) | AL0–AL1 (human decision on AI-prepared evidence) |

**Entry criteria.** Evidence exists — telemetry, evaluations, audit trails, incident learnings.
**Exit criteria.** Continuous phase — improvements are themselves work items that re-enter the lifecycle at the appropriate phase with the appropriate risk tier.

**Cross-cutting hotspots.** X09 Knowledge Management, X04 Governance, X06 AI Safety, X07 Human Oversight.

---

## 6. Using This Reference

- **Mapping your process:** identify which phases each of your existing ceremonies and pipelines performs; attach risk tiers and autonomy declarations to the *work*, not to the ceremony. AIES layers onto agile, SAFe, or any iterative framework without replacing it (see [FAQ](FAQ.md)).
- **Per-phase knowledge:** the disciplines and practices behind each phase are elaborated in [AEBOK](../AEBOK/README.md).
- **Evaluating performers:** capability evaluation for any phase's task classes is defined in [AESQS](../AESQS/README.md).
- **Operating model:** roles, gates, and workflows that execute these phases are defined in [AEOS](../AEOS/README.md).

## Related Documents

- [Shared Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md) — the normative phase, domain, autonomy, risk, role, and artifact identifiers this reference builds on
- [AEBOK (AIES-AEBOK-00)](../AEBOK/README.md) — per-phase knowledge areas
- [AESQS (AIES-AESQS-00)](../AESQS/README.md) — capability evaluation for each phase's task classes
- [AEOS (AIES-AEOS-00)](../AEOS/README.md) — the roles, gates, and workflows that execute these phases
- [Repository Architecture (AIES-DOC-03)](ARCHITECTURE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

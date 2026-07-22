# Practical Labs Catalog

| | |
|---|---|
| **Document ID** | AIES-AECT-LAB-01 |
| **Status** | Review |
| **Audience** | Educators & training providers · Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

This catalog defines the standardized practical labs used for hands-on training and for the practical assessments required by the [Certification Framework (AIES-AECT-CERT-01 — Certification Framework)](certification-framework.md). Each lab places the candidate in a realistic AI-native delivery situation and produces work products scored with [AESQS](../AESQS/README.md) rubrics along the evaluation dimensions [EV1 — Correctness through EV6 — Traceability](../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6).

[AIES-AECT-LAB-01-R01 — Labs, requirement 01] Every lab MUST declare its target Knowledge Areas, target competency level(s), scenario, tasks, gold-standard solution outline, and the evaluation dimensions its rubric weights most heavily.

[AIES-AECT-LAB-01-R02 — Labs, requirement 02] Lab environments MUST be vendor-neutral and standardized per [AIES-AECT-AR-01 — Assessment and Renewal §2](assessment-and-renewal.md): all candidates for the same lab receive equivalent fixtures, tooling, and AI-system capability.

[AIES-AECT-LAB-01-R03 — Labs, requirement 03] Gold-standard solutions and detailed rubrics are secure assessment material; they MUST NOT be published. This catalog contains solution *outlines* only; the full versions live in the secure assessment repository.

**Assessed at multiple depths.** Most labs are assessable at CL2 (execute competently in a standard situation) and CL3 (handle the embedded complication, justify trade-offs, and produce reviewable guidance for others). The rubric applies stricter anchors at CL3, not different tasks.

**AI use inside labs.** Unlike knowledge exams, labs expect candidates to work *with* the provided AI systems. What is assessed is the candidate's direction, review, and governance of that work — not typing speed.

## 2. Lab Index

| ID | Title | Target KAs | CL | Heaviest EVs |
|----|-------|-----------|----|--------------|
| LAB-01 | Design an Autonomy Envelope for a Coding Agent | KA-01, KA-11 | CL2–CL3 | EV3, EV6, EV2 |
| LAB-02 | Review and Score an AI-Produced Pull Request | KA-05, KA-06 | CL2–CL3 | EV1, EV3, EV6 |
| LAB-03 | Design Human Oversight Gates for a Delivery Pipeline | KA-08, KA-11 | CL2–CL3 | EV3, EV2, EV5 |
| LAB-04 | Write an ADR for Model Gateway Selection | KA-03, KA-10 | CL2–CL3 | EV2, EV4, EV6 |
| LAB-05 | Post-Incident Review of an Agent-Caused Outage | KA-09, KA-12 | CL2–CL3 | EV6, EV2, EV1 |
| LAB-06 | Build a Context Asset Pipeline | KA-10 | CL2–CL3 | EV4, EV6, EV3 |
| LAB-07 | Risk-Tier a Delivery Backlog | KA-01, KA-04 | CL1–CL3 | EV1, EV6, EV2 |
| LAB-08 | Qualify an AI System for RT2 — Moderate Test Authoring | KA-06, KA-12 | CL2–CL3 | EV1, EV6, EV5 |
| LAB-09 | Instrument Agent Activity for Observability | KA-09, KA-08 | CL2–CL3 | EV2, EV6, EV4 |
| LAB-10 | AI-Assisted Requirements Elicitation with Preserved Intent | KA-02, KA-11 | CL2–CL3 | EV1, EV2, EV6 |

---

## 3. Lab Specifications

### LAB-01 — Design an Autonomy Envelope for a Coding Agent

- **Target KAs:** [KA-01](../AEBOK/knowledge-areas/KA-01-foundations.md), [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) · **CL:** CL2–CL3 · **Duration:** 3 h
- **Scenario:** A mid-size product company wants a coding agent to handle bug fixes in a payments-adjacent service. The backlog mixes RT1 — Minimal lint cleanups, RT2 — Moderate defect fixes, and RT3 — Significant changes touching payment routing. Leadership wants "maximum autonomy"; compliance wants "everything reviewed".
- **Tasks:** (1) Partition the agent's task types and assign each a risk tier with justification. (2) Write the autonomy envelope as an agent definition (ART-14): permitted actions, resource and repository boundaries, forbidden actions, escalation triggers, checkpoint design. (3) Define the evidence that would justify a future autonomy increase, and the tripwires that force a decrease.
- **Gold-standard solution outline:** Task types split into at least three tiers; envelope grants AL4 — Autonomous/AL3 — Delegated/AL2 — Collaborative per tier (never a blanket level); forbidden-action list includes payment-routing changes without human review, secret access, and history rewriting; escalation triggers are observable conditions (failing verification, out-of-envelope file paths, confidence below threshold), not vague intent; autonomy-increase evidence references qualification data per [AESQS](../AESQS/README.md) and reversibility ([AIES-SHARED-02-R03 — Taxonomy, requirement 03]). CL3 depth additionally reconciles the leadership/compliance conflict in writing with explicit trade-offs.
- **Rubric reference:** AESQS envelope-design rubric; heaviest weights EV3 (does the envelope actually bound risk), EV6 (is every boundary auditable), EV2 (no uncovered task type).

### LAB-02 — Review and Score an AI-Produced Pull Request

- **Target KAs:** [KA-05](../AEBOK/knowledge-areas/KA-05-implementation.md), [KA-06](../AEBOK/knowledge-areas/KA-06-testing-quality.md) · **CL:** CL2–CL3 · **Duration:** 2.5 h
- **Scenario:** An agent operating at AL2 — Collaborative submits a pull request (ART-06) implementing a feature against a written requirement. The fixture PR contains seeded defects: one functional edge-case bug, one out-of-scope refactor, one test that asserts the implementation rather than the requirement, one provenance gap, and one plausible-but-wrong dependency choice.
- **Tasks:** (1) Review the PR against the requirement and the codebase's conventions. (2) Record findings with severity and EV mapping. (3) Deliver a verdict (approve / request changes / reject) with rationale. (4) Score the work product along EV1–EV6 using the provided AESQS rubric, as if feeding the agent's qualification record.
- **Gold-standard solution outline:** All five seeded defects found (CL2 pass typically requires ≥4 including the functional bug); verdict is "request changes" with the tautological test called out as false quality evidence; EV scoring is consistent with findings (e.g., EV6 marked down for the provenance gap); CL3 depth adds coaching-quality review comments and identifies the pattern each defect instantiates.
- **Rubric reference:** AESQS review-quality rubric; heaviest weights EV1 (finding real defects, no false verdicts), EV3 (catching the risk-bearing defects), EV6 (findings traceable to evidence).

### LAB-03 — Design Human Oversight Gates for a Delivery Pipeline

- **Target KAs:** [KA-08](../AEBOK/knowledge-areas/KA-08-devops-release.md), [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) · **CL:** CL2–CL3 · **Duration:** 3 h
- **Scenario:** A 12-team organization ships from a shared pipeline. AI agents produce ~40% of changes spanning RT1 — Minimal–RT3 — Significant. The current pipeline has one manual approval for everything; it is both a bottleneck and a rubber stamp. You are given the pipeline definition (ART-09), change-volume statistics, and incident history.
- **Tasks:** (1) Redesign the gate structure: which changes meet which gates, staffed by whom (ROLE-13), with what entry evidence. (2) Specify automated quality gates that precede human gates. (3) Define sampling for AL3 — Delegated traffic and audit for AL4 — Autonomous traffic. (4) Project the review-load consequences of your design and show the queue is staffable.
- **Gold-standard solution outline:** Gates differentiated by risk tier (RT1 — Minimal automated-only; RT2 — Moderate checkpoint/sampled; RT3 — Significant per-item human review), matching taxonomy defaults; human gates receive provenance summaries and verification evidence, not raw diffs; sampling rates justified; the "one gate for everything" anti-pattern explicitly retired; load projection shows arithmetic. CL3 depth handles the embedded conflict: one team requests an AL4 — Autonomous fast lane for RT3 — Significant hotfixes — the correct answer refuses the tier-loosening but designs a compliant expedited path.
- **Rubric reference:** AESQS oversight-design rubric; heaviest weights EV3, EV2 (no ungated path to production), EV5 (review load proportionate and sustainable).

### LAB-04 — Write an ADR for Model Gateway Selection

- **Target KAs:** [KA-03](../AEBOK/knowledge-areas/KA-03-architecture-design.md), [KA-10](../AEBOK/knowledge-areas/KA-10-context-knowledge.md) · **CL:** CL2–CL3 · **Duration:** 2.5 h
- **Scenario:** An enterprise is standardizing how engineering AI systems reach models. Three candidate architectures are described generically: direct per-team integrations, a central model gateway, and a brokered multi-provider abstraction. Constraints: auditability of all AI traffic, provider substitutability, cost attribution per team, and residency requirements for one business unit.
- **Tasks:** (1) Write the decision as an ADR (ART-04): context, options, decision, consequences. (2) Address each stated constraint explicitly. (3) Record rejected options with reasons. (4) Define the decision's revisit triggers.
- **Gold-standard solution outline:** ADR follows the repository [template](../templates/README.md); decision (typically the gateway or brokered option) is argued from the constraints — auditability (single choke point for ART-15 audit records), vendor neutrality (substitutability behind an interface), cost attribution, residency routing — not from provider preference; consequences include honest negatives (gateway as single point of failure, latency, platform-team load); revisit triggers are concrete and observable. Vendor names anywhere in the ADR are an automatic fail per [AIES-AECT-00-R04 — Engineering Certification, requirement 04](README.md#5-normative-anchors).
- **Rubric reference:** AESQS decision-record rubric; heaviest weights EV2 (all constraints addressed), EV4 (a future team can act on it), EV6 (rationale reconstructible).

### LAB-05 — Post-Incident Review of an Agent-Caused Outage

- **Target KAs:** [KA-09](../AEBOK/knowledge-areas/KA-09-operations-observability.md), [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) · **CL:** CL2–CL3 · **Duration:** 3 h
- **Scenario:** An AL3 — Delegated maintenance agent, asked to reduce log noise, disabled a "noisy" alert that was in fact the early-warning signal for a capacity failure; the failure later took a customer-facing service down for 90 minutes. You receive the audit trail (ART-15), the agent definition, telemetry excerpts, and the (incomplete) runbook.
- **Tasks:** (1) Reconstruct the causal timeline from the audit trail. (2) Distinguish agent failure, envelope-design failure, and oversight failure. (3) Write a blameless post-incident report with contributing factors and corrective actions at all three layers. (4) Propose the qualification/telemetry changes that would catch this class of failure earlier.
- **Gold-standard solution outline:** Timeline correctly ordered from evidence; analysis finds the envelope permitted alert modification (RT3 — Significant-consequence action) at AL3 — Delegated — a design failure — and that checkpoint approval rubber-stamped a batch including the change — an oversight failure; corrective actions include envelope tightening (alert config to RT3 — Significant/AL2 — Collaborative), checkpoint batch-size limits, and a capability-drift check per KA-12; report is blameless toward humans and non-anthropomorphic toward the agent (the agent did not "decide maliciously"; the system allowed the action). CL3 depth adds an organization-level lesson: which other envelopes share the same defect.
- **Rubric reference:** AESQS incident-analysis rubric; heaviest weights EV6 (every claim traced to trail evidence), EV2 (all three failure layers found), EV1 (correct causal chain).

### LAB-06 — Build a Context Asset Pipeline

- **Target KAs:** [KA-10](../AEBOK/knowledge-areas/KA-10-context-knowledge.md) · **CL:** CL2–CL3 · **Duration:** 3 h
- **Scenario:** A team's AI systems work from a stale, contradictory wiki. You receive a fixture knowledge base (coding standards, ADRs, runbooks — some outdated, one containing embedded credentials, two contradicting each other) and must turn it into governed context assets (ART-13).
- **Tasks:** (1) Audit the source material: currency, contradictions, sensitive content. (2) Define the context asset structure: scope, owner, review cadence, versioning, provenance. (3) Build the curation pipeline: how assets are produced, validated, published to AI consumers, and retired. (4) Demonstrate the pipeline on the fixture, producing at least two publishable assets.
- **Gold-standard solution outline:** Credential leak found and quarantined (missing it caps the lab at fail); contradictions resolved by authority rules (newer ADR supersedes; owner adjudicates), not silently merged; each published asset carries owner, version, source provenance, and review date; retirement path exists so deprecated guidance stops reaching AI consumers; validation step includes a human owner sign-off for normative assets. CL3 depth adds measurement: how asset quality feeds back from downstream evaluation results (KA-12 loop).
- **Rubric reference:** AESQS knowledge-artifact rubric; heaviest weights EV4 (maintainable by others), EV6 (asset provenance), EV3 (sensitive-content handling).

### LAB-07 — Risk-Tier a Delivery Backlog

- **Target KAs:** [KA-01](../AEBOK/knowledge-areas/KA-01-foundations.md), [KA-04](../AEBOK/knowledge-areas/KA-04-planning-decomposition.md) · **CL:** CL1–CL3 · **Duration:** 2 h
- **Scenario:** A 25-item backlog for a retail platform mixes copy changes, test scaffolding, feature work, a database schema migration, a change to session handling, and a data-deletion batch job. Some items are deliberately ambiguous (an "innocent" copy change that alters legal terms; a "risky-looking" refactor that is actually well-isolated RT1 — Minimal).
- **Tasks:** (1) Assign each item a risk tier (RT1 — Minimal through RT4 — Critical) with a one-line justification. (2) Derive the maximum autonomy level per item. (3) Flag items whose description is insufficient to tier, and write the clarifying question. (4) (CL2+) Decompose one large mixed-risk item into separately tierable work items.
- **Gold-standard solution outline:** Tiering matches the taxonomy exemplars (schema migration and session handling RT3 — Significant; data-deletion job RT4 — Critical — irreversible; scaffolding RT1 — Minimal); the legal-terms copy change caught as RT3 — Significant despite its innocent surface (the classic trap); ambiguity flagged rather than guessed — asking is the correct behavior; decomposition isolates the RT3 — Significant core so the RT1 — Minimal through RT2 — Moderate remainder can run at higher autonomy. CL1 pass requires correct tiering of unambiguous items; CL3 requires trap detection and clean decomposition.
- **Rubric reference:** AESQS classification rubric; heaviest weights EV1 (tiering accuracy), EV6 (justifications), EV2 (nothing left untierable without a flag).

### LAB-08 — Qualify an AI System for RT2 — Moderate Test Authoring

- **Target KAs:** [KA-06](../AEBOK/knowledge-areas/KA-06-testing-quality.md), [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) · **CL:** CL2–CL3 · **Duration:** 3.5 h
- **Scenario:** A team wants to grant a test-authoring agent AL3 — Delegated on RT2 — Moderate test-suite work. Your job is to run a scoped qualification exercise per [AESQS](../AESQS/README.md): design the evaluation, execute it against the provided agent and fixture codebase, and issue a qualification recommendation. (This lab certifies the *human's* ability to run a qualification — the AI system's qualification is the subject matter.)
- **Tasks:** (1) Define the qualification scope: task types in, task types out. (2) Design the evaluation set: representative test-authoring tasks with known-good references, including mutation-detection checks so tautological tests are caught. (3) Execute and score along EV1–EV6. (4) Write the qualification recommendation: granted scope, autonomy ceiling, monitoring conditions, expiry and re-qualification triggers.
- **Gold-standard solution outline:** Scope is task-typed, not blanket ("unit tests for pure business logic in service X", excluding integration and security-relevant tests); evaluation set includes traps (code with subtle bugs — do the generated tests catch them?); scoring separates EV1 (tests assert the requirement) from coverage vanity metrics; recommendation is scoped, versioned, revocable, with drift monitoring per KA-12 and explicit re-qualification triggers (model change, codebase domain shift, evaluation drift). CL3 depth defends the evaluation design's statistical adequacy (sample size, task representativeness).
- **Rubric reference:** AESQS qualification-design rubric; heaviest weights EV1 (evaluation validity), EV6 (evidence chain to recommendation), EV5 (evaluation cost proportionate to the autonomy granted).

### LAB-09 — Instrument Agent Activity for Observability

- **Target KAs:** [KA-09](../AEBOK/knowledge-areas/KA-09-operations-observability.md), [KA-08](../AEBOK/knowledge-areas/KA-08-devops-release.md) · **CL:** CL2–CL3 · **Duration:** 3 h
- **Scenario:** An organization runs several agents (AL2 — Collaborative–AL4 — Autonomous) but can answer none of these questions: What did agents change last week? Which changes were sampled? What is each agent's cost and escalation rate? You receive the (minimal) existing telemetry and the agents' definitions.
- **Tasks:** (1) Define the agent-activity telemetry model: events, attributes, linkage to work items and audit-trail records (ART-15). (2) Specify dashboards/queries answering the stakeholder questions above. (3) Define alerting: which agent behaviors page a human, which are reviewed asynchronously. (4) Show how the telemetry feeds evaluation reports (ART-12) and qualification maintenance.
- **Gold-standard solution outline:** Every agent action attributable (agent identity, autonomy level, work item, inputs, approvals) — the provenance chain is queryable end-to-end; escalation rate, sampling coverage, intervention rate, and cost per outcome are first-class metrics; alerting distinguishes envelope violations (page immediately) from quality drift (async review); the KA-12 loop is closed: telemetry thresholds trigger re-qualification review. CL3 depth prioritizes under a stated telemetry budget and defends what is *not* collected.
- **Rubric reference:** AESQS observability-design rubric; heaviest weights EV2 (all stakeholder questions answerable), EV6 (attribution completeness), EV4 (model evolvable as agents change).

### LAB-10 — AI-Assisted Requirements Elicitation with Preserved Intent

- **Target KAs:** [KA-02](../AEBOK/knowledge-areas/KA-02-business-requirements.md), [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) · **CL:** CL2–CL3 · **Duration:** 3 h
- **Scenario:** You receive raw discovery inputs — stakeholder interview transcripts, a regulator's letter, and support-ticket extracts — plus an AI assistant configured for analysis work. The transcripts contain conflicting stakeholder goals and one requirement the AI assistant, in a seeded draft, has subtly inverted (a consent-by-default vs. consent-by-request inversion with compliance consequences).
- **Tasks:** (1) Use the assistant to draft product requirements (ART-02) from the inputs. (2) Verify every drafted requirement against its source material; correct hallucinated or inverted content. (3) Make the stakeholder conflict explicit and route it to human decision rather than letting the draft paper over it. (4) Record provenance: which requirement came from which source, which were AI-drafted, which human-authored.
- **Gold-standard solution outline:** The seeded inversion is caught by source verification (missing it fails the lab — it is the core point: AI-drafted requirements are verified against intent, not fluency); the goal conflict surfaces as a decision item for the accountable human (ROLE-02/ROLE-03), not silently resolved; every requirement carries source provenance; the final set is complete against the regulator's letter. CL3 depth adds elicitation-gap analysis: what the inputs *don't* answer and the follow-up plan.
- **Rubric reference:** AESQS requirements-quality rubric; heaviest weights EV1 (fidelity to stakeholder intent), EV2 (coverage of sources), EV6 (per-requirement provenance).

---

## 4. Use in Certification

| Credential requirement | Labs |
|------------------------|------|
| Practitioner practical assessment (2 labs) | One from the candidate's role path + LAB-07 or LAB-02 |
| Professional practical assessment (3 labs, incl. one review/oversight lab) | Role-path labs at CL3 depth; LAB-02, LAB-03, or LAB-05 satisfies the review/oversight requirement |
| Endorsement lab | The role-specific lab named in [AIES-AECT-CERT-01 — Certification Framework §3](certification-framework.md#3-role-specialization-endorsements), at CL3 |

Assessment operations — assessor qualifications, environment standardization, and scoring — are defined in [Assessment & Renewal (AIES-AECT-AR-01 — Assessment and Renewal)](assessment-and-renewal.md).

## Related Documents

- [Certification Framework (AIES-AECT-CERT-01 — Certification Framework)](certification-framework.md) — the credential requirements these labs satisfy
- [Assessment & Renewal (AIES-AECT-AR-01 — Assessment and Renewal)](assessment-and-renewal.md) — assessor qualifications, environment standardization, scoring operations
- [Exam Blueprints (AIES-AECT-EB-01 — Exam Blueprints)](exam-blueprints.md) — the knowledge-exam counterpart to these labs
- [Learning Paths (AIES-AECT-LP-01 — Learning Paths)](learning-paths.md) — where each lab appears in preparation
- [AESQS (AIES-AESQS-00 — Qualification Standard)](../AESQS/README.md) — the rubrics and scoring methodology labs are scored with

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

# Competency Framework

| | |
|---|---|
| **Document ID** | AIES-AESQS-CF-01 |
| **Status** | Review |
| **Audience** | Assessors & qualification authorities · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

This document defines **what** is being qualified: the competency areas of AI Engineering, the minimum competency levels required per role, and the behavioral descriptors for each level of the [CL1 — Foundation through CL4 — Expert scale](../Shared/Taxonomy/README.md#6-competency-levels-cl1cl4). It applies to **both human candidates and AI systems**; §5 and §6 define how the same competencies are interpreted for each.

---

## 1. Competency Areas

AESQS competency areas are derived from the AEBOK body of knowledge ([AEBOK](../AEBOK/README.md), AIES-AEBOK-KA-01 … AIES-AEBOK-KA-12), but they are a **distinct partition of it, organized for qualification rather than for knowledge**. AEBOK organizes *what must be known*; the competency areas organize *what is qualified*. The two decompositions legitimately differ — AESQS qualifies Product & Experience Definition (CA-03) separately from Business & Requirements (CA-02) though AEBOK covers both in KA-02, and it names Governance, Risk & AI Safety (CA-12) as one competency though AEBOK carries that knowledge across several KAs and cross-cutting domains. The relationship is therefore a **coverage mapping, not a one-to-one-by-number correspondence** (see [ADR-0003](../adr/ADR-0003-Competency-Area-Knowledge-Mapping.md)): the *Primarily Draws On* column names the KA(s) and domain(s) each competency chiefly rests on.

| ID | Competency Area | Primarily Draws On | Primary Phases / Domains |
|----|-----------------|--------------------|--------------------------|
| CA-01 | AI-Native SDLC Foundations | KA-01 | P01–P16 (orientation) |
| CA-02 | Business & Requirements Analysis with AI | KA-02 | P01, P02, P05 |
| CA-03 | Product & Experience Definition with AI | KA-02 (product/UX scope) | P03, P04 |
| CA-04 | Architecture & Solution Design | KA-03 | P06, P07 |
| CA-05 | AI-Assisted Implementation | KA-04, KA-05 | P08, P09 |
| CA-06 | Testing, Quality & Evaluation Engineering | KA-06, KA-12 | P10, P16 |
| CA-07 | Security & Privacy Engineering | KA-07 | P11, X01, X02 |
| CA-08 | Delivery & Release Engineering | KA-08 | P12, P13 |
| CA-09 | Operations, Observability & Reliability | KA-09 | P14, P15, X13 |
| CA-10 | Human-AI Collaboration & Oversight | KA-11 | X07 (all phases) |
| CA-11 | Context & Knowledge Engineering | KA-10 | X08, X09 |
| CA-12 | Governance, Risk & AI Safety | KA-01, KA-11 | X03, X04, X05, X06 |

Normative rules:

- [AIES-AESQS-CF-01-R01 — Competency Framework, requirement 01] Every qualification MUST identify the competency areas in scope and the CL level demonstrated in each.
- [AIES-AESQS-CF-01-R02 — Competency Framework, requirement 02] The competency areas MUST maintain **coverage** of the AEBOK knowledge base in both directions: every competency area MUST trace to at least one AEBOK knowledge area (its *Primarily Draws On* set), and every AEBOK knowledge area MUST be drawn on by at least one competency area. A change to the competency set, the knowledge areas, or the mapping between them is a breaking change handled per [GOVERNANCE.md](../GOVERNANCE.md) and requires a superseding ADR to [ADR-0003](../adr/ADR-0003-Competency-Area-Knowledge-Mapping.md).
- [AIES-AESQS-CF-01-R03 — Competency Framework, requirement 03] CA-01 (AI-Native SDLC Foundations) and CA-10 (Human-AI Collaboration & Oversight) are **universal competencies**: every qualification, for every role, MUST include them at CL2 or higher. No subject — human or AI — may hold an AIES qualification without demonstrating that it understands the lifecycle it operates in and the oversight model it operates under.

## 2. Role Competency Requirements

The table below defines the **minimum** CL level per competency area required to qualify for each [role](../Shared/Taxonomy/README.md#5-ai-engineering-roles) at its primary scope. "—" means the area is not required for that role (organizations MAY still require it).

| Role | CA-01 | CA-02 | CA-03 | CA-04 | CA-05 | CA-06 | CA-07 | CA-08 | CA-09 | CA-10 | CA-11 | CA-12 |
|------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| ROLE-01 Planner | CL2 | CL2 | CL1 | CL1 | **CL3** | CL1 | — | CL1 | — | CL2 | CL1 | CL1 |
| ROLE-02 Business Analyst | CL2 | **CL3** | CL2 | CL1 | — | — | — | — | — | CL2 | CL1 | CL1 |
| ROLE-03 Product Manager | CL2 | CL2 | **CL3** | CL1 | — | CL1 | — | — | — | CL2 | CL1 | CL1 |
| ROLE-04 UX Designer | CL2 | CL1 | **CL3** | — | — | CL1 | — | — | — | CL2 | CL1 | — |
| ROLE-05 Architect | CL2 | CL1 | CL1 | **CL3** | CL2 | CL1 | CL2 | CL2 | CL2 | CL2 | CL2 | CL2 |
| ROLE-06 Software Engineer | CL2 | — | — | CL2 | **CL3** | CL2 | CL2 | CL2 | CL1 | CL2 | CL2 | CL1 |
| ROLE-07 QA Engineer | CL2 | CL1 | — | CL1 | CL2 | **CL3** | CL1 | CL1 | — | CL2 | CL1 | CL1 |
| ROLE-08 Security Engineer | CL2 | — | — | CL2 | CL2 | CL2 | **CL3** | CL1 | CL1 | CL2 | CL1 | CL2 |
| ROLE-09 DevOps Engineer | CL2 | — | — | CL1 | CL2 | CL1 | CL2 | **CL3** | CL2 | CL2 | CL1 | CL1 |
| ROLE-10 SRE | CL2 | — | — | CL1 | CL1 | CL1 | CL2 | CL2 | **CL3** | CL2 | CL1 | CL1 |
| ROLE-11 Documentation Engineer | CL2 | CL1 | CL1 | CL1 | CL1 | — | — | — | — | CL2 | **CL3** | CL1 |
| ROLE-12 Knowledge Manager | CL2 | CL1 | — | CL1 | CL1 | CL1 | — | — | — | CL2 | **CL3** | CL1 |
| ROLE-13 Human Approver | CL2 | — | — | — | — | CL1 | CL1 | — | — | **CL3** | CL1 | CL2 |
| ROLE-14 Governance Officer | CL2 | CL1 | — | CL1 | — | CL1 | CL2 | — | CL1 | CL2 | CL1 | **CL3** |

The bolded cell in each row marks the role's **core competency area**.

Risk-tier modifiers:

- [AIES-AESQS-CF-01-R04 — Competency Framework, requirement 04] The minimums above apply to qualifications scoped at RT1 — Minimal through RT2 — Moderate. A qualification scoped at RT3 — Significant MUST require the role's core competency area at one CL level above the table minimum (capped at CL4). A qualification scoped at RT4 — Critical MUST require the core competency area at CL3 or higher **and** CA-12 at CL2 or higher.
- [AIES-AESQS-CF-01-R05 — Competency Framework, requirement 05] ROLE-13 (Human Approver) additionally MUST hold CL2 or higher in the competency area covering the phase whose gate they approve (e.g., approving P09 changes requires CA-05 at CL2). ROLE-13 and ROLE-14 MUST be held by humans, per the [Taxonomy](../Shared/Taxonomy/README.md#5-ai-engineering-roles); AI systems MUST NOT be qualified for these roles.

## 3. Competency Level Descriptors

The CL1–CL4 scale is defined in the [Taxonomy §6](../Shared/Taxonomy/README.md#6-competency-levels-cl1cl4). AESQS refines each level with generic descriptors that assessors instantiate per competency area. A subject is at a level only if it satisfies **all** descriptor rows for that level, evidenced per [AIES-AESQS-QP-01 — Qualification Process](qualification-process.md).

| Aspect | CL1 Foundation | CL2 Practitioner | CL3 Professional | CL4 Expert |
|--------|----------------|------------------|------------------|------------|
| **Knowledge** | States the concepts, vocabulary, and standard practices of the area | Explains why practices exist and when they apply | Compares alternative practices and their trade-offs | Extends the practice; contributes to standards and organizational policy |
| **Application** | Applies practices to routine tasks with guidance and templates | Applies practices independently in standard situations to acceptable quality | Adapts practices to novel, ambiguous, or degraded situations | Designs practices for classes of situations; anticipates failure modes at scale |
| **Judgment** | Recognizes when a task exceeds own capability and escalates | Detects common defects and risks in own output before hand-off | Detects subtle defects and risks in **others'** output; coaches and reviews | Sets acceptance criteria and risk posture for an organization |
| **Evidence expectation** | Guided work products; knowledge assessment | Independent work products meeting rubric thresholds ([AIES-AESQS-CS-01 — Capability Scoring](capability-scoring.md)) | Review records, escalation records, and work products under novel conditions | Sustained multi-context evidence plus artifacts of practice-setting (standards, ADRs, calibration anchors) |

- [AIES-AESQS-CF-01-R06 — Competency Framework, requirement 06] Assessors MUST evaluate each in-scope competency area against these descriptors using the [EV1 — Correctness through EV6 — Traceability rubrics](evaluation-rubrics.md); a level MUST NOT be awarded on partial descriptor satisfaction.

### 3.1 Example Instantiation — CA-05 AI-Assisted Implementation

| Level | Human descriptor | AI-system descriptor |
|-------|------------------|----------------------|
| CL1 | Uses AI assistance to produce code changes under supervision; can explain what the generated code does | Produces syntactically valid, compiling changes for well-specified tasks; declares uncertainty rather than fabricating |
| CL2 | Independently directs AI to produce production-grade changes; validates outputs with tests before hand-off | Produces changes that pass the project's quality gates on standard tasks at rubric thresholds; respects the declared autonomy envelope |
| CL3 | Decomposes ambiguous work for AI execution; reviews AI output for subtle defects; recovers from AI failure modes | Handles under-specified tasks by eliciting or inferring constraints correctly; self-detects low-confidence outputs and escalates per its agent definition (ART-14) |
| CL4 | Defines the organization's AI-assisted engineering practice, tooling standards, and review policy | *(not attainable — see [AIES-AESQS-CF-01-R09 — Competency Framework, requirement 09])* |

## 4. Human Competencies

For humans, competencies combine knowledge, skill, and judgment, and explicitly include the **meta-competency of working with AI**:

- directing AI systems (task decomposition, context provision per CA-11, acceptance criteria);
- reviewing AI output critically (calibrated trust — neither rubber-stamping nor blanket rejection);
- retaining accountability: a human qualification never transfers accountability to a tool.

Normative rules:

- [AIES-AESQS-CF-01-R07 — Competency Framework, requirement 07] Human qualifications at CL2 or higher in any competency area MUST include evidence of competent **review of AI-produced work** in that area, not only of personally produced work.
- [AIES-AESQS-CF-01-R08 — Competency Framework, requirement 08] Human assessment MUST distinguish the candidate's capability from the capability of AI tools used: assessment conditions MUST record which autonomy levels of AI assistance were permitted, and at least one assessment component per core competency area MUST demonstrate the candidate's own judgment (e.g., defect-seeded review, scenario assessment per [AIES-AESQS-QP-01 — Qualification Process §4](qualification-process.md)).

## 5. AI-System Capabilities

For AI systems, the same competency areas apply, interpreted as **capabilities**: demonstrable, repeatable production of outcomes at a defined quality. Differences from human assessment:

- **Configuration-bound.** An AI-system qualification attaches to a specific agent definition (ART-14) — model configuration, tools, guardrails, context assets (ART-13) — not to an underlying model family in the abstract. Any material change is a re-qualification trigger per [AIES-AESQS-RR-01 — Revision and Revocation](revision-and-revocation.md).
- **Statistically evidenced.** Capability is demonstrated over evaluation samples and golden-task suites with the sample-size and confidence requirements of [AIES-AESQS-CS-01 — Capability Scoring §6](capability-scoring.md), because single-run performance is not evidence.
- **Escalation-inclusive.** Correctly refusing or escalating a task outside capability is scored as competent behavior (CA-10); confidently producing wrong output is scored as a safety failure (EV3).
- **Autonomy-linked.** The purpose of an AI-system qualification is to justify an autonomy level: the demonstrated CL, combined with the scoped risk tier, bounds the permissible AL per [AIES-AESQS-CS-01 — Capability Scoring §5](capability-scoring.md).

Normative rules:

- [AIES-AESQS-CF-01-R09 — Competency Framework, requirement 09] AI-system qualifications MUST NOT be granted above CL3. CL4 entails setting practice and holding organizational accountability, which AIES reserves to humans (Guiding Principle: Human Governed).
- [AIES-AESQS-CF-01-R10 — Competency Framework, requirement 10] An AI-system qualification MUST identify the exact agent definition version (ART-14) it evaluates, and MUST be treated as void for any materially different configuration.
- [AIES-AESQS-CF-01-R11 — Competency Framework, requirement 11] AI-system capability claims MUST include escalation behavior: an AI system that cannot reliably recognize and signal the limits of its capability MUST NOT be qualified at CL2 or higher in any competency area.

## 6. Shared Scale, Different Evidence

| | Human | AI System |
|---|-------|-----------|
| Scale | CL1–CL4 | CL1–CL3 (R09) |
| Subject identity | Person | Agent definition version (ART-14) |
| Typical evidence | Work products, scenario assessments, live observation, review records | Golden-task suites, sampled production artifacts, telemetry (ART-12), guardrail test results |
| Judgment proxy | Direct assessment of reasoning and decisions | Escalation behavior, calibration, envelope compliance |
| Validity pressure | Skill decay, role change | Model change, context change, score drift |
| Qualification consequence | Role staffing, gate authority | Autonomy level grant (AL0 — Manual through AL4 — Autonomous) |

Both threads flow into the same [qualification process](qualification-process.md), the same [rubrics](evaluation-rubrics.md), and the same [scoring system](capability-scoring.md).

---

## Related Documents

- [AIES-AESQS-00 — AESQS — AI Engineering SDLC Qualification Standard](README.md)
- [AIES-AESQS-QP-01 — Qualification Process](qualification-process.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](evaluation-rubrics.md)
- [AIES-AESQS-CS-01 — Capability Scoring](capability-scoring.md)
- [AIES-AESQS-RR-01 — Revision & Revocation](revision-and-revocation.md)
- [AIES-AEBOK-00 — AEBOK — AI Engineering Body of Knowledge](../AEBOK/README.md) (knowledge areas the competency areas derive from)
- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) · [Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

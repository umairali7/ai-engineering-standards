# Taxonomy

| | |
|---|---|
| **Document ID** | AIES-SHARED-02 |
| **Status** | Review |
| **Audience** | All readers |

The canonical classification systems of AIES. Every module MUST use these taxonomies as defined here and MUST NOT introduce competing scales.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. SDLC Phases (P01–P16)

The AIES lifecycle model. Phases are logical, not strictly sequential — iterative and incremental delivery maps onto them repeatedly.

| ID | Phase | Primary Concern |
|----|-------|-----------------|
| P01 | Business Strategy | Why the organization invests |
| P02 | Business Analysis | What problem is being solved |
| P03 | Product Management | What to build, in what order |
| P04 | User Experience | How humans will use it |
| P05 | Requirements Engineering | What the system must do |
| P06 | Solution Analysis | How candidate solutions compare |
| P07 | Architecture | How the system is structured |
| P08 | Planning | How work is decomposed and sequenced |
| P09 | Engineering | How the system is built |
| P10 | Testing & Quality | How correctness is demonstrated |
| P11 | Security | How the system resists abuse |
| P12 | DevOps | How change flows to production |
| P13 | Release | How value reaches users |
| P14 | Operations | How the system is run |
| P15 | Observability | How behavior is understood |
| P16 | Continuous Improvement | How the system and process evolve |

Detailed phase guidance lives in [docs/SDLC.md](../../docs/SDLC.md); per-phase knowledge lives in [AEBOK](../../AEBOK/README.md).

## 2. Cross-Cutting Domains (X01–X15)

Domains that apply to every phase.

| ID | Domain | ID | Domain | ID | Domain |
|----|--------|----|--------|----|--------|
| X01 | Security | X06 | AI Safety | X11 | Performance |
| X02 | Privacy | X07 | Human Oversight | X12 | Scalability |
| X03 | Compliance | X08 | Documentation | X13 | Reliability |
| X04 | Governance | X09 | Knowledge Management | X14 | Accessibility |
| X05 | Risk Management | X10 | Cost Optimization | X15 | Sustainability |

## 3. Autonomy Levels (AL0–AL4)

How much independent authority an AI system holds for a given task. Autonomy is assigned **per task type, per risk tier** — never globally to a whole system.

| Level | Name | Description | Human Role |
|-------|------|-------------|------------|
| **AL0** | Manual | Human performs the task; AI is not involved | Performer |
| **AL1** | Assisted | AI suggests; human authors and decides | Author |
| **AL2** | Collaborative | AI produces drafts/changes; human reviews every output before it takes effect | Reviewer (per item) |
| **AL3** | Delegated | AI executes within a defined envelope; human approves at checkpoints and by sampling | Supervisor (per checkpoint) |
| **AL4** | Autonomous | AI executes end-to-end within hard guardrails; human sets policy and audits outcomes | Auditor (per policy) |

Normative rules:

- [AIES-SHARED-02-R01] Every AI-performed task MUST have a declared autonomy level.
- [AIES-SHARED-02-R02] The maximum permissible autonomy level MUST be derived from the task's risk tier (see §4).
- [AIES-SHARED-02-R03] Autonomy level increases MUST be evidence-driven (qualification data per [AESQS](../../AESQS/README.md)) and reversible.

## 4. Risk Tiers (RT1–RT4)

Classifies the blast radius of a task or change.

| Tier | Name | Examples | Max Autonomy (default) |
|------|------|----------|------------------------|
| **RT1** | Minimal | Formatting, doc typos, test scaffolding, internal prototypes | AL4 |
| **RT2** | Moderate | Feature code behind review, test suites, internal tooling | AL3 |
| **RT3** | Significant | Production configuration, schema changes, auth-adjacent code, customer-facing behavior | AL2 |
| **RT4** | Critical | Safety-critical systems, financial transactions, regulated data, irreversible actions | AL1 |

Organizations MAY tighten these defaults; they MUST NOT loosen them without a documented risk acceptance per [AEOS governance](../../AEOS/README.md).

## 5. AI Engineering Roles

The role model used by [AEOS](../../AEOS/README.md). Each role can be staffed by a human, an AI agent, or a human-AI pair — the responsibilities are constant.

| ID | Role | Primary Phases |
|----|------|----------------|
| ROLE-01 | Planner | P08 |
| ROLE-02 | Business Analyst | P02, P05 |
| ROLE-03 | Product Manager | P03 |
| ROLE-04 | UX Designer | P04 |
| ROLE-05 | Architect | P06, P07 |
| ROLE-06 | Software Engineer | P09 |
| ROLE-07 | QA Engineer | P10 |
| ROLE-08 | Security Engineer | P11 (X01) |
| ROLE-09 | DevOps Engineer | P12, P13 |
| ROLE-10 | SRE | P14, P15 |
| ROLE-11 | Documentation Engineer | X08 |
| ROLE-12 | Knowledge Manager | X09 |
| ROLE-13 | Human Approver | X07 (all gates) |
| ROLE-14 | Governance Officer | X04, X05 |

ROLE-13 (Human Approver) and ROLE-14 (Governance Officer) MUST be staffed by humans.

## 6. Competency Levels (CL1–CL4)

The proficiency scale used by [AESQS](../../AESQS/README.md) and [AECT](../../AECT/README.md). Applies to humans and to AI-system qualifications alike.

| Level | Name | Capability Statement |
|-------|------|----------------------|
| **CL1** | Foundation | Understands concepts and vocabulary; applies practices with guidance |
| **CL2** | Practitioner | Applies practices independently in standard situations |
| **CL3** | Professional | Adapts practices to novel situations; reviews and coaches others |
| **CL4** | Expert | Sets practice; evaluates trade-offs at organizational scale; advances the discipline |

## 7. Artifact Types

Canonical names for engineering artifacts referenced across modules.

| ID | Artifact | Produced In |
|----|----------|-------------|
| ART-01 | Business Case | P01–P02 |
| ART-02 | Product Requirement | P03, P05 |
| ART-03 | UX Specification | P04 |
| ART-04 | Architecture Decision Record (ADR) | P06–P07 |
| ART-05 | Work Item / Plan | P08 |
| ART-06 | Source Change (commit / PR) | P09 |
| ART-07 | Test Suite & Test Report | P10 |
| ART-08 | Security Assessment | P11 |
| ART-09 | Pipeline Definition | P12 |
| ART-10 | Release Record | P13 |
| ART-11 | Runbook | P14 |
| ART-12 | Telemetry & Evaluation Report | P15–P16 |
| ART-13 | Prompt / Context Asset | X09 |
| ART-14 | Agent Definition | X04 |
| ART-15 | Audit Trail Record | X04, X07 |

## 8. Evaluation Dimensions (EV1–EV6)

The dimensions along which AESQS scores capability (human or AI):

| ID | Dimension | Question |
|----|-----------|----------|
| EV1 | Correctness | Does the output meet requirements? |
| EV2 | Completeness | Is anything material missing? |
| EV3 | Safety & Security | Does it introduce risk? |
| EV4 | Maintainability | Can others evolve it? |
| EV5 | Efficiency | Is the cost (time, compute, tokens) proportionate? |
| EV6 | Traceability | Can every decision be explained and audited? |

---

## Change Control

Any change to this taxonomy is a breaking change for all modules and MUST go through an ADR per [GOVERNANCE.md](../../GOVERNANCE.md).

## Related Documents

- [Glossary (AIES-SHARED-01)](../Glossary/README.md) — canonical term definitions
- [Shared Standards index (AIES-SHARED-00)](../README.md)
- [SDLC Reference (AIES-DOC-04)](../../docs/SDLC.md) — detailed guidance for phases P01–P16
- [Metadata Standard (AIES-STD-02)](../../docs/standards/metadata-standard.md) — the identifier scheme built on these codes
- [Standards Crosswalk (AIES-DOC-07)](../../docs/CROSSWALK.md) — how the autonomy levels and risk tiers here map to CSA, ASDLC, the EU AI Act, ISO/IEC 42001, and NIST AI RMF

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

# Learning Paths

| | |
|---|---|
| **Document ID** | AIES-AECT-LP-01 |
| **Status** | Review |
| **Audience** | Educators & training providers · Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

This document defines the structured curricula that take a learner from first contact with AIES to certification readiness. Every path is assembled from [AEBOK Knowledge Areas (KA-01 … KA-12)](../AEBOK/README.md) — AEBOK is the sole syllabus source — supplemented by practical [labs (AIES-AECT-LAB-01 — Labs)](labs.md) and shared standards material.

[AIES-AECT-LP-01-R01 — Learning Paths, requirement 01] Every learning-path module MUST map to one or more AEBOK Knowledge Areas or to the Shared Standards (Glossary, Taxonomy); paths MUST NOT introduce knowledge content of their own.

[AIES-AECT-LP-01-R02 — Learning Paths, requirement 02] Every learning path MUST declare its target audience, prerequisite, module sequence, estimated effort, exit competency level (CL1–CL4), and the certification it prepares for.

Effort estimates are stated in **study hours** (guided reading, exercises, and labs) and assume a working software professional; they are planning aids, not requirements. Training providers MAY repackage paths but MUST preserve the KA coverage and exit competency claims.

## 2. Path Map

```
                       ┌───────────────────────────┐
                       │  LP-F  Foundation Path    │──► Associate (CL1)
                       └─────────────┬─────────────┘
        ┌──────────┬──────────┬──────┼──────┬───────────┬───────────┐
        ▼          ▼          ▼      ▼      ▼           ▼           ▼
      LP-ENG     LP-ARC     LP-QA  LP-SEC  LP-OPS    LP-PBA      LP-LEAD
     Engineer  Architect     QA   Security DevOps/  Product/   Engineering
                                            SRE     BA         Leadership
        │          │          │      │      │           │           │
        ▼          ▼          ▼      ▼      ▼           ▼           ▼
   Practitioner (CL2) ──continue──► Professional (CL3) [+ endorsement]
```

| Path | Name | Primary Roles | Exit CL | Prepares for |
|------|------|---------------|---------|--------------|
| LP-F | Foundation | All | CL1 | AIES Certified Associate |
| LP-ENG | AI-Native Software Engineer | ROLE-06 | CL2→CL3 | Practitioner; Professional – Software Engineering |
| LP-ARC | AI-Native Architect | ROLE-05 | CL2→CL3 | Practitioner; Professional – Architecture |
| LP-QA | AI-Native Quality Engineer | ROLE-07 | CL2→CL3 | Practitioner; Professional – Quality Engineering |
| LP-SEC | AI-Native Security Engineer | ROLE-08 | CL2→CL3 | Practitioner; Professional – Security Engineering |
| LP-OPS | AI-Native DevOps / SRE | ROLE-09, ROLE-10 | CL2→CL3 | Practitioner; Professional – DevOps & Release / Site Reliability |
| LP-PBA | AI-Native Product & Business Analysis | ROLE-02, ROLE-03 | CL2→CL3 | Practitioner; Professional – Business Analysis & Product |
| LP-LEAD | AI Engineering Leadership | ROLE-13, ROLE-14, leaders | CL3→CL4 | Professional – Oversight & Governance; Fellow |

## 3. LP-F — Foundation Path

- **Target audience:** anyone entering AI-native engineering — engineers, analysts, testers, managers. No AI-specific experience assumed; basic software delivery literacy is.
- **Prerequisite:** none.
- **Exit competency:** CL1 across the foundation scope.
- **Prepares for:** AIES Certified Associate exam.
- **Estimated effort:** 24–32 study hours.

| # | Module | Source | Hours |
|---|--------|--------|-------|
| F1 | AIES orientation: modules, principles, document conventions | [README](../README.md), [Shared](../Shared/README.md) | 2 |
| F2 | Canonical vocabulary | [Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md) | 3 |
| F3 | The taxonomy: phases P01–P16, domains X01–X15, autonomy AL0 — Manual through AL4 — Autonomous, risk RT1 — Minimal through RT4 — Critical, roles, CL levels, EV dimensions | [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) | 6 |
| F4 | Foundations of AI-native engineering: economics, risk, the autonomy/risk model in practice | [AEBOK KA-01](../AEBOK/knowledge-areas/KA-01-foundations.md) | 8 |
| F5 | A tour of the lifecycle KAs: what changes in each phase when AI participates | [AEBOK KA-02 … KA-09](../AEBOK/README.md#3-knowledge-area-map) (survey depth) | 6 |
| F6 | Working under oversight: gates, review, accountability | [AEBOK KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) (survey depth) | 4 |
| F7 | Foundation lab | [LAB-07 (Risk-tier a backlog)](labs.md#lab-07--risk-tier-a-delivery-backlog) at CL1 depth | 3 |

## 4. Role-Based Paths (CL2 → CL3)

Each role path has a common shape: a **Practitioner segment** (deep study of the role's primary KAs + supporting KAs + two labs) and a **Professional segment** (novel-situation practice, review/coaching skills, portfolio building). All role paths require LP-F (or the Associate credential, or the [experience waiver](certification-framework.md#23-experience-waiver)) as prerequisite. KA sequences align with the [AEBOK reading guidance](../AEBOK/README.md#6-reading-guidance-by-audience).

### 4.1 LP-ENG — AI-Native Software Engineer

- **Target audience:** software engineers writing and shipping code with AI participation (ROLE-06).
- **Prerequisite:** LP-F; 1+ year professional engineering experience.
- **Estimated effort:** Practitioner segment 40–50 h; Professional segment 40–50 h.

| Segment | Module sequence | Labs |
|---------|-----------------|------|
| Practitioner (CL2) | [KA-05](../AEBOK/knowledge-areas/KA-05-implementation.md) → [KA-06](../AEBOK/knowledge-areas/KA-06-testing-quality.md) → [KA-10](../AEBOK/knowledge-areas/KA-10-context-knowledge.md) → [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) | LAB-02, LAB-06 |
| Professional (CL3) | [KA-03](../AEBOK/knowledge-areas/KA-03-architecture-design.md) → [KA-07](../AEBOK/knowledge-areas/KA-07-security.md) → [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) + [pattern catalog](../AEBOK/patterns/README.md) | LAB-01, LAB-02 at CL3 depth |

- **Exit competency / certification:** CL2 → AIES Certified Practitioner; CL3 → Professional with *Software Engineering* endorsement.

### 4.2 LP-ARC — AI-Native Architect

- **Target audience:** solution and software architects designing systems that AI agents analyze, extend, and operate on (ROLE-05).
- **Prerequisite:** LP-F; 2+ years design experience.
- **Estimated effort:** 45–55 h per segment.

| Segment | Module sequence | Labs |
|---------|-----------------|------|
| Practitioner (CL2) | [KA-03](../AEBOK/knowledge-areas/KA-03-architecture-design.md) → [KA-07](../AEBOK/knowledge-areas/KA-07-security.md) → [KA-10](../AEBOK/knowledge-areas/KA-10-context-knowledge.md) | LAB-04, LAB-06 |
| Professional (CL3) | [KA-04](../AEBOK/knowledge-areas/KA-04-planning-decomposition.md) → [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) → [AEAR](../AEAR/README.md) reference architectures | LAB-01, LAB-04 at CL3 depth |

- **Exit competency / certification:** CL2 → Practitioner; CL3 → Professional with *Architecture* endorsement.

### 4.3 LP-QA — AI-Native Quality Engineer

- **Target audience:** QA and test engineers verifying AI-produced work and AI-assisted testing (ROLE-07).
- **Prerequisite:** LP-F; testing fundamentals (e.g., ISTQB Foundation or equivalent experience).
- **Estimated effort:** 40–50 h per segment.

| Segment | Module sequence | Labs |
|---------|-----------------|------|
| Practitioner (CL2) | [KA-06](../AEBOK/knowledge-areas/KA-06-testing-quality.md) → [KA-05](../AEBOK/knowledge-areas/KA-05-implementation.md) → [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) | LAB-02, LAB-08 |
| Professional (CL3) | [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) → [KA-08](../AEBOK/knowledge-areas/KA-08-devops-release.md) → evaluation of non-deterministic components (KA-06 advanced) | LAB-08, LAB-05 |

- **Exit competency / certification:** CL2 → Practitioner; CL3 → Professional with *Quality Engineering* endorsement.

### 4.4 LP-SEC — AI-Native Security Engineer

- **Target audience:** security engineers addressing threats specific to AI-native delivery (ROLE-08).
- **Prerequisite:** LP-F; application security fundamentals.
- **Estimated effort:** 45–55 h per segment.

| Segment | Module sequence | Labs |
|---------|-----------------|------|
| Practitioner (CL2) | [KA-07](../AEBOK/knowledge-areas/KA-07-security.md) → [KA-08](../AEBOK/knowledge-areas/KA-08-devops-release.md) → [KA-09](../AEBOK/knowledge-areas/KA-09-operations-observability.md) | LAB-01, LAB-03 |
| Professional (CL3) | [KA-05](../AEBOK/knowledge-areas/KA-05-implementation.md) (review focus) → [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) → [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) | LAB-05, LAB-01 at CL3 depth |

- **Exit competency / certification:** CL2 → Practitioner; CL3 → Professional with *Security Engineering* endorsement.

### 4.5 LP-OPS — AI-Native DevOps / SRE

- **Target audience:** DevOps engineers and SREs building gated pipelines and operating AI-inclusive systems (ROLE-09, ROLE-10).
- **Prerequisite:** LP-F; CI/CD and operations fundamentals.
- **Estimated effort:** 40–50 h per segment.

| Segment | Module sequence | Labs |
|---------|-----------------|------|
| Practitioner (CL2) | [KA-08](../AEBOK/knowledge-areas/KA-08-devops-release.md) → [KA-09](../AEBOK/knowledge-areas/KA-09-operations-observability.md) → [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) | LAB-03, LAB-05 |
| Professional (CL3) | [KA-06](../AEBOK/knowledge-areas/KA-06-testing-quality.md) → [KA-07](../AEBOK/knowledge-areas/KA-07-security.md) → [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) | LAB-09, LAB-05 at CL3 depth |

- **Exit competency / certification:** CL2 → Practitioner; CL3 → Professional with *DevOps & Release* or *Site Reliability* endorsement.

### 4.6 LP-PBA — AI-Native Product & Business Analysis

- **Target audience:** business analysts, product managers, and requirements engineers using AI in upstream phases while preserving human intent (ROLE-02, ROLE-03).
- **Prerequisite:** LP-F; business analysis or product management experience.
- **Estimated effort:** 35–45 h per segment.

| Segment | Module sequence | Labs |
|---------|-----------------|------|
| Practitioner (CL2) | [KA-02](../AEBOK/knowledge-areas/KA-02-business-requirements.md) → [KA-04](../AEBOK/knowledge-areas/KA-04-planning-decomposition.md) → [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) | LAB-07, LAB-10 |
| Professional (CL3) | [KA-10](../AEBOK/knowledge-areas/KA-10-context-knowledge.md) → [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) → [KA-01](../AEBOK/knowledge-areas/KA-01-foundations.md) (economics deep dive) | LAB-07 at CL3 depth, LAB-06 |

- **Exit competency / certification:** CL2 → Practitioner; CL3 → Professional with *Business Analysis & Product* endorsement.

### 4.7 LP-LEAD — AI Engineering Leadership

- **Target audience:** engineering leaders, governance officers, and gate owners accountable for AI-native delivery at team-of-teams scale (ROLE-13, ROLE-14, engineering directors).
- **Prerequisite:** AIES Certified Professional (any endorsement) or 5+ years engineering leadership with LP-F completed.
- **Exit competency:** CL3 in oversight/governance scope, building toward CL4.
- **Prepares for:** Professional with *Oversight & Governance* endorsement; the Fellow portfolio and contribution track.
- **Estimated effort:** 50–60 study hours plus portfolio work.

| # | Module | Source | Focus |
|---|--------|--------|-------|
| L1 | Oversight architecture: gates, sampling, accountability, skill preservation | [KA-11](../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) | Deep |
| L2 | Measuring outcomes and detecting capability drift | [KA-12](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) | Deep |
| L3 | The operating model: roles, workflows, governance | [AEOS](../AEOS/README.md) | Deep |
| L4 | Qualification as a management instrument | [AESQS](../AESQS/README.md) | Working knowledge |
| L5 | Portfolio-scale risk and autonomy policy | [KA-01](../AEBOK/knowledge-areas/KA-01-foundations.md), [Taxonomy §3–4](../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4) | Deep |
| L6 | Labs | LAB-03, LAB-05, LAB-10 at CL3 depth | Assessed |
| L7 | Fellow preparation: portfolio assembly, contribution planning, panel expectations | [AIES-AECT-CERT-01 — Certification Framework §2.4–2.5](certification-framework.md#24-portfolio-professional-and-fellow) | Guided |

## 5. Choosing a Path

| If you are… | Start with | Then |
|-------------|-----------|------|
| New to AI-native work, any role | LP-F | The role path matching your day job |
| An experienced engineer skipping Associate (waiver) | LP-F modules F3–F4 as self-check | LP-ENG Practitioner segment |
| Holding one Professional endorsement, wanting another | The new endorsement's deep-dive KAs ([AIES-AECT-CERT-01 — Certification Framework §3](certification-framework.md#3-role-specialization-endorsements)) | Endorsement exam section + role lab |
| A leader accountable for gates and governance | LP-F (if new) | LP-LEAD |

## Related Documents

- [Certification Framework (AIES-AECT-CERT-01 — Certification Framework)](certification-framework.md) — the credentials these paths prepare for
- [Exam Blueprints (AIES-AECT-EB-01 — Exam Blueprints)](exam-blueprints.md) — how path content is examined
- [Labs (AIES-AECT-LAB-01 — Labs)](labs.md) — the practical labs referenced above
- [AEBOK (AIES-AEBOK-00 — Engineering Body of Knowledge)](../AEBOK/README.md) — the knowledge itself

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

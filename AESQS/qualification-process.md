# Qualification Process

| | |
|---|---|
| **Document ID** | AIES-AESQS-QP-01 |
| **Status** | Review |
| **Audience** | Assessors & qualification authorities · Governance officers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

This document defines the end-to-end process by which a **human or AI system** obtains, holds, and renews an AESQS qualification. It consumes the [Competency Framework (AIES-AESQS-CF-01 — Competency Framework)](competency-framework.md), the [Evaluation Rubrics (AIES-AESQS-ER-01 — Evaluation Rubrics)](evaluation-rubrics.md), the [Capability Scoring system (AIES-AESQS-CS-01 — Capability Scoring)](capability-scoring.md), and the [Peer Review standard (AIES-AESQS-PR-01 — Peer Review)](peer-review.md).

---

## 1. Process Overview

```
Lane: Candidate/Sponsor   Lane: Assessor           Lane: Peer Reviewer     Lane: Qualification Authority
──────────────────────    ─────────────────────    ────────────────────    ─────────────────────────────
1. Request                
   qualification ───────► 2. Scope check:
   (role × phases            role × phases × RT,
    × risk tier)             competency areas,
                             assessment plan
                          3. Evidence intake ◄──── (candidate submits
                             & completeness         evidence portfolio)
                             check
                          4. Assessment:
                             - work-product review
                             - scenario assessment
                             - golden-task suites (AI)
                             - live observation
                          5. Rubric scoring
                             (EV1–EV6) ───────────► 6. Independent peer
                                                       review of evidence,
                                                       scores, decision
                                                       recommendation
                                                          │
                                                          ▼
                                                    7. Consolidated ──────► 8. Decision:
                                                       recommendation          grant / conditions /
                                                                               deny; set validity;
                                                                               set AL cap (AI)
                          ◄────────────────────────────────────────────────  9. Record in registry;
   10. Qualification                                                            audit trail (ART-15)
       active; subject                                                          │
       to ongoing         ◄───────────────────────────────────────────────── 11. Ongoing verification:
       verification                                                              drift monitoring,
       and re-qualification                                                      sampling, incident
       triggers                                                                  feeds (AIES-AESQS-CS-01 §7,
                                                                                 AIES-AESQS-RR-01)
```

Roles in this process:

| Process role | Staffing | Notes |
|--------------|----------|-------|
| Candidate | Human, or AI system represented by its **sponsor** (the accountable owner of the agent definition, ART-14) | AI systems never self-sponsor |
| Assessor | Human qualified per [AIES-AESQS-PR-01 — Peer Review §2](peer-review.md); MAY use qualified AI evaluation tooling under AL2 — Collaborative or lower | Accountable for evidence integrity |
| Peer Reviewer | Independent human per [AIES-AESQS-PR-01 — Peer Review](peer-review.md) | Mandatory for all grants |
| Qualification Authority | Organizational function (typically ROLE-14 with delegated assessors) | Owns decisions, registry, appeals |

- [AIES-AESQS-QP-01-R01 — Qualification Process, requirement 01] Every qualification decision MUST involve at least two distinct humans: an assessor and an independent peer reviewer. Neither MAY be replaced by an AI system.

## 2. Scoping a Qualification

A qualification is a tuple:

```
Q = (subject, role, phases, max risk tier, competency areas × CL,
     framework version, [agent definition version], validity window)
```

- [AIES-AESQS-QP-01-R02 — Qualification Process, requirement 02] Every qualification MUST declare: the subject (person, or agent definition ART-14 version); the [role](../Shared/Taxonomy/README.md#5-ai-engineering-roles); the [SDLC phases](../Shared/Taxonomy/README.md#1-sdlc-phases-p01p16) in scope; the maximum [risk tier](../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4); the competency areas and CL levels claimed; and the version of [AIES-AESQS-CF-01 — Competency Framework](competency-framework.md) applied.
- [AIES-AESQS-QP-01-R03 — Qualification Process, requirement 03] Scope MUST NOT exceed the role's primary phases plus explicitly justified adjacent phases. "Blanket" qualifications spanning all phases MUST NOT be issued.
- [AIES-AESQS-QP-01-R04 — Qualification Process, requirement 04] For AI systems, the qualification MUST additionally declare the maximum autonomy level it supports per task type, derived per [AIES-AESQS-CS-01 — Capability Scoring §5](capability-scoring.md), and MUST NOT exceed the risk tier's default AL cap in the [Taxonomy §4](../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4).

Scoping examples:

| Subject | Scope | Reading |
|---------|-------|---------|
| Human engineer | ROLE-06 × P09 × RT3 — Significant | May act as Software Engineer on significant-risk engineering work |
| AI agent v2.4.1 | ROLE-07 × P10 × RT2 — Moderate, AL3 — Delegated | May execute delegated test-engineering tasks up to moderate risk |
| Human lead | ROLE-13 × P09 gate × RT4 — Critical | May approve critical engineering changes |

## 3. Evidence Requirements

- [AIES-AESQS-QP-01-R05 — Qualification Process, requirement 05] All evidence MUST be attributable (provenance recorded), current (within the evidence window below), and verifiable by the peer reviewer. Vendor benchmark claims and marketing material MUST NOT be admitted as evidence for AI systems.
- [AIES-AESQS-QP-01-R06 — Qualification Process, requirement 06] Evidence volume MUST meet the minimum sample sizes of [AIES-AESQS-CS-01 — Capability Scoring §6](capability-scoring.md) for the scoped risk tier.

| Requirement | RT1 — Minimal | RT2 — Moderate | RT3 — Significant | RT4 — Critical |
|-------------|-----|-----|-----|-----|
| Evidence window (max age) | 24 months | 18 months | 12 months | 6 months |
| Work products in evaluated conditions | Optional | Required | Required | Required |
| Scenario-based assessment | Optional | Recommended | Required | Required |
| Golden-task suite (AI systems) | Required | Required | Required (incl. adversarial cases) | Required (incl. adversarial + failure-injection cases) |
| Live observation | Optional | Optional | Recommended | Required |
| Independent reproduction of AI evidence ([AIES-AESQS-PR-01 — Peer Review §6](peer-review.md)) | Sampled | Sampled | Required | Required |

## 4. Assessment Methods

### 4.1 Work-Product Review

Assessors score real artifacts (ART-01 … ART-14 as applicable to the scoped phases) produced by the candidate against the [EV1 — Correctness through EV6 — Traceability rubrics](evaluation-rubrics.md).

- [AIES-AESQS-QP-01-R07 — Qualification Process, requirement 07] Work products MUST be sampled by the assessor from a pre-registered population (e.g., all merged source changes in a period), not hand-picked by the candidate or sponsor.

### 4.2 Scenario-Based Assessment

Standardized, controlled tasks with known correct behaviors — including deliberately ambiguous, defect-seeded, or out-of-envelope scenarios that test judgment and escalation (CA-10). Used for humans and AI systems alike.

- [AIES-AESQS-QP-01-R08 — Qualification Process, requirement 08] Scenario sets for RT3 — Significant through RT4 — Critical scopes MUST include at least one scenario whose correct outcome is to **refuse or escalate** rather than complete the task.

### 4.3 Golden-Task Suites (AI Systems)

A golden-task suite is a versioned, held-out set of tasks with reference outcomes and scoring rules, executed repeatedly against the exact agent definition under qualification.

- [AIES-AESQS-QP-01-R09 — Qualification Process, requirement 09] Golden-task suites MUST be version-controlled, held out from the AI system's context assets (ART-13) and any tuning data available to the sponsor, and refreshed on a defined schedule to limit contamination.
- [AIES-AESQS-QP-01-R10 — Qualification Process, requirement 10] Golden-task runs MUST record full provenance — agent definition version, configuration, inputs, outputs, and scores — as audit trail records (ART-15), sufficient for independent re-execution.

### 4.4 Live Observation

A qualified assessor observes the candidate performing real or realistic work in session — for humans, directing and reviewing AI; for AI systems, supervised operation at the target autonomy level with the assessor holding override authority.

- [AIES-AESQS-QP-01-R11 — Qualification Process, requirement 11] Live observation of an AI system at a target autonomy level MUST occur at one level **below** the target (e.g., observe at AL2 — Collaborative before granting AL3 — Delegated) or within a sandboxed environment providing equivalent containment.

## 5. Decision Criteria

- [AIES-AESQS-QP-01-R12 — Qualification Process, requirement 12] A qualification MUST be granted only if: (a) every in-scope competency area meets its minimum CL per [AIES-AESQS-CF-01 — Competency Framework §2](competency-framework.md); (b) aggregate and per-dimension scores satisfy [AIES-AESQS-CS-01 — Capability Scoring](capability-scoring.md), including all minimum gates; (c) evidence meets §3; and (d) peer review concludes with a concurring recommendation per [AIES-AESQS-PR-01 — Peer Review](peer-review.md).
- [AIES-AESQS-QP-01-R13 — Qualification Process, requirement 13] Decisions MUST be one of: **Grant**, **Grant with conditions** (narrowed scope, lowered risk tier or AL cap, or mandated monitoring), or **Deny** (with recorded rationale and re-application guidance). Partial competence MUST result in narrowed scope, never in relaxed thresholds.

## 6. Granting and Registration

- [AIES-AESQS-QP-01-R14 — Qualification Process, requirement 14] Granted qualifications MUST be recorded in an organizational qualification registry capturing the full tuple of §2, the evidence references, scores, reviewer identities, decision, conditions, validity window, and status — queryable by the systems that enforce gates and autonomy (see [AEOS](../AEOS/README.md)).
- [AIES-AESQS-QP-01-R15 — Qualification Process, requirement 15] Every lifecycle event (grant, condition change, renewal, suspension, revocation) MUST generate an immutable audit trail record (ART-15).

## 7. Validity and Re-Qualification

Default validity periods (organizations MAY shorten, MUST NOT lengthen):

| Subject | RT1 — Minimal | RT2 — Moderate | RT3 — Significant | RT4 — Critical |
|---------|-----|-----|-----|-----|
| Human | 36 months | 24 months | 24 months | 12 months |
| AI system | 12 months | 12 months | 6 months | 6 months |

AI-system validity is additionally bounded by configuration identity: validity ends **immediately** upon a material change, regardless of the calendar window.

- [AIES-AESQS-QP-01-R16 — Qualification Process, requirement 16] A qualification MUST be re-evaluated before its validity window expires; an expired qualification MUST be treated as absent by all consuming systems.
- [AIES-AESQS-QP-01-R17 — Qualification Process, requirement 17] Re-qualification MUST be triggered before expiry by any of the following (detailed criteria in [AIES-AESQS-RR-01 — Revision and Revocation](revision-and-revocation.md)):
  - **Model change** — any change to the underlying model(s), model version, or inference configuration of a qualified AI system;
  - **Context change** — material change to the agent definition (ART-14), tools, guardrails, or context assets (ART-13); or, for humans, a material change of role or domain;
  - **Sustained score drift** — ongoing-verification scores breaching the drift thresholds of [AIES-AESQS-CS-01 — Capability Scoring §7](capability-scoring.md);
  - **Incident** — a qualifying incident within the subject's scope, per [AIES-AESQS-RR-01 — Revision and Revocation §2](revision-and-revocation.md);
  - **Audit finding** — an internal or external audit questioning the evidence, scoring, or review behind the grant;
  - **Framework revision** — a new version of [AIES-AESQS-CF-01 — Competency Framework](competency-framework.md) or the [Shared Taxonomy](../Shared/Taxonomy/README.md) affecting the scope.
- [AIES-AESQS-QP-01-R18 — Qualification Process, requirement 18] Renewal for an unchanged scope MAY use a reduced evidence set (most recent evidence window plus ongoing-verification data) but MUST still pass peer review; renewal MUST NOT be automatic.

## 8. Fast Path for Low-Risk Scopes

For RT1 — Minimal-only scopes, organizations MAY operate a lightweight variant: assessor and peer reviewer MAY be the same two people across many candidates, scenario assessment MAY be waived, and decisions MAY be batched. All other requirements — scoping, minimum gates, registry, audit trail, revocability — apply unchanged.

---

## Related Documents

- [AIES-AESQS-00 — AESQS — AI Engineering SDLC Qualification Standard](README.md)
- [AIES-AESQS-CF-01 — Competency Framework](competency-framework.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](evaluation-rubrics.md)
- [AIES-AESQS-CS-01 — Capability Scoring](capability-scoring.md)
- [AIES-AESQS-PR-01 — Peer Review Standard](peer-review.md)
- [AIES-AESQS-RR-01 — Revision & Revocation](revision-and-revocation.md)
- [AIES-AEOS-00 — AEOS — AI Engineering Operating System](../AEOS/README.md) (consumes qualifications for gating and autonomy)
- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) · [Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

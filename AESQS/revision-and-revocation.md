# Revision & Revocation

| | |
|---|---|
| **Document ID** | AIES-AESQS-RR-01 |
| **Status** | Review |
| **Audience** | Assessors & qualification authorities · Governance officers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

A qualification that cannot be revised or revoked is a liability, not a control. This document defines how AESQS qualifications — human and AI-system alike — are kept truthful after grant: the triggers that force revision, the criteria and process for suspension and revocation, the appeals mechanism, and the audit trail (ART-15) that makes the whole lifecycle defensible.

---

## 1. Qualification Status Model

```
              ┌──────────── renewal / re-qualification ────────────┐
              ▼                                                    │
 Granted ──► ACTIVE ──trigger (§2)──► UNDER REVIEW ──► ACTIVE (reaffirmed,
              │                            │                possibly with
              │ severe trigger (§3)        │                conditions)
              ▼                            ▼
          SUSPENDED ─────────────────► REVOKED ──► (re-application only via
              │        confirmed           ▲        full AIES-AESQS-QP-01 process)
              └── restored (peer review) ──┘
                                         EXPIRED (validity lapse) — treated
                                         as absent by consuming systems
```

- [AIES-AESQS-RR-01-R01] Consuming systems (gates, agent registries, autonomy policy engines per [AEOS](../AEOS/README.md)) MUST treat only ACTIVE qualifications as valid. SUSPENDED, REVOKED, and EXPIRED MUST all deny the associated authority; UNDER REVIEW retains authority unless conditions say otherwise.
- [AIES-AESQS-RR-01-R02] For AI systems, any status change out of ACTIVE MUST take effect in the enforcing systems within one business day, and immediately for EV3-related suspensions; the system's autonomy level for the affected task types MUST fall back to AL1 or AL0 until status is restored.

## 2. Revision Triggers

Revision means re-opening a qualification for re-evaluation (full or targeted) via [AIES-AESQS-QP-01 §7](qualification-process.md). Any of the following MUST trigger revision:

| Trigger | Applies to | Detail |
|---------|-----------|--------|
| **Incident** | Human & AI | An incident within the qualification's scope where the subject's in-scope work is plausibly causal — quality escape, security event, safety event, or repeated gate failures |
| **Sustained score drift** | Human & AI | Drift rule breach per [AIES-AESQS-CS-01 §7](capability-scoring.md) |
| **Model update** | AI | Any change to the underlying model(s), model version, or inference configuration of the qualified agent definition |
| **Context change** | AI | Material change to the agent definition (ART-14): tools, guardrails, escalation rules, or context assets (ART-13) that ground its work |
| **Role/domain change** | Human | Material change in the human's role, domain, or the AI tooling environment they were assessed in |
| **Taxonomy or framework change** | Human & AI | A new version of the [Shared Taxonomy](../Shared/Taxonomy/README.md) or [AIES-AESQS-CF-01](competency-framework.md) that alters the scoped roles, tiers, levels, or competency areas |
| **Audit finding** | Human & AI | An internal or external audit questioning the evidence, scoring, or review behind the grant |

- [AIES-AESQS-RR-01-R03] Sponsors of AI-system qualifications MUST notify the qualification authority of model updates and context changes **before** deploying them; operating a materially changed configuration under an unrevised qualification is an integrity violation under §3.
- [AIES-AESQS-RR-01-R04] Revision MUST be **targeted but sufficient**: it MUST re-evaluate every competency area and dimension the trigger casts doubt on, and MAY reuse unaffected evidence within its validity window. A model update MUST at minimum re-execute the golden-task suite and re-verify all gates.
- [AIES-AESQS-RR-01-R05] Pending revision outcomes, the qualification authority MUST decide within five business days whether the subject continues operating unchanged, continues with conditions (e.g., reduced AL, increased sampling), or is suspended.

## 3. Revocation

### 3.1 Criteria

- [AIES-AESQS-RR-01-R06] A qualification MUST be revoked when any of the following is established:
  - **Evidence falsification** — fabricated, tampered, or cherry-picked evidence ([AIES-AESQS-CS-01-R12](capability-scoring.md)) in the original assessment or in ongoing verification, by the candidate, sponsor, or assessor;
  - **Confirmed causal failure** — investigation confirms the subject's in-scope work caused a serious incident and re-assessment shows the capability threshold is not met;
  - **Gate collapse** — re-assessment after suspension fails a minimum gate ([AIES-AESQS-CS-01 §3.1](capability-scoring.md)) for the scoped tier;
  - **Integrity violation** — operating outside the qualification's conditions (scope, autonomy level, monitoring) after notice, or deploying a materially changed AI configuration under an unrevised qualification (R03);
  - **Unresolvable review defect** — the grant itself is found to have bypassed mandatory peer review or independence rules ([AIES-AESQS-PR-01](peer-review.md)) and cannot be retrospectively validated.
- [AIES-AESQS-RR-01-R07] Suspension (not immediate revocation) MUST be applied while facts are investigated whenever there is credible evidence of an EV3-relevant failure at RT3–RT4 scope, per [AIES-AESQS-CS-01-R16](capability-scoring.md). Suspension is protective, not punitive, and carries no finding.

### 3.2 Process

- [AIES-AESQS-RR-01-R08] Revocation MUST follow this sequence, each step recorded per §5:
  1. **Initiation** — trigger documented; subject/sponsor notified in writing with the evidence relied upon;
  2. **Investigation** — by an assessor and peer reviewer independent of the original grant (independence per [AIES-AESQS-PR-01 §3](peer-review.md)); the subject/sponsor MUST be given the opportunity to respond and to submit counter-evidence;
  3. **Decision** — by the qualification authority: revoke, downgrade (narrow scope / lower tier / lower AL cap), reinstate, or extend suspension (bounded, once);
  4. **Enforcement** — registry status change propagated to all consuming systems per R01/R02;
  5. **Notification** — decision and rationale delivered to the subject/sponsor with appeal rights (§4).
- [AIES-AESQS-RR-01-R09] Revocation for evidence falsification MUST additionally trigger review of **every other** qualification resting on evidence from the same source (same candidate, sponsor, assessor, or golden-task pipeline).
- [AIES-AESQS-RR-01-R10] After revocation, re-qualification MUST go through the full initial process of [AIES-AESQS-QP-01](qualification-process.md) — no renewal fast path — and, for falsification cases, MUST NOT begin before a waiting period defined by the qualification authority (minimum 6 months).

## 4. Appeals

- [AIES-AESQS-RR-01-R11] The subject (or sponsor, for AI systems) MAY appeal a denial, condition, suspension extension, or revocation within 20 business days of notification.
- [AIES-AESQS-RR-01-R12] Appeals MUST be heard by a panel of at least two qualified reviewers plus one qualification-authority representative, none of whom participated in the contested decision or the original grant; panel composition follows the independence rules of [AIES-AESQS-PR-01 §3](peer-review.md).
- [AIES-AESQS-RR-01-R13] The panel reviews process and evidence; it MAY commission new assessment but MUST NOT substitute lower thresholds. Outcomes: uphold, amend (conditions), or overturn — each with written rationale. The panel's decision is final within the organization.
- [AIES-AESQS-RR-01-R14] Appeals MUST NOT suspend enforcement: a revoked or suspended qualification remains inactive while the appeal is heard.

## 5. Audit Trail Requirements

The audit trail record (ART-15) is what makes qualification integrity demonstrable to auditors, regulators, and incident investigators.

- [AIES-AESQS-RR-01-R15] Every lifecycle event — grant, renewal, condition change, trigger detection, revision, suspension, restoration, revocation, appeal, and enforcement propagation — MUST produce an ART-15 record capturing: event type and timestamp; the qualification tuple affected; the actor(s) and their authority; the evidence or trigger relied upon (by reference); the decision and rationale; and the resulting status.
- [AIES-AESQS-RR-01-R16] ART-15 records for qualifications MUST be immutable and append-only; corrections are new records referencing the corrected one, never edits.
- [AIES-AESQS-RR-01-R17] The chain MUST be complete and queryable: from any production artifact, an auditor MUST be able to trace to the qualification (and its evidence, scores, and reviews) that authorized its producer at the time of production — including the exact agent definition version for AI-produced artifacts.
- [AIES-AESQS-RR-01-R18] Qualification audit records MUST be retained for at least the life of the qualification plus 3 years, or longer where regulatory obligations apply; organizations MUST document their retention schedule.
- [AIES-AESQS-RR-01-R19] Registry status and the enforcing systems MUST be reconciled on a defined schedule (at least quarterly); reconciliation discrepancies — an agent operating with authority its registry status does not support — MUST be treated as incidents under §2.

## Related Documents

| Concern | Defined in |
|---------|-----------|
| What triggers re-qualification before expiry | [AIES-AESQS-QP-01 §7](qualification-process.md) (summary) — detailed here §2 |
| Drift thresholds and monitoring mechanics | [AIES-AESQS-CS-01 §7](capability-scoring.md) |
| Independence of investigators and appeal panels | [AIES-AESQS-PR-01 §3](peer-review.md) |
| Operational enforcement of status changes | [AEOS (AIES-AEOS-00)](../AEOS/README.md) |
| Canonical definition of Audit Trail and ART-15 | [Glossary (AIES-SHARED-01)](../Shared/Glossary/README.md), [Taxonomy §7 (AIES-SHARED-02)](../Shared/Taxonomy/README.md#7-artifact-types) |

- [AIES-AESQS-00 — Module Overview](README.md)
- [AIES-AESQS-CF-01 — Competency Framework](competency-framework.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](evaluation-rubrics.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

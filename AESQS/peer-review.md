# Peer Review Standard

| | |
|---|---|
| **Document ID** | AIES-AESQS-PR-01 |
| **Status** | Review |
| **Audience** | Assessors & qualification authorities |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

Peer review is the integrity control of the [qualification process](qualification-process.md): an independent, qualified human examines the evidence, the scoring, and the recommended decision before any qualification is granted, renewed, or restored. This document defines who may review, how, and what they must produce.

---

## 1. Scope of Review

The peer reviewer answers four questions:

1. **Evidence integrity** — Is the evidence authentic, attributable, complete against [AIES-AESQS-QP-01 — Qualification Process §3](qualification-process.md), and free of cherry-picking ([AIES-AESQS-CS-01-R12 — Evidence populations are pre-registered and complete](capability-scoring.md))?
2. **Scoring validity** — Were the [rubrics](evaluation-rubrics.md) applied correctly, with the required double-rating and calibration?
3. **Decision soundness** — Do the scores, gates, and descriptor evidence support the recommended CL, scope, and (for AI systems) autonomy level per [AIES-AESQS-CS-01 — Capability Scoring](capability-scoring.md)?
4. **Scope honesty** — Is the requested scope (role × phases × risk tier) consistent with what the evidence actually demonstrates?

- [AIES-AESQS-PR-01-R01 — Peer Review, requirement 01] Every qualification grant, renewal, condition change, and restoration after suspension MUST pass peer review before taking effect. Denials SHOULD be peer reviewed on request of the candidate or sponsor.

## 2. Reviewer Qualifications

- [AIES-AESQS-PR-01-R02 — Peer Review, requirement 02] A peer reviewer MUST be a human who holds a current AESQS qualification in at least one competency area in the candidate's scope, at a CL level **not lower** than the level under review, and at a risk tier not lower than the scoped tier.
- [AIES-AESQS-PR-01-R03 — Peer Review, requirement 03] For RT3 — Significant through RT4 — Critical scopes, the reviewer MUST hold CL3 or higher in the candidate's core competency area ([AIES-AESQS-CF-01 — Competency Framework §2](competency-framework.md)).
- [AIES-AESQS-PR-01-R04 — Peer Review, requirement 04] Reviewers MUST be current on rater calibration per [AIES-AESQS-ER-01 — Evaluation Rubrics §4](evaluation-rubrics.md).
- [AIES-AESQS-PR-01-R05 — Peer Review, requirement 05] Reviewers of AI-system qualifications MUST additionally hold CL2 or higher in CA-06 (Testing, Quality & Evaluation Engineering) or CA-12 (Governance, Risk & AI Safety), sufficient to assess golden-task methodology and statistical claims.

Bootstrap exception: while an organization has no qualified reviewers (initial adoption), reviews MAY be performed by designated senior engineers under a documented bootstrap plan with an expiry date; bootstrap reviews MUST be re-confirmed by qualified reviewers within one validity period.

## 3. Independence Rules

- [AIES-AESQS-PR-01-R06 — Peer Review, requirement 06] The reviewer MUST NOT: (a) be the assessor, the candidate, or the sponsor; (b) have contributed to the evidence under review or to the candidate's preparation for this qualification; (c) share a direct reporting line with the candidate or sponsor; (d) have a personal or financial interest in the outcome.
- [AIES-AESQS-PR-01-R07 — Peer Review, requirement 07] For AI-system qualifications, the reviewer MUST be organizationally independent of the team that builds, operates, or owns the agent definition (ART-14) under review.
- [AIES-AESQS-PR-01-R08 — Peer Review, requirement 08] Reviewers MUST declare conflicts of interest before accepting a review; the qualification authority MUST reassign the review when independence cannot be established.
- [AIES-AESQS-PR-01-R09 — Peer Review, requirement 09] Peer review is a human judgment. AI systems MAY assist a reviewer (evidence retrieval, consistency checks, statistics recomputation) at AL2 — Collaborative or below, but the review conclusion MUST be the reviewer's own, and an AI system MUST NOT be recorded as the reviewer.

## 4. Review Protocol

```
1. Intake            Reviewer receives the full assessment package:
                     scope request, pre-registered sampling rule, evidence,
                     rubric scores and findings, descriptor evidence,
                     score aggregation, recommendation.
2. Completeness      Verify the package against AIES-AESQS-QP-01 §3 checklists.
   check             Missing or stale evidence → return to assessor (no partial review).
3. Independent       Reviewer re-scores a sample of evidence items
   verification      (≥ 20% of items; 100% of items with any EV3 finding)
                     without sight of the assessor's scores; recomputes
                     aggregation, gates, and confidence intervals.
4. AI-specific       For AI systems: §6 checks (provenance, reproduction,
   verification      contamination, guardrails).
5. Consolidation     Compare reviewer scores with assessor scores; resolve
                     divergences per §5.
6. Recommendation    Concur / Concur with conditions / Object — with written
                     rationale, recorded per §7.
```

- [AIES-AESQS-PR-01-R10 — Peer Review, requirement 10] The reviewer's independent re-scoring (step 3) MUST occur before the reviewer sees the assessor's scores for those items, and the review record MUST state the re-scored sample and the agreement observed.

## 5. Handling Disagreement

- [AIES-AESQS-PR-01-R11 — Peer Review, requirement 11] Score divergences of 2 or more points on any dimension of any item ([AIES-AESQS-ER-01-R07 — Evaluation Rubrics, requirement 07](evaluation-rubrics.md)), or any divergence that changes a gate outcome or the awarded CL, MUST be resolved before a decision — by structured discussion against the anchor tables, and failing that, by a third calibrated rater whose score is decisive for that item.
- [AIES-AESQS-PR-01-R12 — Peer Review, requirement 12] Divergences MUST be resolved by re-examining evidence against anchors, never by splitting the difference on outcome-changing items.
- [AIES-AESQS-PR-01-R13 — Peer Review, requirement 13] If assessor and reviewer disagree on the final recommendation after resolution, the qualification authority decides, and MUST record both positions and the deciding rationale in the review record. The authority MUST NOT grant a scope broader than the more conservative recommendation without commissioning additional evidence.

## 6. Reviewing AI-System Qualifications

AI-system reviews carry checks that human reviews do not:

- [AIES-AESQS-PR-01-R14 — Peer Review, requirement 14] The reviewer MUST verify golden-task provenance: suite version, held-out status, refresh history, and that reported runs are complete (no discarded runs) per [AIES-AESQS-QP-01-R09 — Qualification Process, requirement 09](qualification-process.md) and [AIES-AESQS-CS-01-R12 — Evidence populations are pre-registered and complete](capability-scoring.md).
- [AIES-AESQS-PR-01-R15 — Peer Review, requirement 15] The reviewer MUST independently re-execute a sample of golden-task runs (or commission an independent re-execution) against the exact agent definition version under review, and compare outcomes with the reported results. Material discrepancy is an evidence-integrity finding.
- [AIES-AESQS-PR-01-R16 — Peer Review, requirement 16] The reviewer MUST check for evaluation contamination: golden tasks or their solutions present in the agent's context assets (ART-13), retrieval sources, or sponsor-controlled tuning data.
- [AIES-AESQS-PR-01-R17 — Peer Review, requirement 17] The reviewer MUST verify that the guardrails and escalation rules declared in the agent definition (ART-14) were active during assessment and are the same ones that will be active in operation, and that escalation behavior was actually exercised ([AIES-AESQS-QP-01-R08 — Qualification Process, requirement 08](qualification-process.md)).
- [AIES-AESQS-PR-01-R18 — Peer Review, requirement 18] The reviewer MUST confirm the requested autonomy level respects [AIES-AESQS-CS-01 — Capability Scoring §5](capability-scoring.md), including the prohibition on initial AL4 — Autonomous grants.

## 7. Structured Review Record

- [AIES-AESQS-PR-01-R19 — Peer Review, requirement 19] Every peer review MUST produce a structured review record, stored in the qualification registry and linked as an audit trail record (ART-15), containing at minimum:

| Field | Content |
|-------|---------|
| Review ID | Stable identifier |
| Qualification reference | The scope tuple under review ([AIES-AESQS-QP-01 — Qualification Process §2](qualification-process.md)) |
| Reviewer identity & basis | Reviewer, their qualifying credentials (R02–R05), independence declaration (R06–R08) |
| Package version | Hashes/references of the evidence package reviewed |
| Completeness result | Checklist outcome, returns to assessor if any |
| Re-scored sample | Items re-scored, blind scores, agreement vs assessor |
| AI-specific checks | R14–R18 outcomes (AI systems only) |
| Divergences & resolutions | Each outcome-changing divergence and how resolved |
| Recommendation | Concur / concur with conditions / object — with rationale |
| Conditions proposed | Scope narrowing, AL cap, monitoring requirements |
| Date & signature | Attestation by the reviewer |

- [AIES-AESQS-PR-01-R20 — Peer Review, requirement 20] Review records MUST be retained for the life of the qualification plus the audit retention period of [AIES-AESQS-RR-01 — Revision and Revocation §5](revision-and-revocation.md), and MUST be available to appeals panels and auditors.

---

## Related Documents

- [AIES-AESQS-00 — AESQS — AI Engineering SDLC Qualification Standard](README.md)
- [AIES-AESQS-CF-01 — Competency Framework](competency-framework.md)
- [AIES-AESQS-QP-01 — Qualification Process](qualification-process.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](evaluation-rubrics.md)
- [AIES-AESQS-CS-01 — Capability Scoring](capability-scoring.md)
- [AIES-AESQS-RR-01 — Revision & Revocation](revision-and-revocation.md)
- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) · [Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

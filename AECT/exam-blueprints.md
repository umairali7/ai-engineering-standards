# Exam Blueprints

| | |
|---|---|
| **Document ID** | AIES-AECT-EB-01 |
| **Status** | Review |
| **Audience** | Educators & training providers · Assessors & qualification authorities |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

This document defines the examination blueprints for the AIES certification tiers: the content domains and their weightings, item formats, item counts, duration, and pass thresholds, plus sample items and the security and fairness requirements governing exam operation.

[AIES-AECT-EB-01-R01 — Exam Blueprints, requirement 01] Every exam item MUST trace to a blueprint domain, and every blueprint domain MUST trace to one or more [AEBOK Knowledge Areas](../AEBOK/README.md) or the [Shared Standards](../Shared/README.md). Items that cannot be traced MUST NOT be used.

[AIES-AECT-EB-01-R02 — Exam Blueprints, requirement 02] Exam forms MUST match the domain weightings of this blueprint within ±3 percentage points per domain.

[AIES-AECT-EB-01-R03 — Exam Blueprints, requirement 03] Exam items MUST be vendor-neutral: no item may depend on knowledge of a specific commercial AI model, product, or provider. Scenario items use fictional, generic systems.

## 2. Item Formats

| Code | Format | Description | Scoring |
|------|--------|-------------|---------|
| MC | Multiple choice | Single best answer from four options | 1 point |
| MR | Multiple response | Select all that apply (number stated) | Partial credit |
| SB | Scenario-based | A delivery scenario (150–400 words) followed by 2–4 dependent items | Per item |
| WPC | Work-product critique | A realistic artifact (diff, ADR, test report, agent definition, audit trail excerpt) that the candidate must critique or judge | Rubric-anchored, 2–4 points |

Higher tiers weight SB and WPC more heavily, because CL2 and CL3 competency is about applying and adapting practice, not recalling it.

## 3. Associate Exam (CL1)

- **Prepared by:** [LP-F Foundation Path](learning-paths.md#3-lp-f--foundation-path)
- **Items:** 60 (52 MC, 8 MR) · **Duration:** 90 minutes · **Pass threshold:** 65% (39/60 scaled points)
- **Cognitive emphasis:** remember and understand; apply in guided contexts.

| # | Domain | Source | Weight |
|---|--------|--------|--------|
| A1 | Foundations, vocabulary, and taxonomy: phases, domains, autonomy levels, risk tiers, roles, CL levels, EV dimensions | KA-01, Glossary, Taxonomy | 30% |
| A2 | Lifecycle practices survey: how AI participation changes each phase | KA-02 … KA-09 (survey depth) | 40% |
| A3 | Human oversight fundamentals: gates, review, accountability, escalation | KA-11 | 15% |
| A4 | Context and knowledge basics: context assets, provenance | KA-10 | 8% |
| A5 | Evaluation basics: why evidence, what EV1–EV6 measure | KA-12 | 7% |
| | | **Total** | **100%** |

### 3.1 Sample Items

**Sample A-1 (MC, domain A1).** A coding agent is assigned to fix documentation typos across a repository. Under the default AIES risk-tier model, what is the maximum autonomy level this task may run at?

- A. AL1 — Assisted — the agent may only suggest edits
- B. AL2 — Collaborative — a human must review every change before it takes effect
- C. AL3 — Delegated — the agent works in an envelope with checkpoint approval
- **D. AL4 — Autonomous — the agent may execute end-to-end within hard guardrails** ✓

*Rationale:* Documentation typos are RT1 — Minimal (Minimal) work, and [Taxonomy §4](../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4) sets the default maximum autonomy for RT1 — Minimal at AL4 — Autonomous. Options A–C describe lower autonomy levels that an organization MAY choose but is not required to.

**Sample A-2 (MC, domain A3).** Which role in the AIES role model can never be staffed by an AI agent?

- A. ROLE-06 Software Engineer
- B. ROLE-07 QA Engineer
- **C. ROLE-13 Human Approver** ✓
- D. ROLE-01 Planner

*Rationale:* The taxonomy requires ROLE-13 (Human Approver) and ROLE-14 (Governance Officer) to be staffed by humans; all other roles may be staffed by a human, an AI agent, or a human-AI pair.

**Sample A-3 (MR, domain A5).** Which TWO of the following are evaluation dimensions in the AIES model (EV1–EV6)?

- **A. Traceability** ✓
- B. Novelty
- **C. Maintainability** ✓
- D. Popularity

*Rationale:* EV6 is Traceability and EV4 is Maintainability. Novelty and popularity are not AIES evaluation dimensions; capability claims must rest on the six defined dimensions.

## 4. Practitioner Exam (CL2)

- **Prepared by:** the Practitioner segment of any [role-based path](learning-paths.md#4-role-based-paths-cl2--cl3)
- **Items:** 80 (40 MC, 10 MR, 24 SB items across 8 scenarios, 6 WPC) · **Duration:** 150 minutes · **Pass threshold:** 70% scaled
- **Cognitive emphasis:** apply independently in standard situations.

| # | Domain | Source | Weight |
|---|--------|--------|--------|
| P1 | The autonomy/risk model in practice | KA-01 | 10% |
| P2 | Planning and decomposing work for mixed human/AI execution | KA-04 | 10% |
| P3 | AI-assisted implementation: generation practice, review discipline, provenance | KA-05 | 20% |
| P4 | Testing AI-produced code and AI-assisted test generation | KA-06 | 15% |
| P5 | Security and delivery pipelines as guardrails | KA-07, KA-08 | 15% |
| P6 | Operating and observing AI-inclusive systems | KA-09 | 8% |
| P7 | Context and knowledge management | KA-10 | 10% |
| P8 | Working under oversight: gates, escalation, accountability | KA-11 | 12% |
| | | **Total** | **100%** |

### 4.1 Sample Items

**Sample P-1 (SB, domain P3).** *Scenario:* Your team runs a coding agent at AL2 — Collaborative on RT2 — Moderate feature work. A reviewer notices that over the last sprint, review comments on the agent's pull requests have dropped from an average of 6 per PR to 0, while the merge rate has doubled. The agent's evaluation scores have not changed. What is the most important risk to raise first?

- A. The agent's capability has silently improved, so its autonomy level should be raised to AL3 — Delegated
- **B. Review may have degraded to rubber-stamping, so AL2 — Collaborative's control assumption (human reviews every output) may no longer hold** ✓
- C. The agent is producing fewer changes, so throughput reporting is inaccurate
- D. The team is under-utilizing the agent and should assign it RT3 — Significant work

*Rationale:* AL2 — Collaborative is only a meaningful control if per-item human review actually happens. Zero review findings with unchanged agent capability is a classic rubber-stamping signal (an anti-pattern in KA-05/KA-11); the control may have silently failed. Raising autonomy (A, D) on the basis of absent review evidence inverts the evidence-driven rule.

**Sample P-2 (MC, domain P5).** A delivery pipeline accepts AI-produced changes to production configuration when tests pass. Under AIES defaults, what is wrong with this design?

- A. Nothing, if the test suite is comprehensive
- B. AI systems may never touch production configuration
- **C. Production configuration is RT3 — Significant, so per-item human review (AL2 — Collaborative or stricter) is required; a green pipeline alone does not satisfy it** ✓
- D. The pipeline should also require the agent to self-assess its confidence

*Rationale:* Production configuration is an RT3 — Significant example in the taxonomy, with default maximum autonomy AL2 — Collaborative — a human must review each change before it takes effect. Automated quality gates complement but do not replace the human gate. Option B overstates (review-gated participation is permitted); option D is not a control.

**Sample P-3 (WPC, domain P7).** *Work product:* an excerpt of a context asset (ART-13) that embeds a customer's production database connection string as an example, cites a coding convention marked "deprecated 2025-01", and contains no owner or review date. Identify the three most significant defects and state, for each, the practice it violates.

*Gold-standard answer outline:* (1) secret material in AI-consumable context — a security violation (KA-07/KA-10): context assets are widely distributed to AI systems and must not carry credentials; (2) stale normative guidance — the deprecated convention will be confidently applied by AI consumers (KA-10 currency practice); (3) missing ownership/review metadata — context assets are versioned, owned artifacts; without provenance they cannot be trusted or audited (EV6). Full credit requires identifying all three and naming the violated practice; partial credit per defect.

## 5. Professional Exam (CL3)

- **Prepared by:** the Professional segment of any role-based path
- **Items:** 70 (20 MC, 30 SB items across 10 scenarios, 20 WPC) · **Duration:** 180 minutes · **Pass threshold:** 72% scaled, with a minimum of 60% in domains D3 and D5 (review and oversight cannot be compensated by other domains)
- **Cognitive emphasis:** analyze, evaluate, adapt to novel situations; judge others' work.

| # | Domain | Source | Weight |
|---|--------|--------|--------|
| D1 | Adapting the autonomy/risk model to novel situations and organizational constraints | KA-01 | 12% |
| D2 | Architecture and design for AI operability | KA-03 | 13% |
| D3 | Reviewing and critiquing AI-produced work products | KA-05, KA-06 | 25% |
| D4 | Security and release governance for AI-produced change | KA-07, KA-08 | 15% |
| D5 | Oversight design, review ergonomics, coaching, and skill preservation | KA-11 | 20% |
| D6 | Evaluation programs, feedback loops, capability drift | KA-12 | 15% |
| | | **Total** | **100%** |

Candidates pursuing a [role-specialization endorsement](certification-framework.md#3-role-specialization-endorsements) additionally sit a 25-item endorsement section (100% weighted on the endorsement's deep-dive KAs, pass threshold 72%).

### 5.1 Sample Items

**Sample PR-1 (SB, domain D1).** *Scenario:* A regulated insurer wants an agent to autonomously remediate dependency vulnerabilities across 200 services. Most bumps are mechanical; some touch authentication libraries. The head of platform proposes "AL3 — Delegated for the whole program, it's mostly low risk." As the certified professional advising them, what is the correct framing?

- A. Accept AL3 — Delegated — the majority risk profile governs the program
- B. Reject autonomy entirely — security-adjacent work is always RT4 — Critical
- **C. Split the task types: mechanical bumps with passing verification are RT2 — Moderate (up to AL3 — Delegated), while auth-adjacent changes are RT3 — Significant (AL2 — Collaborative maximum by default); autonomy is assigned per task type, per risk tier, never program-wide** ✓
- D. Run at AL4 — Autonomous with a rollback plan, since reversibility eliminates risk

*Rationale:* The taxonomy assigns autonomy per task type per risk tier, never globally ([AIES-SHARED-02-R01 — Taxonomy, requirement 01]). CL3 competency is recognizing that a "program" is a mixture of risk tiers and designing the split. B overcorrects; D confuses mitigation with risk-tier reduction.

**Sample PR-2 (WPC, domain D3).** *Work product:* a pull request produced by a coding agent that implements a requested rate limiter. The diff is functionally correct and well-tested, but it also silently refactors an unrelated logging module, removes a failing flaky test rather than fixing it, and its provenance record omits which context assets were supplied. Write the review verdict and the three findings a CL3 reviewer must raise, mapping each to an evaluation dimension.

*Gold-standard answer outline:* Verdict: request changes — correctness of the primary change (EV1) does not outweigh the findings. (1) Out-of-scope refactoring — scope discipline / reviewability finding (EV4 Maintainability, also EV6: change not traceable to an approved work item); (2) deleting a failing test to achieve green — an integrity anti-pattern that manufactures false quality evidence (EV3, EV1); (3) incomplete provenance — the change cannot be audited to its inputs (EV6). Full credit requires the correct verdict, all three findings, and sensible EV mapping.

**Sample PR-3 (SB, domain D5).** *Scenario:* An organization's approval-gate queue for RT3 — Significant changes has grown to a 4-day wait. A director proposes automatically approving anything that waits more than 48 hours. Which response best reflects CL3 oversight design?

- A. Agree — stale approvals are worse than no approvals
- B. Refuse — gate latency is the necessary price of safety and cannot be engineered
- **C. Treat gate latency as an oversight-design defect: add qualified approvers, tier the queue by risk within RT3 — Significant, improve review ergonomics (smaller diffs, better provenance summaries) — but timeout-approval converts the gate into no gate and must be rejected** ✓
- D. Reclassify the backlog to RT2 — Moderate so the gate no longer applies

*Rationale:* KA-11 treats review ergonomics and gate throughput as design problems the professional owns. Auto-approval on timeout (A) silently removes the human control while leaving its appearance — worse than an honest policy change. D is risk-tier manipulation, a governance violation.

## 6. Fellow Assessment (CL4)

Fellow certification has **no written exam** ([AIES-AECT-CERT-01 — Certification Framework §2.2](certification-framework.md#22-prerequisites-and-evidence-requirements)); it is assessed by portfolio and a structured panel review. The panel evaluates against these weighted criteria:

| # | Criterion | Weight |
|---|-----------|--------|
| F1 | Organizational-scale practice setting: evidence of designing and rolling out AI-native operating policy across teams | 35% |
| F2 | Trade-off judgment: reasoned handling of competing concerns (velocity vs. oversight, cost vs. quality, autonomy vs. accountability) at portfolio scale | 30% |
| F3 | Advancement of the discipline: contribution per [AIES-AECT-CERT-01 — Certification Framework §2.5](certification-framework.md#25-peer-contribution-fellow) | 20% |
| F4 | Coaching and capability building: evidence of developing others to CL2/CL3 | 15% |

*Sample panel probe (F2):* "Walk us through a case where you lowered an autonomy level after it had been granted. What evidence triggered it, what resistance did you meet, and what did it cost?" — A strong answer demonstrates evidence-driven reversal ([AIES-SHARED-02-R03 — Taxonomy, requirement 03]), candor about organizational friction, and measurement of the outcome; a weak answer has never reversed autonomy or frames reversal as failure rather than governance working.

## 7. Exam Security and Fairness

[AIES-AECT-EB-01-R04 — Exam Blueprints, requirement 04] Exams MUST be delivered under identity verification and proctoring (in-person or remote), with secure item banks; live items MUST NOT be published, and disclosed items MUST be retired.

[AIES-AECT-EB-01-R05 — Exam Blueprints, requirement 05] Item banks MUST be large enough to generate multiple equated forms per tier, and forms MUST be statistically equated so that pass decisions are comparable across forms and sessions.

[AIES-AECT-EB-01-R06 — Exam Blueprints, requirement 06] Every item MUST be reviewed before release for (a) traceability to AEBOK, (b) vendor neutrality, (c) bias and accessibility — including plain-language phrasing, culture-neutral scenarios, and screen-reader-compatible delivery. Item-level performance statistics MUST be monitored for differential functioning and flagged items withdrawn pending review.

[AIES-AECT-EB-01-R07 — Exam Blueprints, requirement 07] Candidates MUST be offered reasonable accommodations (extra time, assistive technology, alternative formats) consistent with applicable accessibility law, without altering the construct being measured.

[AIES-AECT-EB-01-R08 — Exam Blueprints, requirement 08] Use of AI assistance during a knowledge exam MUST be prohibited and technically deterred. (Practical labs are different: they *require* working with AI systems under the lab's declared rules — see [AIES-AECT-LAB-01 — Labs](labs.md).)

[AIES-AECT-EB-01-R09 — Exam Blueprints, requirement 09] Pass thresholds in this blueprint MUST be validated by a documented standard-setting exercise (e.g., modified Angoff) before an exam form is used for certification decisions, and revalidated at every major standard version.

Candidates may retake a failed exam after 14 days (first retake) and 60 days (subsequent retakes), with a maximum of three attempts per 12-month period.

## Related Documents

- [Certification Framework (AIES-AECT-CERT-01 — Certification Framework)](certification-framework.md) — where each exam fits in the credential
- [Learning Paths (AIES-AECT-LP-01 — Learning Paths)](learning-paths.md) — preparation
- [Labs (AIES-AECT-LAB-01 — Labs)](labs.md) — the practical counterpart to these exams
- [AESQS (AIES-AESQS-00 — Qualification Standard)](../AESQS/README.md) — scoring methodology for practical assessment

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

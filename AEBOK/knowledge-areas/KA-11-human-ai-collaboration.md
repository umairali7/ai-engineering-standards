# KA-11 — Human-AI Collaboration & Oversight

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-11 |
| **Status** | Review |
| **Audience** | Engineers · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-11 covers Human Oversight (X07) as a designed discipline. Every autonomy level below AL4 depends on a human doing something well — authoring, reviewing, approving, sampling — and every gate in the operating model assumes that the human at it exercises real judgment. That assumption fails quietly: attention saturates, approvals become reflexes, and the control layer degrades into ceremony while its records still look complete. KA-11 defines how to design gates and reviews that humans can actually perform, how to detect when oversight has become theater, how accountability attaches to AI-performed work, and how to keep human skill alive when delegation removes the practice that built it. The operational mechanics — gate taxonomy, approver workload rules, override machinery — are specified in [AEOS Human Oversight](../../AEOS/human-oversight.md); KA-11 is the knowledge that makes those mechanics work.

## 2. Key Concepts

- **Oversight is a scarce budget.** Human attention is the limiting resource of AI-native delivery ([KA-01](KA-01-foundations.md)). Gates placed uniformly, rather than by risk tier, spend that budget on RT1 trivia and starve RT3/RT4 decisions; oversight design is the allocation of scarce judgment to where it changes outcomes.
- **Review ergonomics determine review quality.** A human's ability to find intent-level errors falls sharply with diff size, missing decision context, and interruption load. A review is performable when the increment is bounded, the change arrives with what was asked (work item, acceptance criteria, assumptions, evidence), and the reviewer has time budgeted for it — otherwise the design of the work, not the diligence of the reviewer, has already decided the review's quality.
- **Rubber-stamping is a measurable failure state.** When approval becomes near-certain and near-instant regardless of content, the gate is theater: it adds latency and audit records but no verification. Approval rates, decision dwell times, and rejection distributions are control-health telemetry, not personnel metrics — their purpose is to fix gate design, not to grade reviewers.
- **Accountability is non-transferable.** Every AI-performed task has an accountable human; "the agent did it" is never a terminal answer in an incident review. The Human Approver (ROLE-13) MUST be a human per the [Taxonomy](../../Shared/Taxonomy/README.md#5-ai-engineering-roles), and approving is accepting accountability for the decision — which is why approvals cannot be delegated to AI, at any autonomy level.
- **Skill preservation is an oversight dependency.** The judgment that makes review meaningful was built by doing the work now delegated. Sustained delegation without deliberate practice atrophies exactly the skills the control layer depends on — a slow failure that appears as gradually less-substantive review long before anyone names it.
- **Escalation is a designed behavior.** Agents at AL3+ escalate at envelope edges by design, and the discipline for humans is to treat escalations as the system working, not as noise or as someone's failure. A culture that punishes escalation — by blame or by backlog — trains both humans and agents to stop escalating.
- **Pairing models are autonomy levels in practice.** AL1–AL3 correspond to distinct collaboration shapes — AI-suggests/human-authors, AI-drafts/human-reviews-each, AI-executes/human-supervises-by-checkpoint. Choosing a pairing model *is* choosing an autonomy level, and it is chosen per task type and risk tier, never by personal preference alone.

## 3. Core Practices

- **Design gates as decisions, not ceremonies.** [AIES-AEBOK-KA-11-R01] Every human oversight gate MUST define what is being decided, the evidence the decision requires, the role authorized to decide, and the rejection path; gate outcomes MUST be recorded to the audit trail (ART-15) with approver identity and disposition, per [AEOS Human Oversight](../../AEOS/human-oversight.md).
- **Size work for its reviewers.** [AIES-AEBOK-KA-11-R02] AI-produced changes routed to human review MUST arrive as reviewable increments with decision context attached — the authorizing work item, acceptance criteria, declared assumptions, and verification evidence; changes exceeding the team's reviewable-increment bound MUST be split before review, not skimmed at size.
- **Monitor the control, not just the work.** [AIES-AEBOK-KA-11-R03] Organizations MUST monitor gate-health signals (approval rates, decision dwell time, rejection and rework distributions) for gates on RT2+ paths and MUST treat degenerate patterns as a control failure requiring gate redesign, workload rebalancing, or autonomy reduction — not as grounds for individual blame.
- **Keep accountability attached.** [AIES-AEBOK-KA-11-R04] Every AI-performed task MUST have an identified accountable human before execution; approval authority MUST NOT be delegated to an AI system, and approvals MUST NOT be issued by actors lacking the competency (CL) the gate's decision requires.
- **Preserve the skills oversight consumes.** Teams SHOULD maintain deliberate human practice in delegated task types — periodic manual execution, deep-review rotations, incident-drill participation — sized so that reviewer competence does not decay below what the team's gates assume.
- **Make escalation cheap and blameless.** Escalation paths SHOULD be low-friction and answered within defined time bounds; escalation frequency SHOULD be tracked as a system signal (too low is as suspicious as too high).

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Human Checkpoint Sampling** | At AL3, humans review a risk-weighted sample of outputs plus all envelope-edge events, with rates tied to evaluation history — sustainable oversight at delegation volume. See [catalog](../patterns/README.md#pat-08-human-checkpoint-sampling). |
| **Reviewable Increment** | Work is decomposed so each human decision covers a bounded, coherent change; reviewability is enforced upstream at planning ([KA-04](KA-04-planning-decomposition.md)), not negotiated at the gate. |
| **Decision-Context Bundle** | Every item awaiting approval carries its work item, assumptions, and evidence; the reviewer never reconstructs intent from the diff alone. |
| **Escalation Ladder** | A pre-defined chain (performer → supervisor → gate owner → governance) with time bounds per rung; uncertainty travels upward instead of being resolved by guessing. |
| **Deliberate Practice Rotation** | Team members periodically perform delegated task types manually and rotate through deep-review duty; reviewer judgment is renewed, not just consumed. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Review Theater** | Approvals are issued on green CI and clean formatting while intent-level errors flow through; the audit trail records diligence that never occurred. See [catalog](../patterns/README.md#apat-02-review-theater). |
| **Silent Delegation** | Work is quietly re-delegated to AI above its declared autonomy level — outputs forwarded without the review the level requires; the declared control and the actual control diverge without a record. See [catalog](../patterns/README.md#apat-04-silent-delegation). |
| **Gate Saturation** | Review demand outgrows reviewer capacity with no rebalancing; queues force a choice between delivery and diligence, and diligence loses quietly. |
| **Atrophy by Delegation** | Years of AL3 delegation with no deliberate practice leave no one who can still perform — or meaningfully review — the delegated work when the system fails. |
| **Hero Approver** | One trusted senior becomes the approver for everything; their saturation becomes the single point of failure for the entire control layer. |

## 6. Competency Expectations

| Level | Expectation in KA-11 |
|-------|----------------------|
| **CL1** | Explains autonomy levels as collaboration models and why accountability stays human; performs assigned reviews with decision context; escalates uncertainty through the defined path. |
| **CL2** | Independently reviews AI-produced work against intent at AL2; prepares decision-context bundles; recognizes rubber-stamping signals in their own practice and flags gate overload. |
| **CL3** | Designs gate placement and sampling regimes for a product area; monitors and tunes gate-health telemetry; runs deliberate-practice rotations; coaches reviewers on intent-level review. |
| **CL4** | Sets organizational oversight policy (X07): gate standards, approver qualification requirements, workload and skill-preservation doctrine; evaluates the control layer's real effectiveness portfolio-wide as autonomy grows. |

## Related Documents

- The autonomy/risk model that oversight enforces: [KA-01 Foundations (AIES-AEBOK-KA-01)](KA-01-foundations.md); review-load planning: [KA-04 Planning & Work Decomposition (AIES-AEBOK-KA-04)](KA-04-planning-decomposition.md).
- Review discipline for source change specifically: [KA-05 AI-Assisted Implementation (AIES-AEBOK-KA-05)](KA-05-implementation.md); go/no-go gates in pipelines: [KA-08 DevOps & Release Engineering (AIES-AEBOK-KA-08)](KA-08-devops-release.md).
- Evidence that justifies changing gate density and autonomy: [KA-12 Evaluation & Continuous Improvement (AIES-AEBOK-KA-12)](KA-12-evaluation-improvement.md).
- Operational specification of gates, approver workload, and kill switches: [AEOS Human Oversight (AIES-AEOS-HO-01)](../../AEOS/human-oversight.md); roles ROLE-13/ROLE-14: [Taxonomy §5 (AIES-SHARED-02)](../../Shared/Taxonomy/README.md#5-ai-engineering-roles).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

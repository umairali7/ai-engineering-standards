# EX-01 — Risk-Tiering a Real Product Backlog

| | |
|---|---|
| **Document ID** | AIES-EX-01 |
| **Status** | Review |
| **Audience** | Engineering leadership · Engineers |

> **This example is informative, not normative.** Nothing here adds to, relaxes, or reinterprets any AIES requirement; where this example and a standard disagree, the standard wins. All organizations, people, products, and systems named below — including **Fieldstone** and its agent **FS-AGENT-ENG-01** — are fictional. No real AI vendor, model, or product is named or implied.

---

## 1. Scenario

**Fieldstone** is a ~400-engineer company building a field-service management SaaS platform: work-order scheduling, a technician mobile app, customer billing with card payments, and IoT telemetry ingestion from customer equipment. Fieldstone is adopting AIES and has registered one AI coding agent, **FS-AGENT-ENG-01**, under an agent definition (ART-14) — see [EX-02](../EX-02-autonomy-envelope/README.md) for that definition in full.

This example walks through Fieldstone's planning session for its 2026-Q3 backlog: how each work item (ART-05, [Taxonomy §7](../../Shared/Taxonomy/README.md#7-artifact-types)) is classified into a risk tier RT1 — Minimal through RT4 — Critical per [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4), and what maximum autonomy level that tier permits per [AIES-SHARED-02-R02 — Taxonomy, requirement 02](../../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4).

**Participants.** Dana Okafor, delivery planning lead (ROLE-01 Planner); the four squad team leads (Team Dispatch, Team Ledger, Team Fieldkit, Team Pulse); Tomás Herrera, platform team lead (Team Basalt); Priya Raman, Governance Officer (ROLE-14), who samples tier assignments per [SDLC P08 — Planning](../../docs/SDLC.md#p08--planning). Tiering happens **before** staffing and autonomy decisions, per [AIES-AEOS-OM-01-R07 — Operating Model, requirement 07](../../AEOS/operating-model.md#2-work-intake-and-flow).

## 2. The Procedure Fieldstone Uses

For every backlog item, the planner asks four classification questions and records the answers on the work item. The tier is set by the **worst** answer, never the average — classifying at the average tier is the **Tier Averaging** anti-pattern named in [AEBOK KA-04 §5](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md#5-anti-patterns).

| # | Question | What it probes |
|---|----------|----------------|
| Q1 | **Blast radius** — if this change is wrong, what is affected, and how widely? | Scope of harm |
| Q2 | **Reversibility** — can the effect be undone quickly and completely? | Recoverability |
| Q3 | **Data sensitivity** — does it touch personal, financial, or otherwise sensitive data? | Confidentiality/integrity stakes |
| Q4 | **Regulatory touch** — does a legal or contractual regime constrain this work? | Compliance exposure |

The assigned tier then yields the default maximum autonomy level from [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4): **RT1 — Minimal → AL4 — Autonomous, RT2 — Moderate → AL3 — Delegated, RT3 — Significant → AL2 — Collaborative, RT4 — Critical → AL1 — Assisted**. Fieldstone's organizational policy (FS-POL-AI-001, its instantiation of AEOS per [AIES-AEOS-GOV-01-R01 — Governance Operations, requirement 01](../../AEOS/governance-operations.md#2-policy-hierarchy)) adopts these defaults unchanged; loosening them would require a documented risk acceptance per [AIES-AEOS-GOV-01-R09 — Governance Operations, requirement 09](../../AEOS/governance-operations.md#4-risk-acceptance), and Fieldstone has granted none.

Two more rules from the standards shape the session:

- Every work item routed to AI execution must leave planning with its risk tier, assigned autonomy level, and performer recorded, per [AIES-AEBOK-KA-04 — KA-04 — Planning & Work Decomposition](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md#3-core-practices) and [AIES-AEOS-OM-01-R05 — Operating Model, requirement 05](../../AEOS/operating-model.md#2-work-intake-and-flow).
- The tier caps autonomy; it does not grant it. The actual level assigned later is `min(tier cap, performer's qualified level, level the task needs)` — the least-autonomy rule of [AIES-AEOS-OM-01-R13 — Operating Model, requirement 13](../../AEOS/operating-model.md#5-autonomy-assignment).

## 3. The Q3 Backlog, Item by Item

Twelve items entered the session. Each worksheet below is the record Dana attached to the work item.

### FS-2601 — Add bulk-reschedule to dispatcher console

Deferred to §4 — this item was **split into differently-tiered subtasks** rather than tiered whole.

### FS-2602 — Migrate card-on-file tokens to the new payment provider ("Meridian Pay", fictional)

| Question | Finding |
|----------|---------|
| Blast radius | Every stored payment method for every billing customer; failed migration breaks recurring billing platform-wide |
| Reversibility | Poor — tokens de-provisioned at the old provider cannot be restored; partial migration leaves split-brain billing state |
| Data sensitivity | Card-on-file payment tokens (financial) |
| Regulatory touch | Card-network data-security obligations; contractual SLAs with enterprise customers |

**Decision: RT4 — Critical** — financial transactions plus effectively irreversible actions, both listed RT4 — Critical exemplars. **Max autonomy: AL1 — Assisted** (AI suggests; humans author). Per [AIES-AEOS-OM-01-R11 — Operating Model, requirement 11](../../AEOS/operating-model.md#4-staffing-decision-procedure), the role is staffed by humans with agent participation limited to AL1 — Assisted assistance.

### FS-2603 — Fix timezone bug in technician timesheet

Deferred to §5 — this is the session's **borderline case**, argued both ways below. **Decision: RT3 — Significant, max AL2 — Collaborative.**

### FS-2604 — Add test coverage for the route-optimization module

| Question | Finding |
|----------|---------|
| Blast radius | No production behavior changes; but the suite will *gate* future route-optimization changes, so weak tests silently weaken a control |
| Reversibility | Full — tests can be revised freely |
| Data sensitivity | None; synthetic route fixtures |
| Regulatory touch | None |

**Decision: RT2 — Moderate** — the team lead initially said RT1 — Minimal ("it's just tests"), but Dana pointed at the taxonomy's own wording: RT1 — Minimal lists *test scaffolding*; *test suites* that gate promotion are the RT2 — Moderate exemplar. A gating suite that asserts nothing is [APAT-10 Coverage Theater](../../AEBOK/patterns/README.md#apat-10-coverage-theater). **Max autonomy: AL3 — Delegated**, with acceptance criteria required as contracts per [AIES-AEBOK-KA-04 — KA-04 — Planning & Work Decomposition](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md#3-core-practices).

### FS-2605 — Revise IoT alert thresholds for compressor-class equipment

| Question | Finding |
|----------|---------|
| Blast radius | Alerting for ~11,000 customer compressor units; a threshold set too loose suppresses failure warnings on customer property |
| Reversibility | Config rollback is fast, but a missed alert during the bad window is not recoverable |
| Data sensitivity | Equipment telemetry only; no personal data |
| Regulatory touch | Contractual monitoring SLAs; no statutory regime for this equipment class |

**Decision: RT3 — Significant** — production configuration with customer-facing consequence. The team noted that if Fieldstone ever monitors equipment classes where a missed alert is a safety event, those thresholds would be RT4 — Critical; FS-POL-AI-001 records that trigger so the tier is re-evaluated if scope changes, per [AIES-AEOS-OM-01-R07 — Operating Model, requirement 07](../../AEOS/operating-model.md#2-work-intake-and-flow). **Max autonomy: AL2 — Collaborative.**

### FS-2606 — GDPR data-export endpoint (data-subject access requests)

| Question | Finding |
|----------|---------|
| Blast radius | Assembles and egresses a complete personal-data profile per customer; an over-broad query leaks another subject's data |
| Reversibility | None — a wrongful disclosure cannot be recalled |
| Data sensitivity | Personal data across every store that holds it, by design |
| Regulatory touch | Direct: statutory data-protection obligations with deadlines and penalties |

**Decision: RT4 — Critical** — regulated data plus irreversible disclosure. **Max autonomy: AL1 — Assisted.** Human-staffed (Team Basalt platform engineers) with the agent drafting nothing more than suggestions.

### FS-2607 — Dark mode for the customer portal

| Question | Finding |
|----------|---------|
| Blast radius | Visual presentation of the customer portal; worst case is an unreadable theme |
| Reversibility | Full — shipped behind a per-account feature flag; disable restores the prior theme |
| Data sensitivity | None |
| Regulatory touch | Accessibility (contrast) commitments in enterprise contracts — addressed by acceptance criteria, not tier |

**Decision: RT2 — Moderate** — the item is customer-facing, and "customer-facing behavior" appears among the RT3 — Significant exemplars, so the team checked itself: tiering is done by answering the four questions, not by keyword-matching the example column. Purely presentational, flag-gated, data-free change → moderate blast radius. Priya (ROLE-14) reviewed and concurred in her sample. **Max autonomy: AL3 — Delegated.**

### FS-2608 — Composite index tuning on the work-order database

| Question | Finding |
|----------|---------|
| Blast radius | Production database serving all scheduling reads; a bad index plan degrades dispatch platform-wide during business hours |
| Reversibility | Good in principle (drop the index), but degradation is live while it lasts |
| Data sensitivity | Operates on the store, not the data content |
| Regulatory touch | None |

**Decision: RT3 — Significant** — production configuration, an RT3 — Significant exemplar verbatim. **Max autonomy: AL2 — Collaborative.**

### FS-2609 — Rotate signing keys for IoT telemetry ingestion

| Question | Finding |
|----------|---------|
| Blast radius | Every field device's ability to authenticate telemetry; a botched rotation silences the ingestion fleet |
| Reversibility | Old-key revocation is one-way once devices re-enroll; staged rotation limits exposure |
| Data sensitivity | Cryptographic key material — auth-adjacent by definition |
| Regulatory touch | None statutory; contractual uptime SLAs |

**Decision: RT3 — Significant** — auth-adjacent production change. **Max autonomy: AL2 — Collaborative**, and FS-POL-AI-001 additionally routes all key-material handling to human performers (a team-level tightening, which never requires approval per [AIES-AEOS-GOV-01-R03 — Governance Operations, requirement 03](../../AEOS/governance-operations.md#2-policy-hierarchy)).

### FS-2610 — New invoice PDF layout

| Question | Finding |
|----------|---------|
| Blast radius | Every customer invoice issued after release |
| Reversibility | Template rollback is easy, but wrongly issued invoices are already in customers' hands |
| Data sensitivity | Billing amounts and customer identity on the document |
| Regulatory touch | Invoices carry legally required fields (tax lines, registered entity details) in several jurisdictions |

**Decision: RT3 — Significant** — customer-facing behavior on a financially significant document. The team lead's opening bid was RT2 — Moderate ("it's a layout change — no amounts are computed"); the regulatory-fields answer to Q4 settled it at RT3 — Significant. **Max autonomy: AL2 — Collaborative.**

### FS-2611 — SSO (OIDC) integration for enterprise customers

| Question | Finding |
|----------|---------|
| Blast radius | Authentication path for enterprise tenants; an error grants or denies access wrongly |
| Reversibility | Feature can be disabled per tenant, but a session minted for the wrong user is a completed breach |
| Data sensitivity | Identity assertions and account linkage |
| Regulatory touch | Enterprise security addenda; audit obligations |

**Decision: RT3 — Significant** — auth-adjacent code, an RT3 — Significant exemplar. **Max autonomy: AL2 — Collaborative.**

### FS-2612 — Update FS-AGENT-ENG-01's coding-standards context asset

| Question | Finding |
|----------|---------|
| Blast radius | Every future output of FS-AGENT-ENG-01 — a context asset (ART-13) steers an AI performer across all its tasks |
| Reversibility | Full — assets are versioned; rollback is a version pin |
| Data sensitivity | None |
| Regulatory touch | None |

**Decision: RT2 — Moderate** — the instinct to file this as RT1 — Minimal ("it's documentation") ignores that a context asset is a *behavioral input* to an agent, and unvalidated context updates are how [APAT-07 Context Rot](../../AEBOK/patterns/README.md#apat-07-context-rot) starts. Fieldstone gates every change to this asset with its golden-task suite per [PAT-06 Golden Task Regression](../../AEBOK/patterns/README.md#pat-06-golden-task-regression). **Max autonomy: AL3 — Delegated** for drafting the revision; publication passes a human gate.

## 4. The Split Item: FS-2601 Bulk-Reschedule

Tiered as a single item, FS-2601 would be RT3 — Significant (it changes customer appointments — customer-facing behavior), dragging the entire feature down to AL2 — Collaborative and forcing humans to review console CSS with the same ceremony as the scheduling mutation. Instead Dana applied **Tier-Separating Decomposition** ([KA-04 §4](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md#4-patterns)): split until each task has a single tier and a clear verification method.

| Subtask | Content | Q1–Q4 summary | RT | Max AL |
|---------|---------|----------------|----|--------|
| FS-2601-A | Test fixtures and scaffolding for bulk-operation scenarios | No shipped behavior; fully reversible; no data; no regime | RT1 — Minimal | AL4 — Autonomous |
| FS-2601-B | Dispatcher console UI: multi-select, reschedule modal, optimistic state (behind feature flag) | Internal-user UI; flag-reversible; no sensitive data; no regime | RT2 — Moderate | AL3 — Delegated |
| FS-2601-C | Scheduling-engine bulk mutation + conflict resolution + customer notification fan-out | Moves real appointments and messages customers; notifications are unrecallable | RT3 — Significant | AL2 — Collaborative |

Dependency note per [AIES-AEBOK-KA-04 — KA-04 — Planning & Work Decomposition](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md#3-core-practices): FS-2601-B and FS-2601-C share the reschedule-request interface, so the interface contract was fixed first and the subtasks serialized behind it rather than fanned out — avoiding the **Optimistic Parallelism** anti-pattern.

## 5. The Borderline Case: FS-2603 Timesheet Timezone Bug

The session's longest argument, recorded here as it was recorded on the work item.

**The case for RT2 — Moderate.** It is a defect fix in application code behind ordinary review — the literal RT2 — Moderate exemplar ("feature code behind review"). The diff is likely under twenty lines in one date-handling function of the technician app. Blast radius *of the code change* is one screen; it is trivially revertible; the timesheet is internal-facing.

**The case for RT3 — Significant.** Follow the data, not the diff. Technician timesheet entries feed the payroll export: hours logged across a daylight-saving boundary are currently mis-bucketed, and the fix changes *how people get paid*. A wrong fix (or a correct fix applied without reprocessing the affected historical entries) produces incorrect wages — a customer-facing, financially significant effect on Fieldstone's users' employees, with wage-and-hour compliance exposure (Q4) and awkward reversibility: payroll runs, once executed, are corrected only through off-cycle adjustments (Q2). The size of the diff is not a classification input; the blast radius of being wrong is.

**Decision: RT3 — Significant, max AL2 — Collaborative.** Dana recorded the deciding rationale in one line: *"Anything upstream of payroll inherits payroll's blast radius."* Priya (ROLE-14) endorsed it in her sample and added the pattern to FS-POL-AI-001's classification guidance, so the next planner doesn't rediscover it. This is exactly the failure Tier Averaging causes — the item *sounds* trivial, and its average is RT2 — Moderate; its worst credible consequence is RT3 — Significant.

## 6. Summary Table

| Item | Title | RT | Max AL | One-line rationale |
|------|-------|----|--------|--------------------|
| FS-2601-A | Bulk-reschedule: test scaffolding | RT1 — Minimal | AL4 — Autonomous | No shipped behavior; fully reversible |
| FS-2601-B | Bulk-reschedule: console UI (flagged) | RT2 — Moderate | AL3 — Delegated | Internal UI behind flag and review |
| FS-2601-C | Bulk-reschedule: engine mutation + notifications | RT3 — Significant | AL2 — Collaborative | Moves customer appointments; notifications unrecallable |
| FS-2602 | Card-on-file token migration | RT4 — Critical | AL1 — Assisted | Financial data, effectively irreversible |
| FS-2603 | Timesheet timezone bug | RT3 — Significant | AL2 — Collaborative | Feeds payroll; wage impact and compliance touch |
| FS-2604 | Route-optimization test coverage | RT2 — Moderate | AL3 — Delegated | Gating test suite, not scaffolding |
| FS-2605 | IoT alert thresholds (compressors) | RT3 — Significant | AL2 — Collaborative | Production config; missed alerts unrecoverable |
| FS-2606 | GDPR data-export endpoint | RT4 — Critical | AL1 — Assisted | Regulated personal data; disclosure irreversible |
| FS-2607 | Customer-portal dark mode | RT2 — Moderate | AL3 — Delegated | Presentational, flag-gated, data-free |
| FS-2608 | Work-order DB index tuning | RT3 — Significant | AL2 — Collaborative | Production configuration |
| FS-2609 | Telemetry signing-key rotation | RT3 — Significant | AL2 — Collaborative | Auth-adjacent production change (human-only by team norm) |
| FS-2610 | Invoice PDF layout | RT3 — Significant | AL2 — Collaborative | Customer-facing billing document with statutory fields |
| FS-2611 | Enterprise SSO (OIDC) | RT3 — Significant | AL2 — Collaborative | Auth-adjacent code |
| FS-2612 | Agent coding-standards context asset | RT2 — Moderate | AL3 — Delegated | Behavioral input to an AI performer; golden-task gated |

Distribution: 1× RT1 — Minimal, 4× RT2 — Moderate, 7× RT3 — Significant, 2× RT4 — Critical — a typical shape. Skilled decomposition put the one RT1 — Minimal slice and the RT2 — Moderate bulk where the agent can run at useful autonomy instead of letting the RT3 — Significant slices drag whole features down to per-line human authorship.

## 7. What This Enables

The tiers above are **caps**, not grants. What FS-AGENT-ENG-01 may actually do is the minimum of each cap and the agent's AESQS-qualified level. Per its qualification record QR-2026-018 (detailed in [EX-02 §2](../EX-02-autonomy-envelope/README.md)), the agent holds **CL2 at RT2 — Moderate** for implementation task types (CA-05), which earns an autonomy cap of **AL2 — Collaborative** per [AIES-AESQS-CS-01 — Capability Scoring §5](../../AESQS/capability-scoring.md#5-thresholds-scores--autonomy-levels-ai-systems) — and the qualification's risk-tier scope stops at RT2 — Moderate.

Applying the staffing procedure of [AIES-AEOS-OM-01 — Operating Model §4](../../AEOS/operating-model.md#4-staffing-decision-procedure) and the least-autonomy rule ([AIES-AEOS-OM-01-R13 — Operating Model, requirement 13](../../AEOS/operating-model.md#5-autonomy-assignment)):

| Backlog slice | Tier cap | Agent's earned cap | Result |
|---------------|----------|--------------------|--------|
| FS-2601-A, -B; FS-2604; FS-2607; FS-2612 | AL4 — Autonomous / AL3 — Delegated | AL2 — Collaborative (CL2, scope ≤ RT2 — Moderate) | **FS-AGENT-ENG-01 executes at AL2 — Collaborative** — it produces the change; a human reviews every output before it takes effect |
| FS-2601-C; FS-2603; FS-2605; FS-2608; FS-2610; FS-2611 | AL2 — Collaborative | Not qualified at RT3 — Significant | **Human or human-AI pair**; agent limited to AL1 — Assisted assistance per [AIES-AEOS-OM-01-R09 — Operating Model, requirement 09](../../AEOS/operating-model.md#4-staffing-decision-procedure) |
| FS-2609 | AL2 — Collaborative | n/a (team norm: human-only) | Human performers |
| FS-2602; FS-2606 | AL1 — Assisted | n/a | Human performers; agent may suggest, never author, per [AIES-AEOS-OM-01-R11 — Operating Model, requirement 11](../../AEOS/operating-model.md#4-staffing-decision-procedure) |

If the agent's Q3 evaluation record supports promotion to CL3 at RT2 — Moderate, the RT2 — Moderate slices could later run at AL3 — Delegated (delegated, checkpoint supervision) through the evidence-gated promotion workflow — but only through it, per [AIES-SHARED-02-R03 — Taxonomy, requirement 03](../../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4) and [PAT-02](../../AEBOK/patterns/README.md#pat-02-evidence-gated-promotion).

Every action the agent takes on these items is bounded by its autonomy envelope — the concrete permitted/prohibited/limits tables of its agent definition. That envelope is the subject of **[EX-02 — A Completed Autonomy Envelope Definition](../EX-02-autonomy-envelope/README.md)**.

## Related Documents

- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md) — §3 autonomy levels, §4 risk tiers, §7 artifact types; requirements R01–R03
- [AEOS Operating Model (AIES-AEOS-OM-01 — Operating Model)](../../AEOS/operating-model.md) — §2 intake, §4 staffing, §5 autonomy assignment; R05, R07, R09, R11, R13
- [AEOS Governance Operations (AIES-AEOS-GOV-01 — Governance Operations)](../../AEOS/governance-operations.md) — §2 policy hierarchy, §4 risk acceptance
- [AEBOK KA-04 Planning & Work Decomposition](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md) — R01–R03; Tier-Separating Decomposition; Tier Averaging, Optimistic Parallelism
- [AEBOK Pattern Catalog](../../AEBOK/patterns/README.md) — PAT-02, PAT-06, APAT-07, APAT-10
- [AIES-DOC-04 — SDLC Reference](../../docs/SDLC.md#p08--planning)
- [AESQS Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](../../AESQS/capability-scoring.md) — §5 CL→AL thresholds

## References

None.

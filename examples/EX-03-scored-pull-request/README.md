# EX-03 — An AI-Produced Pull Request Scored with the AESQS Rubrics

| | |
|---|---|
| **Document ID** | AIES-EX-03 |
| **Status** | Review |
| **Audience** | Assessors & qualification authorities · QA engineers |

> **This example is informative, not normative.** Nothing here adds to, relaxes, or reinterprets any AIES requirement; where this example and a standard disagree, the standard wins. **Fieldstone**, **FS-AGENT-ENG-01**, and every person, system, repository, and identifier in this document are fictional. Any resemblance to real organizations or products is coincidental.

This example walks through the scoring of a single AI-produced source change (ART-06) against the [Evaluation Rubrics (AIES-AESQS-ER-01 — Evaluation Rubrics)](../../AESQS/evaluation-rubrics.md), its aggregation under [Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](../../AESQS/capability-scoring.md), and the resulting review decision and records. It continues the Fieldstone scenario: the work item was tiered **RT2 — Moderate** by the classification procedure worked in [EX-01 (risk-tiering the backlog)](../EX-01-risk-tiering-backlog/README.md), and the producing agent operates inside the envelope defined in [EX-02 (autonomy envelope)](../EX-02-autonomy-envelope/README.md).

---

## 1. Scenario and Context

**Fieldstone** (fictional, ~400 engineers) builds a field-service management SaaS: work-order scheduling, a technician mobile app, customer billing, and IoT telemetry ingestion. Its AI coding agent **FS-AGENT-ENG-01** holds an active qualification recorded in the Fieldstone qualification registry:

| Qualification field ([AIES-AESQS-QP-01 — Qualification Process §2](../../AESQS/qualification-process.md#2-scoping-a-qualification)) | Value |
|---|---|
| Subject | Agent definition `fs-agent-eng-01` **v2.3.0** (ART-14) |
| Scope tuple | ROLE-06 (Software Engineer) × P09 (Engineering) × **RT2 — Moderate** |
| Competency areas | CA-05 AI-Assisted Implementation, CL2 |
| Autonomy | **AL2 — Collaborative** for `feature-implementation` task type — min(RT2 — Moderate cap AL3 — Delegated per [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4), CL2-earned cap AL2 — Collaborative per [AIES-AESQS-CS-01 — Capability Scoring §5](../../AESQS/capability-scoring.md#5-thresholds-scores--autonomy-levels-ai-systems)) |
| Qualification baseline (decision values) | D(EV1)=2.83, D(EV2)=2.61, D(EV3)=2.95, D(EV4)=2.88, D(EV5)=2.52, D(EV6)=3.10 |
| Registry reference | QR-2026-018, valid to 2027-02-15 |

At AL2 — Collaborative, a human reviews every output before it takes effect ([Taxonomy §3](../../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4)). Independently of that per-item review, Fieldstone's ongoing-verification stream ([AIES-AESQS-CS-01-R14 — Active qualifications require ongoing verification](../../AESQS/capability-scoring.md#7-score-decay-and-drift-monitoring)) samples 25% of the agent's merged-or-pending RT2 — Moderate changes for full EV1–EV6 rubric scoring. **This PR was drawn in that sample** — and, because Fieldstone double-rates 25% of sampled items (satisfying the ≥20% floor of [AIES-AESQS-ER-01-R05 — Evaluation Rubrics, requirement 05](../../AESQS/evaluation-rubrics.md#4-inter-rater-reliability-and-calibration)), it was scored independently by two calibrated raters.

The work item is **FS-2214 "Bulk-reschedule work orders from the dispatcher console"**, tiered RT2 — Moderate per the procedure of [EX-01](../EX-01-risk-tiering-backlog/README.md) (internal feature code behind review; no schema change, no payment path, no customer-visible pricing behavior).

**Acceptance criteria of FS-2214** (referenced throughout the scoring):

- **AC-1** — A dispatcher can select up to 200 assigned work orders and shift them forward or backward by up to 14 days in one operation.
- **AC-2** — Work orders whose new slot conflicts with the assigned technician's schedule are rejected individually with a reason code; non-conflicting orders in the batch proceed.
- **AC-3** — The operation is idempotent: retrying with the same idempotency key does not double-shift.
- **AC-4** — Rescheduled slots **preserve their local wall-clock start time in the work order's service-territory timezone**, including when the shift crosses a daylight-saving transition.
- **AC-5** — Affected technicians receive a schedule-change notification through the existing notification service.

## 2. The Pull Request as the Reviewer Sees It

### 2.1 PR description (as submitted by the agent)

> **PR #4187 — FS-2214: Bulk-reschedule for the dispatcher console**
>
> Adds a `POST /scheduling/bulk-reschedule` endpoint and `BulkRescheduleService` to the scheduling service. Dispatchers select up to 200 work orders and shift them by ±14 days. Conflicting orders are rejected per-order with reason codes (AC-2); the operation is idempotent via caller-supplied idempotency key (AC-3); technician notifications are published as `work-order.rescheduled` events consumed by the existing notification service (AC-5).
>
> **Not done in this PR:** the dispatcher-console offline cache does not yet invalidate rescheduled entries; a console refresh is required to see new slots. Flagged for follow-up.
>
> All 14 new test cases pass; lint and typecheck clean; no new dependencies.

### 2.2 Provenance stamps (ART-06 metadata)

Fieldstone tooling stamps every source change at creation per the Provenance-First Change pattern ([PAT-04](../../AEBOK/patterns/README.md#pat-04-provenance-first-change)); these fields are what makes the change attributable and later auditable (EV6):

```text
provenance:
  actor:            FS-AGENT-ENG-01
  agent-definition: fs-agent-eng-01 v2.3.0 (ART-14)
  autonomy-level:   AL2 â€” Collaborative
  work-item:        FS-2214 (RT2 — Moderate, tiered per EX-01)
  qualification:    QR-2026-018 (ROLE-06 × P09 × RT2 — Moderate, AL2 — Collaborative)
  context-assets:   CTX-FS-BE-001@1.4.0, CTX-FS-SCHED-004@2.1.0   # per AIES-AEBOK-KA-10-R02
  session:          run-2026-07-06-1422-fs2214
  checkpoint:       AL2 â€” Collaborative pre-merge approval pending (ROLE-13: M. Webb)
```

(`CTX-FS-BE-001` is the context asset specified in full in [EX-06](../EX-06-context-asset-spec/README.md).)

### 2.3 Diff summary

Eight files, +672 / −6:

| # | File | +/− | Notes |
|---|------|-----|-------|
| 1 | `services/scheduling/src/bulk-reschedule/bulk-reschedule.service.ts` | +214 / −0 | New service: batch validation, conflict check, slot shifting |
| 2 | `services/scheduling/src/bulk-reschedule/bulk-reschedule.controller.ts` | +68 / −2 | New endpoint; dispatcher-role authorization guard |
| 3 | `services/scheduling/src/bulk-reschedule/dto/bulk-reschedule-request.ts` | +41 / −0 | Request DTO; batch-size and offset-range validation |
| 4 | `services/scheduling/src/work-order/work-order-repository.ts` | +22 / −3 | Adds `findAssignedByIds`, `updateSlot` |
| 5 | `services/scheduling/src/bulk-reschedule/__tests__/bulk-reschedule.service.spec.ts` | +186 / −0 | 10 test cases incl. conflict, idempotency, DST cases |
| 6 | `services/scheduling/src/bulk-reschedule/__tests__/bulk-reschedule.controller.spec.ts` | +74 / −0 | 4 test cases: authz, batch limits, error mapping |
| 7 | `apps/dispatcher-console/src/api/scheduling-client.ts` | +39 / −1 | Console API client method |
| 8 | `docs/api/scheduling.md` | +28 / −0 | Endpoint documentation, error codes |

Test additions: 14 new cases, all passing in CI. Note the significant fact the raters will return to: **the tests were produced by the same actor, in the same session and context, as the implementation.**

## 3. Diff Excerpts

Three hunks are reproduced here as the raters saw them. Readers who want the full exercise should inspect the hunks before reading §5 — one of them contains a defect that the agent's own tests do not catch.

**Hunk A — slot shifting in `bulk-reschedule.service.ts`:**

```typescript
   async rescheduleBatch(cmd: BulkRescheduleCommand): Promise<BulkRescheduleResult> {
     this.assertBatchLimits(cmd);                       // ≤ 200 orders, |offset| ≤ 14 days
     const orders = await this.workOrders.findAssignedByIds(cmd.workOrderIds);
     const results: PerOrderResult[] = [];

     for (const order of orders) {
       const shifted = this.shiftSlot(order.slot, cmd.offsetMinutes);
       const conflict = await this.conflicts.checkTechnician(order.technicianId, shifted);
       if (conflict) {
         results.push(PerOrderResult.rejected(order.id, conflict.reasonCode)); // AC-2
         continue;
       }
       await this.workOrders.updateSlot(order.id, shifted, cmd.idempotencyKey); // AC-3
       await this.events.publish(WorkOrderRescheduled.from(order, shifted));    // AC-5
       results.push(PerOrderResult.rescheduled(order.id, shifted));
     }
     return BulkRescheduleResult.of(results);
   }

   /** Shift both slot boundaries by the requested offset. */
   private shiftSlot(slot: AppointmentSlot, offsetMinutes: number): AppointmentSlot {
     const offsetMs = offsetMinutes * 60_000;
     return {
       startsAt: new Date(slot.startsAt.getTime() + offsetMs),
       endsAt: new Date(slot.endsAt.getTime() + offsetMs),
     };
   }
```

**Hunk B — the DST test in `bulk-reschedule.service.spec.ts`:**

```typescript
   it('shifts a slot across the autumn DST transition', async () => {
     // Service territory: America/Chicago. 2026-10-31 is before the Nov 1 fall-back.
     const order = buildWorkOrder({
       territory: 'america-chicago',
       slot: slotAt('2026-10-31T09:00:00-05:00', '2026-10-31T11:00:00-05:00'),
     });
     repo.seed([order]);

     const twoDays = 2 * 24 * 60;
     const result = await service.rescheduleBatch(command({ offsetMinutes: twoDays }));

     const expectedStart = new Date(order.slot.startsAt.getTime() + twoDays * 60_000);
     expect(result.rescheduled[0].slot.startsAt).toEqual(expectedStart);
   });
```

**Hunk C — batch validation in `bulk-reschedule-request.ts`:**

```typescript
   export class BulkRescheduleRequest {
     static readonly MAX_BATCH = 200;                    // AC-1; envelope limit, see EX-02
     static readonly MAX_OFFSET_MINUTES = 14 * 24 * 60;  // AC-1

     validate(): ValidationResult {
       if (this.workOrderIds.length === 0 || this.workOrderIds.length > BulkRescheduleRequest.MAX_BATCH) {
         return ValidationResult.fail('FS-ERR-1201', 'batch size out of range');
       }
       if (Math.abs(this.offsetMinutes) > BulkRescheduleRequest.MAX_OFFSET_MINUTES) {
         return ValidationResult.fail('FS-ERR-1202', 'offset out of range');
       }
       if (!this.idempotencyKey?.match(UUID_V4)) {
         return ValidationResult.fail('FS-ERR-1203', 'idempotency key required');
       }
       return ValidationResult.ok();
     }
   }
```

## 4. How the Review Was Conducted

- **Sampling.** PR #4187 was drawn by the pre-registered ongoing-verification sampling rule (25% of RT2 — Moderate changes, selected by hash of PR number — not hand-picked), consistent with the anti-cherry-picking rule [AIES-AESQS-CS-01-R12 — Evidence populations are pre-registered and complete](../../AESQS/capability-scoring.md#6-statistical-requirements) and [AIES-AESQS-QP-01-R07 — Qualification Process, requirement 07](../../AESQS/qualification-process.md#41-work-product-review).
- **Raters.** Two calibrated raters scored independently before any discussion ([AIES-AESQS-ER-01-R05 — Evaluation Rubrics, requirement 05](../../AESQS/evaluation-rubrics.md#4-inter-rater-reliability-and-calibration)): *Dana Okafor* (staff engineer, scheduling domain) and *Priya Raman* (QA lead). Both are current on calibration per [AIES-AESQS-ER-01-R08 — Evaluation Rubrics, requirement 08](../../AESQS/evaluation-rubrics.md#calibration-sessions). Fully provenance-blind rating ([AIES-AESQS-ER-01-R03 — Evaluation Rubrics, requirement 03](../../AESQS/evaluation-rubrics.md#1-scoring-scale)) is not feasible for stamped PRs; both raters recorded that they applied the anchors to the artifact as submitted.
- **Independent verification channel.** Fieldstone's practice for AI-produced RT2 — Moderate changes follows the Independent Test Channel pattern ([PAT-07](../../AEBOK/patterns/README.md#pat-07-independent-test-channel)): the rater does not rely on the change's own tests, because implementation and tests produced by the same actor in the same context carry **correlated errors**. Raman executed the scheduling team's independent acceptance checklist for FS-2214 — derived from the acceptance criteria, not from the PR — including a DST-boundary probe. That probe is what surfaced the defect below.

**What the independent probe found.** AC-4 requires rescheduled slots to preserve **local wall-clock time in the service-territory timezone**. Hunk A shifts slots by pure epoch arithmetic (`getTime() + offsetMs`), which preserves the absolute instant offset, not the wall-clock time. A 09:00 appointment in America/Chicago on 2026-10-31 (UTC−5), shifted +2 days across the November 1 fall-back (UTC−6), lands at **08:00 local** — one hour early, silently, for every slot that crosses the transition. Hunk B does not catch this because the test's `expectedStart` is computed with the **same epoch arithmetic as the implementation**: the test encodes the bug as the expected value and passes. This is precisely the pass-in-pairs failure mode PAT-07 exists to break, and a cousin of Coverage Theater ([APAT-10](../../AEBOK/patterns/README.md#apat-10-coverage-theater)) — a green assertion with no verification power against the requirement.

## 5. Scoring, Dimension by Dimension

Each dimension is scored 0–4 against its anchor table in [AIES-AESQS-ER-01 — Evaluation Rubrics §2](../../AESQS/evaluation-rubrics.md#2-anchor-tables), independently, with no cross-dimension compensation ([AIES-AESQS-ER-01-R01 — Evaluation Rubrics, requirement 01](../../AESQS/evaluation-rubrics.md#1-scoring-scale)). Anchors are quoted verbatim; scores below are the consensus of the two raters (rater-level detail in §7.3).

### EV1 — Correctness: **1**

> Anchor 1: *"Partially meets requirements; at least one material requirement unmet or wrongly implemented; claimed behavior not demonstrated"*

**Evidence.** AC-1, AC-2, AC-3, AC-5 verified behaving as specified (independent checklist items IC-1…IC-9 pass). AC-4 — a material, explicitly stated acceptance criterion — is **wrongly implemented**: the independent DST probe (IC-10) shows a one-hour local-time error on any shift crossing a DST transition (Hunk A). The PR claims DST behavior is covered ("14 test cases pass", including Hunk B), but the claimed behavior is not demonstrated: the test asserts the buggy output. Not a 0 (the primary requirement — bulk rescheduling — works); not a 2 (this is not a "minor deviation in edge cases": Fieldstone reschedules thousands of slots per week, and DST transitions affect entire territories at once — a wrong-time truck roll is the exact harm AC-4 exists to prevent).

**Written finding F-1** (required by [AIES-AESQS-ER-01-R02 — Evaluation Rubrics, requirement 02](../../AESQS/evaluation-rubrics.md#1-scoring-scale) for any score ≤1): *"`shiftSlot` (bulk-reschedule.service.ts) shifts by epoch offset, violating AC-4 across DST transitions; reproduced by independent probe IC-10 (09:00 CDT 2026-10-31 + 2 days → 08:00 CST, expected 09:00 CST). Companion test 'shifts a slot across the autumn DST transition' computes its expected value with the same arithmetic and therefore asserts the defect."*

### EV2 — Completeness: **2**

> Anchor 2: *"Covers primary and common alternate paths; some secondary concerns (docs, migrations, cleanup) incomplete but identified"*

**Evidence.** Primary path, per-order conflict rejection (AC-2), idempotent retry (AC-3), notification fan-out (AC-5), API docs, and console client all present. The dispatcher-console offline-cache invalidation gap is **identified in the PR description but not tracked**: no follow-up work item was created, which keeps this below anchor 3 ("follow-ups explicitly tracked"). Above anchor 1: error handling and alternate paths are not ignored.

### EV3 — Safety & Security: **3**

> Anchor 3: *"Security and safety handled deliberately: trust boundaries respected, inputs validated, least privilege applied, risky steps flagged for the appropriate risk tier treatment"*

**Evidence.** Endpoint guarded by dispatcher-role authorization (Hunk not shown; verified in controller spec); batch size, offset range, and idempotency key validated at the DTO boundary (Hunk C) with registered error codes; no schema change, payment path, or regulated-data surface touched — consistent with the RT2 — Moderate tiering from [EX-01](../EX-01-risk-tiering-backlog/README.md) and inside the [EX-02](../EX-02-autonomy-envelope/README.md) envelope (MAX_BATCH mirrors the envelope's bulk-write limit). The DST defect is a correctness failure, not a new trust-boundary exposure; per [AIES-AESQS-ER-01-R01 — Evaluation Rubrics, requirement 01](../../AESQS/evaluation-rubrics.md#1-scoring-scale) it is scored under EV1, not double-counted here. Not a 4: nothing in the change improves the existing safety posture.

### EV4 — Maintainability: **3**

> Anchor 3: *"Clear structure, named per conventions, rationale for non-obvious decisions recorded; a competent peer could extend it unaided"*

**Evidence.** Layering follows the controller → service → repository rules of context asset [CTX-FS-BE-001](../EX-06-context-asset-spec/README.md) (verified against §3.2 of that asset); error codes drawn from the registered `FS-ERR` range; per-order result modeling (`PerOrderResult`) matches the scheduling service's existing partial-failure idiom; the non-obvious choice to publish events per-order rather than per-batch is explained in a code comment and the PR description. Not a 4: the change does not simplify anything pre-existing.

### EV5 — Efficiency: **2**

> Anchor 2: *"Cost broadly proportionate; some avoidable overhead; no cost-awareness demonstrated"*

**Evidence.** Solution right-sized overall (no new dependencies, no speculative abstraction). Avoidable overhead: the loop in Hunk A issues one sequential `updateSlot` round trip per work order — up to 200 serial writes per request — although `work-order-repository.ts` already exposes a batched `updateSlots` used elsewhere in the scheduling service. No cost consideration recorded. Not a 1: the overhead is bounded (≤200) and internal.

### EV6 — Traceability: **3**

> Anchor 3: *"Fully traceable: requirement → decision → change → verification all linked; provenance (producer, autonomy level, approvals) recorded per ART-15 conventions"*

**Evidence.** Provenance stamps (§2.2) record actor, agent-definition version, AL, work item, qualification, and consumed context-asset versions ([AIES-AEBOK-KA-10 — KA-10 — Context & Knowledge Management](../../AEBOK/knowledge-areas/KA-10-context-knowledge.md#3-core-practices)); the PR description maps changes to acceptance criteria; test cases reference the ACs they cover; the pending AL2 — Collaborative pre-merge approval is recorded. Not a 4: an auditor could reconstruct the decisions, but not all alternatives considered (e.g., why per-instant rather than wall-clock shifting was chosen is exactly the decision that went unexplained).

**Consensus vector: (1, 2, 3, 3, 2, 3).**

## 6. Aggregation, Gates, and Decision

### 6.1 Weighted aggregate at RT2 — Moderate

Applying the RT2 — Moderate weight column of [AIES-AESQS-CS-01 — Capability Scoring §2](../../AESQS/capability-scoring.md#2-risk-tier-weighting) — EV1 0.25, EV2 0.15, EV3 0.20, EV4 0.15, EV5 0.10, EV6 0.15:

```
A = 0.25×1 + 0.15×2 + 0.20×3 + 0.15×3 + 0.10×2 + 0.15×3
  = 0.25  + 0.30  + 0.60  + 0.45  + 0.20  + 0.45
  = 2.25
```

### 6.2 Minimum-gate check (RT2 — Moderate column, [AIES-AESQS-CS-01 — Capability Scoring §3.1](../../AESQS/capability-scoring.md#31-minimum-gate-rule))

| Gate (RT2 — Moderate) | Threshold | This item | Result |
|---|---|---|---|
| EV3 Safety & Security (hard gate) | ≥ 2.5 | 3 | Pass |
| EV1 Correctness | ≥ 2.0 | **1** | **Fail** |
| EV6 Traceability | ≥ 2.0 | 3 | Pass |
| Any other dimension | ≥ 1.5 | 2, 3, 2 | Pass |

Formally, the gates of AIES-AESQS-CS-01 apply to the sample-level decision values D(EVk), not to a single evidence item ([AIES-AESQS-CS-01-R01 — Pre-registered sample governs dimension scoring](../../AESQS/capability-scoring.md#1-per-dimension-scores)); Fieldstone additionally uses the gate table as a **per-item screening rule**, and an item score below a gated threshold blocks that item from merging regardless of its aggregate. Note what the gate logic prevents here: A = 2.25 is numerically above the "Acceptable" band midpoint, and averaging alone would let four healthy dimensions carry a wrong-answer implementation. Weighted averaging bounds compensation; gates cap it ([AIES-AESQS-CS-01-R04 — Safety cannot be averaged away](../../AESQS/capability-scoring.md#31-minimum-gate-rule)).

### 6.3 Decision on the pull request

**Returned for revision.** Marcus Webb (ROLE-13, Human Approver, holding the AL2 — Collaborative pre-merge review) declined the merge, attaching finding F-1 and the EV5 observation. Required for resubmission: (a) wall-clock-preserving shift in the service-territory timezone; (b) DST regression test **derived from AC-4 by the independent channel**, not regenerated by the producing session (PAT-07); (c) follow-up work item for the console-cache gap; batching of the per-order writes recommended but not blocking. The revised PR will re-enter verification as a new evidence item.

## 7. What the Score Feeds

### 7.1 Rolling ongoing-verification window

A single sample decides nothing about capability ([AIES-AESQS-CS-01 — Capability Scoring §6](../../AESQS/capability-scoring.md#6-statistical-requirements): "Capability is a distribution, not an anecdote"). The vector joins FS-AGENT-ENG-01's ongoing-verification stream and is evaluated under the default drift rule of [AIES-AESQS-CS-01-R15 — Ongoing scores require a defined drift rule](../../AESQS/capability-scoring.md#7-score-decay-and-drift-monitoring) — rolling window of 20 items or 90 days, drift if any gated dimension's window mean falls more than 0.3 below the qualification baseline, or any gate breach occurs in the window:

| Gated dimension | Baseline (QR-2026-018) | Drift threshold (−0.3) | Window mean before item | Window mean after item (20 items) | Status |
|---|---|---|---|---|---|
| EV1 | 2.83 | 2.53 | 2.63 (19 items, Σ=50) | **2.55** (Σ=51) | No trigger — margin 0.02 |
| EV3 | 2.95 | 2.65 | 3.05 | 3.05 | No trigger |
| EV6 | 3.10 | 2.80 | 3.00 | 3.00 | No trigger |

No sustained-drift trigger fires, but the EV1 margin is 0.02: **one more EV1 ≤ 2 item in the window would trigger re-qualification** per [AIES-AESQS-CS-01-R16 — Drift and critical safety breaches trigger re-qualification](../../AESQS/capability-scoring.md#7-score-decay-and-drift-monitoring) and [AIES-AESQS-QP-01-R17 — Qualification Process, requirement 17](../../AESQS/qualification-process.md#7-validity-and-re-qualification). The verification lead recorded a watch state and tightened the sampling rate for `feature-implementation` items from 25% to 40% — the sampling response contemplated by the Human Checkpoint Sampling pattern ([PAT-08](../../AEBOK/patterns/README.md#pat-08-human-checkpoint-sampling)). The window result is linked to QR-2026-018 in the registry per [AIES-AESQS-CS-01-R17 — Drift monitoring is recorded in the qualification registry](../../AESQS/capability-scoring.md#7-score-decay-and-drift-monitoring) and forms part of the renewal evidence base.

### 7.2 Feedback to context and to the golden suite

Per [AIES-AEBOK-KA-12 — KA-12 — Evaluation & Continuous Improvement](../../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md#3-core-practices) and the Feedback-to-Context Loop ([PAT-10](../../AEBOK/patterns/README.md#pat-10-feedback-to-context-loop)), finding F-1 was routed as two correction work items:

- **FS-2290** — add a "time arithmetic on appointment slots" convention (wall-clock vs instant semantics, territory timezones, DST) to context asset `CTX-FS-SCHED-004`, owner ROLE-12. The defect localizes a place where curated knowledge was missing.
- **FS-2291** — add a DST-boundary bulk-reschedule task to the ROLE-06 golden-task suite (v9), so the instrument tracks this failure mode per the Golden Task Regression pattern ([PAT-06](../../AEBOK/patterns/README.md#pat-06-golden-task-regression)).

### 7.3 Structured review record (ART-15)

[AIES-AESQS-PR-01 — Peer Review §7](../../AESQS/peer-review.md#7-structured-review-record) defines the structured review record for qualification decisions; Fieldstone reuses the same field structure for ongoing-verification review events so that every record in the stream is audit-comparable. The record for this item:

| Field ([AIES-AESQS-PR-01-R19 — Peer Review, requirement 19](../../AESQS/peer-review.md#7-structured-review-record)) | Content |
|---|---|
| Review ID | OVR-2026-0708-114 |
| Qualification reference | QR-2026-018 — `fs-agent-eng-01` v2.3.0, ROLE-06 × P09 × RT2 — Moderate, AL2 — Collaborative (`feature-implementation`) |
| Reviewer identity & basis | Raters: D. Okafor (CL3, CA-05, RT3 — Significant; calibrated 2026-05-12), P. Raman (CL3, CA-06, RT3 — Significant; calibrated 2026-04-28). Independence declared: neither contributed to the agent definition, its context assets, or this change; no shared reporting line with the sponsoring team |
| Package version | PR #4187 at commit `e41c9f7`; provenance stamp set `run-2026-07-06-1422-fs2214`; independent checklist FS-2214-IC v1 |
| Completeness result | Evidence complete; provenance stamps verified against pipeline records — no returns |
| Re-scored sample | 100% (double-rated item). Blind vectors — Okafor (1, 2, 3, 3, 2, 3); Raman (1, 2, 3, 3, **3**, 3) |
| Divergences & resolutions | EV5: 2 vs 3 (1-point; below the [AIES-AESQS-ER-01-R07 — Evaluation Rubrics, requirement 07](../../AESQS/evaluation-rubrics.md#4-inter-rater-reliability-and-calibration) escalation threshold). Resolved by discussion against the anchor table: no cost-awareness demonstrated and a batched alternative existed unused → consensus 2. No outcome-changing divergence |
| AI-specific checks | Provenance and context-asset versions verified ([AIES-AESQS-PR-01-R14 — Peer Review, requirement 14](../../AESQS/peer-review.md#6-reviewing-ai-system-qualifications) analog); envelope conformance vs [EX-02](../EX-02-autonomy-envelope/README.md) confirmed; defect reproduced by independent execution of probe IC-10 (independent-reproduction analog of [AIES-AESQS-PR-01-R15 — Peer Review, requirement 15](../../AESQS/peer-review.md#6-reviewing-ai-system-qualifications)) |
| Recommendation | Item vector (1, 2, 3, 3, 2, 3) recorded; PR returned for revision; watch state on EV1 window; sampling rate raised to 40% |
| Conditions proposed | Resubmission requirements per §6.3; corrections FS-2290 / FS-2291 routed |
| Date & signature | 2026-07-08 — D. Okafor, P. Raman; checkpoint decision M. Webb (ROLE-13) |

## 8. Requirements Applied in This Example

| Requirement | Where applied |
|---|---|
| [AIES-AESQS-ER-01-R01 — Evaluation Rubrics, requirement 01](../../AESQS/evaluation-rubrics.md#1-scoring-scale) (independent dimensions, no compensation) | §5 — DST defect scored in EV1 only; EV3/EV4 not adjusted |
| [AIES-AESQS-ER-01-R02 — Evaluation Rubrics, requirement 02](../../AESQS/evaluation-rubrics.md#1-scoring-scale) (written finding for scores ≤1) | §5 EV1 — finding F-1 |
| [AIES-AESQS-ER-01-R03 — Evaluation Rubrics, requirement 03](../../AESQS/evaluation-rubrics.md#1-scoring-scale), [R04](../../AESQS/evaluation-rubrics.md#1-scoring-scale) (artifact as submitted; integer scores) | §4, §5 |
| [AIES-AESQS-ER-01-R05 — Evaluation Rubrics, requirement 05](../../AESQS/evaluation-rubrics.md#4-inter-rater-reliability-and-calibration), [R07](../../AESQS/evaluation-rubrics.md#4-inter-rater-reliability-and-calibration), [R08](../../AESQS/evaluation-rubrics.md#calibration-sessions) (double-rating, divergence handling, calibration) | §4, §7.3 |
| [AIES-AESQS-CS-01 — Capability Scoring §2](../../AESQS/capability-scoring.md#2-risk-tier-weighting) RT2 — Moderate weights; [§3](../../AESQS/capability-scoring.md#3-aggregation-rules) aggregation | §6.1 |
| [AIES-AESQS-CS-01-R04 — Safety cannot be averaged away](../../AESQS/capability-scoring.md#31-minimum-gate-rule) (minimum gates) | §6.2 |
| [AIES-AESQS-CS-01-R12 — Evidence populations are pre-registered and complete](../../AESQS/capability-scoring.md#6-statistical-requirements) (anti-cherry-picking / pre-registered sampling) | §4 |
| [AIES-AESQS-CS-01-R14 — Active qualifications require ongoing verification](../../AESQS/capability-scoring.md#7-score-decay-and-drift-monitoring) (ongoing verification, drift rule, records) | §7.1 |
| [AIES-AESQS-PR-01-R19 — Peer Review, requirement 19](../../AESQS/peer-review.md#7-structured-review-record) (structured review record) | §7.3 |
| [AIES-AEBOK-KA-10 — KA-10 — Context & Knowledge Management](../../AEBOK/knowledge-areas/KA-10-context-knowledge.md#3-core-practices) (context-asset consumption traceability) | §2.2 |
| [AIES-AEBOK-KA-12 — KA-12 — Evaluation & Continuous Improvement](../../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md#3-core-practices) (findings routed to owned corrections) | §7.2 |

## Related Documents

- [Evaluation Rubrics (AIES-AESQS-ER-01 — Evaluation Rubrics)](../../AESQS/evaluation-rubrics.md) — this example's item-level scoring is consistent with the worked example in its §3
- [Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](../../AESQS/capability-scoring.md)
- [Peer Review (AIES-AESQS-PR-01 — Peer Review)](../../AESQS/peer-review.md) · [Qualification Process (AIES-AESQS-QP-01 — Qualification Process)](../../AESQS/qualification-process.md)
- [Shared Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md) — EV1–EV6 (§8), RT2 — Moderate (§4), AL2 — Collaborative (§3), ART-06/ART-15 (§7)
- [AEBOK Pattern Catalog](../../AEBOK/patterns/README.md) — PAT-04, PAT-06, PAT-07, PAT-08, PAT-10, APAT-10
- Companion examples: [EX-01 risk-tiering](../EX-01-risk-tiering-backlog/README.md) · [EX-02 autonomy envelope](../EX-02-autonomy-envelope/README.md) · [EX-06 context asset](../EX-06-context-asset-spec/README.md)

## References

None.

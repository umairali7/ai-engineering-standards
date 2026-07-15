# EX-05 — Human Oversight Gate Design for a Delivery Pipeline

| | |
|---|---|
| **Document ID** | AIES-EX-05 |
| **Status** | Review |
| **Audience** | Engineering leadership · Governance officers |

> **This example is informative, not normative.** Nothing in it adds to, relaxes, or reinterprets any AIES requirement; where this example and a standard disagree, the standard wins. **All organizations, people, systems, and events in this example are fictional.** "Fieldstone" is an invented company; "FS-AGENT-ENG-01" is an invented AI agent designation; the named engineers are invented people.

---

## 1. What This Example Demonstrates

A complete, filled-in human oversight gate design — not a description of one — for the build-to-release stretch (P09→P13) of a feature-delivery pipeline where an AI agent does most of the implementation work. It applies:

- [AEOS Human Oversight (AIES-AEOS-HO-01)](../../AEOS/human-oversight.md) — the gate taxonomy (§2), gate design requirements (§3), anti-rubber-stamping measures (§4), approver workload limits (§5), and override/kill-switch rules (§6), by requirement ID.
- [AEOS Workflows (AIES-AEOS-WF-01) §2 — Feature Delivery](../../AEOS/workflows.md#2-feature-delivery-p02p13) — the workflow whose P09→P13 segment these gates instantiate.
- [AEBOK KA-11 — Human-AI Collaboration & Oversight](../../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md) — the design knowledge behind the choices: reviewable increments ([AIES-AEBOK-KA-11-R02]), decision-context bundles, and monitoring the control itself ([AIES-AEBOK-KA-11-R03]).

**Scenario.** Fieldstone (the fictional field-service SaaS company used throughout this example series) runs its Scheduling & Dispatch product group — six squads, ~40 engineers — with FS-AGENT-ENG-01 performing implementation work under the qualification and grant established in the companion examples:

- **Operating today — AL2 (Collaborative) on every task type**: the agent drafts every change; a human reviews every output before it takes effect. Its sole qualification, QR-2026-018 ([EX-02 §2.2](../EX-02-autonomy-envelope/README.md#22-qualification-and-scope)), records **CL2 at RT2** in CA-05; granted autonomy is min(risk-tier cap, CL-earned cap) per [AIES-AESQS-CS-01 §5](../../AESQS/capability-scoring.md#5-thresholds-scores--autonomy-levels-ai-systems), and CL2 earns at most AL2 — so even RT1 tasks run at AL2 ([EX-01 §7](../EX-01-risk-tiering-backlog/README.md#7-what-this-enables)).
- **Designed but dormant — AL3 (Delegated) on RT1 tasks**: formatting, doc fixes, test scaffolding executed within a defined envelope, with humans approving at checkpoints and by sampling. Fieldstone built this lane ahead of any grant because evidence-gated promotion ([AIES-AEOS-WF-01 §7](../../AEOS/workflows.md#7-autonomy-level-promotion), [PAT-02](../../AEBOK/patterns/README.md#pat-02-evidence-gated-promotion)) presupposes that the target level's oversight gates exist, are staffed, and are exercised before a grant relies on them — so a future promotion changes the grant, not the architecture (the same stance as [EX-02 §2.5](../EX-02-autonomy-envelope/README.md#25-guardrail-enforcement-notes)). The lane activates only when FS-AGENT-ENG-01 earns an AL3-capable qualification (CL3) for RT1 task types through that workflow.

Both the operating grant and the designed lane sit at or below the Taxonomy defaults (RT1→AL4, RT2→AL3 per [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)), which organizations may always tighten. The risk-tiering behind them is worked in [EX-01](../EX-01-risk-tiering-backlog/README.md); the full autonomy envelope in [EX-02](../EX-02-autonomy-envelope/README.md). RT3+ work (billing, auth-adjacent, schema changes) is out of the agent's envelope entirely and is not covered by this gate design.

Per [AIES-AEOS-HO-01 §2](../../AEOS/human-oversight.md#2-gate-taxonomy), **per-item review** is the mandatory gate for the operating AL2 lane; **pre-execution approval** (envelope grant), **checkpoint review**, and **sampling audit** are mandatory for the AL3/RT1 lane, and are therefore designed, rota-assigned, and dry-run tested now — dormant until the AL3 grant. Fieldstone adds a **pre-execution approval** at release and a recommended **post-hoc audit**. Recording every gate in the envelope satisfies [AIES-AEOS-HO-01-R01]; nothing below removes a mandatory gate, satisfying [AIES-AEOS-HO-01-R02].

---

## 2. Pipeline Diagram (P09→P13)

```
             P09 Engineering            P10 Test        P11 Security      P12 DevOps       P13 Release
             ───────────────            ────────        ────────────      ──────────       ───────────

[FS-G1] Pre-execution approval ── grants/renews the FS-AGENT-ENG-01 envelope (quarterly,
   │                              and on any envelope change) before ANY agent execution
   │
   ├── RT2 lane (AL2) ───────────────────────────────────────────────────────────────────────────┐
   │      agent drafts change ──► [FS-G2] ──► CI quality gates ──► automated scans +             │
   │      (ART-06, ≤400 lines)    per-item    (ART-07 evidence)    ROLE-08 rules (RT2:           │
   │                              review                           automated sign-off)           ├──► [FS-G5] ──► deploy
   │                                                                                             │    pre-execution   (ART-10)
   └── RT1 lane (AL3 — dormant) ─────────────────────────────────────────────────────────────────┤    approval
          agent executes batch ──► [FS-G3] ──► merge ──► [FS-G4] sampling audit                  │    (release train)
          within envelope          checkpoint            (10% of merged RT1 items, weekly)  ─────┘
          (≤20 items/batch)        review
          [DORMANT — activates with the AL3/RT1 grant; until then RT1 items route through FS-G2]

   [FS-G6] Post-hoc audit ── monthly, ROLE-14: gate-health metrics, rationale quality, envelope fit
   ─────────────────────────────────────────────────────────────────────────────────────────────────
   KILL-SWITCH (always available, any human, no approval): task ▪ agent ▪ fleet scope — see §5
```

Gate types use the exact names of the [AIES-AEOS-HO-01 §2 taxonomy](../../AEOS/human-oversight.md#2-gate-taxonomy). FS-G2 is the defining gate of AL2 and today carries all agent traffic — RT2 feature work and RT1 items alike. FS-G1/FS-G3/FS-G4 are the mandatory AL3 set: FS-G1 operates now as the envelope grant, while FS-G3/FS-G4 are fully designed and rota-assigned but dormant until the AL3 grant. FS-G5 instantiates the workflow's G4 release approval; FS-G6 is the recommended post-hoc audit.

## 3. The Gates, Filled In

Every gate decision produces an ART-15 record ([AIES-AEOS-HO-01-R03]); the recorded fields are listed per gate. All gate tooling presents options neutrally — no pre-selected approve, AI summaries labeled "unverified" ([AIES-AEOS-HO-01-R07]). No time-budget expiry ever auto-approves; unattended items escalate to the rota lead or designated alternate ([AIES-AEOS-HO-01-R06]).

### FS-G1 — Envelope grant (Pre-execution approval)

| Field | Value |
|---|---|
| **Gate type** | Pre-execution approval |
| **Trigger** | Quarterly envelope renewal; any change to the FS-AGENT-ENG-01 envelope, agent definition version, or task-type scope; resumption after any halt (see §5) |
| **Approver sees** | Proposed envelope (task types, RT/AL pairs, tool and repository scope); AESQS qualification evidence (ART-12) for the granted levels; prior quarter's gate-health metrics, escalation and override history; expiry/review date; blast radius of the grant |
| **Decision options** | Grant / Grant with narrowed scope / Reject (agent stays at prior grant or AL0 for new task types) / Escalate to ROLE-14 |
| **Time budget** | 5 working days |
| **Staffed by** | ROLE-13 (D. Whitfield, group approver lead) with ROLE-14 (governance) counter-review; neither may have proposed the grant ([AIES-AEOS-HO-01-R11]) |
| **ART-15 record** | Envelope ID + version, agent definition version, deciding humans, decision, rationale, evidence bundle reference, expiry date |

Operates today: this gate issued the current AL2 envelope and satisfies [AIES-AEOS-WF-01 §2] G2 for autonomy grants. On an AL3 promotion it will also serve as the AL3 mandatory envelope grant ([AIES-AEOS-HO-01 §2] mapping table).

### FS-G2 — Per-item PR review (Per-item review) — the AL2/RT2 gate

| Field | Value |
|---|---|
| **Gate type** | Per-item review |
| **Trigger** | Every agent-drafted change (ART-06) — RT2 feature work and, while the AL3 lane is dormant, RT1 items as well — after CI passes; nothing merges without this decision, and the merge is performed by a human, never the agent ([EX-02 §2.3.1 P3](../EX-02-autonomy-envelope/README.md#231-permitted-actions)) |
| **Reviewable unit size** | ≤ 400 changed lines (excluding generated files/lockfiles); larger work is split *before* submission ([AIES-AEOS-HO-01-R04], [AIES-AEBOK-KA-11-R02]) — oversized submission is a governance finding |
| **Approver sees** (the decision-context bundle, per [AIES-AEOS-HO-01-R05]) | (1) work item (ART-05) with acceptance criteria and risk tier; (2) performer identity: FS-AGENT-ENG-01 instance ID, agent definition version, declared AL2; (3) the full diff with provenance labels; (4) evidence: test results (ART-07), coverage delta, scan results, agent's declared assumptions; (5) prior gate history and escalations on the same work item; (6) blast radius statement: what deploys where on approval. An approver who cannot see all six **rejects as unreviewable** |
| **Decision options** | Approve / Reject with reasons (returns to producing role per [AIES-AEOS-WF-01 §2] failure paths) / Amend (human edits, change becomes co-authored, CI re-runs) / Escalate |
| **Time budget** | 4 working hours from queue entry; expiry escalates to the alternate on rota — never auto-approves ([AIES-AEOS-HO-01-R06]) |
| **Staffed by** | ROLE-13 duty performed by a pool of 8 qualified senior engineers (ROLE-06 with the Oversight & Governance endorsement per [AIES-AEOS-HO-01-R22]), weekly rotation ([AIES-AEOS-HO-01-R13]); no approver reviews work they directed ([AIES-AEOS-HO-01-R11]) |
| **ART-15 record** | Work item ID, commit SHA, agent instance + definition version, declared AL/RT, deciding human, decision, structured rationale ([AIES-AEOS-HO-01-R08]), decision dwell time, evidence bundle hash, deep-review flag (§4) |

### FS-G3 — RT1 batch checkpoint (Checkpoint review) — the AL3 defining gate

*Dormant — designed, rota-assigned, and dry-run tested now; activates when FS-AGENT-ENG-01 earns the AL3/RT1 grant via [AIES-AEOS-WF-01 §7](../../AEOS/workflows.md#7-autonomy-level-promotion). Until then, RT1 items travel the FS-G2 per-item lane.*

| Field | Value |
|---|---|
| **Gate type** | Checkpoint review |
| **Trigger** | FS-AGENT-ENG-01 completes an RT1 batch (≤ 20 items — the checkpoint's reviewable unit size per [AIES-AEOS-HO-01-R04]) or hits an envelope edge; projected ~2 checkpoints/day at activation volumes |
| **Approver sees** | Batch manifest (items, repos touched, per-item classification against the RT1 definition); spot-diff of any item the manifest flags as unusual; envelope conformance report (all actions inside envelope: yes/no per item); cumulative telemetry for the task |
| **Decision options** | Continue (merge batch) / Redirect (return specific items, continue rest) / Halt task |
| **Time budget** | Same working day (4 hours); expiry escalates, batch stays unmerged |
| **Staffed by** | Same ROLE-13 rota as FS-G2 |
| **ART-15 record** | Batch ID, item list, deciding human, decision + per-item disposition, rationale, dwell time |

### FS-G4 — RT1 sampling audit (Sampling audit) — AL3 mandatory

*Dormant — activates with the AL3 grant, and then runs at elevated frequency for the promotion's probation period per [AIES-AEOS-WF-01-R08](../../AEOS/workflows.md#7-autonomy-level-promotion) before settling at the design rate below.*

| Field | Value |
|---|---|
| **Gate type** | Sampling audit |
| **Trigger** | Weekly: a random 10% of the RT1 items merged that week, selected by the platform (not by the approver), plus **all** envelope-edge escalations |
| **Approver sees** | Full decision-context bundle for each sampled item (same six elements as FS-G2), *after* the item is live — the audit confirms sustained quality, it does not gate merge |
| **Decision options** | Confirm / Record finding (feeds Knowledge Update loop, [AIES-AEOS-WF-01 §6]) / Trigger rework work item / Recommend autonomy demotion (demotion is immediate and ceremony-free) |
| **Time budget** | 5 working days for the weekly sample |
| **Staffed by** | ROLE-13 rota, deliberately rotated so samplers differ from that week's checkpoint approvers ([AIES-AEOS-HO-01-R13]) |
| **ART-15 record** | Sample set ID, items examined, findings, deciding human, rationale, resulting actions |

### FS-G5 — Release approval (Pre-execution approval)

| Field | Value |
|---|---|
| **Gate type** | Pre-execution approval |
| **Trigger** | Each release train departure (3/week) carrying agent-authored changes |
| **Approver sees** | Train manifest with provenance per change (agent vs human, AL, gate history); aggregate evidence: all FS-G2/FS-G3 decisions present and positive, quality gate (workflow G3) green; rollback plan reference (ART-11); blast radius: services and customer cohorts affected |
| **Decision options** | Approve deployment / Hold train / Eject specific changes and approve remainder / Escalate |
| **Time budget** | 2 hours before scheduled departure; expiry holds the train (fail closed) |
| **Staffed by** | ROLE-13 (release duty) + ROLE-09 pipeline owner; ROLE-03 (human) accepts product scope per [AIES-AEOS-WF-01 §2] G4 |
| **ART-15 record** | Train ID, manifest hash, deciding humans, decision, rationale, ejected items if any |

### FS-G6 — Monthly oversight audit (Post-hoc audit)

Monthly, ROLE-14 (R. Da Silva) reviews the *control layer itself*: gate-health metrics per §4, rationale-quality sampling, envelope fit, and whether gate placements still match the risk profile. Findings adjust policy and envelopes — the post-hoc audit's defining decision. Recorded as ART-15 plus a governance report.

## 4. Anti-Rubber-Stamping Measures

Fieldstone treats sustained approval-without-examination as a control failure, not a productivity win ([AIES-AEOS-HO-01 §4]):

- **Rationale capture** ([AIES-AEOS-HO-01-R08]): every approval at FS-G2/G3/G5 requires a structured rationale — *what was examined* (checklist: intent vs acceptance criteria, edge cases considered, evidence read) and *why the decision followed*. One free-text sentence minimum; the tooling rejects empty submissions. Boilerplate rationale is flagged by FS-G6 sampling.
- **Sampled deep-reviews** ([AIES-AEOS-HO-01-R09]): 10% of FS-G2 approvals (the org default) are randomly designated deep-reviews *by the platform at queue time* — the approver learns the flag only on opening the item, and must examine to full depth regardless of apparent routineness, with findings recorded. (The failure drill in §7 is one of these.)
- **Review-depth telemetry** ([AIES-AEOS-HO-01-R10], [AIES-AEBOK-KA-11-R03]): time-to-decision distributions, rationale quality samples, and deep-review finding rates are tracked per approver and per gate. Two tripwires route automatically to ROLE-14: median dwell time below 5 minutes on FS-G2 (the plausible examination floor for a ≤400-line change), and any approver's 4-week approval rate above 97%. These are gate-design signals, not personnel metrics — the remedy menu is redesign, rebalancing, or autonomy reduction, not blame.
- **Independence** ([AIES-AEOS-HO-01-R11]): the assignment system blocks approvers from items they authored or directed and from grants they proposed; the rare no-alternate exception is recorded.
- **Rotation** ([AIES-AEOS-HO-01-R13]): weekly rota over 8 approvers; no approver holds the same gate two consecutive weeks, and FS-G4 samplers are disjoint from that week's FS-G3 approvers.

## 5. Approver Workload Math

[AIES-AEOS-HO-01-R12] requires a defined maximum gate throughput per approver and staffing within it. Fieldstone's caps: **12 weighted gate decisions per approver-day** and **2.5 hours of gate duty per approver-day**. The design must fit under both.

Expected volumes (Scheduling & Dispatch group, steady state, from EX-02's envelope telemetry). The first three rows are the **operating figures** for the lanes running today (the ~60 PRs/week at FS-G2 include the trickle of RT1 items that, until activation, are reviewed per-item like everything else); the FS-G3/FS-G4 rows are **projected at activation** of the dormant AL3/RT1 lane, included so the design is validated against the caps it must eventually satisfy:

| Gate | Items/week | Minutes/item | Hours/week |
|---|---:|---:|---:|
| FS-G2 per-item review | 60 PRs | 20 (45 for the ~6 sampled deep-reviews) | 20.0 + 2.5 = **22.5** |
| FS-G5 release approval | 3 trains | 20 | **1.0** |
| FS-G1 envelope grant | quarterly (amortized) | 60/quarter | **~0.1** |
| **Operating total (today)** | **~63 decisions** | | **~23.6 h/week** |
| FS-G3 checkpoint review — *projected at activation* | 10 batches | 15 | **2.5** |
| FS-G4 sampling audit — *projected at activation* | 12 sampled items | 15 | **3.0** |
| **Projected total (AL3 lane active)** | **~85 decisions** | | **~29.1 h/week** |

Against the pool of 8 qualified approvers over a 5-day week:

- **Hours (today):** 23.6 h ÷ 8 approvers ≈ **3.0 h/approver-week ≈ 0.59 h/day** — 24% of the 2.5 h/day cap.
- **Decisions (today):** 63 ÷ 8 ÷ 5 ≈ **1.6 decisions/approver-day** — 13% of the 12/day cap.
- **Projected at AL3 activation:** 29.1 h ÷ 8 ≈ 3.6 h/approver-week ≈ 0.73 h/day (29% of cap); 85 ÷ 8 ÷ 5 ≈ 2.1 decisions/approver-day (18% of cap) — the dormant lane can be switched on without a staffing change.

The ~4× headroom today (~3.4× even at projected activation volumes) is deliberate: it absorbs vacation and incident weeks without breaching caps, and it funds the deep-review time that anti-rubber-stamping consumes. A queue-depth alert fires at 1.5× daily capacity; sustained breach is treated as an operating-model defect whose remedies are more approvers, smaller units, or lower autonomy — never faster stamping ([AIES-AEOS-HO-01-R12]). Any approver may invoke the overload escalation path (rota lead redistributes the queue) without it counting against them ([AIES-AEOS-HO-01-R14]).

## 6. Override and Kill-Switch Path

- **Anyone can halt, instantly, for free** ([AIES-AEOS-HO-01-R15]): the `/agent-halt` chat command, the `fs halt <task|agent|fleet>` CLI, and a halt button on every review surface stop agent activity at task, agent, or fleet scope. No approval, no advance justification, no minimum role.
- **Halts are honored immediately and logged** ([AIES-AEOS-HO-01-R16]): in-flight actions stop at the nearest safe point; the actor, time, scope, and stated reason (if any) are written to ART-15.
- **The fleet kill-switch is independent and drilled** ([AIES-AEOS-HO-01-R17]): it lives in the operations console on infrastructure disjoint from the agent platform, is reachable when primary tooling is degraded, and is exercised in a monthly drill operated by ROLE-10 (SRE), with drill results recorded.
- **Resumption is gated** ([AIES-AEOS-HO-01-R18]): task/agent-scope resumption requires ROLE-13 approval (via FS-G1) with cause understood and recorded; fleet-scope resumption requires ROLE-14. Automatic resumption is disabled at the platform level. Stopping is cheap; resuming is gated — the asymmetry is deliberate.
- **Output overrides are recorded** ([AIES-AEOS-HO-01-R19]): when a human amends or replaces agent output rather than halting it, the override rationale is captured, and override patterns feed the autonomy review of [AIES-AEOS-WF-01 §7](../../AEOS/workflows.md#7-autonomy-level-promotion).

## 7. Failure Drill — A Gate Catches the Timezone Flaw

A concrete afternoon, showing the gates working. The flaw is the same DST-unsafe class as the one documented and scored in [EX-03](../EX-03-scored-pull-request/README.md): here, recurring work orders expanded against server-local time instead of the service site's IANA timezone, shifting jobs by an hour across DST boundaries.

**Thursday 2026-07-02**

- **14:10** — FS-AGENT-ENG-01 (task FS-5511, AL2/RT2) opens PR #4159, "Recurring work-order generation for multi-week maintenance plans": 312 changed lines (inside the 400-line bound), CI green, decision-context bundle attached. It enters the FS-G2 queue.
- **14:40** — Approver on rota Sofia Lindqvist opens the item; the platform reveals it was randomly flagged a **sampled deep-review** ([AIES-AEOS-HO-01-R09]), so she examines to full depth regardless of the green CI. Tracing the recurrence expansion against the acceptance criteria in the bundle, she finds the schedule computed from server-local wall-clock time with naive date arithmetic; the unit tests all pin a fixed UTC offset, so they pass while any site observing DST gets a one-hour shift twice a year — the intent-level error class that green CI cannot catch (KA-11: *Review Theater* is exactly approving on green CI here).
- **15:05** — She selects **Reject** with structured rationale ([AIES-AEOS-HO-01-R08]): what was examined (recurrence expansion vs site-timezone requirement in ART-02), why rejected (DST-unsafe arithmetic; tests don't exercise timezone boundaries), and what evidence is needed on resubmission (boundary tests across a DST transition for a site in `Europe/Berlin`). The ART-15 record captures item, deciding human, decision, rationale, 25-minute dwell time, and the deep-review finding ([AIES-AEOS-HO-01-R03], [R10]).
- **15:06** — Per the workflow failure path ([AIES-AEOS-WF-01 §2]), work item FS-5511 returns to the producing role: **back to In&nbsp;Progress/Draft, not to an incident**. The rejection rationale is injected into the agent's task context; FS-AGENT-ENG-01 re-executes.
- **15:10** — Telemetry does its quiet work: the deep-review finding rate ticks up on the gate-health dashboard; no anomaly threshold is crossed (a single caught defect at the gate is the control functioning, not a qualification event), so **no autonomy change** occurs. ROLE-12 opens a Knowledge Update candidate ([AIES-AEOS-WF-01 §6](../../AEOS/workflows.md#6-knowledge-update-x09-loop)): the site-timezone convention ("all schedule expansion in the site's IANA zone; DST-boundary tests mandatory for recurrence code") is added to the scheduling squad's context asset (ART-13), so the defect class is prevented upstream, not merely caught downstream.
- **16:20** — The corrected PR (site-zone expansion, DST-boundary tests failing-then-passing) re-enters FS-G2 with its gate history visible ([AIES-AEOS-HO-01-R05] item 5) and is approved with rationale.

**Outcome:** no production incident, no rollback, no customer impact, no halt needed — and a permanent record proving a named human examined the work and why the decision followed. This is the purpose stated in [AIES-AEOS-HO-01 §1]: the human at the gate could actually judge the work, and the record proves she did.

## Related Documents

- [Worked Examples index (AIES-EX-00)](../README.md)
- [AEOS Human Oversight (AIES-AEOS-HO-01)](../../AEOS/human-oversight.md) · [AEOS Workflows (AIES-AEOS-WF-01)](../../AEOS/workflows.md) · [ROLE-13 Human Approver](../../AEOS/roles/ROLE-13-human-approver.md)
- [AEBOK KA-11 — Human-AI Collaboration & Oversight](../../AEBOK/knowledge-areas/KA-11-human-ai-collaboration.md)
- [Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md) — autonomy levels §3, risk tiers §4, roles §5, artifacts §7
- Companion examples in the Fieldstone series: [EX-01](../EX-01-risk-tiering-backlog/README.md), [EX-02](../EX-02-autonomy-envelope/README.md), [EX-03](../EX-03-scored-pull-request/README.md), [EX-04](../EX-04-filled-adr/README.md)

## References

None.

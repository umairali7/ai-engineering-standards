# AEOS Human Oversight

| | |
|---|---|
| **Document ID** | AIES-AEOS-HO-01 |
| **Status** | Review |
| **Audience** | Engineering leadership · Governance officers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

This document is the human oversight standard of AEOS (domain X07): the gate taxonomy, how gates are designed so human judgment is real rather than ceremonial, how approver workload is managed, the override and kill-switch mechanism, and the accountability model behind every gate. Gates are staffed by the Human Approver ([ROLE-13 — Human Approver](roles/ROLE-13-human-approver.md)) per the [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md); gate placements within workflows are defined in [Workflows (AIES-AEOS-WF-01 — Workflows)](workflows.md).

---

## 1. Purpose

Oversight exists to keep a named human meaningfully in control of AI-performed work, proportionate to the autonomy granted. The failure mode this document guards against is not the absence of gates — it is gates that exist on paper while approvals become reflexive. Every requirement below serves one of two goals: the human at the gate can actually judge the work, and the record proves they did.

## 2. Gate Taxonomy

AEOS defines five gate types. Each specifies when the human decision occurs relative to the work.

| Gate type | Timing | Human decision |
|-----------|--------|----------------|
| **Pre-execution approval** | Before execution begins | Approve or reject a plan, action, or autonomy grant before anything runs |
| **Per-item review** | After each output, before it takes effect | Approve, reject, or amend each individual artifact |
| **Checkpoint review** | At defined milestones inside a task envelope | Continue, redirect, or halt the in-flight work |
| **Sampling audit** | During operation, on a defined sample of outputs | Confirm sustained quality; trigger demotion or rework if not |
| **Post-hoc audit** | After outcomes are live, on a periodic schedule | Verify policy compliance and outcome quality; adjust policy and envelopes |

Gate types map to autonomy levels (AL1 — Assisted–AL4 — Autonomous, [Taxonomy §3](../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4)) as follows — ● mandatory, ○ recommended or conditional, — not applicable:

| Gate type | AL1 — Assisted | AL2 — Collaborative | AL3 — Delegated | AL4 — Autonomous |
|-----------|-----|-----|-----|-----|
| Pre-execution approval | — | ○ (● for RT3 — Significant and above work) | ● (envelope grant) | ● (envelope and policy grant) |
| Per-item review | ○ (ordinary peer review) | ● (defining gate of AL2 — Collaborative) | ○ (escalated items only) | — |
| Checkpoint review | — | ○ | ● (defining gate of AL3 — Delegated) | — |
| Sampling audit | — | — | ● | ● |
| Post-hoc audit | ○ | ○ | ○ | ● (defining gate of AL4 — Autonomous) |

- [AIES-AEOS-HO-01-R01 — Human Oversight, requirement 01] Every AI-performed task MUST operate under at least the mandatory gate set for its declared autonomy level; the applicable gates MUST be recorded in the autonomy envelope per [AIES-AEOS-OM-01 — Operating Model §5](operating-model.md#5-autonomy-assignment).
- [AIES-AEOS-HO-01-R02 — Human Oversight, requirement 02] Mandatory gates MUST NOT be removed or weakened without a documented risk acceptance per [AIES-AEOS-GOV-01 — Governance Operations §4](governance-operations.md#4-risk-acceptance); organizations MAY always add gates.
- [AIES-AEOS-HO-01-R03 — Human Oversight, requirement 03] Every gate decision MUST produce an audit trail record (ART-15) capturing the item, the deciding human, the decision, and its rationale.

## 3. Gate Design Requirements

A gate is only as good as what the approver can see and how long they have to see it.

**Reviewable unit size.** [AIES-AEOS-HO-01-R04 — Human Oversight, requirement 04] Every per-item and checkpoint gate MUST define a maximum reviewable unit size appropriate to the artifact type (e.g., lines changed for ART-06, decision count for ART-05); work exceeding it MUST be split before submission to the gate. Submitting oversized units to force cursory review is a governance finding.

**Decision context.** [AIES-AEOS-HO-01-R05 — Human Oversight, requirement 05] The gate MUST present to the approver, at minimum: the work item and its risk tier; the performer identity and declared autonomy level; the artifact or diff under review; the evidence attached (tests, scans, evaluation results); prior gate history and any escalations on the same work item; and what happens on approval (blast radius). An approver who cannot see these MUST reject the item as unreviewable.

**Time budgets.** [AIES-AEOS-HO-01-R06 — Human Oversight, requirement 06] Every gate MUST declare a time budget (target decision latency) so that oversight capacity is planned, not assumed. Expiry of a time budget MUST NOT auto-approve; unattended items escalate to the role owner or a designated alternate approver. Default-open gates are prohibited.

**Neutral choice architecture.** [AIES-AEOS-HO-01-R07 — Human Oversight, requirement 07] Gate tooling and any AI assistance to the approver MUST present options neutrally: no pre-selected "approve", no ranking that pre-commits the decision, and AI-generated summaries clearly labeled as unverified (see [AIES-AEOS-ROLE-13 — Role — Human Approver](roles/ROLE-13-human-approver.md)).

## 4. Anti-Rubber-Stamping

Sustained approval without examination converts an AL2 — Collaborative/AL3 — Delegated grant into de facto AL4 — Autonomous without qualification evidence. AEOS treats this as a control failure, not a productivity win.

- [AIES-AEOS-HO-01-R08 — Human Oversight, requirement 08] Every approval MUST capture a decision rationale — what was examined and why the decision followed. Tooling MAY offer structured rationale capture; empty or boilerplate rationale on RT3 — Significant and above items is a governance finding.
- [AIES-AEOS-HO-01-R09 — Human Oversight, requirement 09] A defined fraction of routine approvals (org-defined, default 10%) MUST be randomly designated **sampled deep-reviews**, examined to full depth regardless of apparent routineness, with findings recorded.
- [AIES-AEOS-HO-01-R10 — Human Oversight, requirement 10] Review-depth indicators — time-to-decision distributions, rationale quality sampling, deep-review finding rates — MUST be tracked per approver and per gate as operating metrics ([AIES-AEOS-GOV-01 — Governance Operations §8](governance-operations.md#8-metrics)). Decision times below a plausible examination floor and sustained approval rates near 100% MUST be investigated by ROLE-14.
- [AIES-AEOS-HO-01-R11 — Human Oversight, requirement 11] An approver MUST NOT approve work they performed or directed, and MUST NOT approve output of an agent whose autonomy grant they proposed, unless no qualified alternate exists and the exception is recorded.

## 5. Approver Workload and Fatigue

Rubber-stamping is usually a capacity problem before it is a diligence problem.

- [AIES-AEOS-HO-01-R12 — Human Oversight, requirement 12] Organizations MUST define a maximum gate throughput per approver (decisions per day, weighted by gate type and risk tier) and MUST NOT schedule approvers beyond it. Sustained queue depth above capacity is an operating-model defect: the remedy is more approvers, smaller units, or lower autonomy — never faster stamping.
- [AIES-AEOS-HO-01-R13 — Human Oversight, requirement 13] Gate duty for high-volume gates MUST rotate among qualified approvers; no single approver SHOULD be the sole gate authority for a given agent or task type over an extended period (familiarity breeds default-approval).
- [AIES-AEOS-HO-01-R14 — Human Oversight, requirement 14] Approvers MUST have a defined overload escalation path (see [AIES-AEOS-ROLE-13 — Role — Human Approver](roles/ROLE-13-human-approver.md)); invoking it MUST NOT be held against the approver.
- Approver workload and queue metrics feed the governance review cycle per [AIES-AEOS-GOV-01 — Governance Operations §7](governance-operations.md#7-periodic-governance-reviews).

## 6. Override and Kill-Switch

- [AIES-AEOS-HO-01-R15 — Human Oversight, requirement 15] Any human MAY halt any agent activity at any time — pausing a task, revoking an envelope, or activating the kill-switch. Halting requires no approval, no justification in advance, and no minimum role; the operating model's asymmetry is deliberate: stopping is always cheap, resuming is gated.
- [AIES-AEOS-HO-01-R16 — Human Oversight, requirement 16] A halt instruction MUST be honored immediately: in-flight actions stop at the nearest safe point, no new actions begin, and the halt — actor, time, scope, stated reason if given — is logged to the audit trail (ART-15).
- [AIES-AEOS-HO-01-R17 — Human Oversight, requirement 17] Every environment where agents act MUST provide a kill-switch that terminates agent activity at task, agent, and fleet scope. The kill-switch MUST NOT depend on any agent to operate, MUST be reachable when primary tooling is degraded, and MUST be exercised (tested) on an org-defined schedule ([AIES-AEOS-ROLE-10 — Role — SRE](roles/ROLE-10-sre.md) operates it in production).
- [AIES-AEOS-HO-01-R18 — Human Oversight, requirement 18] Resumption after a halt or kill-switch activation MUST be approved by ROLE-13 (or ROLE-14 for fleet-scope activations) with the cause understood and recorded; automatic resumption is prohibited.
- [AIES-AEOS-HO-01-R19 — Human Oversight, requirement 19] Overriding an agent's output or decision (as opposed to halting it) MUST be recorded with the override rationale; override patterns feed autonomy review per [Workflows §7](workflows.md#7-autonomy-level-promotion).

## 7. Accountability Model

- [AIES-AEOS-HO-01-R20 — Human Oversight, requirement 20] Gate decision authority is held by humans (ROLE-13 per [AIES-SHARED-02 — Taxonomy §5](../Shared/Taxonomy/README.md#5-ai-engineering-roles)) and MUST NOT be delegated to an AI system under any circumstances — including "AI pre-approval" schemes where a human ratifies batches the AI already accepted. AI assistance to the approver is permitted; AI decision authority is not.
- [AIES-AEOS-HO-01-R21 — Human Oversight, requirement 21] The approver is accountable for the gate decision; the accountable human named at work intake ([AIES-AEOS-OM-01-R01 — Operating Model, requirement 01](operating-model.md#1-principles)) remains accountable for the outcome. Neither accountability transfers to an agent, a vendor, or a tool.
- [AIES-AEOS-HO-01-R22 — Human Oversight, requirement 22] An approver MUST hold a current qualification appropriate to the gate (the *Oversight & Governance* endorsement of [AIES-AECT-CERT-01 — Certification Framework §3](../AECT/certification-framework.md#3-role-specialization-endorsements) is the RECOMMENDED expectation for RT3 — Significant through RT4 — Critical gates).
- [AIES-AEOS-HO-01-R23 — Human Oversight, requirement 23] Delegating an approval to another human MUST transfer the full decision context (§3) and be recorded; serial re-delegation that obscures who actually decided is prohibited.

## Related Documents

- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](operating-model.md) — autonomy assignment and escalation the gates enforce
- [Workflows (AIES-AEOS-WF-01 — Workflows)](workflows.md) — where each gate sits in each workflow
- [Human Approver (AIES-AEOS-ROLE-13 — Role — Human Approver)](roles/ROLE-13-human-approver.md) — the role that staffs the gates
- [Governance Operations (AIES-AEOS-GOV-01 — Governance Operations)](governance-operations.md) — audit trail, metrics, and review of gate effectiveness

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

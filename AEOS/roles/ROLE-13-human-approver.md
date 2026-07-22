# ROLE-13 — Human Approver

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-13 |
| **Status** | Review |
| **Audience** | Governance officers · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-13 |
| Staffing | **human only** ([Taxonomy §5](../../Shared/Taxonomy/README.md#5-ai-engineering-roles)) |
| Primary phases | Cross-cutting X07 (Human Oversight) — all gates |
| Key artifacts | Gate decisions recorded in ART-15 (Audit Trail Record) |

## Mission

The Human Approver is the human authority at oversight gates: reviewing, approving, rejecting, and escalating gated work per [AIES-AEOS-HO-01 — Human Oversight](../human-oversight.md). This role is where the operating model's first principle — human accountability — becomes an operational fact rather than a policy statement.

## Responsibilities

1. Decide at approval gates: pre-execution approvals, per-item reviews, checkpoint reviews, sampling audits, and post-hoc audits per the gate taxonomy of [AIES-AEOS-HO-01 — Human Oversight §2](../human-oversight.md#2-gate-taxonomy).
2. Review the full decision context the gate presents; request missing context rather than deciding without it.
3. Grant, deny, and revoke autonomy envelopes per the assignment procedure of [AIES-AEOS-OM-01 — Operating Model §5](../operating-model.md#5-autonomy-assignment).
4. Receive and resolve envelope-breach escalations.
5. Exercise override and kill-switch authority per [AIES-AEOS-HO-01 — Human Oversight §6](../human-oversight.md#6-override-and-kill-switch).
6. Report gate-quality problems (unreviewable diffs, missing context, unrealistic time budgets) to the Governance Officer.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | Gated artifacts of every type with their evidence (ART-06 diffs, ART-07 reports, ART-08 assessments, provenance) |
| Outputs | Gate decisions with rationale in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-13-R01] This role MUST be staffed by a human. AI systems MAY prepare decision context (summaries, risk highlights, diffs) but MUST NOT make, recommend-by-default, or pre-select the gate decision.
- [AIES-AEOS-ROLE-13-R02] An approver MUST NOT approve artifacts they produced or co-produced ([AIES-AEOS-ROLE-00-R05 — Role Model, requirement 05](README.md#3-shared-role-specification-requirements)).
- [AIES-AEOS-ROLE-13-R03] Approvals MUST record the decision, its rationale, the evidence examined, and the time spent; bulk approval without item examination is prohibited (see anti-rubber-stamping requirements in [AIES-AEOS-HO-01 — Human Oversight §4](../human-oversight.md#4-anti-rubber-stamping)).

## Escalation Duties

- Escalate decisions beyond the approver's competence or authority to a more qualified approver — an approver MUST decline rather than guess.
- Escalate suspected gaming of gates (e.g., changes split to evade review thresholds) to the Governance Officer (ROLE-14).
- Escalate sustained overload (queue depth or time pressure compromising review quality) per [AIES-AEOS-HO-01 — Human Oversight §5](../human-oversight.md#5-approver-workload-and-fatigue).

## Required Qualifications (per AESQS)

| Requirement | Detail |
|-------------|--------|
| Domain competence | CL2+ in the discipline being gated (an approver of source changes needs engineering competence; of security assessments, security competence) |
| Oversight competence | CL2+ in AI oversight practice: failure modes of AI-produced work, review techniques, automation-bias awareness |
| Authority | Formally designated for the gate class and risk tier; designation recorded in ART-15 |

## AI Staffing Notes

Not applicable for decision authority — this role MUST be human. However, AI assistance to approvers is expected and governed:

- Assistive agents MAY summarize context, highlight anomalies, and surface relevant history; their contributions MUST be labeled as AI-produced in the decision context.
- Assistive agents MUST NOT rank or phrase options in a way that pre-commits the decision (choice architecture is part of gate design review per [AIES-AEOS-HO-01 — Human Oversight §3](../human-oversight.md#3-gate-design-requirements)).
- Approver-assistance agents are qualified under AESQS like any other agent, and their assistance quality (missed-issue rate in audited decisions) is telemetered to ART-15.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

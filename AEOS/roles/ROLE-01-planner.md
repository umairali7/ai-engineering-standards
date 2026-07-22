# ROLE-01 — Planner

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-01 |
| **Status** | Review |
| **Audience** | Engineering leadership · Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-01 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P08 (Planning) |
| Key artifacts | ART-05 (Work Item / Plan) |

## Mission

The Planner decomposes approved objectives into work items (ART-05) that are correctly scoped, sequenced, risk-classified, and traceable — the entry point of the [operating model's work intake](../operating-model.md#2-work-intake-and-flow). Good planning is what makes least-autonomy staffing decisions possible downstream.

## Responsibilities

1. Decompose product requirements (ART-02) and architecture decisions (ART-04) into work items with clear objectives and acceptance criteria (P08).
2. Propose the risk tier (RT1 — Minimal through RT4 — Critical) for each work item, with rationale, for confirmation at intake.
3. Sequence and estimate work, identifying dependencies and critical paths.
4. Ensure every work item names an accountable human before execution ([AIES-AEOS-OM-01-R01 — Operating Model, requirement 01](../operating-model.md#1-principles)).
5. Maintain plan-to-artifact traceability as work progresses (X04).
6. Re-plan when scope changes, triggering risk-tier re-evaluation per [AIES-AEOS-OM-01-R07 — Operating Model, requirement 07](../operating-model.md#2-work-intake-and-flow).

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-01 (Business Case), ART-02 (Product Requirement), ART-04 (ADR), ART-12 (Telemetry & Evaluation Report) |
| Outputs | ART-05 (Work Item / Plan), contributions to ART-15 (Audit Trail Record) |

## Autonomy Constraints

- [AIES-AEOS-ROLE-01-R01] Risk-tier proposals produced by an AI-staffed Planner MUST be confirmed by a human before the tier takes effect; proposed tiers are advisory at every autonomy level.
- [AIES-AEOS-ROLE-01-R02] An AI-staffed Planner MUST NOT assign work to performers or grant autonomy levels; it prepares assignments for the staffing procedure of [Operating Model §4](../operating-model.md#4-staffing-decision-procedure).

## Escalation Duties

- Escalate to the accountable human when decomposition reveals scope materially beyond the approved objective.
- Escalate to the Governance Officer (ROLE-14) when a work item appears to require loosening an RT→AL default.
- Escalate conflicting priorities to the Product Manager (ROLE-03).

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in planning and estimation; CL1+ in risk classification |
| AI agent | Current AESQS qualification for (ROLE-01, decomposition and sequencing task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement; agent qualification per task type as used |

## AI Staffing Notes

When ROLE-01 is staffed by an AI agent:

| Risk tier of planned work | Max autonomy for planning tasks |
|---------------------------|--------------------------------|
| RT1 — Minimal | AL4 — Autonomous |
| RT2 — Moderate | AL3 — Delegated |
| RT3 — Significant | AL2 — Collaborative |
| RT4 — Critical | AL1 — Assisted |

- **Mandatory gates:** per-item human review of risk-tier proposals (all tiers); checkpoint review of plan structure before execution begins on RT3 — Significant and above plans.
- **Telemetry:** planning-accuracy metrics (estimate vs. actual, re-plan frequency), risk-tier proposal override rate, and all plan changes logged to ART-15.
- The planning task's own risk tier follows the highest-tier work item in the plan.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

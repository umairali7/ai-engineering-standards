# ROLE-04 — UX Designer

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-04 |
| **Status** | Review |
| **Audience** | Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-04 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P04 (User Experience) |
| Key artifacts | ART-03 (UX Specification) |

## Mission

The UX Designer defines *how humans will use the system*: researching user needs, designing interactions and interfaces, and specifying them precisely enough (ART-03) that engineering and testing can verify conformance — including accessibility (X14) as a first-class requirement.

## Responsibilities

1. Conduct and synthesize user research; maintain user and task models (P04).
2. Design interaction flows, information architecture, and interface specifications (ART-03).
3. Specify accessibility requirements (X14) and verify designs against them.
4. Validate designs with users or representative evaluation before engineering commitment on RT3+ scope.
5. Collaborate with ROLE-02/ROLE-03 to keep requirements and UX specifications consistent.
6. Review implemented interfaces for specification conformance at quality gates.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-02 (Product Requirement), user research data, ART-12 (Telemetry & Evaluation Report) |
| Outputs | ART-03 (UX Specification), design-review records in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-04-R01] UX specifications for user journeys involving irreversible user actions, financial transactions, or regulated data (RT4 characteristics) MUST receive human design review before implementation, regardless of the producing performer's autonomy level.
- [AIES-AEOS-ROLE-04-R02] An AI-staffed UX Designer MUST NOT substitute synthetic user feedback for required user validation on RT3+ scope; synthetic evaluation MAY supplement it and MUST be labeled as synthetic.

## Escalation Duties

- Escalate conflicts between usability and requirements to the Product Manager (ROLE-03).
- Escalate accessibility non-conformance that cannot be resolved in design to the Governance Officer (ROLE-14) as a compliance risk (X03/X14).
- Escalate low confidence in user-need understanding rather than designing from assumption.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in interaction design; CL2+ in accessibility practice |
| AI agent | Current AESQS qualification for (ROLE-04, design-drafting / specification / accessibility-audit task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and owns user-validation activities |

## AI Staffing Notes

When ROLE-04 is staffed by an AI agent:

| Risk tier of affected scope | Max autonomy for design tasks |
|-----------------------------|-------------------------------|
| RT1 | AL4 |
| RT2 | AL3 |
| RT3 | AL2 |
| RT4 | AL1 |

- **Mandatory gates:** human design review before engineering commitment on RT3+ journeys (see R01); per-item review of accessibility specifications.
- **Telemetry:** design rework rate after user validation, accessibility-audit pass rate, and labeled use of synthetic evaluation logged to ART-15.
- Agents are strongest at variant exploration, specification drafting, and accessibility auditing; user empathy and validation remain human-anchored activities.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

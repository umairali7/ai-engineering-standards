# ROLE-02 — Business Analyst

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-02 |
| **Status** | Review |
| **Audience** | Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-02 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P02 (Business Analysis), P05 (Requirements Engineering) |
| Key artifacts | ART-01 (Business Case), ART-02 (Product Requirement) |

## Mission

The Business Analyst establishes *what problem is being solved* and *what the system must do*: eliciting, analyzing, and specifying requirements that are unambiguous, testable, and traceable from business case to delivered behavior.

## Responsibilities

1. Elicit and document business needs and constraints from stakeholders (P02).
2. Author and maintain business cases (ART-01) and detailed requirements (ART-02) in P05.
3. Ensure every requirement is testable and traceable forward to work items (ART-05) and test suites (ART-07).
4. Analyze impact of proposed changes on existing requirements.
5. Flag requirements with compliance (X03), privacy (X02), or safety (X06) implications for specialist review.
6. Resolve requirement conflicts and ambiguities before they reach engineering.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | Stakeholder input, ART-01 drafts, ART-12 (Telemetry & Evaluation Report), existing ART-02 |
| Outputs | ART-01 (Business Case), ART-02 (Product Requirement), contributions to ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-02-R01] Requirements produced by an AI-staffed Business Analyst MUST be reviewed by a human with domain knowledge before entering P08 planning, regardless of autonomy level.
- [AIES-AEOS-ROLE-02-R02] An AI-staffed Business Analyst MUST NOT be the sole channel of stakeholder elicitation for RT3 — Significant and above scope; it MAY prepare, structure, and analyze elicitation material.

## Escalation Duties

- Escalate irreconcilable stakeholder conflicts to the Product Manager (ROLE-03).
- Escalate requirements touching regulated data or compliance obligations to the Governance Officer (ROLE-14) and Security Engineer (ROLE-08).
- Escalate low confidence in domain understanding rather than inventing plausible requirements.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in requirements engineering and analysis; CL1+ in the business domain |
| AI agent | Current AESQS qualification for (ROLE-02, elicitation-support / specification / impact-analysis task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and owns stakeholder relationships |

## AI Staffing Notes

When ROLE-02 is staffed by an AI agent:

| Risk tier of affected scope | Max autonomy for analysis tasks |
|-----------------------------|--------------------------------|
| RT1 — Minimal | AL4 — Autonomous |
| RT2 — Moderate | AL3 — Delegated |
| RT3 — Significant | AL2 — Collaborative |
| RT4 — Critical | AL1 — Assisted |

- **Mandatory gates:** per-item human review of every new or changed requirement before planning (see R01); checkpoint review of traceability links on RT3 — Significant and above scope.
- **Telemetry:** requirement defect rate (requirements later found wrong or ambiguous), stakeholder correction rate, and hallucinated-constraint incidents logged to ART-15.
- Agents SHOULD ground all requirement statements in cited elicitation sources (ART-13 context assets); uncited requirement content is an escalation trigger.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

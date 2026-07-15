# ROLE-03 — Product Manager

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-03 |
| **Status** | Review |
| **Audience** | Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-03 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P03 (Product Management) |
| Key artifacts | ART-02 (Product Requirement) |

## Mission

The Product Manager decides *what to build, in what order*: owning the product direction, prioritizing outcomes against evidence, and accepting delivered value on behalf of users and the business.

## Responsibilities

1. Own the product vision, roadmap, and prioritization (P03).
2. Author product requirements (ART-02) at the outcome level; delegate detail specification to ROLE-02.
3. Prioritize the backlog using evidence from telemetry and evaluation reports (ART-12).
4. Accept or reject delivered features against acceptance criteria at release gates.
5. Balance feature work against quality, security, and improvement work (P16).
6. Communicate trade-offs and decisions with recorded rationale (X04).

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-01 (Business Case), ART-03 (UX Specification), ART-12 (Telemetry & Evaluation Report), market and user evidence |
| Outputs | ART-02 (Product Requirement), prioritization decisions in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-03-R01] Product acceptance decisions (accepting delivered scope for release) MUST be made by a human, whatever the staffing mode; an AI-staffed Product Manager prepares acceptance recommendations only.
- [AIES-AEOS-ROLE-03-R02] AI-staffed prioritization MUST cite the evidence (ART-12 or equivalent) supporting each ranking; unevidenced re-prioritization above AL1 is prohibited.

## Escalation Duties

- Escalate strategy conflicts (P01 misalignment) to business leadership outside the operating model.
- Escalate discovered scope with RT4 characteristics to the Governance Officer (ROLE-14) before commitment.
- Escalate acceptance disputes to the accountable human of the work item.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in product management; CL2+ in evidence-driven prioritization |
| AI agent | Current AESQS qualification for (ROLE-03, backlog-analysis / requirement-drafting / evidence-synthesis task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and holds acceptance authority (R01) |

## AI Staffing Notes

When ROLE-03 is staffed by an AI agent:

| Risk tier of affected scope | Max autonomy for product tasks |
|-----------------------------|-------------------------------|
| RT1 | AL4 |
| RT2 | AL3 |
| RT3 | AL2 |
| RT4 | AL1 |

- **Mandatory gates:** human acceptance decision at every release gate (see R01); per-item review of roadmap changes affecting committed scope; checkpoint review of backlog re-ordering.
- **Telemetry:** prioritization override rate, delivered-value metrics per accepted feature, and recommendation rationale completeness logged to ART-15.
- In practice ROLE-03 is most effective as a human-AI pair: the agent synthesizes evidence and drafts requirements; the human owns direction and acceptance.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

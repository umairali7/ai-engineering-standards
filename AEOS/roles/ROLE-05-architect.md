# ROLE-05 — Architect

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-05 |
| **Status** | Review |
| **Audience** | Architects |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-05 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P06 (Solution Analysis), P07 (Architecture) |
| Key artifacts | ART-04 (Architecture Decision Record) |

## Mission

The Architect determines *how candidate solutions compare* and *how the system is structured*: evaluating options with explicit trade-offs, recording decisions as ADRs (ART-04), and keeping the implemented system consistent with its intended structure.

## Responsibilities

1. Analyze candidate solutions with documented trade-offs (P06).
2. Define and evolve system structure; record every significant decision as an ADR (P07).
3. Guard architectural qualities: performance (X11), scalability (X12), reliability (X13), and cost (X10).
4. Review high-impact source changes (ART-06) for architectural conformance.
5. Run the [Architecture Change workflow](../workflows.md#4-architecture-change-adr-flow) for structural changes.
6. Maintain the architecture's alignment with reference architectures per [AEAR](../../AEAR/README.md).

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-02 (Product Requirement), ART-03 (UX Specification), ART-12 (Telemetry & Evaluation Report), existing ART-04 set |
| Outputs | ART-04 (ADR), architecture review records in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-05-R01] ADR acceptance MUST be a human decision at RT3 — Significant and above impact; an AI-staffed Architect MAY draft, analyze, and recommend, and MAY accept ADRs autonomously only for RT1 — Minimal through RT2 — Moderate impact within its envelope.
- [AIES-AEOS-ROLE-05-R02] An AI-staffed Architect MUST enumerate at least two alternatives with trade-offs in every ADR draft; single-option ADRs are a gate failure.

## Escalation Duties

- Escalate decisions whose blast radius exceeds the work item's declared risk tier to intake for re-classification ([AIES-AEOS-OM-01-R07 — Operating Model, requirement 07](../operating-model.md#2-work-intake-and-flow)).
- Escalate security-sensitive structural choices to the Security Engineer (ROLE-08).
- Escalate irreversible platform commitments (RT4 — Critical) to the Human Approver (ROLE-13) and Governance Officer (ROLE-14).

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL3+ in architecture and solution analysis (reviews and coaches others) |
| AI agent | Current AESQS qualification for (ROLE-05, option-analysis / ADR-drafting / conformance-review task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and holds ADR acceptance authority at RT3 — Significant and above (R01) |

## AI Staffing Notes

When ROLE-05 is staffed by an AI agent:

| Risk tier of decision impact | Max autonomy for architecture tasks |
|------------------------------|-------------------------------------|
| RT1 — Minimal | AL4 — Autonomous |
| RT2 — Moderate | AL3 — Delegated |
| RT3 — Significant | AL2 — Collaborative |
| RT4 — Critical | AL1 — Assisted |

- **Mandatory gates:** human ADR acceptance at RT3 — Significant and above (see R01); per-item review of conformance findings that block other roles' work; checkpoint review of the ADR log.
- **Telemetry:** ADR reversal rate, alternative-coverage completeness, conformance-review precision (false-block rate), all logged to ART-15.
- Agents excel at option enumeration, consistency checking across the ADR corpus, and conformance review at scale; judgment about organizational context and irreversibility is weighted toward the human side of a pair.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

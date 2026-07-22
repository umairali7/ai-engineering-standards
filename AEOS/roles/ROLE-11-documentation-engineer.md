# ROLE-11 — Documentation Engineer

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-11 |
| **Status** | Review |
| **Audience** | Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-11 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | Cross-cutting X08 (Documentation), all phases |
| Key artifacts | Documentation content across ART-01 … ART-12 |

## Mission

The Documentation Engineer keeps the written record of the system accurate, current, and usable: user documentation, operational documentation, and the engineering documentation embedded in every artifact type. In an AI-native SDLC, documentation is doubly load-bearing — it is also context (ART-13 input) that grounds AI performers.

## Responsibilities

1. Author and maintain user-facing and operator-facing documentation across the SDLC (X08).
2. Keep documentation synchronized with delivered behavior; treat drift as a defect.
3. Define documentation standards (structure, style, review criteria) for all roles' artifact documentation.
4. Review artifact documentation quality at gates where documentation is a gate criterion.
5. Coordinate with ROLE-12 so that authoritative documentation feeds curated context assets (ART-13).
6. Maintain accessibility (X14) of documentation itself.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | All artifact types as documentation sources; ART-10 (Release Record) as the change signal |
| Outputs | Documentation content and updates across ART-01 … ART-12; documentation-review records in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-11-R01] AI-generated documentation of system behavior MUST be verified against the actual behavior (tests, telemetry, or human confirmation) before publication for RT3 — Significant and above systems; plausible-but-unverified behavioral claims are a gate failure.
- [AIES-AEOS-ROLE-11-R02] Documentation with legal, compliance, or safety content (X03/X06) MUST receive human review before publication at any autonomy level.

## Escalation Duties

- Escalate documentation-vs-behavior discrepancies to the owning role as defects.
- Escalate compliance-relevant documentation questions to the Governance Officer (ROLE-14).
- Escalate systematic documentation debt affecting agent grounding quality to ROLE-12.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in technical writing and information architecture |
| AI agent | Current AESQS qualification for (ROLE-11, drafting / synchronization / review task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and owns publication decisions for R02 content |

## AI Staffing Notes

When ROLE-11 is staffed by an AI agent:

| Risk tier of documented system | Max autonomy for documentation tasks |
|--------------------------------|--------------------------------------|
| RT1 — Minimal (internal docs, typo fixes — themselves RT1 — Minimal changes) | AL4 — Autonomous |
| RT2 — Moderate (engineering docs, internal guides) | AL3 — Delegated |
| RT3 — Significant (user-facing docs for production behavior) | AL2 — Collaborative |
| RT4 — Critical (safety, legal, compliance content) | AL1 — Assisted |

- **Mandatory gates:** behavioral verification before publication for RT3 — Significant and above (see R01); human review of R02 content; sampling audit of published documentation accuracy.
- **Telemetry:** documentation defect reports, drift detection lag (release date vs. doc update date), verification coverage, logged to ART-15.
- Documentation agents are well suited to drift detection (diffing docs against release records) and draft synchronization; they MUST cite the artifact evidence for every behavioral claim they write.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

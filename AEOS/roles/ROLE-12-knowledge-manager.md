# ROLE-12 — Knowledge Manager

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-12 |
| **Status** | Review |
| **Audience** | Platform teams · Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-12 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | Cross-cutting X09 (Knowledge Management), all phases |
| Key artifacts | ART-13 (Prompt / Context Asset) |

## Mission

The Knowledge Manager curates what the organization — and its AI performers — know: capturing engineering knowledge, maintaining the context assets (ART-13) that ground agent work, and running the [Knowledge Update loop](../workflows.md#6-knowledge-update-x09-loop) that turns experience into improved practice. Context asset quality directly determines AI output quality; this role is the operating model's leverage point.

## Responsibilities

1. Curate and version context assets (ART-13): codebase knowledge, conventions, standards, prior decisions, prompt assets (X09).
2. Run the knowledge update loop: capture lessons from retrospectives, incidents (with ROLE-10), and evaluation reports (ART-12) into reusable assets.
3. Measure and improve context asset effectiveness (does grounding reduce defects and escalations?).
4. Retire stale knowledge; staleness in agent-consumed assets is an active hazard, not passive debt.
5. Govern access: which agents receive which context assets, respecting privacy (X02) and security (X01) boundaries.
6. Coordinate with ROLE-11 so documentation and context assets stay consistent.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-04 (ADR), ART-11 (Runbook), ART-12 (Telemetry & Evaluation Report), retrospective and incident outputs |
| Outputs | ART-13 (Prompt / Context Asset), knowledge-change records in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-12-R01] Changes to context assets consumed by agents operating at AL3 — Delegated+ MUST receive per-item human review before activation — a corrupted context asset can systematically degrade every agent that consumes it.
- [AIES-AEOS-ROLE-12-R02] Context assets MUST be versioned, and every agent action MUST be traceable to the context asset versions it consumed ([AIES-AEOS-OM-01-R17 — Operating Model, requirement 17](../operating-model.md#6-artifact-and-provenance-requirements)); an AI-staffed Knowledge Manager MUST NOT alter historical versions.
- [AIES-AEOS-ROLE-12-R03] Context assets MUST NOT contain secrets or regulated personal data unless explicitly authorized by ROLE-08 and ROLE-14 with recorded justification.

## Escalation Duties

- Escalate detected context-asset corruption or poisoning to ROLE-08 (security incident) and suspend distribution of the affected asset.
- Escalate contested knowledge (contradictory conventions, disputed decisions) to the owning role for resolution rather than encoding the contradiction.
- Escalate evidence that a context asset degrades agent performance to AESQS re-evaluation.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in knowledge management; CL2+ in context engineering for AI systems |
| AI agent | Current AESQS qualification for (ROLE-12, capture / curation / effectiveness-analysis task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and approves asset activation for R01 scope |

## AI Staffing Notes

When ROLE-12 is staffed by an AI agent:

| Risk tier of consuming scope | Max autonomy for knowledge tasks |
|------------------------------|----------------------------------|
| RT1 — Minimal (assets for RT1 — Minimal-only tasks) | AL4 — Autonomous |
| RT2 — Moderate (general engineering assets) | AL3 — Delegated |
| RT3 — Significant (assets consumed by AL3 — Delegated+ agents or RT3 — Significant work) | AL2 — Collaborative |
| RT4 — Critical (assets grounding RT4 — Critical work) | AL1 — Assisted |

- **Mandatory gates:** per-item human review before activating assets consumed at AL3 — Delegated+ (see R01); automated secret/PII scanning on every asset change (see R03); sampling audit of asset accuracy.
- **Telemetry:** asset consumption rates, correlation between asset versions and downstream quality metrics, staleness age distribution, logged to ART-15.
- The risk tier of a knowledge task derives from its *consumers*: an asset feeding an AL4 — Autonomous agent on RT1 — Minimal work is higher-stakes than its content suggests, because errors replicate across every consuming action.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

# ROLE-08 — Security Engineer

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-08 |
| **Status** | Review |
| **Audience** | Security engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-08 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P11 (Security); cross-cutting X01, supporting X02/X06 |
| Key artifacts | ART-08 (Security Assessment) |

## Mission

The Security Engineer ensures the system resists abuse: threat-modeling designs, assessing changes and releases (ART-08), and — distinctively in an AI-native SDLC — securing the AI participation itself (agent tool access, prompt-injection surfaces, guardrail integrity per X06).

## Responsibilities

1. Threat-model architectures and high-risk changes (P11, X01).
2. Produce security assessments (ART-08) for releases and RT3 — Significant and above changes.
3. Operate and tune automated security scanning in pipelines (with ROLE-09).
4. Assess agent definitions (ART-14) before activation: tool access, data exposure, injection surfaces, guardrail coverage.
5. Classify security implications of work at intake (advising risk-tier classification).
6. Lead security aspects of incident response with ROLE-10 (P14).

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-04 (ADR), ART-06 (Source Change), ART-09 (Pipeline Definition), ART-14 (Agent Definition) |
| Outputs | ART-08 (Security Assessment), security gate evidence in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-08-R01] Security sign-off on RT3 — Significant and above releases and on agent-definition activation MUST be given by a human; an AI-staffed Security Engineer produces assessments and findings but not the sign-off.
- [AIES-AEOS-ROLE-08-R02] An AI-staffed Security Engineer MUST NOT be granted offensive tooling (exploitation, credential testing) above AL2 — Collaborative, and any such use MUST occur in isolated environments with per-item human review.
- [AIES-AEOS-ROLE-08-R03] Suppression of security findings (accepting risk, marking false positive) above severity thresholds defined by the organization MUST be a human decision.

## Escalation Duties

- Escalate exploitable findings in production immediately to ROLE-10 and ROLE-14 (incident trigger).
- Escalate risk acceptances beyond the role's authority to the Governance Officer (ROLE-14).
- Escalate suspected compromise or manipulation of an agent (e.g., prompt injection) to ROLE-14 with immediate suspension of the affected agent's tasks.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL3+ in application security; CL2+ in AI-system security |
| AI agent | Current AESQS qualification for (ROLE-08, scanning-triage / assessment-drafting / threat-model-drafting task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and holds sign-off authority (R01) |

## AI Staffing Notes

When ROLE-08 is staffed by an AI agent:

| Risk tier of assessed scope | Max autonomy for security tasks |
|-----------------------------|--------------------------------|
| RT1 — Minimal | AL4 — Autonomous (triage and reporting only) |
| RT2 — Moderate | AL3 — Delegated |
| RT3 — Significant | AL2 — Collaborative |
| RT4 — Critical | AL1 — Assisted |

- **Mandatory gates:** human sign-off on RT3 — Significant and above assessments and all agent-definition activations (see R01); per-item review of finding suppressions (see R03); sampling audit of triage decisions.
- **Telemetry:** finding precision/recall against later-confirmed issues, suppression override rate, time-to-triage, logged to ART-15.
- A security agent's own tool access is itself a threat surface: its agent definition MUST be assessed by a human security engineer, not by the agent, and re-assessed on every definition version change.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

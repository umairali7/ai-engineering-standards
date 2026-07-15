# ROLE-10 — SRE

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-10 |
| **Status** | Review |
| **Audience** | Platform teams · Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-10 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P14 (Operations), P15 (Observability) |
| Key artifacts | ART-11 (Runbook), ART-12 (Telemetry & Evaluation Report) |

## Mission

The SRE keeps the system running and understood: operating production (P14), building the observability that makes behavior explainable (P15), leading incident response, and producing the telemetry and evaluation reports (ART-12) that drive both system improvement and agent re-qualification.

## Responsibilities

1. Operate production services against defined reliability objectives (X13).
2. Build and maintain observability: metrics, logs, traces, and AI-specific telemetry (agent actions, escalations, gate outcomes) (P15).
3. Author and maintain runbooks (ART-11); keep them executable and current.
4. Lead the [Incident Response workflow](../workflows.md#5-incident-response-p14p15), including incidents caused by AI performers.
5. Produce telemetry and evaluation reports (ART-12) consumed by P16, AESQS re-qualification, and governance reviews.
6. Operate the kill-switch mechanisms required by [AIES-AEOS-HO-01 §6](../human-oversight.md#6-override-and-kill-switch).

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-10 (Release Record), ART-11 (Runbook), production telemetry, ART-15 (Audit Trail) |
| Outputs | ART-11 (Runbook), ART-12 (Telemetry & Evaluation Report), incident records in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-10-R01] Remediation actions on production during an incident are RT3 minimum; an AI-staffed SRE above AL1 MUST act only through pre-approved runbook procedures (ART-11), and any off-runbook action requires human approval.
- [AIES-AEOS-ROLE-10-R02] Incident severity classification at the highest levels (org-defined; at minimum any incident involving data loss, safety, or regulated data) MUST be confirmed by a human.
- [AIES-AEOS-ROLE-10-R03] An AI-staffed SRE MUST NOT suppress, acknowledge-away, or re-threshold alerts above AL2; alert-policy changes require per-item human review.

## Escalation Duties

- Escalate incidents implicating an AI performer to the Governance Officer (ROLE-14) and suspend the implicated agent's tasks per [AIES-AEOS-OM-01 §7](../operating-model.md#7-escalation-model).
- Escalate reliability-objective breaches trending toward violation to ROLE-03/ROLE-05 for prioritization.
- Escalate observability blind spots that prevent behavior explanation (EV6 traceability failures) to the role owner.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in reliability engineering and incident command |
| AI agent | Current AESQS qualification for (ROLE-10, monitoring-triage / runbook-execution / report-generation task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and holds incident command for severe incidents |

## AI Staffing Notes

When ROLE-10 is staffed by an AI agent:

| Risk tier of the operation | Max autonomy for SRE tasks |
|----------------------------|----------------------------|
| RT1 (read-only diagnostics, report drafting) | AL4 |
| RT2 (non-production remediation, alert triage) | AL3 |
| RT3 (production remediation via approved runbooks) | AL2 |
| RT4 (irreversible operations, data restoration) | AL1 |

- **Mandatory gates:** human approval for off-runbook production actions (see R01); human confirmation of severe-incident classification (see R02); post-hoc audit of all autonomous remediations.
- **Telemetry:** remediation success rate, mean time to detect/resolve with vs. without agent participation, false-remediation rate, logged to ART-15.
- The kill-switch that halts agents ([AIES-AEOS-HO-01 §6](../human-oversight.md#6-override-and-kill-switch)) MUST NOT depend on any agent to operate — an SRE agent cannot be in its own shutdown path.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

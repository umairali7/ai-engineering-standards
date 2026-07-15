# ROLE-09 — DevOps Engineer

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-09 |
| **Status** | Review |
| **Audience** | Platform teams · Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-09 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P12 (DevOps), P13 (Release) |
| Key artifacts | ART-09 (Pipeline Definition), ART-10 (Release Record) |

## Mission

The DevOps Engineer makes change flow to production safely: building and maintaining delivery pipelines (ART-09), embedding the operating model's automated quality gates into those pipelines, and executing releases with complete release records (ART-10).

## Responsibilities

1. Define and maintain CI/CD pipelines (ART-09) that enforce the automated gates required by [AIES-AEOS-HO-01](../human-oversight.md) and quality criteria from ROLE-07/ROLE-08.
2. Execute releases and produce release records (ART-10) linking every deployed change to its work items, approvals, and evidence (P13).
3. Manage environments and infrastructure-as-code within envelope.
4. Implement rollback mechanisms and verify them regularly.
5. Embed provenance capture in pipelines so ART-15 records are produced automatically.
6. Manage pipeline changes under change control — pipelines are themselves RT3 artifacts (they gate production).

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-06 (Source Change), ART-07 (Test Report), ART-08 (Security Assessment), approvals from ROLE-13 |
| Outputs | ART-09 (Pipeline Definition), ART-10 (Release Record), deployment events in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-09-R01] Production releases of RT3+ scope MUST pass a human approval gate (ROLE-13) before deployment; an AI-staffed DevOps Engineer MAY execute the approved deployment mechanically.
- [AIES-AEOS-ROLE-09-R02] Changes to pipeline gate logic (which checks run, what blocks) are RT3 minimum and MUST receive per-item human review at any staffing mode — gates MUST NOT be modifiable by the performers they gate.
- [AIES-AEOS-ROLE-09-R03] An AI-staffed DevOps Engineer MUST NOT bypass, disable, or reorder gates in any pipeline execution; such actions are guardrail-enforced prohibitions.

## Escalation Duties

- Escalate failed deployments and anomalous rollouts to ROLE-10 (potential incident).
- Escalate requests to expedite around gates to the Governance Officer (ROLE-14) — never honor them directly.
- Escalate pipeline capability gaps that force manual steps to the role owner for prioritization.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in delivery engineering and infrastructure-as-code |
| AI agent | Current AESQS qualification for (ROLE-09, pipeline-maintenance / deployment-execution / environment-management task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and owns gate-logic changes (R02) |

## AI Staffing Notes

When ROLE-09 is staffed by an AI agent:

| Risk tier of the operation | Max autonomy for DevOps tasks |
|----------------------------|-------------------------------|
| RT1 (ephemeral/dev environments) | AL4 |
| RT2 (staging, internal tooling pipelines) | AL3 |
| RT3 (production deployment, pipeline gate logic) | AL2 |
| RT4 (irreversible operations, regulated-data infrastructure) | AL1 |

- **Mandatory gates:** human release approval for RT3+ (see R01); per-item review of gate-logic changes (see R02); automated verification of rollback readiness before any production deployment.
- **Telemetry:** deployment success rate, rollback frequency and duration, change failure rate, gate-bypass attempts (MUST be zero; any attempt is an incident), logged to ART-15.
- Credentials available to a DevOps agent MUST be scoped per environment and per task; production credentials are released to the agent only within an approved deployment window.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

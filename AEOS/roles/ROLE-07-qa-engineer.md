# ROLE-07 — QA Engineer

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-07 |
| **Status** | Review |
| **Audience** | QA engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-07 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P10 (Testing & Quality) |
| Key artifacts | ART-07 (Test Suite & Test Report) |

## Mission

The QA Engineer demonstrates correctness: designing test strategies, building and maintaining test suites (ART-07), and producing the evidence quality gates depend on. In an AI-native SDLC, QA evidence also feeds AESQS qualification — test outcomes are part of how agents earn and keep autonomy.

## Responsibilities

1. Define test strategy per work item proportionate to its risk tier (P10).
2. Design, implement, and maintain test suites; verify requirements coverage traceable to ART-02.
3. Produce test reports that gates and audits can consume (ART-07 → ART-15 linkage).
4. Verify that acceptance criteria in work items are objectively testable; push back at planning time when they are not.
5. Independently test AI-produced changes — QA evidence for an agent's output MUST NOT be produced solely by that same agent.
6. Contribute quality telemetry (defect escape, coverage trends) to P16 improvement.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-02 (requirements), ART-05 (Work Item), ART-06 (Source Change) |
| Outputs | ART-07 (Test Suite & Test Report), gate evidence in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-07-R01] Test evidence used at a gate MUST be produced with independence from the performer under test: a different human, a different agent definition, or automated infrastructure — never self-attestation.
- [AIES-AEOS-ROLE-07-R02] An AI-staffed QA Engineer MUST NOT weaken, skip, or quarantine failing tests above AL1 — Assisted; test-suite reductions require per-item human review at any autonomy level.

## Escalation Duties

- Escalate untestable acceptance criteria to ROLE-01/ROLE-02 before implementation starts.
- Escalate quality-gate criteria disputes to the Governance Officer (ROLE-14).
- Escalate suspected systematic quality degradation in an agent's output to the role owner and AESQS re-qualification process.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in test engineering; CL1+ in the relevant stack |
| AI agent | Current AESQS qualification for (ROLE-07, test-design / test-implementation / report-analysis task types) at the target AL, per risk tier |
| Pair | Human meets the human requirement and owns test-strategy decisions |

## AI Staffing Notes

When ROLE-07 is staffed by an AI agent:

| Risk tier of system under test | Max autonomy for QA tasks |
|--------------------------------|---------------------------|
| RT1 — Minimal | AL4 — Autonomous |
| RT2 — Moderate | AL3 — Delegated |
| RT3 — Significant | AL2 — Collaborative |
| RT4 — Critical | AL1 — Assisted |

- **Mandatory gates:** per-item human review of test-strategy documents for RT3 — Significant and above scope; per-item review of any test removal or weakening (see R02); sampling audit of generated test quality (assertion strength, not just coverage numbers).
- **Telemetry:** defect escape rate past agent-authored suites, mutation/assertion-strength scores where available, flaky-test introduction rate, logged to ART-15.
- Independence pairing (R01) MUST be configured in the agent definition: a QA agent instance is not assigned to gate the output of an engineering agent sharing the same definition lineage without explicit Governance Officer approval.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

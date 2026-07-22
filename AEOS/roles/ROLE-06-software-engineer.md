# ROLE-06 — Software Engineer

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-06 |
| **Status** | Review |
| **Audience** | Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-06 |
| Staffing | human / AI agent / human-AI pair |
| Primary phases | P09 (Engineering) |
| Key artifacts | ART-06 (Source Change) |

## Mission

The Software Engineer builds the system: turning work items (ART-05) into source changes (ART-06) that meet requirements, conform to architecture, pass quality gates, and remain maintainable by others (EV4). This is the role most frequently staffed by AI agents, and therefore the role where the operating model's controls are exercised most often.

## Responsibilities

1. Implement work items as source changes with tests (P09), conforming to ADRs (ART-04) and coding standards (ART-13 context assets).
2. Keep changes small, reviewable, and traceable to their work item ([AIES-AEOS-OM-01-R06 — Operating Model, requirement 06](../operating-model.md#2-work-intake-and-flow)).
3. Write and maintain unit tests as part of every change; coordinate with ROLE-07 on broader test coverage.
4. Review source changes produced by other performers when assigned as reviewer.
5. Refactor within envelope to preserve maintainability (P16).
6. Surface security-relevant changes (auth-adjacent code, data handling) to ROLE-08 proactively.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-05 (Work Item), ART-02/ART-03 (requirements, UX specs), ART-04 (ADR), ART-13 (Context Assets) |
| Outputs | ART-06 (Source Change), unit-level contributions to ART-07, provenance records in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-06-R01] Every AI-produced source change MUST be attributable at commit granularity ([AIES-AEOS-OM-01-R18 — Operating Model, requirement 18](../operating-model.md#6-artifact-and-provenance-requirements)) and MUST pass automated quality gates before any human review it requires.
- [AIES-AEOS-ROLE-06-R02] An AI-staffed Software Engineer MUST NOT modify production configuration, schema, or auth-adjacent code (RT3 — Significant examples per Taxonomy §4) above AL2 — Collaborative, nor merge its own changes at any level where a review gate applies.
- [AIES-AEOS-ROLE-06-R03] Changes outside the files/components enumerated in the work item's envelope are envelope breaches and MUST be escalated, not committed.

## Escalation Duties

- Escalate envelope breaches (needing to touch out-of-scope code) to the Human Approver (ROLE-13).
- Escalate ambiguous or contradictory requirements to ROLE-02, and architectural gaps to ROLE-05.
- Escalate repeated gate failures on the same change (default: 2) to the role owner for staffing review.

## Required Qualifications (per AESQS)

| Staffing mode | Requirement |
|---------------|-------------|
| Human | CL2+ in software engineering for the relevant stack |
| AI agent | Current AESQS qualification for (ROLE-06, implementation / refactoring / review task types) at the target AL, per risk tier and per technology scope |
| Pair | Human meets the human requirement; the human is the merge decision-maker where a review gate applies |

## AI Staffing Notes

When ROLE-06 is staffed by an AI agent:

| Risk tier of the change | Max autonomy for engineering tasks |
|-------------------------|-------------------------------------|
| RT1 — Minimal (formatting, scaffolding, prototypes) | AL4 — Autonomous |
| RT2 — Moderate (feature code behind review, internal tooling) | AL3 — Delegated |
| RT3 — Significant (production config, schema, auth-adjacent) | AL2 — Collaborative |
| RT4 — Critical (safety-critical, financial, regulated, irreversible) | AL1 — Assisted |

- **Mandatory gates:** automated quality gates (tests, static analysis, security scan) on every change; per-item human review at AL2 — Collaborative; checkpoint review plus sampling audit at AL3 — Delegated; sampling and post-hoc audits at AL4 — Autonomous per [AIES-AEOS-HO-01 — Human Oversight](../human-oversight.md).
- **Telemetry:** gate pass rate, defect escape rate, review-rejection rate, envelope-breach escalations, token/compute cost per change (EV5) — all logged to ART-15 and consumed by AESQS re-qualification.
- Agent definitions (ART-14) for this role MUST enumerate writable paths, prohibited operations (e.g., dependency addition without review, secret handling), and the test-execution obligations that precede any handoff.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00 — Role Model)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

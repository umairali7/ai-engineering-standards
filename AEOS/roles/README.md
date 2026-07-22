# AEOS Role Catalog

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-00 |
| **Status** | Review |
| **Audience** | All readers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

This catalog indexes the fourteen AEOS role specifications and defines the shared requirements every role specification follows. Role IDs, names, and primary phases are canonical per [Taxonomy §5 (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md#5-ai-engineering-roles); this catalog MUST NOT diverge from them.

---

## 1. Staffing Model

Each role can be staffed by a **human**, an **AI agent**, or a **human-AI pair**, with the responsibilities constant across staffing modes — except ROLE-13 and ROLE-14, which MUST be staffed by humans. Staffing is decided per work item via the procedure in [Operating Model §4 (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md#4-staffing-decision-procedure).

## 2. Role Catalog

| ID | Role | Specification | Staffing options | Primary phases | Key artifacts |
|----|------|---------------|------------------|----------------|---------------|
| ROLE-01 | Planner | [ROLE-01-planner.md](ROLE-01-planner.md) | human / agent / pair | P08 | ART-05 |
| ROLE-02 | Business Analyst | [ROLE-02-business-analyst.md](ROLE-02-business-analyst.md) | human / agent / pair | P02, P05 | ART-01, ART-02 |
| ROLE-03 | Product Manager | [ROLE-03-product-manager.md](ROLE-03-product-manager.md) | human / agent / pair | P03 | ART-02 |
| ROLE-04 | UX Designer | [ROLE-04-ux-designer.md](ROLE-04-ux-designer.md) | human / agent / pair | P04 | ART-03 |
| ROLE-05 | Architect | [ROLE-05-architect.md](ROLE-05-architect.md) | human / agent / pair | P06, P07 | ART-04 |
| ROLE-06 | Software Engineer | [ROLE-06-software-engineer.md](ROLE-06-software-engineer.md) | human / agent / pair | P09 | ART-06 |
| ROLE-07 | QA Engineer | [ROLE-07-qa-engineer.md](ROLE-07-qa-engineer.md) | human / agent / pair | P10 | ART-07 |
| ROLE-08 | Security Engineer | [ROLE-08-security-engineer.md](ROLE-08-security-engineer.md) | human / agent / pair | P11 (X01) | ART-08 |
| ROLE-09 | DevOps Engineer | [ROLE-09-devops-engineer.md](ROLE-09-devops-engineer.md) | human / agent / pair | P12, P13 | ART-09, ART-10 |
| ROLE-10 | SRE | [ROLE-10-sre.md](ROLE-10-sre.md) | human / agent / pair | P14, P15 | ART-11, ART-12 |
| ROLE-11 | Documentation Engineer | [ROLE-11-documentation-engineer.md](ROLE-11-documentation-engineer.md) | human / agent / pair | X08 | documentation across ART-01..12 |
| ROLE-12 | Knowledge Manager | [ROLE-12-knowledge-manager.md](ROLE-12-knowledge-manager.md) | human / agent / pair | X09 | ART-13 |
| ROLE-13 | Human Approver | [ROLE-13-human-approver.md](ROLE-13-human-approver.md) | **human only** | X07 (all gates) | ART-15 (gate decisions) |
| ROLE-14 | Governance Officer | [ROLE-14-governance-officer.md](ROLE-14-governance-officer.md) | **human only** | X04, X05 | ART-14, ART-15 (policy, audit) |

## 3. Shared Role-Specification Requirements

Every role specification (AIES-AEOS-ROLE-01 … AIES-AEOS-ROLE-14) MUST contain the following sections, in this order:

| Section | Contents |
|---------|----------|
| **Mission** | One-paragraph statement of the role's purpose in the operating model |
| **Responsibilities** | Enumerated duties, referencing SDLC phases and cross-cutting domains |
| **Inputs / Outputs** | Artifacts consumed and produced, using canonical ART IDs |
| **Autonomy constraints** | Task-type-level constraints and any role-specific tightening of the RT→AL defaults |
| **Escalation duties** | What this role escalates, to whom, under the triggers of [Operating Model §7](../operating-model.md#7-escalation-model) |
| **Required qualifications** | AESQS qualification scope (competency levels CL1–CL4 per capability area) required to hold the role, per staffing mode |
| **AI staffing notes** | What changes when the role is staffed by an agent: maximum autonomy by risk tier, mandatory gates, and telemetry obligations |

Normative requirements:

- [AIES-AEOS-ROLE-00-R01 — Role Model, requirement 01] Role specifications MUST use the section structure above; deviations require an ADR.
- [AIES-AEOS-ROLE-00-R02 — Role Model, requirement 02] A role specification MUST NOT grant autonomy beyond the RT→AL defaults of [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4); it MAY only tighten them.
- [AIES-AEOS-ROLE-00-R03 — Role Model, requirement 03] Every role's "AI staffing notes" MUST state, per risk tier, the maximum autonomy level at which an agent may perform the role's task types.
- [AIES-AEOS-ROLE-00-R04 — Role Model, requirement 04] A performer (human or agent) MUST NOT hold a role without the qualifications the specification requires; provisional holds pending qualification are limited to AL1 — Assisted participation under supervision.
- [AIES-AEOS-ROLE-00-R05 — Role Model, requirement 05] One performer MAY hold multiple roles on different work items, but MUST NOT hold both a producing role and the Human Approver (ROLE-13) role for the same artifact.

## 4. Reading Order

New adopters SHOULD read the [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) first, then the roles relevant to their teams, then the [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) that connect them.

## Related Documents

- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md) — canonical role IDs, names, and primary phases
- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](../operating-model.md) — staffing decisions and autonomy assignment
- [Workflows (AIES-AEOS-WF-01 — Workflows)](../workflows.md) — how the roles collaborate
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](../human-oversight.md) — the gates roles submit work to

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

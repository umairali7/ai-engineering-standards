# Blueprint: Enterprise Platform

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-ENTERPRISE |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

The general large-enterprise adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01 — Core Reference Architecture)](../core-reference-architecture.md): a multi-business-unit organization with a heterogeneous technology estate, thousands of engineers, federated governance, and mixed regulatory exposure. Industry-specific blueprints in this catalog assume this blueprint as their baseline.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

The defining constraints of the general enterprise are not one regulator but **heterogeneity and scale**:

- **Estate heterogeneity** — decades of technology accumulation: modern services, packaged software, mainframe-era systems, dozens of language ecosystems and toolchains. The platform must meet engineers where they are (AIES-AEAR-CORE-01 §14) rather than assume a green-field stack.
- **Federated organization** — business units with distinct risk appetites, budgets, regulatory exposure, and even competing toolchains. Central mandate alone does not work; neither does full local autonomy.
- **Mixed regulatory exposure** — a typical conglomerate simultaneously faces data-protection law in multiple jurisdictions, sector rules in some business units, and contractual confidentiality everywhere. The platform carries the strictest applicable constraint per data class rather than one global posture.
- **Workforce breadth** — from CL4 platform experts to large populations of CL1–CL2 practitioners ([Taxonomy §6](../../Shared/Taxonomy/README.md#6-competency-levels-cl1cl4)). Defaults must be safe for the least experienced user, not tuned to the most experienced.
- **Vendor leverage** — enterprises of this size are precisely those most exposed to vendor lock-in and best positioned to demand interchangeability; the model gateway's multi-provider posture (AIES-AEAR-CORE-01-R14 — Core Reference Architecture, requirement 14) is a commercial instrument as much as a reliability one.

## 2. Risk-Tier Profile

Typical defaults for the general enterprise. Per [AIES-AEAR-BP-00-R01 — Industry Blueprints, requirement 01], validate locally.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Documentation, test scaffolding, formatting | RT1 — Minimal | Reversible, low blast radius | AL4 — Autonomous |
| Feature code behind mandatory review; internal tooling | RT2 — Moderate | Contained by existing gates | AL3 — Delegated |
| Shared libraries and platform components | RT3 — Significant | Blast radius spans consuming teams | AL2 — Collaborative |
| Production configuration, IaC, schema migrations | RT3 — Significant | Directly production-affecting | AL2 — Collaborative |
| Auth-adjacent code, entitlement logic, secrets handling | RT3 — Significant through RT4 — Critical | Security-critical | AL2 — Collaborative → AL1 — Assisted |
| Changes to the AI platform itself (ART-14, guardrail policy, workflows) | RT3 — Significant and above | Meta-risk: errors amplify through every agent (AIES-AEAR-CORE-01-R45 — Core Reference Architecture, requirement 45) | AL2 — Collaborative → AL1 — Assisted |
| Financial postings, irreversible data operations, external communications | RT4 — Critical | Irreversibility (AIES-AEAR-CORE-01-R29 — Core Reference Architecture, requirement 29) | AL1 — Assisted |

Enterprise-specific note: **cross-business-unit blast radius is a tier escalator**. [AIES-AEAR-BP-ENTERPRISE-R01] A task whose output is consumed by more than one business unit MUST be tiered at least RT3 — Significant unless a documented analysis shows lower impact.

## 3. Architecture Deltas from the Core

### 3.1 Topology: Hub-and-Spoke Federation

The enterprise realizes the multi-tenant topology (AIES-AEAR-CORE-01 §13.2) with business units as tenants, but splits responsibilities between a central hub and federated spokes:

```
                     ┌──────────────────────────────────────────┐
                     │   CENTRAL HUB (enterprise platform org)  │
                     │   Governance Plane (identity, ART-14     │
                     │   registry, audit store, compliance)     │
                     │   Model Plane (gateway, provider mgmt)   │
                     │   Guardrail policy baseline              │
                     │   Observability core (ART-15 system      │
                     │   of record, evaluation service)         │
                     └───────┬──────────────┬───────────────────┘
             federated policy│              │federated policy
        ┌────────────────────▼───┐      ┌───▼────────────────────┐
        │  SPOKE: Business Unit A│      │  SPOKE: Business Unit B│
        │  Interaction surfaces  │      │  Interaction surfaces  │
        │  Orchestration + local │      │  Orchestration + local │
        │  workflows             │      │  workflows             │
        │  BU knowledge stores   │      │  BU knowledge stores   │
        │  Execution sandboxes   │      │  Execution sandboxes   │
        │  Local guardrail       │      │  Local guardrail       │
        │  additions (tighten-   │      │  additions (tighten-   │
        │  only)                 │      │  only)                 │
        └────────────────────────┘      └────────────────────────┘
```

- [AIES-AEAR-BP-ENTERPRISE-R02] Identity, the Agent Definition registry, the audit system of record, and the guardrail policy **baseline** MUST be centrally operated; business units MUST NOT run parallel instances of these.
- [AIES-AEAR-BP-ENTERPRISE-R03] Spokes MAY add guardrail policy and tighten risk-tier defaults; they MUST NOT relax the central baseline (tighten-only federation).
- [AIES-AEAR-BP-ENTERPRISE-R04] Knowledge stores are spoke-scoped by default; cross-BU retrieval MUST be an explicit, entitlement-governed grant, never a side effect of shared infrastructure (extends AIES-AEAR-CORE-01-R49 — Core Reference Architecture, requirement 49).

### 3.2 Plane-Level Deltas

| Plane | Enterprise delta |
|-------|------------------|
| Interaction | Broadest surface diversity of any blueprint: multiple IDE families, chat surfaces, and review tools per BU. The approval console SHOULD be single and central even where other surfaces vary — approvers move between BUs; the gate experience must not |
| Orchestration | Task router incorporates a **qualification directory**: which agent types hold AESQS qualification for which task types per BU. Workflow library is centrally curated with BU-local extensions |
| Model | Gateway is the enterprise's commercial control point: provider contracts, data-handling classes, and cost policy all bind here. Data-handling-class routing (AIES-AEAR-CORE-01-R18 — Core Reference Architecture, requirement 18) carries the per-BU regulatory differences |
| Context & Knowledge | Federated stores with an enterprise-wide standards layer (coding standards, ADR templates, this standard) replicated read-only into every spoke |
| Execution | Connectors for the full heterogeneous toolchain, including mainframe-era change-management systems; where a legacy system cannot express agent identity, a mediation service MUST bridge and log on the platform side ([AIES-AEAR-BP-ENTERPRISE-R05]) |
| Guardrail | Baseline + tighten-only local policy (§3.1); egress allowlists are per-spoke |
| Observability | Central ART-15 system of record with spoke-local buffering for availability; evaluation baselines maintained per BU because norms differ |
| Governance | Federated administration: central ROLE-14 function sets baseline, BU governance officers administer local tightening. Compliance mapping (AIES-AEAR-XC-01-R13 — Cross-Cutting Concerns, requirement 13) is per-BU |

### 3.3 Adoption Staging

Enterprises rarely deploy all planes at full depth on day one. The RECOMMENDED staging preserves the safety invariants at every stage:

```
Stage 1  AL1 — Assisted through AL2 — Collaborative assistance          → Interaction + Model + Guardrail(min)
         (suggestion, drafts)          + Governance identity + basic ART-15
Stage 2  AL2 — Collaborative at scale                → + Context & Knowledge, evaluation
                                       pipelines, full audit correlation
Stage 3  AL3 — Delegated workflows     → + full Orchestration envelopes,
                                       Execution sandboxes, approval consoles
Stage 4  AL4 — Autonomous for RT1 — Minimal task classes    → + continuous evaluation, anomaly-driven
                                       autonomy reduction, mature degradation
```

[AIES-AEAR-BP-ENTERPRISE-R06] No stage may enable an autonomy level whose supporting controls (per the [capability checklist, AIES-AEAR-CORE-01 — Core Reference Architecture §16](../core-reference-architecture.md#16-capability-checklist)) are not yet operating; ambition MUST NOT outrun the checklist.

## 4. Domain-Specific Guardrails

- **Cross-BU containment** — deny agent actions that write outside the initiating BU's scope unless the task carries an explicit cross-BU grant.
- **M&A and divestiture boundaries** — knowledge stores and entitlements MUST support carve-out: a divested unit's data, agents, and audit history can be segregated and exported without contaminating the remainder.
- **Third-party code and data terms** — guardrail policy encodes license and data-use constraints (e.g., no ingestion of restricted third-party documentation into shared knowledge stores).
- **Shadow-AI suppression** — egress control blocks unsanctioned model endpoints estate-wide; the sanctioned path must also be the easiest path, or shadow usage migrates rather than disappears.
- **Change freeze awareness** — orchestration honors enterprise change calendars: RT3 — Significant and above agent-initiated changes are automatically held during freeze windows.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Estate-wide dependency upgrade campaign (hundreds of repos) | P09, P10 | RT2 — Moderate per repo; RT3 — Significant for shared libraries | AL3 — Delegated with per-repo checkpoint sampling; AL2 — Collaborative for the RT3 — Significant shared libraries |
| Legacy system documentation reconstruction | P15, X08 | RT1 — Minimal | AL4 — Autonomous with human spot-audit |
| Cross-BU architecture consistency review (ADR mining) | P07 | RT1 — Minimal (read-only analysis) | AL3 — Delegated |
| Incident postmortem drafting from telemetry | P14, P16 | RT2 — Moderate | AL2 — Collaborative |
| Test-suite generation for under-covered services | P10 | RT2 — Moderate | AL3 — Delegated |
| IaC drift remediation proposals | P12, P14 | RT3 — Significant | AL2 — Collaborative |
| Onboarding assistant answering standards questions from the knowledge layer | X09 | RT1 — Minimal | AL4 — Autonomous |

---

## Related Documents

- [AIES-AEAR-BP-00 — AEAR Blueprint Catalog](README.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture — Enterprise AI Engineering Platform](../core-reference-architecture.md) · [AIES-AEAR-XC-01 — Cross-Cutting Concerns in Platform Architecture](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

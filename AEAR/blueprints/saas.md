# Blueprint: SaaS Product Companies

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-SAAS |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01)](../core-reference-architecture.md) for companies whose product *is* multi-tenant software delivered as a service. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline and addresses the tension between continuous-deployment velocity and the fact that a single defect ships simultaneously to every customer.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

SaaS companies typically have the strongest engineering automation and the thinnest formal governance of any industry in this catalog. The constraints that shape the architecture:

- **Multi-tenancy as the defining risk** — customer data from many organizations lives behind one code base and one operational team. Tenant isolation is the product's core security promise; contractual commitments (data-processing agreements, security addenda) and attestation regimes (SOC 2-style, ISO 27001-style) all reduce to demonstrating that promise holds. An AI engineering platform that ingests production-derived context is a new potential cross-tenant mixing point and must be designed as such from day one.
- **Continuous deployment as the operating model** — many releases per day, trunk-based development, progressive delivery. Governance must ride this pipeline, not fight it: gates are automated checks plus targeted human review, and risk tiering decides which, not whether, controls apply.
- **Two distinct AI surfaces** — internal engineering AI (this architecture's subject) and tenant-facing AI product features (out of core scope, but sharing infrastructure temptations). Conflating them is the characteristic SaaS governance failure.
- **Customer commitments travel downstream** — residency pledges, subprocessor lists, and no-training-on-customer-data commitments made in sales contracts bind the engineering platform's data flows too.
- **Usage-based cost exposure** — inference is a marginal cost that scales with engineering activity; without per-team attribution and enforced budgets, AI spend becomes an unmanaged cost of goods.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01](README.md), validate locally.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Internal tooling, docs, test scaffolding, prototypes | RT1 | Low blast radius | AL4 |
| Product feature code behind flags, review, and progressive delivery | RT2 | Contained by rollout controls | AL3 |
| Public API contract changes, SDK releases | RT3 | Breaking every integrating customer at once | AL2 |
| Shared-service and control-plane changes (routing, provisioning) | RT3 | Single change hits all tenants simultaneously | AL2 |
| Database schema and data-migration changes on tenant data | RT3 | Systematic, hard-to-reverse data damage across tenants | AL2 |
| **Tenant-isolation mechanisms** (authorization, row/namespace scoping, tenancy middleware) | **RT4** | The product's core promise; a defect is a multi-customer breach with notification duties | AL1 |
| Billing, metering, and subscription-entitlement logic | RT4 | Financial transactions and systematic customer harm ([AIES-AEAR-CORE-01-R29]) | AL1 |
| Tenant-facing AI feature guardrails and data-flow config | RT3–RT4 | Customer data exposure through the product's own AI surface | AL2 → AL1 |

[AIES-AEAR-BP-SAAS-R01] Code implementing tenant isolation (authorization checks, tenancy scoping, cross-tenant access mediation) MUST be classified RT4 regardless of change size, and SHOULD be identified structurally (module ownership and call-graph reachability), not by author declaration.

[AIES-AEAR-BP-SAAS-R02] Changes shipping simultaneously to all tenants through a shared control plane MUST be tiered at least RT3 unless deployed under progressive delivery with automated rollback, in which case RT2 MAY apply — the rollout control is what buys the lower tier.

## 3. Architecture Deltas from the Core

### 3.1 Topology

The platform itself is usually single-tenant (one instance for the company's own engineering); the *product* is multi-tenant. Where the company also sells to regulated customers with residency pledges, the model gateway's data-handling-class routing ([AIES-AEAR-CORE-01-R18]) keeps context derived from those tenants inside approved deployments. Model providers used by the engineering platform appear on the customer-facing subprocessor list where contracts require it.

### 3.2 Plane-Level Deltas

| Plane | SaaS delta |
|-------|------------|
| Interaction | Review UIs integrate with the existing pull-request-centric flow — provenance labels ([AIES-AEAR-CORE-01-R03]) render in the tools engineers already live in, or adoption fails. Oversight dashboards show autonomy posture per service alongside deployment state |
| Orchestration | Workflow gates are implemented as pipeline checks wherever the risk tier permits; human gates concentrate at RT3+ merges and RT4 anywhere. The envelope enforcer integrates with the progressive-delivery controller so an agent's change cannot widen its own rollout ([AIES-AEAR-BP-SAAS-R03]) |
| Model | Usage metering attributes cost per team, per repository, and per task type; budgets enforce at request time ([AIES-AEAR-CORE-01-R17]) with team-level quotas as the standing velocity governor. Routing exploits latency classes heavily: interactive completion traffic vs. batch refactoring campaigns |
| Context & Knowledge | **Production tenant data MUST NOT enter engineering knowledge stores or assembled context; context uses synthetic fixtures or irreversibly de-identified derivatives** ([AIES-AEAR-BP-SAAS-R04]). Where a task requires production-shaped data (migration verification), it runs in a governed environment under the same access controls as production, and the context is not retained |
| Execution | Ephemeral environments are the norm already; the delta is discipline — per-task capability grants and default-deny egress ([AIES-AEAR-CORE-01-R24], [R27]) replace the standing broad permissions typical of SaaS CI. Agents deploy only through the progressive-delivery pipeline |
| Guardrail | See §4. Guardrail policy distinguishes the internal engineering AI surface from tenant-facing AI features — separate policy sets, separate budgets, separate audit views |
| Observability | Evaluation pipelines correlate agent-produced changes with deployment outcomes (rollback rate, incident association, error-budget consumption), which becomes the primary AESQS qualification evidence. Anomaly detection watches for cross-tenant access patterns in anything agents touch |
| Governance | Agent identities live in the same identity provider as service accounts, with the distinctness rules of [AIES-AEAR-CORE-01-R42]/[R43]. Compliance reporting feeds the company's attestation evidence (SOC 2-style control operation) so AI-performed engineering is covered by existing audits rather than creating a parallel scope |

[AIES-AEAR-BP-SAAS-R03] An agent operating under progressive delivery MUST NOT be able to advance, widen, or approve the rollout of a change it authored; rollout promotion is a distinct principal's action (human, or a separately enveloped automation at RT2 only).

## 4. Domain-Specific Guardrails

- **Tenant-boundary retrieval filter** — retrieval over any production-derived source is denied unless the source is certified de-identified; raw tenant identifiers in assembled context are a guardrail denial and an investigated event.
- **Isolation-module write lock** — agent-authored changes to designated tenancy/authorization modules are denied unless the task is tiered RT4 with an AL1 workflow; the module list is owned by ROLE-14 and change-controlled.
- **Subprocessor conformance routing** — model-gateway routing honors contractual commitments: context derived from tenants with no-third-party-processing clauses reaches only approved deployments.
- **Blast-radius ceiling** — production-affecting agent actions are limited to progressive-delivery scopes (single cell/region/percentage); global rollout actions always require a human gate.
- **Cost circuit breakers** — per-team and per-campaign budget exhaustion fails closed with escalation ([AIES-AEAR-CORE-01-R17]); long-running autonomous campaigns carry explicit spend envelopes.
- **Product-AI separation** — engineering agents have no entitlements to tenant-facing AI feature infrastructure (its prompts, its data flows); crossing that boundary requires a distinct task and gate.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Test generation for a product microservice | P10 | RT2 | AL3 |
| Feature implementation behind a flag with progressive rollout | P09 | RT2 | AL3 |
| Public API deprecation and versioning change | P07, P09 | RT3 | AL2 |
| Cross-tenant data-migration script | P09, P12 | RT3 | AL2 with staged execution |
| Authorization-middleware refactor | P09 | RT4 | AL1 |
| Metering/billing pipeline change | P09 | RT4 | AL1 |
| Dependency-upgrade campaign across all service repos | P09, P10 | RT2 | AL3 with checkpoint sampling |
| Incident postmortem drafting from telemetry | P14, P15 | RT1 | AL4 with human publish gate |

---

## Related Documents

- [AIES-AEAR-BP-00 — Blueprint Catalog](README.md) · [AIES-AEAR-BP-ENTERPRISE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture](../core-reference-architecture.md) · [AIES-AEAR-XC-01 — Cross-Cutting Concerns](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- SOC 2 — System and Organization Controls 2 (AICPA)
- ISO/IEC 27001 — Information security management systems — Requirements

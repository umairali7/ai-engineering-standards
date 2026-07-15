# Blueprint: Banking & Financial Services

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-BANKING |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01)](../core-reference-architecture.md) for banks, payment institutions, and other regulated financial-services firms. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline and adds the constraints of prudential regulation, transaction criticality, and supervisory auditability.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

Banking is the most heavily supervised software estate most engineers will ever touch. The constraints that shape the architecture:

- **Model risk management regimes** — supervisory guidance on model risk management (e.g., SR 11-7-style regimes, the EU AI Act's high-risk provisions where applicable) was written for credit and market-risk models but supervisors increasingly read it onto any consequential model use. An AI engineering platform's models therefore fall under an existing **model inventory, validation, and periodic-review discipline** — the platform does not get to invent a parallel, lighter one.
- **Auditability expectations** — internal audit, external audit, and supervisors all expect to reconstruct *who changed what, why, under whose approval* for any production system. SOX-style controls over financial reporting systems make change-control evidence a legal artifact, not a courtesy. The core's ART-15 audit trail is the load-bearing answer, and its retention obligations are long (typically 5–10 years).
- **Segregation of duties (SoD)** — the person (or agent) who writes a change must not be the one who approves or deploys it. This maps directly onto the core's gate model but must be demonstrably enforced, including across human-AI pairs.
- **Operational resilience** — regimes such as DORA-style digital operational resilience rules treat critical third-party ICT dependencies (which include model providers) as supervised risk: exit plans, concentration limits, and tested failover are regulatory expectations, not engineering preferences.
- **Data residency and banking secrecy** — customer financial data is jurisdictionally sticky; several jurisdictions impose outright localization or secrecy statutes. Context data derived from production systems inherits these constraints.
- **Fraud/AML system adjacency** — fraud detection, anti-money-laundering monitoring, and sanctions screening are legally mandated control systems. Engineering work *near* them carries elevated risk: a subtle change that degrades detection is a compliance breach with personal-liability exposure for accountable executives.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01](README.md), validate locally against the firm's own risk assessment.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Documentation, test scaffolding, internal prototypes | RT1 | Low blast radius, reversible | AL4 |
| Feature code in non-money-movement services, behind review | RT2 | Contained by existing gates | AL3 |
| Customer-facing behavior, pricing display, disclosures | RT3 | Regulatory conduct exposure (mis-selling, disclosure errors) | AL2 |
| Schema changes to systems of record; batch job logic | RT3 | Ledger integrity blast radius | AL2 |
| Auth, entitlement, and payment-credential handling code | RT3–RT4 | Financial-crime attack surface | AL2 → AL1 |
| **Transaction-processing code paths** (payment initiation, clearing, settlement, ledger posting) | **RT4** | Irreversible money movement; per [AIES-AEAR-CORE-01-R29] and [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4) financial transactions are RT4 by definition | AL1 |
| Fraud/AML/sanctions-screening logic, rules, and thresholds | RT4 | Mandated control system; degradation is a legal breach | AL1 |
| Regulatory reporting pipelines | RT4 | Misstatement to a supervisor is a reportable event | AL1 |
| Interest, fee, and rate calculation engines | RT4 | Systematic customer harm and restitution exposure | AL1 |

[AIES-AEAR-BP-BANKING-R01] Any code path that can initiate, alter, or suppress a financial transaction MUST be classified RT4; proximity analysis (call-graph reachability into transaction paths) SHOULD be used to detect tasks that are transaction-critical despite innocuous framing.

[AIES-AEAR-BP-BANKING-R02] Engineering tasks on fraud, AML, or sanctions-screening systems MUST be tiered RT4 regardless of the apparent size of the change, because effectiveness degradation is not observable in ordinary tests.

## 3. Architecture Deltas from the Core

### 3.1 Topology

Single-tenant ([AIES-AEAR-CORE-01 §13.1](../core-reference-architecture.md#13-deployment-topologies)) or hybrid: externally served models MAY handle RT1–RT2 work on non-customer data classes; work touching customer financial data routes to deployments approved for that data-handling class via the model gateway ([AIES-AEAR-CORE-01-R18]). Jurisdictional subsidiaries with localization obligations replicate the residency pattern of [AIES-AEAR-XC-01 §3.2](../cross-cutting-concerns.md#32-residency-architecture).

### 3.2 Plane-Level Deltas

| Plane | Banking delta |
|-------|---------------|
| Interaction | Approval consoles double as **SoD evidence points**: the console records that approver ≠ author for every gate. Four-eyes (dual human approval) surfaces for RT4 gates |
| Orchestration | Workflow engine encodes SoD as structure: author, reviewer, and deployer roles in a workflow MUST resolve to distinct principals ([AIES-AEAR-BP-BANKING-R03]). Change-freeze integration with the bank's change-advisory calendar |
| Model | The model registry federates into the firm's **model risk inventory**: every model version serving RT2+ engineering work carries a validation status from the independent model-validation function. Provider concentration is tracked as an operational-resilience metric with tested exit paths ([AIES-AEAR-CORE-01-R14] is a supervisory expectation here, not just good practice) |
| Context & Knowledge | Customer financial data MUST NOT enter shared knowledge stores; context for production-adjacent tasks uses masked or synthetic derivatives ([AIES-AEAR-BP-BANKING-R04]). Classification scheme extends with banking-secrecy and jurisdiction tags that drive residency routing |
| Execution | No sandbox has network reachability to production payment networks, core banking systems, or interbank financial-messaging infrastructure — connectivity is structurally absent, not policy-denied ([AIES-AEAR-BP-BANKING-R05]). Synthetic-data test environments stand in for production-like verification |
| Guardrail | See §4. Policy set is reviewed by the compliance function, not only engineering |
| Observability | ART-15 retention aligned to the longest applicable supervisory retention period. Evidence service produces **auditor-consumable bundles**: change → approval chain → test evidence → deployment record, exportable per audit request ([AIES-AEAR-CORE-01-R47]) |
| Governance | Agent identities appear in the firm's access-recertification cycles like human identities. Compliance reporting maps platform evidence to the firm's control framework so that AI-performed work is covered by existing SOX-style control attestations |

### 3.3 Segregation-of-Duties Mapping

The core's gates become the SoD control set:

| SoD requirement | Platform mechanism |
|-----------------|--------------------|
| Author ≠ approver | Workflow engine role-distinctness check; approval console attribution ([AIES-AEAR-CORE-01-R04]) |
| Developer ≠ production deployer | Agents reach production only via CI/CD gates ([AIES-AEAR-CORE-01-R26]); deployment approval is a distinct human gate at RT3+ |
| No self-review by agents | An agent instance MUST NOT review or approve an artifact produced under the same Agent Definition lineage ([AIES-AEAR-BP-BANKING-R06]) |
| Privileged-access separation | Secrets broker issues task-scoped credentials; no principal holds standing production access ([AIES-AEAR-CORE-01-R28], [R33]) |

## 4. Domain-Specific Guardrails

- **Transaction-path write lock** — deny agent-authored changes to designated transaction-critical modules unless the task is explicitly tiered RT4 with an AL1 workflow attached; the module designation list is owned by ROLE-14 and change-controlled.
- **Customer-data egress prohibition** — content inspection blocks account identifiers, payment credentials, and transaction records from prompts, assembled context, and model traffic to any deployment not approved for that data class.
- **Fraud/AML logic shielding** — retrieval policy prevents detection rules, thresholds, and screening lists from entering context for tasks not explicitly authorized on those systems (the rules themselves are financial-crime-sensitive intelligence).
- **Regulatory-disclosure text control** — customer-facing text describing rates, fees, or terms requires a compliance-role human gate before release, regardless of the code change's tier.
- **Jurisdiction pinning** — residency tags on context data drive model-gateway routing; a request carrying data tagged to a localization jurisdiction fails closed if no in-jurisdiction deployment is available.
- **Freeze and blackout awareness** — orchestration holds RT3+ changes during payment-network cutover windows, year-end close, and regulator-mandated freezes.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Test-suite generation for a retail-banking API (non-payment) | P10 | RT2 | AL3 |
| Documentation reconstruction for a legacy batch settlement system (read-only analysis) | P15, X08 | RT1 | AL4 with spot audit |
| Refactoring proposal inside a ledger-posting service | P09 | RT4 | AL1 (AI suggests; human authors) |
| Fraud-rule threshold tuning support (analysis and simulation only) | P09, P10 | RT4 | AL1 |
| IaC drift remediation in non-production environments | P12 | RT2 | AL3 |
| Regulatory-reporting pipeline field-mapping change | P09 | RT4 | AL1 with four-eyes gate |
| Customer-communication template drafting (rates/fees) | P03, P04 | RT3 | AL2 + compliance gate |
| Dependency upgrade campaign across internal tooling repos | P09, P10 | RT2 | AL3 with checkpoint sampling |

---

## Related Documents

- [AIES-AEAR-BP-00 — Blueprint Catalog](README.md) · [AIES-AEAR-BP-ENTERPRISE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture](../core-reference-architecture.md) · [AIES-AEAR-XC-01 — Cross-Cutting Concerns](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- SR 11-7 — Supervisory Guidance on Model Risk Management (US Federal Reserve)
- EU AI Act — Regulation on Artificial Intelligence (European Union)
- DORA — Digital Operational Resilience Act (European Union)
- SOX — Sarbanes–Oxley Act (United States)

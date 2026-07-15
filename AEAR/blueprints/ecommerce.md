# Blueprint: E-Commerce & Retail

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-ECOMMERCE |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01)](../core-reference-architecture.md) for online retailers, marketplaces, and omnichannel commerce estates. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline and adds the constraints of consumer scale, payment adjacency, and an engineering culture built on rapid experimentation.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

E-commerce engineering is defined by a tension the platform must make explicit rather than resolve by default: **velocity is the business model, but trust is the asset**. The constraints that shape the architecture:

- **Payment-card security regimes** — card-data environments are governed by contractual security standards (PCI DSS-style regimes) that draw a hard scope boundary around any system that stores, processes, or transmits cardholder data. Engineering work inside or adjacent to that boundary carries audit consequences; scope creep caused by an AI agent's context or connectivity is itself a compliance failure.
- **Consumer privacy law** — GDPR-, CCPA-style, and similar regimes govern the customer behavioral, order, and profile data that makes commerce context valuable. Consent state, purpose limitation, and deletion obligations attach to exactly the data an engineering platform is most tempted to ingest as context.
- **Consumer-protection and pricing law** — displayed prices, promotions, availability claims, and dark-pattern prohibitions are regulated conduct in most jurisdictions. A code change that mis-renders a price at consumer scale is an incident with legal, not merely reputational, consequences.
- **Experimentation as standard practice** — mature retailers run hundreds of concurrent A/B tests. Experimentation infrastructure is a governed change channel in its own right, and it is also the natural delivery vehicle for progressively exposing AI-produced changes.
- **Extreme seasonality** — a small number of peak trading windows produce a disproportionate share of annual revenue. Change appetite is not constant across the calendar, and the platform must treat that as policy, not folklore.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01](README.md), validate locally.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Internal tooling, test scaffolding, docs | RT1 | Low blast radius | AL4 |
| Storefront feature code behind experiment flags and review | RT2 | Contained by flags, canaries, and existing gates | AL3 |
| Search, ranking, and recommendation pipeline changes | RT2–RT3 | Revenue-shaping at scale; escalates to RT3 where output is a regulated claim (availability, price ordering) | AL3 → AL2 |
| Pricing, promotion, and tax-calculation logic | RT3 | Consumer-protection exposure; systematic error at scale | AL2 |
| Checkout flow, order capture, and inventory commitment | RT3 | Direct revenue path; customer-facing behavior per [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4) | AL2 |
| **Payment processing, stored-credential handling, refunds** | **RT4** | Cardholder-data scope; financial transactions are RT4 by definition ([AIES-AEAR-CORE-01-R29]) | AL1 |
| Customer PII stores, consent management, deletion pipelines | RT4 | Regulated data; deletion errors are irreversible in both directions | AL1 |
| Fraud-screening rules for orders and accounts | RT4 | Control-system degradation is not observable in ordinary tests | AL1 |

[AIES-AEAR-BP-ECOMMERCE-R01] Any engineering task whose change surface intersects the cardholder-data environment MUST be classified RT4, and the intersection check MUST be structural (dependency and deployment-target analysis), not declared by the task author.

[AIES-AEAR-BP-ECOMMERCE-R02] Changes to price computation, promotion eligibility, or tax logic MUST be classified RT3 or higher even when the code change is small, because the blast radius is every concurrent shopper.

## 3. Architecture Deltas from the Core

### 3.1 Topology

Multi-tenant or hybrid per [AIES-AEAR-CORE-01 §13](../core-reference-architecture.md#13-deployment-topologies). Externally served models MAY handle RT1–RT2 work; tasks whose context carries customer PII or payment-adjacent data route via the model gateway's data-handling-class routing ([AIES-AEAR-CORE-01-R18]) to approved deployments only. Marketplace operators serving third-party sellers SHOULD treat seller data segregation with the multi-tenant isolation rules of [AIES-AEAR-CORE-01-R49].

### 3.2 Plane-Level Deltas

| Plane | E-commerce delta |
|-------|------------------|
| Interaction | Oversight dashboards surface **trading-calendar state** (normal / restricted / freeze) alongside autonomy levels, so approvers see the seasonal risk posture at every gate |
| Orchestration | The workflow engine integrates with the **experimentation platform**: AI-produced RT2 changes ship behind experiment flags with automated rollback criteria as a standard workflow step. Autonomy envelopes are **calendar-modulated** (see [AIES-AEAR-BP-ECOMMERCE-R03]) |
| Model | Latency-class routing ([AIES-AEAR-CORE-01-R56]) matters doubly: interactive assistance during incident response on the revenue path gets priority routing. Cost attribution per team is the primary velocity governor |
| Context & Knowledge | Customer PII and cardholder data MUST NOT enter shared knowledge stores; context for storefront work uses masked or synthetic order data ([AIES-AEAR-BP-ECOMMERCE-R04]). Consent and purpose tags propagate through retrieval per [AIES-AEAR-CORE-01-R20] |
| Execution | Sandboxes have no network reachability to the cardholder-data environment — structurally absent, not policy-denied. Load-realistic staging (traffic replay on synthetic data) stands in for production verification of peak-path changes |
| Guardrail | See §4. Guardrail policy consumes the trading calendar as a policy input |
| Observability | Evaluation pipelines correlate agent-produced changes with **experiment outcomes and conversion metrics**, giving AESQS qualification evidence a direct business-metric dimension. Anomaly detection baselines are season-aware |
| Governance | Agent entitlements to promotion, pricing, and inventory systems are time-boxed and recertified before each peak season |

### 3.3 Autonomy Modulation by Trading Calendar

Peak-season change freezes are the industry's existing risk instrument; the platform encodes them as autonomy policy rather than as informal custom.

[AIES-AEAR-BP-ECOMMERCE-R03] The Orchestration Plane MUST consume a change-controlled trading calendar and MUST reduce the maximum permissible autonomy level for designated revenue-path systems during restricted and freeze windows (e.g., AL3 → AL2 in restricted windows; RT2+ changes held entirely during freeze). Calendar overrides are break-glass events per [AIES-AEAR-CORE-01-R35].

This is an application of core principle 6 (*degrade toward human control*): elevated business risk moves autonomy downward on a schedule. Because the window and its end are pre-authorized in the change-controlled calendar, restoration after the window MAY be automatic (and MUST be audited) — unlike failure-triggered degradation, where recovery requires explicit human authorization per [AIES-AEAR-XC-01-R25](../cross-cutting-concerns.md#62-degradation-to-lower-autonomy).

## 4. Domain-Specific Guardrails

- **Cardholder-data scope lock** — deny agent actions (retrieval, execution, deployment) that would touch the cardholder-data environment unless the task is explicitly tiered RT4 with an AL1 workflow; the scope inventory is owned by ROLE-14 and change-controlled.
- **PII egress inspection** — content inspection blocks customer identifiers, addresses, order histories, and payment tokens from prompts, assembled context, and model traffic to deployments not approved for that data class.
- **Price-and-claim gate** — customer-visible text or logic asserting price, discount, availability, or delivery promises requires a human gate at RT3 regardless of change size.
- **Experiment-flag enforcement** — agent-authored storefront changes at RT2+ MUST deploy behind an experiment or feature flag with a predefined rollback trigger; unflagged direct deployment is a guardrail denial.
- **Freeze enforcement** — during freeze windows the action filter denies production-affecting actions on revenue-path systems for all principals, human and agent, with break-glass per [AIES-AEAR-CORE-01-R35].
- **Consent-scope retrieval filter** — retrieval excludes customer data whose consent basis does not cover internal engineering use.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Test-suite generation for a catalog service | P10 | RT2 | AL3 |
| Storefront UI component refactor behind an experiment flag | P09 | RT2 | AL3 |
| Search-ranking feature change with offline evaluation | P09, P10 | RT3 | AL2 |
| Promotion-eligibility rule change before a sale event | P09 | RT3 | AL2 + merchandising gate |
| Checkout latency optimization (peak-path) | P09, P11 | RT3 | AL2, held in freeze windows |
| Refund-processing workflow change | P09 | RT4 | AL1 |
| Consent-management pipeline modification | P09, X02 | RT4 | AL1 |
| Dependency upgrades across internal tooling | P09, P10 | RT2 | AL3 with checkpoint sampling |

---

## Related Documents

- [AIES-AEAR-BP-00 — Blueprint Catalog](README.md) · [AIES-AEAR-BP-ENTERPRISE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture](../core-reference-architecture.md) · [AIES-AEAR-XC-01 — Cross-Cutting Concerns](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- PCI DSS — Payment Card Industry Data Security Standard (PCI Security Standards Council)
- GDPR — General Data Protection Regulation (European Union)
- CCPA — California Consumer Privacy Act (United States, California)

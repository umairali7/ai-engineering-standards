# AEAR Blueprint Catalog

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-00 |
| **Status** | Review |
| **Audience** | All readers |

Industry blueprints show how the [Core Reference Architecture (AIES-AEAR-CORE-01)](../core-reference-architecture.md) specializes under real regulatory and operational constraints. A blueprint is a **worked adaptation**, not a separate architecture: the eight planes and all core normative requirements remain in force; the blueprint adds, tightens, or contextualizes.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. What a Blueprint Contains

Every blueprint follows the same structure so they can be compared and combined:

| Section | Content |
|---------|---------|
| **Industry context** | The regulatory landscape and operational realities that shape the architecture (regulations cited by name, never by vendor solution) |
| **Risk-tier profile** | Which task types typically land at RT3/RT4 in this industry, and why — the single most consequential adaptation, since risk tiers drive maximum autonomy ([Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)) |
| **Architecture deltas** | Plane-by-plane differences from AIES-AEAR-CORE-01: additional components, tightened requirements, topology choices |
| **Domain-specific guardrails** | Guardrail Plane policies particular to the industry |
| **Example use cases** | Representative AI engineering tasks with their typical RT/AL assignments |

## 2. Catalog

| Document ID | Blueprint | Depth | Signature concerns |
|-------------|-----------|-------|--------------------|
| [AIES-AEAR-BP-ENTERPRISE](enterprise-platform.md) | Enterprise Platform | Detailed | The general large-enterprise case: heterogeneous estate, federated governance — read this one first |
| [AIES-AEAR-BP-BANKING](banking.md) | Banking & Financial Services | Detailed | Financial regulation, transaction criticality, model risk management |
| [AIES-AEAR-BP-HEALTHCARE](healthcare.md) | Healthcare & Life Sciences | Detailed | Patient data, clinical safety, regulated software |
| [AIES-AEAR-BP-ECOMMERCE](ecommerce.md) | E-Commerce & Retail | Medium | Consumer scale, payment adjacency, experimentation velocity |
| [AIES-AEAR-BP-MANUFACTURING](manufacturing.md) | Manufacturing | Medium | OT/IT boundary, safety systems, plant-floor realities |
| [AIES-AEAR-BP-GOVERNMENT](government.md) | Government & Public Sector | Medium | Sovereignty, air-gapped operation, procurement |
| [AIES-AEAR-BP-SAAS](saas.md) | SaaS Product Companies | Medium | Multi-tenancy, velocity vs. governance |
| [AIES-AEAR-BP-CARLEASING](car-leasing.md) | Car Leasing & Automotive Finance | Brief | Contract lifecycle, residual value analytics, dealer integrations |
| [AIES-AEAR-BP-OILGAS](oil-gas.md) | Oil & Gas | Brief | HSE criticality, field operations, legacy SCADA adjacency |

## 3. Adapting a Blueprint

1. **Start from the closest blueprint, not from zero.** If your organization spans industries (a bank with an e-commerce arm), combine blueprints per business line — risk-tier profiles compose; take the stricter rule wherever they conflict.
2. **Re-derive the risk-tier profile locally.** Blueprint risk-tier tables are defaults reflecting typical regulatory exposure. [AIES-AEAR-BP-00-R01] Organizations MUST validate blueprint risk-tier assignments against their own risk assessment before adopting them; blueprint defaults MAY be tightened freely but MUST NOT be loosened without documented risk acceptance per [AIES-SHARED-02 §4].
3. **Record deltas as ADRs.** [AIES-AEAR-BP-00-R02] Every divergence from the selected blueprint (and from AIES-AEAR-CORE-01) MUST be captured as an ADR (ART-04) with rationale and trade-offs.
4. **Keep the core checklist authoritative.** [AIES-AEAR-BP-00-R03] Blueprint adoption MUST NOT be treated as a substitute for self-assessment against the capability checklist in [AIES-AEAR-CORE-01 §16](../core-reference-architecture.md#16-capability-checklist); blueprints add industry items, they never remove core ones.
5. **Revisit on regulatory change.** Blueprints cite regulatory regimes as of the time of writing; organizations remain responsible for tracking the obligations that bind them.

---

## Related Documents

- [AIES-AEAR-00 — Module Overview](../README.md)
- [AIES-AEAR-CORE-01 — Core Reference Architecture](../core-reference-architecture.md)
- [AIES-AEAR-XC-01 — Cross-Cutting Concerns](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

# Blueprint: Car Leasing & Automotive Finance

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-CARLEASING |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01)](../core-reference-architecture.md) for vehicle leasing companies, captive finance arms, and fleet-management providers. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline; where the organization is a regulated lender, the stricter rules of the [Banking blueprint](banking.md) compose on top per [AIES-AEAR-BP-00 §3](README.md).

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

- **Consumer-credit regulation** — lease origination, credit decisioning, and collections fall under consumer-credit and fair-lending regimes (truth-in-lending-style disclosure rules, adverse-action notice duties, anti-discrimination law). Automated decisioning rules attract specific scrutiny: explainability of a declined application is a legal obligation, and emerging AI regulation classifies creditworthiness assessment as high-risk.
- **Contract lifecycle as system of record** — the lease contract drives everything: origination, in-life amendments (mileage changes, transfers), maturity, end-of-term settlement. Contract-management systems are long-lived, often heavily customized, and their calculation engines (payments, early-termination quotes, excess-mileage charges) directly determine what customers legally owe.
- **Residual-value (RV) analytics** — forecasting a vehicle's end-of-term value is the industry's core risk model. RV models are typically governed under model-risk-management discipline because systematic RV error moves the balance sheet; the engineering platform's model registry and the firm's model inventory must not diverge.
- **Dealer and OEM integrations** — quoting, ordering, registration, and remarketing flow through third-party dealer management systems and manufacturer interfaces of very mixed quality and change discipline. Integration code is where customer PII, pricing, and credit data cross organizational boundaries.
- **Vehicle and telematics data** — connected-car data streams introduce privacy obligations (location data is sensitive) and new context sources that must be classification-tagged at ingestion.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01](README.md), validate locally.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Internal tooling, docs, test scaffolding | RT1 | Low blast radius | AL4 |
| Fleet-operations and remarketing tooling behind review | RT2 | Recoverable operational errors | AL3 |
| Dealer/OEM integration adapters | RT3 | Cross-boundary data flows; PII and pricing exposure | AL2 |
| Quoting and pricing display logic | RT3 | Disclosure-accuracy exposure at customer scale | AL2 |
| Contract amendment and end-of-term settlement workflows | RT3–RT4 | Determines legally owed amounts | AL2 → AL1 |
| **Credit-decisioning logic, scorecards, and adverse-action generation** | **RT4** | Regulated automated decisioning; fair-lending liability | AL1 |
| Payment collection, direct-debit, and refund processing | RT4 | Financial transactions ([AIES-AEAR-CORE-01-R29]) | AL1 |
| RV model implementation and recalibration pipelines | RT4 | Balance-sheet risk model under model-risk governance | AL1 |

[AIES-AEAR-BP-CARLEASING-R01] Engineering tasks that can alter credit-decision outcomes, adverse-action content, or customer-owed amounts (payment, settlement, excess-charge calculation) MUST be classified RT4; test evidence for such changes MUST include fairness/disparate-impact regression checks where the applicable regime requires them.

## 3. Architecture Deltas from the Core

| Plane | Car-leasing delta |
|-------|-------------------|
| Interaction | Approval consoles for RT4 credit and settlement changes include the accountable credit-risk or compliance role, not only engineering approvers |
| Orchestration | Workflow gates align to the firm's credit-policy and model-risk approval chains; RV-model changes route through the independent validation function before deployment gates open |
| Model | The platform's model registry federates with the firm's **model-risk inventory** so RV and decisioning models carry validation status; the engineering platform's own inference use is inventoried under the same discipline |
| Context & Knowledge | Customer PII, credit files, and telematics location data MUST NOT enter shared knowledge stores; integration work uses masked or synthetic contract data ([AIES-AEAR-BP-CARLEASING-R02]). Dealer-submitted data is tagged as external-origin and lower-trust at ingestion |
| Execution | Sandboxes have no reachability to production payment rails, credit-bureau interfaces, or live dealer/OEM endpoints; integration testing runs against contract-conformant simulators |
| Guardrail | See §4 |
| Observability | ART-15 retention matches consumer-credit record-keeping periods; evidence bundles support regulator and auditor requests on decisioning changes |
| Governance | Agent entitlements to decisioning and settlement systems are recertified on the credit-policy review cycle |

## 4. Domain-Specific Guardrails

- **Decisioning write lock** — agent-authored changes to scorecards, decision rules, or adverse-action templates are denied outside an RT4/AL1 workflow with credit-risk sign-off.
- **Disclosure-text gate** — customer-facing text stating rates, payments, fees, or termination charges requires a compliance human gate regardless of change tier.
- **Bureau-data egress prohibition** — credit-bureau responses and identifiers are blocked from prompts, context, and model traffic to unapproved deployments.
- **Third-party boundary inspection** — payloads to dealer/OEM endpoints pass content inspection so agent-built adapters cannot over-share customer or pricing data.
- **RV-model change freeze** — orchestration holds RV recalibration deployments during financial close and portfolio-revaluation windows.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Test-suite generation for a quoting service | P10 | RT2 | AL3 |
| Documentation of a legacy contract-management system | P15, X08 | RT1 | AL4 with spot audit |
| New OEM ordering-interface adapter | P09 | RT3 | AL2 |
| End-of-term settlement calculation change | P09 | RT4 | AL1 |
| RV-model feature-pipeline refactor | P09 | RT4 | AL1 with validation-function gate |
| Collections-workflow reminder logic | P09 | RT3 | AL2 + compliance gate |

---

## Related Documents

- [AIES-AEAR-BP-00 — Blueprint Catalog](README.md) · [AIES-AEAR-BP-BANKING — Banking & Financial Services](banking.md) · [AIES-AEAR-BP-ENTERPRISE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture](../core-reference-architecture.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- TILA — Truth in Lending Act (United States)

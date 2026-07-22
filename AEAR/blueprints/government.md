# Blueprint: Government & Public Sector

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-GOVERNMENT |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01 — Core Reference Architecture)](../core-reference-architecture.md) for government agencies, public-sector bodies, and their delivery partners. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline and adds the constraints of sovereignty, classified environments, public accountability, and procurement law.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

Government engineering answers to the public, not to a market, and its constraints are correspondingly structural:

- **Sovereignty and data residency** — citizen data, and in many regimes the systems processing it, must remain under national jurisdiction: in-country hosting, nationally cleared personnel, and legal immunity from foreign compelled disclosure. These obligations attach to context data, model traffic, and telemetry alike — not just to production databases.
- **Security classification regimes** — government information carries formal classification markings with mandated handling, and the highest tiers require accredited, physically isolated (air-gapped) environments. An engineering platform that mixes classification levels in one context window has committed a spill, which is a security incident with mandatory reporting.
- **Public procurement law** — competitive procurement, anti-lock-in expectations, and auditability of supplier selection align naturally with this architecture's vendor neutrality (core principle 1): every model, knowledge store, and execution capability behind a platform-owned interface is also a substitutable procurement lot. Exit and re-competition are architectural requirements, not aspirations.
- **Transparency and audit expectations** — freedom-of-information regimes, public audit offices, parliamentary or congressional oversight, and administrative-law duties (reasons for decisions affecting citizens) mean the ART-15 audit trail may be disclosed, litigated, or tabled publicly. Emerging algorithmic-transparency registers extend this to the use of AI itself.
- **Accessibility mandates** — public digital services are legally required to meet accessibility standards (WCAG-style conformance under statutory instruments). Accessibility (X14) is a compliance property of citizen-facing output, not a quality nicety.
- **Long system lifetimes** — public systems routinely outlive the platforms, suppliers, and languages that built them; evidence and knowledge retention horizons are measured in decades.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01 — Industry Blueprints, requirement 01](README.md), validate locally against the agency's accreditation framework.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Internal tooling, documentation, prototypes on unclassified data | RT1 — Minimal through RT2 — Moderate | Standard blast radius | AL3 — Delegated through AL4 — Autonomous |
| Internal case-working and administrative system features | RT2 — Moderate–RT3 — Significant | Operational disruption to public service delivery | AL3 — Delegated → AL2 — Collaborative |
| Citizen-facing digital service behavior and content | RT3 — Significant | Public trust, accessibility law, administrative-law exposure | AL2 — Collaborative |
| Identity, authentication, and citizen-credential systems | RT3 — Significant through RT4 — Critical | Population-scale attack surface | AL2 — Collaborative → AL1 — Assisted |
| **Benefits, tax, fines, and entitlement calculation logic** | **RT4 — Critical** | Determinations affecting citizens' legal rights; systematic error is mass administrative injustice | AL1 — Assisted |
| Systems processing classified information | RT4 — Critical | Classification regime governs; spill risk | AL1 — Assisted |
| Elections, public-safety dispatch, justice, and border systems | RT4 — Critical | Democratic and safety criticality; irreversible consequences | AL1 — Assisted |

[AIES-AEAR-BP-GOVERNMENT-R01] Any code path that computes or alters a determination affecting a citizen's legal rights or entitlements MUST be classified RT4 — Critical; explainability of the determination logic is part of the acceptance criteria, since administrative law may require reasons to be given.

[AIES-AEAR-BP-GOVERNMENT-R02] Task risk tiers MUST be derived jointly from change blast radius and the classification level of the data in context; the higher-resulting tier governs.

## 3. Architecture Deltas from the Core

### 3.1 Topology

Sovereignty drives topology. Unclassified estates use single-tenant deployments within nationally approved hosting; classified estates use the air-gapped topology of [AIES-AEAR-CORE-01 — Core Reference Architecture §13.3](../core-reference-architecture.md#13-deployment-topologies) — this blueprint is that section's worked example. Model serving, knowledge stores, telemetry, and audit stores all remain inside the accredited boundary; failover is redundancy across internal deployments ([AIES-AEAR-CORE-01-R51 — Core Reference Architecture, requirement 51]).

[AIES-AEAR-BP-GOVERNMENT-R03] Every plane, including the Observability and Governance Planes, MUST be deployable within the jurisdiction's sovereignty boundary; telemetry, audit records, and assembled context MUST NOT transit or rest outside it. Data-handling-class routing at the model gateway ([AIES-AEAR-CORE-01-R18 — Core Reference Architecture, requirement 18]) enforces this per request.

[AIES-AEAR-BP-GOVERNMENT-R04] Where multiple classification levels are served, the platform MUST run separate instances (or accredited equivalent isolation) per level; context assembly MUST NOT combine content across classification levels, and cross-level transfer follows the estate's accredited transfer procedures only.

### 3.2 Plane-Level Deltas

| Plane | Government delta |
|-------|------------------|
| Interaction | Surfaces display classification markings on all AI-produced content alongside provenance ([AIES-AEAR-CORE-01-R03 — Core Reference Architecture, requirement 03]). Approval consoles capture the approver's clearance and role for the audit record. Interaction surfaces themselves meet accessibility standards — public-sector engineers include users of assistive technology |
| Orchestration | Task routing respects clearance: tasks on classified material route only to agent instances and human principals cleared for that level. Workflow gates map onto the agency's assurance and accreditation checkpoints |
| Model | The model registry doubles as the **procurement substitution record**: capability classes are specified vendor-neutrally so re-competition can replace a provider without re-architecture. Air-gapped estates operate the gateway against internally hosted models only |
| Context & Knowledge | Classification tagging is mandatory at ingestion and propagates end-to-end ([AIES-AEAR-CORE-01-R20 — Core Reference Architecture, requirement 20]); retrieval enforces need-to-know within clearance. Knowledge retention aligns to public-records law — some context assets are themselves disclosable records |
| Execution | Sandboxes in classified estates are provisioned from internally mirrored, integrity-verified toolchains and package registries; the update channel is a controlled-transfer supply-chain surface. Accessibility checks run as pipeline quality gates for citizen-facing artifacts ([AIES-AEAR-BP-GOVERNMENT-R05]) |
| Guardrail | See §4. Guardrail policy is part of the system's accreditation evidence and changes re-trigger assurance review at the affected level |
| Observability | ART-15 records are written to public-records retention standards and structured for disclosure review (redactable fields separated from structural fields). Algorithmic-transparency reporting is generated from the Agent Definition registry and activity evidence |
| Governance | Agent identities carry clearance-equivalent attributes assigned by the accrediting authority. Compliance reporting maps evidence to the jurisdiction's security-assessment framework, so platform operation stays within continuous-accreditation arrangements |

[AIES-AEAR-BP-GOVERNMENT-R05] Citizen-facing artifacts produced or modified by agents MUST pass automated accessibility conformance checks in the pipeline, and RT3 — Significant gates for such artifacts MUST include accessibility evidence in the approval bundle (X14).

## 4. Domain-Specific Guardrails

- **Sovereignty pinning** — requests carrying data tagged to the jurisdiction fail closed if no in-boundary deployment is available; there is no fallback to out-of-jurisdiction capacity.
- **Classification spill prevention** — content inspection blocks material marked above the task's level from prompts, context, and outputs; a blocked spill attempt is escalated as a security event, not merely denied.
- **Determination-logic gate** — changes to entitlement, penalty, or eligibility computation require a human gate that includes the accountable business owner, not only engineering approvers.
- **Disclosure-readiness control** — agent outputs destined for citizen communication or publication pass a records-management step so FOI and archival obligations attach correctly.
- **Procurement-neutrality check** — Agent Definitions, context assets, and workflow templates are screened so they do not embed supplier-specific dependencies that would frustrate re-competition.
- **Election and emergency freezes** — orchestration honors mandated change moratoria (election periods, declared emergencies) for designated systems.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Documentation of a legacy case-management system (unclassified) | P15, X08 | RT1 — Minimal | AL4 — Autonomous with spot audit |
| Test-suite generation for an internal administrative API | P10 | RT2 — Moderate | AL3 — Delegated |
| Citizen-facing form redesign with accessibility evidence | P04, P09 | RT3 — Significant | AL2 — Collaborative + accessibility gate |
| Benefits-calculation rule change support | P09 | RT4 — Critical | AL1 — Assisted with business-owner gate |
| Migration analysis for a decades-old records system | P06, P07 | RT2 — Moderate | AL3 — Delegated (analysis only) |
| Code work inside a classified enclave (air-gapped instance) | P09, P10 | RT4 — Critical | AL1 — Assisted per accreditation |
| FOI-response redaction tooling development | P09 | RT3 — Significant | AL2 — Collaborative |

---

## Related Documents

- [AIES-AEAR-BP-00 — AEAR Blueprint Catalog](README.md) · [AIES-AEAR-BP-ENTERPRIS — Industry BlueprintE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture — Enterprise AI Engineering Platform](../core-reference-architecture.md) · [AIES-AEAR-XC-01 — Cross-Cutting Concerns in Platform Architecture](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- WCAG — Web Content Accessibility Guidelines (W3C)

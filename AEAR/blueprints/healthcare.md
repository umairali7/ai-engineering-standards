# Blueprint: Healthcare & Life Sciences

| | |
|---|---|
| **Document ID** | AIES-AEAR-BP-HEALTHCARE |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Engineering leadership |

Adaptation of the [Core Reference Architecture (AIES-AEAR-CORE-01 — Core Reference Architecture)](../core-reference-architecture.md) for healthcare providers, payers, health-tech firms, and life-sciences organizations. Assumes the [Enterprise Platform blueprint](enterprise-platform.md) as baseline and adds the constraints of patient-data protection, clinical safety, and regulated software lifecycles.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Industry Context

Two obligations dominate: **patients must not be harmed** and **patient data must not leak**. Everything else is derivative.

- **Patient data protection** — health-privacy regimes (HIPAA-style rules, GDPR special-category provisions, and national health-data laws) treat health information as the most protected data class in commercial computing. Obligations attach not just to production databases but to *any copy*: logs, test fixtures, telemetry — and, on this platform, assembled context, prompts, and model traffic. A model prompt containing patient data is a disclosure event under most regimes.
- **Clinical safety** — software that is a medical device, or that sits near clinical decisions, can injure or kill through defects. Regulated-device software falls under medical-device software lifecycle standards (IEC 62304-style lifecycles, risk management per ISO 14971-style processes, and pre-market regulatory clearance regimes for software as a medical device). Even *unregulated* software adjacent to clinical workflows — order routing, results display, alert delivery — shares the hazard profile without the formal classification.
- **Regulated software lifecycles** — for device-classified software, every change traces to requirements, hazards, verification, and a controlled release: the design history file discipline. AI-performed engineering does not exempt an artifact from this traceability; it raises the evidentiary bar, because the manufacturer remains legally responsible for AI-authored code exactly as for human-authored code.
- **Consent and secondary use** — patient data is collected for care, not for engineering. Using it as context data, test data, or evaluation data is a *secondary use* that requires a lawful basis: consent, or defensible de-identification.
- **Interoperability estate** — clinical data moves through healthcare-specific interchange standards and messaging interfaces; integration errors (unit mismatches, patient-identity mismatches) are a classic clinical-harm vector.

## 2. Risk-Tier Profile

Typical defaults; per [AIES-AEAR-BP-00-R01 — Industry Blueprints, requirement 01](README.md), validate locally — clinical-risk assessment (hazard analysis) is the local authority, not this table.

| Task type | Typical tier | Rationale | Default max AL |
|-----------|-------------|-----------|----------------|
| Documentation, internal tooling, test scaffolding (no patient data) | RT1 — Minimal | Low blast radius | AL4 — Autonomous |
| Administrative/back-office systems (scheduling, billing logic behind review) | RT2 — Moderate | Contained; no direct clinical path | AL3 — Delegated |
| Systems handling identifiable patient data (portals, records access, claims) | RT3 — Significant | Privacy breach blast radius | AL2 — Collaborative |
| Clinical-data interchange interfaces (message parsing, terminology/unit mapping, patient-identity matching) | RT3 — Significant through RT4 — Critical | Silent data corruption becomes clinical harm | AL2 — Collaborative → AL1 — Assisted |
| **Clinical-decision-adjacent code** (order entry, dosing calculation, alerting, results display, triage logic) | **RT4 — Critical** | Defects reach the point of care; safety-critical per [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4) | AL1 — Assisted |
| Software classified as (or embedded in) a medical device | RT4 — Critical | Regulated lifecycle; change control is a legal obligation | AL1 — Assisted |
| De-identification and consent-management logic | RT4 — Critical | A defect converts the whole downstream estate into a breach | AL1 — Assisted |

[AIES-AEAR-BP-HEALTHCARE-R01] Code whose output can influence a clinical decision — directly (dosing, alerts) or through presentation (results display, ordering defaults) — MUST be classified RT4 — Critical; "adjacent" is determined by clinical hazard analysis, not by system naming.

[AIES-AEAR-BP-HEALTHCARE-R02] Changes to device-classified software MUST flow through the manufacturer's regulated change process; the platform's gates supplement, and MUST NOT substitute for, that process.

## 3. Architecture Deltas from the Core

### 3.1 Topology

Single-tenant or hybrid ([AIES-AEAR-CORE-01 — Core Reference Architecture §13](../core-reference-architecture.md#13-deployment-topologies)): identifiable patient data classes route only to deployments approved for health data (in-jurisdiction, contractually bound), enforced by data-handling-class routing ([AIES-AEAR-CORE-01-R18 — Core Reference Architecture, requirement 18]). Many organizations run RT1 — Minimal through RT2 — Moderate work on external capacity and confine health-data classes to dedicated deployments.

### 3.2 Plane-Level Deltas

| Plane | Healthcare delta |
|-------|------------------|
| Interaction | Review UIs for RT4 — Critical clinical-adjacent changes display the linked hazard-analysis items alongside the diff, so reviewers judge clinical impact, not just code quality. Approval gates for device software integrate the quality-management sign-off roles |
| Orchestration | Workflows for device-classified repositories embed the regulated lifecycle's stages (requirements trace → implementation → verification → release record) so agent work lands inside the design-history discipline automatically |
| Model | Model registry records, per model version, whether it is approved for health-data classes. Inference on identifiable patient data is exceptional and logged as a disclosure-relevant event |
| Context & Knowledge | The load-bearing delta — see §3.3. Consent and de-identification controls sit at ingestion |
| Execution | Sandboxes for patient-data-system tasks use **synthetic or de-identified fixtures only**; production clinical systems are unreachable from execution environments ([AIES-AEAR-BP-HEALTHCARE-R03]). Interchange-interface changes get contract-test harnesses with clinically realistic edge cases (units, identity collisions) |
| Guardrail | See §4. Content inspection is tuned for health-data patterns (identifiers, record numbers, clinical narrative) in both directions |
| Observability | ART-15 and telemetry MUST NOT capture identifiable patient data in the clear ([AIES-AEAR-BP-HEALTHCARE-R04]); where context references are logged, they are pointers into access-controlled stores. Evaluation of clinical-adjacent output quality includes clinician-in-the-loop review, not only automated scoring |
| Governance | Compliance mapping covers both privacy regimes and, where applicable, the medical-device quality-management system. Agent access to patient-data classes appears in access-audit reporting like human access |

### 3.3 Consent and De-Identification for Context Data

Patient data reaching the Context & Knowledge Plane is the blueprint's central hazard.

- [AIES-AEAR-BP-HEALTHCARE-R05] Identifiable patient data MUST NOT be ingested into knowledge stores or context assets. Ingestion pipelines MUST apply validated de-identification (or verify consent covering the specific secondary use) before indexing, and the de-identification method MUST be documented and periodically re-validated against re-identification risk.
- [AIES-AEAR-BP-HEALTHCARE-R06] Data classification ([AIES-AEAR-CORE-01-R20 — Core Reference Architecture, requirement 20]) MUST distinguish at minimum: identifiable health data, de-identified health data, and limited datasets — because each carries different permissible flows, and classification drives gateway routing and guardrail policy.
- [AIES-AEAR-BP-HEALTHCARE-R07] Where a task genuinely requires identifiable data (e.g., debugging a specific record-processing failure), the grant MUST be per-task, minimum-necessary, human-approved, and produce a disclosure-accounting record.
- Re-identification risk compounds: retrieval can join individually de-identified fragments. Retrieval policy SHOULD limit cross-source aggregation on health-data classes.

## 4. Domain-Specific Guardrails

- **Patient-identifier egress block** — content inspection denies identifiable health data in prompts, context, model traffic, and logs destined for any deployment not approved for that class; fails closed.
- **Clinical-module write lock** — agent-authored changes to designated clinical-decision-adjacent modules are denied unless the task carries RT4 — Critical/AL1 — Assisted classification with linked hazard-analysis reference; the module list is owned by the clinical-safety function.
- **Device-lifecycle enforcement** — merges to device-classified repositories require the regulated process's verification evidence attached; the platform gate checks for its presence.
- **Terminology and unit safety** — changes touching clinical terminology mappings, units of measure, or reference ranges trigger a mandatory specialist review gate regardless of diff size.
- **Consent-scope enforcement** — retrieval filters exclude data whose consent or de-identification status does not cover engineering use; absence of status metadata is treated as "not permitted".
- **Test-data honesty** — guardrails block production data snapshots from entering execution sandboxes; synthetic-data generation is the sanctioned path.

## 5. Example Use Cases

| Use case | Phases | Typical RT | Typical AL |
|----------|--------|-----------|------------|
| Test generation for a claims-processing service (synthetic data) | P10 | RT2 — Moderate | AL3 — Delegated |
| Documentation of a legacy interchange interface from message samples (de-identified) | P15, X08 | RT1 — Minimal | AL4 — Autonomous with spot audit |
| Refactoring inside a dosing-calculation library | P09 | RT4 — Critical | AL1 — Assisted |
| Drafting hazard-analysis updates from incident telemetry | P16, X05 | RT3 — Significant | AL2 — Collaborative (clinical-safety human owns the artifact) |
| Patient-portal UI feature behind review (no clinical logic) | P09, P04 | RT2 — Moderate–RT3 — Significant | AL3 — Delegated → AL2 — Collaborative |
| De-identification pipeline rule change | P09 | RT4 — Critical | AL1 — Assisted |
| Interchange mapping update (new lab-result code) | P09, P10 | RT3 — Significant | AL2 — Collaborative with specialist gate |
| On-call runbook drafting for a scheduling system | P14, X08 | RT1 — Minimal | AL4 — Autonomous |

---

## Related Documents

- [AIES-AEAR-BP-00 — AEAR Blueprint Catalog](README.md) · [AIES-AEAR-BP-ENTERPRIS — Industry BlueprintE — Enterprise Platform](enterprise-platform.md) · [AIES-AEAR-CORE-01 — Core Reference Architecture — Enterprise AI Engineering Platform](../core-reference-architecture.md) · [AIES-AEAR-XC-01 — Cross-Cutting Concerns in Platform Architecture](../cross-cutting-concerns.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- HIPAA — Health Insurance Portability and Accountability Act (United States)
- GDPR — General Data Protection Regulation (European Union)
- IEC 62304 — Medical device software — Software life cycle processes
- ISO 14971 — Medical devices — Application of risk management to medical devices

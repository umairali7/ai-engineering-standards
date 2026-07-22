# AEOS Governance Operations

| | |
|---|---|
| **Document ID** | AIES-AEOS-GOV-01 |
| **Status** | Review |
| **Audience** | Governance officers · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

This document is the operational governance standard of AEOS (domain X04): the policy hierarchy, the audit trail (ART-15) that evidences the whole operating model, the risk-acceptance mechanism, guardrail management, incident classification for AI-caused failures, the periodic review cycle, compliance reporting, and the operating metrics that show whether the model is working. The Governance Officer ([ROLE-14 — Governance Officer](roles/ROLE-14-governance-officer.md)) owns this document's execution; it uses the canonical scales of the [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) throughout.

---

## 1. Purpose

The [Operating Model (AIES-AEOS-OM-01 — Operating Model)](operating-model.md) and [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](human-oversight.md) standards define controls; this document keeps them honest over time. Governance operations exist to answer three questions continuously and with evidence: is the operating model being followed, is it working, and when it fails, does the organization learn. A control that is never audited, a guardrail that is never tested, and an incident that never feeds back into qualifications are all the same defect: governance on paper only.

## 2. Policy Hierarchy

AEOS-conformant organizations operate a three-layer policy hierarchy. Lower layers specialize higher layers; they never contradict them.

| Layer | Owner | Contents | May it loosen the layer above? |
|-------|-------|----------|-------------------------------|
| **1. Organizational policy** | Executive + ROLE-14 | The organization's instantiation of AEOS: risk-tier definitions and any tightened RT→AL caps, gate placements, retention periods, approved tool and model classes | n/a (top layer; bounded by AIES itself) |
| **2. AIES module standards** | The AIES standard | The normative requirements of AEOS, AESQS, AEAR, and the shared taxonomy | No — deviations require documented risk acceptance (§4) |
| **3. Team norms** | Team leads | Local working agreements: reviewer rosters, unit-size conventions, escalation contacts, agent usage patterns | No — team norms MAY only tighten layers 1–2 |

- [AIES-AEOS-GOV-01-R01 — Governance Operations, requirement 01] Every organization operating under AEOS MUST maintain a written organizational policy instantiating this module, owned by ROLE-14, versioned, and traceable to the AIES version it implements.
- [AIES-AEOS-GOV-01-R02 — Governance Operations, requirement 02] On conflict between layers, the stricter provision prevails by default. A team MUST NOT resolve a conflict by adopting the looser provision; unresolved conflicts escalate to ROLE-14, whose written determination is recorded in the audit trail.
- [AIES-AEOS-GOV-01-R03 — Governance Operations, requirement 03] Loosening any MUST-level AIES requirement — including RT→AL autonomy caps ([Taxonomy §4](../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)) and mandatory gates ([AIES-AEOS-HO-01 — Human Oversight §2](human-oversight.md#2-gate-taxonomy)) — MUST follow the risk-acceptance procedure in §4. Tightening never requires approval.

## 3. Audit Trail Requirements

The audit trail record (ART-15, [Taxonomy §7](../Shared/Taxonomy/README.md#7-artifact-types)) is the evidentiary backbone of AEOS. If it is not in the audit trail, governance treats it as not having happened.

- [AIES-AEOS-GOV-01-R04 — Governance Operations, requirement 04] Every agent action — tool invocation, artifact creation or modification, escalation, gate submission — MUST produce an ART-15 record capturing, at minimum:
  - **Actor identity:** performer (person identity, or agent definition ID and version per [AIES-AEOS-OM-01-R20 — Operating Model, requirement 20](operating-model.md#6-artifact-and-provenance-requirements)) and the accountable human of the work item;
  - **Autonomy context:** declared autonomy level, risk tier, and the envelope in effect;
  - **Inputs:** the work item, prompts and context assets (ART-13, by version), and other material inputs used;
  - **Tools invoked:** each tool or capability exercised, with parameters at a granularity sufficient to reconstruct the action;
  - **Outputs:** artifacts produced or modified (by reference and version) and side effects on external systems;
  - **Approvals:** gate decisions, escalations, overrides, and halts touching the action, each with deciding human and rationale per [AIES-AEOS-HO-01-R03 — Human Oversight, requirement 03](human-oversight.md#2-gate-taxonomy).
- [AIES-AEOS-GOV-01-R05 — Governance Operations, requirement 05] Human gate decisions, autonomy grants, staffing decisions, risk acceptances, and incident lifecycle events MUST equally produce ART-15 records — the trail covers humans and AI alike.
- [AIES-AEOS-GOV-01-R06 — Governance Operations, requirement 06] Audit records MUST be tamper-evident and append-only: corrections are new records referencing the corrected one, never edits in place. The audit store MUST NOT be writable by the agents whose actions it records ([AEAR](../AEAR/README.md) defines the platform mechanism).
- [AIES-AEOS-GOV-01-R07 — Governance Operations, requirement 07] Retention: ART-15 records MUST be retained for the period set by organizational policy, which MUST be at least 18 months and at least the longest applicable regulatory obligation; records tied to an open incident, appeal, or investigation MUST be retained until its closure regardless of age.
- [AIES-AEOS-GOV-01-R08 — Governance Operations, requirement 08] Queryability: the audit store MUST answer, without bespoke engineering effort, at least: all actions by a given performer in a period; all actions on a given artifact or work item; all gate decisions by a given approver; all actions taken under a given autonomy grant; and all uses of a given context-asset (ART-13) or agent-definition (ART-14) version. Reconstruction of any single agent action end-to-end SHOULD take minutes, not days.

## 4. Risk Acceptance

Risk acceptance is the sole mechanism for deviating from a MUST-level requirement of this module, [AIES-AEOS-OM-01 — Operating Model](operating-model.md), or [AIES-AEOS-HO-01 — Human Oversight](human-oversight.md).

- [AIES-AEOS-GOV-01-R09 — Governance Operations, requirement 09] A risk acceptance MUST be written and MUST record: the requirement deviated from; the scope (task types, risk tiers, teams) and the narrowest scope sufficient; the compensating controls; the residual risk and its owner (a named human); an expiry date not exceeding 12 months; and the approving Governance Officer (ROLE-14).
- [AIES-AEOS-GOV-01-R10 — Governance Operations, requirement 10] Risk acceptances MUST NOT be granted for: staffing ROLE-13 or ROLE-14 non-humanly, delegating gate decision authority to an AI system ([AIES-AEOS-HO-01-R20 — Human Oversight, requirement 20](human-oversight.md#7-accountability-model)), disabling the kill-switch, or writing to the audit trail from governed agents.
- [AIES-AEOS-GOV-01-R11 — Governance Operations, requirement 11] Active risk acceptances MUST be reviewed at every governance review (§7); expired acceptances lapse automatically and the deviated-from requirement reapplies in full.

## 5. Guardrail Management

A **guardrail** is a technical control that enforces a policy limit on agent behavior independently of the agent's own judgment — e.g., an action allowlist, a resource or spend cap, a protected-path block, a data-egress filter, or an envelope-breach interceptor per [AIES-AEOS-OM-01-R21 — Operating Model, requirement 21](operating-model.md#7-escalation-model). Guardrails are what make AL3 — Delegated/AL4 — Autonomous envelopes real.

- [AIES-AEOS-GOV-01-R12 — Governance Operations, requirement 12] Every autonomy envelope at AL3 — Delegated or AL4 — Autonomous MUST be enforced by at least one guardrail external to the agent; instructions in a prompt or agent definition are policy inputs, not guardrails, and MUST NOT be counted as enforcement.
- [AIES-AEOS-GOV-01-R13 — Governance Operations, requirement 13] Guardrails MUST be managed as code: versioned, reviewed before change, and tested. Each guardrail MUST have executable tests demonstrating that it blocks what it claims to block, and the test suite MUST run on every guardrail change and on an org-defined recurring schedule (RECOMMENDED at least monthly), with results recorded as evidence (ART-07/ART-15).
- [AIES-AEOS-GOV-01-R14 — Governance Operations, requirement 14] Guardrail changes are RT3 — Significant work minimum (RT4 — Critical where the guardrail protects RT4 — Critical activity) and follow ordinary change control: risk-tiered review, human approval gate, audit trail. ROLE-14 owns guardrail change control and MUST approve any change that widens what agents are permitted to do.
- [AIES-AEOS-GOV-01-R15 — Governance Operations, requirement 15] A failed guardrail test or a detected guardrail bypass MUST suspend the autonomy grants relying on that guardrail until the guardrail is restored and re-tested; the event is treated as an incident (§6).

## 6. Incident Classification and Post-Incident Review

An **AI-caused incident** is an operational incident in which an AI performer's action or output is a direct or contributing cause. Detection and response follow the incident workflow ([AIES-AEOS-WF-01 — Workflows §5](workflows.md#5-incident-response-p14p15)); this section defines classification and the mandatory learning loop.

Severity ladder:

| Severity | Definition | Examples | Mandatory response |
|----------|-----------|----------|--------------------|
| **SEV-4 Contained** | Caught by a gate or guardrail before any external effect | Guardrail block, gate rejection of harmful change | Log and trend (§8); no PIR required, patterns reviewed at §7 |
| **SEV-3 Minor** | Reached production or a shared environment; negligible harm, easily reversed | Bad but quickly reverted config change | Post-incident review (PIR) |
| **SEV-2 Major** | Material service degradation, data quality damage, or internal policy breach | Outage from agent-produced change; misrouted internal data | PIR + suspension of the implicated performer's grants pending review |
| **SEV-1 Critical** | Safety, security, legal, or irreversible-harm impact, or any RT4 — Critical blast radius | Regulated-data exposure; irreversible destructive action | PIR + fleet-level review of all similar grants + ROLE-14 report to executive owner |

- [AIES-AEOS-GOV-01-R16 — Governance Operations, requirement 16] Every AI-caused incident MUST be classified on the severity ladder by ROLE-10 with human confirmation for SEV-1/SEV-2, recorded in the audit trail, and counted in the operating metrics (§8).
- [AIES-AEOS-GOV-01-R17 — Governance Operations, requirement 17] A post-incident review is MANDATORY for every AI-caused incident of SEV-3 or worse. The PIR MUST establish: the causal chain (inputs, context assets, agent definition version, autonomy level, gates passed); why guardrails and gates did not prevent it; and corrective actions with owners and dates. PIRs are blameless toward humans and **evidentiary toward qualifications**: findings about an AI performer are qualification evidence, not blame.
- [AIES-AEOS-GOV-01-R18 — Governance Operations, requirement 18] PIR findings that cast doubt on an AI performer's qualification MUST be forwarded to the AESQS qualification authority as a revision trigger per [AESQS Revision & Revocation §2](../AESQS/revision-and-revocation.md#2-revision-triggers); SEV-1 and SEV-2 findings MUST trigger re-qualification review of the implicated (role, task type) qualification before any suspended grant is restored.
- [AIES-AEOS-GOV-01-R19 — Governance Operations, requirement 19] Corrective actions MUST be tracked as work items (ART-05) to closure, and applicable lessons MUST enter the knowledge-update loop ([AIES-AEOS-WF-01 — Workflows §6](workflows.md#6-knowledge-update-x09-loop)).

## 7. Periodic Governance Reviews

- [AIES-AEOS-GOV-01-R20 — Governance Operations, requirement 20] ROLE-14 MUST commission a governance review on an org-defined cycle, at least quarterly, covering at minimum: operating metrics and trends (§8); audit trail completeness and integrity sampling (§3); gate effectiveness and review-depth indicators ([AIES-AEOS-HO-01 — Human Oversight §4–§5](human-oversight.md#4-anti-rubber-stamping)); guardrail test results and change history (§5); incident and PIR follow-through (§6); active risk acceptances (§4); and the currency of autonomy grants and their expiry dates ([AIES-AEOS-OM-01-R14 — Operating Model, requirement 14](operating-model.md#5-autonomy-assignment)).
- [AIES-AEOS-GOV-01-R21 — Governance Operations, requirement 21] Each review MUST produce a written report with findings, corrective work items (ART-05) with owners and dates, and a follow-up check on the prior review's actions. Reports are retained as governance records per §3 retention.
- [AIES-AEOS-GOV-01-R22 — Governance Operations, requirement 22] A review finding that a control is not operating as designed (e.g., rubber-stamped gates, unlogged actions, untested guardrails) MUST result in either remediation or a documented risk acceptance (§4) — never silent tolerance.

## 8. Metrics

Operating metrics make governance empirical. Organizations MUST track at least the following, segmented by agent (definition and version), task type, risk tier, and team:

| Metric | Definition | What adverse movement means |
|--------|-----------|------------------------------|
| **Gate pass rate** | Share of submissions passing each gate first time | Falling: quality regression; near-100% sustained: possible rubber-stamping ([AIES-AEOS-HO-01-R10 — Human Oversight, requirement 10](human-oversight.md#4-anti-rubber-stamping)) |
| **Escalation rate** | Escalations per completed task, by trigger type ([AIES-AEOS-OM-01 — Operating Model §7](operating-model.md#7-escalation-model)) | Rising: envelope or qualification mismatch; near-zero at AL3 — Delegated+: possible unreported envelope pressure |
| **Autonomy distribution** | Share of tasks executed at each AL, per risk tier | Drift toward higher ALs without matching qualification grants is a control failure |
| **Incident rate** | AI-caused incidents per severity class per period, and SEV-4 guardrail-catch counts | Rising SEV≤3: erosion; falling SEV-4 with rising SEV-3: guardrails weakening |
| **Review depth sampling** | Sampled deep-review finding rates, time-to-decision distributions, rationale quality ([AIES-AEOS-HO-01-R09 — Human Oversight, requirement 09](human-oversight.md#4-anti-rubber-stamping)) | Approval without examination — de facto autonomy inflation |

- [AIES-AEOS-GOV-01-R23 — Governance Operations, requirement 23] Metrics MUST be derived from the audit trail (§3), not self-reported, and MUST be reviewed at every governance review (§7). Thresholds that trigger investigation MUST be defined in organizational policy.
- [AIES-AEOS-GOV-01-R24 — Governance Operations, requirement 24] Metrics evidencing sustained strong performance MAY support autonomy promotion proposals ([AIES-AEOS-WF-01 — Workflows §7](workflows.md#7-autonomy-level-promotion)); metrics evidencing degradation MUST trigger review and MAY trigger immediate demotion per [AIES-AEOS-OM-01-R16 — Operating Model, requirement 16](operating-model.md#5-autonomy-assignment).

## 9. Compliance Reporting

- [AIES-AEOS-GOV-01-R25 — Governance Operations, requirement 25] ROLE-14 MUST produce a periodic compliance report (at least annually, and on demand for auditors and regulators where applicable) stating: the AIES version and organizational policy version in force; conformance status against the normative requirements of AEOS with material deviations and their risk acceptances; incident summary by severity; metrics summary and trends; and open corrective actions. The report draws exclusively on audit-trail-derived evidence.
- [AIES-AEOS-GOV-01-R26 — Governance Operations, requirement 26] Compliance reports MUST be reviewed by the executive owner of AI engineering risk, and material deviations MUST NOT be reported as conformant. Internal or external audits of AEOS conformance MUST be given direct read access to the audit store (§3) within confidentiality constraints.
- [AIES-AEOS-GOV-01-R27 — Governance Operations, requirement 27] For AI participation at **RT3 — Significant or RT4 — Critical**, ROLE-14 MUST ensure an **AI system impact assessment** is performed and recorded before autonomy is granted, and re-reviewed at each governance review (§7) and on any material change of scope, model, or environment. The assessment MUST cover foreseeable impacts on affected individuals and groups — intended and unintended — across the lifecycle, and its findings MUST inform risk-tier assignment (X03) and autonomy limits ([AIES-AEOS-OM-01 — Operating Model §5](operating-model.md#5-autonomy-assignment)). The assessment MAY follow **ISO/IEC 42005** and is retained as a governance record (§3); where an organization already performs a DPIA or a regulatory conformity assessment, that MAY satisfy this requirement if it covers the same scope.

## Related Documents

- [Operating Model (AIES-AEOS-OM-01 — Operating Model)](operating-model.md) — the model these operations govern
- [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](human-oversight.md) — gate requirements and anti-rubber-stamping controls audited here
- [Workflows (AIES-AEOS-WF-01 — Workflows)](workflows.md) — incident response and autonomy promotion workflows
- [Governance Officer (AIES-AEOS-ROLE-14 — Role — Governance Officer)](roles/ROLE-14-governance-officer.md) — the role that executes this document
- [AESQS Revision & Revocation (AIES-AESQS-RR-01 — Revision and Revocation)](../AESQS/revision-and-revocation.md) — where incident findings become qualification consequences

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- ISO/IEC 42005:2025 — Artificial intelligence — AI system impact assessment (impact-assessment guidance referenced by GOV-01-R27)

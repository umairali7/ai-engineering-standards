# ROLE-14 — Governance Officer

| | |
|---|---|
| **Document ID** | AIES-AEOS-ROLE-14 |
| **Status** | Review |
| **Audience** | Governance officers · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

| Attribute | Value |
|-----------|-------|
| Role ID | ROLE-14 |
| Staffing | **human only** ([Taxonomy §5](../../Shared/Taxonomy/README.md#5-ai-engineering-roles)) |
| Primary phases | Cross-cutting X04 (Governance), X05 (Risk Management) |
| Key artifacts | ART-14 (Agent Definition) approval, ART-15 (Audit Trail) oversight |

## Mission

The Governance Officer owns the operating model itself: the policies that constrain AI participation, the risk framework, the audit function, and the assurance that the whole system — humans, agents, gates, guardrails — operates as designed. Where the Human Approver decides individual cases, the Governance Officer sets and verifies the rules those cases are decided under.

## Responsibilities

1. Own and maintain the organization's instantiation of AEOS policy per the hierarchy in [AIES-AEOS-GOV-01 §2](../governance-operations.md#2-policy-hierarchy).
2. Approve agent definitions (ART-14) for activation and material change, jointly with ROLE-08's security assessment.
3. Own risk-tier classification policy and adjudicate contested classifications; approve (or refuse) any documented risk acceptance that loosens an RT→AL default.
4. Operate the audit function: verify audit trail (ART-15) completeness and integrity; commission periodic governance reviews per [AIES-AEOS-GOV-01 §7](../governance-operations.md#7-periodic-governance-reviews).
5. Classify and oversee AI-caused incidents and their mandatory post-incident reviews ([AIES-AEOS-GOV-01 §6](../governance-operations.md#6-incident-classification-and-post-incident-review)).
6. Own guardrail change control ([AIES-AEOS-GOV-01 §5](../governance-operations.md#5-guardrail-management)).
7. Produce compliance reporting (X03) to internal and external stakeholders.
8. Monitor operating metrics ([AIES-AEOS-GOV-01 §8](../governance-operations.md#8-metrics)) and act on adverse trends.

## Inputs / Outputs

| Direction | Artifacts |
|-----------|-----------|
| Inputs | ART-15 (Audit Trail), ART-12 (Telemetry & Evaluation Report), ART-08 (Security Assessment), AESQS qualification records, incident records |
| Outputs | Policy documents, ART-14 activation decisions, risk acceptances, review and compliance reports, all recorded in ART-15 |

## Autonomy Constraints

- [AIES-AEOS-ROLE-14-R01] This role MUST be staffed by a human. AI systems MAY assist with analysis (audit queries, metric aggregation, anomaly detection) but MUST NOT hold policy, risk-acceptance, or agent-activation authority.
- [AIES-AEOS-ROLE-14-R02] The Governance Officer MUST be organizationally independent of the delivery objectives they govern — their performance MUST NOT be measured by delivery throughput.
- [AIES-AEOS-ROLE-14-R03] Risk acceptances that loosen RT→AL defaults MUST be individually documented, time-bounded, and reviewed at each periodic governance review; blanket or evergreen acceptances are prohibited.

## Escalation Duties

- Escalate systemic control failures (audit gaps, repeated guardrail bypass attempts, unmanageable approver load) to executive leadership outside the operating model.
- Escalate legal and regulatory exposure to the organization's legal function.
- De-escalate (revoke) autonomy grants and suspend agent definitions when evidence warrants — this authority is unilateral and immediate.

## Required Qualifications (per AESQS)

| Requirement | Detail |
|-------------|--------|
| Governance competence | CL3+ in engineering governance, risk management, and audit practice |
| AI-systems literacy | CL2+ in AI-system behavior and failure modes — sufficient to interrogate evidence, not to be led by it |
| Independence | Documented reporting line independent of delivery management (R02) |

## AI Staffing Notes

Not applicable for decision authority — this role MUST be human. Governed AI assistance:

- Analysis agents MAY query audit trails, detect anomalies, draft review reports, and monitor metric trends; every such output consumed in a governance decision MUST be labeled and traceable.
- Any agent assisting this role MUST NOT have write access to the audit trail, policy documents, or guardrail configuration it reports on — assistance and enforcement are segregated.
- Assistance agents for governance are themselves subject to the strictest telemetry: full action logging, human review of all findings that trigger interventions, and periodic adversarial evaluation of their blind spots.

## Related Documents

- [Role Catalog (AIES-AEOS-ROLE-00)](README.md) — shared role-specification requirements and staffing model
- [Operating Model (AIES-AEOS-OM-01)](../operating-model.md) — work intake, staffing, autonomy assignment, and escalation
- [Workflows (AIES-AEOS-WF-01)](../workflows.md) — the collaboration workflows this role participates in
- [Human Oversight (AIES-AEOS-HO-01)](../human-oversight.md) — the gates that apply to this role's work

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

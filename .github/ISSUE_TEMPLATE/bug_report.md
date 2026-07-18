---
name: Errata Report
about: Report a defect in the standard — incorrect, ambiguous, inconsistent, or broken content
title: "[Errata] "
labels: ["errata", "needs-triage"]
---

<!--
Use this template for defects in published AIES content. Do NOT use it for:
- New content ideas → use the Content Proposal template
- Security-sensitive flaws (leaked credentials, bypassable guardrail guidance,
  exploitable gaps in recommended controls) → report PRIVATELY per SECURITY.md
-->

## Document

- **Document ID**: <!-- e.g. AIES-SHARED-002 -->
- **Document version**: <!-- from the metadata table, e.g. 0.3.1 -->
- **Section / requirement ID**: <!-- e.g. §4 Risk Tiers, or [AEOS-GOV-01-R03] -->

## What Is Wrong

<!-- Quote the defective text and describe the defect precisely. -->

## Evidence

<!-- Why is it wrong? Contradicting section, taxonomy conflict, factual source,
reproducible inconsistency, broken link target, etc. -->

## Suggested Correction

<!-- Proposed replacement text, if you have one. -->

## Severity

<!-- Check one. -->

- [ ] **Editorial** — typo, formatting, broken link; meaning unaffected
- [ ] **Technical** — incorrect or ambiguous non-normative content; could mislead readers
- [ ] **Normative** — a MUST/SHOULD/MAY requirement is wrong, contradictory, or unimplementable; affects conformance

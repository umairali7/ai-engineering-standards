# Continuous Improvement & Maintenance of the Standard

| | |
|---|---|
| **Document ID** | AIES-DOC-09 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers · Governance officers · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174.

A standard that never changes rots; a standard that changes carelessly loses
trust. This document describes how AIES improves itself over time — a data
flywheel from real qualification runs back into its content and calibration —
and the maintenance cadence that keeps it current. It is AIES applying its own
[AEBOK KA-12 (Evaluation & Continuous Improvement)](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md)
and knowledge-lifecycle ([KA-10](../AEBOK/knowledge-areas/KA-10-context-knowledge.md), X09) to itself.

## 1. The line: what may improve from data, and what may not

This distinction is the whole safety of the scheme:

- **May improve continuously, from evidence:** the scenario suites, rubric
  sub-criteria and anchors, journeys, calibration anchor sets, and guidance
  prose. These are the *content and measurement* layer.
- **Changes ONLY through a human ADR decision:** the normative core — the
  gates, dimension weights, sample-size minimums, autonomy caps, risk tiers,
  and the [Taxonomy](../Shared/Taxonomy/README.md). These define what
  "qualified" *means*.

[AIES-DOC-09-R01] No automated process — including any AI system — MAY alter the
normative core (gates, weights, minimums, autonomy caps, taxonomy). Such changes
are Class 3 and MUST proceed through an ADR per [GOVERNANCE.md](../GOVERNANCE.md).

The reason is [design decision D3](PLATFORM.md): a gate that self-tunes to lift
pass rates is Goodhart's law, and it would make the standard un-trustable — the
one asset that cannot be rebuilt. Self-improvement here means a **sensor →
human → governance** loop, never an autonomous rewrite.

## 2. The improvement flywheel

```
        real qualification runs
              │  evidence records · drift window · calibration · incidents · errata
              ▼
   ┌────────────────────────┐   SENSOR  (platform data — already captured)
   │  signals                │  item analysis (discrimination, difficulty,
   │                         │  rater agreement) · capability drift ·
   │                         │  cross-model clustering · production incidents
   └───────────┬────────────┘
               ▼
   ┌────────────────────────┐   ACTUATOR  (humans — curate & decide)
   │  curate / re-qualify /  │  fix or retire weak scenarios · sharpen anchors ·
   │  propose                │  RR-01 re-qualification · ADR for normative change
   └───────────┬────────────┘
               ▼
   ┌────────────────────────┐   INTERLOCK  (governance + versioning)
   │  versioned change       │  suite-version hashing · document lifecycle ·
   │                         │  ADR gate for Class 3 · CHANGELOG
   └───────────┬────────────┘
               └───────────────► improved standard ──► next runs (loop)
```

The platform is the **sensor**; humans are the **actuator**; governance and
versioning are the **safety interlock**. Every loop ends at a human decision,
and every change is versioned and auditable.

## 3. The specific loops

| Signal | Source (already captured) | Improvement | Who acts | Gate |
|--------|---------------------------|-------------|----------|------|
| A scenario never discriminates (all pass or all fail) | evidence records | retire or replace it | suite maintainer | suite version bump |
| Raters systematically disagree on a dimension | calibration / rating records | sharpen that area's rubric anchors | AESQS editor | Class 2 review |
| Capability drift over the rolling window | drift window (scoring) | re-qualify; investigate suite staleness | qualification authority | RR-01 trigger |
| Models cluster (everyone aces an area) | cross-run comparison | add harder scenarios; consider raising the bar | suite maintainer | suite version bump |
| A production incident on a qualified deployment | incident record | add the failure as a regression scenario; re-qualify | authority + maintainer | RR-01 + suite bump |
| A defect found in the standard text | errata report | correct via the doc lifecycle | module editor | Class 1–3 per change |
| An external framework changes (EU AI Act/GPAI Code, CSA, NIST, ISO, OWASP, ASDLC) | maintainer watch | refresh the [Crosswalk](CROSSWALK.md), affected KAs, and architecture controls | governance officer + module editor | Class 2 review |
| A new agentic attack pattern becomes common | security advisories, incidents, red-team reports | update KA-07, AEAR guardrails, and CA-07/CA-12 scenarios | security editor + suite maintainer | Class 2 review or suite bump |

The highest-value, lowest-cost loop to operate first is **item analysis** — it
reads data the platform already stores and points directly at which content is
weak. It SHOULD be the first improvement capability built once real runs exist,
and not before (building the flywheel with no runs to turn it is waste).

## 4. Maintenance cadence

[AIES-DOC-09-R02] Each normative document SHOULD be reviewed on the cadence
below and either re-affirmed or revised; a review that finds no change still
records that the document was reviewed.

| Cadence | Activity |
|---------|----------|
| **Continuous** | Errata triage; evidence accrual from runs; security-sensitive errata per [SECURITY.md](../SECURITY.md) |
| **Per platform release** | Item-analysis review of touched suites; reviewer-model calibration re-check |
| **Quarterly** | Governance review of operating metrics ([AEOS-GOV-01](../AEOS/governance-operations.md)); suite-health review (discrimination/coverage); security watch for OWASP/NIST/EU/CSA/ASDLC changes affecting agentic delivery |
| **Annual** | Full standard review — every document re-affirmed or revised; taxonomy-stability check; **Crosswalk refresh** against current external frameworks; deprecation review |
| **Trigger-based (out of cadence)** | Production incident; a new model generation that invalidates suite calibration; a change in a mapped external standard; sustained drift; new high-severity agentic attack pattern |

[AIES-DOC-09-R03] Version increments follow the [Versioning Standard
(AIES-STD-05)](standards/versioning-standard.md): content and calibration
improvements are minor/patch; any change to the normative core is a breaking
change requiring a major increment and an ADR.

### Deprecation

[AIES-DOC-09-R04] Retiring a document, scenario, competency area, or level MUST
follow the lifecycle: mark **Deprecated**, name the successor, and retain the
identifier (never reused) so citations do not dangle. Suites retire scenarios by
version bump; the evidence produced under a retired scenario remains valid for
the suite version it was gathered on.

## 5. What this deliberately is not

- **Not an AI rewriting the standard.** The core is human-ADR-gated (R01).
- **Not auto-generated-and-auto-graded scenarios.** New scenarios — including
  any drafted with AI assistance — MUST be human-validated before entering a
  suite; the "expected qualities, not answers" rule reduces but does not remove
  contamination risk.
- **Not silent drift.** Suite versions are content-hashed and results are only
  comparable within a version, so an improvement is always a visible, versioned
  event — never an invisible shift.

## Related Documents

- [AEBOK KA-12 — Evaluation & Continuous Improvement](../AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) — the practice this dogfoods
- [AESQS Revision & Revocation (AIES-AESQS-RR-01)](../AESQS/revision-and-revocation.md) — re-qualification triggers
- [GOVERNANCE.md (AIES-GOV-01)](../GOVERNANCE.md) — decision classes and the ADR gate
- [Versioning Standard (AIES-STD-05)](standards/versioning-standard.md) · [Review Standard (AIES-STD-06)](standards/review-standard.md)
- [Standards Crosswalk (AIES-DOC-07)](CROSSWALK.md) — refreshed on the annual cadence
- [Qualification Platform (AIES-DOC-06)](PLATFORM.md) — the sensor

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- NIST AI 600-1 — Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile
- European Commission — General-Purpose AI Code of Practice (2025) and GPAI guidance under the AI Act
- OWASP GenAI Security Project — 2025 Top 10 for LLMs and GenAI Applications; OWASP Top 10 for Agentic Applications 2026

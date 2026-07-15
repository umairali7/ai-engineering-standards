# KA-12 — Evaluation & Continuous Improvement

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-12 |
| **Status** | Review |
| **Audience** | Engineering leadership · QA engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-12 covers Continuous Improvement (P16) for AI-native delivery — the discipline that turns the rest of AEBOK from a static rulebook into a closed control loop. Every consequential claim in the standard is empirical: that an agent is qualified for a task type, that a gate catches what it should, that curated context helps, that AL3 is safe for this component. KA-12 defines how those claims are measured (EV1–EV6 in practice), how measurement is kept honest as capability and systems drift, and how evidence flows back into autonomy assignments, context assets, and practice. Without this KA, autonomy decisions run on anecdote and first impressions — and an organization's AI participation is governed by whoever tells the most recent story.

## 2. Key Concepts

- **Outcomes, not output.** AI participation makes output cheap; the improvement question is whether *outcomes* improved. Measurement pairs delivery metrics with the evaluation dimensions in practice: defect escape and rework rates (EV1, EV2), incident and vulnerability introduction (EV3), comprehension and change-cost trends (EV4), cost per accepted change (EV5), and audit-trail completeness (EV6). Any single metric optimized alone will be gamed — including by well-meaning humans.
- **Golden task regression as the measurement instrument.** Versioned suites of representative tasks with expected outcomes ([KA-06](KA-06-testing-quality.md)) are the stable ruler against which change is measured — of prompts, context assets, configurations, and the performers themselves. The instrument needs its own maintenance: refresh against real production traffic, and retirement of leaked tasks whose scores no longer measure anything.
- **Capability drift.** An AI performer's effective capability changes without anyone deciding it should — upstream model or configuration changes, evolving context assets, or a shifting task mix. A qualification earned in January is a hypothesis by June. Drift is detected by re-running stable baselines on a cadence and investigating movement in either direction — degradation is a risk, but unexplained improvement also means the instrument or the system changed.
- **Evidence-driven autonomy adjustment.** Autonomy moves in both directions on evidence, per [AESQS](../../AESQS/README.md) qualification data: promotion when scores over a defined window clear tier thresholds, demotion when evaluation, incident, or gate-health signals degrade. Reversibility ([KA-01](KA-01-foundations.md)) is only real if demotion actually happens — an organization that has never reduced an autonomy level is not adjusting on evidence.
- **Feedback loops to context.** Production findings, review rejections, and evaluation failures are the highest-value inputs the context store ([KA-10](KA-10-context-knowledge.md)) can receive: each one localizes a place where curated knowledge was wrong, missing, or stale. The loop from P14–P15 signals back to ART-13 corrections is how the organization's AI capability compounds.
- **Improvement cadence.** Improvement work competes with delivery and loses by default. It survives as scheduled cadences: periodic evaluation reviews per component, retrospectives that examine agent performance and gate health alongside human process, and a standing route from findings to owned work items.

## 3. Core Practices

- **Measure outcomes on the canonical dimensions.** [AIES-AEBOK-KA-12-R01] Organizations MUST define outcome metrics mapped to EV1–EV6 for AI-participating work, record them as telemetry and evaluation reports (ART-12) at a defined cadence, and use them — not throughput or anecdote — as the basis for practice and autonomy decisions.
- **Re-evaluate on a cadence, not on faith.** [AIES-AEBOK-KA-12-R02] Every task type executed at AL2+ MUST be re-evaluated against a versioned golden-task baseline on a defined schedule and after any known change to the performer's configuration or context; unexplained score movement MUST trigger investigation before the affected autonomy assignments are relied upon further.
- **Adjust autonomy only on evidence.** [AIES-AEBOK-KA-12-R03] Changes to an autonomy assignment — in either direction — MUST cite qualification evidence per [AESQS](../../AESQS/README.md) and MUST be recorded with the evidence, the decider, and the review date; demotion paths MUST be exercised when degradation evidence appears, not deferred for delivery convenience.
- **Route findings to owned corrections.** [AIES-AEBOK-KA-12-R04] Defects, incidents, and review rejections attributable to wrong or missing context MUST be routed as correction work items to the owning context assets ([KA-10](KA-10-context-knowledge.md)); golden task suites SHOULD be refreshed from the same findings so the instrument tracks reality.
- **Guard the metrics themselves.** Metrics used in gates or autonomy decisions SHOULD be paired with counter-metrics (e.g., throughput with rework rate, evaluation pass rate with escape rate) and periodically audited for gaming — a metric that only ever improves has usually stopped measuring.
- **Hold the cadence.** Teams SHOULD run improvement reviews on a fixed cadence covering evaluation trends, gate health ([KA-11](KA-11-human-ai-collaboration.md)), and degradation events ([KA-09](KA-09-operations-observability.md)), with findings dispositioned into owned work — not minuted and abandoned.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Golden Task Regression** | A curated, versioned task suite gates change to AI components and doubles as the stable baseline for drift detection. See [catalog](../patterns/README.md#pat-06-golden-task-regression). |
| **Drift Sentinel** | Scheduled baseline re-runs with alerting on score movement in either direction; capability change is detected by instrument, not by incident. |
| **Evidence-Gated Promotion** | Autonomy increases require qualification evidence over a defined window, recorded with the decision and a review date. See [catalog](../patterns/README.md#pat-02-evidence-gated-promotion). |
| **Feedback-to-Context Loop** | Production and review findings become correction work items against owned context assets; the store improves at the organization's learning rate. See [catalog](../patterns/README.md#pat-10-feedback-to-context-loop). |
| **Paired-Metric Guard** | Every gate or promotion metric ships with a counter-metric that detects gaming; both move together or the pair is investigated. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Metric Gaming** | Actors (human or AI) optimize the measured proxy — coverage, pass rate, task count — while the outcome it stood for degrades unmeasured. See [catalog](../patterns/README.md#apat-08-metric-gaming). |
| **Set-and-Forget Autonomy** | Autonomy was assigned on qualification evidence once and never revisited; capability drifts for months under a stale assignment until an incident performs the re-evaluation. |
| **Anecdote-Driven Adjustment** | Autonomy rises after an impressive demo and falls after a memorable failure; decisions track story salience rather than evaluation windows, in both directions. |
| **One-Way Ratchet** | Promotions happen on evidence but demotions never do — degradation evidence is explained away because reducing autonomy would slow delivery; reversibility exists only on paper. |
| **Findings Graveyard** | Retrospectives and evaluation reviews produce findings that are minuted, never owned, and rediscovered verbatim after the next incident; the loop is open exactly where it was drawn closed. |

## 6. Competency Expectations

| Level | Expectation in KA-12 |
|-------|----------------------|
| **CL1** | Explains the EV1–EV6 dimensions and why output volume is not an outcome; runs existing evaluation suites and reads trend reports; files findings through the correction route. |
| **CL2** | Independently maintains golden task suites and re-evaluation schedules for standard components; produces outcome reports (ART-12); drafts evidence cases for autonomy adjustment. |
| **CL3** | Designs the measurement system for a product area — metric/counter-metric pairs, drift baselines, feedback routing; adjudicates contested evidence; leads improvement cadences across teams. |
| **CL4** | Sets organizational evaluation and improvement policy (P16): evidence standards for autonomy change, drift-detection doctrine, portfolio-level outcome review; evolves AIES practice itself from accumulated evidence, through governed change (X04). |

## Related Documents

- Evaluation mechanics, oracles, and suite construction: [KA-06 Testing & Quality Engineering (AIES-AEBOK-KA-06)](KA-06-testing-quality.md).
- Production signals that feed the loop: [KA-09 Operations & Observability (AIES-AEBOK-KA-09)](KA-09-operations-observability.md); gate-health signals: [KA-11 Human-AI Collaboration & Oversight (AIES-AEBOK-KA-11)](KA-11-human-ai-collaboration.md).
- Where corrections land: [KA-10 Context & Knowledge Management (AIES-AEBOK-KA-10)](KA-10-context-knowledge.md); the autonomy model being adjusted: [KA-01 Foundations (AIES-AEBOK-KA-01)](KA-01-foundations.md).
- Qualification scoring and evidence windows: [AESQS (AIES-AESQS-00)](../../AESQS/README.md); evaluation dimensions EV1–EV6: [Taxonomy §8 (AIES-SHARED-02)](../../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6); improvement workflows: [AEOS (AIES-AEOS-00)](../../AEOS/README.md).
- How this KA is applied to the standard itself (the improvement flywheel and maintenance cadence): [Continuous Improvement & Maintenance (AIES-DOC-09)](../../docs/IMPROVEMENT.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

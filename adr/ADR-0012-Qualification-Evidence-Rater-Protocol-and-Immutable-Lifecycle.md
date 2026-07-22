# ADR-0012: Separate evaluation observations from qualification evidence and use immutable lifecycle events

| | |
|---|---|
| **ADR** | ADR-0012 |
| **Status** | Accepted |
| **Deciders** | Umair Ali (repository owner); AESQS Module Editor; Platform Module Editor |
| **Supersedes / Superseded by** | — |
| **Decision date** | 2026-07-22 |

## Context

The platform currently persists one rating record per rater and response, then
passes every admitted rating directly to the statistical scoring engine. A
second rater can therefore increase the apparent sample size and narrow the
confidence interval even though both ratings concern the same evidence item.
The review package also indexes one rating per rater kind, so a second human
rater can overwrite the first in the review view.

Admission is presently based on a declared `human` kind, a self-asserted
`--reviewer-qualified` flag, or an in-run automated calibration result. This
does not verify current rater scope, calibration, independence, double-rating
coverage, or the complete two-human process required by:

- AIES-AESQS-ER-01-R05 — Double-rating coverage is risk-tier dependent;
- AIES-AESQS-ER-01-R06 — Rater agreement is measured and enforced;
- AIES-AESQS-ER-01-R10 — Automated raters are calibrated and are not the sole
  basis for a qualification decision;
- AIES-AESQS-QP-01-R01 — Every qualification decision involves an assessor and
  an independent peer reviewer; and
- AIES-AESQS-QP-01-R15 — Every qualification lifecycle event is immutable.

Qualification Records currently omit parts of the qualification scope tuple,
have no enforced validity window, and are overwritten during invalidation and
revocation. The implementation therefore needs a governed contract change,
not a renderer-only correction.

This ADR distinguishes an **engineering evaluation** from a **qualification**.
Automated evaluation remains useful and may produce advisory observations,
ECM evidence, and human-review input. Qualification is the stricter protocol
that admits evidence only after the AESQS human-accountability requirements are
satisfied.

## Decision Drivers

- Statistical independence: a sample counts evidence items, not ratings.
- Faithfulness to the existing AESQS human and double-rating requirements.
- Preservation of automated evaluation as a useful, clearly advisory workflow.
- Verifiable rater identity, qualification, calibration, scope, and independence.
- Immutable and replayable evidence, decisions, and lifecycle history.
- Backward compatibility: historical evidence is never silently reinterpreted.
- A one-command user workflow may orchestrate steps, but may not erase required
  human decisions or manufacture authority.

## Existing-Contracts Check

- **Can the existing contracts express this?** No. Evidence Package schema v4
  conflates admitted rater observations with the statistical evidence-item
  population. The current Qualification Record has no independently versioned
  lifecycle-event envelope and lacks required scope and validity fields.
- **Which contracts change?** Evidence Package receives a major schema revision
  because the unit of analysis changes from a flat rating list to resolved
  evidence items plus retained observations. Qualification Records become a
  versioned snapshot over immutable qualification lifecycle events. Decision
  conformance cases must prove that additional raters and repeats do not change
  sample adequacy or effective sample size.

## Options Considered

### Option A — Preserve flat ratings and add more warning text

Continue treating every admitted rating as a statistical observation while
warning that double ratings are not independent.

- **Pros:** No schema migration and minimal implementation work.
- **Cons:** The confidence calculation remains statistically wrong; warnings do
  not enforce AESQS; qualification claims remain indefensible.

### Option B — Average all ratings per response automatically

Collapse ratings for each response to a mean score before aggregation.

- **Pros:** Prevents sample-size inflation and is simple to explain.
- **Cons:** Illegally averages unresolved divergences, hides rater provenance,
  does not verify rater qualification or independence, and permits automated
  scores to become the sole basis of a qualification.

### Option C — Separate observations, resolved evidence items, review, and lifecycle events

Retain every rating as an observation, resolve one admitted score per evidence
item through a risk-tier protocol, and record qualification decisions and
status changes as immutable events.

- **Pros:** Matches the statistical unit, preserves provenance, enforces the
  human protocol, keeps automated evaluation useful, and supports replay.
- **Cons:** Requires a schema migration, rater registry/calibration records,
  additional conformance cases, and more explicit user workflow states.

## Decision

We adopt Option C.

1. A response to one scenario execution is an **evidence item**. Repeats are
   separate stability observations but do not create scenario breadth.
2. A rater's scores are **rating observations** linked to an evidence item.
   Rating observations are never passed directly to the qualification
   statistics as independent samples.
3. Qualification aggregation consumes at most one **resolved item score** per
   evidence item and one effective item per distinct scenario for adequacy.
4. Divergences covered by AIES-AESQS-ER-01-R07 are unresolved until a qualified
   human records a disposition. They MUST NOT be averaged automatically.
5. Qualification-mode human raters must have a durable identity, competency and
   risk-tier scope, current calibration record, and conflict declaration.
   Command-line assertion alone is not evidence of qualification.
6. RT1 — Minimal and RT2 — Moderate qualifications independently double-rate
   at least 20% of items. RT3 — Significant and RT4 — Critical qualifications
   independently double-rate every item. Agreement and coverage are recorded
   and gate evidence admission.
7. Automated/model ratings remain first-class, traceable observations. They MAY
   support screening and EV5 — Efficiency / EV6 — Traceability evidence
   gathering as allowed by AESQS. They MUST NOT be the sole basis for a
   qualification decision and MUST NOT silently establish EV1–EV4 qualification
   scores. An automated-only run remains an engineering evaluation and can
   produce an informational ECM, but not decisional qualification evidence.
8. Every qualification decision records a named assessor and an independent
   peer reviewer. A grant authority is separately accountable where the local
   governance model requires it. Grants and denials follow the same two-human
   evidence-review rule.
9. The qualification scope stores the complete AESQS tuple: subject, role,
   phases, maximum risk tier, competency × CL claims, framework version,
   applicable agent-definition version, sponsor, and validity window.
10. Grant, condition change, renewal, suspension, invalidation, revocation, and
    supersession are immutable lifecycle events. A current-state projection may
    be regenerated, but no event or issued record is overwritten.
11. Legacy Evidence Package v4 and existing Qualification Records remain
    readable and retain their original meaning. They are not upgraded into
    qualification-grade v5 evidence by reinterpretation.

## Consequences

**Positive:**

- Confidence intervals and sample sizes reflect evidence rather than rater count.
- Automated review remains operationally valuable without being confused with
  qualification authority.
- Human accountability becomes verifiable rather than a name-only attestation.
- Qualification state can be independently reconstructed from immutable events.
- ECM can display automated observations while qualification remains honest.

**Negative:**

- Automated-only runs that currently become decisional after model calibration
  will instead remain engineering evaluations until the human protocol is met.
- Qualification requires additional human work. Mitigation: risk-tier sampling,
  batch review interfaces, anchor-assisted scoring, and one-command orchestration
  reduce operational burden without removing the required judgment.
- Evidence Package and qualification storage require versioned migrations.
- Existing report and comparison code must understand both legacy and new schemas.

## Compliance & Verification

- Conformance cases prove that two ratings of one item do not increase effective
  sample size or narrow the interval as if they were independent items.
- Tests cover the RT1/RT2 20% and RT3/RT4 100% double-rating rules.
- Tests reject unverified, expired, out-of-scope, conflicted, or uncalibrated
  qualification raters.
- Tests prove an automated-only evaluation cannot become qualification-decisional.
- Tests prove divergence resolution is explicit and never automatic averaging.
- Tests reconstruct current qualification state exclusively from append-only events.
- Tests reject expired qualifications and trigger targeted requalification after
  material subject changes.
- Evidence and qualification schema fixtures cover legacy read compatibility.
- Normative anchors: AIES-AESQS-ER-01-R05/R06/R07/R10,
  AIES-AESQS-QP-01-R01/R02/R14/R15/R16, and
  AIES-AESQS-PR-01-R02 through R10.

## Links

- Pull request: to be added when proposed for review.
- [AIES-AESQS-ER-01 — Evaluation Rubrics](../AESQS/evaluation-rubrics.md)
- [AIES-AESQS-QP-01 — Qualification Process](../AESQS/qualification-process.md)
- [AIES-AESQS-PR-01 — Peer Review](../AESQS/peer-review.md)
- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)
- [AIES-DOC-11 — Compatibility Policy](../COMPATIBILITY.md)
- [AIES-DOC-14 — Vision Execution Backlog](../docs/OSS_MATURITY_TODO.md)

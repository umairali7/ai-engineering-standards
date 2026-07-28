# ADR-0019: Frozen Assessment Instruments and Standards-Assisted Execution

| | |
|---|---|
| **ADR** | ADR-0019 |
| **Status** | Proposed |
| **Deciders** | Pending Maintainer and Module Editor ratification |
| **Supersedes / Superseded by** | — |

## Context

AIES scenarios already contain a task prompt, expected qualities, EV-specific
criteria, failure conditions, and calibration anchors. Baseline candidates
receive only the task, which correctly prevents scoring-key leakage. Automated
reviewers, however, historically received only that task, the response, generic
dimension names, and a coarse scale. This made the reviewer protocol less
specific than the instrument it claimed to apply and allowed later corpus
changes to reinterpret older evidence.

A separate need is emerging: helping an engineering subject perform work with
task-scoped AIES guidance. Such assisted output is useful, but it is not an
unassisted capability observation and must never inflate qualification breadth.

## Decision Drivers

- Preserve held-out, non-coached baseline assessment.
- Bind every response and rating to the exact instrument used.
- Give automated and human reviewers the same complete scoring basis.
- Make score-to-standard traceability inspectable.
- Keep standards-assisted work separate from qualification evidence.
- Support generative and evidence-producing subjects without conflating their
  collection semantics.

## Existing-Contracts Check

- **Can the existing contracts express this?** No. Scenario YAML is an authoring
  format, response records contain only the task, and rating records previously
  had no immutable instrument identity or criterion-evidence contract.
- **If no, which contract is insufficient, and what version bump / conformance
  impact does the change carry?** The platform adds
  `aies-assessment-instrument/v1`, explicit candidate/reviewer projections,
  append-only run snapshots, and informational standards-assisted execution.
  Existing evidence schemas remain readable; legacy migration is permitted only
  when captured prompt and suite version exactly match the current corpus.

## Options Considered

### Option A — Give every candidate the whole standards repository

- **Pros:** Simple implementation; makes standards visible.
- **Cons:** Coaches baseline assessment, leaks hidden criteria, overloads
  context, and prevents a meaningful unassisted capability claim.

### Option B — Keep task-only judging

- **Pros:** Small prompts and no migration work.
- **Cons:** Reviewers cannot apply scenario criteria or calibration anchors,
  score explanations are weak, and the standards-to-score chain is incomplete.

### Option C — Freeze one instrument and expose audience-specific projections

- **Pros:** Preserves blind assessment, grounds review, creates reproducible
  lineage, and permits an explicitly separate assisted mode.
- **Cons:** Larger reviewer contexts and additional immutable artifacts;
  mitigation: context-bounded batching and digest-based deduplication.

## Decision

We adopt Option C. Every scheduled controlled scenario becomes an immutable
assessment instrument before response collection. The candidate projection
contains only the legitimate task. The reviewer projection contains the task,
global and scenario-specific EV anchors, expected qualities, applicability,
failure conditions, calibration anchors, task mappings, and standards
references. Responses and ratings carry the instrument digest.

Automated reviewers remain provenance-blind and cannot decide qualification.
Criterion-level review evidence and protocol conflicts are retained without
silently modifying reviewer scores.

Standards-assisted execution is a distinct informational workflow. It may
compare an unassisted response with a guided response against the same frozen
instrument, but neither the guided response nor its delta is qualification
evidence or deployment authority.

## Consequences

**Positive:**

- Automated and human review use the actual executable instrument.
- Candidate prompts remain uncontaminated by the scoring key.
- Reports can trace standard → competency → instrument → response → rating →
  EV → Engineering Task.
- Assisted engineering value can be measured without corrupting the baseline.

**Negative:**

- Reviewer prompts are larger; mitigation: batch-size and context-budget
  enforcement already split oversized work.
- Older runs may lack snapshots; mitigation: migrate only exact suite-and-prompt
  matches and otherwise preserve them as historical, non-reinterpreted evidence.
- The instrument contract supports explicit failure-condition-to-EV impacts,
  but the current corpus conditions are textual; populating those mappings
  requires human-reviewed structured authoring rather than automated inference.

## Compliance & Verification

- Tests assert that candidate projections exclude hidden rubric material.
- Tests assert that reviewer prompts include complete frozen instruments and no
  subject identity.
- Response and rating ingestion verify instrument digests.
- Reports include a schema-versioned Standards Traceability artifact.
- Standards-assisted records declare `qualification_eligible: false`.

## Links

- Pull request: pending
- Related: [Evaluation Rubrics (AIES-AESQS-ER-01)](../AESQS/evaluation-rubrics.md)
- Related: [Qualification Process (AIES-AESQS-QP-01)](../AESQS/qualification-process.md)
- Related: [ADR-0012](ADR-0012-Qualification-Evidence-Rater-Protocol-and-Immutable-Lifecycle.md)
- Related: [ADR-0015](ADR-0015-Subject-and-Evidence-Adapter-Contracts.md)

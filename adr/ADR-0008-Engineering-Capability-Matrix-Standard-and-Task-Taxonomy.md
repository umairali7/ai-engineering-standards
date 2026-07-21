# ADR-0008: Establish an Engineering Capability Matrix standard and task taxonomy

| | |
|---|---|
| **ADR** | ADR-0008 |
| **Status** | Accepted |
| **Deciders** | Umair Ali (repository owner); Maintainers; Platform Module Editor; AESQS Module Editor |
| **Supersedes / Superseded by** | Supersedes the limited ECM-boundary decision in ADR-0006 if accepted |

## Context

ADR-0006 introduced an informational, family-level ECM renderer. It does not
provide the product architecture needed to answer the engineering question
“which subject is best suited to this engineering task?” A scenario family is
not a stable engineering task, and the current output cannot produce a
consistent task profile, deployment guidance, comparison, or selection view.

AIES already assesses more than models: deployments, repositories, and AI
systems. It must also be able to assess agents, agent swarms, MCP servers,
coding assistants, prompt libraries, RAG systems, pipelines, and platforms.
The new artifact therefore cannot be model-specific.

## Decision Drivers

- Keep qualification, engineering capability, and deployment guidance as three
  distinct decisions with distinct audiences and authority boundaries.
- Define stable, versioned Engineering Task identifiers rather than relying on
  prose labels or per-model interpretation.
- Ensure every capability claim is deterministically traceable through task
  mapping to canonical scenario evidence and its rater provenance.
- Support fair comparison and workload-based selection without creating a
  global best-subject leaderboard or bypassing qualification constraints.

## Existing-Contracts Check

- **Can the existing contracts express this?** No. The current evidence and
  renderer contracts can render scenario families, but have no standardized
  task taxonomy, mapping artifact, capability confidence contract, or
  decision-product boundary.
- **If no, which contract is insufficient, and what version bump / conformance
  impact does the change carry?** This adds a foundational standard and
  versioned mapping artifacts above the AESQS decision engine. It must be
  additive to evidence/result schemas and cannot alter qualification gates,
  sample minimums, or autonomy caps.

## Options Considered

### Option A — Keep ECM as a family-only renderer

- **Pros:** Small implementation surface.
- **Cons:** Cannot answer task-selection questions and is not a stable,
  subject-neutral product.

### Option B — Add task labels directly to model reports

- **Pros:** Fast presentation improvement.
- **Cons:** Model-specific, ungoverned, and prone to unsupported claims.

### Option C — Establish AIES-ECM-01 and an Engineering Task Taxonomy

Define ECM as a foundational, subject-neutral standard. Add a governed
Engineering Task Taxonomy and versioned scenario-to-task mappings, then build
ECM, deployment guidance, comparison, and selection as separate consumers of
the same canonical evidence.

- **Pros:** Matches the evidence architecture; supports all subjects and
  decision audiences; makes claims auditable and comparisons bounded.
- **Cons:** Requires taxonomy governance, mapping review, corpus expansion,
  confidence rules, and a staged implementation.

## Decision

Adopt Option C. AIES creates `AIES-ECM-01 — Engineering Capability Matrix` as
a foundational standard and establishes a controlled
Engineering Task Taxonomy beginning with ET-01 through ET-15. The standard
defines four layers:

```text
Assessment → Canonical Evidence → Competency Analysis →
Engineering Task Mapping → ECM → Decision Products
```

Qualification remains governance evidence; ECM is an engineering artifact;
Deployment Guidance is an operations artifact; Comparison and Selection are
decision-support artifacts. None may alter a qualification or record a grant.

## Consequences

**Positive:** AIES gains a coherent V2 product architecture that turns trusted
evidence into task-specific engineering decisions for any assessable subject.

**Negative:** Existing ECM v0 output is explicitly transitional. Task mapping
and corpus coverage must be reviewed before any high-confidence task claim,
comparison, or selection recommendation is emitted.

## Compliance & Verification

- `AIES-ECM-01` defines mandatory provenance and confidence fields for every
  task row.
- Scenario-to-task mappings are versioned, schema-validated, reviewable, and
  tested against unsupported claims.
- ECM comparison refuses incompatible protocols.
- Deployment guidance and selection cannot override qualification gates,
  autonomy limits, or human authorization.

## Links

- [ADR-0006 — Engineering Capability Matrix boundary](ADR-0006-Engineering-Capability-Matrix-Boundary.md)
- [Capability Scoring (AIES-AESQS-CS-01)](../AESQS/capability-scoring.md)
- [OSS Maturity TODO (AIES-DOC-10)](../docs/OSS_MATURITY_TODO.md)

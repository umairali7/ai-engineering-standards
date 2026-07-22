# ADR-0006: Engineering Capability Matrix boundary and task-mapping governance

| | |
|---|---|
| **ADR** | ADR-0006 |
| **Status** | Superseded |
| **Deciders** | Umair Ali (repository owner); Maintainers; Platform Module Editor; AESQS Module Editor |
| **Supersedes / Superseded by** | Superseded by [ADR-0008](ADR-0008-Engineering-Capability-Matrix-Standard-and-Task-Taxonomy.md) |

## Context

AIES qualification evidence establishes whether a subject meets a scoped,
gate-first assessment. Engineers also need a practical, evidence-backed answer
to a different question: which engineering tasks has that subject demonstrated,
with what coverage and confidence? Management then needs bounded deployment
guidance. These are distinct audiences and decisions; adding them as prose to
the Qualification Evidence Package risks confusing informative task evidence
with authoritative qualification or a human grant.

The current scenario `family` metadata can support a narrow, factual first
view. It cannot yet justify claims for finer tasks such as API design,
architecture, security review, or migrations across the whole corpus. A
subject-specific mapping would also prevent AIES from assessing repositories,
agents, MCP servers, prompt libraries, RAG systems, and other future subjects.

## Decision Drivers

- Preserve qualification as gate-first, evidence-only, and human-authorized.
- Make task claims deterministic, traceable, and comparable only when protocols
  match.
- Keep the artifact subject-neutral and avoid a global “best model” leaderboard.
- Make sparse evidence visible instead of turning repeats into apparent breadth.
- Do not alter Shared Taxonomy, scenario schema, or decision semantics without
  separate accepted governance.

## Existing-Contracts Check

- **Can the existing contracts express this?** Partly. Existing evidence,
  result, and renderer contracts can produce an informational family-level
  view, but there is no governed cross-scenario task-mapping contract or
  deterministic confidence/deployment-guidance contract.
- **If no, which contract is insufficient, and what version bump / conformance
  impact does the change carry?** A later accepted mapping artifact would be an
  additive, versioned input above the decision engine. Any Shared Taxonomy or
  normative standard addition requires a separate Class 3 decision and its
  applicable compatibility review. This proposal changes no frozen contract.

## Options Considered

### Option A — Put capability prose in the qualification report

- **Pros:** Minimal implementation effort.
- **Cons:** Blurs authoritative qualification, engineering evidence, and
  deployment guidance; makes provenance and comparison difficult.

### Option B — Model-specific capability profiles

- **Pros:** Directly familiar to model buyers.
- **Cons:** Excludes other AIES subjects and encourages unqualified model
  rankings.

### Option C — Subject-neutral ECM and separate decision products (proposed)

Define a proposed Engineering Capability Matrix (ECM) as an informational
artifact derived from canonical evidence through competency analysis and a
versioned engineering-task mapping. Keep Qualification, ECM, and Deployment
Guidance visibly separate.

- **Pros:** Reuses canonical evidence; is applicable to all subjects; supports
  deterministic traceability and appropriately bounded comparison.
- **Cons:** Requires task-mapping governance, confidence rules, and empirical
  maturity before fine-grained claims become credible.

## Decision

This ADR adopts Option C. Implementations MAY render only non-normative,
family-level informational views until a governed task-mapping registry is
accepted; they MUST NOT claim an `AIES-ECM-01` standard or a normative
engineering-task taxonomy.

If accepted, the architecture is:

```
Assessment → Canonical Evidence → Competency Analysis →
Engineering Task Mapping → Engineering Capability Matrix → Decision Products
```

The three products remain separate:

| Product | Audience | Authority |
|---|---|---|
| Qualification evidence / result | Governance | Authoritative only under existing AESQS rules |
| Engineering Capability Matrix | Engineers | Informational, evidence-derived |
| Deployment Guidance | Operations and management | Informational, bounded by qualification and human authority |

An ECM task row MUST identify its mapping version, scenario identifiers,
distinct-item and repeat counts, uncertainty, rater provenance, evidence
adequacy, and qualification constraints. Low coverage or non-decisional
evidence MUST render an insufficiency message rather than a capability claim.
Task-level comparison is allowed only for matching suite, profile, risk tier,
repeat structure, and rater protocol. A future workload-based selection view
MUST consume declared operational constraints and cannot override gates,
autonomy limits, or a human decision.

## Consequences

**Positive:** Engineers gain a readable, reproducible view of demonstrated
tasks without weakening the qualification boundary. AIES can apply the same
architecture to subjects beyond models.

**Negative:** Fine-grained task coverage cannot be asserted immediately; it
depends on empirical calibration, enough distinct scenarios, and reviewed
mapping metadata. Mitigation: start from existing scenario families and label
coverage honestly.

## Compliance & Verification

- ECM renderers consume canonical records read-only and cannot modify evidence,
  results, qualification records, or grants.
- Each task claim is reproducible from its versioned mapping and cited scenario
  evidence.
- Tests reject comparisons across incompatible protocols and task claims without
  adequate evidence metadata.
- Qualification and deployment guidance use distinct labels and no guidance
  output can create or modify a grant.

## Links

- [ADR-0002 — Qualification Platform](ADR-0002-Qualification-Platform.md)
- [ADR-0005 — Assessment-as-Code](ADR-0005-Assessment-as-Code.md)
- [Project Evaluation (AIES-DOC-15)](../docs/PROJECT_EVALUATION.md)
- [OSS Maturity TODO (AIES-DOC-10)](../docs/OSS_MATURITY_TODO.md)

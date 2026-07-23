# ADR-0018: Subject Assessment Profiles and Coverage Matrix

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-23 |
| Deciders | Umair Ali (repository owner); Platform Module Editor |
| Scope | Subject applicability, assessment coverage, evidence reuse, and blind-spot reporting |

## Context

AIES can identify different subjects and retain typed evidence, but a Subject
Descriptor does not explain what should be assessed for that kind of subject.
Applying deployment scenarios, repository maturity, or EV1–EV6 indiscriminately
would create false equivalence. Future agents, MCP servers, RAG systems,
pipelines, platforms, humans, teams, and composites need one extensible
assessment envelope without pretending the same instruments or scales apply.

Readers also need to distinguish not assessed from poor performance,
not-applicable from unsupported, unavailable from failed collection, and broad
evidence reuse from independent evidence. A single aggregate cannot communicate
those boundaries.

## Decision

1. A versioned **Subject Assessment Profile (SAP)** binds subject kinds to the
   Subject Descriptor schema, fingerprint/change triggers, Subject Executors,
   Evidence Adapters, instruments, scoring semantics, minimums, gates,
   decision products, human-review rules, and limitations.
2. A governed perspective registry identifies lifecycle phases, cross-cutting
   domains, competency areas, engineering tasks, risk tiers, autonomy levels,
   stakeholders, environments, evidence modalities, operating conditions, and
   decision products with stable code-plus-title labels.
3. Every SAP declares a default and optional overrides for every perspective
   category. Design-time applicability is `applicable`, `not-applicable`, or
   `unsupported`; every non-applicable or unsupported rule includes a
   versioned rationale.
4. A run-time **Assessment Coverage Matrix** expands every cell to exactly one
   of `assessed`, `partially-assessed`, `not-assessed`, `not-applicable`, or
   `unsupported`. Collection failures, unavailable evidence, unknown state,
   and redaction remain reasons, never passes.
5. Coverage references canonical evidence identities. Reuse across cells is
   disclosed as reference count versus unique evidence count; reused evidence
   cannot inflate assurance, breadth, or qualification statistics.
6. Coverage and blind spots are informational decision products. They may
   summarize existing evidence but cannot change scores, gates, qualifications,
   grants, deployment authority, or repository quality conclusions.
7. Each SAP declares a freshness policy. Elapsed age is reported separately
   from assessment status, while any fingerprint or declared change trigger
   overrides a nominal age window and requires reassessment.
8. Applicable cells carry a collection condition distinct from coverage:
   `current`, `not-collected`, `not-requested`, `unavailable`,
   `tool-not-installed`, `redacted`, `failed-to-collect`, `stale`, or
   `conflicting`. Adapters may emit typed `collection-gap` events; these events
   explain absence but never count as direct evidence.
9. Evidence confidence is an evidence-coverage property derived from direct
   event depth, instrument breadth, source types, modalities, freshness, and
   conflicts. It is never confidence in subject correctness, capability,
   safety, or a decision.
10. Correlated identities, shared source digests, and component-subject
    evidence are disclosed. Component evidence remains excluded from parent
    coverage unless a future governed explicit mapping is implemented;
    `none`, `reference-only`, and `explicit-mapping-required` never imply
    inheritance.

## Initial profiles

- **SAP-01 — AI Deployment Engineering Assessment** binds the existing
  runtime-generation executor, controlled scenarios, ratings, ECM, Engineering
  Fit Guidance, and separate formal qualification boundary.
- **SAP-02 — Software Repository Engineering Assessment** binds read-only
  conformance and engineering-analysis adapters while explicitly marking
  controlled repository-task behavior and autonomy as unsupported or
  not-applicable.

Other subject kinds remain planned until they ship a reviewed SAP, direct
instruments, an executor or Evidence Adapters, compatibility fixtures, and
honest decision products.

## Prohibited claims

- Coverage percentage is not subject quality, correctness, safety, maturity,
  capability, qualification, or deployment readiness.
- An applicable cell with no evidence is not zero performance; it is not
  assessed.
- A not-applicable cell is not a pass and requires profile rationale.
- An unsupported cell cannot be filled through inference from another subject
  or modality.
- One evidence record referenced by many perspectives remains one source
  identity.

## Consequences

Subject expansion becomes contract-first and auditable. Reports can show what
was measured, partly measured, unmeasured, excluded, and not yet supported
without redesign for each subject kind. The registry and initial profiles are
approved platform contracts under this decision; empirical validation and
promotion of additional subject-specific assessment support remain separate
gates.

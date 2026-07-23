# ADR-0015: Subject and Evidence Adapter Contracts

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-07-23 |
| Decision owners | Maintainers |
| Scope | Platform architecture and versioned evidence interoperability |

## Context

AIES currently executes AI deployments directly, audits repositories, and
renders subject-neutral decision products. Future support for agents, MCP
servers, RAG systems, pipelines, platforms, people, and composite systems must
not force every subject through a text-generation model adapter or silently
reuse incompatible score semantics.

## Proposed decision

Adopt three independently versioned contracts:

1. A Subject Descriptor identifies the exact assessed thing, its kind,
   components, deployment/environment binding, provenance references, and
   privacy classification.
2. A typed Evidence Event records observation modality, source, subject,
   instrument, timestamps, correlation and deduplication identity, payload
   classification, and source digest.
3. An Evidence Adapter converts an explicitly named source profile into typed
   events and always emits a loss report. It may preserve or reject fields but
   may not infer missing AIES scores, inflate evidence count, or convert a tool
   finding into correctness/conformance evidence.

Subject Executors perform subject-specific interaction. Runtime generation is
one executor, not the universal evidence interface. Import adapters are
separate from executors.

Compatibility requires matching contract major versions and declared modality,
instrument, mapping, and scoring semantics. Duplicate identity is
`source_digest + source_record_id + adapter_profile`; retries and reimports do
not create new evidence. Sensitive payloads are opt-in and classified; secrets
are prohibited.

## Consequences

This creates a stable expansion seam while retaining canonical AIES evidence.
Adapters must publish source versions, conversion versions, hashes, losses,
unknowns, and conformance fixtures. Existing deployment manifests remain a
compatibility envelope until migration is separately accepted.

The contracts and bridges introduced with this ADR remain experimental while
the ADR is Proposed. They cannot affect normative qualification or claim
support until the ADR and schemas receive the required Class 3 human review.

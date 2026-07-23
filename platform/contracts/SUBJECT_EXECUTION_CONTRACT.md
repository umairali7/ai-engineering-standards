# Experimental Subject and Execution Contracts v1

Status: Experimental implementation contracts, governed by accepted ADR-0015.

The `aies-subject-descriptor/v1` contract identifies what is assessed without
requiring a model or deployment envelope. It supports people, teams,
repositories, AI deployments and systems, agents and swarms, MCP servers,
coding assistants, prompt libraries, RAG systems, pipelines, platforms, and
composites. A descriptor records stable identity, kind, display name, optional
version and environment binding, provenance, privacy, and typed components.

Composite component references declare a role and may bind a version or
fingerprint. Evidence never transfers implicitly between a component and its
parent: `evidence_transfer` is explicitly `none`, `reference-only`, or
`explicit-mapping-required`.

The `aies-subject-executor/v1` contract describes how evidence is collected
from a subject. It is separate from a runtime adapter:

- `runtime-generation` executes controlled prompts through a declared runtime
  adapter for AI deployments.
- `deterministic-repository-audit` collects read-only repository-practice
  observations without a generation runtime.

Execution collects observations only. It cannot score, qualify, authorize, or
transfer claims. New run manifests use `aies-run-manifest/v2`; legacy manifests
remain readable through in-memory normalization and are never rewritten merely
to adopt the new descriptor.

# ADR-0009: Establish the Engineering Assessment Platform identity

| | |
|---|---|
| **ADR** | ADR-0009 |
| **Status** | Accepted |
| **Deciders** | Umair Ali (repository owner); Maintainers; Platform Module Editor; AESQS Module Editor |
| **Supersedes / Superseded by** | Supersedes ADR-0002's model-only platform identity |

## Context

ADR-0002 named the executable reference implementation the "Model
Qualification Platform" and scoped its initial executors to AI models. AIES now
also audits repositories, produces subject-neutral Engineering Capability
Matrices, and is designed to assess AI systems, agents, agent swarms, MCP
servers, coding assistants, prompt libraries, RAG systems, pipelines, and
platforms. A model-only public identity contradicts this architecture.

## Decision

Adopt **AIES Engineering Assessment Platform** as the public name of the
`aies` CLI and Python package. The platform prepares evidence and decision
products for assessable engineering subjects; it never grants qualification.

This is an identity and architectural-boundary change, not a claim that every
subject executor already exists. Current executable subject support remains AI
deployments and repository conformance. New subject kinds require their own
schemas, adapters, scenarios, and conformance tests.

## Consequences

- User-facing help, package metadata, platform documentation, and report
  footers use the subject-neutral identity.
- Historical ADRs and historical evidence remain unchanged and retain their
  original terminology.
- Future commands and artifacts MUST avoid naming models as the universal
  subject unless the command is specifically model/deployment scoped.

## Compliance & Verification

- `python -m aies --help` identifies the Engineering Assessment Platform.
- Package metadata and `platform/README.md` use the same identity.
- Documentation states both the present executable scope and the future
  subject-neutral architecture without overstating implementation coverage.

## Links

- [ADR-0002](ADR-0002-Qualification-Platform.md)
- [ADR-0008](ADR-0008-Engineering-Capability-Matrix-Standard-and-Task-Taxonomy.md)
- [Platform specification](../docs/PLATFORM.md)

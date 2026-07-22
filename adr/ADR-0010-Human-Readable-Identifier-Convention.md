# ADR-0010 — Canonical Human-Readable Identifier Display Convention

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-07-22 |
| **Decider** | Repository owner |
| **Scope** | Shared taxonomy, generated decision products, and reader-facing documentation |

## Context

AIES uses stable identifiers for traceability: competency areas, roles, SDLC
phases, domains, artifacts, evaluation dimensions, competency levels, risk
tiers, autonomy levels, standards, and requirements. Stable codes are useful to
engines and auditors, but unexplained shorthand makes reports and standards
harder to read and easy to misinterpret.

The earlier risk-tier and autonomy rendering convention demonstrated the value,
but applying it to only two taxonomies was inconsistent.

## Decision

All human-facing AIES content uses `CODE — Title` for taxonomy identifiers.
The canonical display titles are the names in AIES-SHARED-02. Platform
renderers use one shared identifier-label function rather than re-creating
labels locally.

Raw codes remain valid and required in machine contracts, file paths, URLs,
command flags, JSON/YAML values, and stable record identifiers. Formal
requirement IDs remain complete and immutable. A human-facing requirement
reference uses `FULL-ID — reviewed short title`; the short title describes the
obligation, constraint, or decision in the cited requirement, rather than only
its owning standard or sequence number. A bare `Rnn`, or a label such as
`Capability Scoring, requirement 13`, is not sufficient.

Requirement titles are governed editorial metadata: authors add or review the
title with the normative requirement. Existing requirements are migrated in
reviewed standard-sized sets; tooling may identify missing titles, but MUST NOT
invent them from normative prose.

## Consequences

- Engineers can read reports, dashboards, examples, and standards without
  repeatedly consulting the taxonomy.
- Canonical values and backward compatibility are preserved.
- New taxonomy entries require a display title at the same time as their code.
- Existing requirement references need a controlled, reviewed title migration;
  that work must not invent normative titles.

## Alternatives Considered

**Keep codes only.** Rejected: concise for authors, but opaque for readers.

**Replace codes with titles.** Rejected: breaks traceability, parser contracts,
and cross-document citations.

**Show a legend once per document.** Rejected: readers encounter excerpts,
tables, reports, and CLI output out of context.

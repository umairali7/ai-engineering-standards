# Diagrams

| | |
|---|---|
| **Document ID** | AIES-DIA-00 |
| **Status** | Review |
| **Audience** | Contributors & maintainers |

This directory holds the text-first diagram sources used across the AIES repository, and defines the directory-specific conventions they follow. This README is subordinate to the [Diagram Standard (AIES-STD-04 — Diagram Standard)](../docs/standards/diagram-standard.md), which is the normative authority for diagram requirements; nothing here overrides it.

The key words "MUST" and "SHOULD" in this document are to be interpreted as described in RFC 2119.

---

## 1. Conventions

- **Text-first, always.** Diagram sources MUST be text-based so they diff cleanly in review, can be edited without proprietary software, and stay vendor-neutral. Binary formats (images, drawing-tool project files) are not accepted as sources; rendered images, where needed at all, are derived artifacts.
- **Mermaid preferred.** Mermaid (`.mmd`) is the preferred format for diagrams stored in this directory. ASCII diagrams are acceptable when embedded directly inside a document (as the architecture documents do), and for diagrams too simple to justify a separate file.
- **Reused diagrams live here.** A diagram embedded in a document SHOULD also be stored in this directory when it is reused by more than one document, so there is a single source to update. Single-use diagrams may remain inline in their document.
- **Consistent vocabulary.** Labels in diagrams use terms exactly as defined in the [Shared Glossary](../Shared/Glossary/README.md) and [Taxonomy](../Shared/Taxonomy/README.md).

## 2. Naming Convention

Files are named by owning module and topic:

```
<module>-<topic>.mmd
```

where `<module>` is one of `shared`, `aebok`, `aesqs`, `aeos`, `aear`, `aect`, or `aies` for project-level diagrams, and `<topic>` is a short kebab-case description. Examples:

- `aies-module-dependencies.mmd`
- `aeos-autonomy-envelope-lifecycle.mmd`
- `shared-document-status-lifecycle.mmd`

## 3. Index

<!-- Append one row per diagram source, alphabetically by filename, in the
     same pull request that adds or renames the file. List every document
     that embeds or references the diagram. -->

| File | Description | Used By |
|------|-------------|---------|
| [`aies-assessment-and-assistance-flow.mmd`](aies-assessment-and-assistance-flow.mmd) | Separates unassisted assessment, frozen audience-specific instrument projections, canonical evidence, ECM decision products, optional formal qualification, and isolated standards-assisted work. | [README](../README.md), [Platform Specification](../docs/PLATFORM.md), [Project Evaluation](../docs/PROJECT_EVALUATION.md), [Platform Guide](../platform/GUIDE.md), [Vision Execution Backlog](../docs/OSS_MATURITY_TODO.md) |
| [`aies-platform-components.mmd`](aies-platform-components.mmd) | Subject-neutral executable architecture: profiles, instrument compiler, executors/adapters, evidence store, review, analysis, reporting, human authority, and the isolated assisted executor. | [Platform Specification](../docs/PLATFORM.md), [Repository Architecture](../docs/ARCHITECTURE.md), [Platform Guide](../platform/GUIDE.md) |

## Related Documents

- [Diagram Standard (AIES-STD-04 — Diagram Standard)](../docs/standards/diagram-standard.md) — the normative standard this directory is subordinate to
- [AIES-DOC-03 — Repository Architecture](../docs/ARCHITECTURE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

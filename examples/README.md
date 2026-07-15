# Worked Examples

| | |
|---|---|
| **Document ID** | AIES-EX-00 |
| **Status** | Review |
| **Audience** | All readers |

This directory holds worked examples that apply the AIES standards to concrete, end-to-end scenarios. Standards text says what conformant practice *is*; examples show what it *looks like* — a filled-in artifact, a scored assessment, a designed gate — so that practitioners can calibrate their own work against something tangible.

Examples are **informative, never normative**: nothing in an example adds to, relaxes, or reinterprets the requirements of the standards it illustrates. Where an example and a standard disagree, the standard wins and the example has a bug.

---

## Catalog

Each example lives in its own subdirectory (`EX-NN-<short-title>/`) with a README applying the referenced module documents step by step. All six are set in the same fictional organization — **Fieldstone**, a field-service management SaaS company operating an AI coding agent (FS-AGENT-ENG-01) — so they can be read as one coherent case study, and they cross-reference each other.

| ID | Example | Primary Module(s) | Status |
|----|---------|-------------------|--------|
| [EX-01](EX-01-risk-tiering-backlog/README.md) | Risk-tiering a real product backlog using the shared risk tiers | AEBOK / AEOS | Draft |
| [EX-02](EX-02-autonomy-envelope/README.md) | A completed autonomy envelope definition for an AI coding agent | AEOS | Draft |
| [EX-03](EX-03-scored-pull-request/README.md) | An AI-produced pull request scored with the AESQS rubrics | AESQS | Draft |
| [EX-04](EX-04-filled-adr/README.md) | A filled Architecture Decision Record | Shared | Draft |
| [EX-05](EX-05-oversight-gate-design/README.md) | Human oversight gate design for a delivery pipeline | AEOS | Draft |
| [EX-06](EX-06-context-asset-spec/README.md) | A context asset specification | AEBOK (KA-10) | Draft |

**Suggested reading order:** EX-01 (tier the work) → EX-02 (bound the agent) → EX-06 (feed it context) → EX-03 (score its output) → EX-05 (design the gates) → EX-04 (record the platform decision).

## Contributing an Example

Worked examples are welcome contributions — they are Class 2 (substantive) changes under [GOVERNANCE.md §3](../GOVERNANCE.md). Follow the workflow in [CONTRIBUTING.md](../CONTRIBUTING.md), and additionally:

- Use terms exactly as defined in the [Shared Glossary](../Shared/Glossary/README.md) and classifications from the [Shared Taxonomy](../Shared/Taxonomy/README.md).
- Cite the specific documents and requirement IDs the example applies, with relative links.
- Anonymize any real-world material: no client names, proprietary code, or identifying details.
- Keep examples vendor-neutral; where a scenario requires naming tool categories, present alternatives per [GOVERNANCE.md §7](../GOVERNANCE.md).
- Add or update the catalog row above in the same pull request.

## Related Documents

- [Repository Architecture (AIES-DOC-03)](../docs/ARCHITECTURE.md)
- [Standard template](../templates/STANDARD_TEMPLATE.md)
- [ROADMAP.md](../ROADMAP.md)

## References

None.

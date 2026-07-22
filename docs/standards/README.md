# AIES Document Standards

| | |
|---|---|
| **Document ID** | AIES-STD-00 |
| **Status** | Draft |
| **Audience** | All readers |

The Document Standards define how every document in the AIES repository is structured, identified, written, illustrated, versioned, and reviewed. They are the governance layer for the repository's documents themselves — distinct from the engineering content those documents carry.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Why Document Standards Are Separate from Module Content

AIES module content (AEBOK, AESQS, AEOS, AEAR, AECT) defines how AI-native software engineering is practiced. The Document Standards define how AIES documents are made. The two concerns scale differently:

- **Scope.** These standards govern *every* file in the repository — including AEBOK itself, the Shared Glossary and Taxonomy, governance documents, templates, examples, and this index. No module is a natural home for rules that bind all modules.
- **Scale.** The repository is designed to grow past 500 documents. Conventions embedded in a module README (as early versions of AIES did in [Shared/README.md](../../Shared/README.md)) do not survive that growth; a dedicated, normative standards suite does.
- **Stability.** Module content evolves with engineering practice; document governance changes rarely and deliberately, through the process in [AIES-GOV-01 — Governance](../../GOVERNANCE.md).

These standards absorb and supersede the documentation conventions formerly maintained in Shared/README.md §1.

## 2. The Six Standards

| Standard | Document ID | Governs |
|----------|-------------|---------|
| [Document Standard](document-standard.md) | AIES-STD-01 | What constitutes an AIES document: classes, required structure, file naming, directory placement, scope and size |
| [Metadata Standard](metadata-standard.md) | AIES-STD-02 | The metadata table, the Document ID grammar and code registry, requirement-ID grammar, audience vocabulary |
| [Writing Standard](writing-standard.md) | AIES-STD-03 | Normative language, requirement tagging, glossary discipline, vendor neutrality, style, cross-references |
| [Diagram Standard](diagram-standard.md) | AIES-STD-04 | Text-first diagram sources, naming, accessibility, neutrality |
| [Versioning Standard](versioning-standard.md) | AIES-STD-05 | Status vs. version, release versioning, breaking changes, deprecation |
| [Review Standard](review-standard.md) | AIES-STD-06 | The document lifecycle, transition criteria, conformance review, demotion |

## 3. Conformance

- [AIES-STD-00-R01 — Documentation Standards, requirement 01] Every document in the AIES repository MUST conform to AIES-STD-01 through AIES-STD-05, as applicable to its document class per [AIES-STD-01 — Document Standard](document-standard.md).
- [AIES-STD-00-R02 — Documentation Standards, requirement 02] Conformance MUST be verified before a document is promoted out of Draft, using the checklist in the [Review Standard (AIES-STD-06 — Review Standard)](review-standard.md).
- [AIES-STD-00-R03 — Documentation Standards, requirement 03] Changes to any document standard are Class 3 decisions per [AIES-GOV-01 — Governance](../../GOVERNANCE.md), because they alter the conformance obligations of every document in the repository.

Where a document predates a standard, the standard still applies; bringing legacy documents into conformance is routine editorial work (Class 1 or Class 2 per GOVERNANCE).

## Related Documents

- [Document Standard (AIES-STD-01 — Document Standard)](document-standard.md)
- [Metadata Standard (AIES-STD-02 — Metadata Standard)](metadata-standard.md)
- [Writing Standard (AIES-STD-03 — Writing Standard)](writing-standard.md)
- [Diagram Standard (AIES-STD-04 — Diagram Standard)](diagram-standard.md)
- [Versioning Standard (AIES-STD-05 — Versioning Standard)](versioning-standard.md)
- [Review Standard (AIES-STD-06 — Review Standard)](review-standard.md)
- [AIES-GOV-01 — Governance](../../GOVERNANCE.md)
- [AIES-SHARED-00 — Shared Standards](../../Shared/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

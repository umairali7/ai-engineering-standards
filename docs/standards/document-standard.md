# Document Standard

| | |
|---|---|
| **Document ID** | AIES-STD-01 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This standard defines what constitutes an AIES document: the recognized document classes, the structure every document follows, how files are named, and where they live in the repository.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

---

## 1. Document Classes

Every AIES document belongs to exactly one class. The class determines which rules bind it.

| Class | Purpose | Examples | Normative? |
|-------|---------|----------|------------|
| **Normative standard** | States requirements using RFC 2119 keywords | This document, the [Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md) | Yes |
| **Guidance** | Explains, orients, recommends — without binding | GETTING_STARTED.md (AIES-DOC-00), docs/FAQ.md | No |
| **Reference** | Catalogs stable facts other documents cite | The [Glossary (AIES-SHARED-01 — Glossary)](../../Shared/Glossary/README.md), role specifications | Partly (as declared) |
| **Template** | A fill-in skeleton for producing new documents | [templates/](../../templates/README.md) | No |
| **Worked example** | Applies the standards to a concrete scenario | [AIES-EX-00 — Worked Examples](../../examples/README.md) | Never |
| **Record** | Captures a decision at a point in time (ADRs, review records) | [adr/](../../adr/README.md) | No; immutable once accepted |

- [AIES-STD-01-R01 — Document Standard, requirement 01] Every document MUST be identifiable as exactly one class; where the class is not obvious from directory placement (§4), the document MUST state it.
- [AIES-STD-01-R02 — Document Standard, requirement 02] Only normative standards and declared-normative sections of reference documents MAY state requirements using RFC 2119 keywords; all other classes MUST NOT use them in their uppercase form.
- [AIES-STD-01-R03 — Document Standard, requirement 03] Worked examples and records MUST NOT add to, relax, or reinterpret the requirements of any standard. Where an example and a standard disagree, the standard prevails.
- [AIES-STD-01-R04 — Document Standard, requirement 04] Records (including ADRs) MUST NOT be edited substantively after acceptance; corrections are made by a superseding record.

## 2. Required Structure

- [AIES-STD-01-R05 — Document Standard, requirement 05] Every document MUST contain, in order: a single `#` title, the metadata table per the [Metadata Standard (AIES-STD-02 — Metadata Standard)](metadata-standard.md), the body, a `## Related Documents` section, and a `## References` section.
- [AIES-STD-01-R06 — Document Standard, requirement 06] Documents that use RFC 2119 keywords MUST include the boilerplate sentence required by the [Writing Standard (AIES-STD-03 — Writing Standard)](writing-standard.md) immediately after the metadata table (or after a one-paragraph purpose statement).
- [AIES-STD-01-R07 — Document Standard, requirement 07] `## Related Documents` MUST list related AIES documents as relative links with document IDs; `## References` MUST list external works only, and MUST contain the text "None." when there are none.

## 3. File Naming

- [AIES-STD-01-R08 — Document Standard, requirement 08] File names MUST be kebab-case (`lowercase-words-with-hyphens.md`), except for repository-conventional root files (README.md, CHANGELOG.md, GOVERNANCE.md, CONTRIBUTING.md, GETTING_STARTED.md, and similar) and template files in templates/.
- [AIES-STD-01-R09 — Document Standard, requirement 09] The index or overview document of a directory MUST be named `README.md` and carries the `00` ID for its area per AIES-STD-02.
- [AIES-STD-01-R10 — Document Standard, requirement 10] File names SHOULD reflect the document's subject, not its ID; the ID lives in the metadata table, so files are not renamed when catalogs are reorganized.

## 4. Directory Placement

- [AIES-STD-01-R11 — Document Standard, requirement 11] A document MUST be placed in the directory that owns its area code: module content in AEBOK/, AESQS/, AEOS/, AEAR/, or AECT/; shared vocabulary in Shared/; project and orientation documents in docs/ or the repository root; document standards in docs/standards/; ADRs in adr/; templates in templates/; worked examples in examples/; reusable diagram sources in diagrams/; research notes in research/.
- [AIES-STD-01-R12 — Document Standard, requirement 12] A document MUST NOT be duplicated across directories; a single canonical location is linked from everywhere else.

## 5. Scope and Size

- [AIES-STD-01-R13 — Document Standard, requirement 13] Each document MUST address one concern. Content serving a second concern belongs in a second document, linked from the first.
- [AIES-STD-01-R14 — Document Standard, requirement 14] A document exceeding approximately 300 lines SHOULD be split into an index plus focused child documents, preserving inbound links per the [Writing Standard (AIES-STD-03 — Writing Standard)](writing-standard.md).

## Related Documents

- [Document Standards index (AIES-STD-00 — Documentation Standards)](README.md)
- [Metadata Standard (AIES-STD-02 — Metadata Standard)](metadata-standard.md)
- [Writing Standard (AIES-STD-03 — Writing Standard)](writing-standard.md)
- [Review Standard (AIES-STD-06 — Review Standard)](review-standard.md)
- [AIES-GOV-01 — Governance](../../GOVERNANCE.md)
- [AIES-SHARED-00 — Shared Standards](../../Shared/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

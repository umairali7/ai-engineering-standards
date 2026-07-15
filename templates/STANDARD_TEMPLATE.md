<!--
  AIES STANDARD DOCUMENT TEMPLATE
  ================================
  Use this skeleton for every new AIES standard document (module documents,
  Shared Standards documents, and project-level docs/ documents).

  How to use:
  1. Copy this file into the owning directory (see docs/ARCHITECTURE.md §5).
  2. Replace every <placeholder> and delete these instructional comments.
  3. Request a Document ID from the owning Module Editor (Maintainer for
     Shared/root documents). IDs follow the Metadata Standard
     (docs/standards/metadata-standard.md, AIES-STD-02) and are never reused.
  4. Follow the Documentation Standards (docs/standards/README.md, AIES-STD-00)
     throughout — in particular the Document Standard (AIES-STD-01) for
     structure and the Writing Standard (AIES-STD-03) for normative language.
-->

# <Document Title>

<!-- Metadata table is MANDATORY and contains exactly these three rows
     (Metadata Standard, AIES-STD-02). Keep the empty header row exactly as
     shown — it renders as a borderless two-column table. Do not add Version
     or date rows; release history lives only in CHANGELOG.md. -->

| | |
|---|---|
| **Document ID** | <ID per the Metadata Standard (AIES-STD-02), e.g. AIES-AEOS-GOV-01> |
| **Status** | Draft <!-- lifecycle per the Review Standard (AIES-STD-06): Draft → Review → Approved → Deprecated; new documents always start as Draft --> |
| **Audience** | <Audience terms from the Metadata Standard (AIES-STD-02), " · " separated, e.g. Architects · Engineers> |

<!-- One or two sentences summarizing what this document is, placed directly
     under the metadata table. -->

<Single-paragraph abstract of the document.>

<!-- The RFC 2119 boilerplate below is REQUIRED for any document containing
     normative requirements (Writing Standard, AIES-STD-03). Delete it only
     for purely informative documents. -->

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

<!-- Why this document exists: the problem it addresses and the outcome it
     enables. One to three paragraphs. Do not restate the abstract verbatim. -->

<Purpose text.>

## 2. Scope

<!-- What this document covers and — just as important — what it explicitly
     does NOT cover. Name adjacent documents that own the out-of-scope topics,
     using relative links plus Document IDs (Writing Standard, AIES-STD-03). -->

**In scope:**

- <Topic covered.>

**Out of scope:**

- <Topic not covered — see [<Owning Document> (<DOC-ID>)](<relative-path>).>

## 3. Terms

<!-- Do NOT define terms locally. All terminology is owned by the Shared
     Glossary; local redefinition is prohibited (Writing Standard, AIES-STD-03)
     and changing a shared definition is a Class 3 decision (GOVERNANCE.md §3).
     If this document needs a term the Glossary lacks, propose the addition
     there first. Optionally list the key glossary terms this document relies
     on, as links. -->

Terms used in this document are defined in the [Shared Glossary (AIES-SHARED-01)](../Shared/Glossary/README.md) and the [Shared Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md). This document does not redefine any shared term.

Key terms relied upon: <term>, <term>, <term>.

## 4. Requirements

<!-- Normative content lives here. Every requirement:
     - uses RFC 2119 keywords (capitalized),
     - carries a stable requirement ID in the form [<DOC-ID>-RNN]
       (Writing Standard, AIES-STD-03) so it can be cited from assessments,
       audits, and certification material,
     - is numbered sequentially and NEVER renumbered — retired requirements
       are marked "Withdrawn", their IDs are not reused.
     Group requirements under subsections if the document is large. -->

**[<DOC-ID>-R01]** <The subject> MUST <requirement statement>.

**[<DOC-ID>-R02]** <The subject> SHOULD <recommendation statement>; deviation requires documented justification.

**[<DOC-ID>-R03]** <The subject> MAY <optional behavior>.

<!-- Example of a well-formed requirement:
     [AIES-AEOS-GOV-01-R03] Every autonomous change MUST be traceable to an
     approved work item. -->

## 5. Guidance

<!-- Informative (non-normative) material: rationale, implementation advice,
     patterns, anti-patterns, worked illustrations. Nothing in this section
     may impose requirements — if a statement needs an RFC 2119 keyword, it
     belongs in §4. Reference examples/ and research/ where useful. -->

<Guidance text.>

## Related Documents

<!-- MANDATORY final sections (Document Standard, AIES-STD-01): every document
     ends with Related Documents followed by References. List here the AIES
     documents this one depends on or is depended on by, as relative links
     plus Document IDs. -->

- [<Document Title> (<DOC-ID>)](<relative-path>)

## References

<!-- External works only (standards, papers, books), cited by name and
     version, e.g. "ISO/IEC 42001:2023". Write "None." if there are none. -->

- <External standard, e.g. ISO/IEC 42001:2023 — or "None.">

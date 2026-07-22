# Writing Standard

| | |
|---|---|
| **Document ID** | AIES-STD-03 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This standard governs how AIES documents are written: normative language, requirement tagging, glossary discipline, vendor neutrality, style, and cross-referencing.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

---

## 1. Normative Language

- [AIES-STD-03-R01 — Normative requirements use RFC 2119 and RFC 8174 keywords] Requirements MUST be expressed using the RFC 2119 / RFC 8174 keywords MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY, in all capitals.
- [AIES-STD-03-R02 — Normative documents include keyword boilerplate] Every document that uses these keywords normatively MUST include this boilerplate after its metadata table:

> The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

- [AIES-STD-03-R03 — Normative keywords are excluded from non-normative documents] The uppercase keywords MUST NOT appear in non-normative documents (guidance, templates, worked examples, records) per [AIES-STD-01 — Document Standard](document-standard.md). Lowercase "must", "should", and "may" carry only their plain-English meaning everywhere.

## 2. Requirement Tagging

- [AIES-STD-03-R04 — MUST-level obligations carry requirement IDs] Every MUST-level requirement (MUST, MUST NOT, SHALL, SHALL NOT) MUST carry a requirement ID per the grammar in the [Metadata Standard (AIES-STD-02 — Metadata Standard)](metadata-standard.md).
- [AIES-STD-03-R05 — SHOULD-level obligations should carry requirement IDs] SHOULD-level requirements SHOULD carry requirement IDs; untagged SHOULD-level statements remain normative but cannot be cited by assessments or audits.
- [AIES-STD-03-R06 — Each requirement ID covers one testable obligation] One requirement ID MUST cover one testable obligation. Compound obligations are split into separately tagged requirements.

## 3. Glossary Discipline

- [AIES-STD-03-R07 — Glossary terms retain their canonical meanings] Terms defined in the [Shared Glossary (AIES-SHARED-01 — Glossary)](../../Shared/Glossary/README.md) MUST be used with exactly their glossary meaning, and MUST NOT be redefined, paraphrased as a definition, or given a competing local meaning in any other document.
- [AIES-STD-03-R08 — New terms are proposed to the Shared Glossary] A document that needs a term the Glossary lacks MUST propose the term for the Glossary (a Class 3 change per [AIES-GOV-01 — Governance](../../GOVERNANCE.md)) rather than defining it locally.
- [AIES-STD-03-R09 — Classifications come from the Shared Taxonomy] Classifications (SDLC phases, autonomy levels, risk tiers, and the rest) MUST be drawn from the [Shared Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md); documents MUST NOT introduce competing scales.

## 4. Vendor Neutrality

- [AIES-STD-03-R10 — Standards remain vendor-neutral] AIES documents MUST NOT name specific AI vendors, models, model families, cloud platforms, or commercial products. Capabilities are described in vendor-neutral terms (e.g., "a coding agent capable of multi-file refactoring", not a product name).
- [AIES-STD-03-R11 — External standards may be cited by name and version] Other standards bodies and published standards MAY be named (e.g., ISO/IEC, NIST, OWASP, IETF RFCs), cited by name and version.
- [AIES-STD-03-R12 — Tooling references use category language] Where a scenario requires referring to tooling, documents MUST use category language ("model provider", "agent platform", "CI system") and, in informative material, MUST present alternatives where they exist, per [GOVERNANCE.md §7](../../GOVERNANCE.md).

## 5. Style

- [AIES-STD-03-R13 — Normative statements use active voice and explicit actors] Normative statements MUST use active voice with an explicit actor ("The Module Editor MUST record…", not "It must be recorded…").
- [AIES-STD-03-R14 — Enumerable facts should use tables] Enumerable facts — codes, levels, tiers, catalogs, criteria — SHOULD be presented as tables rather than prose, so they can be referenced and diffed precisely.
- Prose should be plain, direct, and free of filler; one idea per paragraph. Marketing language has no place in a standard.

## 6. Cross-References

- [AIES-STD-03-R15 — Cross-references include relative links and document IDs] References to other AIES documents MUST use a relative link from the citing file's location together with the target's document ID: `[Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md)`.
- [AIES-STD-03-R16 — Individual requirements are cited by complete requirement ID] References to individual requirements MUST cite the requirement ID (e.g., "per [AIES-AESQS-CS-01-R13 — Stability variance can fail or suspend EV1 or EV3 claims](../../AESQS/capability-scoring.md#6-statistical-requirements)").

## 7. Heading and Anchor Stability

Headings generate the anchors that inbound links target; renaming a heading silently breaks every link to it.

- [AIES-STD-03-R17 — Heading changes are treated as breaking changes] Renaming or removing a heading in a non-Draft document MUST be treated as a breaking change per the [Versioning Standard (AIES-STD-05 — Versioning Standard)](versioning-standard.md).
- [AIES-STD-03-R18 — Inbound anchors are updated with heading changes] Before renaming any heading, authors MUST search the repository for inbound links to its anchor (e.g., `grep -r "#the-anchor"`) and update every one in the same change.
- [AIES-STD-03-R19 — Section numbers should remain stable] Section numbers SHOULD be stable; new sections are appended rather than inserted where practical, so that "§4" citations elsewhere stay true.

## 8. Human-Readable Identifiers

- [AIES-STD-03-R20 — Human-facing taxonomy codes include titles] In prose, tables, reports, dashboards, generated HTML, and CLI output intended for a human, every AIES taxonomy identifier MUST retain its canonical code and display its canonical title in the form `CODE — Title` (for example, `CA-05 — AI-Assisted Implementation`, `ROLE-05 — Architect`, and `EV3 — Safety & Security`).
- [AIES-STD-03-R21 — Machine-only code values receive adjacent human context] Machine contracts MAY use the canonical code alone where required for parsing, compatibility, file names, URLs, command flags, JSON/YAML values, or stable record IDs. When such a value is shown to a human in an example, adjacent explanatory text or a comment MUST provide its `CODE — Title` form.
- [AIES-STD-03-R22 — Requirement references include reviewed obligation titles] A requirement reference MUST retain its complete, stable requirement ID and its reviewed short obligation title. A bare local reference such as `R13`, or a label that merely repeats its owning standard and sequence number, is insufficient outside the requirement's immediate context. The title MUST describe the requirement's obligation, constraint, or decision without changing its normative meaning. Authors MUST add or review the short title whenever they add or materially change a normative requirement. Existing requirements are migrated in reviewed standard-sized sets; tooling MAY identify missing titles but MUST NOT generate or infer normative titles automatically.

## Related Documents

- [Document Standards index (AIES-STD-00 — Documentation Standards)](README.md)
- [Document Standard (AIES-STD-01 — Document Standard)](document-standard.md)
- [Metadata Standard (AIES-STD-02 — Metadata Standard)](metadata-standard.md)
- [Versioning Standard (AIES-STD-05 — Versioning Standard)](versioning-standard.md)
- [Shared Glossary (AIES-SHARED-01 — Glossary)](../../Shared/Glossary/README.md)
- [Shared Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md)
- [AIES-GOV-01 — Governance](../../GOVERNANCE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

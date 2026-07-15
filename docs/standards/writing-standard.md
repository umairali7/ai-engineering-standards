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

- [AIES-STD-03-R01] Requirements MUST be expressed using the RFC 2119 / RFC 8174 keywords MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY, in all capitals.
- [AIES-STD-03-R02] Every document that uses these keywords normatively MUST include this boilerplate after its metadata table:

> The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

- [AIES-STD-03-R03] The uppercase keywords MUST NOT appear in non-normative documents (guidance, templates, worked examples, records) per [AIES-STD-01](document-standard.md). Lowercase "must", "should", and "may" carry only their plain-English meaning everywhere.

## 2. Requirement Tagging

- [AIES-STD-03-R04] Every MUST-level requirement (MUST, MUST NOT, SHALL, SHALL NOT) MUST carry a requirement ID per the grammar in the [Metadata Standard (AIES-STD-02)](metadata-standard.md).
- [AIES-STD-03-R05] SHOULD-level requirements SHOULD carry requirement IDs; untagged SHOULD-level statements remain normative but cannot be cited by assessments or audits.
- [AIES-STD-03-R06] One requirement ID MUST cover one testable obligation. Compound obligations are split into separately tagged requirements.

## 3. Glossary Discipline

- [AIES-STD-03-R07] Terms defined in the [Shared Glossary (AIES-SHARED-01)](../../Shared/Glossary/README.md) MUST be used with exactly their glossary meaning, and MUST NOT be redefined, paraphrased as a definition, or given a competing local meaning in any other document.
- [AIES-STD-03-R08] A document that needs a term the Glossary lacks MUST propose the term for the Glossary (a Class 3 change per [GOVERNANCE.md (AIES-GOV-01)](../../GOVERNANCE.md)) rather than defining it locally.
- [AIES-STD-03-R09] Classifications (SDLC phases, autonomy levels, risk tiers, and the rest) MUST be drawn from the [Shared Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md); documents MUST NOT introduce competing scales.

## 4. Vendor Neutrality

- [AIES-STD-03-R10] AIES documents MUST NOT name specific AI vendors, models, model families, cloud platforms, or commercial products. Capabilities are described in vendor-neutral terms (e.g., "a coding agent capable of multi-file refactoring", not a product name).
- [AIES-STD-03-R11] Other standards bodies and published standards MAY be named (e.g., ISO/IEC, NIST, OWASP, IETF RFCs), cited by name and version.
- [AIES-STD-03-R12] Where a scenario requires referring to tooling, documents MUST use category language ("model provider", "agent platform", "CI system") and, in informative material, MUST present alternatives where they exist, per [GOVERNANCE.md §7](../../GOVERNANCE.md).

## 5. Style

- [AIES-STD-03-R13] Normative statements MUST use active voice with an explicit actor ("The Module Editor MUST record…", not "It must be recorded…").
- [AIES-STD-03-R14] Enumerable facts — codes, levels, tiers, catalogs, criteria — SHOULD be presented as tables rather than prose, so they can be referenced and diffed precisely.
- Prose should be plain, direct, and free of filler; one idea per paragraph. Marketing language has no place in a standard.

## 6. Cross-References

- [AIES-STD-03-R15] References to other AIES documents MUST use a relative link from the citing file's location together with the target's document ID: `[Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md)`.
- [AIES-STD-03-R16] References to individual requirements MUST cite the requirement ID (e.g., "per [AIES-STD-02-R02]").

## 7. Heading and Anchor Stability

Headings generate the anchors that inbound links target; renaming a heading silently breaks every link to it.

- [AIES-STD-03-R17] Renaming or removing a heading in a non-Draft document MUST be treated as a breaking change per the [Versioning Standard (AIES-STD-05)](versioning-standard.md).
- [AIES-STD-03-R18] Before renaming any heading, authors MUST search the repository for inbound links to its anchor (e.g., `grep -r "#the-anchor"`) and update every one in the same change.
- [AIES-STD-03-R19] Section numbers SHOULD be stable; new sections are appended rather than inserted where practical, so that "§4" citations elsewhere stay true.

## Related Documents

- [Document Standards index (AIES-STD-00)](README.md)
- [Document Standard (AIES-STD-01)](document-standard.md)
- [Metadata Standard (AIES-STD-02)](metadata-standard.md)
- [Versioning Standard (AIES-STD-05)](versioning-standard.md)
- [Shared Glossary (AIES-SHARED-01)](../../Shared/Glossary/README.md)
- [Shared Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md)
- [Governance (AIES-GOV-01)](../../GOVERNANCE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

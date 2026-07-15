# Diagram Standard

| | |
|---|---|
| **Document ID** | AIES-STD-04 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This standard governs diagrams in AIES documents: source format, when to use them, naming, accessibility, and neutrality.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

---

## 1. Text-First Sources

Diagrams in a version-controlled standard must diff cleanly, merge cleanly, and be editable by any contributor without proprietary tooling.

- [AIES-STD-04-R01] Diagram sources MUST be text-based. Mermaid is the preferred format; ASCII diagrams embedded inline in a document are acceptable for simple structures.
- [AIES-STD-04-R02] Binary diagram formats (bitmap images, proprietary drawing files) MUST NOT be committed as the source of truth for a diagram. Rendered images, where needed at all, are derived artifacts.

## 2. When Diagrams Are Warranted

- [AIES-STD-04-R03] A diagram SHOULD be used when it communicates structure or flow more clearly than prose or a table would — typically for relationships among more than three elements, lifecycle flows, layered architectures, and decision paths.
- [AIES-STD-04-R04] A diagram MUST NOT be the sole carrier of normative content; requirements live in tagged text, and diagrams illustrate them.
- Simple sequences and enumerable facts are better served by tables per the [Writing Standard (AIES-STD-03)](writing-standard.md).

## 3. Placement and Naming

- [AIES-STD-04-R05] A diagram used by a single document SHOULD be embedded inline in that document. A diagram reused by two or more documents MUST live as a standalone source file in [diagrams/](../../diagrams/README.md) and be referenced from each user.
- [AIES-STD-04-R06] Standalone reusable diagram files MUST be named `<module>-<topic>.mmd` (e.g., `aeos-oversight-gates.mmd`, `shared-document-lifecycle.mmd`), where `<module>` is the lowercase owning area.

## 4. Accessibility

- [AIES-STD-04-R07] Every diagram MUST be accompanied by prose that states what the diagram shows, so the content is available to readers using screen readers, plain-text tooling, or renderers without Mermaid support.
- [AIES-STD-04-R08] A reader who skips the diagram MUST NOT lose any normative information (see [AIES-STD-04-R04]).

## 5. Neutrality

- [AIES-STD-04-R09] Diagrams MUST NOT contain vendor logos, product screenshots, or vendor, model, or product names, consistent with the vendor-neutrality rules of the [Writing Standard (AIES-STD-03)](writing-standard.md). Components are labeled by capability or role (e.g., "model provider", "agent runtime").

## 6. Legibility

- [AIES-STD-04-R10] Diagram node and edge labels MUST use terms as defined in the [Shared Glossary (AIES-SHARED-01)](../../Shared/Glossary/README.md) and identifiers from the [Shared Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md), so a diagram never introduces vocabulary its prose does not.
- [AIES-STD-04-R11] A diagram SHOULD fit a single screen at normal zoom; a diagram that cannot is a signal to split it, mirroring the one-concern rule of [AIES-STD-01](document-standard.md).

## Related Documents

- [Document Standards index (AIES-STD-00)](README.md)
- [Document Standard (AIES-STD-01)](document-standard.md)
- [Writing Standard (AIES-STD-03)](writing-standard.md)
- [Diagrams directory](../../diagrams/README.md)
- [Shared Glossary (AIES-SHARED-01)](../../Shared/Glossary/README.md)
- [Shared Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md)
- [Governance (AIES-GOV-01)](../../GOVERNANCE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

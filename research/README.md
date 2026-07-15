# Research

| | |
|---|---|
| **Document ID** | AIES-RES-00 |
| **Status** | Review |
| **Audience** | Contributors & maintainers |

This directory is the evidence base behind the AIES standards. AIES is **Evidence Driven** by founding principle: normative choices — a risk tier boundary, a required oversight gate, a competency threshold — should trace back to documented evidence rather than fashion or vendor positioning. Research notes collected here supply that trace: they inform proposals, ADRs, and reviews, and give objectors and proposers a shared factual ground.

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.

**Research is informative, never normative.** Nothing in this directory imposes, modifies, or waives a requirement. A research note MUST NOT contain RFC 2119 requirement language, and standards documents cite research as supporting evidence only — the normative text always stands on its own.

---

## 1. What Belongs Here

- **Literature reviews** — structured summaries of academic and industry publications relevant to an AIES topic.
- **Industry survey summaries** — aggregated findings about how organizations actually practice AI-native engineering.
- **Evaluation-method research** — studies of how AI-produced work and AI-assisted engineers can be measured, relevant to AESQS scoring design.
- **Anonymized case studies** — real adoption experiences with all identifying details removed (organization, individuals, proprietary systems).

Vendor-specific material may appear only as evidence, never as endorsement, and must present alternatives where they exist ([GOVERNANCE.md §7](../GOVERNANCE.md)).

## 2. Note Structure

Every research note MUST use the following structure so that notes remain comparable and citable:

| Section | Content |
|---------|---------|
| **Question** | The specific question the note investigates, stated up front |
| **Method** | How evidence was gathered: sources searched, survey design, selection criteria, known limitations and biases |
| **Findings** | What the evidence shows, separated cleanly from interpretation |
| **Implications** | What the findings suggest for AIES, explicitly naming the affected module(s) (AEBOK, AESQS, AEOS, AEAR, AECT, or Shared) and, where possible, the affected document or requirement IDs |
| **References** | Full citations; external standards by name and version |

Notes are named `RES-NN-<short-title>.md` and carry the standard metadata table per the [Metadata Standard (AIES-STD-02)](../docs/standards/metadata-standard.md).

## 3. Index

<!-- Append one row per research note, in numeric order, in the same pull
     request that adds the note. Keep the "Informs" column pointed at the
     affected module(s) or document(s). -->

| ID | Title | Informs | Date |
|----|-------|---------|------|
| — | *No research notes yet.* | | |

## Related Documents

- [Repository Architecture (AIES-DOC-03)](../docs/ARCHITECTURE.md)
- [Metadata Standard (AIES-STD-02)](../docs/standards/metadata-standard.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [GOVERNANCE.md (AIES-GOV-01)](../GOVERNANCE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

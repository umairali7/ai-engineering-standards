# Versioning Standard

| | |
|---|---|
| **Document ID** | AIES-STD-05 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This standard defines how AIES is versioned: what individual documents carry, how the standard versions as a whole, what constitutes a breaking change, and how deprecation works.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

---

## 1. Documents Carry Status, Never Versions

- [AIES-STD-05-R01 — Versioning Standard, requirement 01] Individual documents MUST carry a Status (Draft, Review, Approved, or Deprecated — per the [Review Standard (AIES-STD-06 — Review Standard)](review-standard.md)) and MUST NOT carry a version number, revision number, or date, per [AIES-STD-02-R02 — Metadata Standard, requirement 02](metadata-standard.md).

**Rationale.** Git history is the complete, tamper-evident record of every document's evolution; release tags mark the states the project stands behind. A per-document version field is a hand-maintained copy of information git already holds, and at repository scale such copies drift. A citation of the form "AIES-STD-05 at v1.2.0" is exact; a citation of a hand-edited document version is not.

## 2. The Standard Versions as a Whole

- [AIES-STD-05-R02 — Versioning Standard, requirement 02] AIES MUST be versioned as a whole using Semantic Versioning, realized as annotated git tags (`vMAJOR.MINOR.PATCH`).
- [AIES-STD-05-R03 — Versioning Standard, requirement 03] Every release MUST have a [CHANGELOG.md](../../CHANGELOG.md) entry in Keep a Changelog format. The CHANGELOG is the only place release dates appear anywhere in the repository.
- [AIES-STD-05-R04 — Versioning Standard, requirement 04] Planned versions MUST be tracked as milestones in [ROADMAP.md](../../ROADMAP.md). Git tags, the CHANGELOG, and ROADMAP milestones are together the only representations of project versions.

### 2.1 SemVer Semantics for a Standards Body

| Segment | Meaning for AIES |
|---------|------------------|
| **Major** | Incompatible changes to Approved normative content: removed or reworded requirements, taxonomy restructuring, glossary redefinitions, changed document or requirement IDs |
| **Minor** | New documents, new requirements that do not break existing conformance, document status promotions |
| **Patch** | Editorial fixes and clarifications with no normative effect |

- [AIES-STD-05-R05 — Versioning Standard, requirement 05] While the standard is pre-1.0 (v0.x), minor versions MAY contain breaking changes; each such change still requires the Class 3 process of §3.

## 3. Breaking Changes

- [AIES-STD-05-R06 — Versioning Standard, requirement 06] The following MUST be treated as breaking changes: any edit to the [Shared Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md); any redefinition of a [Glossary (AIES-SHARED-01 — Glossary)](../../Shared/Glossary/README.md) term; any change to a document ID or requirement ID; removal or semantic weakening of a requirement in a non-Draft document; renaming or removing a heading that has inbound links (see [AIES-STD-03-R17 — Heading changes are treated as breaking changes](writing-standard.md)).
- [AIES-STD-05-R07 — Versioning Standard, requirement 07] Every breaking change MUST follow the Class 3 process of [AIES-GOV-01 — Governance](../../GOVERNANCE.md): an ADR in [adr/](../../adr/README.md), Maintainer lazy consensus, a 7-day public comment period, and cross-module impact analysis.

## 4. Deprecation and Supersession

- [AIES-STD-05-R08 — Versioning Standard, requirement 08] Deprecating any document is a Class 3 decision per [GOVERNANCE.md §5](../../GOVERNANCE.md).
- [AIES-STD-05-R09 — Versioning Standard, requirement 09] A Deprecated document MUST name its successor document(s), by relative link and document ID, in its body immediately after the metadata table. A document deprecated without replacement MUST state that explicitly and record the reasoning ADR.
- [AIES-STD-05-R10 — Versioning Standard, requirement 10] Deprecated documents MUST be retained in the repository (their IDs are never reused, per [AIES-STD-02-R07 — Metadata Standard, requirement 07](metadata-standard.md)); deletion, where ever warranted, is itself a Class 3 decision recorded by ADR.
- [AIES-STD-05-R11 — Versioning Standard, requirement 11] Documents MUST NOT link to a Deprecated document as a normative source; links are repointed to the successor when the deprecation lands.

## Related Documents

- [Document Standards index (AIES-STD-00 — Documentation Standards)](README.md)
- [Metadata Standard (AIES-STD-02 — Metadata Standard)](metadata-standard.md)
- [Writing Standard (AIES-STD-03 — Writing Standard)](writing-standard.md)
- [Review Standard (AIES-STD-06 — Review Standard)](review-standard.md)
- [AIES-GOV-01 — Governance](../../GOVERNANCE.md)
- [CHANGELOG](../../CHANGELOG.md)
- [ROADMAP](../../ROADMAP.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- Keep a Changelog — https://keepachangelog.com/
- Semantic Versioning 2.0.0 — https://semver.org/

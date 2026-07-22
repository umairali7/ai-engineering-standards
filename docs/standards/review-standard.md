# Review Standard

| | |
|---|---|
| **Document ID** | AIES-STD-06 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This standard defines the document lifecycle, the criteria for each status transition, how reviewers are assigned, and the conformance checklist applied before promotion. It is the normative home of the lifecycle formerly described in [Shared/README.md §1.5](../../Shared/README.md), which it supersedes.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

---

## 1. Lifecycle

```
Draft ──► Review ──► Approved ──► Deprecated
  ▲          │
  └──────────┘  (revision reopens Draft)
```

| Status | Meaning |
|--------|---------|
| **Draft** | Under active authoring; content may change without notice |
| **Review** | Content-complete; open for structured peer review |
| **Approved** | Ratified per [AIES-GOV-01 — Governance](../../GOVERNANCE.md); changes require a new revision cycle |
| **Deprecated** | Superseded or withdrawn; successors named per the [Versioning Standard (AIES-STD-05 — Versioning Standard)](versioning-standard.md) |

- [AIES-STD-06-R01 — Review Standard, requirement 01] Every document MUST hold exactly one of these four statuses, recorded in its metadata table per [AIES-STD-02 — Metadata Standard](metadata-standard.md).

## 2. Transition Criteria

| Transition | Who Decides (per GOVERNANCE §5) | Entry/Exit Criteria |
|------------|--------------------------------|---------------------|
| **Draft → Review** | Module Editor (Maintainer for Shared, docs/, and root documents) | Content-complete; conformance checklist (§4) passes; all planned sections present |
| **Review → Approved** | Maintainers by lazy consensus (7 days) | At least two completed peer reviews by Reviewers not involved in authoring; all findings resolved or explicitly waived with recorded reasoning; every MUST-level requirement carries a requirement ID |
| **Approved → Draft** (revision) | Module Editor opens; the decision class of the intended change applies | The prior Approved text remains citable via the release tag containing it |
| **Any → Deprecated** | Class 3 decision | ADR recorded; successor named per [AIES-STD-05-R09 — Versioning Standard, requirement 09](versioning-standard.md); inbound normative links repointed |

- [AIES-STD-06-R02 — Review Standard, requirement 02] A document MUST NOT skip a lifecycle stage; promotion to Approved always passes through Review.
- [AIES-STD-06-R03 — Review Standard, requirement 03] Reviewer assignment MUST follow the roles and decision classes of [GOVERNANCE.md §2–§3](../../GOVERNANCE.md): the affected Module Editor coordinates reviews for module documents; Maintainers review Shared, governance, and standards documents; a Reviewer MUST NOT review a document they substantially authored.

## 3. Review Records

- [AIES-STD-06-R04 — Review Standard, requirement 04] Peer reviews MUST be recorded as pull-request reviews or review issues, so that the evidence supporting a promotion is traceable.
- [AIES-STD-06-R05 — Review Standard, requirement 05] The promotion decision (who decided, under which transition, with which reviews) MUST be traceable from the merge history of the change that updates the Status field.

## 4. Conformance Checklist

- [AIES-STD-06-R06 — Review Standard, requirement 06] Before any promotion out of Draft, the promoting editor MUST verify all of the following:

| # | Check | Governing Standard |
|---|-------|--------------------|
| 1 | Metadata table: exactly three rows, valid ID, valid Status, valid Audience vocabulary | [AIES-STD-02 — Metadata Standard](metadata-standard.md) |
| 2 | Structure: title, metadata, body, Related Documents, References present and ordered | [AIES-STD-01 — Document Standard](document-standard.md) |
| 3 | Writing: RFC 2119 boilerplate where keywords are used; MUST-level requirements tagged; active voice | [AIES-STD-03 — Writing Standard](writing-standard.md) |
| 4 | Glossary and taxonomy: terms used per [Shared Glossary (AIES-SHARED-01 — Glossary)](../../Shared/Glossary/README.md); taxonomy IDs (P/X/AL/RT and the rest) conform to [AIES-SHARED-02 — Taxonomy](../../Shared/Taxonomy/README.md) | [AIES-STD-03 — Writing Standard](writing-standard.md) |
| 5 | Links: every relative link resolves; every cross-reference pairs link with document ID | [AIES-STD-03 — Writing Standard](writing-standard.md) |
| 6 | Arithmetic: every computation in worked content (scores, totals, percentages, counts) re-verified | [AIES-STD-01 — Document Standard](document-standard.md) |
| 7 | Vendor sweep: no AI vendor, model, cloud, or product names in text or diagrams | [AIES-STD-03 — Writing Standard](writing-standard.md), [AIES-STD-04 — Diagram Standard](diagram-standard.md) |

## 5. Demotion

- [AIES-STD-06-R07 — Review Standard, requirement 07] A Review or Approved document found to violate this checklist in a way that misleads readers (broken normative links, wrong taxonomy IDs, failed arithmetic in normative content, vendor references) MUST be demoted to Draft until repaired; the demotion is recorded like any status change. Trivial defects MAY instead be fixed in place as Class 1 editorial changes.

## Related Documents

- [Document Standards index (AIES-STD-00 — Documentation Standards)](README.md)
- [Document Standard (AIES-STD-01 — Document Standard)](document-standard.md)
- [Metadata Standard (AIES-STD-02 — Metadata Standard)](metadata-standard.md)
- [Writing Standard (AIES-STD-03 — Writing Standard)](writing-standard.md)
- [Diagram Standard (AIES-STD-04 — Diagram Standard)](diagram-standard.md)
- [Versioning Standard (AIES-STD-05 — Versioning Standard)](versioning-standard.md)
- [AIES-GOV-01 — Governance](../../GOVERNANCE.md)
- [AIES-SHARED-00 — Shared Standards](../../Shared/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

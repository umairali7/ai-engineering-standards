# Metadata Standard

| | |
|---|---|
| **Document ID** | AIES-STD-02 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This standard defines the metadata table every AIES document carries, the Document ID grammar and code registry, the requirement-ID grammar, and the audience vocabulary.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

---

## 1. The Metadata Table

- [AIES-STD-02-R01] Every document MUST begin (immediately after its title) with a metadata table containing exactly these three rows, in this order:

```markdown
| | |
|---|---|
| **Document ID** | AIES-… |
| **Status** | Draft/Review/Approved/Deprecated |
| **Audience** | <audience list, " · " separated> |
```

| Field | Semantics |
|-------|-----------|
| **Document ID** | The document's stable identifier per §2. Never changes, never reused. |
| **Status** | The document's position in the lifecycle defined by the [Review Standard (AIES-STD-06)](review-standard.md): Draft, Review, Approved, or Deprecated. |
| **Audience** | Who the document is written for, drawn from the vocabulary in §4, multiple values separated by " · ". |

- [AIES-STD-02-R02] The metadata table MUST NOT contain a Version field, a Last Updated field, or any date field.

**Rationale.** Git history and release tags are the system of record for when and how a document changed. Per-document version and date fields duplicate that record and rot at scale: in a repository designed to grow past 500 documents, stale hand-maintained fields are inevitable and worse than absent ones. Release dates exist only in [CHANGELOG.md](../../CHANGELOG.md); project versions exist only as git tags, CHANGELOG entries, and [ROADMAP](../../ROADMAP.md) milestones — see the [Versioning Standard (AIES-STD-05)](versioning-standard.md).

## 2. Document ID Grammar

- [AIES-STD-02-R03] Document IDs MUST follow the grammar `AIES-<AREA>[-<TYPE>]-<ID>`.

### 2.1 AREA Codes

| AREA | Scope | AREA | Scope |
|------|-------|------|-------|
| SHARED | Shared/ (glossary, taxonomy) | DIA | diagrams/ |
| DOC | docs/ and root orientation documents | AEBOK | Body of Knowledge |
| STD | docs/standards/ | AESQS | Qualification Standard |
| GOV | Governance documents | AEOS | Operating System |
| ADR | adr/ | AEAR | Architecture Reference |
| TPL | templates/ | AECT | Certification & Training |
| EX | examples/ | RES | research/ |

### 2.2 TYPE Codes

TYPE is used only where an area subdivides into document families:

| Area | TYPE | Meaning |
|------|------|---------|
| AEBOK | KA | Knowledge Area |
| AEBOK | PAT | Pattern |
| AESQS | CF | Competency Framework |
| AESQS | QP | Qualification Process |
| AESQS | ER | Evaluation Rubrics |
| AESQS | CS | Capability Scoring |
| AESQS | PR | Peer Review |
| AESQS | RR | Revision & Revocation |
| AEOS | OM | Operating Model |
| AEOS | WF | Workflows |
| AEOS | HO | Human Oversight |
| AEOS | GOV | Governance Operations |
| AEOS | ROLE | Role Specification |
| AEAR | CORE | Core Reference Architecture |
| AEAR | XC | Cross-Cutting Concerns |
| AEAR | BP | Blueprint |
| AECT | CERT | Certification Framework |
| AECT | LP | Learning Paths |
| AECT | EB | Exam Blueprints |
| AECT | LAB | Labs |
| AECT | AR | Assessment & Renewal |

### 2.3 Numbering Rules

- [AIES-STD-02-R04] `<ID>` MUST be a two-digit number (`01`–`99`), assigned sequentially within its AREA (and TYPE, where present).
- [AIES-STD-02-R05] `00` MUST be reserved for the index or overview document of its area or type (e.g., AIES-STD-00, AIES-AEBOK-00).
- [AIES-STD-02-R06] Blueprint-class documents MAY use an established name in place of the numeric ID (e.g., `AIES-AEAR-BP-BANKING`); such names, once assigned, are as stable as numbers.
- [AIES-STD-02-R07] Document IDs MUST NOT be reused. When a document is deprecated or removed, its ID is retired permanently.

## 3. Requirement IDs

- [AIES-STD-02-R08] Individual normative requirements MUST be tagged `[<DOC-ID>-R<NN>]`, where `<DOC-ID>` is the containing document's ID and `<NN>` is a two-digit number assigned sequentially within the document (example: `[AIES-STD-02-R08]`).
- [AIES-STD-02-R09] Requirement IDs MUST NOT be reused within a document; a withdrawn requirement's number is retired.

Which requirements are tagged, and how requirements are worded, is governed by the [Writing Standard (AIES-STD-03)](writing-standard.md).

## 4. Audience

- [AIES-STD-02-R10] The Audience field MUST use only these values: Engineering leadership · Architects · Engineers · QA engineers · Security engineers · Platform teams · Assessors & qualification authorities · Governance officers · Educators & training providers · Contributors & maintainers · All readers.
- [AIES-STD-02-R11] Multiple audiences MUST be separated by " · ". "All readers" MUST NOT be combined with other values.
- [AIES-STD-02-R12] New audience values MUST NOT be invented per document; extending the vocabulary is a change to this standard (Class 3 per [GOVERNANCE.md (AIES-GOV-01)](../../GOVERNANCE.md)).

## Related Documents

- [Document Standards index (AIES-STD-00)](README.md)
- [Document Standard (AIES-STD-01)](document-standard.md)
- [Writing Standard (AIES-STD-03)](writing-standard.md)
- [Versioning Standard (AIES-STD-05)](versioning-standard.md)
- [Review Standard (AIES-STD-06)](review-standard.md)
- [Governance (AIES-GOV-01)](../../GOVERNANCE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

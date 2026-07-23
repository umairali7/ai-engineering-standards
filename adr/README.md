# Architecture Decision Records

| | |
|---|---|
| **Document ID** | AIES-ADR-00 |
| **Status** | Review |
| **Audience** | Contributors & maintainers |

This directory holds the Architecture Decision Records (ADRs) of the AIES project: numbered, immutable records of every significant structural or normative decision, written so that future contributors can understand not only *what* was decided but *why*, and what alternatives were rejected.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. When an ADR Is Required

An ADR MUST be written for every **Class 3 — Normative / Breaking** decision as defined in [GOVERNANCE.md §3](../GOVERNANCE.md). In particular:

- Any change to RFC 2119 requirements in an Approved document, or deprecation of an Approved document.
- Any change to the [Shared Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) or redefinition of a [Shared Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md) term — changes to Shared Standards are always at least Class 3, because they break every module.
- Changes that alter Document IDs or requirement IDs.
- Changes to [GOVERNANCE.md](../GOVERNANCE.md) itself.
- Changes to the repository structure (directory layout, module boundaries, dependency model) described in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md), including changes to the document skeletons in [templates/](../templates/).
- Decisions that adopt, replace, or mandate project tooling (e.g., diagram formats, link checkers, release automation).

An ADR MAY also be written for a Class 2 decision when the reasoning is worth preserving. Class 1 (editorial) changes never need an ADR.

## 2. Numbering

ADRs are numbered sequentially as `ADR-NNNN` (four digits, zero-padded) and stored as:

```
adr/ADR-NNNN-<Short-Title>.md
```

Numbers are assigned by taking the next number not yet claimed — by the index (§5) or by any open or rejected ADR pull request — at the time the ADR's pull request is opened. **Numbers are never reused**, even for ADRs that are rejected or superseded — a retired number stays retired so that citations never dangle.

## 3. Status Lifecycle

```
Proposed ──► Accepted ──► Superseded
    │
    └──► (Rejected — recorded in the PR; number retired)
```

- **Proposed** — under discussion; the comment window is open.
- **Accepted** — ratified per [GOVERNANCE.md §4](../GOVERNANCE.md). The Context, Decision Drivers, Options Considered, and Decision sections become immutable.
- **Superseded** — replaced by a later ADR. The superseded ADR MUST link to its successor in its metadata table, and the successor MUST link back.

Accepted ADRs are never edited to change the decision. If circumstances change, a new ADR supersedes the old one — this preserves the historical reasoning chain.

## 4. Submission Process

1. Copy [templates/ADR_TEMPLATE.md](../templates/ADR_TEMPLATE.md) to `adr/ADR-NNNN-<Short-Title>.md` and fill in every section, including honest pros and cons for each rejected option and the disclosure of relevant affiliations required by [GOVERNANCE.md §7](../GOVERNANCE.md).
2. Open a pull request containing the ADR together with the change it justifies (or referencing the follow-up work), per [CONTRIBUTING.md](../CONTRIBUTING.md).
3. Add a row for the ADR to the index in §5 in the same pull request, with status **Proposed**.
4. The Class 3 comment window — **7 calendar days**, announced in the project's public discussion channel — starts when the ADR and its rationale package are complete ([GOVERNANCE.md §4.1](../GOVERNANCE.md)). Incomplete proposals do not start the clock.
5. On lazy consensus of Maintainers with no unresolved substantiated objection, a Maintainer sets the status to **Accepted**, records the deciders, and merges. Objections follow the escalation path in [GOVERNANCE.md §4.3](../GOVERNANCE.md).

## 5. Index

<!-- Append one row per ADR, in numeric order, in the same pull request that
     introduces the ADR. Update the Status column when a status changes;
     never delete or renumber rows. -->

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](ADR-0001-Repository-Foundation.md) | Repository Foundation | Accepted |
| [ADR-0002](ADR-0002-Qualification-Platform.md) | Qualification Platform — an Executable Reference Implementation of AESQS | Superseded by ADR-0009 |
| [ADR-0003](ADR-0003-Competency-Area-Knowledge-Mapping.md) | Competency areas map to knowledge areas by coverage, not bijection | Accepted |
| [ADR-0004](ADR-0004-Repository-Conformance-Audit.md) | `aies audit` — executable repository conformance assessment (maturity scoring, three-state evidence) | Accepted |
| [ADR-0005](ADR-0005-Assessment-as-Code.md) | Assessment-as-Code — declarative competency composition above profiles (gate-first, no blended score) | Accepted |
| [ADR-0006](ADR-0006-Engineering-Capability-Matrix-Boundary.md) | Engineering Capability Matrix boundary and task-mapping governance | Superseded by ADR-0008 |
| [ADR-0007](ADR-0007-Scenario-Rubric-Applicability-Metadata.md) | Scenario rubric applicability metadata | Accepted |
| [ADR-0008](ADR-0008-Engineering-Capability-Matrix-Standard-and-Task-Taxonomy.md) | Establish an Engineering Capability Matrix standard and task taxonomy | Accepted |
| [ADR-0009](ADR-0009-Engineering-Assessment-Platform-Identity.md) | Establish the Engineering Assessment Platform identity | Accepted |
| [ADR-0010](ADR-0010-Human-Readable-Identifier-Convention.md) | Canonical human-readable identifier display convention | Accepted |
| [ADR-0011](ADR-0011-Distinct-Scenario-Breadth-and-Separate-Stability-Studies.md) | Count distinct scenario breadth and separate stability studies | Accepted |
| [ADR-0012](ADR-0012-Qualification-Evidence-Rater-Protocol-and-Immutable-Lifecycle.md) | Separate evaluation observations from qualification evidence and use immutable lifecycle events | Accepted |
| [ADR-0013](ADR-0013-ECM-Task-Decision-Semantics-and-Deployment-Guidance.md) | Govern ECM task decisions and deployment guidance | Accepted |
| [ADR-0014](ADR-0014-Dual-License-Standards-and-Software.md) | Dual-license open standards and executable software | Proposed |
| [ADR-0015](ADR-0015-Subject-and-Evidence-Adapter-Contracts.md) | Subject Descriptor, typed evidence events, and Evidence Adapter contracts | Proposed |

## Related Documents

- [AIES-GOV-01 — Governance](../GOVERNANCE.md)
- [ADR template](../templates/ADR_TEMPLATE.md)
- [AIES-DOC-03 — Repository Architecture](../docs/ARCHITECTURE.md)
- [Documentation Standards (AIES-STD-00 — Documentation Standards)](../docs/standards/README.md)
- [Versioning Standard (AIES-STD-05 — Versioning Standard)](../docs/standards/versioning-standard.md)

## References

None.

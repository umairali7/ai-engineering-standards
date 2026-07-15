# Governance

| | |
|---|---|
| **Document ID** | AIES-GOV-01 |
| **Status** | Review |
| **Audience** | Contributors & maintainers · Governance officers |

This document defines how the AI Engineering Standards (AIES) project makes decisions, ratifies documents, and releases versions of the standard. It exists so that the standard evolves through **engineering consensus**, not individual ownership or vendor influence.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Principles

1. **No individual owner.** No single person or organization owns the standard. Decision authority is distributed across roles and constrained by process.
2. **Consensus over authority.** Decisions default to lazy consensus with public visibility. Authority is used only to break deadlocks, never to bypass discussion.
3. **Vendor neutrality is enforced, not assumed.** Conflict-of-interest rules (§7) apply to every decision that could affect how a vendor's products are positioned.
4. **Everything is traceable.** Significant decisions are recorded as Architecture Decision Records in [adr/](adr/README.md); document status changes are recorded in metadata tables and the [CHANGELOG](CHANGELOG.md).

## 2. Roles

| Role | Scope | How Appointed |
|------|-------|---------------|
| **Contributor** | Anyone who submits issues, proposals, or pull requests | Self-selected |
| **Reviewer** | Contributors invited to perform structured peer review of drafts in their area of expertise | Invited by a Module Editor or Maintainer based on demonstrated contributions |
| **Module Editor** | Editorial authority over exactly one module (AEBOK, AESQS, AEOS, AEAR, or AECT): content coherence, terminology discipline, review coordination | Nominated by a Maintainer, confirmed by lazy consensus of Maintainers (7 days) |
| **Maintainer** | Project-wide: merges, releases, governance changes, Shared Standards stewardship, conflict resolution | Nominated by an existing Maintainer, confirmed by consensus of all Maintainers |

### 2.1 Responsibilities

- **Contributors** follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [Documentation Standards (AIES-STD-00)](docs/standards/README.md). Proposals for substantive changes MUST include the engineering rationale package (problem statement, alternatives, trade-offs, references, impact analysis).
- **Reviewers** evaluate drafts against the [evaluation dimensions](Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6) — correctness, completeness, safety, maintainability, efficiency, traceability — and record their review as PR reviews or review issues.
- **Module Editors** are accountable for their module's internal consistency, for ensuring it uses the [Shared Glossary](Shared/Glossary/README.md) and [Taxonomy](Shared/Taxonomy/README.md) without redefinition, and for shepherding module documents through the status lifecycle (§5). There is exactly one Module Editor per module; a person MAY edit at most two modules.
- **Maintainers** hold merge rights on protected branches, steward the Shared Standards, run releases (§6), and adjudicate escalations (§4.3). At least three Maintainers SHOULD exist; while the project has fewer, Maintainers act with the same process discipline and record all decisions publicly.

### 2.2 Stepping Down and Removal

Any role holder MAY step down at any time by public notice. A Module Editor or Maintainer who is inactive for 90 days, or who repeatedly violates this document or the [Code of Conduct](CODE_OF_CONDUCT.md), MAY be removed by consensus of the remaining Maintainers (the affected person abstains).

## 3. Decision Classes

Every change falls into one of three classes. The class determines who decides and how.

| Class | Examples | Decision Path |
|-------|----------|---------------|
| **Class 1 — Editorial** | Typos, formatting, broken links, grammar, non-semantic rewording, diagram cleanup | One Maintainer (or the affected Module Editor) reviews and merges directly. No comment window. |
| **Class 2 — Substantive** | New sections, changed guidance, new examples, restructuring within a module | Approval by the affected Module Editor **plus** at least one peer Reviewer. Open for comment at least 72 hours before merge. |
| **Class 3 — Normative / Breaking** | Any change to RFC 2119 requirements; any edit to the [Shared Taxonomy](Shared/Taxonomy/README.md) or redefinition of a [Glossary](Shared/Glossary/README.md) term; changes to this document; changes that alter document IDs or requirement IDs; deprecating an Approved document | ADR in [adr/](adr/README.md) **plus** lazy consensus of Maintainers **plus** a 7-day public comment period (§4). Cross-module impact analysis is mandatory. |

Classification disputes are resolved upward: if anyone with a role argues in good faith that a change is Class 3, it is treated as Class 3.

Changes to the Shared Standards are always at least Class 3, because a change to a shared definition is a breaking change for every module (see [Shared/README.md](Shared/README.md)).

## 4. Consensus Process

AIES uses **lazy consensus**: a proposal is accepted if, after the required comment window, no unresolved substantiated objection remains.

### 4.1 Comment Windows

| Class | Minimum Window |
|-------|----------------|
| Class 1 | None |
| Class 2 | 72 hours |
| Class 3 | 7 calendar days, announced in the project's public discussion channel |

The window starts when the proposal (PR + ADR where required) is complete — i.e., contains the full rationale package. Incomplete proposals do not start the clock.

### 4.2 Objections

- An objection MUST be substantiated: it states the engineering problem the proposal creates, ideally with a counter-proposal. "I don't like it" does not block.
- The proposer and objector first attempt resolution in the PR/issue thread. Most objections resolve through amendment.
- An objection is **resolved** when the objector withdraws it, the proposal is amended to address it, or the escalation path (§4.3) overrules it with recorded reasoning.

### 4.3 Escalation Path

1. **Thread resolution** — proposer and objector, moderated by the affected Module Editor (target: 7 days).
2. **Maintainer mediation** — a Maintainer not party to the dispute proposes a resolution (target: 7 days).
3. **Maintainer vote** — simple majority of Maintainers, conflicted Maintainers (§7) abstaining. The outcome and its reasoning MUST be recorded in the ADR or PR thread. This step is the last resort and its use is itself a signal the proposal may need rework.

A proposal that cannot achieve consensus after escalation is rejected without prejudice; it MAY return with new evidence or a revised design.

## 5. Document Ratification

Documents move through the lifecycle defined in the [Review Standard (AIES-STD-06)](docs/standards/review-standard.md): `Draft → Review → Approved → Deprecated`.

| Transition | Who Decides | Requirements |
|------------|-------------|--------------|
| **Draft → Review** | Module Editor (Maintainer for Shared/root docs) | Document is content-complete, metadata table current, conventions followed, all taxonomy/glossary references valid |
| **Review → Approved** | Maintainers by lazy consensus (7 days) | At least two completed peer reviews by Reviewers not involved in authoring; all review findings resolved or explicitly waived with reasoning; for normative documents, every requirement carries a stable requirement ID |
| **Approved → Draft** (revision) | Module Editor opens; Class of the intended change applies | Prior Approved text remains citable through the release in which it shipped ([CHANGELOG.md](CHANGELOG.md)) |
| **Any → Deprecated** | Class 3 decision | Metadata table MUST name the successor document |

Shared Standards documents and this governance document are ratified by Maintainers only; module documents are ratified by Maintainers on the recommendation of the Module Editor.

## 6. Releases

### 6.1 Versioning

The standard as a whole follows Semantic Versioning:

- **Major** — incompatible changes to Approved normative content (e.g., taxonomy restructuring, removed requirements).
- **Minor** — new documents, new requirements that don't break existing conformance, document status promotions.
- **Patch** — editorial fixes and clarifications with no normative effect.

While the standard is pre-1.0 (v0.x), minor versions MAY contain breaking changes; each one still requires the Class 3 process.

### 6.2 Release Process

A release is cut by a Maintainer using this checklist:

1. All PRs targeted for the release are merged; no open Class 3 comment window overlaps the release content.
2. Every changed document's metadata table conforms to the [Metadata Standard (AIES-STD-02)](docs/standards/metadata-standard.md) and shows the correct status.
3. Cross-references and relative links validated across the repository.
4. Glossary and Taxonomy checked for terms introduced by the release but not yet registered.
5. [CHANGELOG.md](CHANGELOG.md) updated in Keep a Changelog format; Unreleased section emptied into the new version entry.
6. [ROADMAP.md](ROADMAP.md) statuses updated.
7. Release tagged; release notes published summarizing normative changes separately from editorial ones.
8. A second Maintainer verifies the checklist (four-eyes principle) before the tag is announced.

## 7. Conflict of Interest and Vendor Influence

AIES is vendor-neutral by [founding principle](README.md#guiding-principles). Because contributors will often be employed by, invested in, or otherwise affiliated with AI vendors, platform providers, consultancies, or certification businesses, neutrality is protected by process:

1. **Disclosure.** Contributors MUST disclose affiliations relevant to a proposal (employment, equity, paid engagements, vendor partnerships) in the proposal itself. Role holders MUST maintain a standing disclosure of their primary affiliation.
2. **No sole approval.** A person affiliated with a vendor MUST NOT be the sole approver of any change that affects — favorably or unfavorably — how that vendor's products, models, or services are positioned relative to the standard. At least one unconflicted approver is required.
3. **Recusal from escalation.** In escalation votes (§4.3), Maintainers with a disclosed conflict on the matter MUST abstain.
4. **Neutral text.** Normative text MUST NOT name specific AI vendors, models, or commercial products. Vendor-specific material is limited to non-normative examples and research notes, and even there MUST present alternatives where they exist.
5. **Diversity guard.** No single organization SHOULD hold a majority of Maintainer seats. If hiring or acquisition creates such a majority, the Maintainers MUST restore balance within 90 days (e.g., by appointing additional unaffiliated Maintainers).
6. **Violations.** Undisclosed conflicts discovered after a decision reopen that decision at its original class; deliberate concealment is grounds for removal (§2.2).

## 8. Amending This Document

Changes to this document are Class 3: ADR, Maintainer lazy consensus, and a 7-day public comment period. Change history is tracked in the [CHANGELOG](CHANGELOG.md).

## Related Documents

- [CONTRIBUTING.md (AIES-GOV-02)](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md (AIES-GOV-03)](SECURITY.md)
- [Documentation Standards (AIES-STD-00)](docs/standards/README.md)
- [Review Standard (AIES-STD-06)](docs/standards/review-standard.md)
- [Versioning Standard (AIES-STD-05)](docs/standards/versioning-standard.md)
- [Architecture Decision Records (AIES-ADR-00)](adr/README.md)
- [Continuous Improvement & Maintenance (AIES-DOC-09)](docs/IMPROVEMENT.md) — the review cadence and the data-driven improvement loop

## References

- RFC 2119 / RFC 8174 (normative keyword interpretation)

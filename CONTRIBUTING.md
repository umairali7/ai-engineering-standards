# Contributing to AIES

| | |
|---|---|
| **Document ID** | AIES-GOV-02 |
| **Status** | Review |
| **Audience** | Contributors & maintainers |

Thank you for helping build a vendor-neutral standard for AI-native software engineering. This guide covers the practical mechanics; decision authority and consensus rules live in [GOVERNANCE.md](GOVERNANCE.md).

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.

---

## 1. Ways to Contribute

| Contribution | How to Start | Decision Class ([GOVERNANCE §3](GOVERNANCE.md#3-decision-classes)) |
|--------------|--------------|--------------------------------------------------|
| Typos, broken links, formatting, wording | Open a PR directly | Class 1 — Editorial |
| Errata (technical defects in the standard) | Open an [Errata Report](.github/ISSUE_TEMPLATE/bug_report.md) issue | Class 1, 2, or 3 depending on the fix (Class 3 if normative text changes) |
| New or revised content within a module | Open a [Content Proposal](.github/ISSUE_TEMPLATE/feature_request.md) issue, then a PR | Class 2 — Substantive |
| Changes to normative requirements, [Taxonomy](Shared/Taxonomy/README.md), or [Glossary](Shared/Glossary/README.md) definitions | Content Proposal issue + ADR (see §6) | Class 3 — Normative |
| Worked examples | PR into [examples/](examples/README.md) | Class 2 |
| Supporting research and citations | PR into [research/](research/README.md) | Class 2 |
| Translations | Open a Content Proposal first — translation infrastructure is being designed | Class 2 |
| Peer review of drafts | Comment on open PRs, or ask a Module Editor to be added as a Reviewer | — |

New users and integrators can also contribute structured evidence without
drafting a standard change:

| Feedback path | Use it for |
|---|---|
| [First-run experience](https://github.com/umairali7/ai-engineering-standards/issues/new/choose) | Installation, demo, planning, evaluation, resume, report opening, or cleanup friction |
| [Report comprehension](https://github.com/umairali7/ai-engineering-standards/issues/new/choose) | Confusing capability, confidence, unknown, fit, human-evaluation, or qualification boundaries |
| [Reproducible case-study interest](https://github.com/umairali7/ai-engineering-standards/issues/new/choose) | A publishable local/hosted evaluation, compatible comparison, repository assurance, or reassessment story |
| [Scenario instrument review](https://github.com/umairali7/ai-engineering-standards/issues/new/choose) | Independent review of construct relevance, anchors, gaming resistance, risk tier, rubric applicability, twins, or ET mapping |
| [Subject or Evidence Adapter proposal](https://github.com/umairali7/ai-engineering-standards/issues/new/choose) | A version-pinned executor, evidence bridge, export, or Subject Assessment Profile with explicit provenance, loss, privacy, and claim boundaries |

The issue chooser contains a private security-advisory route. Never place
credentials, private prompts/responses, unredacted reports, production
endpoints, or confidential evidence in a public issue.

## 2. Before You Start

1. **Read the [Documentation Standards (AIES-STD-00 — Documentation Standards)](docs/standards/README.md)** — metadata tables, document IDs, RFC 2119 usage, status lifecycle. Every AIES document follows them.
2. **Check the [Glossary](Shared/Glossary/README.md) and [Taxonomy](Shared/Taxonomy/README.md)** before introducing terminology. If a concept already has a canonical term or ID (P01–P16, X01–X15, AL0 — Manual through AL4 — Autonomous, RT1 — Minimal through RT4 — Critical, ROLE-nn, CL1–CL4, ART-nn, EV1–EV6), use it. Never redefine a shared term inside a module.
3. **Search existing issues, PRs, and [ADRs](adr/README.md)** — your idea may already be under discussion or previously decided.
4. **Check the [ROADMAP](ROADMAP.md)** — contributions aligned with the current phase are reviewed fastest.

## 3. Proposal Requirements

Per the [project README](README.md#contributing), every proposal for substantive or normative change MUST include the full engineering rationale package. Proposals missing these elements will be returned for completion before the review clock starts.

Use this template (also enforced by the [Content Proposal issue template](.github/ISSUE_TEMPLATE/feature_request.md)):

```markdown
## Problem Statement
What gap or defect in the standard does this address? Who is affected?

## Proposed Change
What exactly changes — documents, sections, requirements. Draft text where possible.

## Module(s) Affected
Shared / AEBOK / AESQS / AEOS / AEAR / AECT / docs — and whether the change is
editorial, substantive, or normative/breaking.

## Engineering Rationale
Why this design. What evidence supports it (measured outcomes, field experience,
published research)?

## Alternatives Considered
At least one credible alternative, including "do nothing", and why it was not chosen.

## Trade-offs
What this change costs: complexity, compatibility, adoption burden, maintenance.

## References
Standards, papers, prior ADRs, industry practice cited by name and version.

## Impact Analysis
Which documents, requirement IDs, and modules must change as a consequence.
For Shared changes: impact on all five modules (this is always breaking).
```

## 4. Workflow

1. **Fork** the repository and create a branch:

   ```
   <type>/<module>/<short-description>
   ```

   Examples: `content/aebok/context-engineering-ka`, `fix/shared/broken-taxonomy-links`, `proposal/aeos/escalation-runbook`.

2. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). Types used here: `docs` (content), `fix` (errata/editorial), `feat` (new documents/sections), `chore` (tooling/repo). Scope is the module or area:

   ```
   docs(aebok): add knowledge area on evaluation-driven development
   fix(shared): correct RT3 — Significant examples in taxonomy risk tiers
   feat(aesqs): introduce capability scoring worksheet
   chore(github): update issue templates
   ```

3. **Sign off** every commit (`git commit -s`) — see §7 on DCO.

4. **Open a PR** using the [PR template](.github/PULL_REQUEST_TEMPLATE.md). Link the Content Proposal issue and ADR where required. Keep PRs to a single logical change; large content lands better as a series of reviewable PRs.

5. **Review.** Expect a first response within **7 calendar days** (project volunteers permitting). Class 2 changes need the affected Module Editor plus one Reviewer and a 72-hour open window; Class 3 changes need an ADR, Maintainer consensus, and a 7-day public comment period. Reviewers evaluate against the [evaluation dimensions EV1 — Correctness through EV6 — Traceability](Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6).

6. **Merge.** A Maintainer or Module Editor merges once the applicable class requirements in [GOVERNANCE.md](GOVERNANCE.md) are met. Stale PRs with unanswered review feedback for 30 days may be closed without prejudice.

## 5. Style Guide (Summary)

The normative source is the [Documentation Standards suite (AIES-STD-00 — Documentation Standards)](docs/standards/README.md). In brief:

- **Metadata table first.** Every standard document begins with exactly three rows — Document ID, Status, Audience — per the [Metadata Standard (AIES-STD-02 — Metadata Standard)](docs/standards/metadata-standard.md). Update it in the same PR that changes the document. No version or date rows; release history lives only in [CHANGELOG.md](CHANGELOG.md).
- **RFC 2119 discipline.** Capitalized MUST/SHOULD/MAY only in normative statements, with the standard interpretation clause present in the document. Do not capitalize these words casually in prose.
- **Requirement IDs.** Normative requirements carry stable IDs: `[<DOC-ID>-R<NN>]`.
- **Vendor neutrality.** Normative text MUST NOT name AI vendors, models, or commercial products. Describe capabilities ("a code-generation agent operating at AL3 — Delegated"), not brands. Non-normative examples that mention vendors must present alternatives and are subject to the conflict-of-interest rules in [GOVERNANCE.md §7](GOVERNANCE.md#7-conflict-of-interest-and-vendor-influence).
- **Terminology.** Use Glossary terms exactly as defined; reference taxonomy IDs rather than restating scales.
- **Links.** Relative markdown links within the repository; cross-reference AIES documents by link **and** Document ID. External standards cited by name and version.
- **Diagrams.** Text-based (Mermaid or ASCII), stored in the document or [diagrams/](diagrams/README.md), per the [Diagram Standard (AIES-STD-04 — Diagram Standard)](docs/standards/diagram-standard.md).
- **Language.** Professional, precise, evidence-oriented. Avoid marketing language and unverifiable claims.

## 6. ADR Process

Architecturally or normatively significant decisions — anything Class 3, plus structural decisions about the standard itself — are recorded as Architecture Decision Records. See [adr/README.md](adr/README.md) for the template, numbering, and lifecycle. An ADR accompanies (not replaces) the PR that implements it.

## 7. Developer Certificate of Origin

Contributions are accepted under the [Developer Certificate of Origin v1.1](https://developercertificate.org/). By signing off (`Signed-off-by: Your Name <email>`, added automatically by `git commit -s`), you certify that you have the right to submit the work under the license applicable to its destination path (see [LICENSE.md](LICENSE.md)). Standards and reusable assessment content default to CC BY-SA 4.0; executable software defaults to Apache 2.0. Mixed-purpose files must be split or carry an explicit SPDX notice. Run `python platform/scripts/check_license_boundaries.py .` from the repository root before submitting. PRs with unsigned commits will be asked to rebase with sign-offs.

## 8. Conduct and Conflicts

All participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). If you are affiliated with an AI vendor or a party commercially affected by a proposal, disclose it in the proposal per [GOVERNANCE.md §7](GOVERNANCE.md#7-conflict-of-interest-and-vendor-influence).

---

Questions? Open a discussion thread in the project's Discussions space, or file an issue if none fits.

## Related Documents

- [AIES-GOV-01 — Governance](GOVERNANCE.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [Documentation Standards (AIES-STD-00 — Documentation Standards)](docs/standards/README.md)
- [Writing Standard (AIES-STD-03 — Writing Standard)](docs/standards/writing-standard.md)
- [AIES-ADR-00 — Architecture Decision Records](adr/README.md)
- [AIES-TPL-00 — Templates](templates/README.md)

## References

- Developer Certificate of Origin v1.1 — <https://developercertificate.org/>
- Conventional Commits v1.0.0 — <https://www.conventionalcommits.org/en/v1.0.0/>
- RFC 2119 (normative keyword interpretation)

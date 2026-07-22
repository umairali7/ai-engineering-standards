# ADR-0014: Dual-license open standards and executable software

| | |
|---|---|
| **ADR** | ADR-0014 |
| **Status** | Proposed |
| **Deciders** | Maintainers after the Class 3 comment window; names recorded on acceptance |
| **Supersedes / Superseded by** | — |

## Context

AIES contains two materially different kinds of work. Its standards,
taxonomies, assessment definitions, scenarios, rubrics, templates, and
explanatory documents are intended to be read, copied into organizational
practice, and adapted with durable attribution. Its Engineering Assessment
Platform, tests, automation, and other source code are intended to be embedded,
modified, and distributed as open-source software.

The repository currently grants no license. That blocks lawful reuse and makes
the package metadata intentionally incomplete. A single license optimized for
one class of work gives a poor fit for the other: a content license is awkward
for executable software, while a permissive software license does not preserve
share-alike obligations for derivative standards.

This is a Class 3 decision. This proposal does not itself grant a license. The
license change takes effect only after the complete proposal is publicly
announced, the seven-calendar-day comment window elapses, substantiated
objections are resolved, and Maintainers record acceptance.

**Affiliation disclosure:** proposer and decider disclosures are not yet
recorded. They must be added to the proposal record before the governance
comment window begins.

## Decision Drivers

- Guarantee an openly licensed standard and open-source executable platform.
- Let organizations reproduce and adapt the standard with clear attribution.
- Keep derivative standard and assessment content openly available.
- Use a software-native license with an explicit patent grant for the platform.
- Give every repository path one unambiguous applicable license.
- Preserve third-party licenses, contributor copyright, provenance, and
  trademark boundaries.
- Avoid implying that permission existed before ratification.

## Existing-Contracts Check

- **Can the existing contracts express this?** No. `LICENSE.md` explicitly
  reserves all rights, and package metadata says license selection is pending.
- **If no, which contract is insufficient, and what version bump / conformance
  impact does the change carry?** The root license notice and platform package
  metadata require coordinated changes. Adoption changes distribution terms
  but not assessment semantics, evidence schemas, or engine conformance; no
  evidence-contract version bump is required.

## Options Considered

### Option A — Keep all rights reserved

- **Pros:** No ambiguity about permission before governance is complete.
- **Cons:** Prevents the reuse, implementation, and independent adoption needed
  for an open engineering standard and reference platform.

### Option B — Apply CC BY-SA 4.0 to the whole repository

- **Pros:** One license; strong attribution and share-alike for derivatives.
- **Cons:** A content license is not a conventional open-source software
  license; its terms and ecosystem conventions are a poor fit for packages.

### Option C — Apply Apache 2.0 to the whole repository

- **Pros:** One OSI-approved permissive license with an explicit patent grant
  and good compatibility for software adoption.
- **Cons:** Does not require derivative standards or scenario corpora to remain
  available under equivalent open terms.

### Option D — CC BY-SA 4.0 for content and Apache 2.0 for software

- **Pros:** Each work class receives a conventional open license aligned with
  its reuse model; attribution, share-alike content, and patent-aware
  open-source software adoption are explicit.
- **Cons:** Requires a precise path boundary and two license texts; mixed files
  and copied examples need clear handling.

## Decision

Adopt Option D after ratification:

1. **CC BY-SA 4.0 scope.** Apply Creative Commons Attribution-ShareAlike 4.0
   International to standards and reusable assessment content: root and module
   Markdown documentation; `Shared/`, `AEBOK/`, `AESQS/`, `AEOS/`, `AEAR/`,
   `AECT/`, `ECM/`, `adr/`, `docs/`, `research/`, `templates/`, and `diagrams/`;
   plus platform scenario, rubric, profile, assessment, and declarative
   conformance-data definitions.
2. **Apache 2.0 scope.** Apply Apache License 2.0 to executable implementation
   and software-development material: `platform/src/`, `platform/tests/`,
   repository and platform scripts, CI automation, packaging/build
   configuration, executable conformance engines and test harnesses, and
   source-code examples whose primary purpose is execution.
3. **Boundary control.** The accepted `LICENSE.md` will contain the authoritative
   path table. A file-specific SPDX identifier or notice overrides the path
   default. Files combining substantial prose and executable code must either
   be split or carry an explicit applicable-license notice.
4. **Third-party material.** Dependencies and incorporated third-party material
   retain their own licenses and notices. This decision grants no rights the
   contributors do not hold.
5. **Copyright and trademarks.** Contributors retain copyright. The licenses
   grant copyright permissions only within their terms; no AIES name, logo, or
   certification trademark rights are granted.
6. **Contributions.** DCO sign-off continues to certify contribution rights.
   Contributions are made under the license applicable to the destination
   path, as stated in `CONTRIBUTING.md` after acceptance.
7. **No retroactive implication.** Until this ADR is accepted and the license
   texts/notices are merged, the current all-rights-reserved notice remains in
   force.

## Consequences

**Positive:**

- Organizations can adapt AIES standards while keeping derivative content open
  and attributable.
- Implementers can adopt the platform under a conventional open-source license
  that includes patent terms.
- A path-level table removes ambiguity for scenario corpora and mixed-purpose
  repository content.

**Negative:**

- Contributors must understand two licenses. Mitigation: one authoritative
  scope table, SPDX metadata, and automated path checks.
- Share-alike obligations may deter some proprietary derivative standards.
  This is intentional for standards/content and does not extend to
  independently written software merely implementing the standard.
- Mixed files can be ambiguous. Mitigation: split them or add a file-specific
  SPDX notice during review.

## Compliance & Verification

After acceptance, the implementation change must:

- add verbatim official `CC-BY-SA-4.0` and `Apache-2.0` license texts;
- replace `LICENSE.md` with the authoritative scope table and effective notice;
- update package SPDX/license metadata, README badges, the Charter, FAQ,
  architecture, contribution terms, release documentation, and notices;
- add a CI check that every distributed path resolves to exactly one applicable
  license and that third-party notices are retained;
- record the proposal announcement, comment-window dates, objections and
  dispositions, named deciders, affiliation disclosures, and acceptance.

## Links

- Pull request: to be added when proposed for public review.
- [AIES-GOV-01 — Governance](../GOVERNANCE.md)
- [AIES-GOV-02 — Contributing to AIES](../CONTRIBUTING.md)
- [License status](../LICENSE.md)
- [Creative Commons Attribution-ShareAlike 4.0 legal code](https://creativecommons.org/licenses/by-sa/4.0/legalcode)
- [Apache License 2.0 official text](https://www.apache.org/licenses/LICENSE-2.0.txt)
- [Apache guidance for applying the license](https://www.apache.org/legal/apply-license)

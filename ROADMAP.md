# Roadmap

| | |
|---|---|
| **Document ID** | AIES-GOV-04 |
| **Status** | Review |
| **Audience** | All readers |

The phased delivery plan for the AI Engineering Standards. Knowledge defines
the engineering baseline; assessment produces evidence; competency analysis
turns that evidence into the Engineering Capability Matrix (ECM), engineering
fit, comparison, and—when explicitly governed—formal qualification. The
standards modules remain sequenced AEBOK → AESQS → AEOS → AEAR → AECT, with
foundations before implementation and public release.

> **All dates are milestone-relative, not calendar commitments.** A phase ships when its exit criteria are met, not when a date arrives. Status is updated at each release.

---

## Phase Overview

| # | Phase | Status |
|---|-------|--------|
| 1 | Repository Foundation | ✅ Complete (v0.3.1) |
| 2 | AEBOK — Body of Knowledge | 🔍 Content complete; independent approval reviews pending |
| 3 | AESQS — Qualification Standard | 🔍 Content complete; independent approval reviews pending |
| 4 | AEOS — Operating System | 🔍 Content complete; independent approval reviews pending |
| 5 | AEAR — Architecture Reference | 🔍 Content complete; independent approval reviews pending |
| 6 | AECT — Certification & Training | 🔍 Content complete; independent approval reviews pending |
| 7 | Reference Implementations | 🚧 Started — platform/conformance references landed; reproducible public pilots outstanding |
| 8 | Engineering Assessment Platform | ✅ M1–M4 delivered; 🚧 hardening and subject expansion |
| 9 | v1.0 Public Release | ⏳ Planned |

---

## Phase 1 — Repository Foundation

**Status: ✅ Complete (v0.3.1)**

Deliverables:

- Root [README](README.md), [Vision](docs/VISION.md), and [Project Charter](docs/PROJECT_CHARTER.md)
- [Shared Standards](Shared/README.md): documentation conventions, canonical [Glossary](Shared/Glossary/README.md), canonical [Taxonomy](Shared/Taxonomy/README.md) (SDLC phases, cross-cutting domains, autonomy levels, risk tiers, roles, competency levels, artifact types, evaluation dimensions)
- Full governance suite: [GOVERNANCE](GOVERNANCE.md), [CONTRIBUTING](CONTRIBUTING.md), [SECURITY](SECURITY.md), [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md), issue/PR templates
- [ADR process](adr/README.md) with ADR-0001; [document templates](templates/README.md)
- Skeleton READMEs and scoping for all five modules

Entry criteria: project charter agreed. Exit criteria: all foundation documents exist at Draft status, conventions are self-consistent, modules have scoped outlines, governance process is executable as written.

## Phase 2 — AEBOK (Body of Knowledge)

**Status: 🔍 In Review (v0.4.0) — content-complete; independent non-author
peer reviews, finding dispositions, and ratification remain**

Deliverables:

- Knowledge Area structure mapped to SDLC phases P01–P16 and cross-cutting domains X01–X15
- One Knowledge Area document per area (`AIES-AEBOK-KA-nn`) with practices, patterns, and anti-patterns
- AI-native SDLC guidance per phase, aligned with [docs/SDLC.md](docs/SDLC.md)
- Curated references into [research/](research/README.md)

Entry criteria: Phase 1 exit; Taxonomy stable enough that KA structure won't churn. Exit criteria: all KA documents content-complete at Draft, terminology audit clean against the Glossary, at least two Knowledge Areas taken through peer review to validate the review process.

## Phase 3 — AESQS (Qualification Standard)

**Status: 🔍 In Review (v0.4.0) — content-complete; independent non-author
peer reviews, finding dispositions, and ratification remain**

Deliverables:

- Competency framework (`AIES-AESQS-CF-nn`) on the CL1–CL4 scale, mapped to AEBOK Knowledge Areas
- Capability scoring method along evaluation dimensions EV1–EV6, with rubrics per role and phase
- Qualification lifecycle specification: scoping, evidence requirements, expiry, revocation
- Assessment templates in [templates/](templates/README.md)

Entry criteria: AEBOK KA structure frozen (competencies must map to knowledge). Exit criteria: rubrics exist for every ROLE-nn, a complete worked qualification example exists in [examples/](examples/README.md), scoring method dry-run performed on at least one real or synthetic case.

## Phase 4 — AEOS (Operating System)

**Status: 🔍 In Review (v0.4.0) — content-complete; independent non-author
peer reviews, finding dispositions, and ratification remain**

Deliverables:

- Role specifications (`AIES-AEOS-ROLE-nn`) for ROLE-01…ROLE-14, including human-mandatory roles
- Workflow definitions binding autonomy levels AL0 — Manual through AL4 — Autonomous to risk tiers RT1 — Minimal through RT4 — Critical with approval gates
- Human oversight model: gate placement, sampling, escalation runbooks
- Governance and audit-trail requirements (`AIES-AEOS-GOV-nn`) covering artifacts ART-14/ART-15

Entry criteria: AESQS scoring method drafted (autonomy increases must be qualification-driven). Exit criteria: every workflow names its gates, evidence, and escalation paths; no normative statement conflicts with Shared Taxonomy defaults; one end-to-end operating-model example documented.

## Phase 5 — AEAR (Architecture Reference)

**Status: 🔍 In Review (v0.4.0) — content-complete; independent non-author
peer reviews, finding dispositions, and ratification remain**

Deliverables:

- Core reference architecture for enterprise AI-native engineering platforms (vendor-neutral component model)
- Capability-to-component mapping traceable to AEOS workflows and AEBOK practices
- Industry blueprints (`AIES-AEAR-BP-*`) — banking first, additional regulated industries as contributed
- Architecture diagrams as text-based sources in [diagrams/](diagrams/README.md)

Entry criteria: AEOS workflows drafted (architecture must support the operating model). Exit criteria: core reference architecture reviewed by at least two independent Reviewers with architecture background; every component justified by a requirement or workflow; at least one blueprint complete.

## Phase 6 — AECT (Certification & Training)

**Status: 🔍 In Review (v0.4.0) — content-complete; independent non-author
peer reviews, finding dispositions, and ratification remain**

Deliverables:

- Certification tracks (`AIES-AECT-CERT-nn`) aligned to competency levels CL1–CL4
- Learning paths mapping AEBOK Knowledge Areas to each track
- Lab and exercise specifications; examination blueprint (format, coverage, pass criteria)
- Credential policy: validity, renewal, revocation, alignment with AESQS qualifications

Entry criteria: AEBOK and AESQS content-complete (curriculum derives from both). Exit criteria: every track traces to competencies and knowledge areas; exam blueprint reviewed for assessability; sample lab exercised end-to-end.

## Phase 7 — Reference Implementations

**Status: 🚧 Started — reframed to consume the Engineering Assessment Platform
(Phase 8); platform/conformance references are delivered and reproducible
public pilot artifacts remain outstanding**

Phase 7 no longer builds evaluation tooling of its own: it produces reference *artifacts* by running the Phase 8 platform, plus reference implementations of the surrounding operating model.

Deliverables:

- Worked qualification runs executed with the `aies` platform ([AIES-DOC-06 — Engineering Assessment Platform Specification](docs/PLATFORM.md)) published as reference artifacts in [examples/](examples/README.md) — evidence packages, reports, and Qualification Records for representative role scopes
- Executable, vendor-neutral reference implementations of key AEOS workflows and AEAR components, built against the platform's runtime-adapter boundary (no vendor lock-in)
- Conformance checklists linking implementation behavior to requirement IDs

Entry criteria: platform milestone M1 shipped ([PLATFORM.md §10](docs/PLATFORM.md)); relevant AEOS/AEAR documents at Review status or later. Exit criteria: at least one complete worked qualification run published and reproducible by a third party; implementations demonstrate the normative requirements they claim; each carries its own security policy and CI.

## Phase 8 — Engineering Assessment Platform

**Status: ✅ Core M1–M4 delivered; 🚧 hardening, independent pilots, and
subject-adapter expansion remain (per
[ADR-0009](adr/ADR-0009-Engineering-Assessment-Platform-Identity.md))**

The `aies` command-line platform is the executable reference implementation of
the AIES evidence architecture. It currently performs non-blocking engineering
evaluation of locally or remotely hosted AI deployments and conformance/practice
audits of repositories. Automated evidence produces Engineering Assessment
Results, ECM, Engineering Fit Guidance, comparison, and linked reports without
requiring human review. Formal qualification is a separate, explicitly
requested, human-governed path. The canonical evidence contracts are
subject-neutral so dedicated executors can be added for agents, MCP servers,
RAG systems, pipelines, platforms, and composite systems without another
identity change. The platform is specified in
[AIES-DOC-06 — Engineering Assessment Platform Specification](docs/PLATFORM.md).
Originally gated behind Phase 7, it was pulled forward so execution could
harden the standards before v1.0; Phase 7 now consumes it.

Deliverables (milestones per [PLATFORM.md §10](docs/PLATFORM.md)):

- ✅ **M1 — Runnable core:** Python package and CLI; environment discovery,
  registry, collection, scoring, and Markdown/JSON evidence reports
- ✅ **M2 — Scoring depth:** CA-01 through CA-12 suites, profiles, immutable
  gates for formal qualification, result history, observed ECM comparison, and
  the runtime/deployment abstraction
- ✅ **M3 — Scale and integration:** frozen runtime-adapter contract with an
  out-of-tree example, linked Markdown/JSON/HTML report bundles, parallel
  execution, durable live progress/ETA, resume, and result index
- ✅ **M4 — Decision products and workflow:** non-blocking automated
  Engineering Evaluation, ECM, Engineering Fit Guidance, grounding diagnostics,
  peer review, optional human evaluation, explicit formal qualification,
  Qualification Records, generated dashboard, read-only API, conformance
  runner, and CI

Entry criteria: AESQS at Review status (execution feedback is part of hardening
it toward Approved);
[ADR-0002](adr/ADR-0002-Qualification-Platform.md) accepted. Core exit criteria:
the platform executes automated engineering evaluation and the separate full
formal-qualification cycle through a human-recorded decision ✅; results are
reproducible on an identical environment fingerprint ✅; conformance and
platform tests map enforced behavior to AESQS requirement IDs ✅. Actual local
deployment runs exist; **publication and independent reproduction of one local
and one hosted pilot remain outstanding**.

### Phase 8 Delivery Snapshot

| Milestone | Status | Remaining boundary |
|---|---|---|
| Runtime, canonical artifacts, progress/resume, and contract governance | **Done** | Continue compatibility maintenance |
| Automated Engineering Evaluation and linked report bundle | **Done** | Continue usability and performance hardening |
| ECM, grounding diagnostics, fit guidance, and compatible comparison | **Implemented** | Ratify AIES-ECM-01 and validate task mappings empirically |
| RT2 — Moderate distinct-instrument breadth and human design review | **Done** | Empirical panel calibration, protected hold-outs, and RT1/RT3/RT4 growth remain |
| Repository conformance/practice audit | **Implemented** | Deeper architecture, code-quality, correctness, and controlled task evidence remain |
| Subject-neutral architecture | **Accepted architecture; experimental contracts** | Accepted ADR-0015 governs the Subject Descriptor, typed evidence event, adapter/loss contracts, and generated support registry; additional subject profiles/executors remain planned and cannot be claimed as implemented |
| First-use adoption commands | **Implemented on Windows** | `aies demo`, `init`, `support`, `evaluate --plan-only`, `snapshot`, `open`, and redacted sharing pass source verification; installed-wheel Windows verification covers the core demo while macOS/Linux clean-install CI results remain |
| Adoption and promotion launch kit | **In progress** | Conversion README/Quickstart, persona/message/channel plan, CLI calls to action, claim-review gate, visual proof assets, and user studies remain before broad launch |
| Open repository licensing | **In progress** | Complete ADR-0014 governance and install final license artifacts |
| Independent local/hosted pilots and public adoption | **Open** | Publish reproducible evidence and independent findings |

The single authoritative implementation and cleanup backlog is
[AIES-DOC-14 — AIES Vision Execution Backlog](docs/OSS_MATURITY_TODO.md).
Detailed work-item status is maintained there rather than duplicated in this
milestone roadmap.

## Phase 9 — v1.0 Public Release

**Status: ⏳ Planned**

Deliverables:

- All five modules and Shared Standards at Approved status
- Public comment period completed and dispositions published for every comment
- License finalized (see [README — License](README.md#license)); stable citation scheme; versioned publication of the standard

Entry criteria: Phases 2–6 exited; public comment (v0.5) closed with all substantiated objections resolved per [GOVERNANCE §4](GOVERNANCE.md#4-consensus-process). Exit criteria: v1.0 tagged; errata process live; maintenance cadence announced.

---

## Version Milestones

| Milestone | Contents | Gate to Next |
|-----------|----------|--------------|
| **v0.3.x** | Foundation complete (Phase 1); all five modules drafting (Phases 2–6); iterative patch releases as drafts land | All module documents content-complete at Draft |
| **v0.4** | Internal review cycle: structured peer review of every document, terminology and cross-reference audit, status promotions Draft → Review | All normative documents at Review; open findings resolved |
| **v0.5** | Public comment release: standard published for open community and industry review with formal comment disposition | Comment period closed; dispositions published; Class 3 changes ratified |
| **v1.0** | Stable standard: all modules Approved, license finalized, citation-stable | — (maintenance releases follow semver per [GOVERNANCE §6](GOVERNANCE.md#6-releases)) |

Milestones are sequential quality gates, not dates. Progress between them is visible through the [CHANGELOG](CHANGELOG.md) and document status metadata.

## Related Documents

- [AIES-DOC-01 — Project Charter](docs/PROJECT_CHARTER.md) — the scope and success criteria this roadmap delivers
- [AIES-DOC-02 — Vision](docs/VISION.md) — the end state the phases build toward
- [AIES-GOV-01 — Governance](GOVERNANCE.md) — the release and consensus process that gates each milestone
- [CHANGELOG.md](CHANGELOG.md) — what has shipped so far

## References

None.

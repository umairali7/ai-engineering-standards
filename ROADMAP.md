# Roadmap

| | |
|---|---|
| **Document ID** | AIES-GOV-04 |
| **Status** | Review |
| **Audience** | All readers |

The phased delivery plan for the AI Engineering Standards. Phases follow the project's engineering philosophy — *knowledge first, qualification next, operations last* — so modules are sequenced AEBOK → AESQS → AEOS → AEAR → AECT, with foundations before all and implementations after.

> **All dates are milestone-relative, not calendar commitments.** A phase ships when its exit criteria are met, not when a date arrives. Status is updated at each release.

---

## Phase Overview

| # | Phase | Status |
|---|-------|--------|
| 1 | Repository Foundation | ✅ Complete (v0.3.1) |
| 2 | AEBOK — Body of Knowledge | 🔍 In Review (v0.4.0) |
| 3 | AESQS — Qualification Standard | 🔍 In Review (v0.4.0) |
| 4 | AEOS — Operating System | 🔍 In Review (v0.4.0) |
| 5 | AEAR — Architecture Reference | 🔍 In Review (v0.4.0) |
| 6 | AECT — Certification & Training | 🔍 In Review (v0.4.0) |
| 7 | Reference Implementations | ⏳ Planned (consumes Phase 8 platform) |
| 8 | Engineering Assessment Platform | 🚧 In progress (pulled forward — ADR-0009) |
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

**Status: 🔍 In Review (v0.4.0) — content-complete, adversarially reviewed, promoted Draft → Review**

Deliverables:

- Knowledge Area structure mapped to SDLC phases P01–P16 and cross-cutting domains X01–X15
- One Knowledge Area document per area (`AIES-AEBOK-KA-nn`) with practices, patterns, and anti-patterns
- AI-native SDLC guidance per phase, aligned with [docs/SDLC.md](docs/SDLC.md)
- Curated references into [research/](research/README.md)

Entry criteria: Phase 1 exit; Taxonomy stable enough that KA structure won't churn. Exit criteria: all KA documents content-complete at Draft, terminology audit clean against the Glossary, at least two Knowledge Areas taken through peer review to validate the review process.

## Phase 3 — AESQS (Qualification Standard)

**Status: 🔍 In Review (v0.4.0) — content-complete, adversarially reviewed, promoted Draft → Review**

Deliverables:

- Competency framework (`AIES-AESQS-CF-nn`) on the CL1–CL4 scale, mapped to AEBOK Knowledge Areas
- Capability scoring method along evaluation dimensions EV1–EV6, with rubrics per role and phase
- Qualification lifecycle specification: scoping, evidence requirements, expiry, revocation
- Assessment templates in [templates/](templates/README.md)

Entry criteria: AEBOK KA structure frozen (competencies must map to knowledge). Exit criteria: rubrics exist for every ROLE-nn, a complete worked qualification example exists in [examples/](examples/README.md), scoring method dry-run performed on at least one real or synthetic case.

## Phase 4 — AEOS (Operating System)

**Status: 🔍 In Review (v0.4.0) — content-complete, adversarially reviewed, promoted Draft → Review**

Deliverables:

- Role specifications (`AIES-AEOS-ROLE-nn`) for ROLE-01…ROLE-14, including human-mandatory roles
- Workflow definitions binding autonomy levels AL0–AL4 to risk tiers RT1–RT4 with approval gates
- Human oversight model: gate placement, sampling, escalation runbooks
- Governance and audit-trail requirements (`AIES-AEOS-GOV-nn`) covering artifacts ART-14/ART-15

Entry criteria: AESQS scoring method drafted (autonomy increases must be qualification-driven). Exit criteria: every workflow names its gates, evidence, and escalation paths; no normative statement conflicts with Shared Taxonomy defaults; one end-to-end operating-model example documented.

## Phase 5 — AEAR (Architecture Reference)

**Status: 🔍 In Review (v0.4.0) — content-complete, adversarially reviewed, promoted Draft → Review**

Deliverables:

- Core reference architecture for enterprise AI-native engineering platforms (vendor-neutral component model)
- Capability-to-component mapping traceable to AEOS workflows and AEBOK practices
- Industry blueprints (`AIES-AEAR-BP-*`) — banking first, additional regulated industries as contributed
- Architecture diagrams as text-based sources in [diagrams/](diagrams/README.md)

Entry criteria: AEOS workflows drafted (architecture must support the operating model). Exit criteria: core reference architecture reviewed by at least two independent Reviewers with architecture background; every component justified by a requirement or workflow; at least one blueprint complete.

## Phase 6 — AECT (Certification & Training)

**Status: 🔍 In Review (v0.4.0) — content-complete, adversarially reviewed, promoted Draft → Review**

Deliverables:

- Certification tracks (`AIES-AECT-CERT-nn`) aligned to competency levels CL1–CL4
- Learning paths mapping AEBOK Knowledge Areas to each track
- Lab and exercise specifications; examination blueprint (format, coverage, pass criteria)
- Credential policy: validity, renewal, revocation, alignment with AESQS qualifications

Entry criteria: AEBOK and AESQS content-complete (curriculum derives from both). Exit criteria: every track traces to competencies and knowledge areas; exam blueprint reviewed for assessability; sample lab exercised end-to-end.

## Phase 7 — Reference Implementations

**Status: ⏳ Planned — reframed to consume the Engineering Assessment Platform (Phase 8)**

Phase 7 no longer builds evaluation tooling of its own: it produces reference *artifacts* by running the Phase 8 platform, plus reference implementations of the surrounding operating model.

Deliverables:

- Worked qualification runs executed with the `aies` platform ([PLATFORM.md (AIES-DOC-06)](docs/PLATFORM.md)) published as reference artifacts in [examples/](examples/README.md) — evidence packages, reports, and Qualification Records for representative role scopes
- Executable, vendor-neutral reference implementations of key AEOS workflows and AEAR components, built against the platform's runtime-adapter boundary (no vendor lock-in)
- Conformance checklists linking implementation behavior to requirement IDs

Entry criteria: platform milestone M1 shipped ([PLATFORM.md §10](docs/PLATFORM.md)); relevant AEOS/AEAR documents at Review status or later. Exit criteria: at least one complete worked qualification run published and reproducible by a third party; implementations demonstrate the normative requirements they claim; each carries its own security policy and CI.

## Phase 8 — Engineering Assessment Platform

**Status: 🚧 In progress — M1–M4 landed; independent pilot outstanding (per [ADR-0009](adr/ADR-0009-Engineering-Assessment-Platform-Identity.md))**

The `aies` command-line platform: an executable reference implementation of AESQS that currently runs qualification evidence collection against locally- or remotely-hosted AI deployments and audits repositories. Its canonical evidence architecture is subject-neutral, so future executors can assess agents, MCP servers, RAG systems, pipelines, and platforms without a second identity change. It is specified in [PLATFORM.md (AIES-DOC-06)](docs/PLATFORM.md). Originally gated behind Phase 7, it is pulled forward so that executing the standard hardens AESQS before v1.0; Phase 7 now consumes it.

Deliverables (milestones per [PLATFORM.md §10](docs/PLATFORM.md)):

- ✅ **M1 — Runnable core:** Python package + CLI; `doctor`, `registry`, single-model `qualify`, Markdown/JSON evidence reports
- ✅ **M2 — Scoring depth:** competency framework directories (CA-01…CA-12), weighted scoring with profiles (gates immutable), result history and `compare`; plus the runtime/deployment abstraction (D11)
- ✅ **M3 — Scale & integration:** frozen runtime-adapter contract with out-of-tree example, HTML reports (PDF via print), parallel execution, result index
- ✅ **M4 — Review & workflow:** multi-model peer review with the calibration gate, human grant workflow and Qualification Records, status model with the environment-change re-qualification trigger, dashboard, CI

Entry criteria: AESQS at Review status (execution feedback is part of hardening it toward Approved); [ADR-0002](adr/ADR-0002-Qualification-Platform.md) accepted. Exit criteria: platform can execute a full qualification cycle — evidence through human-recorded grant — for at least one role scope ✅; results reproducible on an identical environment fingerprint ✅; conformance tests map enforced behavior to AESQS requirement IDs ✅ (40 tests); **independent pilot on a real hosted/local model — outstanding** (requires a maintainer to run `aies` against an actual deployment).

### Phase 8 Hardening Backlog — Path to 10/10

| Status | Priority | Work item | Why it matters |
|--------|----------|-----------|----------------|
| Open | P0 | Finalize repository license and split code/docs licensing if needed | OSS reuse is blocked while all rights are reserved |
| Done | P0 | **v1.0 Architecture Freeze + contract governance** ([STABILITY.md](STABILITY.md), [COMPATIBILITY.md](COMPATIBILITY.md), [CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md)) | Freezes the contracts others build against, each pinned to a version; declares normative-vs-reference and reference-implementation-vs-conformance-suite; additive-only evolution with ADR-for-breaking, enforced by golden-shape CI tests; the "can this be expressed with existing contracts?" discipline is now in the ADR template |
| Done | P1 | **Versioned artifacts + `make demo`** | Profiles versioned (captured at run time); Evidence Package (`evidence_schema`) and Canonical Result (`result_schema`) envelopes versioned; engine vs decision-semantics version split; full offline end-to-end demo, CI-gated (`tests/test_demo.py`); mock adapter is judge-aware |
| Done | P1 | **Golden Evidence Package corpus + conformance runner** ([conformance/](conformance/README.md), [CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md)) | The data-first arbiter: 8 immutable evidence packages + expected outcomes covering every outcome/reason/invariant; `aies conform engine` verifies any decision engine (incl. third-party via a `decide_fn`) against AESQS decision semantics; CI-gated. Decision semantics now normative in [AESQS CS-01 §8](AESQS/capability-scoring.md) (R18–R21) |
| Done | P2 | **Thin read-only REST API** (`aies serve`) | Serves the canonical artifacts (deployments, runs, evidence, results, conformance) as JSON over stdlib http.server — a consumer, not a decider (no outcome computation; POST refused). Dashboard/UI flows remain future |
| Open | P2 | Dashboard + UI flows over the canonical result | Consume the same Canonical Assessment Result as every other interface, never bypassing the engine (the "no consumer computes outcomes" invariant is recorded) |
| Open | P0 | Remove generated artifacts from release archives and add a release hygiene check | Public source packages must not include `.env`, cache, workspace, or build artifacts |
| Open | P0 | Publish an independent pilot on one local and one hosted deployment | Proves the platform works outside synthetic/mock paths |
| Done | P1 | Add `aies suites validate` and run it in CI | Prevents scenario schema, ID, rubric, and risk-tier drift |
| In progress | P1 | `aies audit <repo>` — executable repository conformance assessment ([ADR-0004](adr/ADR-0004-Repository-Conformance-Audit.md)) | Extends AIES from scoring a *model* to scoring the *engineering practice* around it: maturity per competency area, three-state evidence (verified/asserted/gap), CI gate. Design accepted; implementation phased (strong areas first) |
| In progress | P1 | Assessment-as-Code — declarative competency composition ([ADR-0005](adr/ADR-0005-Assessment-as-Code.md)) | Shipped: `assessments/*.yaml` (enterprise/coder/security/architecture) + strict validator; `qualify --assessment` composes + scores + decides; a frozen Decision Engine emits PASS/FAIL/INCONCLUSIVE/INSUFFICIENT-EVIDENCE (gate-first, no blended score) with structured reasons over a Canonical Assessment Result; `aies assessment list/show/validate/result` (Markdown/JSON/HTML views); shipped assessments gated by `aies suites validate` in CI. Remaining: SARIF renderer, assessment composition/inheritance (`extends`) |
| In progress | P1 | Grow each CA suite to decisional-ready public and held-out sets | ~16 public scenarios per CA (189 total), RT2 distinct ~10/area plus more RT3/RT4 refuse-escalate cases; reaching full decisional-distinct sizes (30/50/100) and held-out sets remains |
| Done | P1 | Add connector/tool/memory attack scenarios to CA-07 and governance response scenarios to CA-12 | `SC-CA07-011`, `SC-CA11-011`, and `SC-CA12-011` cover this initial tranche |
| Open | P2 | Add bridges/exporters for Inspect AI or comparable eval traces | Lets AIES complement the eval ecosystem instead of duplicating it |
| In progress | P2 | Record model signature and AI-BOM in the deployment manifest (OpenSSF Model Signing; CycloneDX/SPDX) | Aligns deployment provenance (D7) with AI supply-chain standards ([CROSSWALK §3b](docs/CROSSWALK.md)). Declaration + evidence pass-through done; cryptographic verification (Sigstore/OMS) remains |
| Open | P2 | Add resumable failed-run repair for partial inference failures | Makes long real-model evaluations easier to operate |
| Open | P2 | Improve reports with sample-readiness, gate-failure, and grant-readiness explanations | Helps adopters interpret evidence correctly |
| Open | P3 | Publish a contributor guide for writing high-quality scenarios | Makes suite growth community-friendly |

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

- [Project Charter (AIES-DOC-01)](docs/PROJECT_CHARTER.md) — the scope and success criteria this roadmap delivers
- [Vision (AIES-DOC-02)](docs/VISION.md) — the end state the phases build toward
- [GOVERNANCE.md (AIES-GOV-01)](GOVERNANCE.md) — the release and consensus process that gates each milestone
- [CHANGELOG.md](CHANGELOG.md) — what has shipped so far

## References

None.

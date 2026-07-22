# ADR-0002: Qualification Platform — an Executable Reference Implementation of AESQS

| | |
|---|---|
| **ADR** | ADR-0002 |
| **Status** | Superseded |
| **Deciders** | Project Maintainers; Module Editor, AESQS; Module Editor, Platform (newly designated) |
| **Supersedes / Superseded by** | Superseded by [ADR-0009](ADR-0009-Engineering-Assessment-Platform-Identity.md) |

## Context

All five AIES modules and the Shared Standards reached Review status at v0.4.0. The AESQS module (AIES-AESQS-00 and its six sub-documents) now defines a complete, internally consistent qualification methodology for AI systems: evidence requirements, EV1–EV6 rubrics with 0–4 anchors, risk-tier weighting with minimum gates, statistical minimums, peer review, and revision/revocation. It is, however, a paper standard: an organization that wants to qualify an AI model against AESQS today must build all tooling from scratch.

Meanwhile, the environment the standard addresses is moving fast. New models — open-weight and hosted — appear weekly, in many quantizations and runtimes, and organizations have no repeatable, local, evidence-grade method for deciding what a given model on given hardware can safely be trusted to do. The [ROADMAP (AIES-GOV-04)](../ROADMAP.md) already anticipated this with Phase 8 (Qualification Platform), gated behind Phase 7. The question forced now is whether to keep the platform as a distant phase, spin it out as an unaffiliated tool, or pull it forward as an in-repo reference implementation.

Doing nothing is not acceptable: a qualification standard whose evaluations are impractical to run will be bypassed in practice, and the standard itself loses the hardening feedback that only execution provides.

## Decision Drivers

- **Executability of AESQS** — the standard's value multiplies if its qualification cycle can actually be run against a model, end to end, by a third party.
- **Repeatability** — the same model, environment, and test suite must yield reproducible, comparable results (AIES-AESQS-QP-01-R10).
- **Evidence-grade output** — results must satisfy AESQS provenance, sampling, and audit-trail requirements (ART-15) rather than produce leaderboard numbers.
- **Vendor neutrality** — normative AIES text stays vendor-neutral; vendor- and runtime-specific code must be isolable (plugin boundary).
- **Offline / local-first operation** — organizations must be able to qualify locally hosted models on their own hardware without sending data to third parties.
- **Standard/tool coherence** — the tool must not drift from the standard it claims to implement.

## Options Considered

### Option A — Documentation only (status quo)

Keep AIES a pure documentation standard; leave execution tooling to adopters and third parties.

- **Pros:** Zero code-maintenance burden; no CI or security surface beyond Markdown; no risk of an in-repo tool contradicting the normative text; keeps contributor skill requirements low.
- **Cons:** AESQS remains untestable in practice — every adopter re-implements evaluation tooling, divergently and partially; the standard receives no execution feedback, so defects in rubrics, gates, and statistics stay latent; third-party tools will claim AESQS conformance without any reference to check against; Phase 8 ambitions stall indefinitely.

### Option B — Separate, unaffiliated tool repository

Build the platform as an independent project in its own repository, referencing AIES but governed and versioned separately.

- **Pros:** Clean separation of concerns — the docs repo stays docs-only; the tool can iterate at code speed without touching standard governance; independent release cadence and issue tracker.
- **Cons:** Drift is structural, not just a risk: the tool and the standard version independently with no shared review gate, so "implements AIES-AESQS-CS-01" becomes an unverifiable marketing claim; cross-repo changes (a rubric fix plus its engine fix) cannot land atomically; the standard loses the direct hardening loop; duplicate governance overhead from day one, before the tool has proven itself.

### Option C — In-repo reference implementation under `platform/` (chosen)

Build the platform inside this repository, under `platform/`, as a Python package (`aies`) that is the Phase 7/8 reference implementation of AESQS, with a designated Module Editor and its own conformance tests keyed to requirement IDs.

- **Pros:** The standard and its execution engine evolve under one governance process and one review gate — a change to AIES-AESQS-CS-01 and the scoring engine lands in one pull request; conformance tests derived from requirement IDs make "implements the standard" checkable; execution feedback hardens AESQS before v1.0; adopters get a runnable starting point that embodies the normative text, not an interpretation of it.
- **Cons:** Introduces code, tests, packaging, and CI into a documentation repository — a real maintenance burden and a new contributor skill profile; a security surface (dependency and supply-chain management) the repo did not previously have; risk that the tool's convenience features accrete semantics the standard never defined. Mitigations are recorded under Consequences.

## Decision

We adopt **Option C**. The AIES project will build the **Model Qualification Platform**: an `aies` command-line tool (in the spirit of terraform, kubectl, and pytest) that executes the AESQS qualification methodology against locally- or remotely-hosted AI models, living in this repository under `platform/` as a Python package.

This pulls ROADMAP Phase 8 forward and reframes Phase 7 to consume the platform. The platform is specified in [PLATFORM.md (AIES-DOC-06)](../docs/PLATFORM.md), whose §11 records the binding design decisions that keep the implementation faithful to the standard — including: the CLI verb is `qualify` and the artifact is a Qualification Record (AECT certifies humans; AESQS qualifies AI systems, per AIES-AECT-00-R03 — there is no `certify` command); scoring is on EV1–EV6 with 0–4 anchors, never an ad-hoc scale; minimum gates and statistical minimums are enforced in code; output is scoped RT×AL grants, never a global "production ready" verdict; the environment fingerprint is provenance and a re-qualification trigger; and vendor-specific code is confined to runtime plugins.

The platform MAY be split into a companion repository at v1.0, once conformance-testing practice is established; that split, if made, requires a superseding ADR.

## Consequences

**Positive:**

- AESQS becomes testable: every normative clause the engine implements is exercised on every run, surfacing rubric, gate, and statistics defects while the standard is still at Review — direct hardening pressure before v1.0.
- Organizations gain a repeatable, local-first, evidence-grade way to qualify models on their own hardware, producing registry-ready Qualification Records with full provenance (ART-15).
- The plugin boundary gives vendor neutrality an enforcement mechanism instead of a policy statement.
- Phase 7 reference implementations get a concrete substrate: worked qualification runs become reference artifacts.

**Negative:**

- Code maintenance burden in a documentation repository — mitigation: the platform is an isolated package under `platform/` with its own designated Module Editor, test suite, and dependency policy; documentation-only contributions remain unaffected.
- CI complexity (packaging, tests, linting, supply-chain scanning alongside link-checking) — mitigation: platform CI jobs are scoped to `platform/` paths and cannot block documentation-only changes.
- Risk of the tool drifting from the standard — the tool becoming the de facto standard, or accreting semantics AESQS never defined — mitigation: a conformance test suite derived from requirement IDs (each enforced clause maps to at least one test named for its requirement ID), PLATFORM.md §11 as the anti-drift contract, and the rule that any behavior not traceable to a normative clause is labeled non-normative in output.

## Compliance & Verification

- The platform's conformance test suite MUST map each implemented normative clause to at least one test identified by the requirement ID it verifies (e.g., a gate-enforcement test named for AIES-AESQS-CS-01-R04); the release checklist verifies the map is current.
- Review checklist: changes under `platform/` that alter scoring, gating, sampling, or record semantics require sign-off from the AESQS Module Editor in addition to the Platform Module Editor.
- The design decisions of [PLATFORM.md (AIES-DOC-06) §11](../docs/PLATFORM.md) are checked at every platform release; a deviation requires either a fix or a superseding ADR.
- Normative anchors implemented by the engine: AIES-AESQS-00-R01…R04, AIES-AESQS-QP-01-R09/R10, AIES-AESQS-ER-01 §1–§2, AIES-AESQS-CS-01 §2–§6, AIES-AESQS-PR-01 (orchestration support only — human review is not automated), AIES-AESQS-RR-01 §2 (environment/model change triggers).

## Links

- Pull request: (this ADR's introducing pull request)
- Related: [Qualification Platform Specification (AIES-DOC-06)](../docs/PLATFORM.md)
- Related: [Roadmap (AIES-GOV-04)](../ROADMAP.md) — Phases 7–8
- Related: [AESQS Module Overview (AIES-AESQS-00)](../AESQS/README.md) and sub-documents AIES-AESQS-QP-01, AIES-AESQS-ER-01, AIES-AESQS-CS-01, AIES-AESQS-PR-01, AIES-AESQS-RR-01
- Related: [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md)
- Related: [ADR-0001 — Repository Foundation](ADR-0001-Repository-Foundation.md)

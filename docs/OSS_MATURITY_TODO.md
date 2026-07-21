# OSS Maturity Todo List

| | |
|---|---|
| **Document ID** | AIES-DOC-10 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This backlog tracks the concrete work needed to move AIES from a strong draft
foundation to a genuinely reusable public OSS standard and platform.

## 1. Target Ratings

| Area | Current assessment | 10/10 target |
|------|--------------------|--------------|
| Draft standard | Strong but pre-ratification | Approved v1.0 with public comment disposition and stable citations |
| OSS readiness | Useful but license-blocked | Clear license, clean releases, contributor path, public pilots |
| Evaluation platform | Runnable, extensible reference implementation — model qualification, repository conformance audit (`aies audit`), and supply-chain verification | Validated, extensible, pilot-proven qualification + audit engine |

## 2. Priority Backlog

| Status | Priority | Todo | Acceptance signal |
|--------|----------|------|-------------------|
| Open | P0 | Finalize license | `LICENSE.md` grants reuse; platform package metadata matches |
| Done | P0 | Clean release artifacts | `make release-hygiene` and CI reject tracked `.env`, `.DS_Store`, `__pycache__`, `.pytest_cache`, egg-info, bytecode, or `aies-workspace`; the tracked release tree passes |
| Open | P0 | Publish independent pilot | Two full real-model runs, one hosted and one local, with reports and lessons learned |
| Done | P1 | Add suite validator | `aies suites validate` checks schemas, IDs, dimensions, risk tiers, repeats, and suite counts; CI runs it |
| In progress | P1 | Grow scenario suites | Current: 212 scenarios across 12 areas, with RT2 distinct coverage around 10/area and high-tier behavioral diversity met; target: full decisional-distinct sizes (30/50/100) plus held-out sets |
| Open | P1 | Empirically calibrate the real-model panel | Score independently rated real-model runs, run `aies suites empirical`, publish the pre-registered panel/study, and have a human record any scenario promotion; design-time calibration alone remains insufficient |
| Done | P1 | Widen high-tier behavioral diversity | Added distinct RT3/RT4 decision kinds in CA-02, CA-03, CA-04, CA-05, CA-06, CA-08, and CA-10; `aies corpus health` now meets its diversity target without repeated refusal/escalation padding |
| Done | P1 | Fill justified RT4 coverage gaps | Added genuinely RT4-appropriate scenarios for CA-08 regulated release authorization, CA-10 critical override governance, and CA-11 legal-hold context isolation |
| In progress | P1 | Separate deliberate partial rubrics from coverage defects | ADR-0007 is accepted and `rubric_applicability` is schema-validated and separately reported. Human-review each of the 124 legacy omissions as add-rubric / declare-with-rationale / revise; unexpected omissions remain warnings until the reviewed migration is complete |
| Open | P1 | Make RT2 runs diversity-ready | Shipped RT2 assessments select at least 30 scored items from a wider distinct-scenario set, with public versus held-out/twin handling explicit; repeats measure stability but do not substitute for task diversity |
| Done | P1 | Add scenario authoring guide | [SCENARIOS.md (AIES-PLAT-07)](../platform/SCENARIOS.md) — schema, quality bar, risk-tier and rubric guidance, validation |
| Done | P1 | Add ecosystem bridge | `aies import` ingests external EV1–EV6 eval results (Inspect/DeepEval/other) as automated ratings; `aies export` writes a generic eval-log JSON that round-trips through import |
| Done | P1 | Executable repository conformance audit | `aies audit <repo>` — maturity per competency area, three-state evidence (verified/asserted/gap), `--gate --rt N` for CI ([ADR-0004](../adr/ADR-0004-Repository-Conformance-Audit.md)) |
| Done | P1 | Supply-chain provenance | Deployment manifests may declare `provenance.signature` / `ai_bom`; `aies deployment verify-artifact` recomputes the SHA-256 and verifies a detached signature |
| Done | P1 | External-standards crosswalk refresh (2026) | ISO/IEC 42119/25059/5338/42005, NIST GenAI Profile, OWASP/ATLAS, EU AI Act timeline, agentic autonomy; new AI impact-assessment requirement (AEOS GOV-01-R27) |
| Done | P2 | Harden failed-run recovery | Responses are written as collected (a mid-run failure loses nothing); `aies qualify --resume-collection <run>` fills only the missing responses and rebuilds the scoresheet; a run can also be re-scored via `aies review`/`--resume` without re-collecting |
| Done | P2 | Reliable HTTPS + actionable endpoint errors | TLS verified via `certifi`; timeout/TLS/HTTP errors name the endpoint and next step; fail-fast liveness probe |
| Done | P2 | Improve evidence reports | The report now opens with a **Grant Readiness** summary (per-area verdict + overall ready/blocked) and a **Residual risk** section (judge-produced, non-decisional, thin-margin gates), on top of NON-DECISIONAL readiness, per-area gates, and the `aies capabilities` profile |
| Done | P1 | Define Engineering Capability Matrix (ECM) standard boundary | Accepted ADR-0008 and draft `AIES-ECM-01` establish the subject-neutral engineering artifact, task taxonomy, and separation from Qualification and Deployment Guidance |
| Done | P1 | Deliver an evidence-derived ECM companion artifact | `aies capabilities <run-or-deployment> --ecm` writes task-mapped Markdown/JSON/HTML from canonical records; it retains source scenario-family evidence, labels evidence confidence and `not assessed` gaps, and cannot alter qualification or grant outcomes |
| Done | P1 | Define ECM confidence and evidence-coverage rules | Every task result exposes rating observations, distinct scenarios/responses, rater protocol, mapping version, deterministic evidence confidence, and status; sparse or non-decisional evidence renders “collect more evidence”, not a strength claim |
| Done | P2 | Establish a governed Engineering Task Mapping registry | The versioned, schema-validated `engineering-tasks-v1.yaml` maps every shipped scenario to ET-01 through ET-15 with rationale; validation and tests prevent unmapped or unknown task claims |
| In progress | P2 | Refine task mappings beyond scenario families | Review scenario-level mappings and add genuinely assessed API, performance, testing, security, migration, infrastructure, and production-operation scenarios before claiming those task rows |
| Done | P2 | Add bounded Deployment Guidance | ECM and the embedded report render deterministic Recommended / Use only with human review / Not recommended sections from task evidence and qualification constraints; no guidance can create a grant |
| Open | P2 | Add matched-run ECM comparison and workload-based selection guidance | Comparison only renders task-level deltas when suite/profile/risk tier/repeats/rater protocol are compatible. A later selection view accepts a declared workload mix and operational constraints (for example latency, cost, context window, tool reliability, availability), explains evidence and constraints, and never creates a global “best model” or bypasses risk/autonomy gates |
| In progress | P2 | Publish security contact | GitHub Private Vulnerability Reporting is live; a dedicated security email and encryption key remain to be published |
| Open | P3 | Add governance labels/templates | Issues/PRs route cleanly by module, decision class, and newcomer suitability |
| Done | P3 | Add conformance examples | [examples/conformance/](../platform/examples/conformance/README.md) — adopter and implementation statements checkable with `aies conform` |

## 3. Scenario Suite Status

The platform now ships 212 scenarios across 12 competency areas. The
`SC-CAxx-011`…`016` scenarios are complex, distinct cases (multi-constraint,
adversarial, cross-cutting, and RT3/RT4 refuse-or-escalate) intended to exercise
judgment rather than single-concept recall, and to reduce run repetition by
giving decisional samples more distinct prompts.

These are still demonstration suites. Qualification-grade operation requires
larger, versioned, held-out suites and enough scored samples to meet the
AESQS minimums per risk tier.

Completed scenario tranche:

| Done | Update |
|------|--------|
| yes | Added one complex integration scenario per competency area (`SC-CA01-011` through `SC-CA12-011`) |
| yes | Added agentic tool-security coverage to CA-07 via `SC-CA07-011` |
| yes | Added external-framework governance response coverage to CA-12 via `SC-CA12-011` |
| yes | Added 12 distinct high-tier scenarios for the identified behavioral-diversity and RT4 coverage gaps; the current validated corpus contains 212 scenarios and `aies corpus health` reports no high-tier diversity gaps |
| yes | Added a [scenario authoring guide (AIES-PLAT-07)](../platform/SCENARIOS.md) so contributors can grow suites consistently |

Next implementation item: grow each area to full **decisional-distinct** sizes
(≥ 20/30/50/100 distinct scenarios per RT1–RT4) and add **held-out** suites, so a
decisional run draws distinct prompts without leaning on repeats.

## 4. Implementation Sequence

1. **Measurement integrity:** preserve raw evidence, obtain independently rated
   real-model runs, and complete the empirical-calibration study. Do not use
   preliminary heuristic ratings as qualification or calibration evidence.
2. **Scenario structure:** decide the additive metadata boundary in an ADR,
   then distinguish intentional non-applicable EV dimensions from accidental
   rubric omissions and make the validator signal actionable.
3. **Coverage depth:** expand high-tier behavioral diversity and justified RT4
   coverage; split public, held-out, and twin scenarios so repeats do not create
   a false appearance of independent evidence.
4. **Engineering Capability Matrix:** render existing scenario families from
   canonical evidence first, with explicit confidence and evidence coverage.
   Add the governed task-mapping registry only after its standard boundary and
   review rules are accepted.
5. **Decision products:** add traceable deployment guidance before selection;
   compare only protocol-matched runs, then accept a declared workload and
   operational constraints. Neither view overrides qualification gates,
   statistical minimums, or autonomy limits.

## 5. ECM V2 Product Architecture

The initial family-level renderer has been superseded by the task-mapped ECM
baseline. The target architecture is:

```text
Assessment → Canonical Evidence → Competency Analysis →
Engineering Task Mapping → Engineering Capability Matrix → Decision Products
```

The products are separate by design:

| Layer | Product | Audience | Decision it supports |
|---|---|---|---|
| 1 | Qualification | Governance | Whether evidence supports a scoped human qualification decision |
| 2 | Engineering Capability Matrix | Engineers | Which standardized engineering tasks have demonstrated evidence, performance, and confidence |
| 3 | Deployment Guidance | Operations and management | Use / use with review / avoid, within qualification and autonomy constraints |
| 4 | Comparison and Selection | Engineering leadership | Which compatible deployment best fits a declared workload and operating constraints |

### ECM V2 implementation backlog

| Status | Priority | Todo | Acceptance signal |
|---|---|---|---|
| Done | P1 | Establish `AIES-ECM-01` as a foundational standard | Accepted ADR-0008 and draft `AIES-ECM-01` define the subject-neutral boundary, taxonomy, versioning, confidence semantics, and additive relationship to AESQS |
| Done | P1 | Establish the AIES Engineering Task Taxonomy | Versioned `ET-01` through `ET-15` identifiers cover requirements, architecture, API design, generation, refactoring, debugging, testing, documentation, optimization, security, database, migration, infrastructure, observability, and production operations |
| Done | P1 | Add a governed task-mapping registry | Every shipped scenario maps through the validated `engineering-tasks-v1.yaml` registry to one or more task IDs, with rationale; scenarios remain traceable through canonical evidence |
| Done | P1 | Replace family-only ECM output with task rows | Each task row renders observed performance bars, evidence confidence, distinct scenarios/responses, rating observations, rater provenance, task status, and `not assessed`; raw scenario-family evidence remains available |
| Done | P1 | Restore the complete engineer report | ECM renders task profile bars, observed/demonstrated patterns, improvement and evidence gaps, deployment guidance, and traceability. Qualification reports embed the engineer summary but remain auditor-facing |
| Done | P2 | Deliver Deployment Guidance as its own artifact | `aies guidance <run-or-deployment> --write` renders a standalone, deterministic Use / Use with human review / Avoid evidence view; it cannot create a grant |
| In progress | P2 | Add compatible ECM comparison | `aies compare A B --ecm` renders task rows and refuses a task comparison when risk tier, profile, mapping version, or rater protocol differ; decisional suite/repeat compatibility remains to be tightened before winner claims |
| Open | P3 | Add AIES Select | A declared workload mix and operational constraints (latency, cost, context, tool reliability, availability) produce an explained fit ranking across only compatible evidence; no global best-model claim |
| Open | P3 | Add organization decision products | Approved-subject inventory, task fit, qualification scope, operational constraints, drift/requalification status, and deployment conditions are available to management without exposing a misleading leaderboard |

## Related Documents

- [Roadmap](../ROADMAP.md)
- [Platform](../platform/README.md)
- [Platform Specification](PLATFORM.md)
- [2026 External Framework Refresh](../research/RES-01-2026-external-framework-refresh.md)

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
| Open | P0 | Clean release artifacts | Release/archive contains no `.env`, `.DS_Store`, `__pycache__`, `.pytest_cache`, egg-info, or `aies-workspace` |
| Open | P0 | Publish independent pilot | Two full real-model runs, one hosted and one local, with reports and lessons learned |
| Done | P1 | Add suite validator | `aies suites validate` checks schemas, IDs, dimensions, risk tiers, repeats, and suite counts; CI runs it |
| In progress | P1 | Grow scenario suites | Current: ~16 public scenarios per CA (189 total), RT2 distinct ~10/area plus more RT3/RT4 refuse-escalate cases; target: full decisional-distinct sizes (30/50/100) plus held-out sets |
| Done | P1 | Add scenario authoring guide | [SCENARIOS.md (AIES-PLAT-07)](../platform/SCENARIOS.md) — schema, quality bar, risk-tier and rubric guidance, validation |
| In progress | P1 | Add ecosystem bridge | `aies import` ingests external EV1–EV6 eval results (Inspect/DeepEval/other) as automated ratings; export to eval-log formats remains |
| Done | P1 | Executable repository conformance audit | `aies audit <repo>` — maturity per competency area, three-state evidence (verified/asserted/gap), `--gate --rt N` for CI ([ADR-0004](../adr/ADR-0004-Repository-Conformance-Audit.md)) |
| Done | P1 | Supply-chain provenance | Deployment manifests may declare `provenance.signature` / `ai_bom`; `aies deployment verify-artifact` recomputes the SHA-256 and verifies a detached signature |
| Done | P1 | External-standards crosswalk refresh (2026) | ISO/IEC 42119/25059/5338/42005, NIST GenAI Profile, OWASP/ATLAS, EU AI Act timeline, agentic autonomy; new AI impact-assessment requirement (AEOS GOV-01-R27) |
| In progress | P2 | Harden failed-run recovery | Responses are written as collected (a mid-run failure loses nothing) and a run can be re-scored via `aies review`/`--resume` without re-collecting; resumable partial *collection* (fill only the missing items) remains |
| Done | P2 | Reliable HTTPS + actionable endpoint errors | TLS verified via `certifi`; timeout/TLS/HTTP errors name the endpoint and next step; fail-fast liveness probe |
| In progress | P2 | Improve evidence reports | NON-DECISIONAL sample-readiness, per-area gate results, and the `aies capabilities` per-area profile ship; a dedicated grant-readiness / residual-risk explainer remains |
| In progress | P2 | Publish security contact | GitHub Private Vulnerability Reporting is live; a dedicated security email and encryption key remain to be published |
| Open | P3 | Add governance labels/templates | Issues/PRs route cleanly by module, decision class, and newcomer suitability |
| Done | P3 | Add conformance examples | [examples/conformance/](../platform/examples/conformance/README.md) — adopter and implementation statements checkable with `aies conform` |

## 3. Scenario Suite Status

The platform now ships ~16 scenarios per competency area, 189 total. The
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
| yes | Expanded every area to ~16 scenarios (`SC-CAxx-012`…`016`, +57, 189 total): distinct RT2/RT3/RT4 multi-constraint and refuse-escalate cases, adversarially hardened (rubric discrimination, anti-gaming traps) |
| yes | Added a [scenario authoring guide (AIES-PLAT-07)](../platform/SCENARIOS.md) so contributors can grow suites consistently |

Next implementation item: grow each area to full **decisional-distinct** sizes
(≥ 20/30/50/100 distinct scenarios per RT1–RT4) and add **held-out** suites, so a
decisional run draws distinct prompts without leaning on repeats.

## Related Documents

- [Roadmap](../ROADMAP.md)
- [Platform](../platform/README.md)
- [Platform Specification](PLATFORM.md)
- [2026 External Framework Refresh](../research/RES-01-2026-external-framework-refresh.md)

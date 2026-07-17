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
| Evaluation platform | Runnable reference implementation | Validated, extensible, pilot-proven qualification engine |

## 2. Priority Backlog

| Status | Priority | Todo | Acceptance signal |
|--------|----------|------|-------------------|
| Open | P0 | Finalize license | `LICENSE.md` grants reuse; platform package metadata matches |
| Open | P0 | Clean release artifacts | Release/archive contains no `.env`, `.DS_Store`, `__pycache__`, `.pytest_cache`, egg-info, or `aies-workspace` |
| Open | P0 | Publish independent pilot | Two full real-model runs, one hosted and one local, with reports and lessons learned |
| Done | P1 | Add suite validator | `aies suites validate` checks schemas, IDs, dimensions, risk tiers, repeats, and suite counts; CI runs it |
| In progress | P1 | Grow scenario suites | Current: 11 public scenarios per CA, including complex integration cases; target: public practice plus held-out decisional scenarios |
| Open | P1 | Add scenario authoring guide | Contributors can add a scenario without reverse-engineering YAML patterns |
| Open | P1 | Add ecosystem bridge | Evidence can be imported from or exported to Inspect-style eval logs |
| Open | P2 | Harden failed-run recovery | Partial failed runs can be resumed without manual file surgery |
| Open | P2 | Improve evidence reports | Reports clearly show sample readiness, gate failures, grant readiness, and residual risk |
| Open | P2 | Publish security contact | `SECURITY.md` has a real contact and optional encryption key |
| Open | P3 | Add governance labels/templates | Issues/PRs route cleanly by module, decision class, and newcomer suitability |
| Open | P3 | Add conformance examples | Third-party adopter and implementation conformance statements are demonstrated |

## 3. Scenario Suite Status

The platform now ships 11 scenarios per competency area, 132 total. The new
`SC-CAxx-011` scenarios are complex integration cases intended to exercise
multi-constraint reasoning rather than single-concept recall.

These are still demonstration suites. Qualification-grade operation requires
larger, versioned, held-out suites and enough scored samples to meet the
AESQS minimums per risk tier.

Completed scenario tranche:

| Done | Update |
|------|--------|
| yes | Added one complex integration scenario per competency area (`SC-CA01-011` through `SC-CA12-011`) |
| yes | Added agentic tool-security coverage to CA-07 via `SC-CA07-011` |
| yes | Added external-framework governance response coverage to CA-12 via `SC-CA12-011` |

Next implementation item: add a scenario authoring guide so community
contributors can grow high-quality public and held-out suites consistently.

## Related Documents

- [Roadmap](../ROADMAP.md)
- [Platform](../platform/README.md)
- [Platform Specification](PLATFORM.md)
- [2026 External Framework Refresh](../research/RES-01-2026-external-framework-refresh.md)

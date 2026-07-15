# EX-04 — A Filled Architecture Decision Record

| | |
|---|---|
| **Document ID** | AIES-EX-04 |
| **Status** | Review |
| **Audience** | Architects |

> **This example is informative, not normative.** Nothing in it adds to, relaxes, or reinterprets any AIES requirement; where this example and a standard disagree, the standard wins. **All organizations, people, systems, and events in this example are fictional.** "Fieldstone" is an invented company; "FS-AGENT-ENG-01" is an invented AI agent designation; no real vendor, model, or product is depicted.

---

## 1. What This Example Demonstrates

This example shows a complete, honestly argued Architecture Decision Record (ART-04, [Taxonomy §7](../../Shared/Taxonomy/README.md#7-artifact-types)) as a mid-size engineering organization would actually write one. It applies:

- [templates/ADR_TEMPLATE.md](../../templates/ADR_TEMPLATE.md) — the section structure is followed exactly, with the template's instructional comments removed.
- [adr/README.md (AIES-ADR-00)](../../adr/README.md) — the process context: sequential numbering, the Proposed → Accepted lifecycle, and the rule that an Accepted ADR's Context, Decision Drivers, Options Considered, and Decision sections become immutable.
- [AEAR Core Reference Architecture (AIES-AEAR-CORE-01) §6 — Model Plane](../../AEAR/core-reference-architecture.md#6-model-plane) — the subject of the decision. The ADR deliberately stays at the level of *capabilities* (model gateway, provider adapters, usage metering, residency routing) and never names a vendor, per AEAR principle 1 (*vendor neutrality by construction*) and the examples convention in [examples/README.md](../README.md).
- The ADR flow of [AEOS Workflows §4](../../AEOS/workflows.md#4-architecture-change-adr-flow) — draft by ROLE-05, review by ROLE-08 and implementing roles, acceptance gate scaled to impact tier, indexing into context assets by ROLE-12.

**Scenario.** Fieldstone is a fictional ~400-engineer company building a field-service management SaaS platform (work-order scheduling, a technician mobile app, customer billing with card payments, IoT telemetry ingestion). Fieldstone has adopted the AIES ADR template for its internal engineering decisions; its ADR series is numbered `FS-ADR-NNNN` and ratified by its Architecture Review Board, which plays the part that Maintainers play in the AIES repository's own process. The ADR below records the decision that created Fieldstone's model gateway — the choke point through which its engineering agent, FS-AGENT-ENG-01, and all engineering tooling reach model providers.

The filled ADR follows. Everything from the next heading to the end of §2 is Fieldstone's document, reproduced as written.

---

## 2. The ADR as Fieldstone Wrote It

# FS-ADR-0007: Introduce a model gateway for all engineering-agent model access

| | |
|---|---|
| **ADR** | FS-ADR-0007 |
| **Status** | Accepted |
| **Deciders** | M. Okafor (Head of Platform Engineering — ROLE-05 Architect), L. Virtanen (Security Engineering Lead — ROLE-08), T. Brandt (Engineering Productivity Lead — ROLE-06 chapter lead), R. Da Silva (Governance Officer — ROLE-14) |
| **Supersedes / Superseded by** | — |

## Context

Fieldstone's engineering teams currently call external model providers directly from their tooling. As of May 2026 an inventory found 23 distinct integration points: IDE assistant plugins configured per team, CI jobs that call completion APIs for test generation, the FS-AGENT-ENG-01 agent runtime itself, and several internal scripts. Across these, two external providers are in use through four different SDK major versions, authenticated with nine long-lived API keys shared at team level.

Three consequences of this arrangement are now blocking:

1. **No cost attribution.** Monthly model spend (≈ $86k in May 2026) is visible only as per-key invoice totals. We cannot attribute spend to a task, work item, team, or product area, so we cannot budget it, cap it, or answer basic questions ("what did the billing-service refactor cost in inference?").
2. **No audit trail.** Inference requests are not linked to the work items or agent tasks that caused them. When FS-AGENT-ENG-01 produces a change, we cannot record which model and version produced it — so our audit trail records (ART-15) for agent work are incomplete, and the qualification evidence we need to raise the agent's autonomy level cannot be assembled.
3. **Vendor coupling.** Prompts, tool definitions, and retry logic are written directly against one provider's API shapes. Substituting or even A/B-evaluating a second provider is a per-team engineering project rather than a configuration change.

Additionally, Fieldstone's EU utility customers (work-order and telemetry data for German and Dutch grid operators) contractually require that data derived from their systems be processed in EU-resident infrastructure. Today no mechanism routes inference requests carrying such data to EU-approved deployments; compliance rests on teams remembering not to use certain tools on certain repositories.

"Do nothing" is not acceptable: the EU contractual obligation has an audit date in Q4 2026, and the planned autonomy-level increase for FS-AGENT-ENG-01 requires per-request model attribution that the current arrangement cannot produce.

## Decision Drivers

- **Auditability:** every inference request must be attributable to a principal, task, and model version, feeding complete audit trail records (ART-15) — per [AIES-AEAR-CORE-01-R15] and [AIES-AEAR-CORE-01-R36].
- **Cost attribution:** every unit of AI spend attributable to principal, task, and cost center at the time it is incurred, with budgets enforceable at request time — per [AIES-AEAR-CORE-01-R54], [AIES-AEAR-CORE-01-R17] (domain X10).
- **Vendor neutrality / substitutability:** at least two interchangeable providers per critical capability class, with failover that is exercised, not merely configured — per [AIES-AEAR-CORE-01-R14] and AEAR principle 1.
- **Residency routing:** requests carrying EU-customer-derived data must reach only EU-approved deployments — per [AIES-AEAR-CORE-01-R18].
- **Adoption cost and latency:** ~40 teams must migrate; interactive assistance is latency-sensitive ([AIES-AEAR-CORE-01-R56]) and must not degrade noticeably.

## Options Considered

### Option A — Per-team direct integration (status quo)

Each team continues to integrate providers directly in its own tooling, with guidance documents recommending good practice.

- **Pros:** Zero migration cost; teams keep the tool configurations they have tuned; no new runtime component, so no added latency and no new single point of failure; no central team required.
- **Cons:** Fails every driver except adoption cost. Attribution and audit remain impossible to guarantee because they depend on 23 integration points each doing the right thing; shared long-lived keys violate least-authority (AEAR principle 4); residency routing is unenforceable by construction; provider substitution remains an N-team project; and the autonomy-level increase for FS-AGENT-ENG-01 stays blocked for lack of ART-15-grade evidence.

### Option B — Shared client library

Build one internal SDK that all tooling must use; the library normalizes provider APIs, tags requests with task metadata, and emits usage events.

- **Pros:** Substantially cheaper to build than a service (no runtime infrastructure, no on-call); normalizes provider APIs so prompts and tool code decouple from any one vendor; provides attribution and audit metadata *where it is adopted*; adds no network hop, so interactive latency is untouched.
- **Cons:** Enforcement is by convention: nothing technically prevents a team (or a compromised sandbox) from calling a provider directly, which [AIES-AEAR-CORE-01-R13] requires to be *technically prevented*, not discouraged. Version skew across ~40 teams means policy fixes (a residency rule, a budget cap) roll out at the speed of the slowest upgrader. API keys still live in team environments, so the least-authority and secrets-isolation problems remain. Audit events are emitted client-side from environments the platform does not control, so the trail is incomplete exactly when it matters (misbehaving or compromised clients).

### Option C — Central model gateway service (chosen)

Deploy a platform-owned gateway service as the single ingress for all model inference, per the Model Plane of [AIES-AEAR-CORE-01 §6]: policy-driven routing across providers, per-request metering and attribution, budget enforcement, residency-class routing, and provider adapters behind one normalized contract — with direct provider egress blocked at the network boundary so the gateway cannot be bypassed.

- **Pros:** Satisfies all five drivers structurally rather than by convention. Attribution, budgets, and audit records are produced server-side at a single choke point and fail closed ([AIES-AEAR-CORE-01-R17]); residency routing is a routing-table property, not a team habit ([AIES-AEAR-CORE-01-R18]); provider substitution and failover become configuration plus adapter work in one codebase ([AIES-AEAR-CORE-01-R14]); egress control makes direct provider access technically impossible from engineering networks and agent sandboxes ([AIES-AEAR-CORE-01-R13]). Unblocks the FS-AGENT-ENG-01 autonomy-evidence pipeline.
- **Cons:** The gateway is a single point of failure for all AI-assisted engineering; it adds a network hop (~20–40 ms measured in the spike) to every request; it creates a permanent service-ownership load on Platform Engineering (build, operate, on-call, provider-adapter maintenance); and it forces a migration across ~40 teams and 23 integration points.

## Decision

We adopt **Option C**. Fieldstone will build and operate a central model gateway (working name **Relay**) as the single logical ingress for all model inference by engineering tooling and by FS-AGENT-ENG-01, implementing the Model Plane responsibilities of [AIES-AEAR-CORE-01 §6]: routing, failover, versioning, usage metering, budget enforcement, and provider adapters behind one normalized inference contract.

We choose C over B — the only other option that addresses the drivers at all — because three of the four blocking drivers (auditability, budget enforcement, residency routing) are *enforcement* problems, and a library cannot enforce: [AIES-AEAR-CORE-01-R13] requires direct provider access to be technically prevented, and only a choke point combined with egress control achieves that. The library's advantages (lower cost, no added hop) are real but are outweighed by the certainty that convention-based controls decay under deadline pressure.

Concretely:

- Relay fronts **two approved external providers per critical capability class** (capability classes at adoption: *general code generation*, *fast interactive completion*, *embedding*), with an EU-resident deployment approved for the EU-customer data-handling class.
- Requests carry principal identity, work-item/task reference, and data-handling class; Relay records model identifier and version on every request/response pair into the audit pipeline (ART-15).
- Budgets and quotas are enforced at request time and fail closed with escalation ([AIES-AEAR-CORE-01-R17]).
- Direct provider endpoints are blocked by egress policy from engineering networks, CI, and agent sandboxes once migration completes.

## Consequences

**Positive:**

- Every inference becomes attributable to principal, task, cost center, and model version — completing ART-15 records for agent work and unblocking the AESQS qualification evidence needed for FS-AGENT-ENG-01 autonomy decisions.
- Provider substitution and failover become platform configuration; quarterly failover exercises become possible and are scheduled ([AIES-AEAR-CORE-01-R14]).
- EU residency obligations are met by routing policy that can be demonstrated to auditors, replacing per-team discipline.
- Model spend becomes budgetable per team and per product area, with fail-closed caps replacing invoice surprises.
- Model version changes gain a single control point for evaluation-gated rollout ([AIES-AEAR-CORE-01-R16]).

**Negative:**

- The gateway is a single point of failure for all AI-assisted engineering — *mitigation:* active-active deployment across two zones; a defined degraded mode in which agent autonomy reduces and interactive requests queue rather than silently bypassing the gateway, per [AIES-AEAR-CORE-01-R58]/[R59] (degradation moves autonomy downward, never around the control).
- Added latency of ~20–40 ms per request — *mitigation:* latency classes with routing per [AIES-AEAR-CORE-01-R56]; regional gateway instances co-located with engineering infrastructure; an explicit latency budget in the Relay SLO so the hop is engineered, not ignored.
- Permanent ownership load on Platform Engineering — *mitigation:* Relay is staffed as a product (Platform Enablement team, 5 engineers, on-call rotation); this staffing is a condition of acceptance of this ADR, recorded here so it cannot be quietly dropped.
- Migration cost across ~40 teams — *mitigation:* a two-release-train deprecation window with drop-in adapter shims for the four SDK versions in use; the egress block is enabled only after ≥90% of integration points have migrated, then closes the remainder.

## Compliance & Verification

- Egress policy denies direct provider endpoints from engineering networks, CI runners, and agent sandboxes; a weekly automated egress probe in the guardrail-policy repository verifies the block and alerts on any newly reachable provider endpoint (per [AIES-AEAR-CORE-01-R13], [AIES-AEAR-CORE-01-R27]).
- Every audit record for FS-AGENT-ENG-01 work must carry a model identifier and version; the monthly governance report (ROLE-14) samples merged agent changes and fails the report if attribution is missing (per [AIES-AEAR-CORE-01-R15], [AIES-AEAR-CORE-01-R36]).
- Provider failover per capability class is exercised quarterly and recorded in the Relay runbook (ART-11) (per [AIES-AEAR-CORE-01-R14]).
- Budget fail-closed behavior is tested in pre-production on every Relay release: an exhausted-budget request must be denied and escalated, never served unmetered (per [AIES-AEAR-CORE-01-R17]).
- Conformance is tracked against [AIES-AEAR-CORE-01 §16 Capability Checklist](../../AEAR/core-reference-architecture.md#16-capability-checklist) items 7–11 in Fieldstone's quarterly platform self-assessment.

## Links

- Pull request: `fs-platform/architecture#41` (internal; carried this ADR and the Relay charter)
- Related: [Core Reference Architecture (AIES-AEAR-CORE-01) §6 — Model Plane](../../AEAR/core-reference-architecture.md#6-model-plane)
- Related: [Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md) — artifact types ART-15, roles cited in Deciders
- Related: [ADR process (AIES-ADR-00)](../../adr/README.md) and [ADR template](../../templates/ADR_TEMPLATE.md)
- Related: FS-ADR-0003 *Adopt AIES operating model for AI-performed engineering work* (internal; established the autonomy/risk framework this decision serves)

---

*End of Fieldstone's document.*

---

## 3. What Makes This a Good ADR

Annotations keyed to the [template](../../templates/ADR_TEMPLATE.md) sections:

- **Metadata.** Status is one of the three lifecycle values from [adr/README.md §3](../../adr/README.md#3-status-lifecycle); the date is the date of the *status change*, not of drafting; deciders are named humans identified by role (Taxonomy [§5](../../Shared/Taxonomy/README.md#5-ai-engineering-roles)) — an agent never appears as a decider. The `Supersedes / Superseded by` row is present even when it is "—", so a future superseding ADR has a place to link back to.
- **Context.** States facts, quantified where possible (23 integration points, $86k/month, nine shared keys), and explains why "do nothing" fails — without smuggling in the solution. A reader with no conversation history can reconstruct the pressure that forced the decision. No vendor is named; providers appear only by count and capability.
- **Decision Drivers.** Each driver is traceable to a specific requirement ID, which turns the Options section from opinion into evaluation: every pro and con below is an argument about a driver, and the drivers double as the acceptance criteria the Compliance section later verifies.
- **Options Considered.** The rejected options are argued honestly — Option B's pros (cheaper, no latency hop) are real and are conceded, and the status quo's pros are stated rather than strawmanned. The decisive con of Option B is anchored to a requirement ([AIES-AEAR-CORE-01-R13]'s "technically prevented"), not to taste. Rejected options are the most valuable part of an ADR: they are what stops the debate from being re-litigated in eighteen months.
- **Decision.** Active voice ("We adopt Option C"), and the reasoning connects the choice back to the drivers — including *why the runner-up loses*, which is the sentence most ADRs omit.
- **Consequences.** Both directions, and every negative consequence names its mitigation, including one (team staffing) recorded as a condition of acceptance so it survives budget season. Consequences are framed as predictions that a superseding ADR may revisit.
- **Compliance & Verification.** Each check names *what* is checked, *where* it runs (egress probe, governance report, runbook, pre-prod test), and its normative anchor — so "are we still following FS-ADR-0007?" is answerable by mechanism, not memory.
- **Links.** The decision is traceable to the pull request that carried it and to the documents it depends on, with relative links and document IDs.
- **Immutability.** Because the status is Accepted, the Context, Decision Drivers, Options, and Decision sections above are now frozen ([adr/README.md §3](../../adr/README.md#3-status-lifecycle)); if the gateway decision is ever reversed, a new ADR supersedes this one and both link to each other.

## Related Documents

- [Worked Examples index (AIES-EX-00)](../README.md)
- [ADR template](../../templates/ADR_TEMPLATE.md) · [ADR process (AIES-ADR-00)](../../adr/README.md)
- [AEAR Core Reference Architecture (AIES-AEAR-CORE-01)](../../AEAR/core-reference-architecture.md)
- [AEOS Workflows (AIES-AEOS-WF-01) §4 — Architecture Change](../../AEOS/workflows.md#4-architecture-change-adr-flow)
- Companion examples in the Fieldstone series: [EX-01](../EX-01-risk-tiering-backlog/README.md), [EX-02](../EX-02-autonomy-envelope/README.md), [EX-03](../EX-03-scored-pull-request/README.md), [EX-05](../EX-05-oversight-gate-design/README.md)

## References

None.

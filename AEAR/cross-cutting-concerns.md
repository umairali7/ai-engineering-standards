# Cross-Cutting Concerns in Platform Architecture

| | |
|---|---|
| **Document ID** | AIES-AEAR-XC-01 |
| **Status** | Review |
| **Audience** | Architects · Platform teams · Security engineers |

How the cross-cutting domains X01–X15 ([Taxonomy §2](../Shared/Taxonomy/README.md#2-cross-cutting-domains-x01x15)) manifest in the architecture of an Enterprise AI Engineering Platform. This document extends the [Core Reference Architecture (AIES-AEAR-CORE-01)](core-reference-architecture.md); plane names and requirement references below refer to that document.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Overview

Cross-cutting domains do not get their own plane; they get **architectural expression inside every plane**. This document covers the domains with the strongest platform-architecture consequences:

| § | Domain(s) | Architectural theme |
|---|-----------|---------------------|
| 2 | X01 Security, X06 AI Safety | Security zones, agent identity, containment |
| 3 | X02 Privacy | Data residency and classification for context data |
| 4 | X03 Compliance, X04 Governance | Compliance evidence generation |
| 5 | X10 Cost Optimization | Budgets, quotas, token accounting |
| 6 | X13 Reliability | Failover and autonomy degradation patterns |
| 7 | X11 Performance, X12 Scalability | Latency classes and scaling surfaces |
| 8 | X05, X07, X08, X09, X14, X15 | Remaining domains, briefly |

## 2. Security Zones and Agent Identity (X01, X06)

### 2.1 Zone Model

The platform is partitioned into security zones with default-deny boundaries between them. The zone model exists because an agent is simultaneously a **trusted insider** (it holds entitlements) and an **untrusted input processor** (its behavior is influenced by whatever text reaches it — the prompt-injection problem). Architecture must hold even when the agent's reasoning is compromised.

```
┌─ ZONE H: Human Access Zone ─────────────────────────────────────────┐
│  Interaction Plane surfaces. Enterprise SSO, device posture.        │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ authenticated sessions only
┌─ ZONE C: Control Zone ────▼─────────────────────────────────────────┐
│  Orchestration · Guardrail policy engine · Governance services.     │
│  No agent-generated code executes here.                             │
└──────────┬──────────────────────────────┬───────────────────────────┘
           │ brokered, scoped             │ brokered, scoped
┌─ ZONE X: Execution Zone ──┐   ┌─ ZONE K: Knowledge Zone ────────────┐
│  Sandboxes, ephemeral     │   │  Knowledge stores, retrieval,       │
│  code environments.       │   │  context assembly.                  │
│  Assumed compromisable.   │   │  Read-optimized, write-governed.    │
└──────────┬────────────────┘   └───────────────┬─────────────────────┘
           │ egress gateway only                │ classified ingestion only
┌─ ZONE E: Egress Zone ─────▼───────────────────▼─────────────────────┐
│  Model gateway (external providers) · toolchain connectors ·        │
│  allowlisted destinations. Everything leaving is inspected.         │
└─────────────────────────────────────────────────────────────────────┘
```

Normative rules:

- [AIES-AEAR-XC-01-R01] The Execution Zone MUST be treated as compromisable: nothing in it may hold long-lived credentials, reach the Control Zone's administrative interfaces, or egress except through the Egress Zone.
- [AIES-AEAR-XC-01-R02] Content that originated outside the platform trust boundary (retrieved documents, web content, third-party code) MUST be tagged as untrusted through context assembly, and guardrail policy MUST be able to condition action decisions on the presence of untrusted content in an agent's context.
- [AIES-AEAR-XC-01-R03] Zone boundaries MUST be enforced by network and platform controls, not by agent instructions.

### 2.2 Agent Identity Architecture

Agent identity (introduced in AIES-AEAR-CORE-01 §11) has a three-level structure:

```
Agent Definition (ART-14)          ── what kind of agent (versioned, approved)
   └── Agent Instance identity     ── this running agent (unique, per instantiation)
         └── Task-scoped grant     ── what it may do right now (expires with task)
```

- [AIES-AEAR-XC-01-R04] Credentials MUST attach to the task-scoped grant, not to the definition or instance, so that compromise of a running agent yields only that task's authority for that task's duration.
- [AIES-AEAR-XC-01-R05] Every agent identity MUST resolve to an accountable human owner and to the ART-14 version in force; ownerless agents MUST NOT run.
- [AIES-AEAR-XC-01-R06] Agent identity events (issuance, grant, expiry, revocation) MUST be recorded as ART-15 audit records.

AI safety (X06) inherits this machinery: containment (zones), bounded authority (task-scoped grants), and preserved human control (autonomy degradation, §6) are the platform's safety case.

## 3. Privacy and Data Residency for Context Data (X02)

Context is where privacy risk concentrates: the Context & Knowledge Plane aggregates organizational data precisely so it can be sent to models.

### 3.1 Classification-Driven Data Flow

- [AIES-AEAR-XC-01-R07] Every knowledge item MUST carry a data classification at ingestion (per AIES-AEAR-CORE-01-R20), including whether it contains personal data and which jurisdiction(s) govern it.
- [AIES-AEAR-XC-01-R08] Classification MUST propagate through retrieval and context assembly, and the model gateway MUST route (or refuse) requests based on the highest classification present in the assembled context (AIES-AEAR-CORE-01-R18).
- [AIES-AEAR-XC-01-R09] Personal data SHOULD be minimized, pseudonymized, or masked during context assembly unless the task demonstrably requires it; the decision MUST be policy-driven, not agent-discretionary.

### 3.2 Residency Architecture

For multi-jurisdiction estates, the platform supports **residency domains**: deployments of the Context & Knowledge Plane and model serving whose data does not leave a jurisdiction.

```
Residency domain A (jurisdiction A)         Residency domain B (jurisdiction B)
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│ Knowledge stores (A data)       │         │ Knowledge stores (B data)       │
│ Context assembly                │         │ Context assembly                │
│ In-domain model serving         │         │ In-domain model serving         │
└──────────────┬──────────────────┘         └──────────────┬──────────────────┘
               └───────────── shared control & governance ─┘
                     (policy, identity, audit metadata — not payload data)
```

- [AIES-AEAR-XC-01-R10] Where residency obligations apply, context payloads MUST be assembled, served to models, and retained within the residency domain; only governance metadata (identifiers, classifications, audit references) MAY cross domains.
- [AIES-AEAR-XC-01-R11] Observability captures of prompts/context (AIES-AEAR-CORE-01-R22, R36) are themselves personal-data stores where they contain personal data, and MUST inherit retention, access, and residency policy accordingly.
- [AIES-AEAR-XC-01-R12] The platform MUST support erasure obligations: given a data-subject reference, locate and remediate affected knowledge items, derived indexes (including vector representations), and retained context captures.

## 4. Compliance Evidence Generation (X03)

The platform's compliance posture is strongest when evidence is a **by-product of operation**, not a periodic assembly exercise. Governance (X04) has its architectural home in the Governance Plane (AIES-AEAR-CORE-01 §11); this section covers the evidence machinery through which that governance — and the compliance obligations (X03) it administers — is demonstrated.

```
Operational record            →   Evidence for
──────────────────────────────────────────────────────────────
ART-15 audit trail            →   who/what acted, under whose approval
ART-14 registry history       →   what agents were authorized to exist
Guardrail decision log        →   controls operating effectiveness
Evaluation reports (ART-12)   →   quality and safety of AI output
Entitlement grants/expiries   →   least-authority operation
Gate approvals (X07)          →   human oversight actually exercised
```

- [AIES-AEAR-XC-01-R13] The Governance Plane MUST maintain a machine-readable mapping from each external obligation the organization asserts (regulation, standard clause, internal policy) to the platform controls and evidence sources that satisfy it.
- [AIES-AEAR-XC-01-R14] Compliance reports MUST be reproducible: the same query over the same evidence period yields the same report, and reports cite the underlying ART-15/ART-12 records.
- [AIES-AEAR-XC-01-R15] Evidence stores MUST be tamper-evident and retained per the longest applicable obligation; retention conflicts with privacy erasure (§3) MUST be resolved by documented policy, not ad hoc.
- [AIES-AEAR-XC-01-R16] Control failures (guardrail engine outage, evaluation gaps, missing audit records) MUST themselves be recorded and reportable — absence of evidence must be detectable.

## 5. Cost Management Architecture (X10)

AI spend is high-variance and per-request; cost management must therefore be **in-line**, not end-of-month.

### 5.1 Token and Resource Accounting

- [AIES-AEAR-XC-01-R17] The model gateway MUST meter every request (tokens in/out, model class, latency) and attribute it to principal, task, team/tenant, and cost center at request time (AIES-AEAR-CORE-01-R54).
- [AIES-AEAR-XC-01-R18] Execution Plane compute and Context & Knowledge Plane storage/retrieval SHOULD be attributed with the same keys, so total cost-per-task is computable.

### 5.2 Budget and Quota Enforcement

Hierarchical budget model, enforced at the gateway and orchestration layers:

```
Organization budget
 └── Team / tenant budgets
      └── Workflow / agent-type quotas
           └── Per-task ceilings (declared in ART-05 or ART-14)
```

- [AIES-AEAR-XC-01-R19] Budget exhaustion MUST fail closed with escalation (AIES-AEAR-CORE-01-R17); the platform MUST distinguish soft thresholds (alert, require approval to continue) from hard ceilings (halt).
- [AIES-AEAR-XC-01-R20] Runaway-consumption protection MUST exist at per-task granularity (loop detection, per-task token ceilings), independent of team budgets — one defective agent run must not consume a team's month.
- [AIES-AEAR-XC-01-R21] Cost telemetry SHOULD flow to the same Observability Plane dashboards as quality telemetry, so cost-quality trade-offs (EV5 Efficiency) are visible where routing policy is decided.

Cost optimization levers the architecture should expose as **policy**, not code change: model-class routing (cheaper models for lower-EV-requirement tasks), context budget limits per task type, caching of assembled context and inference where determinism permits, and batch scheduling of non-interactive work.

## 6. Reliability Patterns (X13)

### 6.1 Model Failover

The Model Plane's gateway implements a standard failure ladder:

```
Primary provider/deployment degraded?
  1. Retry within policy (bounded, idempotent requests only)
  2. Fail over to alternate provider of same capability class     (R14)
  3. Fail over to alternate of lower capability class → flag
     outputs for elevated review
  4. Queue non-interactive work; inform interactive users
  5. No serving path → degrade autonomy (§6.2)
```

- [AIES-AEAR-XC-01-R22] Failover MUST preserve data-handling constraints: an alternate provider outside the request's data-handling class MUST NOT be used, even during an outage ([AIES-AEAR-CORE-01-R18] holds under failure).
- [AIES-AEAR-XC-01-R23] Failover events MUST be recorded in ART-15 with the substituted model version, since output provenance changes.

### 6.2 Degradation to Lower Autonomy

The platform's signature reliability pattern (AIES-AEAR-CORE-01 §2 principle 6, R58–R59): when a control or capability is lost, the platform reduces agent authority rather than continuing unsupervised.

| Failure | Degradation |
|---------|-------------|
| Evaluation pipeline down | Autonomy increases blocked; AL4 tasks drop to AL3 sampling via human queue |
| Observability ingestion down | AL3–AL4 execution halts (unobserved autonomy violates X07); AL1–AL2 may continue |
| Guardrail policy engine down | Affected action classes denied (fail closed, AIES-AEAR-CORE-01-R32) |
| Model quality regression detected | Affected task types drop one autonomy level pending review |
| Anomalous agent behavior | Instance suspended; agent type may be demoted (AIES-AEAR-CORE-01-R41) |

- [AIES-AEAR-XC-01-R24] Each degraded mode MUST have a defined trigger, a defined reduced-autonomy state, a human notification path, and a defined recovery procedure — and MUST be exercised through testing, not merely documented.
- [AIES-AEAR-XC-01-R25] Recovery to normal autonomy MUST be an explicit, human-authorized action, not automatic on signal clearance.

## 7. Performance and Scalability (X11, X12)

### 7.1 Latency Classes

- **Interactive** (IDE/chat assistance): human-perceptible latency budget; guardrail and entitlement decisions on this path MUST be engineered for low latency (caching of policy decisions with bounded staleness MAY be used where policy semantics permit).
- **Reviewable** (AL2 draft production): seconds-to-minutes; throughput matters more than latency.
- **Delegated/batch** (AL3–AL4 workflows): schedulable; optimize for cost and evaluation coverage over speed.

[AIES-AEAR-XC-01-R26] Task types MUST declare a latency class, and the Model and Orchestration Planes MUST route and prioritize by it; interactive traffic MUST NOT be starved by batch agent workloads.

### 7.2 Scaling Surfaces

| Surface | Scaling behavior | Architectural note |
|---------|------------------|--------------------|
| Agent concurrency | Horizontal (Orchestration/Execution) | Bounded by policy per team/tenant (AIES-AEAR-CORE-01-R57), not by accident |
| Inference throughput | Provider capacity + gateway queueing | Multi-provider routing doubles as capacity management |
| Retrieval | Read-heavy; index sharding/replication | Entitlement filtering must scale with the index, not post-filter |
| Telemetry & ART-15 | Highest-volume write path in the platform | Append-optimized store; retention tiering from day one |
| Evaluation | Grows with output volume × sampling rate | Sampling policy is the cost lever; RT3+ SHOULD be sampled at higher rates |

## 8. Remaining Domains in Brief

- **X05 Risk Management** — risk tiers (RT1–RT4) are the platform's load-bearing risk abstraction; the tier assignment mechanism (who classifies tasks, how disputes escalate) lives in AEOS, while the platform MUST make the tier machine-readable on every task and enforce tier-derived policy everywhere (AIES-AEAR-CORE-01-R07, R44).
- **X07 Human Oversight** — architecturally realized as approval consoles and dashboards (Interaction Plane), gates (Orchestration), sampling queues (Observability), and human-only roles (Governance); see AIES-AEAR-CORE-01 §4, §12.
- **X08 Documentation** — platform configuration (Agent Definitions, workflows, policy-as-code) is documentation-as-code and MUST be versioned with review history; generated documentation inherits provenance labeling.
- **X09 Knowledge Management** — the Context & Knowledge Plane is X09's architectural home; ART-13 lifecycle is its governing process.
- **X14 Accessibility** — Interaction Plane surfaces (including approval consoles and dashboards) MUST meet the organization's accessibility standard; oversight cannot depend on interfaces some approvers cannot use.
- **X15 Sustainability** — inference and execution carry energy cost; the cost-accounting keys of §5 SHOULD extend to energy/carbon attribution where the organization reports on it, and model-class routing is the primary reduction lever.

---

## Related Documents

- [AIES-AEAR-CORE-01 — Core Reference Architecture](core-reference-architecture.md)
- [AIES-AEAR-BP-00 — Blueprint Catalog](blueprints/README.md) (industry-specific manifestations of these concerns)
- [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md) · [Glossary (AIES-SHARED-01)](../Shared/Glossary/README.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

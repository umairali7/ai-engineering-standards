# Engineering Capability Matrix Standard

| | |
|---|---|
| **Document ID** | AIES-ECM-01 |
| **Status** | Draft |
| **Audience** | Engineers, platform teams, operations leaders, and implementers |

## 1. Purpose

The Engineering Capability Matrix (ECM) communicates demonstrated engineering
capabilities from canonical AIES evidence. It is subject-neutral: it applies to
models, repositories, AI systems, agents, agent swarms, MCP servers, coding
assistants, prompt libraries, RAG systems, pipelines, and platforms.

ECM does not qualify a subject and does not grant deployment authority. It
consumes qualification evidence; it never changes gates, risk tiers, autonomy
limits, or human accountability.

Each ECM is scoped to the risk tier recorded in its source run. A task marked
`not assessed` has no mapped scored evidence in that scope; it does not mean
the subject failed the task. `observed` is descriptive evidence whose mapping
or qualification admission is incomplete. `insufficient` has admitted evidence
but lacks task breadth or rater-protocol assurance. `gate-failed` and
`performance-below-threshold` are explicit negative task decisions.
`demonstrated` satisfies [ADR-0013](../adr/ADR-0013-ECM-Task-Decision-Semantics-and-Deployment-Guidance.md).
An all-area run covers all areas at one tier, not all four risk tiers.

## 2. Architecture

```text
Assessment → Canonical Evidence → Competency Analysis →
Engineering Task Mapping → Engineering Capability Matrix → Decision Products
```

| Layer | Artifact | Primary audience |
|---|---|---|
| Qualification | Qualification Evidence / Result | Governance |
| Engineering capability | ECM | Engineers |
| Operations | Deployment Guidance | Managers and operators |
| Selection | Comparison and AIES Select | Engineering leadership |

## 3. Engineering Task Taxonomy

| ID | Task |
|---|---|
| ET-01 | Requirements Analysis |
| ET-02 | Architecture Design |
| ET-03 | API Design |
| ET-04 | Code Generation |
| ET-05 | Refactoring |
| ET-06 | Debugging |
| ET-07 | Testing |
| ET-08 | Documentation |
| ET-09 | Performance Optimization |
| ET-10 | Security Review |
| ET-11 | Database Design |
| ET-12 | Migration |
| ET-13 | Infrastructure |
| ET-14 | Observability |
| ET-15 | Production Operations |

The versioned mapping registry is the only source that connects scenario
evidence to task identifiers. A task with no mapped, scored evidence MUST
render as **not assessed**.

## 4. ECM task row requirements

Every task row MUST include task ID and versioned mapping, subject, scenario
IDs, risk tier, distinct scenarios, repeats, rating observations, resolved
admitted items, 90% uncertainty, risk-tier gates, rater protocol, mapping-review
provenance, instrument maturity, parent competency outcomes, evidence adequacy,
qualification constraints, and its exact status/reasons.

Observed performance and evidence confidence are separate. A high observed
score with low evidence confidence is never a recommendation.

## 5. Decision Products

Deployment Guidance MAY render **Use** only from a demonstrated task plus an
active matching human Qualification Record. **Use with Review** is only for a
demonstrated task whose qualification conditions or autonomy envelope require
review; it is never a fallback for weak evidence. Comparison MAY show
task deltas only when suite, mapping version, risk tier, profile, repeat
structure, rater protocol, and adequacy are compatible. AIES Select MUST use a
declared workload and operating constraints; it MUST NOT emit a global best
subject claim.

Pending mapping reviews, unverified rater evidence, inadequate distinct-task
breadth, uncertainty/gate failures, expired or invalid qualifications, and
scope/autonomy mismatches render **No recommendation / collect evidence** or
**Avoid for this scoped use**, never an operational use claim.

## Related Documents

- [ADR-0008](../adr/ADR-0008-Engineering-Capability-Matrix-Standard-and-Task-Taxonomy.md)
- [Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](../AESQS/capability-scoring.md)
- [Platform](../docs/PLATFORM.md)

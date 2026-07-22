# ADR-0013: Govern ECM task decisions and deployment guidance

| | |
|---|---|
| **ADR** | ADR-0013 |
| **Status** | Accepted |
| **Deciders** | Umair Ali (repository owner); ECM Module Editor; AESQS Module Editor; Platform Module Editor |
| **Supersedes / Superseded by** | Extends ADR-0008; supersedes no accepted decision |

## Context

ADR-0008 established the subject-neutral Engineering Capability Matrix (ECM)
and Engineering Task Taxonomy. The current reference renderer maps scenarios to
ET-01 through ET-15 and reports observed performance, but AIES-ECM-01 remains
Draft and does not yet define a task-specific decision protocol.

The implementation has borrowed competency-area sample minimums when deciding
whether a task is `demonstrated`. That is not valid: a competency sample and a
task sample are different populations, rating observations are not independent
task evidence items, and an area gate does not prove a task-specific safety
floor. The renderer also has enough information to place such a row under
Deployment Guidance `Use`, which turns an ungoverned inspection statistic into
an operational recommendation.

During migration, the platform conservatively labels mapped task evidence
`observed` and emits no `Use` recommendation until each required mapping review
and task-decision control is present.

## Decision Drivers

- One canonical evidence item must count once regardless of repeat ratings.
- A high mean with weak breadth, unsafe tails, or unresolved disagreement must
  not become a capability claim.
- Task performance, evidence confidence, qualification, and deployment
  authorization are separate facts.
- Task decisions must remain subject-neutral and comparable only under matching
  protocols.
- Deployment Guidance must be bounded by an active human qualification record,
  its conditions, risk tier, role/phases, and autonomy envelope.
- Current unreviewed mappings and the absence of empirical calibration must be
  visible limitations, not silently converted into certainty.

## Existing-Contracts Check

- **Can existing contracts express this?** Partly. Evidence Package v5 supplies
  resolved evidence items, rater protocol, gates, and provenance. The task
  mapping supplies stable ET identifiers. AIES-ECM-01 does not yet specify task
  sample adequacy, task uncertainty, safety floors, or deployment-guidance
  semantics.
- **Contracts affected:** AIES-ECM-01 and the versioned task-mapping contract
  require additive normative fields. The ECM artifact must receive a schema
  version bump when implemented. AESQS qualification gates and decision
  semantics remain unchanged; ECM cannot reinterpret or weaken them.

## Options Considered

### Option A — Continue borrowing competency-area adequacy

- **Pros:** Produces immediate `demonstrated` rows from existing runs.
- **Cons:** Uses the wrong population, lets multi-rater observations inflate
  coverage, and overstates what the evidence establishes.

### Option B — Treat any mapped evidence as demonstrated

- **Pros:** Simple and visually useful.
- **Cons:** A single easy scenario could authorize a task claim; there is no
  uncertainty, safety floor, or qualification boundary.

### Option C — Govern a distinct task-decision protocol (proposed)

Compute task decisions only from qualification-eligible resolved evidence
items with reviewed mappings, task-specific breadth, uncertainty, gates, and
protocol checks. Keep descriptive automated observations available, but never
promote them into `demonstrated` or `Use`.

## Decision

Adopt Option C with these rules:

1. **Unit of analysis.** One retained response is one task evidence item. A
   response mapped to multiple tasks may inform each mapped task, but multiple
   raters and exact repeats never create additional distinct-task breadth.
2. **Two evidence lanes.** `observed_performance` may summarize complete
   automated or human engineering-evaluation observations and is always
   informational. `task_decision` uses only Evidence Package v5 resolved items
   whose `qualification_eligible` value is true.
3. **Mapping admission.** Every counted scenario-to-task mapping records mapping
   version, rationale, reviewer identity, review status, and review date.
   Unreviewed mappings may populate `observed`; they cannot populate
   `demonstrated`.
4. **Task-specific breadth.** The initial conservative minimum is explicitly
   task-scoped and equals the AESQS subject-kind/risk-tier item minimum: for AI
   subjects, 20/30/50/100 distinct mapped scenarios at RT1 — Minimal through
   RT4 — Critical; for human subjects, 5/8/12/20. These numbers are not borrowed
   after the fact from a contributing area. Any later task-specific thresholds
   require empirical evidence and a superseding decision.
5. **Uncertainty.** Each EV1–EV6 task dimension reports `n`, mean, and two-sided
   90% confidence interval over resolved distinct items. The lower bound is the
   decision value. The row reports mapping version, scenario IDs, distinct
   items, repeats, rating observations, admitted items, unresolved items,
   double-rating coverage, agreement, and instrument-calibration maturity.
6. **Task gates and safety floors.** Apply the scoped risk-tier EV gates to task
   decision values without profile relaxation. At RT3 — Significant and RT4 —
   Critical, any admitted task item with EV3 — Safety & Security = 0 hard-fails
   the task. Every contributing competency area must also be decisional and
   gate-passing; a strong task slice cannot compensate for a failed parent
   qualification scope.
7. **Demonstrated semantics.** A task is `demonstrated` only when its mappings
   are reviewed, distinct-task minimum is met, ADR-0012 rater protocol is met,
   no material divergence remains, all task gates pass, every contributing area
   passes, and the task aggregate reaches at least CL1 — Foundational (2.0).
   `observed` means descriptive scored evidence exists but is not admitted or
   not yet governed/adequate. `insufficient` means admitted evidence exists but
   fails breadth/protocol/uncertainty requirements without a performance gate
   failure. `not assessed` means no direct mapped evidence exists. A gate or
   safety failure is reported explicitly and never softened to `insufficient`.
8. **No global score.** Task aggregates remain task-scoped. ECM does not average
   tasks into a global subject score or a global best-subject ranking.
9. **Deployment Guidance.** `Use` requires a demonstrated task and a current
   active/conditional human Qualification Record covering the same subject,
   framework/mapping version, risk tier, contributing competencies, role,
   phases, and requested autonomy. `Use with Review` is permitted only for a
   demonstrated task when the qualification or autonomy envelope requires
   human review/approval; it is not a fallback for weak evidence. Unassessed,
   observed, insufficient, expired, invalidated, out-of-scope, or gate-failing
   tasks receive **No recommendation / collect evidence** or **Avoid for this
   scoped use**, with the exact reason. Guidance never creates authority.
10. **Comparison.** Descriptive observed values may be shown side by side, but
    a delta/winner claim requires compatible mapping version, risk tier,
    profile/weights, suites, task protocol, rater protocol, instrument maturity,
    and demonstrated status on both sides.
11. **Honesty during migration.** Until this ADR's conformance cases pass for a
    task and its mappings are reviewed, that task remains `observed`, numeric
    decision confidence is marked unavailable, and Deployment Guidance emits
    no `Use` recommendation.

## Consequences

**Positive:** Task claims become statistically and operationally defensible;
model selection can compare like with like; high observed performance remains
visible without becoming deployment authority.

**Negative:** Existing runs will initially show fewer demonstrated tasks, and
the current mapping registry requires human review metadata. RT3/RT4 task
claims require much larger distinct-task corpora. This is intentional: missing
evidence is work to perform, not confidence to manufacture.

## Compliance & Verification

- Conformance fixtures prove additional raters and repeats do not increase task
  `n` or confidence.
- Boundary tests cover every subject-kind/risk-tier task minimum.
- Gate, EV3 hard-fail, unresolved-divergence, mapping-review, and parent-area
  failures each prevent `demonstrated`.
- Deployment Guidance fixtures reject absent, expired, invalidated,
  out-of-scope, or autonomy-incompatible Qualification Records.
- Comparison fixtures reject every protocol incompatibility independently.
- Markdown, HTML, and JSON consume one factual ECM view model and render the
  same status/reasons.

## Links

- Pull request: to be added when proposed for review.
- [ADR-0008 — Engineering Capability Matrix standard and task taxonomy](ADR-0008-Engineering-Capability-Matrix-Standard-and-Task-Taxonomy.md)
- [AIES-ECM-01 — Engineering Capability Matrix](../ECM/README.md)
- [ADR-0012 — Qualification evidence, rater protocol, and immutable lifecycle](ADR-0012-Qualification-Evidence-Rater-Protocol-and-Immutable-Lifecycle.md)
- [AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md)
- [AIES-DOC-14 — Vision Execution Backlog](../docs/OSS_MATURITY_TODO.md)

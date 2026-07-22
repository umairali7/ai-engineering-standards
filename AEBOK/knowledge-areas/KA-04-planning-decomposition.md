# KA-04 — Planning & Work Decomposition

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-04 |
| **Status** | Review |
| **Audience** | Engineers · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-04 covers Planning (P08): how work is decomposed, classified, sequenced, and routed when the executing workforce is a mix of humans, AI agents, and human-AI pairs. In pre-AI planning, decomposition optimized for human cognition and team boundaries. In AI-native planning, decomposition additionally determines **what autonomy is possible**: a well-decomposed task can be safely delegated at AL3 — Delegated; the same work left as one entangled lump forces AL1 — Assisted or saturates review. Planning quality is therefore a direct input to delivery throughput, not administrative overhead — the plan (ART-05) is where risk classification and routing decisions become concrete.

## 2. Key Concepts

- **Decomposition determines delegability.** A task is delegable to an agent to the degree that it has: a self-contained scope, explicit acceptance criteria, machine-verifiable success conditions, bounded blast radius, and available context. Decomposition is the act of manufacturing these properties.
- **Task-level risk classification.** Risk tiers attach to tasks, not projects. A single feature typically decomposes into tasks of different tiers — scaffolding (RT1 — Minimal), feature logic behind review (RT2 — Moderate), schema migration (RT3 — Significant) — each with a different autonomy ceiling. Skilled decomposition *separates* tiers so the RT3 — Significant slice does not drag the whole feature down to AL1 — Assisted.
- **Routing.** Each task is routed to a performer class — human, human-AI pair, or agent at a declared AL — based on task type, risk tier, and the performer's qualification (AESQS evidence). Routing is a planning decision (ROLE-01) and is recorded in the work item.
- **Verifiability as a planning input.** "How will we know this is correct?" is asked at planning time, not testing time. Tasks whose success can be verified automatically (tests, contract checks, evaluation criteria) can be executed at higher autonomy; tasks verifiable only by human judgment must be sized to fit human review capacity (see [KA-11](KA-11-human-ai-collaboration.md)).
- **Dependency honesty.** Agents parallelize cheaply, which makes hidden dependencies expensive: two agents working "independent" tasks that share unstated coupling produce conflicting changes that consume more review than sequential work would have. Dependency mapping is a precondition of parallel AI execution.
- **AI-assisted planning.** AI participates in P08 itself — proposing decompositions, estimating from historical work items, detecting dependency conflicts, drafting acceptance criteria. Plan approval remains human (ROLE-01, with ROLE-13 at gates) because the plan encodes risk acceptance.

## 3. Core Practices

- **Decompose to the autonomy boundary.** Split work until each task has a single risk tier and a clear verification method; stop splitting when further division adds coordination cost without changing tier or verifiability.
- **Classify and route every task.** [AIES-AEBOK-KA-04-R01] Every work item (ART-05) routed to AI execution MUST record its risk tier, the assigned autonomy level, and the performer (human, pair, or agent per its agent definition ART-14), consistent with the [Taxonomy §3–4 mapping](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4).
- **Write acceptance criteria as contracts.** [AIES-AEBOK-KA-04-R02] Tasks assigned to agents at AL2 — Collaborative or above MUST include explicit acceptance criteria and the verification method by which the criteria will be checked; "done when it looks right" criteria MUST NOT be used for AL3 — Delegated+ tasks.
- **Map dependencies before parallelizing.** [AIES-AEBOK-KA-04-R03] Tasks scheduled for concurrent execution by multiple agents MUST be checked for shared-artifact and interface dependencies; tasks with unresolved shared state SHOULD be serialized or re-decomposed.
- **Bundle context with the task.** Each routed task SHOULD reference the context assets (ART-13) its performer needs — relevant ADRs, conventions, prior art — so agents start grounded rather than guessing (see [KA-10](KA-10-context-knowledge.md)).
- **Plan the review load.** Planning SHOULD forecast the human review demand a batch of AI-executed tasks will generate and keep it within the team's demonstrated review capacity; exceeding it produces Review Theater downstream (see [KA-11](KA-11-human-ai-collaboration.md)).

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Tier-Separating Decomposition** | Split mixed-risk work so high-tier slices are isolated into small, human-supervised tasks while the low-tier bulk runs at higher autonomy. |
| **Verification-First Task Design** | Author the acceptance check (test, contract, evaluation rubric) before or with the task description; a task without a check is not ready to route. |
| **Capability-Matched Routing** | Route task types to performers based on qualification evidence (AESQS) for that task type — not on general reputation or availability alone. |
| **Context-Bundled Work Item** | The work item carries links to everything its performer needs; an agent that must forage for context is a task that was not finished being planned. |
| **Review Budgeting** | Treat human review capacity as a scheduled resource; a sprint plan that generates more review than the team can perform is over capacity, regardless of agent throughput. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Monolithic Delegation** | An entire feature ("build the invoicing module") is handed to an agent as one task; risk tiers blur, verification is impossible, and review arrives as one unreviewable mass. |
| **Tier Averaging** | A mixed-risk task is classified at its *average* tier instead of its highest; the RT3 — Significant schema change inside rides through at RT2 — Moderate autonomy. |
| **Optimistic Parallelism** | Agents are fanned out over undecomposed dependencies; merge conflicts and interface mismatches consume the "saved" time. |
| **Criteria-Free Tasking** | Tasks are routed with intent but no acceptance criteria; the agent optimizes for plausibility, and rework loops replace planning. |
| **Throughput Mirage** | Planning celebrates agent task-completion volume while integration, review, and rework queues grow unbounded — output rises, outcomes do not (measure per [KA-12](KA-12-evaluation-improvement.md)). |

## 6. Competency Expectations

| Level | Expectation in KA-04 |
|-------|----------------------|
| **CL1** | Explains why decomposition affects delegability; writes acceptance criteria for a simple task; identifies the risk tier of routine task types with guidance. |
| **CL2** | Independently decomposes standard features into tier-separated, verification-first tasks; routes tasks to appropriate performers; maintains dependency maps for parallel execution. |
| **CL3** | Plans mixed human/AI delivery for complex, cross-team work; balances review budgets across a program; coaches teams out of monolithic delegation and throughput-mirage habits. |
| **CL4** | Defines organizational planning standards for AI-native delivery; evaluates portfolio-level routing policy against outcome data; evolves decomposition practice as agent capability and qualification evidence shift. |

## Related Documents

- Risk/autonomy foundations applied here: [KA-01 (AIES-AEBOK-KA-01 — Knowledge Area — Foundations)](KA-01-foundations.md); the architecture that makes decomposition possible: [KA-03 (AIES-AEBOK-KA-03 — Knowledge Area — Architecture Design)](KA-03-architecture-design.md).
- What routed tasks become downstream: [KA-05 Implementation (AIES-AEBOK-KA-05 — Knowledge Area — Implementation)](KA-05-implementation.md), [KA-06 Testing & Quality (AIES-AEBOK-KA-06 — Knowledge Area — Testing and Quality)](KA-06-testing-quality.md).
- Review capacity and gate mechanics that planning must respect: [KA-11 (AIES-AEBOK-KA-11 — Knowledge Area — Human-AI Collaboration)](KA-11-human-ai-collaboration.md).
- Context bundling: [KA-10 (AIES-AEBOK-KA-10 — Knowledge Area — Context and Knowledge)](KA-10-context-knowledge.md). Outcome measurement of planning quality: [KA-12 (AIES-AEBOK-KA-12 — Knowledge Area — Evaluation and Improvement)](KA-12-evaluation-improvement.md).
- Planner role definition (ROLE-01) and workflow: [AIES-AEOS-00 — AEOS — AI Engineering Operating System](../../AEOS/README.md); performer qualification evidence: [AESQS (AIES-AESQS-00 — Qualification Standard)](../../AESQS/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

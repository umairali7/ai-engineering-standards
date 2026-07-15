# KA-06 — Testing & Quality Engineering

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-06 |
| **Status** | Review |
| **Audience** | Engineers · QA engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-06 covers Testing & Quality (P10) in AI-native delivery, which has three distinct concerns that are often conflated: (1) **testing AI-produced code** — adapting quality practice to artifacts with plausible failure modes and high volume; (2) **AI-assisted test engineering** — using AI to generate and maintain tests without corrupting the independence that makes tests meaningful; and (3) **evaluating non-deterministic components** — establishing quality claims about system components whose outputs vary across runs. Testing is also the load-bearing wall of autonomy: the autonomy ceilings of KA-01 and the delegation patterns of KA-04/KA-05 all assume that verification is real. If P10 is weak, every AL2+ assignment in the organization is running on unverified trust.

## 2. Key Concepts

- **Tests as the delegation contract.** For an agent-executed task, the test suite *is* the enforceable meaning of "done." Autonomy levels above AL2 are only as sound as the verification that backs them — which makes test quality a governance concern (X04), not just an engineering nicety.
- **Independence of verification.** A test's value depends on its independence from the artifact it verifies. When the same actor (human or AI, or the same AI context) produces both code and its tests, errors correlate: the misunderstanding that produced the bug also produces the test that blesses it. Independence can be restored by separating actors, separating contexts, or deriving tests from requirements rather than from implementation.
- **Coverage theater vs. verification power.** AI test generation makes high coverage numbers nearly free — and nearly meaningless. Tests that assert what the code *does* (snapshot its current behavior) rather than what it *should do* (its requirements) produce coverage without verification power. Mutation testing and requirement-tracing expose the difference.
- **Evaluation of non-deterministic components.** Components whose behavior includes AI inference cannot be verified by example-based assertion alone. Quality claims take statistical form — pass rates over golden task sets, score distributions along EV1–EV6 dimensions, threshold gates on regression suites — and are produced by *evaluation* (see [Glossary](../../Shared/Glossary/README.md)), a repeatable procedure distinct from but complementary to testing.
- **Oracle problem, sharpened.** For non-deterministic outputs there is often no single correct answer to assert against. Practical oracles include property checks (invariants that must hold for any output), reference-based scoring, rubric evaluation, and — under strict conditions — model-based judges, which are themselves non-deterministic components requiring their own validation.
- **Quality signal decay.** Test suites and evaluation sets are context assets (ART-13) that decay: golden tasks go stale as the product changes, and once an evaluation set leaks into training or generation context, its scores inflate. Quality assets need lifecycle management ([KA-10](KA-10-context-knowledge.md)).

## 3. Core Practices

- **Verify AI-produced code against requirements, not behavior.** [AIES-AEBOK-KA-06-R01] Acceptance tests for AI-produced changes MUST derive from the work item's acceptance criteria (ART-05), not from the produced implementation's observed behavior.
- **Enforce verification independence.** [AIES-AEBOK-KA-06-R02] For RT2+ changes, the verification that gates a change MUST have independence from the change's producer: authored by a different actor, generated in a separate context from separate inputs, or pre-existing before the change. Agent-written tests for that agent's own change MAY be included but MUST NOT be the sole gate.
- **Use AI test generation for breadth, humans for meaning.** AI SHOULD be used to generate edge cases, property candidates, and regression scaffolding (typically RT1–RT2 work at AL2–AL3); humans (ROLE-07) validate that generated tests assert intended behavior. Generated tests that merely snapshot current behavior SHOULD be labeled as characterization tests, distinct from acceptance tests.
- **Measure verification power, not just coverage.** Teams SHOULD periodically apply mutation testing or fault-injection to test suites that gate AI-produced change; suites with high coverage but low mutation kill rates are treated as gate failures in themselves.
- **Evaluate non-deterministic components statistically.** [AIES-AEBOK-KA-06-R03] Components with non-deterministic (AI-inference) behavior MUST be qualified through defined evaluation procedures — versioned task sets, scoring rubrics mapped to EV1–EV6, and explicit pass thresholds — executed repeatably and recorded (ART-07/ART-12), not through ad hoc spot checks.
- **Maintain golden task regression.** [AIES-AEBOK-KA-06-R04] Changes to prompts, context assets, or model configuration of a production AI component MUST pass the component's golden task regression suite before promotion (see [pattern catalog](../patterns/README.md#pat-06-golden-task-regression)).
- **Validate the judges.** Where model-based evaluation is used, the judge's agreement with human expert judgment SHOULD be measured on a calibration set before its scores are trusted in gates, and re-measured when the judge's configuration changes.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Independent Test Channel** | Tests for an AI-produced change are produced through a path (actor/context/inputs) disjoint from the implementation, restoring error decorrelation. |
| **Golden Task Regression** | A curated, versioned set of representative tasks with expected outcomes gates every change to an AI component's prompt, context, or configuration. |
| **Property-Based Oracle** | Where exact outputs vary, assert invariant properties (schema validity, safety constraints, referential integrity) that every acceptable output must satisfy. |
| **Mutation Audit** | Periodic mutation testing scores the real verification power of suites that gate autonomous change; kill-rate thresholds are part of quality policy. |
| **Rubric-Scored Evaluation** | Non-deterministic outputs are scored against explicit rubrics mapped to EV1–EV6, with human calibration samples keeping scorers honest. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Self-Certifying Change** | The agent that wrote the code writes the only tests that gate it; correlated errors pass in pairs. |
| **Coverage Theater** | Generated tests inflate coverage metrics while asserting nothing about requirements; dashboards are green, verification power is near zero. |
| **Snapshot Blessing** | Characterization tests of buggy current behavior get promoted to acceptance tests, freezing defects as specification. |
| **Single-Run Verdict** | A non-deterministic component is declared working because one demo run succeeded; variance was never measured. |
| **Stale Golden Set** | The golden task set no longer represents production traffic, or has leaked into generation context; regression gates pass while real quality regresses. |
| **Unvalidated Judge** | Model-based scores gate promotion without ever being calibrated against human judgment; the gate measures the judge's biases, not quality. |

## 6. Competency Expectations

| Level | Expectation in KA-06 |
|-------|----------------------|
| **CL1** | Explains verification independence and the oracle problem; runs existing test and evaluation suites and interprets their reports; distinguishes acceptance from characterization tests. |
| **CL2** | Independently builds requirement-derived tests for AI-produced changes; uses AI test generation with human validation; executes and maintains golden task regressions for standard components. |
| **CL3** | Designs evaluation procedures for novel non-deterministic components, including oracle selection and judge validation; runs mutation audits; coaches teams out of coverage theater. |
| **CL4** | Sets organizational quality policy for AI-native delivery: independence requirements, evaluation standards, gate thresholds per risk tier; evolves policy from defect-escape and drift data ([KA-12](KA-12-evaluation-improvement.md)). |

## Related Documents

- What testing gates: [KA-05 AI-Assisted Implementation (AIES-AEBOK-KA-05)](KA-05-implementation.md); where gates execute: [KA-08 DevOps & Release (AIES-AEBOK-KA-08)](KA-08-devops-release.md).
- Task-level acceptance criteria that tests derive from: [KA-04 Planning & Work Decomposition (AIES-AEBOK-KA-04)](KA-04-planning-decomposition.md).
- Lifecycle of golden sets, rubrics, and other quality assets: [KA-10 Context & Knowledge Management (AIES-AEBOK-KA-10)](KA-10-context-knowledge.md).
- Production-side evaluation and drift detection: [KA-09 Operations & Observability (AIES-AEBOK-KA-09)](KA-09-operations-observability.md), [KA-12 Evaluation & Continuous Improvement (AIES-AEBOK-KA-12)](KA-12-evaluation-improvement.md).
- QA role definition (ROLE-07): [AEOS (AIES-AEOS-00)](../../AEOS/README.md); the evaluation dimensions (EV1–EV6) and scoring method: [AESQS (AIES-AESQS-00)](../../AESQS/README.md) and [Taxonomy §8 (AIES-SHARED-02)](../../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

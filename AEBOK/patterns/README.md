# AEBOK Pattern & Anti-Pattern Catalog

| | |
|---|---|
| **Document ID** | AIES-AEBOK-PAT-00 |
| **Status** | Review |
| **Audience** | Engineers · Architects |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

This catalog consolidates the named patterns and anti-patterns of AI participation in engineering work that recur across the [AEBOK Knowledge Areas](../README.md#3-knowledge-area-map). Each entry has a stable ID (`PAT-NN` / `APAT-NN`) so that KAs, [AEOS](../../AEOS/README.md) workflows, and [AECT](../../AECT/README.md) course material can reference the same concept without redefinition. Individual KAs also name *local* patterns specific to their phase (e.g., Agent Activity Ledger in [KA-09](../knowledge-areas/KA-09-operations-observability.md)); this catalog indexes the cross-cutting canon that multiple KAs share.

Catalog entries are descriptive vocabulary, not requirements. Where a pattern is mandatory in some context, the owning KA states it as a tagged requirement; this catalog links to the KAs where that normative language lives. All entries use taxonomy IDs ([AIES-SHARED-02](../../Shared/Taxonomy/README.md)) for phases, autonomy levels, risk tiers, roles, and artifacts.

## 2. Patterns

Reusable approaches that make AI participation bounded, verifiable, and traceable. Each row states the problem the pattern answers and the shape of the solution.

| ID | Pattern | Problem | Solution | Primary KAs | Phases |
|----|---------|---------|----------|-------------|--------|
| <a id="pat-01-bounded-autonomy-envelope"></a>PAT-01 | **Bounded Autonomy Envelope** | An agent's effective authority defaults to whatever its credentials permit, which no one has reviewed as a whole. | Define, per agent (ART-14) and task type, the explicit set of permitted actions, resources, and limits; everything outside the envelope escalates to a human. | [KA-01](../knowledge-areas/KA-01-foundations.md), [KA-07](../knowledge-areas/KA-07-security.md) | All |
| <a id="pat-02-evidence-gated-promotion"></a>PAT-02 | **Evidence-Gated Promotion** | Autonomy and promotion decisions drift toward enthusiasm and convenience when nothing forces them onto evidence. | Promotion — of a change through the pipeline, or of an agent to a higher AL — requires attached evidence evaluated against tier policy; no evidence, no promotion, regardless of author. | [KA-01](../knowledge-areas/KA-01-foundations.md), [KA-08](../knowledge-areas/KA-08-devops-release.md), [KA-12](../knowledge-areas/KA-12-evaluation-improvement.md) | P12–P13, P16 |
| <a id="pat-03-least-autonomy-default"></a>PAT-03 | **Least-Autonomy Default** | New task types launch at whatever autonomy the tooling makes easy, then adjust after incidents. | Start every new task type at the lowest useful AL for its risk tier and raise it only through PAT-02; the default answers "why so low?", never "why so high?". | [KA-01](../knowledge-areas/KA-01-foundations.md), [KA-04](../knowledge-areas/KA-04-planning-decomposition.md) | P08–P09 |
| <a id="pat-04-provenance-first-change"></a>PAT-04 | **Provenance-First Change** | After merge, no one can tell which changes an AI produced, under what authority, against what task. | Tooling stamps every source change (ART-06) with actor, AL, and work-item identifiers automatically at creation; provenance survives through deployment into telemetry. | [KA-05](../knowledge-areas/KA-05-implementation.md), [KA-08](../knowledge-areas/KA-08-devops-release.md), [KA-09](../knowledge-areas/KA-09-operations-observability.md) | P09, P12–P15 |
| <a id="pat-05-context-curation-pipeline"></a>PAT-05 | **Context Curation Pipeline** | Organizational knowledge reaches agents raw — ambiguous, stale, contradictory — or not at all. | Knowledge flows through an explicit pipeline: capture → transform for machine consumption → validate → version → publish as owned context assets (ART-13). | [KA-10](../knowledge-areas/KA-10-context-knowledge.md), [KA-03](../knowledge-areas/KA-03-architecture-design.md) | All (X09) |
| <a id="pat-06-golden-task-regression"></a>PAT-06 | **Golden Task Regression** | Changes to prompts, context, or configuration alter AI behavior invisibly; quality regressions surface in production. | A curated, versioned suite of representative tasks with expected outcomes gates every change to an AI component and doubles as the drift-detection baseline. | [KA-06](../knowledge-areas/KA-06-testing-quality.md), [KA-12](../knowledge-areas/KA-12-evaluation-improvement.md) | P10, P16 |
| <a id="pat-07-independent-test-channel"></a>PAT-07 | **Independent Test Channel** | When one actor (or one context) produces both code and its tests, errors correlate and pass in pairs. | Verification for an AI-produced change is produced through a path — actor, context, inputs — disjoint from the implementation, restoring error decorrelation. | [KA-06](../knowledge-areas/KA-06-testing-quality.md), [KA-05](../knowledge-areas/KA-05-implementation.md) | P09–P10 |
| <a id="pat-08-human-checkpoint-sampling"></a>PAT-08 | **Human Checkpoint Sampling** | Per-item human review does not survive AL3 volume; dropping review entirely is not an option. | Humans review a risk-weighted sample of outputs plus all envelope-edge events, with sampling rates tied to the performer's evaluation history and tightened on degradation. | [KA-11](../knowledge-areas/KA-11-human-ai-collaboration.md), [KA-05](../knowledge-areas/KA-05-implementation.md) | P09 (X07) |
| <a id="pat-09-degrade-to-assist"></a>PAT-09 | **Degrade-to-Assist** | When an AI performer's quality slips in operation, the only prepared responses are "ignore" or "shut down". | Define degradation triggers and fallback levels in advance; autonomy steps down (AL3 → AL2 → AL1) when signals cross thresholds, so capability degrades to assistance instead of failing opaque. | [KA-09](../knowledge-areas/KA-09-operations-observability.md), [KA-12](../knowledge-areas/KA-12-evaluation-improvement.md) | P14–P15 |
| <a id="pat-10-feedback-to-context-loop"></a>PAT-10 | **Feedback-to-Context Loop** | Production incidents and review rejections repeat because the knowledge that caused them is never corrected at its source. | Findings traced to wrong or missing context become correction work items against the owning context assets; golden suites refresh from the same findings. | [KA-12](../knowledge-areas/KA-12-evaluation-improvement.md), [KA-10](../knowledge-areas/KA-10-context-knowledge.md) | P16 (X09) |

## 3. Anti-Patterns

Named failure modes of AI-native delivery. Each row states the symptom to recognize and the remedy — which is usually one or more of the patterns above.

| ID | Anti-Pattern | Symptom | Remedy | Primary KAs | Phases |
|----|--------------|---------|--------|-------------|--------|
| <a id="apat-01-unbounded-agent"></a>APAT-01 | **Unbounded Agent** | An agent operates without a declared envelope; its real authority is discovered during the incident it causes. | Declare envelopes before operation (PAT-01); derive credentials from the envelope, not the reverse. | [KA-01](../knowledge-areas/KA-01-foundations.md), [KA-07](../knowledge-areas/KA-07-security.md) | All |
| <a id="apat-02-review-theater"></a>APAT-02 | **Review Theater** | Near-100% approval at near-zero dwell time; audit records show diligence that never occurred; intent-level errors flow through green gates. | Reviewable increments with decision context, gate-health monitoring, sampling regimes matched to capacity (PAT-08). | [KA-11](../knowledge-areas/KA-11-human-ai-collaboration.md), [KA-05](../knowledge-areas/KA-05-implementation.md) | P09–P13 (X07) |
| <a id="apat-03-autonomy-creep"></a>APAT-03 | **Autonomy Creep** | Autonomy expands through convenience-driven exceptions — each reasonable alone — until actual autonomy exceeds the declared level with no decision on record. | Least-autonomy defaults (PAT-03) and evidence-gated promotion (PAT-02); periodic reconciliation of declared vs. actual autonomy. | [KA-01](../knowledge-areas/KA-01-foundations.md), [KA-12](../knowledge-areas/KA-12-evaluation-improvement.md) | All |
| <a id="apat-04-silent-delegation"></a>APAT-04 | **Silent Delegation** | Work is quietly re-delegated to AI above its declared AL — outputs forwarded without the required review; the declared control and the actual control diverge without a record. | Provenance-First Change (PAT-04) to make the true producer visible; blameless escalation so overload is reported instead of hidden. | [KA-11](../knowledge-areas/KA-11-human-ai-collaboration.md), [KA-05](../knowledge-areas/KA-05-implementation.md) | P09 (X07) |
| <a id="apat-05-prompt-sprawl"></a>APAT-05 | **Prompt Sprawl** | Uncontrolled copies of prompts and instructions multiply across tools and personal stashes; nobody knows which variant produced what, and fixes never propagate. | Context curation pipeline with single-source, versioned assets (PAT-05); retire duplicates deliberately. | [KA-10](../knowledge-areas/KA-10-context-knowledge.md) | All (X09) |
| <a id="apat-06-fluency-as-validation"></a>APAT-06 | **Fluency-as-Validation** | Well-written AI output passes review because it reads professionally; correctness of content is never independently established. | Review against sources and acceptance criteria, not prose quality; assumption ledgers and traceable derivation ([KA-02](../knowledge-areas/KA-02-business-requirements.md)). | [KA-02](../knowledge-areas/KA-02-business-requirements.md), [KA-11](../knowledge-areas/KA-11-human-ai-collaboration.md) | P01–P05 |
| <a id="apat-07-context-rot"></a>APAT-07 | **Context Rot** | The context store grows but is never validated or retired; stale and contradictory assets carry curated authority while misleading every consumer at once. | Freshness SLAs, review-by dates enforced at assembly, deliberate retirement (PAT-05, PAT-10). | [KA-10](../knowledge-areas/KA-10-context-knowledge.md) | All (X09) |
| <a id="apat-08-metric-gaming"></a>APAT-08 | **Metric Gaming** | A gate or promotion metric only ever improves — coverage, pass rate, task count — while the outcome it stood for degrades unmeasured. | Paired counter-metrics, mutation audits of gating suites, periodic audit of what each metric still measures ([KA-12](../knowledge-areas/KA-12-evaluation-improvement.md)). | [KA-12](../knowledge-areas/KA-12-evaluation-improvement.md), [KA-06](../knowledge-areas/KA-06-testing-quality.md) | P10, P16 |
| <a id="apat-09-vendor-lock-in-by-convenience"></a>APAT-09 | **Vendor Lock-in by Convenience** | Envelopes, gates, provenance, and context assets are expressed only in one supplier's proprietary configuration; switching or multi-sourcing becomes a rewrite of the control layer. | Express policy in taxonomy terms (AL/RT/ART) owned by the organization; treat supplier configuration as a replaceable projection of it, per [AEAR](../../AEAR/README.md). | [KA-01](../knowledge-areas/KA-01-foundations.md), [KA-03](../knowledge-areas/KA-03-architecture-design.md) | All |
| <a id="apat-10-coverage-theater"></a>APAT-10 | **Coverage Theater** | Generated tests inflate coverage metrics while asserting nothing about requirements; dashboards are green, verification power is near zero. | Requirement-derived acceptance tests, mutation audits, characterization tests labeled as such ([KA-06](../knowledge-areas/KA-06-testing-quality.md)). | [KA-06](../knowledge-areas/KA-06-testing-quality.md) | P10 |

## 4. Using the Catalog

- **Referencing.** Documents SHOULD reference catalog entries by ID and anchor (e.g., `[PAT-06](../patterns/README.md#pat-06-golden-task-regression)`) rather than restating definitions; KA-local patterns remain defined in their KA.
- **Extending.** New entries MUST be added through the change process in [GOVERNANCE.md](../../GOVERNANCE.md); IDs are stable and MUST NOT be renumbered or reused after retirement.
- **Learning.** [AECT](../../AECT/README.md) uses this catalog as the recognition vocabulary for CL1–CL2 assessment: recognizing an anti-pattern in a scenario and naming the remedying pattern is a core practitioner skill.

## Related Documents

- [AEBOK Module Overview (AIES-AEBOK-00)](../README.md) — the Knowledge Areas this catalog cross-references
- [Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md) — canonical IDs for phases, autonomy levels, risk tiers, roles, and artifacts
- [AEOS (AIES-AEOS-00)](../../AEOS/README.md) — workflows that reference catalog entries
- [AECT (AIES-AECT-00)](../../AECT/README.md) — course material built on this vocabulary
- [Governance (AIES-GOV-01)](../../GOVERNANCE.md) — the change process for extending the catalog

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

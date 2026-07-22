# KA-01 — Foundations of AI-Native Engineering

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-01 |
| **Status** | Review |
| **Audience** | All readers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-01 defines the conceptual foundation that every other Knowledge Area assumes. It explains what changes when AI systems participate in engineering work — economically, organizationally, and in the risk profile of delivery — and how the AIES autonomy/risk model turns that change from a hazard into a managed capability. A practitioner who has internalized KA-01 can reason about *any* AI-in-the-SDLC question from first principles, even in situations no later KA covers explicitly.

## 2. Key Concepts

### 2.1 AI-Native Software Engineering

**AI-native software engineering** (see [Glossary](../../Shared/Glossary/README.md)) is a practice in which AI participation is *designed into* the SDLC — with declared roles, autonomy levels, quality gates, and audit trails — rather than adopted ad hoc. The distinction is architectural, not tooling-based: an organization using AI tools heavily but without declared autonomy levels or provenance is not AI-native; it is merely AI-exposed.

### 2.2 The Economic Shift

AI participation changes the cost structure of engineering:

| Dimension | Pre-AI baseline | AI-native shift | Consequence |
|-----------|-----------------|-----------------|-------------|
| Cost of producing artifacts | High (human hours) | Low and falling | Production is no longer the bottleneck |
| Cost of reviewing artifacts | Moderate | Unchanged (human attention) | **Review becomes the bottleneck** |
| Cost of a wrong artifact reaching production | High | Unchanged or higher (volume) | Verification capacity must scale with generation capacity |
| Marginal cost of exploration | High | Near zero | More alternatives can be evaluated (P06) |
| Cost of knowledge retrieval | High (tribal knowledge) | Low *if curated* | Context curation (KA-10) becomes a first-class investment |

The central economic insight: **when generation is cheap, judgment is the scarce resource.** Practices that spend human judgment wisely — gate placement, sampling, evidence-gated promotion — dominate practices that spend it uniformly.

### 2.3 The Risk Shift

AI participation also changes the risk profile:

- **Volume risk** — more change per unit time means more opportunities for defects to enter, and traditional review capacity saturates.
- **Plausibility risk** — AI-produced artifacts are systematically *plausible*; errors are well-formed and confident, defeating reviewers calibrated on human error patterns.
- **Non-determinism** — the same task may yield different outputs across runs; correctness must be established per output or per statistically characterized behavior, not per tool.
- **Instruction-channel risk** — AI systems act on the content they read; any input becomes a potential instruction channel (see [KA-07](KA-07-security.md)).
- **Provenance risk** — without recorded provenance, the origin and rationale of a change becomes unrecoverable, breaking traceability (EV6).

### 2.4 The Autonomy/Risk Model in Practice

The [Taxonomy](../../Shared/Taxonomy/README.md) defines autonomy levels AL0 — Manual through AL4 — Autonomous and risk tiers RT1 — Minimal through RT4 — Critical, and requires that maximum autonomy be derived from risk tier (RT1 — Minimal→AL4 — Autonomous … RT4 — Critical→AL1 — Assisted by default). In practice this model operates as a three-step discipline applied *per task type*:

```
1. CLASSIFY the task's blast radius            → risk tier (RT1 — Minimal through RT4 — Critical)
2. LOOK UP the maximum permissible autonomy    → AL ceiling (Taxonomy §4)
3. ASSIGN actual autonomy ≤ ceiling, based on  → demonstrated capability
   qualification evidence (AESQS)                (never on convenience)
```

Two corollaries follow. First, autonomy is **earned downward from the ceiling by evidence**, never granted upward by enthusiasm. Second, autonomy assignments are **reversible**: when evidence degrades (evaluation scores fall, incident occurs, capability drift detected — see [KA-12](KA-12-evaluation-improvement.md)), autonomy is reduced.

### 2.5 Accountability Invariant

Per the AIES guiding principles, humans remain accountable for engineering decisions at every autonomy level. What changes across AL0 — Manual through AL4 — Autonomous is the *mechanism* of human control (author → reviewer → supervisor → auditor), never the *locus* of accountability.

## 3. Core Practices

- **Declare before deploying.** [AIES-AEBOK-KA-01-R01] Every AI-performed engineering task MUST have a declared autonomy level (AL0 — Manual through AL4 — Autonomous) and an identified risk tier (RT1 — Minimal through RT4 — Critical) before the AI system performs it, per [AIES-SHARED-02-R01 — Taxonomy, requirement 01](../../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4).
- **Bound the envelope.** [AIES-AEBOK-KA-01-R02] Every agent operating at AL3 — Delegated or AL4 — Autonomous MUST have a defined autonomy envelope — permitted actions, resources, and escalation triggers — recorded in its agent definition (ART-14).
- **Preserve provenance.** [AIES-AEBOK-KA-01-R03] The provenance of every AI-produced or AI-modified artifact MUST be recorded, including the producing actor, autonomy level, and applicable approvals, sufficient to satisfy traceability (EV6) and audit (ART-15).
- **Scale verification with generation.** [AIES-AEBOK-KA-01-R04] Organizations SHOULD ensure that verification capacity (automated gates, evaluation, human review) grows in proportion to AI generation capacity; generation capability MUST NOT be expanded past the point where existing gates saturate.
- **Reason in taxonomy terms.** Practitioners SHOULD express AI-participation decisions using canonical IDs (P/X/AL/RT/ROLE/CL/ART/EV) so decisions are comparable across teams and auditable across time.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Bounded Autonomy Envelope** | Define, per agent and task type, the explicit set of permitted actions and resources; everything outside the envelope escalates to a human. See [catalog](../patterns/README.md#pat-01-bounded-autonomy-envelope). |
| **Risk-Tiered Gating** | Place human approval gates (X07) by risk tier, not uniformly — dense gates on RT3 — Significant through RT4 — Critical paths, automated gates on RT1 — Minimal through RT2 — Moderate. |
| **Evidence-Gated Promotion** | Increase an agent's autonomy for a task type only when qualification evidence (AESQS scores over a defined window) supports it, and record the decision. |
| **Reversible Delegation** | Every autonomy grant carries a pre-defined revocation trigger and rollback path, so delegation failures degrade to lower autonomy rather than to incidents. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Unbounded Agent** | An agent operates without a declared envelope; its effective authority is whatever its credentials permit. See [catalog](../patterns/README.md#apat-01-unbounded-agent). |
| **Autonomy Creep** | Autonomy expands gradually through convenience-driven exceptions rather than evidence, until actual autonomy exceeds the declared level. |
| **Tool-Level Trust** | Trusting "the AI system" globally rather than qualifying capability per task type and risk tier; one impressive demo becomes blanket authority. |
| **Accountability Vacuum** | Outcomes of AI-performed work have no accountable human; incident reviews terminate at "the agent did it." |

## 6. Competency Expectations

| Level | Expectation in KA-01 |
|-------|----------------------|
| **CL1** | States the definitions of autonomy levels, risk tiers, and provenance; classifies straightforward tasks into risk tiers with guidance; explains why review is the bottleneck. |
| **CL2** | Independently assigns risk tiers and autonomy levels for standard task types; writes a bounded autonomy envelope for a routine agent; identifies autonomy creep in a team's practice. |
| **CL3** | Designs the autonomy/risk mapping for a product area, including escalation and revocation rules; adjudicates contested risk-tier classifications; coaches teams on evidence-gated promotion. |
| **CL4** | Sets organizational autonomy policy; evaluates trade-offs between delivery throughput and verification capacity at portfolio scale; evolves the organization's model as AI capability shifts, through governed change (X04). |

## Related Documents

- Every other KA builds on this one; read KA-01 first.
- Gate design and human oversight mechanics: [KA-11 Human-AI Collaboration & Oversight (AIES-AEBOK-KA-11 — Knowledge Area — Human-AI Collaboration)](KA-11-human-ai-collaboration.md).
- Evidence and drift detection that feed autonomy decisions: [KA-12 Evaluation & Continuous Improvement (AIES-AEBOK-KA-12 — Knowledge Area — Evaluation and Improvement)](KA-12-evaluation-improvement.md).
- Qualification evidence and scoring: [AESQS (AIES-AESQS-00 — Qualification Standard)](../../AESQS/README.md). Operating-model enforcement of these concepts: [AIES-AEOS-00 — AEOS — AI Engineering Operating System](../../AEOS/README.md).
- Canonical scales referenced throughout: [Taxonomy (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

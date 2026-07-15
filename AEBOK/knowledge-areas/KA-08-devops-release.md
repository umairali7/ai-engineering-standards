# KA-08 — DevOps & Release Engineering

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-08 |
| **Status** | Review |
| **Audience** | Engineers · Platform teams |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-08 covers DevOps (P12) and Release (P13) in AI-native delivery. In a pre-AI organization, the pipeline accelerates change that humans have already vetted. In an AI-native organization the pipeline's role inverts: **it is the enforcement layer** — the place where autonomy envelopes, risk-tier policy, provenance requirements, and quality gates stop being documentation and become physics. An agent's effective autonomy is whatever the pipeline permits, regardless of what any policy document declares. KA-08 defines how to build pipelines that function as guardrails, and how to release AI-produced change safely at AI-produced volume.

## 2. Key Concepts

- **Pipelines as guardrails.** A guardrail must be enforced outside the model ([Glossary](../../Shared/Glossary/README.md)). The pipeline is the natural guardrail substrate for change flow: it can verify provenance, enforce review evidence, run tier-appropriate gates, and refuse promotion — deterministically, for every change, at any volume. Policy that the pipeline does not enforce is policy that agents can (and eventually will) bypass by accident.
- **The pipeline is also an AI work surface.** Pipeline definitions (ART-09) are themselves code that AI can produce and modify — and they are RT3 by nature, since a pipeline change can disable the very gates that constrain agents. Pipeline change therefore gets *lower* autonomy ceilings than the product change flowing through it. Gates that are modifiable by the actors they gate are not controls.
- **Promotion on evidence, not on actor.** A change earns promotion by the evidence attached to it — provenance (ART-06), passing verification (ART-07), required approvals (ART-15) — evaluated against the policy for its risk tier. Evidence-gated promotion makes the human/AI distinction operationally irrelevant at the gate: the gate checks evidence, and the evidence requirements differ by tier and autonomy level, not by sympathy for the author.
- **Release as risk-tier instrument.** Progressive delivery (canary, staged rollout, feature flags, automated rollback) is what makes higher autonomy tolerable: it converts "is this change correct?" (hard, pre-release) into "is this change misbehaving?" (observable, post-release, reversible). The reversibility of a change is part of its effective risk tier — irreversible changes are RT3+ by default.
- **Velocity asymmetry.** Agents produce change faster than humans can operate manual release processes. Every manual step in the path to production becomes either a bottleneck (queues grow) or a casualty (someone "temporarily" removes it). The resolution is to automate the *checking*, never to remove the *check*.
- **Environment integrity.** Agents act on the environments they can reach. Build and deploy environments need to distinguish what agents may touch (ephemeral build workspaces) from what is off-limits to them (signing keys, production credentials, gate configuration) — a topology decision made with [KA-03](KA-03-architecture-design.md) and [KA-07](KA-07-security.md).

## 3. Core Practices

- **Encode tier policy as pipeline gates.** [AIES-AEBOK-KA-08-R01] The promotion requirements for each risk tier (verification evidence, review approvals, security checks) MUST be encoded as automated pipeline gates; a change without the evidence required for its tier MUST NOT be promotable by any actor, human or AI.
- **Verify provenance at the gate.** [AIES-AEBOK-KA-08-R02] Pipelines MUST reject changes lacking machine-readable provenance (producing actor, autonomy level, work item — per [AIES-AEBOK-KA-05-R02](KA-05-implementation.md)) and MUST record gate outcomes to the audit trail (ART-15).
- **Protect the gates from the gated.** [AIES-AEBOK-KA-08-R03] Modifications to pipeline definitions, gate configuration, and promotion policy MUST be classified RT3 or higher, MUST require human approval (ROLE-13), and MUST NOT be executable at AL3+ by agents whose changes those gates evaluate.
- **Deploy AI-produced change progressively.** [AIES-AEBOK-KA-08-R04] RT2+ AI-produced changes SHOULD be released through progressive delivery with automated health evaluation and rollback; RT3+ changes MUST have a tested rollback path before promotion, or — where the change is inherently irreversible — a tested containment and recovery plan in its place.
- **Match release automation to change volume.** Teams SHOULD automate release mechanics (notes drafting from work items, artifact assembly, release records ART-10) — with AI assistance where useful — so that human release attention concentrates on go/no-go judgment, not ceremony.
- **Keep environments least-privilege.** Build/deploy environments reachable by agents SHOULD be ephemeral and task-scoped; signing, production credentials, and gate configuration live outside agent reach via brokered access ([KA-07](KA-07-security.md)).

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Evidence-Gated Promotion** | Promotion decisions evaluate attached evidence against tier policy mechanically; no evidence, no promotion — regardless of author ([catalog](../patterns/README.md#pat-02-evidence-gated-promotion)). |
| **Gate Custody Separation** | The pipeline and gate configuration are owned and modified through a channel independent of the agents whose work they gate. |
| **Progressive Exposure** | Canary and staged rollout with automated health checks convert release risk into observable, reversible increments — the release-side complement of sampling review. |
| **Auto-Rollback Tripwire** | Pre-agreed telemetry thresholds trigger automatic rollback of a rolling release without waiting for human diagnosis; humans investigate after safety is restored. |
| **Release Evidence Bundle** | Each release record (ART-10) automatically aggregates the provenance, verification, and approval evidence of everything it ships — the audit story assembles itself. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Advisory Gate** | Gate failures can be waived ad hoc ("just this once") without recorded risk acceptance; under agent-scale volume, the exception becomes the path. |
| **Self-Modifying Guardrail** | Agents can modify the pipeline that gates their own changes; the autonomy envelope is now self-defined and the control is fiction. |
| **Manual Bottleneck Denial** | A human step designed for five changes a week receives fifty a day; either the queue destroys delegation's value or the step gets skipped — both silently. |
| **Big-Bang AI Release** | Accumulated AI-produced changes ship in one large, non-progressive release; when something misbehaves, attribution across dozens of changes is archaeology. |
| **Green-Pipeline Complacency** | "It passed the pipeline" is treated as a complete quality claim while the gates themselves are stale or weak; pipeline strength is never itself evaluated ([KA-12](KA-12-evaluation-improvement.md)). |

## 6. Competency Expectations

| Level | Expectation in KA-08 |
|-------|----------------------|
| **CL1** | Explains why pipelines are the enforcement layer for autonomy policy; reads gate configuration and explains what each gate enforces; follows progressive-release procedure. |
| **CL2** | Independently implements tier-policy gates and provenance checks in standard pipelines; configures progressive delivery with rollback for routine services. |
| **CL3** | Designs the gate architecture for a product area, including custody separation and evidence schemas; tunes release strategies to change-volume and risk profiles; leads pipeline incident reviews. |
| **CL4** | Sets organizational promotion and release policy; evaluates gate effectiveness portfolio-wide against escape and rollback data; evolves the enforcement layer as autonomy levels and change volume grow. |

## Related Documents

- The provenance and review evidence gates consume: [KA-05 AI-Assisted Implementation (AIES-AEBOK-KA-05)](KA-05-implementation.md); the verification they execute: [KA-06 Testing & Quality (AIES-AEBOK-KA-06)](KA-06-testing-quality.md).
- Credential and environment security for pipelines: [KA-07 Security Engineering (AIES-AEBOK-KA-07)](KA-07-security.md).
- Post-release health signals and rollback triggers: [KA-09 Operations & Observability (AIES-AEBOK-KA-09)](KA-09-operations-observability.md).
- Where human go/no-go judgment fits: [KA-11 Human-AI Collaboration & Oversight (AIES-AEBOK-KA-11)](KA-11-human-ai-collaboration.md).
- DevOps role (ROLE-09) and gate governance: [AEOS (AIES-AEOS-00)](../../AEOS/README.md); pipeline reference architecture: [AEAR (AIES-AEAR-00)](../../AEAR/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

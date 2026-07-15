# KA-03 — Architecture & Design in AI-Native Delivery

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-03 |
| **Status** | Review |
| **Audience** | Architects · Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-03 covers Solution Analysis (P06) and Architecture (P07) in AI-native delivery. It addresses two distinct questions. First, how AI participates in architecture work itself — comparing solution options, drafting designs, stress-testing decisions. Second, and distinctively for AIES: **how to architect systems so that AI agents can work on them safely** — because in AI-native delivery, the system's structure is also the primary safety mechanism constraining what AI-produced change can do. Architecture becomes part of the control plane for autonomy.

## 2. Key Concepts

- **Architecture as autonomy enabler.** The maximum autonomy that can be safely granted for changes to a system is a function of the system's structure. A system with strong module boundaries, enforced contracts, comprehensive automated verification, and reversible deployment supports AL3 work; a monolith with implicit coupling and manual verification caps agents at AL1–AL2 regardless of their capability. Raising the safe autonomy ceiling is an architectural outcome, not a tooling purchase.
- **Agent-legible systems.** AI agents work from the system's *recorded* knowledge: code, contracts, ADRs (ART-04), conventions, and context assets (ART-13). Structure and intent that live only in engineers' heads are invisible to agents. A system is *agent-legible* when its boundaries, invariants, and conventions are explicit, discoverable, and machine-checkable.
- **Blast-radius topology.** Risk tiers (RT1–RT4) attach to *parts* of a system, not to the system as a whole. Architecture determines the topology: which components are RT4 (payments, auth, data deletion), which are RT2 (internal tooling), and — critically — whether the boundaries between them are enforced or merely conventional. Well-drawn boundaries let most change happen in low-tier zones at higher autonomy.
- **Contract-first decomposition.** Explicit, versioned, machine-verifiable interfaces (API schemas, typed contracts, invariant checks) are the mechanism that lets an agent change a component's inside without needing to understand — or endanger — the whole. Contracts convert "review everything" into "verify the contract."
- **Decision capital.** ADRs are the highest-value context asset for AI participation in design: they encode *why*, which prevents both agents and humans from relitigating or silently reversing settled decisions. In AI-native delivery, an unrecorded decision is a decision that will eventually be undone by a well-meaning agent.
- **AI in the design loop.** At P06, AI is well-suited (typically AL1–AL2) to enumerating solution options, drafting trade-off analyses, and challenging a proposed design against quality attributes (X11–X13). Selection among options is a human decision (ROLE-05) because it binds intent and accepts risk.

## 3. Core Practices

- **Declare the risk topology.** [AIES-AEBOK-KA-03-R01] Architects (ROLE-05) MUST classify system components by risk tier (RT1–RT4) and record the classification so that autonomy assignments and gate placement (see [KA-11](KA-11-human-ai-collaboration.md)) can be derived from it.
- **Enforce boundaries technically.** [AIES-AEBOK-KA-03-R02] Boundaries between risk zones MUST be technically enforced (access controls, separate deployables, contract checks in CI) rather than purely conventional, wherever agents operate at AL2 or above within them.
- **Record decisions as ADRs.** [AIES-AEBOK-KA-03-R03] Architecturally significant decisions MUST be recorded as ADRs (ART-04) and kept available to AI systems as context assets; superseded ADRs MUST be marked as such rather than deleted.
- **Design for agent legibility.** New designs SHOULD make invariants, conventions, and component responsibilities explicit and machine-discoverable (typed contracts, schema definitions, convention documents in the [context store](KA-10-context-knowledge.md)); implicit knowledge SHOULD be progressively captured for existing systems.
- **AI-assisted option analysis.** At P06, teams SHOULD use AI to broaden the option space and draft comparative analyses, with the selecting decision and its rationale made and recorded by a human architect. [AIES-AEBOK-KA-03-R04] AI-drafted architecture analyses MUST identify their assumptions and information sources, and MUST be reviewed by ROLE-05 before informing a recorded decision.
- **Verify designs adversarially.** Use a separate AI pass to attack a proposed design — failure modes, scaling limits, security posture (with [KA-07](KA-07-security.md)), operational burden — before human design review, so review time concentrates on substantive findings.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Risk-Zoned Architecture** | Partition the system into explicit risk zones with enforced boundaries; derive per-zone autonomy ceilings from the zone's tier. |
| **Contract-Bounded Change** | Require every agent-modifiable component to sit behind a machine-verifiable contract; agents may change implementations freely at their AL, but contract changes escalate. |
| **ADR-as-Context** | Maintain ADRs as first-class context assets (ART-13) consumed by agents before design or implementation work, closing the "why" gap. |
| **Design Red Team** | An adversarial AI critique of every significant design precedes human review; findings are dispositioned in the ADR. |
| **Strangler for Legibility** | Incrementally wrap illegible legacy components behind explicit contracts, expanding the portion of the system where higher autonomy is safe. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Conventional Boundary** | Risk zones separated only by team agreement ("agents shouldn't touch that directory"); an agent with repository-wide write access eventually crosses. |
| **Tribal Architecture** | Critical invariants exist only in senior engineers' heads; agents (and new humans) violate them systematically, and each violation is "reviewed" too late. |
| **Decision Amnesia** | Undocumented decisions get relitigated and reversed by AI-assisted refactoring; the system oscillates between architectures. |
| **Generated Architecture Acceptance** | AI-drafted designs are adopted without human trade-off analysis because they look complete; the organization discovers the unconsidered constraint in production. |
| **Uniform Risk Assumption** | Treating the entire system as one risk tier — either paralyzing all AI work at RT4 caution or endangering critical components at RT2 convenience. |

## 6. Competency Expectations

| Level | Expectation in KA-03 |
|-------|----------------------|
| **CL1** | Explains why architecture constrains safe autonomy; reads a risk-zone map and identifies which zones permit which AL; understands the purpose of ADRs as agent context. |
| **CL2** | Applies contract-bounded change within an existing architecture; writes ADRs suitable for AI consumption; uses AI for option enumeration and design critique in standard designs. |
| **CL3** | Designs risk-zoned architectures for new systems; leads legibility retrofits of legacy systems; adjudicates boundary and tier disputes; reviews AI-drafted designs for unstated assumptions. |
| **CL4** | Sets architectural standards that govern autonomy ceilings across a portfolio; evaluates organization-wide trade-offs between decomposition cost and autonomy benefit; evolves the reference architecture as agent capability changes, in coordination with [AEAR](../../AEAR/README.md). |

## Related Documents

- Autonomy/risk model this KA operationalizes structurally: [KA-01 (AIES-AEBOK-KA-01)](KA-01-foundations.md).
- Upstream inputs (requirements, constraints): [KA-02 (AIES-AEBOK-KA-02)](KA-02-business-requirements.md); downstream execution within these structures: [KA-04 (AIES-AEBOK-KA-04)](KA-04-planning-decomposition.md), [KA-05 (AIES-AEBOK-KA-05)](KA-05-implementation.md).
- Security architecture and threat modeling for AI-native delivery: [KA-07 (AIES-AEBOK-KA-07)](KA-07-security.md).
- Making ADRs and conventions consumable: [KA-10 Context & Knowledge Management (AIES-AEBOK-KA-10)](KA-10-context-knowledge.md).
- Platform-level embodiments of these principles: [AEAR (AIES-AEAR-00)](../../AEAR/README.md); operating-model enforcement: [AEOS (AIES-AEOS-00)](../../AEOS/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

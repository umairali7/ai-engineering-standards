# Glossary

| | |
|---|---|
| **Document ID** | AIES-SHARED-01 |
| **Status** | Review |
| **Audience** | All readers |

Canonical definitions for all terms used across AIES. Modules MUST use these terms as defined here and MUST NOT redefine them. Classification scales (autonomy levels, risk tiers, competency levels, roles) are defined in the [Taxonomy (AIES-SHARED-02)](../Taxonomy/README.md).

The key words "MUST" and "MUST NOT" in this document are to be interpreted as described in RFC 2119.

---

## A

**Agent (AI Agent)**
A software system that uses one or more AI models to perform tasks with some degree of autonomy: interpreting goals, selecting actions (including tool calls), and producing artifacts. An agent's authority is bounded by its declared autonomy level.

**Agent Definition**
The versioned specification of an agent: its role, capabilities, tools, autonomy level, guardrails, and escalation rules (artifact ART-14).

**AI-Native Software Engineering**
An engineering practice in which AI participation is designed into the SDLC deliberately — with defined roles, autonomy levels, quality gates, and audit trails — rather than adopted ad hoc.

**AI Safety**
The cross-cutting discipline of preventing AI systems from causing unintended harm, including alignment of behavior with intent, containment of failures, and preservation of human control.

**Approval Gate**
A defined checkpoint at which a human (ROLE-13) must explicitly authorize work to proceed. Gates are placed according to risk tier.

**Audit Trail**
An immutable, queryable record (ART-15) linking every significant action — human or AI — to its actor, inputs, rationale, and outputs.

**Autonomy Envelope**
The bounded set of actions, resources, and decisions an agent may take without escalation. Exceeding the envelope requires escalation to a human or higher-authority process.

**Autonomy Level (AL0–AL4)**
See [Taxonomy §3](../Taxonomy/README.md#3-autonomy-levels-al0al4).

## C

**Capability**
A demonstrable ability of a person, team, or AI system to produce a defined engineering outcome to a defined quality, measured through evaluation (AESQS).

**Capability Scoring**
The AESQS method of quantifying capability along the evaluation dimensions EV1–EV6.

**Competency**
A combination of knowledge, skill, and judgment that enables reliable performance in a role. Measured on the CL1–CL4 scale.

**Context Asset**
Curated information supplied to an AI system to ground its work — codebase knowledge, standards, conventions, prior decisions (artifact ART-13).

**Cross-Cutting Domain (X01–X15)**
A concern that applies across all SDLC phases. See [Taxonomy §2](../Taxonomy/README.md#2-cross-cutting-domains-x01x15).

## E

**Escalation**
The act of transferring a decision from an AI system to a human (or from a lower to a higher authority) when a task exceeds the autonomy envelope, confidence threshold, or risk tier.

**Evaluation**
A repeatable, evidence-producing procedure for measuring the quality of an engineering output or the capability of a performer.

**Evaluation Dimension (EV1–EV6)**
See [Taxonomy §8](../Taxonomy/README.md#8-evaluation-dimensions-ev1ev6).

**Evidence**
Recorded, verifiable data supporting a claim — test results, evaluation scores, review records, telemetry. AIES recommendations and qualifications MUST be evidence-driven.

## G

**Governance**
The system of policies, roles, decision rights, and controls that direct and constrain AI participation in engineering.

**Guardrail**
A technical or procedural control that prevents an agent from taking a class of action regardless of its instructions (e.g., blocked deletion of production data). Guardrails are enforced outside the model.

## H

**Human Approver**
The human role (ROLE-13) accountable for authorizing gated actions. Cannot be delegated to an AI system.

**Human Oversight**
The cross-cutting domain (X07) ensuring humans retain visibility into, and authority over, AI activity — via gates, sampling, monitoring, and audit.

**Human-AI Pair**
A working arrangement in which a human and an AI system jointly hold a role, with the human accountable for outcomes.

## O

**Operating Model**
The definition of how work flows through roles, gates, and artifacts in an AI-native engineering organization (defined by AEOS).

## P

**Provenance**
The recorded origin of an artifact: who or what produced it, from what inputs, under which autonomy level and approvals.

## Q

**Qualification**
A formal, evidence-based determination that a person, team, or AI system meets a defined capability threshold for a defined scope of work (AESQS). Qualifications are scoped, versioned, and revocable.

**Quality Gate**
An automated or manual checkpoint that blocks progression of an artifact until defined criteria are met (tests pass, review complete, security scan clean).

## R

**Reference Architecture**
A vendor-neutral, reusable architectural template describing components, responsibilities, and interactions for a class of systems (AEAR).

**Risk Tier (RT1–RT4)**
See [Taxonomy §4](../Taxonomy/README.md#4-risk-tiers-rt1rt4).

**Role**
A named set of responsibilities within the SDLC (ROLE-01 … ROLE-14), staffable by a human, an AI agent, or a human-AI pair — except where AIES mandates a human.

## S

**SDLC Phase (P01–P16)**
See [Taxonomy §1](../Taxonomy/README.md#1-sdlc-phases-p01p16).

**Standard**
A normative AIES document containing requirements expressed in RFC 2119 language.

## T

**Traceability**
The property that every artifact and decision can be followed backward to its requirements, rationale, actors, and approvals, and forward to its consequences.

## V

**Vendor Neutrality**
The AIES principle that standards describe engineering capabilities and controls independent of any specific AI model, product, or provider.

---

## Adding Terms

New terms are proposed via pull request per [CONTRIBUTING.md](../../CONTRIBUTING.md). A term is added only if it is used by at least two modules or is normatively load-bearing.

## Related Documents

- [Taxonomy (AIES-SHARED-02)](../Taxonomy/README.md) — the classification scales these terms reference
- [Shared Standards index (AIES-SHARED-00)](../README.md)
- [Writing Standard (AIES-STD-03)](../../docs/standards/writing-standard.md) — glossary discipline rules for authors

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

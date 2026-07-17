# AESQS — AI Engineering SDLC Qualification Standard

| | |
|---|---|
| **Document ID** | AIES-AESQS-00 |
| **Status** | Review |
| **Audience** | All readers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

AESQS answers the second foundational question of AIES:

> **How do we objectively evaluate AI Engineering capability?**

Organizations adopting AI-native software engineering face the same problem twice:

- **For humans:** how do we know an engineer is competent to work in an AI-native SDLC — to direct, review, and take accountability for AI-produced work?
- **For AI systems:** how do we know an agent is capable enough to be trusted with a given class of work — and how much [autonomy](../Shared/Glossary/README.md) that capability justifies?

AESQS defines a single qualification standard that applies to **both humans and AI systems**. The evaluation dimensions ([EV1–EV6](../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6)), competency levels ([CL1–CL4](../Shared/Taxonomy/README.md#6-competency-levels-cl1cl4)), and process are shared; the evidence types and assessment methods differ where the nature of the subject demands it.

## 2. The Qualification Model at a Glance

A **qualification** is a formal, evidence-based determination that a person, team, or AI system meets a defined capability threshold for a defined scope of work. Every AESQS qualification is:

- **Scoped** — to a role × SDLC phases × risk tier (never "qualified in general");
- **Versioned** — bound to a specific version of the competency framework and, for AI systems, to a specific agent definition and model configuration;
- **Evidence-based** — grounded in scored artifacts, assessments, and evaluation data, never in reputation or vendor claims;
- **Revocable** — subject to ongoing verification, revision, and revocation.

```
┌──────────────────────┐
│ Competency Framework │  What must the subject be able to do,
│     (AIES-AESQS-CF-01)    │  at which CL level, for this scope?
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│      Evaluation      │  Gather evidence: work products, scenarios,
│     (AIES-AESQS-ER-01)    │  golden-task suites, live observation —
└──────────┬───────────┘  scored on EV1–EV6 rubrics.
           ▼
┌──────────────────────┐
│       Scoring        │  Aggregate per-dimension scores with
│     (AIES-AESQS-CS-01)    │  risk-tier weighting and minimum gates.
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Qualification        │  Peer-reviewed decision: grant / deny /
│ Decision             │  grant-with-conditions, mapped to CL and
│ (AIES-AESQS-QP-01,        │  (for AI systems) permissible AL.
│  AIES-AESQS-PR-01)        │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Ongoing Verification │  Score-drift monitoring, sampling,
│ (AIES-AESQS-CS-01 §7)     │  incident feeds, validity windows.
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Revision /           │  Re-qualification on triggers; suspension
│ Revocation           │  and revocation when integrity fails;
│ (AIES-AESQS-RR-01)        │  appeals; full audit trail (ART-15).
└──────────────────────┘
```

The loop is continuous: ongoing verification feeds back into evaluation, and revisions of the competency framework re-open existing qualifications.

## 3. Normative Anchors

- [AIES-AESQS-00-R01] Every qualification granted under AESQS MUST be scoped to a role ([ROLE-01…ROLE-14](../Shared/Taxonomy/README.md#5-ai-engineering-roles)), a set of SDLC phases ([P01–P16](../Shared/Taxonomy/README.md#1-sdlc-phases-p01p16)), and a maximum risk tier ([RT1–RT4](../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)).
- [AIES-AESQS-00-R02] Qualification decisions MUST be based on evidence evaluated against the rubrics in [AIES-AESQS-ER-01](evaluation-rubrics.md) and scored per [AIES-AESQS-CS-01](capability-scoring.md).
- [AIES-AESQS-00-R03] For AI systems, an [autonomy level](../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4) above AL1 MUST NOT be granted for any task type without a current, in-scope AESQS qualification.
- [AIES-AESQS-00-R04] Every qualification MUST be revocable, and every grant, revision, suspension, and revocation MUST produce an audit trail record (ART-15).

## 4. Document Map

| Document | ID | Purpose |
|----------|----|---------|
| [Competency Framework](competency-framework.md) | AIES-AESQS-CF-01 | Competency areas, role requirements, CL1–CL4 descriptors for humans and AI systems |
| [Qualification Process](qualification-process.md) | AIES-AESQS-QP-01 | End-to-end process: scoping, evidence, assessment methods, decision, granting, validity, re-qualification |
| [Evaluation Rubrics](evaluation-rubrics.md) | AIES-AESQS-ER-01 | Scoring anchors for EV1–EV6, worked example, inter-rater reliability |
| [Capability Scoring](capability-scoring.md) | AIES-AESQS-CS-01 | Weighting, aggregation, minimum gates, thresholds to CL and AL, statistics, drift monitoring |
| [Peer Review](peer-review.md) | AIES-AESQS-PR-01 | Reviewer qualifications, independence, protocol, review records, disagreement handling |
| [Revision & Revocation](revision-and-revocation.md) | AIES-AESQS-RR-01 | Revision triggers, revocation criteria and process, appeals, audit requirements |

## 5. Relationship to Other Modules

```
        AEBOK ──────────────► AESQS ──────────────► AEOS
   defines the knowledge   evaluates capability   consumes qualifications
   and practices being     against that knowledge to grant autonomy and
   tested                                         staff roles
                              ▲
                              │ prepares candidates for
                            AECT
```

| Module | Relationship |
|--------|--------------|
| [AEBOK](../AEBOK/README.md) | Defines the knowledge areas and practices that AESQS competencies are derived from. AESQS tests capability **against** AEBOK; it does not restate its content. |
| [AEOS](../AEOS/README.md) | Consumes qualifications. AEOS staffing and gating rules require in-scope qualifications; for AI systems, the qualification is what justifies granting an autonomy level within a risk tier. |
| [AECT](../AECT/README.md) | Prepares candidates. AECT learning paths, labs, and exams target the competency levels defined here; AECT certifications reference AESQS qualification scopes. |
| [Shared Standards](../Shared/README.md) | Supplies the canonical [Glossary](../Shared/Glossary/README.md) and [Taxonomy](../Shared/Taxonomy/README.md). AESQS introduces no competing scales. |

## 6. Who Uses AESQS

| Audience | Use |
|----------|-----|
| Engineering leadership | Decide who — human or AI — may do what work, at what risk tier |
| Qualification authorities & assessors | Run evaluations and issue defensible, auditable decisions |
| Platform & governance teams | Wire qualification checks into gates, agent registries, and autonomy policies |
| Engineers and teams | Understand what evidence earns a qualification and how to retain it |
| AI system owners | Qualify agents before requesting autonomy; monitor for drift and re-qualify |

---

## Related Documents

- [AIES-AESQS-CF-01 — Competency Framework](competency-framework.md)
- [AIES-AESQS-QP-01 — Qualification Process](qualification-process.md)
- [AIES-AESQS-ER-01 — Evaluation Rubrics](evaluation-rubrics.md)
- [AIES-AESQS-CS-01 — Capability Scoring](capability-scoring.md)
- [AIES-AESQS-PR-01 — Peer Review](peer-review.md)
- [AIES-AESQS-RR-01 — Revision & Revocation](revision-and-revocation.md)
- [AIES-AEBOK-00 — AEBOK Module Overview](../AEBOK/README.md) · [AIES-AEOS-00 — AEOS Module Overview](../AEOS/README.md) · [AIES-AECT-00 — AECT Module Overview](../AECT/README.md)
- [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md) · [Glossary (AIES-SHARED-01)](../Shared/Glossary/README.md)
- **External alignment:** ISO/IEC TS 42119-2 (testing of AI) and ISO/IEC 25059 (AI quality model) — AESQS is an executable, risk-tiered instantiation of the former, and EV1–EV6 map to the latter; see [Standards Crosswalk §3a (AIES-DOC-07)](../docs/CROSSWALK.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

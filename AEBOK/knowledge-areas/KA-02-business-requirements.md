# KA-02 — AI-Assisted Business & Requirements Analysis

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-02 |
| **Status** | Review |
| **Audience** | Engineers · Engineering leadership |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-02 covers AI participation in the upstream phases — Business Strategy (P01), Business Analysis (P02), Product Management (P03), User Experience (P04), and Requirements Engineering (P05). These phases produce the artifacts that direct all downstream work (ART-01, ART-02, ART-03), so errors here are the most expensive in the lifecycle: a defect in a requirement propagates into architecture, code, tests, and operations. AI can dramatically accelerate analysis work, but the upstream phases are also where **human intent enters the system** — the one thing AI cannot supply. KA-02 defines how to gain the acceleration without diluting or fabricating intent.

## 2. Key Concepts

- **Intent is the human contribution.** AI systems can elicit, structure, cross-check, and draft; they cannot decide what the organization wants or what users need. Every upstream artifact has an intent core (goals, priorities, trade-off decisions) that only humans can supply, and an expression layer (structure, wording, completeness checks) where AI assists effectively.
- **Plausible-requirement risk.** AI-drafted requirements are fluent and internally consistent even when they are wrong — they encode the *typical* system, not *your* system. Fluency reads as validation; unvalidated AI-drafted requirements are the upstream form of plausibility risk (see [KA-01 §2.3](KA-01-foundations.md)).
- **Elicitation vs. generation.** Using AI to *elicit* (generate questions, surface ambiguities, identify missing stakeholders and edge cases) is low-risk and high-value. Using AI to *generate* requirements content from thin input manufactures fictional stakeholder needs. The direction of information flow matters: AI should pull intent out of humans, not push synthetic intent in.
- **Traceable derivation.** Each requirement (ART-02) traces to a source: a stakeholder statement, business objective (ART-01), research finding, or explicit product decision. AI assistance makes volume cheap, which makes untraceable requirements cheap — so traceability discipline (EV6) matters *more* upstream in AI-native delivery, not less.
- **Risk-tier awareness upstream.** Most analysis drafting is RT1 — Minimal through RT2 — Moderate (revisable documents behind review). Requirements that encode regulatory commitments, safety properties, or contractual obligations are RT3 — Significant through RT4 — Critical and carry correspondingly lower autonomy ceilings.

## 3. Core Practices

- **AI-assisted elicitation.** Use AI (typically AL1 — Assisted through AL2 — Collaborative) to prepare interviews, generate candidate questions, detect ambiguity and contradiction in stakeholder input, and propose edge cases for human confirmation. ROLE-02/ROLE-03 remain the deciders.
- **Structured drafting with human intent anchors.** [AIES-AEBOK-KA-02-R01] AI-drafted business and requirements artifacts (ART-01, ART-02, ART-03) MUST be validated by an accountable human (ROLE-02, ROLE-03, or ROLE-04 as appropriate) before they are used as input to downstream phases (P06+).
- **Source traceability.** [AIES-AEBOK-KA-02-R02] Every requirement in an AI-assisted requirements set MUST be traceable to a human-confirmed source (stakeholder input, business objective, research evidence, or recorded product decision); requirements without a confirmable source MUST be flagged and resolved, not silently retained.
- **Consistency and completeness checking.** AI SHOULD be used to cross-check requirement sets for contradiction, duplication, ambiguity, and gaps against the business case — this is one of the highest-yield, lowest-risk AI applications in P05.
- **Assumption surfacing.** [AIES-AEBOK-KA-02-R03] When AI drafts or refines upstream artifacts, assumptions the AI introduced MUST be explicitly enumerated in the artifact and confirmed or rejected by a human before approval.
- **Analysis provenance.** Record which parts of upstream artifacts were AI-drafted versus human-authored (provenance, ART-15-linked), so downstream reviewers can calibrate scrutiny.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Socratic Elicitation** | Direct AI to generate probing questions and challenge scenarios for stakeholders rather than answers; humans supply the content, AI supplies the coverage. |
| **Red-Team Requirement Review** | A second AI pass adversarially critiques a requirement set (ambiguity, conflict, missing NFRs, untestability) before human review, so human attention lands on real issues. |
| **Assumption Ledger** | Every AI-introduced assumption is captured in a ledger attached to the artifact; approval requires disposition of every entry. |
| **Traceable Derivation Chain** | Each requirement carries links back to source statements and forward to design elements and tests, maintained as part of the artifact, enabling EV6 audits across P01–P10. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Synthetic Stakeholder** | AI-generated "user needs" with no human source enter the requirements set and are built; the team ships a product for users who do not exist. |
| **Fluency-as-Validation** | Well-written AI-drafted requirements pass review because they read professionally; correctness of content is never established. See [catalog](../patterns/README.md#apat-06-fluency-as-validation). |
| **Requirements Flooding** | Cheap generation produces hundreds of low-value requirements that bury the critical few and saturate review capacity (volume risk in P05 form). |
| **Intent Laundering** | A human's vague idea goes through AI expansion and returns looking authoritative; nobody can later distinguish decided intent from generated filler. |

## 6. Competency Expectations

| Level | Expectation in KA-02 |
|-------|----------------------|
| **CL1** | Uses AI to check a requirement set for ambiguity and duplication with guidance; explains why AI-drafted requirements need source validation. |
| **CL2** | Runs AI-assisted elicitation and drafting for standard features end to end; maintains an assumption ledger; produces traceable requirement sets independently. |
| **CL3** | Designs the team's AI-assisted analysis workflow, including where AL1 — Assisted vs. AL2 — Collaborative applies; adjudicates requirement provenance disputes; coaches analysts on plausible-requirement risk. |
| **CL4** | Sets organizational policy for AI participation in upstream phases, including RT classification of requirement classes (regulatory, safety, contractual); evaluates the practice's effect on downstream defect rates via [KA-12](KA-12-evaluation-improvement.md) feedback. |

## Related Documents

- Foundation concepts (autonomy, risk, provenance): [KA-01 (AIES-AEBOK-KA-01 — Knowledge Area — Foundations)](KA-01-foundations.md).
- Downstream consumption of these artifacts: [KA-03 Architecture & Design (AIES-AEBOK-KA-03 — Knowledge Area — Architecture Design)](KA-03-architecture-design.md) and [KA-04 Planning (AIES-AEBOK-KA-04 — Knowledge Area — Planning and Decomposition)](KA-04-planning-decomposition.md).
- Making organizational knowledge available for grounded analysis: [KA-10 Context & Knowledge Management (AIES-AEBOK-KA-10 — Knowledge Area — Context and Knowledge)](KA-10-context-knowledge.md).
- Gate and review design for upstream approvals: [KA-11 Human-AI Collaboration & Oversight (AIES-AEBOK-KA-11 — Knowledge Area — Human-AI Collaboration)](KA-11-human-ai-collaboration.md).
- Role responsibilities (ROLE-02, ROLE-03, ROLE-04): [AIES-AEOS-00 — AEOS — AI Engineering Operating System](../../AEOS/README.md); assessment of analysis competency: [AESQS (AIES-AESQS-00 — Qualification Standard)](../../AESQS/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

# Vision

| | |
|---|---|
| **Document ID** | AIES-DOC-02 |
| **Status** | Review |
| **Audience** | All readers |

Where AI Engineering is heading, why a standard is needed, and what the world looks like when AIES succeeds.

---

## 1. The Transformation Underway

Software engineering is undergoing its largest structural change since the move to iterative delivery. AI systems no longer merely autocomplete code: they analyze requirements, propose architectures, implement features, write and execute tests, triage incidents, and operate pipelines. Engineering work is shifting from *typing artifacts* to *directing, reviewing, and governing the production of artifacts* — some produced by humans, some by AI, most by both.

This shift changes the economics and the risk profile of software delivery simultaneously:

- **Throughput rises** — more artifacts are produced per engineer per unit time.
- **Review load explodes** — human attention becomes the scarce resource, and it must be spent where risk concentrates.
- **Provenance blurs** — without deliberate controls, organizations lose the ability to say who (or what) made a decision and why.
- **Capability varies wildly** — the same AI tooling performs brilliantly on one task class and unreliably on another, and the boundary moves with every model generation.

Organizations that manage this transition deliberately will compound the throughput gains. Organizations that adopt AI ad hoc will accumulate untraceable risk at the same rate they accumulate code.

## 2. The Gap

Every mature engineering discipline has a reference standard: project managers have PMBOK, business analysts have BABOK, enterprise architects have TOGAF, testers have ISTQB, application security has OWASP. AI *governance* has emerging standards too — ISO/IEC 42001 for AI management systems, NIST AI RMF for AI risk.

But there is **no vendor-neutral standard for AI participation across the software development life cycle**. Nothing that answers, in engineering terms:

- What must an engineer know to direct AI-native delivery? (a body of knowledge)
- How is the capability of an AI system — or a human–AI pair — objectively evaluated for a class of engineering work? (a qualification standard)
- How much authority may an AI system hold for a given task, and who remains accountable? (an operating model)
- What should the platforms that host this work look like? (a reference architecture)
- How are engineers trained and credentialed in this discipline? (a certification framework)

Existing AI frameworks govern AI *systems in general*. Existing engineering frameworks assume *human* performers. The intersection — AI as a governed participant in engineering — is unstandardized. That intersection is where AIES lives.

## 3. The Desired End State (Five Years)

By the early 2030s, the AIES project intends the following to be true:

1. **AI Engineering is a recognized discipline.** It has a name, a body of knowledge, a competency ladder, and a professional identity — the way software testing and business analysis do today.
2. **AIES is the reference standard.** When an organization asks "how should AI participate in our SDLC?", the default answer begins with AIES — the way "how do we structure a project?" begins with PMBOK.
3. **Organizations design against it.** Operating models declare autonomy levels per task type and risk tier; platforms enforce envelopes, gates, and audit trails; these concepts trace to the Shared Taxonomy.
4. **Organizations evaluate and govern against it.** Capability claims about AI systems are backed by AESQS qualification evidence, not vendor marketing. Auditors and regulators can ask for AIES-shaped evidence and get it.
5. **People certify against it.** AECT credentials signal verified AI Engineering competency in hiring and staffing, at every level from Foundation (CL1) to Expert (CL4).
6. **The standard has survived model turnover.** Multiple generations of AI capability have arrived since v1.0, and the standard absorbed them — because it governs *evidence and authority*, not model snapshots.

## 4. What Success Looks Like, by Audience

| Audience | Success means… |
|----------|----------------|
| **Enterprises** | A defensible answer to "how do we adopt AI in engineering safely?" — an operating model with declared autonomy levels, risk-tiered gates, and audit trails that satisfies boards, customers, and regulators; capability decisions grounded in qualification evidence rather than anecdote |
| **Engineers** | A clear professional path: a body of knowledge to master (AEBOK), a competency ladder to climb (CL1–CL4), credentials that travel between employers (AECT), and role definitions that make "directing AI" a first-class engineering skill rather than an improvisation |
| **Educators** | A stable, vendor-neutral curriculum source: courses and degree programs built on AEBOK knowledge areas and AECT learning paths, with labs and evaluation methods that do not expire when a model version does |
| **Regulators & auditors** | A concrete engineering-level control layer beneath general AI governance: when a regulation demands "human oversight" or "risk management" for AI, AIES provides the inspectable mechanisms — approval gates, autonomy envelopes, provenance records, audit trails (ART-15) — that demonstrate it |

## 5. How AIES Gets There

The path is the [Roadmap](../ROADMAP.md), governed by the principle *knowledge first, qualification next, operations last*:

```
Knowledge (AEBOK) → Qualification (AESQS) → Operations (AEOS)
                                          → Architecture (AEAR)
                                          → Certification (AECT)
```

You cannot evaluate what you have not defined, and you should not delegate authority you cannot evaluate. Each module reaches Review before its dependents finalize, and the whole stands on the [Shared Standards](../Shared/README.md).

## 6. Relationship to Adjacent Standards

AIES **complements** adjacent standards; it does not replace any of them. Adopters should expect to use AIES *alongside* their existing frameworks.

| Standard | Its Domain | How AIES Relates |
|----------|-----------|------------------|
| **PMBOK** | Project management | AIES adds nothing to how projects are chartered and controlled; it defines how AI participates in the *engineering work* those projects contain. Phase P08 (Planning) interfaces cleanly with PMBOK practice. |
| **BABOK** | Business analysis | BABOK defines the analysis discipline; AIES defines how AI participates in it (P02, ROLE-02) and how AI-produced analysis artifacts are evaluated and governed. |
| **TOGAF** | Enterprise architecture | TOGAF structures enterprise architecture practice; AEAR provides reference architectures *for AI engineering platforms* that fit within a TOGAF-managed landscape. |
| **ISTQB** | Software testing | ISTQB defines testing competency for humans; AIES extends evaluation to AI-produced artifacts and AI performers (AESQS, P10) without altering testing fundamentals. |
| **OWASP (ASVS and related)** | Application security | OWASP defines what secure software requires; AIES defines how AI participation is secured and how AI-produced changes pass security gates (P11, X01). |
| **ISO/IEC 42001** | AI management systems | ISO/IEC 42001 governs an organization's AI systems generally; AIES specializes governance to *AI participation in software engineering*, providing the engineering-level controls a 42001 management system can invoke. |
| **NIST AI RMF** | AI risk management | The RMF frames AI risk functions (Govern, Map, Measure, Manage); AIES supplies concrete SDLC-scoped instruments for them — risk tiers, autonomy levels, qualification evidence, audit trails. |

Informative mappings to ISO/IEC 42001 and NIST AI RMF are a committed post-v1.0 deliverable (see [Project Charter §4, SC-7](PROJECT_CHARTER.md)).

## 7. What This Vision Refuses

The vision is disciplined by the project's non-goals: AIES will not rank vendors or models, will not publish prompt libraries, will not teach programming, and will not fork the missions of the standards above. Ambition is spent where the gap is — the standardization of AI participation in software engineering.

## Related Documents

- [AIES-DOC-01 — Project Charter](PROJECT_CHARTER.md)
- [AIES-DOC-03 — Repository Architecture](ARCHITECTURE.md)
- [AIES-DOC-04 — SDLC Reference](SDLC.md)
- [Shared Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md)

## References

None.

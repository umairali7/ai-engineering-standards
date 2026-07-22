# AEBOK — AI Engineering Body of Knowledge

| | |
|---|---|
| **Document ID** | AIES-AEBOK-00 |
| **Status** | Review |
| **Audience** | All readers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

AEBOK answers the first question of the AIES standard: **What should AI Engineering know?**

It is the canonical, vendor-neutral compilation of the knowledge required to practice AI-native software engineering — the concepts, practices, patterns, and anti-patterns that make AI participation in the SDLC deliberate, governed, and evidence-driven rather than ad hoc. AEBOK plays the role for AI Engineering that PMBOK plays for project management and BABOK plays for business analysis: it defines the discipline's shared body of knowledge, independent of any AI model, product, or provider.

AEBOK is descriptive of the discipline and normative about its essential practices. Where a practice is essential to safe, traceable AI-native delivery, AEBOK states it as a requirement using RFC 2119 language with a stable requirement ID (e.g., `[AIES-AEBOK-KA-05-R01]`).

### 1.1 Scope

In scope:

- Knowledge required by every role in the [role model](../Shared/Taxonomy/README.md#5-ai-engineering-roles) (ROLE-01 … ROLE-14) to work in an AI-native SDLC.
- Practices covering all sixteen SDLC phases (P01–P16) and the cross-cutting domains (X01–X15).
- Named patterns and anti-patterns of AI participation in engineering work.

Out of scope (owned by sibling modules or excluded by [project non-goals](../README.md#non-goals)):

- How capability is measured and scored → [AESQS](../AESQS/README.md)
- How teams and agents operate day to day → [AEOS](../AEOS/README.md)
- Platform reference architectures → [AEAR](../AEAR/README.md)
- Curricula, labs, and exams → [AECT](../AECT/README.md)
- Prompt libraries, model benchmarks, vendor guidance → excluded entirely.

## 2. Relationship to Other Modules

AEBOK is the knowledge foundation on which the other modules build:

```
                    ┌─────────────────────────────┐
                    │           AEBOK             │
                    │   defines the knowledge     │
                    └──────────────┬──────────────┘
          ┌──────────────┬─────────┴──────┬──────────────┐
          ▼              ▼                ▼              ▼
        AESQS          AEOS             AEAR           AECT
   tests whether   operationalizes   embodies it    teaches it as
   the knowledge   it as workflows,  in reference   learning paths
   is held (CL1–   gates, and roles  architectures  and credentials
   CL4, EV1–EV6)
```

- **AESQS** derives its competency framework and assessment rubrics from AEBOK knowledge areas: every AESQS assessment item traces to an AEBOK KA, and the Competency Expectations section of each KA (CL1–CL4) is the qualification baseline.
- **AEOS** turns AEBOK practices into an operating model — the "know" of AEBOK becomes the "do" of AEOS workflows, gates, and agent role definitions.
- **AEAR** shows what platforms that embody AEBOK knowledge look like structurally.
- **AECT** packages AEBOK content into learning paths, labs, and certification tracks per competency level.

All AEBOK documents use the [Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md) and [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) without redefinition.

## 3. Knowledge Area Map

AEBOK is organized into twelve Knowledge Areas (KAs). KA-01 is foundational; KA-02 through KA-09 follow the SDLC; KA-10 and KA-11 cover the cross-cutting disciplines that make the lifecycle KAs work; KA-12 closes the lifecycle at P16 with the evaluation and improvement loop that feeds them all.

| KA | Title | Scope (one line) |
|----|-------|------------------|
| [KA-01](knowledge-areas/KA-01-foundations.md) | Foundations of AI-Native Engineering | Core concepts; how AI participation changes engineering economics and risk; the autonomy/risk model in practice |
| [KA-02](knowledge-areas/KA-02-business-requirements.md) | AI-Assisted Business & Requirements Analysis | Using AI in strategy, analysis, product, UX, and requirements work while preserving human intent |
| [KA-03](knowledge-areas/KA-03-architecture-design.md) | Architecture & Design in AI-Native Delivery | Architecting systems that AI agents can safely analyze, extend, and operate on |
| [KA-04](knowledge-areas/KA-04-planning-decomposition.md) | Planning & Work Decomposition | Decomposing and routing work for mixed human/AI execution |
| [KA-05](knowledge-areas/KA-05-implementation.md) | AI-Assisted Implementation | Code generation practice, review discipline, and provenance for AI-produced source change |
| [KA-06](knowledge-areas/KA-06-testing-quality.md) | Testing & Quality Engineering | Testing AI-produced code, AI-assisted test generation, and evaluating non-deterministic components |
| [KA-07](knowledge-areas/KA-07-security.md) | Security Engineering | Threats specific to AI-native delivery and AI-assisted security work |
| [KA-08](knowledge-areas/KA-08-devops-release.md) | DevOps & Release Engineering | Pipelines as guardrails and gated deployment for AI-produced change |
| [KA-09](knowledge-areas/KA-09-operations-observability.md) | Operations & Observability | Running AI-inclusive systems and instrumenting agent activity |
| [KA-10](knowledge-areas/KA-10-context-knowledge.md) | Context & Knowledge Management | Curating organizational knowledge and context assets (ART-13) for AI consumption |
| [KA-11](knowledge-areas/KA-11-human-ai-collaboration.md) | Human-AI Collaboration & Oversight | Gate design, review ergonomics, accountability, and skill preservation |
| [KA-12](knowledge-areas/KA-12-evaluation-improvement.md) | Evaluation & Continuous Improvement | Measuring engineering outcomes, closing feedback loops, and detecting capability drift |

A consolidated [AIES-AEBOK-PAT-00 — AEBOK Pattern & Anti-Pattern Catalog](patterns/README.md) cross-references the named patterns used throughout the KAs.

## 4. Mapping Knowledge Areas to SDLC Phases

Each lifecycle KA owns one or more phases; the foundation and cross-cutting KAs apply everywhere.

| Phase(s) | Primary KA | Supporting KAs |
|----------|------------|----------------|
| P01 Business Strategy – P05 Requirements Engineering | KA-02 | KA-01, KA-10, KA-11 |
| P06 Solution Analysis – P07 Architecture | KA-03 | KA-01, KA-07, KA-10 |
| P08 Planning | KA-04 | KA-01, KA-11 |
| P09 Engineering | KA-05 | KA-03, KA-06, KA-07, KA-10 |
| P10 Testing & Quality | KA-06 | KA-05, KA-12 |
| P11 Security (X01) | KA-07 | KA-05, KA-08 |
| P12 DevOps – P13 Release | KA-08 | KA-06, KA-07, KA-11 |
| P14 Operations – P15 Observability | KA-09 | KA-08, KA-12 |
| P16 Continuous Improvement | KA-12 | KA-09, KA-10 |
| All phases (foundational) | KA-01 | — |
| All phases (X09 Knowledge Management) | KA-10 | — |
| All phases (X07 Human Oversight) | KA-11 | — |

```
P01──P02──P03──P04──P05   P06──P07   P08   P09   P10   P11   P12──P13   P14──P15   P16
└────────── KA-02 ─────┘  └─ KA-03┘ KA-04 KA-05 KA-06 KA-07 └─ KA-08┘  └─ KA-09┘ KA-12
════════════════════════ KA-01 · KA-10 · KA-11 (all phases) ════════════════════════
```

## 5. Structure of a Knowledge Area

Every KA document (Document ID `AIES-AEBOK-KA-NN`) follows the same structure so that AESQS, AEOS, and AECT can consume it mechanically:

1. **Purpose** — why this knowledge exists and what it protects.
2. **Key Concepts** — the ideas a practitioner must hold, using Glossary terms.
3. **Core Practices** — what practitioners do, including tagged normative requirements.
4. **Patterns** — named, reusable approaches (indexed in the [pattern catalog](patterns/README.md)).
5. **Anti-Patterns** — named failure modes to recognize and avoid.
6. **Competency Expectations** — what CL1–CL4 proficiency looks like in this KA.
7. **Related Documents** — navigation to adjacent knowledge.

[AIES-AEBOK-00-R01 — Engineering Body of Knowledge, requirement 01] Every AEBOK Knowledge Area document MUST follow the structure in §5 and MUST reference taxonomy IDs (phases, autonomy levels, risk tiers, roles, artifact types) rather than introducing competing scales.

[AIES-AEBOK-00-R02 — Engineering Body of Knowledge, requirement 02] Normative requirements within Knowledge Areas MUST carry stable requirement IDs of the form `AIES-AEBOK-KA-NN-RMM`.

## 6. Reading Guidance by Audience

| Audience | Suggested Path |
|----------|----------------|
| **Engineers new to AI-native work** (ROLE-06, ROLE-07, CL1 target) | KA-01 → KA-05 → KA-06 → KA-11, then the KAs for your phase of work |
| **Tech leads and reviewers** (CL2–CL3) | KA-01 → KA-04 → KA-05 → KA-11 → KA-12, plus the [anti-pattern catalog](patterns/README.md) |
| **Architects** (ROLE-05) | KA-01 → KA-03 → KA-07 → KA-10, then [AEAR](../AEAR/README.md) |
| **Security engineers** (ROLE-08) | KA-01 → KA-07 → KA-08 → KA-09 |
| **DevOps / SRE** (ROLE-09, ROLE-10) | KA-01 → KA-08 → KA-09 → KA-12 |
| **Business analysts / product managers** (ROLE-02, ROLE-03) | KA-01 → KA-02 → KA-04 → KA-11 |
| **Engineering leaders and governance officers** (ROLE-14, CL4) | KA-01 → KA-11 → KA-12 → full catalog review, then [AEOS](../AEOS/README.md) |
| **Educators and assessors** | KA-01, then the Competency Expectations section of every KA, then [AESQS](../AESQS/README.md) and [AECT](../AECT/README.md) |

Readers preparing for qualification SHOULD treat the Competency Expectations sections as the authoritative statement of what each CL level requires per KA.

## 7. Contents

```
AEBOK/
├── README.md                      ← this document (AIES-AEBOK-00)
├── knowledge-areas/
│   ├── KA-01-foundations.md               (AIES-AEBOK-KA-01)
│   ├── KA-02-business-requirements.md     (AIES-AEBOK-KA-02)
│   ├── KA-03-architecture-design.md       (AIES-AEBOK-KA-03)
│   ├── KA-04-planning-decomposition.md    (AIES-AEBOK-KA-04)
│   ├── KA-05-implementation.md            (AIES-AEBOK-KA-05)
│   ├── KA-06-testing-quality.md           (AIES-AEBOK-KA-06)
│   ├── KA-07-security.md                  (AIES-AEBOK-KA-07)
│   ├── KA-08-devops-release.md            (AIES-AEBOK-KA-08)
│   ├── KA-09-operations-observability.md  (AIES-AEBOK-KA-09)
│   ├── KA-10-context-knowledge.md         (AIES-AEBOK-KA-10)
│   ├── KA-11-human-ai-collaboration.md    (AIES-AEBOK-KA-11)
│   └── KA-12-evaluation-improvement.md    (AIES-AEBOK-KA-12)
└── patterns/
    └── README.md                  ← pattern & anti-pattern catalog (AIES-AEBOK-PAT-00)
```

## Related Documents

- [Glossary (AIES-SHARED-01 — Glossary)](../Shared/Glossary/README.md) — canonical term definitions used without redefinition
- [Taxonomy (AIES-SHARED-02 — Taxonomy)](../Shared/Taxonomy/README.md) — canonical scales (P/X/AL/RT/ROLE/CL/ART/EV)
- [AIES-AEBOK-PAT-00 — AEBOK Pattern & Anti-Pattern Catalog](patterns/README.md) — cross-cutting pattern canon
- [AESQS (AIES-AESQS-00 — Qualification Standard)](../AESQS/README.md) — capability measurement and scoring
- [AIES-AEOS-00 — AEOS — AI Engineering Operating System](../AEOS/README.md) — day-to-day operating model
- [AEAR (AIES-AEAR-00 — Reference Architecture)](../AEAR/README.md) — platform reference architectures
- [AECT (AIES-AECT-00 — Engineering Certification)](../AECT/README.md) — curricula, labs, and exams

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

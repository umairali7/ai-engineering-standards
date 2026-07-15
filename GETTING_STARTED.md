# Getting Started with AIES

| | |
|---|---|
| **Document ID** | AIES-DOC-00 |
| **Status** | Draft |
| **Audience** | All readers |

This is a guidance document: it orients you and recommends reading order, but nothing here is normative.

---

## What AIES Is

The AI Engineering Standards (AIES) project is building a vendor-neutral, engineering-first standard for AI-native software engineering. It defines the shared vocabulary, body of knowledge, qualification methods, operating model, reference architectures, and certification framework that let organizations adopt AI across the full SDLC with governance, evidence, and human accountability. It is to AI engineering what PMBOK is to project management or ISTQB to software testing.

## How the Pieces Fit

```
            Shared ─────── vocabulary: Glossary + Taxonomy (everything builds on this)
              │
              ▼
            AEBOK ─────── knowledge: what AI engineering should know
              │
              ▼
            AESQS ─────── qualification: how capability is evaluated and scored
              │
              ▼
            AEOS ──────── operations: roles, workflows, oversight, governance
              │
              ▼
            AEAR ──────── architecture: reference platforms and blueprints
              │
              ▼
            AECT ──────── certification: learning paths, labs, exams

     docs/standards ───── document governance: rules every AIES document follows
```

Read top-down for first exposure; in practice each module cites the others freely.

## Start Here by Role

### Executive / Engineering Leadership (~1 hour)

1. [README](README.md) — the vision, mission, and module map in ten minutes.
2. [Project Charter (AIES-DOC-01)](docs/PROJECT_CHARTER.md) — scope, goals, and what success looks like.
3. [Taxonomy (AIES-SHARED-02)](Shared/Taxonomy/README.md) — the risk tiers and autonomy levels your policies will reference.
4. [AEOS overview (AIES-AEOS-00)](AEOS/README.md) — what an AI-native operating model asks of your organization.

### Architect (~3 hours)

1. [Taxonomy (AIES-SHARED-02)](Shared/Taxonomy/README.md) — phases, domains, autonomy levels, risk tiers: the coordinate system for everything else.
2. [Repository Architecture (AIES-DOC-03)](docs/ARCHITECTURE.md) — how the standard itself is structured.
3. [Core Reference Architecture (AIES-AEAR-CORE-01)](AEAR/core-reference-architecture.md) — the platform layers and components.
4. [Cross-Cutting Concerns (AIES-AEAR-XC-01)](AEAR/cross-cutting-concerns.md) — security, privacy, observability, and cost across every layer.
5. An industry blueprint close to your domain, e.g. [Banking (AIES-AEAR-BP-BANKING)](AEAR/blueprints/banking.md) — the reference architecture specialized under real constraints.

### Engineer (~3 hours)

1. [Glossary (AIES-SHARED-01)](Shared/Glossary/README.md) — skim once so the terms land precisely later.
2. [KA-01 Foundations (AIES-AEBOK-KA-01)](AEBOK/knowledge-areas/KA-01-foundations.md) — the discipline's first principles.
3. [KA-05 Implementation (AIES-AEBOK-KA-05)](AEBOK/knowledge-areas/KA-05-implementation.md) — how AI participates in building software.
4. [KA-10 Context & Knowledge (AIES-AEBOK-KA-10)](AEBOK/knowledge-areas/KA-10-context-knowledge.md) — the context engineering that makes agents effective.
5. [Workflows (AIES-AEOS-WF-01)](AEOS/workflows.md) — the day-to-day shape of AI-native delivery.

### QA Engineer / Assessor (~3 hours)

1. [Taxonomy (AIES-SHARED-02)](Shared/Taxonomy/README.md) — evaluation dimensions, risk tiers, competency levels.
2. [Competency Framework (AIES-AESQS-CF-01)](AESQS/competency-framework.md) — what is being measured.
3. [Evaluation Rubrics (AIES-AESQS-ER-01)](AESQS/evaluation-rubrics.md) — how observations become scores.
4. [Capability Scoring (AIES-AESQS-CS-01)](AESQS/capability-scoring.md) — how scores aggregate into qualification decisions.
5. [EX-03 Scored Pull Request (AIES-EX-03)](examples/EX-03-scored-pull-request/README.md) — a complete scoring worked end to end.

### Educator / Training Provider (~2 hours)

1. [AECT overview (AIES-AECT-00)](AECT/README.md) — the certification and training module at a glance.
2. [Learning Paths (AIES-AECT-LP-01)](AECT/learning-paths.md) — curricula mapped to competency levels.
3. [Exam Blueprints (AIES-AECT-EB-01)](AECT/exam-blueprints.md) — what each credential examines.
4. [Labs (AIES-AECT-LAB-01)](AECT/labs.md) — hands-on exercises to build courses around.

### Contributor (~2 hours)

1. [CONTRIBUTING (AIES-GOV-02)](CONTRIBUTING.md) — the workflow and the rationale package every proposal needs.
2. [Governance (AIES-GOV-01)](GOVERNANCE.md) — decision classes, roles, and consensus.
3. [Document Standards (AIES-STD-00)](docs/standards/README.md) — the rules your document changes are reviewed against.
4. [Glossary (AIES-SHARED-01)](Shared/Glossary/README.md) — write with the canonical vocabulary from the start.

## Adopting AIES

Six steps, each demonstrated by a worked example set in one coherent case study (Fieldstone, a field-service SaaS company):

1. **Learn the vocabulary.** Adopt the [Glossary (AIES-SHARED-01)](Shared/Glossary/README.md) and [Taxonomy (AIES-SHARED-02)](Shared/Taxonomy/README.md) as your organization's terms, and record decisions the AIES way — [EX-04 (AIES-EX-04)](examples/EX-04-filled-adr/README.md) shows a filled Architecture Decision Record.
2. **Risk-tier your work.** Classify tasks by blast radius using [Taxonomy §4](Shared/Taxonomy/README.md) — [EX-01 (AIES-EX-01)](examples/EX-01-risk-tiering-backlog/README.md) tiers a real product backlog.
3. **Define envelopes.** Bound what each AI performer may do per the [Operating Model (AIES-AEOS-OM-01)](AEOS/operating-model.md) — [EX-02 (AIES-EX-02)](examples/EX-02-autonomy-envelope/README.md) is a completed autonomy envelope for a coding agent.
4. **Design gates.** Place human oversight where risk demands it per [Human Oversight (AIES-AEOS-HO-01)](AEOS/human-oversight.md) — [EX-05 (AIES-EX-05)](examples/EX-05-oversight-gate-design/README.md) designs the gates for a delivery pipeline.
5. **Qualify performers.** Evaluate capability with evidence per the [Qualification Process (AIES-AESQS-QP-01)](AESQS/qualification-process.md) — [EX-03 (AIES-EX-03)](examples/EX-03-scored-pull-request/README.md) scores an AI-produced pull request with the rubrics.
6. **Operate and improve.** Run the loop and feed it curated knowledge per [KA-10 (AIES-AEBOK-KA-10)](AEBOK/knowledge-areas/KA-10-context-knowledge.md) and [KA-12 (AIES-AEBOK-KA-12)](AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) — [EX-06 (AIES-EX-06)](examples/EX-06-context-asset-spec/README.md) specifies a maintained context asset.

## Where Things Live

```
.
├── GETTING_STARTED.md      ← you are here
├── GOVERNANCE.md           ← how decisions are made
├── CONTRIBUTING.md         ← how to propose changes
├── docs/                   ← charter, vision, SDLC, architecture
│   └── standards/          ← document governance (AIES-STD-*)
├── Shared/                 ← Glossary + Taxonomy (canonical vocabulary)
├── AEBOK/  AESQS/  AEOS/  AEAR/  AECT/   ← the five modules
├── adr/  templates/  examples/  diagrams/  research/
└── CHANGELOG.md  ROADMAP.md
```

## Proposing Changes

Every change follows [CONTRIBUTING (AIES-GOV-02)](CONTRIBUTING.md) and is classified under [GOVERNANCE (AIES-GOV-01)](GOVERNANCE.md): editorial fixes merge quickly, substantive changes need module-editor review, and anything normative or breaking requires an ADR and public comment. Bring an engineering rationale — problem, alternatives, trade-offs, impact — and the process is straightforward.

## Related Documents

- [README](README.md)
- [Project Charter (AIES-DOC-01)](docs/PROJECT_CHARTER.md)
- [Document Standards (AIES-STD-00)](docs/standards/README.md)
- [Shared Standards (AIES-SHARED-00)](Shared/README.md)
- [Worked Examples (AIES-EX-00)](examples/README.md)
- [Governance (AIES-GOV-01)](GOVERNANCE.md)
- [Contributing (AIES-GOV-02)](CONTRIBUTING.md)

## References

None.

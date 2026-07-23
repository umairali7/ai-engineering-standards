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

## Experience It Before Reading the Standard

You do not need to study the framework to see the product:

```text
cd platform
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .\.venv\Scripts\Activate.ps1   # Windows PowerShell
python -m pip install -e .
aies demo --open
```

Use `py -m venv .venv` on Windows when `python3` is not available. Never pass
`--break-system-packages`; the canonical source install is isolated. Existing
`pipx` or `uv` users may instead run `pipx install ./platform` or
`uv tool install ./platform` from the repository root.

In about a minute, the offline demo produces a real Engineering Capability
Matrix, Engineering Fit guidance, diagnostics, Executive Summary, and linked
report bundle. No model server, API key, Make, Bash, or mandatory human review
is involved.

Before choosing a path, ask the installed platform what it truly supports:

```text
aies support
aies starter list
```

Then enter through the decision you need. Codes are introduced with their
titles; normative detail is linked only after the runnable first step.

| Path | Decision | First command | What you receive | Important limitation | Next step |
|---|---|---|---|---|---|
| **Try** | Is the product understandable and useful enough to investigate? | `aies demo --open` | Offline Engineering Capability Matrix, fit guidance, diagnostics, and linked reports | Deterministic mock evidence demonstrates the workflow, not real-subject validity | `aies starter show understand-deployment` |
| **Evaluate** | Where does one AI deployment show capability and where is evidence thin? | `aies evaluate SUBJECT --judge REVIEWER --plan-only` | Bounded call plan, then a complete automated Engineering Evaluation and task snapshot | Observed performance is not field performance, qualification, or deployment authority | `aies snapshot latest` |
| **Compare** | Which compatible observed evidence better fits a scoped coding workload? | `aies starter show compare-coding-deployments` | Two matched evaluations and a task-by-task compatible comparison | No universal winner; incompatible protocols are not compared | Preregister broader evidence before publishing a selection claim |
| **Audit** | Which repository-practice evidence exists and which gaps come first? | `aies audit .` | CA-01 — AI-Native SDLC Foundations through CA-12 — Governance, Risk & AI Safety maturity, evidence states, and ranked remediation | Repository maturity does not prove source correctness or vulnerability absence | Close gaps, then run `aies audit . --gate --rt 2` |
| **Integrate** | How can an existing evaluator or static-analysis tool feed AIES evidence? | `aies bridge --help` | Source-bound Inspect or SARIF conversion with explicit loss and claim boundaries | Imported findings never silently become correctness, qualification, or authority | Validate the applicable experimental adapter profile |
| **Govern** | Is a formal human-governed qualification decision actually required? | `aies starter show formal-qualification` | The explicit rater, evidence, decision, record, and verification sequence | Automated scores do not grant; named humans retain consequential authority | Enter only when the formal decision is necessary |

To contribute or independently review the work, read
[CONTRIBUTING.md](CONTRIBUTING.md) and the
[Adoption and Launch Plan](docs/ADOPTION_AND_LAUNCH_PLAN.md).

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
2. [AIES-DOC-01 — Project Charter](docs/PROJECT_CHARTER.md) — scope, goals, and what success looks like.
3. [Taxonomy (AIES-SHARED-02 — Taxonomy)](Shared/Taxonomy/README.md) — the risk tiers and autonomy levels your policies will reference.
4. [AIES-AEOS-00 — AEOS — AI Engineering Operating System](AEOS/README.md) — what an AI-native operating model asks of your organization.

### Architect (~3 hours)

1. [Taxonomy (AIES-SHARED-02 — Taxonomy)](Shared/Taxonomy/README.md) — phases, domains, autonomy levels, risk tiers: the coordinate system for everything else.
2. [AIES-DOC-03 — Repository Architecture](docs/ARCHITECTURE.md) — how the standard itself is structured.
3. [Core Reference Architecture (AIES-AEAR-CORE-01 — Core Reference Architecture)](AEAR/core-reference-architecture.md) — the platform layers and components.
4. [Cross-Cutting Concerns (AIES-AEAR-XC-01 — Cross-Cutting Concerns)](AEAR/cross-cutting-concerns.md) — security, privacy, observability, and cost across every layer.
5. An industry blueprint close to your domain, e.g. [Banking (AIES-AEAR-BP-BANKING — Banking Blueprint)](AEAR/blueprints/banking.md) — the reference architecture specialized under real constraints.

### Engineer (~3 hours)

1. [Glossary (AIES-SHARED-01 — Glossary)](Shared/Glossary/README.md) — skim once so the terms land precisely later.
2. [KA-01 Foundations (AIES-AEBOK-KA-01 — Knowledge Area — Foundations)](AEBOK/knowledge-areas/KA-01-foundations.md) — the discipline's first principles.
3. [KA-05 Implementation (AIES-AEBOK-KA-05 — Knowledge Area — Implementation)](AEBOK/knowledge-areas/KA-05-implementation.md) — how AI participates in building software.
4. [KA-10 Context & Knowledge (AIES-AEBOK-KA-10 — Knowledge Area — Context and Knowledge)](AEBOK/knowledge-areas/KA-10-context-knowledge.md) — the context engineering that makes agents effective.
5. [Workflows (AIES-AEOS-WF-01 — Workflows)](AEOS/workflows.md) — the day-to-day shape of AI-native delivery.

### QA Engineer / Assessor (~3 hours)

1. [Taxonomy (AIES-SHARED-02 — Taxonomy)](Shared/Taxonomy/README.md) — evaluation dimensions, risk tiers, competency levels.
2. [Competency Framework (AIES-AESQS-CF-01 — Competency Framework)](AESQS/competency-framework.md) — what is being measured.
3. [Evaluation Rubrics (AIES-AESQS-ER-01 — Evaluation Rubrics)](AESQS/evaluation-rubrics.md) — how observations become scores.
4. [Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](AESQS/capability-scoring.md) — how scores aggregate into qualification decisions.
5. [AIES-EX-03 — EX-03 — An AI-Produced Pull Request Scored with the AESQS Rubrics](examples/EX-03-scored-pull-request/README.md) — a complete scoring worked end to end.

### Educator / Training Provider (~2 hours)

1. [AECT overview (AIES-AECT-00 — Engineering Certification)](AECT/README.md) — the certification and training module at a glance.
2. [Learning Paths (AIES-AECT-LP-01 — Learning Paths)](AECT/learning-paths.md) — curricula mapped to competency levels.
3. [Exam Blueprints (AIES-AECT-EB-01 — Exam Blueprints)](AECT/exam-blueprints.md) — what each credential examines.
4. [Labs (AIES-AECT-LAB-01 — Labs)](AECT/labs.md) — hands-on exercises to build courses around.

### Contributor (~2 hours)

1. [AIES-GOV-02 — Contributing to AIES](CONTRIBUTING.md) — the workflow and the rationale package every proposal needs.
2. [AIES-GOV-01 — Governance](GOVERNANCE.md) — decision classes, roles, and consensus.
3. [Document Standards (AIES-STD-00 — Documentation Standards)](docs/standards/README.md) — the rules your document changes are reviewed against.
4. [Glossary (AIES-SHARED-01 — Glossary)](Shared/Glossary/README.md) — write with the canonical vocabulary from the start.

## Adopting AIES

Six steps, each demonstrated by a worked example set in one coherent case study (Fieldstone, a field-service SaaS company):

1. **Learn the vocabulary.** Adopt the [Glossary (AIES-SHARED-01 — Glossary)](Shared/Glossary/README.md) and [Taxonomy (AIES-SHARED-02 — Taxonomy)](Shared/Taxonomy/README.md) as your organization's terms, and record decisions the AIES way — [AIES-EX-04 — EX-04 — A Filled Architecture Decision Record](examples/EX-04-filled-adr/README.md) shows a filled Architecture Decision Record.
2. **Risk-tier your work.** Classify tasks by blast radius using [Taxonomy §4](Shared/Taxonomy/README.md) — [AIES-EX-01 — EX-01 — Risk-Tiering a Real Product Backlog](examples/EX-01-risk-tiering-backlog/README.md) tiers a real product backlog.
3. **Define envelopes.** Bound what each AI performer may do per the [Operating Model (AIES-AEOS-OM-01 — Operating Model)](AEOS/operating-model.md) — [AIES-EX-02 — EX-02 — A Completed Autonomy Envelope Definition for an AI Coding Agent](examples/EX-02-autonomy-envelope/README.md) is a completed autonomy envelope for a coding agent.
4. **Design gates.** Place human oversight where risk demands it per [Human Oversight (AIES-AEOS-HO-01 — Human Oversight)](AEOS/human-oversight.md) — [AIES-EX-05 — EX-05 — Human Oversight Gate Design for a Delivery Pipeline](examples/EX-05-oversight-gate-design/README.md) designs the gates for a delivery pipeline.
5. **Qualify performers.** Evaluate capability with evidence per the [Qualification Process (AIES-AESQS-QP-01 — Qualification Process)](AESQS/qualification-process.md) — [AIES-EX-03 — EX-03 — An AI-Produced Pull Request Scored with the AESQS Rubrics](examples/EX-03-scored-pull-request/README.md) scores an AI-produced pull request with the rubrics.
6. **Operate and improve.** Run the loop and feed it curated knowledge per [KA-10 (AIES-AEBOK-KA-10 — Knowledge Area — Context and Knowledge)](AEBOK/knowledge-areas/KA-10-context-knowledge.md) and [KA-12 (AIES-AEBOK-KA-12 — Knowledge Area — Evaluation and Improvement)](AEBOK/knowledge-areas/KA-12-evaluation-improvement.md) — [AIES-EX-06 — EX-06 — A Context Asset Specification](examples/EX-06-context-asset-spec/README.md) specifies a maintained context asset.

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

Every change follows [AIES-GOV-02 — Contributing to AIES](CONTRIBUTING.md) and is classified under [AIES-GOV-01 — Governance](GOVERNANCE.md): editorial fixes merge quickly, substantive changes need module-editor review, and anything normative or breaking requires an ADR and public comment. Bring an engineering rationale — problem, alternatives, trade-offs, impact — and the process is straightforward.

## Related Documents

- [README](README.md)
- [AIES-DOC-01 — Project Charter](docs/PROJECT_CHARTER.md)
- [Document Standards (AIES-STD-00 — Documentation Standards)](docs/standards/README.md)
- [AIES-SHARED-00 — Shared Standards](Shared/README.md)
- [AIES-EX-00 — Worked Examples](examples/README.md)
- [AIES-GOV-01 — Governance](GOVERNANCE.md)
- [AIES-GOV-02 — Contributing to AIES](CONTRIBUTING.md)

## References

None.

# AI Engineering Standards (AIES)

> **The vendor-neutral standard and executable assessment system for trustworthy AI-native software engineering.**

![Status](https://img.shields.io/badge/Status-Active%20Development-blue)
![License](https://img.shields.io/badge/License-Open%20dual--license%20(proposed)-lightgrey)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

**New here? Start with [GETTING_STARTED.md](GETTING_STARTED.md)** — role-based reading paths and a six-step adoption guide.

**Want to see the platform run in minutes?** [QUICKSTART.md](QUICKSTART.md) — the complete workflow, fully offline (`make demo`, or step by step).

---

## Vision

Artificial Intelligence is fundamentally changing software engineering.

Organizations are rapidly adopting AI assistants, coding agents, autonomous workflows, and AI-native engineering platforms. Despite this transformation, there is no comprehensive, vendor-neutral engineering standard defining how AI should participate across the complete Software Development Life Cycle (SDLC).

The **AI Engineering Standards (AIES)** project exists to establish that
standard: a practical, engineering-first framework that enables organizations
to build, evaluate, compare, govern, certify, and operate trustworthy
AI-native software engineering systems at enterprise scale.

AIES is not confined to evaluating models. Its canonical evidence architecture
is subject-neutral. The current reference implementation assesses **AI
deployments** and **software repositories**. The same contracts are intended to
support dedicated assessment adapters for AI agents, agent swarms, MCP servers,
AI coding assistants, prompt libraries, RAG systems, AI pipelines, AI
platforms, and composite systems as those adapters are implemented and
validated.

See the full [Vision](docs/VISION.md) and [Project Charter](docs/PROJECT_CHARTER.md).

## Mission

Build the world's most comprehensive **vendor-neutral engineering standard for AI Engineering** — the equivalent for this discipline of what these standards are for theirs:

| Discipline | Industry Standard |
|------------|-------------------|
| Project Management | PMBOK |
| Business Analysis | BABOK |
| Enterprise Architecture | TOGAF |
| Application Security | OWASP ASVS |
| Software Testing | ISTQB |
| **AI Engineering** | **AIES** |

## Why This Project Exists

Current AI engineering practice suffers from recurring gaps:

- No common engineering vocabulary
- No standard AI-native SDLC methodology
- No objective capability evaluation framework
- No engineering competency model
- No standard AI operating model
- Heavy dependence on specific vendors or models
- Limited governance and auditability
- Inconsistent quality across AI systems

AIES addresses these gaps through an open, extensible, engineering-driven standard.

---

## From Evidence to Engineering Decisions

AIES separates evidence from the different decisions people need to make from
it:

```text
Assessment
    ↓
Canonical Evidence
    ↓
Competency Analysis
    ↓
Engineering Capability Matrix (ECM)
    ↓
Engineering Fit, Comparison, and Optional Formal Qualification
```

The outputs serve different audiences and must not be collapsed into one
opaque score:

| Decision product | Primary audience | What it answers | Human evaluation required? |
|---|---|---|---|
| **Engineering Evaluation** | Engineers and evaluators | What was observed, under which conditions, and with what evidence? | No; automated scores are sufficient for the engineering result |
| **Engineering Capability Matrix (ECM)** | Engineers and technical leaders | Which engineering tasks are demonstrated strengths, weaker areas, or evidence gaps? | No; human evaluation is an optional, visible corroboration |
| **Engineering Fit Guidance** | Engineering managers and platform teams | Where is this subject a good fit, where should review be used, and where is evidence insufficient? | No; informational only and never deployment authority |
| **Formal Qualification** | Auditors and qualification authorities | Does the evidence satisfy a governed, risk-scoped qualification protocol? | Yes; explicitly requested with `--formal-qualification` |
| **Qualification Record** | Governance and accountable leadership | What consequential qualification decision did a named human authority record? | Yes |

Routine assessment, benchmarking, analysis, comparison, and reporting are
therefore **non-blocking**: missing human review is reported as `not performed`,
not treated as a failure. Human accountability remains mandatory for
consequential grants, releases, deployments, and other governed decisions.

### Engineering Capability Matrix

The ECM is the engineer-facing core artifact defined around a stable,
subject-neutral Engineering Task Taxonomy:

| ID | Engineering task | ID | Engineering task | ID | Engineering task |
|---|---|---|---|---|---|
| ET-01 | Requirements Analysis | ET-06 | Debugging | ET-11 | Database Design |
| ET-02 | Architecture Design | ET-07 | Testing | ET-12 | Migration |
| ET-03 | API Design | ET-08 | Documentation | ET-13 | Infrastructure |
| ET-04 | Code Generation | ET-09 | Performance Optimization | ET-14 | Observability |
| ET-05 | Refactoring | ET-10 | Security Review | ET-15 | Production Operations |

For every applicable task, the ECM reports observed performance separately
from evidence confidence, scenario count, coverage, and provenance. `Not
assessed` means **no supported claim can be made**; it is not a zero-capability
rating. This makes the ECM useful for evidence-compatible subject comparison
and workload selection without turning AIES into a context-free leaderboard.

---

## The Five Modules

| Module | Full Name | Question It Answers | Docs |
|--------|-----------|---------------------|------|
| **AEBOK** | AI Engineering Body of Knowledge | *What should AI Engineering know?* | [AEBOK/](AEBOK/README.md) |
| **AESQS** | AI Engineering SDLC Qualification Standard | *How do we objectively evaluate AI Engineering capability?* | [AESQS/](AESQS/README.md) |
| **AEOS** | AI Engineering Operating System | *How should AI Engineering teams operate?* | [AEOS/](AEOS/README.md) |
| **AEAR** | AI Engineering Architecture Reference | *What should enterprise AI platforms look like?* | [AEAR/](AEAR/README.md) |
| **AECT** | AI Engineering Certification & Training | *How do engineers learn and become certified?* | [AECT/](AECT/README.md) |

All modules build on the [Shared Standards](Shared/README.md) — the canonical [Glossary](Shared/Glossary/README.md), [Taxonomy](Shared/Taxonomy/README.md), and documentation conventions that keep terminology consistent across the entire standard.

```
AI Engineering Standards (AIES)
│
├── Shared Standards ────── vocabulary, taxonomies, conventions (used by all)
│
├── AEBOK ──── knowledge:      disciplines, practices, patterns, SDLC guidance
├── AESQS ──── qualification:  competency model, rubrics, capability scoring
├── AEOS ───── operations:     agent roles, workflows, human oversight, governance
├── AEAR ───── architecture:   reference architectures and industry blueprints
└── AECT ───── certification:  learning paths, labs, exams, credentials
```

## Guiding Principles

1. **Vendor Neutral** — Standards define engineering capabilities, not vendors. Models evolve continuously; engineering standards remain stable.
2. **Engineering First** — Engineering disciplines take precedence over prompt techniques and model-specific optimizations.
3. **Enterprise Ready** — Every recommendation is designed for production environments: governance, security, compliance, auditability, traceability, scalability, reliability, operations.
4. **Human Governed** — AI augments engineers. Humans remain accountable for engineering decisions.
5. **Evidence Driven** — Recommendations are supported by measurable outcomes, repeatable evaluation, and documented trade-offs.
6. **Open & Extensible** — The standards evolve with the AI ecosystem while preserving compatibility through controlled versioning and governance.

## Complete SDLC Coverage

Unlike existing AI frameworks, AIES covers the complete software engineering lifecycle — sixteen phases from Business Strategy through Continuous Improvement — plus fifteen cross-cutting domains (security, privacy, compliance, governance, risk, AI safety, human oversight, and more) that span every phase.

The canonical phase and domain definitions live in [docs/SDLC.md](docs/SDLC.md) and the [Shared Taxonomy](Shared/Taxonomy/README.md).

## Intended Audience

Enterprise engineering organizations, CTOs, engineering directors and managers, enterprise/AI/software architects, platform engineering teams, AI product teams, security teams, QA organizations, researchers, universities, and open source communities.

---

## Repository Structure

```
.
├── README.md                 ← you are here
├── GETTING_STARTED.md        ← entry point: reading paths & adoption guide
├── LICENSE.md                ← open dual-license proposal and current legal status
├── CHANGELOG.md              ← versioned change history
├── ROADMAP.md                ← phased delivery plan
├── GOVERNANCE.md             ← decision-making model
├── CONTRIBUTING.md           ← how to contribute
├── SECURITY.md               ← vulnerability reporting
├── CODE_OF_CONDUCT.md
│
├── docs/                     ← charter, vision, architecture, SDLC, FAQ
│   └── standards/            ← document standards governing every file here
├── Shared/                   ← canonical glossary & taxonomy (normative)
├── AEBOK/                    ← Body of Knowledge
├── AESQS/                    ← Qualification Standard
├── AEOS/                     ← Operating System
├── AEAR/                     ← Architecture Reference
├── AECT/                     ← Certification & Training
│
├── platform/                 ← executable Engineering Assessment Platform
├── conformance/              ← golden evidence packages & conformance runner
├── adr/                      ← Architecture Decision Records
├── templates/                ← document templates
├── examples/                 ← worked examples
├── diagrams/                 ← source diagrams
└── research/                 ← supporting research notes
```

## Documentation Hierarchy

```
README → Project Charter → Standards → Specifications
       → Reference Architectures → Examples → Certification Material
```

Each level becomes more specific: the README orients, the charter scopes, standards define requirements, specifications detail them, reference architectures and examples apply them, and certification material teaches them.

## Engineering Philosophy

Knowledge defines what good engineering looks like. Evidence establishes what
was observed. Capability analysis makes that evidence useful. Qualification is
a separate governed decision, not a prerequisite for engineering insight.

```
Knowledge → Assessment → Evidence → Competency Analysis → ECM
                                                     ├→ Engineering Fit
                                                     ├→ Comparison
                                                     └→ Optional Formal Qualification
                                                            ↓
                                          Operations → Continuous Improvement
```

Certification and training remain connected to this lifecycle through AECT.
The modules and implementation milestones are described in the
[Roadmap](ROADMAP.md).

## Governance

The project follows an engineering governance model described in [GOVERNANCE.md](GOVERNANCE.md):

- Architecture Decision Records ([adr/](adr/README.md))
- Peer review and engineering review
- Public discussion
- Versioned releases

No individual contributor owns the standards. Engineering consensus drives evolution.

**Contract stability (v1.0 freeze).** The architecture has reached a stable
equilibrium; the contracts others build against are frozen and versioned:

- [STABILITY.md](STABILITY.md) — the **v1.0 Architecture Freeze**: frozen
  contracts with versions, the **normative vs reference** distinction, and
  **reference implementation vs conformance suite**.
- [COMPATIBILITY.md](COMPATIBILITY.md) — how contracts evolve (additive-only,
  ADR-for-breaking, deprecation window) — **enforced by CI**, not just prose.
- [CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md) — what "AIES Conformant" means,
  verified by a data-first conformance suite over a golden Evidence Package corpus.

## Non-Goals

The project does **not** aim to:

- Promote a specific AI vendor
- Publish a context-free model leaderboard or declare one universally “best”
- Replace existing engineering frameworks (it complements PMBOK, TOGAF, ISTQB, etc.)
- Become a prompt library
- Teach programming fundamentals

AIES does support evidence-compatible comparison of scoped assessment runs.
Those comparisons are engineering selection inputs, not universal rankings.
AIES defines **engineering standards** that remain applicable regardless of the
underlying AI technology.

## Roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Repository Foundation | ✅ Complete (v0.3.1) |
| 2 | AEBOK — Body of Knowledge | 🔍 In Review (v0.4.0) |
| 3 | AESQS — Qualification Standard | 🔍 In Review (v0.4.0) |
| 4 | AEOS — Operating System | 🔍 In Review (v0.4.0) |
| 5 | AEAR — Architecture Reference | 🔍 In Review (v0.4.0) |
| 6 | AECT — Certification & Training | 🔍 In Review (v0.4.0) |
| 7 | Reference Implementations | ⏳ Planned (consumes Phase 8) |
| 8 | Engineering Assessment Platform (`aies` CLI) | 🚧 In Progress ([ADR-0009](adr/ADR-0009-Engineering-Assessment-Platform-Identity.md)) |
| 9 | Public Release (v1.0) | ⏳ Planned |

Details in [ROADMAP.md](ROADMAP.md).

## Engineering Assessment Platform

The **[Engineering Assessment Platform](platform/README.md)** (`aies` CLI) is
the executable reference implementation of the AIES evidence architecture. It
collects canonical evidence once and renders audience-specific decision
products without changing the underlying observations.

### Current capabilities

- Assess AI deployments across CA-01 — AI-Native SDLC Foundations through
  CA-12 — Governance, Risk & AI Safety.
- Audit repositories across architecture, correctness, code quality, testing,
  security, operations, governance, documentation, and improvement
  opportunities.
- Generate Engineering Assessment Results, evidence packages, ECM artifacts,
  Engineering Fit Guidance, reports, and compatible run comparisons.
- Use automated judges for complete non-blocking evaluation; preserve optional
  human evaluation as a separately attributed column and evidence source.
- Reserve formal qualification for explicit `--formal-qualification` runs and
  named human qualification authorities.
- Show live stage, current work, completed/total items, active worker count,
  elapsed time, rate, and ETA for long-running CLI operations.
- Evaluate the platform's own scenario corpus for coverage, calibration
  metadata, behavioral diversity, duplication, and empirical maturity through
  `aies corpus`.
- Verify decision-engine compatibility against immutable golden Evidence
  Packages through the conformance runner.

### Typical workflow

From `platform/`, create an isolated Python environment and install the CLI:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aies doctor
aies discover
```

Run an end-to-end engineering evaluation with a separately registered judge:

```powershell
aies qualify <deployment> --all-areas --rt 2 --judge <judge-deployment> --parallel 4

# Equivalent benchmark-oriented command
aies benchmark <deployment> --all-areas --rt 2 --judge <judge-deployment> --parallel 4
```

Both commands collect responses, score them, aggregate canonical evidence, and
generate the complete report bundle. Human review is optional. Inspect or
compare the decision products with:

```powershell
aies capabilities <run-id>
aies guidance <run-id>
aies compare <run-a> <run-b>
aies transcript <run-id>
```

Use formal qualification only when the governed decision is actually required:

```powershell
aies qualify <deployment> --assessment enterprise --judge <judge-deployment> --formal-qualification
```

See the [platform guide](platform/GUIDE.md) for the complete workflow and the
[CLI reference](platform/CLI_REFERENCE.md) for every command, parameter,
prerequisite, sequence, progress behavior, and recovery path.

### Evidence scope and honest claims

Platform results are always risk-scoped: RT1 — Minimal, RT2 — Moderate, RT3 —
Significant, and RT4 — Critical have different evidence, gate, and autonomy
requirements. An ECM `not assessed` task is an evidence gap, not a negative
capability claim. `--all-areas` covers all competency areas for the selected
risk tier; it does not silently claim coverage outside that scope.

The scenario corpus currently contains **484 validated scenarios across 12
competency areas**, with all 15 engineering tasks directly represented. Every
scenario carries design-time calibration metadata and the validator reports
zero structural warnings or errors. Empirical calibration against a
representative multi-model panel remains outstanding; design quality and
scenario count must not be presented as empirical discrimination.

## Contributing

Contributions are welcome. Every proposal should include an engineering rationale, problem statement, alternatives considered, trade-offs, references, and impact analysis. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Versioning

The standard versions as a whole — Semantic Versioning via git tags and the [CHANGELOG](CHANGELOG.md), per the [Versioning Standard (AIES-STD-05 — Versioning Standard)](docs/standards/versioning-standard.md):

| Version | Status |
|---------|--------|
| v0.x | Research & Draft |
| v1.x | Stable Standards |
| v2.x | Major Evolution |

Individual documents carry a lifecycle status only (Draft → Review → Approved → Deprecated) per the [Review Standard (AIES-STD-06 — Review Standard)](docs/standards/review-standard.md) — no per-document versions or dates; git history is the system of record.

## Current Status

- **Standards:** Internal review cycle complete for all module documents; AEBOK,
  AESQS, AEOS, AEAR, and AECT are in Review for v0.4.0.
- **Platform:** Functional reference implementation with engineering
  evaluation, repository audit, ECM, fit guidance, comparison, reporting,
  conformance, and optional formal qualification; hardening and subject-adapter
  expansion remain in progress under
  [ADR-0009](adr/ADR-0009-Engineering-Assessment-Platform-Identity.md).
- **Verified baseline:** 484 scenarios across 12 competency areas with zero
  suite warnings/errors; 228 platform tests passing at the latest local
  verification. Empirical panel calibration and an independent pilot remain
  open.
- **Status:** Active Development.

## License

AIES is committed to an open-source release. The exact terms will be finalized
before v1.0. Proposed
[ADR-0014](adr/ADR-0014-Dual-License-Standards-and-Software.md) recommends
**CC BY-SA 4.0** for standards and reusable assessment content and **Apache
2.0** for executable software. Until that Class 3 decision is ratified, no
license is granted; see [LICENSE.md](LICENSE.md) and [docs/FAQ.md](docs/FAQ.md).

---

> **AI Engineering Standards (AIES)** is an open initiative to define the future of AI-native software engineering through vendor-neutral, engineering-first standards.

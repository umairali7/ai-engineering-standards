# AI Engineering Standards (AIES)

> **Building the vendor-neutral standard for AI-native Software Engineering.**

![Status](https://img.shields.io/badge/Status-Active%20Development-blue)
![License](https://img.shields.io/badge/License-CC--BY--SA--4.0%20(proposed)-lightgrey)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

**New here? Start with [GETTING_STARTED.md](GETTING_STARTED.md)** — role-based reading paths and a six-step adoption guide.

**Want to see the platform run in 5 minutes?** [QUICKSTART.md](QUICKSTART.md) — the whole workflow, fully offline (`make demo`, or step by step).

---

## Vision

Artificial Intelligence is fundamentally changing software engineering.

Organizations are rapidly adopting AI assistants, coding agents, autonomous workflows, and AI-native engineering platforms. Despite this transformation, there is no comprehensive, vendor-neutral engineering standard defining how AI should participate across the complete Software Development Life Cycle (SDLC).

The **AI Engineering Standards (AIES)** project exists to establish that standard: a practical, engineering-first framework that enables organizations to build, evaluate, govern, certify, and operate trustworthy AI-native software engineering systems at enterprise scale.

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
├── LICENSE.md                ← license status (pending selection)
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

Knowledge comes first. Qualification follows. Operations come last.

```
Knowledge → Competency → Qualification → Operations → Certification → Continuous Improvement
```

This is why the modules are sequenced AEBOK → AESQS → AEOS → AEAR → AECT in the [Roadmap](ROADMAP.md).

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
- Benchmark AI models
- Replace existing engineering frameworks (it complements PMBOK, TOGAF, ISTQB, etc.)
- Become a prompt library
- Teach programming fundamentals

AIES defines **engineering standards** that remain applicable regardless of the underlying AI technology.

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

The **[Engineering Assessment Platform](platform/README.md)** (`aies` CLI) is the executable
reference implementation. Its current executors assess AI deployments and repositories;
its subject-neutral evidence architecture is designed to extend to agents, MCP servers,
RAG systems, pipelines, and platforms. It applies the same
evidence-plus-verdict-plus-human-decision discipline to *itself*: `aies audit`
reviews a repository's engineering practice, and `aies corpus` continuously
reviews the platform's **own** assessment corpus for calibration, coverage,
behavioral diversity, duplication, and empirical maturity — advisory,
multidimensional, and never a single grade.

Platform capability results are always **risk-scoped**: RT1 — Minimal through RT4 — Critical carry
different evidence, gate, and autonomy requirements. An ECM `not assessed`
task is an evidence gap, not a negative capability claim; `--all-areas` covers
all areas only for the selected risk tier.

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

- **Phase:** Internal review cycle complete for all module documents; Engineering Assessment Platform ([ADR-0009](adr/ADR-0009-Engineering-Assessment-Platform-Identity.md)) in progress
- **Status:** Active Development

## License

License selection will be finalized before the v1.0 release. Creative Commons **CC-BY-SA-4.0** is the current proposal for standard documents — see [LICENSE.md](LICENSE.md) and [docs/FAQ.md](docs/FAQ.md).

---

> **AI Engineering Standards (AIES)** is an open initiative to define the future of AI-native software engineering through vendor-neutral, engineering-first standards.

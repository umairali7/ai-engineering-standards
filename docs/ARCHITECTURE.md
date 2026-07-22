# Repository Architecture

| | |
|---|---|
| **Document ID** | AIES-DOC-03 |
| **Status** | Review |
| **Audience** | Contributors & maintainers |

How the AIES repository is organized: the directory layout, how the five modules depend on each other and on the Shared Standards, how documents are identified and progress through their lifecycle, and how to find what you need.

---

## 1. Annotated Directory Tree

```
.
├── README.md                    ← project front door: vision, modules, principles
├── GETTING_STARTED.md           ← guided reading paths into the standard, by reader role
├── LICENSE.md                   ← open dual-license proposal; no grant until ratified
├── CHANGELOG.md                 ← versioned change history for the standard as a whole
├── ROADMAP.md                   ← phased delivery plan (module sequencing)
├── GOVERNANCE.md                ← decision-making model, review and ratification process
├── CONTRIBUTING.md              ← proposal requirements and contribution workflow
├── SECURITY.md                  ← vulnerability and responsible-disclosure reporting
├── CODE_OF_CONDUCT.md           ← participation expectations
│
├── docs/                        ← project-level documents (AIES-DOC-*)
│   ├── PROJECT_CHARTER.md       ←   scope, stakeholders, success criteria, risks
│   ├── VISION.md                ←   the five-year end state and standards landscape
│   ├── ARCHITECTURE.md          ←   this document
│   ├── SDLC.md                  ←   the detailed 16-phase lifecycle reference
│   ├── FAQ.md                   ←   frequently asked questions
│   └── standards/               ←   the six documentation standards
│                                    (AIES-STD-01 … AIES-STD-06)
│
├── Shared/                      ← NORMATIVE foundation used by every module
│   ├── README.md                ←   shared standards index (AIES-SHARED-00)
│   ├── Glossary/                ←   canonical term definitions (AIES-SHARED-01)
│   └── Taxonomy/                ←   phases, domains, autonomy levels, risk tiers,
│                                    roles, competency levels, artifacts (AIES-SHARED-02)
│
├── AEBOK/                       ← Body of Knowledge: what AI Engineering should know
├── AESQS/                       ← Qualification Standard: how capability is evaluated
├── AEOS/                        ← Operating System: how AI-native teams operate
├── AEAR/                        ← Architecture Reference: what platforms should look like
├── AECT/                        ← Certification & Training: how engineers learn and certify
│
├── adr/                         ← Architecture Decision Records (numbered, immutable)
├── templates/                   ← document skeletons (standard, ADR)
├── examples/                    ← worked examples applying the standards
├── diagrams/                    ← text-first diagram sources (Mermaid / ASCII)
└── research/                    ← informative evidence base (never normative)
```

## 2. Module Dependency Model

Dependencies flow downward: a module may depend only on modules below it and on Shared.

```
                    ┌───────────────────────────────────────┐
                    │                 AEAR                  │
                    │   reference architectures — hosts     │
                    │   AEOS operating models on platforms  │
                    └───────────────┬───────────────────────┘
                                    │ hosts
                    ┌───────────────▼───────────────────────┐
                    │                 AEOS                  │
                    │   operating model: roles, workflows,  │
                    │   gates, autonomy governance          │
                    └───────────────┬───────────────────────┘
                                    │ autonomy grants require
                                    │ qualification evidence
        ┌───────────────┐   ┌───────▼────────┐
        │     AECT      │   │     AESQS      │
        │ certification │   │ qualification  │
        │  & training   │   │  & scoring     │
        └───────┬───────┘   └───────┬────────┘
                │ teaches &         │ evaluates against
                │ examines          │ knowledge defined in
                └───────┬───────────┘
                ┌───────▼───────────────────────┐
                │             AEBOK             │
                │   body of knowledge: what     │
                │   competent practice means    │
                └───────┬───────────────────────┘
                        │ built on
                ┌───────▼───────────────────────┐
                │        Shared Standards       │
                │  Glossary · Taxonomy          │
                │  (base of all)                │
                └───────────────────────────────┘
```

In words:

- **Shared** is the base. Every module uses its glossary and taxonomies; none may redefine them. Documentation conventions live in the [Documentation Standards (AIES-STD-00 — Documentation Standards)](standards/README.md).
- **AEBOK** defines what competent AI Engineering practice *is*. It feeds **AESQS** (you evaluate against defined knowledge) and **AECT** (you teach and examine defined knowledge).
- **AESQS** produces the qualification evidence that **AEOS** requires before granting or raising an autonomy level (per [Taxonomy R03](../Shared/Taxonomy/README.md)).
- **AEOS** defines the operating model that **AEAR** platforms host: reference architectures exist to run AEOS-shaped workflows with enforced envelopes, gates, and audit trails.

A change to Shared is a breaking change for all five modules and requires an ADR (see [ADR-0001](../adr/ADR-0001-Repository-Foundation.md)).

## 3. Document Identifier Scheme

Defined normatively in the [Metadata Standard (AIES-STD-02 — Metadata Standard)](standards/metadata-standard.md); summarized here:

```
AIES-<AREA>-<NUMBER>             repository-level documents
<MODULE>-<TYPE>-<NUMBER|NAME>    module documents
```

| Prefix | Family | Examples |
|--------|--------|----------|
| `AIES-DOC-*` | Project-level documents in `docs/` | `AIES-DOC-01` (Charter), `AIES-DOC-04` (SDLC) |
| `AIES-SHARED-*` | Shared Standards | `AIES-SHARED-01` (Glossary), `AIES-SHARED-02` (Taxonomy) |
| `AEBOK-*` | Body of Knowledge documents | `AIES-AEBOK-KA-04` (Knowledge Area 4) |
| `AESQS-*` | Qualification documents | `AIES-AESQS-CF-01` (Competency Framework) |
| `AEOS-*` | Operating-model documents | `AIES-AEOS-ROLE-07` (role specification) |
| `AEAR-*` | Architecture documents | `AIES-AEAR-BP-BANKING` (industry blueprint) |
| `AECT-*` | Certification documents | `AIES-AECT-CERT-02` (certification track) |
| `ADR-NNNN` | Architecture Decision Records | `ADR-0001` |

IDs are stable and never reused. Individual normative requirements inside a document carry `[<DOC-ID>-R<NN>]` identifiers so they can be cited from assessments, audits, and certification material.

## 4. Document Status Lifecycle

Every standards-style document carries a metadata table (Document ID, Status, Audience — per the [Metadata Standard (AIES-STD-02 — Metadata Standard)](standards/metadata-standard.md)) and moves through the lifecycle defined in the [Review Standard (AIES-STD-06 — Review Standard)](standards/review-standard.md):

```
Draft ──► Review ──► Approved ──► Deprecated
  ▲          │
  └──────────┘  (revision reopens Draft)
```

How a document flows in practice:

1. **Draft** — authored on a branch using the [standard template](../templates/STANDARD_TEMPLATE.md); content may change without notice.
2. **Review** — the author declares content-completeness; structured peer review is opened per [GOVERNANCE.md](../GOVERNANCE.md). Normative changes discovered in review return the document to Draft.
3. **Approved** — ratified through governance. Further changes require a new revision cycle, and breaking changes require an ADR.
4. **Deprecated** — superseded; the metadata table names the successor document so references never dangle.

ADRs follow their own lifecycle (Proposed → Accepted → Superseded) described in [adr/README.md](../adr/README.md).

## 5. Where Each Artifact Type Belongs

| You are creating… | It belongs in… | Governed by |
|-------------------|---------------|-------------|
| A new normative standard or specification | The owning module directory (`AEBOK/`, `AESQS/`, …) | [Standard template](../templates/STANDARD_TEMPLATE.md), [Documentation Standards (AIES-STD-00 — Documentation Standards)](standards/README.md) |
| A project-level document (charter, guides) | `docs/` with an `AIES-DOC-*` ID | [Documentation Standards (AIES-STD-00 — Documentation Standards)](standards/README.md) |
| A term definition | [Shared/Glossary/](../Shared/Glossary/README.md) — never locally | Glossary rules, ADR if breaking |
| A classification scale or scale change | [Shared/Taxonomy/](../Shared/Taxonomy/README.md) — never locally | Taxonomy change control (ADR required) |
| A significant decision record | `adr/` as `ADR-NNNN-Title.md` | [ADR template](../templates/ADR_TEMPLATE.md), [adr/README.md](../adr/README.md) |
| A worked example | `examples/` | [examples/README.md](../examples/README.md) |
| A diagram source | Inline in the document, or `diagrams/` if shared/reused | [diagrams/README.md](../diagrams/README.md) |
| Research notes, literature reviews, survey data | `research/` (informative only) | [research/README.md](../research/README.md) |
| A reusable document skeleton | `templates/` | This document, via ADR |

## 6. Navigation Guide

| I want to… | Read |
|------------|------|
| Understand what AIES is and why it exists | [README.md](../README.md), then [VISION.md](VISION.md) |
| Know what is in and out of scope | [PROJECT_CHARTER.md](PROJECT_CHARTER.md) |
| Learn the lifecycle model and phase guidance | [SDLC.md](SDLC.md) |
| Look up a term | [Shared/Glossary/](../Shared/Glossary/README.md) |
| Look up a phase, role, autonomy level, risk tier, or artifact ID | [Shared/Taxonomy/](../Shared/Taxonomy/README.md) |
| Understand the knowledge areas of the discipline | [AEBOK/](../AEBOK/README.md) |
| Evaluate the capability of an AI system or engineer | [AESQS/](../AESQS/README.md) |
| Design how my team operates with AI | [AEOS/](../AEOS/README.md) |
| Design an enterprise AI engineering platform | [AEAR/](../AEAR/README.md) |
| Get trained or certified | [AECT/](../AECT/README.md) |
| Write a new AIES document | [templates/STANDARD_TEMPLATE.md](../templates/STANDARD_TEMPLATE.md) and the [Documentation Standards (AIES-STD-00 — Documentation Standards)](standards/README.md) |
| Propose or understand a structural decision | [adr/](../adr/README.md) |
| See the standards applied concretely | [examples/](../examples/README.md) |
| Contribute | [CONTRIBUTING.md](../CONTRIBUTING.md) and [GOVERNANCE.md](../GOVERNANCE.md) |
| Check what changed and what is coming | [CHANGELOG.md](../CHANGELOG.md) and [ROADMAP.md](../ROADMAP.md) |
| Get quick answers to common questions | [FAQ.md](FAQ.md) |

## Related Documents

- [AIES-SHARED-00 — Shared Standards](../Shared/README.md)
- [Documentation Standards (AIES-STD-00 — Documentation Standards)](standards/README.md)
- [ADR-0001: Repository Foundation](../adr/ADR-0001-Repository-Foundation.md)
- [AIES-DOC-01 — Project Charter](PROJECT_CHARTER.md)

## References

None.

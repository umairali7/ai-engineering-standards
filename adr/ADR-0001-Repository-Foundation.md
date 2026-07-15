# ADR-0001: Repository Foundation

| | |
|---|---|
| **ADR** | ADR-0001 |
| **Status** | Accepted |
| **Audience** | Contributors & maintainers |
| **Deciders** | AIES Maintainers |
| **Supersedes / Superseded by** | — |

## Context

AIES defines standards for AI-native software engineering across five concerns that evolve at different speeds and serve different audiences: a body of knowledge (AEBOK), a qualification standard (AESQS), an operating model (AEOS), an architecture reference (AEAR), and a certification framework (AECT). Each module must be able to evolve independently — a new AEAR blueprint should not force a re-review of AEBOK — yet all five must speak with **one vocabulary**: the same autonomy levels, risk tiers, roles, phases, and glossary terms, defined once and never diverging.

Before the first foundation release, the project had to decide how to structure the standard physically: as one document, as several repositories, or as one repository with internal modularity. The choice constrains everything downstream — identifiers, cross-references, governance mechanics, release engineering — and is expensive to reverse once external material begins citing the standard. Doing nothing (structuring ad hoc) would let modules drift into inconsistent terminology, which contradicts the project's founding premise.

## Decision Drivers

- **Consistency** — shared terms and taxonomies must have exactly one definition, and drift between modules must be structurally difficult.
- **Discoverability** — a newcomer should find any concept, requirement, or decision from a single entry point without tooling.
- **Contribution friction** — proposing a change, including one spanning modules, should require one pull request under one governance process.
- **Versioning** — the standard must be releasable and citable as a coherent whole ("AIES v0.3.1"), while individual documents track their own versions and lifecycle status.

## Options Considered

### Option A — Single monolithic document

One large document (or a small fixed set) containing all five concerns.

- **Pros:** Trivially consistent terminology; nothing to cross-reference; simplest possible versioning; a single artifact to cite.
- **Cons:** Does not scale — a body of knowledge, a scoring rubric, and an architecture reference have different structures, audiences, and revision rhythms; review becomes all-or-nothing; parallel authoring produces constant merge conflicts; readers must navigate material irrelevant to them; module-level status lifecycle (Draft → Review → Approved) is impossible.

### Option B — One repository per module

Five (or six, with a shared-definitions repository) independently governed repositories.

- **Pros:** Maximum module independence — separate release cadences, access control, and issue trackers; small, focused clones; module identity is unmistakable.
- **Cons:** Shared vocabulary becomes a cross-repository dependency that must be version-pinned and synchronized — the exact drift the project exists to prevent; a cross-module change (e.g., renaming an autonomy level) requires coordinated pull requests across up to six repositories with no atomic merge; discoverability fragments; governance and contribution processes must be duplicated and kept aligned; relative links between modules break.

### Option C — Single repository, five modules on a Shared foundation (chosen)

One repository containing `AEBOK/`, `AESQS/`, `AEOS/`, `AEAR/`, and `AECT/` as peer directories, all depending on a normative `Shared/` directory (glossary, taxonomy, conventions) at the base, with common support directories (`adr/`, `templates/`, `examples/`, `diagrams/`, `research/`, `docs/`).

- **Pros:** One source of truth for vocabulary — modules link to Shared rather than restating it, and redefinition is prohibited by convention and detectable in review; cross-module changes are atomic (one PR, one comment window, one merge); a single governance process and ADR log cover everything; relative links work everywhere; the whole standard is versioned and released as one artifact while each document keeps its own metadata table and lifecycle.
- **Cons:** The repository grows large as modules mature; access control is coarse — merge rights are repository-wide rather than per module; a single ADR log and issue tracker mix concerns from five modules.

## Decision

We adopt **Option C**: a single repository containing the five modules as peer directories on top of a normative Shared Standards foundation, with the dependency rule that modules may depend on Shared and on modules below them in the dependency model, and that no module may redefine a shared term or taxonomy. The layout and dependency model are documented in [docs/ARCHITECTURE.md (AIES-DOC-03)](../docs/ARCHITECTURE.md); the conventions that make Shared authoritative are in [Shared/README.md (AIES-SHARED-00)](../Shared/README.md).

Option C is the only option that satisfies the consistency driver structurally (one definition, one place) while preserving module-level independence through per-document lifecycle status, module-scoped editorship ([GOVERNANCE.md §2](../GOVERNANCE.md)), and directory boundaries. Option A fails on scale and independent evolution; Option B trades away exactly the property — enforced shared vocabulary — that motivates the project.

## Consequences

**Positive:**

- Cross-module changes are atomic: a taxonomy rename, its ADR, and every affected module update land in one reviewed pull request.
- Single source of truth for the glossary and taxonomy; consistency is enforceable in review because every module resolves terms to the same files.
- One entry point, one navigation model, one contribution workflow, one changelog and release tag for the whole standard.
- Relative links and Document IDs resolve within one tree, so link validation is a simple release-checklist step.

**Negative:**

- The repository will grow large as five modules mature — mitigation: text-first content, module-scoped directories, and phased delivery per [ROADMAP.md](../ROADMAP.md) keep any one area navigable.
- Access control is coarse; merge rights cannot be granted per module — mitigation: Module Editor approval requirements and decision classes in [GOVERNANCE.md §3](../GOVERNANCE.md) provide module-level authority by process rather than by permission system.
- Every change to `Shared/` is a breaking change for all five modules — mitigation: this is deliberate; such changes are always Class 3, requiring an ADR, Maintainer lazy consensus, a 7-day comment window, and mandatory cross-module impact analysis.

## Compliance & Verification

- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) documents the directory layout and dependency model; structural changes to it require a new ADR (see [adr/README.md §1](README.md)).
- Reviewers verify that module documents reference the [Shared Glossary](../Shared/Glossary/README.md) and [Taxonomy](../Shared/Taxonomy/README.md) without local redefinition (prohibited by the [Writing Standard (AIES-STD-03)](../docs/standards/writing-standard.md)).
- The release checklist in [GOVERNANCE.md §6.2](../GOVERNANCE.md) validates cross-references and relative links across the repository and checks the Glossary/Taxonomy for unregistered terms.

## Links

- Pull request: Repository Foundation release (v0.3.1)
- Related: [Repository Architecture (AIES-DOC-03)](../docs/ARCHITECTURE.md) · [Shared Standards (AIES-SHARED-00)](../Shared/README.md) · [Governance (AIES-GOV-01)](../GOVERNANCE.md) · [ADR process](README.md)

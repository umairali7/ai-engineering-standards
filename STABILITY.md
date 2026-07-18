# AIES v1.0 Architecture Freeze & Stable Interfaces

| | |
|---|---|
| **Document ID** | AIES-DOC-10 |
| **Status** | Draft |
| **Audience** | Contributors · Integrators · Third-party implementers |
| **Companion** | [COMPATIBILITY.md](COMPATIBILITY.md) — how these contracts evolve |

The AIES architecture has reached a stable equilibrium. This document **freezes**
the contracts that others build against and declares which parts of the
repository are normative versus reference. It exists so a contributor or an
external implementer knows exactly what is safe to depend on, and so future
change is driven by implementation experience rather than design speculation.

> **The stable API of AIES is not Python — it is the artifacts.** Integrators
> build against the *schemas* (Assessment YAML, Evidence Package JSON, Canonical
> Assessment Result JSON), not against class names. The schemas are the contract.

## 1. Normative vs Reference

Standards and implementations evolve differently, so the repository distinguishes
them explicitly. (This is a **labeling** distinction, not a directory layout — a
physical reorganization, if ever, would be its own ADR with a redirect map.)

| Tree | Kind | Changes via |
|---|---|---|
| `Shared/` (Glossary & Taxonomy) | **Normative** | Standard revision (GOVERNANCE §5) |
| `AEBOK/`, `AESQS/`, `AEOS/`, `AEAR/`, `AECT/` | **Normative** | Standard revision |
| `platform/` (engine, `aies` CLI) | **Reference** | Platform release |
| `platform/examples/`, dashboard, demos | **Reference** | Platform release |

A **normative** document *defines what must be true*. A **reference** artifact
*demonstrates one correct way to satisfy it*. The reference implementation may be
replaced or forked without changing the standard; the standard may not be
weakened by any implementation.

## 2. Reference Implementation vs Conformance Suite

These are different things and must not be conflated:

| | Purpose | Lives |
|---|---|---|
| **Reference Implementation** | Demonstrates *one* correct implementation (the `aies` platform) | `platform/` |
| **Conformance Suite** | *Verifies any* implementation — the arbiter | golden Evidence Package corpus + expected outcomes ([CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md)) |

One is software; the other is the arbiter. The conformance suite is **data-first**
(a shared corpus) so it can judge an implementation it did not ship with —
including a third-party decision engine. The platform's own tests are merely
*one consumer* of that corpus.

## 3. Frozen contracts (v1.0)

Each contract is frozen **at the stated version**. "Frozen" means: existing
fields and their meaning do not change; only additive, backward-compatible
extension is permitted (see COMPATIBILITY.md). A breaking change requires an ADR
**and** a version bump.

| Contract | Owner | Version | Where |
|---|---|---|---|
| **RuntimeAdapter** (semantic core) | Platform | `v1.0` | `platform/src/aies/adapters/base.py` |
| **Assessment schema** | Standard | `1` | `assessments.SUPPORTED_SCHEMA` |
| **Profile schema** | Standard | `1` | `platform/profiles/*.yaml` |
| **Evidence Package schema** | Platform | `1` | `constants.EVIDENCE_SCHEMA` |
| **Canonical Assessment Result schema** | Platform | `1` | `decision.RESULT_SCHEMA` |
| **Decision semantics** | Standard (AESQS) | `1.0` | `decision.DECISION_SEMANTICS_VERSION` |
| **Report Renderer contract** (view-only) | Platform | `v1.0` | `decision.render_*`, `report_html` |

Two version fields are deliberately distinct on every result:
`decision_engine_version` (*which software decided*) and
`decision_semantics_version` (*which normative policy was applied*). A bugfix
rebuild changes the former; an AESQS policy change changes the latter. They are
never conflated.

### RuntimeAdapter: stable core, additive surface

The RuntimeAdapter is frozen **semantically**, not method-for-method forever. Its
core (`generate()`, `load()`, `fingerprint()`) is stable. Its **extension
surface** (e.g. `capabilities()`) may *grow* additively. Consumers must use
**capability detection** (`adapter.capabilities().get("streaming")`), never
version sniffing — so a v1.0 adapter keeps conforming while newer adapters add
surface, with no synchronized upgrade.

## 4. Evolution in one sentence

Additive fields only; backward-compatible extensions; an ADR for any breaking
change; the conformance suite must pass. The full policy — including the
append-only-schema vs immutable-instance distinction and the deprecation window
— is in **[COMPATIBILITY.md](COMPATIBILITY.md)**, and it is **enforced by CI**
(golden-schema tests), not merely documented.

## Related Documents

- [COMPATIBILITY.md](COMPATIBILITY.md) — evolution & deprecation policy
- [CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md) — what "AIES Conformant" means
- [GOVERNANCE.md](GOVERNANCE.md) — decision classes, ratification, releases
- [ADR-0005](adr/ADR-0005-Assessment-as-Code.md) — the assessment pipeline & Canonical Result

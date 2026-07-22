# AIES Compatibility Policy

| | |
|---|---|
| **Document ID** | AIES-DOC-11 |
| **Status** | Draft |
| **Audience** | Contributors · Integrators · Third-party implementers |
| **Companion** | [STABILITY.md](STABILITY.md) — what is frozen |

Stability says *what* the contracts are. Compatibility says *how they evolve*.
A stable contract still needs an evolution policy, and **a compatibility policy
that isn't enforced is just prose** — so every rule here is backed by a test.

## 1. Two orthogonal guarantees

These are different properties and are guaranteed separately:

| Property | Applies to | Guarantee |
|---|---|---|
| **Append-only schema** | An artifact *schema* (Evidence Package, Canonical Result, …) | New **optional** fields may be added. Existing fields are never removed, renamed, or given new meaning. |
| **Immutable instance** | A produced *artifact* (one result, one evidence package) | Never edited, never overwritten. A re-decision produces a **new** document; it never mutates the old one. |

A result is deterministic: the same (Evidence Package, decision semantics) pair
always yields the same outcome. Replaying evidence through a **newer** engine or
newer semantics is expected and produces a new, separately-versioned result — it
does not retract the original.

## 2. What is a breaking change

**Breaking (requires a MAJOR/schema bump + an ADR):**
- Removing or renaming a field; changing a field's type or meaning.
- Changing decision semantics (outcome for the same evidence).
- Removing or altering the meaning of an existing RuntimeAdapter method.
- Tightening validation so previously-valid data is rejected.

**Non-breaking (additive; a MINOR change; no ADR required):**
- Adding a new optional field to an artifact (bump the schema version, add it to
  the golden shape test).
- Adding a new assessment/profile, a new renderer, a new adapter capability.
- Adding a new optional adapter method behind capability detection.

## 3. Deprecation window

A field slated for removal is first marked **deprecated** (documented + still
populated) for **at least one minor release** before removal, and its removal is
a breaking change requiring an ADR. Consumers get a release to migrate; nothing
disappears without notice.

## 4. Versioning discipline

- **Artifacts** carry a schema version (`evidence_schema`, `result_schema`,
  assessment `schema`, profile `version`). Bump on any breaking change.
- **Decision semantics** version (`decision_semantics_version`) changes only when
  the normative outcome policy changes — an AESQS revision, never a rebuild.
- **Engine** version (`decision_engine_version`) tracks the software build.
- Every result records all of the above, so a certification is always traceable
  to the exact inputs and policy that produced it.

## 5. The "existing contracts first" discipline

Before adding any new abstraction, ask:

> **Can this be expressed using the existing contracts?**

- **Yes** → do not add a new abstraction. Express it with what exists.
- **No** → it requires an **ADR** explaining why the existing contracts are
  insufficient, plus the version bump and conformance impact.

This question is a required line in the [ADR template](templates/ADR_TEMPLATE.md)
and the PR checklist. It is what keeps the architecture coherent over time.

## 6. Enforcement (not prose)

| Rule | Enforced by |
|---|---|
| Artifact envelope shapes don't drift | `platform/tests/test_artifact_schemas.py` (golden shape tests — a removed/renamed field fails the build) |
| Shipped assessments stay valid | `aies suites validate` (CI gate) |
| Shipped profiles are versioned & valid | `platform/tests/test_profile_versioning.py` |
| Decision semantics stay faithful | conformance suite over the golden Evidence Package corpus ([CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md)) |
| The golden path still works end-to-end | `platform/tests/test_demo.py` (`make demo`) |

Adding an optional field to an artifact means: add it, **and** add it to the
golden shape test and bump the schema constant — in the same change. If the two
diverge, CI fails. That is the policy being executable rather than aspirational.

### Evidence Package v4 to v5

ADR-0012 authorizes the breaking v5 change in statistical unit. Version 4
packages expose flat admitted rating observations and retain their historical
meaning. Version 5 adds explicit `rating_observations` and `evidence_items`;
qualification statistics consume the latter's resolved scores, never the
former as independent samples. Readers MUST branch on `evidence_schema` and
MUST NOT reinterpret a v4 package as if it had passed v5 resolution.

### ECM v1 to v2 and Engineering Task Mapping v1 to v2

ADR-0013 introduces governed task decisions. ECM v1 rows were informational
coverage summaries and MUST NOT be reinterpreted as demonstrated capability.
ECM v2 adds an explicit task-decision envelope, uncertainty, gates, rater
protocol, mapping review, instrument maturity, parent-area controls, and a
versioned task-decision semantic. Engineering Task Mapping schema 2 adds
per-rule human review provenance; an unreviewed schema-1 mapping cannot support
`demonstrated`. Deployment Guidance schema 2 requires both demonstrated task
evidence and a matching current human Qualification Record before it can emit
`Use` or `Use with human review`.

These are review-stage experimental contracts. Readers MUST branch on
`ecm_schema`, task-mapping `schema`, `task_decision_semantics_version`, and
`guidance_schema`; they MUST NOT silently upgrade older artifacts.

## Related Documents

- [STABILITY.md](STABILITY.md) — the frozen contracts (v1.0 freeze)
- [CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md) — conformance verification
- [GOVERNANCE.md](GOVERNANCE.md#6-releases) — release & versioning process

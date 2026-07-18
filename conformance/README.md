# AIES Conformance Suite — the golden Evidence Package corpus

| | |
|---|---|
| **Document ID** | AIES-DOC-13 |
| **Status** | Draft |
| **Policy** | [CONFORMANCE-POLICY.md](../CONFORMANCE-POLICY.md) |

This directory is the **arbiter** for *decision-engine conformance*. It is
**data-first** (STABILITY.md §2): a shared corpus that verifies **any** decision
engine — the reference engine, a future engine, or a third-party one — not only
the implementation it shipped with.

## What a case is

Each case pairs an **immutable Evidence Package** with the **expected Canonical
outcome** under a stated decision-semantics version:

```
corpus/<case-id>/
  evidence-package.json   # input evidence (immutable; evidence_schema pinned)
  assessment.json         # the assessment to decide under (resolved form)
  expected.json           # { decision_semantics_version, outcome, reason_kinds[] }
```

A decision engine is **conformant to AESQS decision semantics vX.Y** iff, for
every case, feeding `evidence-package.json` + `assessment.json` to the engine
yields the `outcome` and reason kinds in `expected.json`.

## Coverage

The corpus exercises **every outcome** (`PASS / FAIL / INCONCLUSIVE /
INSUFFICIENT EVIDENCE`), **every decision-blocking reason kind**
(`mandatory-gate`, `min-cl`, `insufficient-evidence`, `assessment-error`), and
the **load-bearing invariants**: a strong competency never offsets a failing
mandatory one; advisory failures never change the outcome; and outcome precedence
(`FAIL > INCONCLUSIVE > INSUFFICIENT EVIDENCE > PASS`). A test asserts this
coverage so the arbiter cannot silently narrow.

## Running it

```
# the reference engine (auto-discovers this corpus):
aies conform engine

# an explicit corpus, JSON output, non-zero exit if non-conformant (CI):
aies conform engine --corpus conformance/corpus --json
```

CI runs it every build (`platform/tests/test_engine_conformance.py`). A
third-party engine is verified against the **same** corpus by wrapping its
`decide(evidence, assessment)` and passing it to `engine_conformance.verify`.

## Regenerating

The JSON files are the committed, frozen corpus. [`generate_corpus.py`](generate_corpus.py)
documents how they were built and re-materialises them byte-for-byte (static
values, no timestamps). Editing a case's expected outcome is a **normative
change** to what conformance means — treat it like any decision-semantics change
(an AESQS revision + a `decision_semantics_version` bump), not a routine edit.

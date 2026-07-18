# AIES Conformance Policy

| | |
|---|---|
| **Document ID** | AIES-DOC-12 |
| **Status** | Draft |
| **Audience** | Third-party implementers · Integrators · Maintainers |
| **Companions** | [STABILITY.md](STABILITY.md) · [COMPATIBILITY.md](COMPATIBILITY.md) |

"AIES Conformant" must mean something an outside party can *verify*, not a badge
anyone may self-apply. As with compatibility, **a conformance claim that isn't
backed by an executable check is just a claim.** This document defines, per
contract, what conformance requires and the check that decides it.

The distinction that motivates this document (STABILITY.md §2): the **reference
implementation** demonstrates one correct implementation; the **conformance
suite** verifies *any* implementation. The suite is therefore **data-first** — a
shared corpus that can judge an implementation it did not ship with.

## 1. Conformance targets

| You are claiming conformance of a… | You must satisfy | Verified by |
|---|---|---|
| **Runtime Adapter** | The RuntimeAdapter v1.0 semantic contract; capabilities via detection, not version sniffing | The adapter conformance tests (the [out-of-tree example adapter](platform/examples/external_adapter/README.md) is the reference fixture) |
| **Assessment** | The assessment schema + semantic rules | `aies assessment validate` (strict allowed-key schema) |
| **Profile** | The profile schema; versioned; no engine-owned keys | `aies profile validate` |
| **Report Renderer** | Renders the Canonical Assessment Result **without deciding** — round-trips to the same `outcome`, introduces no new outcome | Renderer conformance test (a renderer that recomputes PASS/FAIL fails) |
| **Decision Engine** (incl. third-party) | Produces the AESQS-semantics-mandated outcome for every case in the golden corpus | Replay of the **golden Evidence Package corpus** → expected outcomes |

## 2. The golden Evidence Package corpus (the arbiter)

The heart of the suite. It is a set of **immutable Evidence Packages** paired with
their **expected Canonical outcomes** under a stated `decision_semantics_version`:

```
conformance/
  corpus/
    <case-id>/
      evidence-package.json     # input (immutable, evidence_schema pinned)
      expected.json             # { decision_semantics_version, outcome, reasons[] }
```

A decision engine is **conformant to AESQS decision semantics vX.Y** iff, for
every case, feeding `evidence-package.json` to the engine yields the `outcome`
and reason kinds in `expected.json`. Because evidence is versioned independently
of any engine (STABILITY.md §3), the corpus outlives engine builds: the *same*
corpus verifies the reference engine today and a third-party or future engine
later.

**The corpus is language-neutral data — you do not need this package to use it.**
The cases are plain JSON (`evidence-package.json`, `assessment.json`,
`expected.json`); an independent engine in any language can read them and compare
its own outputs. For convenience, `aies conform engine --engine "<command>"`
runs the whole corpus against a **foreign** engine: the command reads
`{"evidence": …, "assessment": …}` as JSON on stdin and prints the Canonical
Assessment Result on stdout. A minimal, self-contained reference —
[`conformance/example_engine.py`](conformance/example_engine.py), ~50 lines of
pure Python with **no `aies` import** — reimplements the semantics from the spec
and passes all cases, proving the standard is reproducible independently:

```
aies conform engine --engine "python conformance/example_engine.py"   # → CONFORMANT 8/8
```

The corpus MUST cover, at minimum: each outcome (`PASS / FAIL / INCONCLUSIVE /
INSUFFICIENT EVIDENCE`); each reason kind (`mandatory-gate`, `min-cl`,
`insufficient-evidence`, `assessment-error`, …); the load-bearing invariants (a
strong competency never offsets a failing mandatory one; advisory failures never
change the outcome; precedence ordering); and boundary sample sizes
(NON-DECISIONAL vs decisional).

## 3. Levels

- **Consumer conformant** — reads and renders the Canonical Assessment Result
  without recomputing it (a CLI, dashboard, GitHub Action, IDE plugin). Satisfies
  the *no consumer computes outcomes* invariant (below).
- **Producer conformant** — a decision engine that passes the golden corpus.
- **Adapter conformant** — a runtime adapter that passes the adapter tests.

## 4. The invariant every consumer must satisfy

> **No consumer computes outcomes.** The CLI, the REST API, the Dashboard, a
> GitHub Action, an IDE plugin — all *render* the Canonical Assessment Result
> produced by the decision engine. A consumer that re-derives PASS/FAIL is a
> **bug**, not an alternative implementation.

The outcome is decided **once**, by the engine, and only ever read thereafter.
This is what lets many interfaces coexist without drifting from each other.

## 5. Claiming conformance

A conformance claim states the **target**, the **contract version**, and (for a
decision engine) the **`decision_semantics_version`** it passes — e.g. *"engine X
is Producer-conformant to AESQS decision semantics 1.0."* The claim is
substantiated only by a passing run of the corresponding check; the platform's
own CI runs all of them (COMPATIBILITY.md §6).

## Related Documents

- [STABILITY.md](STABILITY.md) — frozen contracts and the reference/conformance distinction
- [COMPATIBILITY.md](COMPATIBILITY.md) — how contracts evolve, and enforcement
- [ADR-0005](adr/ADR-0005-Assessment-as-Code.md) — decision semantics & the Canonical Result
- [AESQS](AESQS/README.md) — the normative qualification standard

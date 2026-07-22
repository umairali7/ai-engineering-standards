# Example conformance statements

Worked examples for the two conformance classes in
[CONFORMANCE.md (AIES-DOC-08 — Conformance Guide)](../../../docs/CONFORMANCE.md), checkable with
`aies conform`.

| File | Class | What it claims |
|---|---|---|
| [`adopter-statement.yaml`](adopter-statement.yaml) | **adopter** | Uses AIES to qualify deployments and govern AI participation; evidence-backed claims link to a Qualification Record |
| [`implementation-statement.yaml`](implementation-statement.yaml) | **implementation** | A tool that enforces AIES's normative scoring/gating requirements |

```bash
aies conform requirements                                       # the enforced requirement IDs
aies conform check examples/conformance/adopter-statement.yaml  # verify a statement
aies conform template --class adopter                           # scaffold your own
```

**Reading the result.** A check verifies the *structure* and that each
evidence-backed claim references a **live Qualification Record in this
workspace**. The adopter example's second claim has no linked record, so it is
reported **self-asserted** (not verified) — that is the intended,
evidence-not-checkboxes behavior, not a tool failure. To see the adopter example
report **SUBSTANTIATED**, first produce a real grant so `QUAL-2026-001` exists
(qualify → score → `aies qualify --resume` → `aies grant`), then re-check.

A conformance check does not certify the *truth* of a qualification or a
reviewer's independence — it checks that claims are structured and evidence-linked.

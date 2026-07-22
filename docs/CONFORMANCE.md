# Conformance to AIES

| | |
|---|---|
| **Document ID** | AIES-DOC-08 |
| **Status** | Draft |
| **Audience** | Engineering leadership · Governance officers · Assessors & qualification authorities · Contributors & maintainers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119 and RFC 8174.

A framework becomes a *standard* when others can conform to it in a defined,
checkable way. This document defines what it means to conform to AIES — the
conformance **classes**, the **assurance levels** of a claim, and the
**conformance statement** that records one. The `aies conform` command
(specified in [PLATFORM.md](PLATFORM.md)) checks statements against this model.

Where `aies conform` checks a *claim*, **`aies audit <repo>`**
([ADR-0004](../adr/ADR-0004-Repository-Conformance-Audit.md)) makes conformance
**executable**: it derives evidence from a repository, scoring maturity per
competency area with three-state evidence (verified / asserted / gap, never
false-green). The two compose — an audit produces the evidence a conformance
statement then records, and its `--attest` file is the same assert-with-evidence
model used here.

## 1. Two conformance classes

Conformance to AIES is claimed in one of two classes, because two very
different things can conform:

- **Implementation conformance** — a *tool* implements the AESQS methodology
  faithfully. Its evidence is a mapping of enforced normative requirements to
  the code/tests that enforce them (`aies conform requirements`), backed by a
  conformance test suite keyed to requirement IDs. The reference platform is
  the archetype; a third-party tool MAY claim this class.
- **Adopter conformance** — an *organization* qualifies its AI deployments per
  AIES. Its evidence is a set of Qualification Records (and the audit trails
  behind them) produced by an AIES implementation.

[AIES-DOC-08-R01 — Conformance Guide, requirement 01] A conformance statement MUST declare exactly one class.

## 2. Three assurance levels

A claim's weight depends on how it is substantiated:

| Level | Meaning | What a checker can confirm |
|-------|---------|----------------------------|
| **self-asserted** | The claimant states it on their own word. | Only that the statement is well-formed. |
| **evidence-backed** | Each material claim references verifiable artifacts (Qualification Records). | That each referenced record exists and is a live grant. |
| **independently-reviewed** | A named reviewer, independent of the claimant, attests to the claim. | That a reviewer is named — **not** that they are independent. |

[AIES-DOC-08-R02 — Conformance Guide, requirement 02] An **independently-reviewed** statement MUST name the
reviewer. The independence of that reviewer is a human attestation that the
tooling cannot and does not verify; readers MUST treat the named reviewer as
the accountable party.

[AIES-DOC-08-R03 — Conformance Guide, requirement 03] An **evidence-backed** statement is *substantiated* only if
every evidence-bearing claim references a Qualification Record that exists and
holds a live grant status (`active` or `conditional`). A record that is
`denied`, `invalidated`, `revoked`, or absent MUST render the statement **not
substantiated**.

## 3. The conformance statement

A conformance statement is a small YAML record. Scaffold one with
`aies conform template [--class adopter|implementation]`:

```yaml
conformance_statement:
  claimant: <organization or person>
  aies_version: v0.4.0            # the AIES version claimed against
  class: adopter                  # or implementation
  assurance: evidence-backed      # self-asserted | evidence-backed | independently-reviewed
  reviewer: <name>                # required only for independently-reviewed
  date: <YYYY-MM-DD>
  claims:
    - statement: "Deployment <id> is qualified for CA-05 at RT2 — Moderate (AL2 — Collaborative)."
      evidence:
        qualification_record: QUAL-2026-001   # checked against the workspace
    - statement: "Human approval gates operate per AIES-AEOS-HO-01."
      evidence: {}                             # self-asserted; not tool-verifiable
```

[AIES-DOC-08-R04 — Conformance Guide, requirement 04] Every conformance statement MUST name the AIES version it
claims against. Conformance is always to a specific version — a claim against
v0.4.0 says nothing about a later version.

## 4. Checking a statement

```
aies conform check statement.yaml            # human-readable verdict
aies conform check statement.yaml --json     # machine-readable
aies conform check statement.yaml --write     # also persist a report artifact
```

The checker:
1. validates the statement's structure (§1–§3);
2. for each evidence-bearing claim, verifies the referenced Qualification
   Record exists in the workspace and is a live grant, reporting its actual
   scope so a reader can compare it to the claim text;
3. marks claims with no evidence as **self-asserted** (allowed, but not
   substantiation);
4. reports whether the statement as a whole is **substantiated** (per R03), and
   exits non-zero when an evidence-backed statement is not — so continuous
   integration can gate on it.

## 5. What conformance does and does not mean

- **It is scoped and versioned.** A conformance claim covers named deployments
  (or a named implementation) against a named AIES version — never "AIES
  conformant" in the abstract.
- **The tool checks evidence, not truth.** A verified claim means a live
  Qualification Record backs it — not that the qualification decision was
  correct. That correctness rests on the human authority who granted it
  ([PLATFORM.md D8](PLATFORM.md)), the rubric scoring, and the sample
  ([AIES-AESQS-CS-01 — Capability Scoring](../AESQS/capability-scoring.md)).
- **It is not a certificate issued by AIES.** AIES is an open standard, not a
  certifying body. A conformance statement is a claim the claimant publishes
  and stands behind; anyone can re-run `aies conform check` against the cited
  evidence to test it.
- **It is revocable in effect.** Because it references Qualification Records,
  and a record is invalidated when its environment changes (D7) or revoked
  after an incident, a previously-substantiated statement can cease to hold
  without being rewritten — re-checking reveals it.

## Related Documents

- [AIES-DOC-06 — Engineering Assessment Platform Specification](PLATFORM.md) — the `aies conform` command and the records it checks
- [AESQS Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](../AESQS/capability-scoring.md) — the requirements an implementation enforces
- [AESQS Qualification Process (AIES-AESQS-QP-01 — Qualification Process)](../AESQS/qualification-process.md) — how grants are made
- [AIES-DOC-07 — Standards Crosswalk — How AIES Maps to Adjacent Frameworks](CROSSWALK.md) · [AIES-GOV-01 — Governance](../GOVERNANCE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

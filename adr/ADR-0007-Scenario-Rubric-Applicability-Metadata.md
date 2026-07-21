# ADR-0007: Scenario rubric applicability metadata

| | |
|---|---|
| **ADR** | ADR-0007 |
| **Status** | Accepted |
| **Deciders** | Umair Ali (repository owner); Maintainers; Platform Module Editor; AESQS Module Editor |
| **Supersedes / Superseded by** | — |

## Context

The suite validator reports 124 warnings where a scenario rubric omits one or
more EV dimensions. Some omissions may be deliberate: a narrow task can be
unsuitable for a dimension. Others may be accidental coverage defects. The
single warning class makes those cases indistinguishable, reducing the signal
of validator output and tempting authors to add empty rubric text merely to
silence a warning.

The scenario schema currently permits a partial rubric. No field records why a
dimension is not applicable, and no engine decision rule may be weakened by
scenario metadata.

## Decision Drivers

- Preserve full EV1–EV6 scoring and existing decision/gate semantics.
- Make intentional non-applicability explicit, reviewable, and auditable.
- Continue to fail or warn on accidental omissions rather than hiding them.
- Keep the change additive and compatible with existing scenario files.

## Existing-Contracts Check

- **Can the existing contracts express this?** No. Existing scenario fields can
  omit a rubric dimension but cannot distinguish a reviewed non-applicability
  rationale from a missing authoring field.
- **If no, which contract is insufficient, and what version bump / conformance
  impact does the change carry?** The scenario schema needs an additive,
  validator-owned metadata field. It must not modify the evidence envelope,
  scoring constants, result schema, or RuntimeAdapter contract. The precise
  schema/version treatment requires compatibility review before acceptance.

## Options Considered

### Option A — Require every scenario rubric to cover every EV dimension

- **Pros:** Simple validator output.
- **Cons:** Encourages invented anchors where a dimension is not meaningfully
  exercised and rewrites valid narrow instruments solely for uniformity.

### Option B — Leave all omissions as undifferentiated warnings

- **Pros:** No schema change.
- **Cons:** 124 warnings obscure defects and provide no record of author intent.

### Option C — Add reviewed applicability metadata (proposed)

Add a scenario-level mapping that may declare a missing EV dimension
non-applicable only with a concise rationale. The validator distinguishes a
declared, valid exception from an unexpected omission; a report surfaces both.

- **Pros:** Makes intent auditable without inventing evidence; retains a strong
  signal for unreviewed gaps; additive.
- **Cons:** Requires a controlled migration and reviewer judgement; authors may
  misuse it to avoid writing difficult anchors.

## Decision

This ADR adopts Option C. A scenario may carry only an additive metadata block
of this shape:

```yaml
rubric_applicability:
  EV5:
    status: not_applicable
    rationale: "The task evaluates a fixed-policy escalation decision; it has no performance or resource-efficiency behavior to assess."
```

The validator MUST reject unknown dimensions, unknown status values, empty
rationales, and a declaration for a dimension that the rubric already covers.
It MUST continue to warn for every uncovered dimension without a valid
declaration. Reports MUST expose declared non-applicability separately from
unexpected omissions. This metadata MUST NOT change scoring anchors, evidence
minimums, gates, autonomy limits, or outcome semantics.

Migration is human-reviewed: each current warning is classified as either
add-the-missing-rubric, declare-not-applicable-with-rationale, or revise/split
the scenario. Bulk suppression is prohibited.

## Consequences

**Positive:** Validator output becomes actionable and intentional scope limits
are traceable to the scenario.

**Negative:** More authoring metadata and review work. Mitigation: migrate one
area at a time, require a concrete rationale, and retain warnings for all
undeclared omissions.

## Compliance & Verification

- Tests cover valid declarations, all invalid declaration forms, and undeclared
  omissions.
- `aies suites validate` reports declared exclusions and unexpected omissions
  separately.
- A migration report records the disposition of each existing warning.
- Scoring, qualification, and grants are unchanged for a scenario whose
  metadata is added.

## Links

- [ADR-0002 — Qualification Platform](ADR-0002-Qualification-Platform.md)
- [ADR-0005 — Assessment-as-Code](ADR-0005-Assessment-as-Code.md)
- [Scenario authoring guide (AIES-PLAT-07)](../platform/SCENARIOS.md)
- [OSS Maturity TODO (AIES-DOC-10)](../docs/OSS_MATURITY_TODO.md)

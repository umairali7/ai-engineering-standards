# Qualification Profiles

| | |
|---|---|
| **Document ID** | AIES-PLAT-02 |
| **Status** | Draft |
| **Audience** | Engineering leadership · Assessors & qualification authorities · Platform teams |

A **profile** is a weighting preset that expresses an organization's emphasis
when qualifying a deployment. It changes *how much each competency area and
each evaluation dimension counts* — never the pass/fail thresholds. The gates
and statistical minimums are engine constants from
[AIES-AESQS-CS-01](../AESQS/capability-scoring.md); **no profile can relax
them** (PLATFORM.md design decision D3). A profile makes a qualification
emphasize what you care about; it can never make an unsafe model look safe.

## How a profile works

Two knobs, both bounded:

- **`area_weights`** — relative emphasis across competency areas
  [CA-01…CA-12](../AESQS/competency-framework.md). An area at weight `2.0`
  counts twice as much toward the overall picture as one at `1.0`; unlisted
  areas default to `1.0`. This shapes *which competencies dominate the summary*.
- **`dimension_weight_adjustments`** — small shifts (±0.05 max per dimension,
  per [AIES-AESQS-CS-01-R03](../AESQS/capability-scoring.md)) to the per-tier
  [EV1–EV6](../Shared/Taxonomy/README.md#8-evaluation-dimensions-ev1ev6) weights.
  The Profile Loader rejects any adjustment beyond the bound, any set that
  fails to sum to 1.0, or any that drops the combined EV3+EV6 (safety +
  traceability) weight below the RT3/RT4 floor.

What a profile **cannot** touch: the EV3 safety gate, the EV1/EV6 gates, the
per-tier minimum sample sizes, or the confidence level. Those are the standard.

## Shipped profiles

| Profile | Emphasis | Area weights | Dimension shifts |
|---------|----------|--------------|------------------|
| **enterprise** | Traceability- and safety-weighted, for regulated delivery | CA-06 ×1.2, CA-12 ×1.5 | EV6 +0.05, EV5 −0.05 |
| **coder** | Implementation-heavy, for engineering-focused deployment | CA-05 ×2.0 | EV1 +0.05, EV5 −0.05 |
| **architect** | Design and trade-off reasoning | CA-04 ×2.0, CA-05 ×0.8 | EV4 +0.05, EV5 −0.05 |
| **security** | Safety-first, for security-sensitive scopes | CA-07 ×2.0 | EV3 +0.05, EV5 −0.05 |
| **startup** | Velocity-conscious, for low-regulation contexts | CA-05 ×1.5 | EV5 +0.05, EV4 −0.05 |
| **research** | Exploration-oriented; areas unweighted | (none) | (none) |

```
aies profile list                 # all profiles with descriptions
aies profile show enterprise      # the full weighting preset
aies profile validate ./mine.yaml # check a custom profile against the bounds
```

## Writing your own

Copy a shipped profile from `platform/profiles/`, adjust the weights, and pass
the file path to `--profile`. A profile is plain YAML:

```yaml
name: my-team
version: 1.0.0      # semver — bump when you change the weights (see below)
description: What this profile emphasizes and why
area_weights:
  CA-05: 1.5        # weight the areas your deployment will actually do
  CA-07: 1.2
dimension_weight_adjustments:
  EV6: +0.05        # at most ±0.05; must keep weights summing to 1.0
  EV5: -0.05
# gates and sample minimums are NOT expressible here (D3)
```

`aies profile validate <file>` confirms it stays within the standard's bounds
before you use it.

**Version your profile.** A profile is a *versioned normative artifact*: changing
the weights changes what "enterprise" means, so bump the `version` when you do.
The version used is **captured at run time** and stamped into the evidence
package and the Canonical Assessment Result — a later edit to the profile file
can never silently reinterpret a past certification. Two results under the same
profile *name* but different profile *versions* are correctly distinguishable.
An unversioned profile still loads, but is recorded as `0.0.0` (UNVERSIONED) —
which is exactly the ambiguity versioning exists to remove.

## Related Documents

- [Capability Scoring (AIES-AESQS-CS-01)](../AESQS/capability-scoring.md) — the weights, gates, and minimums profiles operate within
- [Competency Framework (AIES-AESQS-CF-01)](../AESQS/competency-framework.md) — the CA-01…CA-12 areas
- [Platform Specification (AIES-DOC-06) §5.2, §6](../docs/PLATFORM.md)
- [Deployments (AIES-PLAT-03)](DEPLOYMENTS.md) · [Guide (AIES-PLAT-01)](GUIDE.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

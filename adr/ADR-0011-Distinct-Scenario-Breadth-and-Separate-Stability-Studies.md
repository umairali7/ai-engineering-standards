# ADR-0011: Count distinct scenario breadth and separate stability studies

| | |
|---|---|
| **ADR** | ADR-0011 |
| **Status** | Accepted |
| **Deciders** | Umair Ali (repository owner); Platform Module Editor; AESQS Module Editor |
| **Decision date** | 2026-07-22 |

## Context

The platform previously reached statistical sample minima by automatically
executing each of roughly ten RT2 scenarios two or three times. This measured
same-prompt variation, but it also let repeated observations stand in for task
breadth. An all-area RT2 run therefore planned 341 candidate requests while
still leaving five Engineering Tasks entirely unmapped. The resulting sample
size was formally large but behaviorally narrow.

Exact reruns are useful for empirical stability work. They are not independent
measurement instruments and must not repair missing scenario or task coverage.

## Decision

1. Per-area qualification minima count **distinct scenario instruments**, not
   repeat observations or multiple raters of the same response.
2. Every selected scenario executes once by default. `repeats_min` remains
   advisory metadata for corpus calibration and is never an implicit execution
   instruction.
3. Exact repeat runs occur only when explicitly requested for a stability
   study. All executed repeats remain reportable under the anti-cherry-picking
   rule, but they do not increase distinct-scenario sample adequacy.
4. Run-to-run variance is evaluated in empirical calibration, periodic
   stability studies, or ongoing verification. A material EV1 or EV3 stability
   breach still fails or suspends the affected claim.
5. Corpus breadth must be expanded with genuinely distinct, calibrated
   instruments rather than generated paraphrases.

## Consequences

- RT2 requires at least 30 distinct scenarios per competency area.
- `--decisional` rejects a thin suite instead of increasing repeats.
- Default qualification is less wasteful and produces broader capability
  evidence; explicit stability studies remain available with `--repeats`.
- The engine, reports, documentation, and conformance mapping must distinguish
  raw observations from distinct scenario adequacy.
- Existing run artifacts retain their original sampling rule and are not
  reinterpreted retroactively.

## Existing-contract check

The prior wording of AIES-AESQS-CS-01-R10 and R13 coupled minimum samples to
same-prompt repeats. Those requirements are revised by this accepted ADR;
sample thresholds, confidence intervals, gates, and anti-cherry-picking rules
do not change.

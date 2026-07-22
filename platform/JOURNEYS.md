# Journeys — Testing Lifecycle Depth

| | |
|---|---|
| **Document ID** | AIES-PLAT-05 |
| **Status** | Draft |
| **Audience** | Engineers · Platform teams · Assessors & qualification authorities |

Competency suites test **breadth** — can the model do requirements work, or
architecture, or testing, each on its own? A **journey** tests **depth**: can
the model carry *one piece of work through the SDLC*, where each phase must
build on the model's own output from the phase before?

This is the most AIES-native test there is. The whole premise of AIES is AI
participating across the *complete* lifecycle; a journey is where the platform
actually exercises that.

## How a journey differs from a suite

| | Competency suite | Journey |
|---|---|---|
| Shape | independent single-turn scenarios | ordered steps, chained |
| Threading | none | each step is given the model's prior step output |
| Tests | breadth (one competency at a time) | depth (does phase N follow from phase N−1?) |
| Scored | per area | per step, attributed to that step's competency area |

A journey does **not** replace suites — it complements them. Suites get you to
decisional sample sizes; journeys reveal whether the model's phases actually
cohere (does the architecture serve the requirement it just wrote? do the tests
cover the implementation's real edge cases?).

## Shipped journeys

| ID | Title | Phases it carries work through |
|----|-------|--------------------------------|
| **JOURNEY-01** | Feature delivery — requirement to release readiness | CA-02 requirements → CA-04 architecture → CA-05 implementation → CA-06 tests → CA-10 release & oversight |
| **JOURNEY-02** | Incident to fix — diagnosis to post-incident governance | CA-09 diagnosis → CA-05 fix → CA-06 regression test → CA-12 post-incident review |

```
aies journey list             # all journeys and their steps
aies journey show JOURNEY-01   # the full step definitions
aies qualify <deployment> --journey JOURNEY-01 --profile enterprise
```

## How it runs

Steps execute in order. Each step's prompt is a template that may pull in the
model's earlier output:

- `{{prior_response}}` — the immediately preceding step's response.
- `{{prior}}` — a formatted transcript of all prior steps.

Every step is recorded as an ordinary response record tagged with its
competency area and the journey's risk tier, so the **existing pipeline
consumes journeys unchanged** — `score`, `qualify --resume`, `report`,
`grant`, `verify` all work exactly as for a suite run. The evidence package
simply has one competency area per step.

## Interpreting journey results

- A single journey yields **one scored item per area** — so journeys are
  **depth, not sample volume**. They are labelled NON-DECISIONAL on their own;
  combine repeats and several journeys (or pair with suite runs) to reach
  decisional sizes. This is intentional: a journey's value is showing whether
  the phases cohere, which a human reads directly from the transcript.
- Journeys are scored at one declared risk tier (JOURNEY-01 at RT2 — Moderate, JOURNEY-02
  at RT3 — Significant), so the gates reflect the stakes of the work being carried.

## Authoring a journey

Add a YAML file under `platform/journeys/`:

```yaml
id: JOURNEY-03
title: <what work this carries and through which phases>
risk_tier: RT2                 # RT2 — Moderate; the tier the whole journey is scored at
steps:
  - id: J03-S1-<phase>
    area: CA-02                 # a competency area (CA-01…CA-12)
    phase: P05 Requirements     # informational label
    prompt: |
      <the task for this phase>
    expected_qualities: [ <observable properties> ]
    rubric: { EV1: [...], EV6: [...] }
    failure_conditions: [ "<observable failure>  # -> EVn" ]
    weight: 1.0
  - id: J03-S2-<phase>
    area: CA-04
    phase: P07 Architecture
    prompt: |
      Given your prior work:
      {{prior_response}}
      Now ...
    ...
```

Step ids are unique within the journey; `area` must be a real CA-01…CA-12 code.
`aies journey show <id>` validates and displays it.

## Related Documents

- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)
- [AIES-PLAT-01 — AIES Platform — Architecture & Run Guide](GUIDE.md) · [AIES-PLAT-03 — Deployments — Qualify Deployments, Not Models](DEPLOYMENTS.md) · [AIES-PLAT-02 — Qualification Profiles](PROFILES.md)
- [Competency Framework (AIES-AESQS-CF-01 — Competency Framework)](../AESQS/competency-framework.md) — the CA areas steps map to
- [AIES-DOC-04 — SDLC Reference](../docs/SDLC.md) — the phases journeys traverse

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

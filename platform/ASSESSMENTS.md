# Assessments — Engineering Composition as Code

| | |
|---|---|
| **Document ID** | AIES-PLAT-08 |
| **Status** | Draft |
| **Audience** | Assessment authors · Assessors · Platform teams |

An **assessment** is a named engineering scope composed as **declarative data**:
which competencies make it up, whether each is mandatory or advisory, how much
each weighs, the EV-weighting profile, and sampling. Adding a new assessment
is `git add assessments/finance.yaml`, not a code change. Design and rationale:
[ADR-0005](../adr/ADR-0005-Assessment-as-Code.md).

Assessment authors declare **what to assess and how much it matters**. The engine
owns **how it decides** — the decision algorithm, gate semantics, statistical
minimums, AL caps, and outcome precedence. An assessment can never weaken any of
those (the validator enforces a strict allowed-key schema).

## Run one

```
aies assessment list                                  # the shipped assessments
aies qualify <deployment> --assessment enterprise --judge <judge>   # compose, score, analyze
aies assessment result <run>                          # Engineering Assessment Result
aies assessment result <run> --json                   # COMPLETE/PARTIAL/NOT SCORED
aies assessment result <run> --format html --out result.html   # presentation-grade view

# Explicit formal qualification:
aies qualify <deployment> --assessment enterprise --formal-qualification
aies assessment result <run> --formal-qualification
```

The default Markdown, JSON, and HTML renderers are views of the same
non-blocking Engineering Assessment Result. Automated coverage can complete it;
human evaluation is optional and shown separately. The HTML is self-contained,
theme-aware, and print-ready.

`--assessment` selects the competency set, profile, risk tier, and sampling; the
resolved assessment is recorded immutably in the run manifest. After scoring +
aggregation, the platform records engineering completion and observed results.

## Engineering result (default)

| Status | Meaning |
|---|---|
| **COMPLETE** | every mandatory competency has complete automated, human, or mixed score coverage |
| **PARTIAL** | at least one mandatory competency has scores, but coverage is incomplete |
| **NOT SCORED** | no mandatory competency has scored evidence |

These statuses describe execution and evidence coverage. They are not a
qualification, grant, or deployment authorization.

## Formal outcome (explicit)

`--formal-qualification` selects the governed decision engine. Its result is
one of the following, decided over the **mandatory** competencies:

most-severe wins (`FAIL > INCONCLUSIVE > INSUFFICIENT EVIDENCE > PASS`):

| Outcome | Meaning |
|---|---|
| **PASS** | every mandatory competency is decisional, passes its gates, and meets any `min_cl` |
| **FAIL** | a mandatory competency is decisional but fails a gate or `min_cl` |
| **INCONCLUSIVE** | a mandatory competency's evidence is present but ambiguous, or it wasn't evaluated |
| **INSUFFICIENT EVIDENCE** | a mandatory competency lacks enough scored evidence to decide |

A strong competency **never** offsets a failing one — there is no blended score.
`PASS` is an *assessment outcome*, not a deployment decision: a named human still
records any grant/certification (`Assessment PASS → certification →
production-ready`).

**Evidential maturity by tier.** An assessment's `default_risk_tier` states its
*ambition*; whether the corpus can *decisively* support that tier depends on how
many **distinct** high-tier scenarios back each mandatory area (a decisional RT3 — Significant
run needs far more than repeats of a handful of prompts — see
[CALIBRATION.md §5](CALIBRATION.md)). Describe this honestly, e.g. *"RT2 — Moderate:
decisional. RT3 — Significant: operationally ready; an expanded distinct-scenario corpus is
required for decisional confidence."* The platform already labels under-sampled
runs NON-DECISIONAL, but stating maturity up front keeps claims credible.

## Three reporting layers

1. **Normative (authoritative):** per-mandatory PASS/FAIL + overall outcome + structured reasons.
2. **Diagnostic (informational):** per-area numeric scores — engineering feedback.
3. **Analytics (non-authoritative):** coverage, mandatory pass-rate, weighted summaries — dashboards/trends, never a verdict.

AIES deliberately publishes **no single "82/100"** — a comparable headline turns
a conformity framework into a leaderboard.

## Author an assessment

```yaml
id: finance                    # stable identifier
version: 1.0.0                 # CONTENT version — certifications cite this
schema: 1                      # file-format version (engine-owned)
description: Finance-grade AI-native SDLC engineering assessment.
profile: enterprise            # an existing profiles/*.yaml (EV weighting)
default_risk_tier: RT3       # RT3 — Significant
competencies:
  - area: CA-07                # Security & Privacy
    requirement: { type: mandatory }
    weight: 30
    min_cl: CL3                # optional per-area floor
  - area: CA-12                # Governance, Risk & AI Safety
    requirement: { type: mandatory }
    weight: 30
  - area: CA-05                # Implementation
    requirement: { type: mandatory }
    weight: 25
  - area: CA-09                # Operations — informational only
    requirement: { type: advisory }
    weight: 15
```

- **`requirement`** is an object (`{ type: mandatory | advisory }`), leaving room
  for future types. **Mandatory** competencies decide the outcome; **advisory**
  ones are scored and reported but never fail an assessment.
- **`weight`** governs composition, execution priority, and reporting emphasis —
  it **never** compensates for a failed gate or mandatory requirement.
- Shipped assessments execute every selected scenario once. Exact repeats are
  requested explicitly with `--repeats N` only for a separately identified
  stability study; they never increase distinct-scenario breadth or repair a
  qualification sample minimum (ADR-0011).
- The optional legacy-compatible `sampling.repeats` field can only raise raw
  observation volume. New general-purpose assessments SHOULD omit it; a
  specialized stability assessment MUST say so in its identity and description.

Validate before committing:

```
aies assessment validate ./assessments/finance.yaml
```

The validator rejects: unknown/engine-owned keys, unknown or duplicate
competencies, non-positive weights, no mandatory competency, an orphan profile
reference, bad `id`/`version`/`schema`, and sub-minimum sampling.

Every shipped assessment is also validated by `aies suites validate` — the same
gate CI runs — so a broken assessment file cannot merge silently:

```
aies suites validate     # areas + scenarios + shipped assessments, one gate
```

## Reproducibility

Every result carries **immutable execution metadata** (assessment id/version/
schema, profile, platform + AIES version, runtime + model fingerprint,
timestamp) so a certification is traceable to its exact inputs and drift is
explainable — *"why did this pass in July but fail today?"*. Results are
comparable only across identical assessment **content versions**.

## Related Documents

- [ADR-0005 — Assessment-as-Code](../adr/ADR-0005-Assessment-as-Code.md)
- [AIES-PLAT-01 — AIES Platform — Architecture & Run Guide](GUIDE.md) · [AIES-PLAT-02 — Qualification Profiles](PROFILES.md) · [AIES-PLAT-07 — Authoring Competency Scenarios](SCENARIOS.md)
- [Capability Scoring (AIES-AESQS-CS-01 — Capability Scoring)](../AESQS/capability-scoring.md) — the per-area scoring assessments compose
- [AIES-DOC-06 — Engineering Assessment Platform Specification](../docs/PLATFORM.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

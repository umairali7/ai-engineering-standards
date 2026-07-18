# Assessments — Qualification Composition as Code

| | |
|---|---|
| **Document ID** | AIES-PLAT-08 |
| **Status** | Draft |
| **Audience** | Assessment authors · Assessors · Platform teams |

An **assessment** is a named qualification composed as **declarative data**:
which competencies make it up, whether each is mandatory or advisory, how much
each weighs, the EV-weighting profile, and sampling. Adding a new qualification
is `git add assessments/finance.yaml`, not a code change. Design and rationale:
[ADR-0005](../adr/ADR-0005-Assessment-as-Code.md).

Assessment authors declare **what to assess and how much it matters**. The engine
owns **how it decides** — the decision algorithm, gate semantics, statistical
minimums, AL caps, and outcome precedence. An assessment can never weaken any of
those (the validator enforces a strict allowed-key schema).

## Run one

```
aies assessment list                                  # the shipped assessments
aies qualify <deployment> --assessment enterprise --judge <judge>   # compose, score, decide
aies assessment result <run>                          # re-decide an aggregated run (no inference)
aies assessment result <run> --json                   # the Canonical Assessment Result object
aies assessment result <run> --format html --out result.html   # presentation-grade view
```

The Markdown, JSON, and HTML renderers are **views of the same Canonical
Assessment Result** — they never re-decide. The outcome shown is verbatim from
the frozen decision engine; the HTML is a single self-contained, theme-aware,
print-ready file (browser "Save as PDF" gives the PDF deliverable).

`--assessment` selects the competency set, profile, risk tier, and sampling; the
resolved assessment is recorded immutably in the run manifest. After scoring +
aggregation, the platform decides the **outcome** and appends it to the report.

## The outcome (authoritative)

An assessment result is one of — decided over the **mandatory** competencies,
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
many **distinct** high-tier scenarios back each mandatory area (a decisional RT3
run needs far more than repeats of a handful of prompts — see
[CALIBRATION.md §5](CALIBRATION.md)). Describe this honestly, e.g. *"RT2:
decisional. RT3: operationally ready; an expanded distinct-scenario corpus is
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
description: Finance-grade AI-native SDLC qualification.
profile: enterprise            # an existing profiles/*.yaml (EV weighting)
default_risk_tier: RT3
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
sampling:
  repeats: 3
```

- **`requirement`** is an object (`{ type: mandatory | advisory }`), leaving room
  for future types. **Mandatory** competencies decide the outcome; **advisory**
  ones are scored and reported but never fail an assessment.
- **`weight`** governs composition, execution priority, and reporting emphasis —
  it **never** compensates for a failed gate or mandatory requirement.
- Everything under `sampling`/gates/minimums is bounded by the engine: an
  assessment can only *raise* effective volume, never lower a gate or minimum.

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
- [Guide (AIES-PLAT-01)](GUIDE.md) · [Profiles (AIES-PLAT-02)](PROFILES.md) · [Scenarios (AIES-PLAT-07)](SCENARIOS.md)
- [Capability Scoring (AIES-AESQS-CS-01)](../AESQS/capability-scoring.md) — the per-area scoring assessments compose
- [Platform Specification (AIES-DOC-06)](../docs/PLATFORM.md)

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

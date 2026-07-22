# Empirical Calibration Study — Template

| | |
|---|---|
| **Document ID** | AIES-RES-TMPL-EC |
| **Status** | Template |
| **Audience** | Contributors & maintainers · Reviewers |
| **Companion** | [platform/CALIBRATION.md](../platform/CALIBRATION.md) (the harness & metrics) |

A completed study is filed as `RES-NN-YYYY-empirical-calibration-<assessment>.md`
using this structure. Research is **informative, never normative** (research
README): a study reports what a model panel showed; the promotion of any
scenario's `empirical_status.empirically_calibrated` is a separate human decision
that *cites* the study.

> **Pre-register before you run.** The **Method** section below — panel
> composition, selection rationale, the methodology and thresholds versions and
> values, the scenario set, and repeats — is fixed and dated **before** any run is
> collected or scored, mirroring the anti-cherry-picking rule for qualification
> evidence ([AIES-AESQS-CS-01-R12 — Evidence populations are pre-registered and complete](../AESQS/capability-scoring.md)). Findings are
> filled in afterward against that frozen design. Recording thresholds *after*
> seeing results, adding or dropping panel models to move a verdict, or narrowing
> the scenario set post-hoc invalidates the study exactly as it would a
> qualification.

---

## Question

*State the specific question.* e.g. "Do the design-time-calibrated scenarios of
the `security` assessment empirically discriminate weak from strong engineering
capability across a real model panel, repeatably and without gaming?"

## Method *(pre-registered — fix and date this before running)*

- **Panel composition** — the participating models, each with an assigned ability
  rank. Include enough of a spread that discrimination is measurable (a floor and
  a ceiling), and record model identity + version + provenance (the harness
  captures `run_id` and checksum per model).
- **Selection rationale** — *why these models*: how the ability ranks were
  assigned (independent benchmark, expert consensus, prior qualification), and why
  the panel is a fair, non-circular basis for measuring discrimination. Name the
  conflicts of interest considered.
- **Scenario set** — which competency areas / assessment, how many distinct
  scenarios, and the sampling rule (repeats per scenario), registered up front.
- **Scoring** — who/what scores (human raters, or a calibrated judge model — note
  the judge is itself an instrument, cf. `SC-CA06-012`) and the rater-reliability
  check.
- **Methodology & thresholds** — the harness `methodology_version` and
  `thresholds_version`, **and the exact threshold values** used
  (`discrimination_min`, `ceiling_min`, `floor_max`, `repeatability_max_std`,
  `twin_gap_max`). These travel in the result `metadata`; restate them here so the
  frozen design is legible without the JSON.
- **Assembly** — `aies suites empirical --runs <run>=<ability> … --panel-id <id>
  --write-panel panel.json`. Attach `panel.json` and the result JSON.

## Findings *(post-run — report against the frozen design)*

- **Observed discrimination** — per-scenario and aggregate: how strongly scores
  separated the ability groups, monotonicity across the panel.
- **Repeatability** — score stability across repeats (per-model, per-scenario).
- **Ceiling reach / live floor** — did strong models reach the ceiling and weak
  models actually sink? Where the ceiling was unreached, note it.
- **Twin robustness** — hold-out-twin consistency; any scenarios where a model
  aced one form and failed its twin (gaming signal).
- **Per-scenario verdicts** — the harness partition: *empirically calibratable*
  vs *flagged* (`low-discrimination`, `too-easy`, `ceiling-unreached`, `noisy`,
  `gameable`), with counts per area.
- **Reproducibility block** — paste the result `metadata` (panel id, participating
  models, methodology/thresholds versions + values, `analyzed_at`).

## Limitations

State them honestly — this is what makes the study trustworthy:

- **Panel size and diversity** — how few models, how correlated their training,
  how the ability ranking might be wrong.
- **Scoring reliability** — inter-rater agreement, or judge-model bias/variance
  and its own (un)calibration.
- **Construct validity** — does the ability rank measure the *engineering*
  capability the scenario targets, or a proxy (fluency, verbosity)?
- **Generalization** — the panel is a sample; results are indicative for models
  outside it, not decisive.
- **Mock caveat** — any run against the mock runtime is a mechanics check, never
  capability evidence.

## Implications

- **Scenarios requiring revision** — the flagged scenarios and the specific fix
  each needs (raise the ceiling, add a floor, resolve a gameable twin, reduce
  noise). This is the study's most actionable output.
- **Evidential maturity** — which assessments’ tier claims the findings support or
  qualify (e.g. does `security` now have RT3 — Significant-decisional backing?).
- **`empirical_status` promotions** — the scenarios a human may promote to
  `empirically_calibrated: true`, each citing this study.
- **Threshold observations** — if a threshold looks mis-set, propose a change *as
  a proposal* (a new `thresholds_version`), never a silent edit; re-analysis under
  a new version is a new, separately-recorded finding.

## References

- [platform/CALIBRATION.md](../platform/CALIBRATION.md) — the harness, metrics, and metadata contract
- [AIES-AESQS-CS-01 — Capability Scoring §6, R12](../AESQS/capability-scoring.md) — statistical minimums; register-before-scoring
- The panel models (identity + version) and the assessment under study
- The assembled `panel.json` and the empirical-calibration result JSON (attach)

# Project Evaluation and Engineering Capability Matrix Direction

| | |
|---|---|
| **Document ID** | AIES-DOC-11 |
| **Status** | Draft |
| **Audience** | Maintainers, contributors, adopters |

This is a dated, non-normative assessment of the repository and a record of
recommended product direction. It is not a conformance claim or a replacement
for the evidence produced by the AIES platform.

## Assessment Summary

The project has a strong technical and governance foundation. Its principal
distinction is executable assurance: a vendor-neutral standard is connected to
scenario suites, versioned evidence packages, a deterministic decision engine,
and human-recorded grants. This is more credible and useful than a prose-only
framework.

At the time of this assessment, the qualification platform had 12 competency
areas, 200 scenarios, 163 passing tests, a passing suite validator (with
warnings), and a passing 8-case decision-engine conformance corpus. These are
repository observations, not a claim of external validation.

## Strengths

- Coherent five-module structure: knowledge, qualification, operations,
  architecture, and certification share a canonical taxonomy and glossary.
- Governance is executable: ADRs, change classes, evidence records, CI, and
  conformance checks reinforce the standard's stated principles.
- Qualification decisions correctly retain human accountability and distinguish
  evidence from a grant.
- The platform is a real implementation, with reproducible, plain-data
  artifacts, offline execution paths, runtime-adapter boundaries, and
  data-first decision-engine conformance.
- The assessment corpus treats scenarios as measurement instruments and openly
  reports coverage, duplication, diversity, and empirical-maturity limitations.

## Priority Recommendations

### P0 — unblock external adoption

1. Finalize and apply repository licensing, including a clear code-versus-
   documentation boundary where appropriate. Until then, reuse and contribution
   are materially constrained.
2. Publish reproducible, independently reviewed runs against at least one local
   and one hosted deployment. Each publication should include the immutable
   Evidence Package, rater/judge method, suite/profile versions, limitations,
   and human decision status.
3. Replace public-project placeholders: repository discussion and security
   links, security contact, conduct contact, and named maintainership route.

### P1 — make the measurement system decision-ready

4. Grow each competency area into versioned public and held-out scenario sets.
   Preserve the distinction between exploratory/smoke coverage and decisive
   evidence; do not label an undersized sample as qualification evidence.
5. Run the existing empirical-calibration methodology on a pre-registered,
   diverse real-model panel. Publish discrimination, repeatability, rater
   agreement, ceiling/floor behavior, and scenario revisions.
6. Triage suite-validation warnings. Where partial EV coverage is deliberate,
   encode that intent so new or accidental coverage gaps remain visible rather
   than being lost in a large warning count.
7. Add the missing repository assurance controls identified by the project's
   own audit: dependency locking, SBOM/AI-BOM generation, secret scanning/SAST,
   CODEOWNERS/review evidence, and branch-protection attestation.

### P2 — improve maintainability and adoption

8. Add CI for Markdown/relative-link validation and documentation consistency.
   Key counts and claims should be generated or tested: for example, older
   documentation refers to 189 scenarios whereas the validated corpus contains
   200.
9. Add Python quality/security checks proportionate to the project: formatting,
   linting, static type checking, coverage reporting, and dependency audit.
10. Narrow the initial adoption wedge. A strong first offer is deployment
    qualification plus repository conformance for teams operating AI-assisted
    engineering in regulated or high-assurance contexts.

## Product Direction: Three Complementary Views

Qualification evidence answers a governance question: *is there sufficient,
appropriately scoped evidence for a named human authority to record a grant?*
It should remain gate-first, risk-scoped, and non-compensatory.

Engineers and decision makers need different, legitimate questions answered
from the same underlying evidence. The platform should provide three clearly
labeled views, none of which changes a qualification decision:

| View | Primary reader | Question answered | Constraints |
|---|---|---|---|
| Qualification Report | Governance and assurance | Is the evidence sufficient for a scoped decision? | Existing evidence, gates, sample adequacy, and human-grant boundary remain authoritative. |
| Engineering Capability Matrix (ECM) | Engineers and platform teams | What engineering tasks and task families is this subject comparatively strong or weak at? | Derived only from scored scenario evidence; always show sample size, uncertainty, risk tier, and decisional status. |
| Deployment Model Card | CTOs, procurement, and risk owners | Where should we use this deployment, and under what controls? | A bounded decision aid; must state unsupported uses, residual risk, and that it is not a grant. |

The existing `aies capabilities` command is a useful first layer: it presents
per-competency-area results side by side. The proposed Engineering Capability
Matrix is a finer-grained, evidence-derived extension, not a replacement.

The intended data path is:

```text
Assessment -> Canonical Evidence -> Competency Analysis
-> Engineering-task mapping -> Engineering Capability Matrix -> audience views
```

The matrix must be subject-neutral. It should describe a deployment, agent,
repository, AI system, or another assessable subject—not only a bare model.

## Engineering Capability Matrix Design Principles

1. **Use task-family metadata, not a model-written summary.** Start with the
   existing scenario `family` field (CA-05 already distinguishes
   implementation, refactoring, defect-fix, and escalation). Add a controlled
   `capability_tags` field only where the existing family is too broad (for
   example `api-design`, `debugging`, `testing`, `performance`, or
   `security-review`). Tags require a taxonomy, contributor guidance, and
   review because they become part of the measurement model.
2. **Report observations, never invented behavioral claims.** A strength must
   link to the contributing scenario IDs, score distribution, evaluator type,
   and sample count. “18/21 maximum EV1 scores” is defensible; “excellent API
   designer” is not, unless a defined metric supports it.
3. **Do not turn sparse evidence into percent certainty.** For the supplied
   CA-05 example, 21 items are below the 30-item minimum. A matrix may show
   exploratory signals, but must be marked **NON-DECISIONAL / preliminary**;
   stars or percentages must not imply validated capability.
4. **Preserve risk and safety as non-compensatory.** A high average in
   implementation cannot neutralize a failed security gate. Recommended uses
   must respect the applicable risk tier and autonomy envelope.
5. **Separate fact, inference, and recommendation.**
   - *Evidence:* scored scenario results and confidence intervals.
   - *Matrix inference:* a transparent calculation over task mappings and dimensions.
   - *Recommendation:* a human-approved deployment policy, with conditions.
6. **Make comparisons fair.** Compare deployments only where the suite version,
   risk tier, repeats, rater/judge protocol, and evidence sufficiency are
   comparable. Otherwise show the difference as non-comparable, not as a
   leaderboard.

## Suggested Output Shape

```text
Engineering Capability Matrix — exploratory (non-decisional)
Subject: local-qwen3-coder-next-8but | CA-05 | RT2
Evidence: 21 scored items / 30 required; judge-produced ratings

Task family              Evidence-derived signal       Coverage
Implementation           high EV1 lower bound          scenario IDs + n
Refactoring              insufficient evidence         scenario IDs + n
Performance optimization insufficient evidence         scenario IDs + n

Observed strengths
- 18/21 scenarios had maximum EV1 score. [scenario IDs]

Limitations and cautions
- Results are non-decisional because n=21 < 30.
- Ratings were produced by the named judge; human spot-check is required.
- This CA-05 run does not establish architecture, security-review, or
  autonomous-production capability.
```

“Best fit” should appear only as a policy layer with explicit conditions, e.g.
“appropriate for human-reviewed RT2 implementation tasks within the recorded
autonomy envelope.” It should not infer that a model is safe for security-
critical work merely because it performs well on general coding tasks.

## Recommended Delivery Sequence

1. Publish the actual-run Evidence Packages and reproduce them under a defined
   evaluator protocol.
2. Render CA-05's existing scenario families first; add controlled tags and
   schema validation only for the distinctions that families cannot express.
3. Build a JSON/Markdown Engineering Capability Matrix renderer from canonical evidence;
   include scenario IDs, n, confidence intervals, evaluator provenance, and
   explicit non-decisional labels.
4. Add profile-focused tests for no unsupported claims, no cross-suite
   comparison, no gate bypass, and correct sparse-evidence behavior.
5. Add a human-reviewed Deployment Model Card template that consumes—not
   recomputes—the canonical Qualification Result and Engineering Capability Matrix.
6. Extend comparisons to matched runs, producing task-family deltas only where
   protocol compatibility is established.

## Interpretation of the Supplied First Run

The supplied CA-05 run is promising exploratory evidence: all reported
dimension decision values exceed their gates and the aggregate is high. It is
not a qualification result and cannot substantiate broad claims because it is
explicitly non-decisional (21 scored items against a minimum of 30), covers
only CA-05 at RT2, and used heuristic judge ratings. It supports the need for a
matrix that communicates *what was observed* while carrying those limits
forward, not a profile that converts a partial sample into product marketing.

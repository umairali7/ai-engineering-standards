# ADR-0005: Assessment-as-Code — declarative competency composition above profiles

| | |
|---|---|
| **ADR Number** | 0005 |
| **Status** | Accepted |
| **Deciders** | Maintainers; Platform Module Editor; AESQS Module Editor |
| **Supersedes** | — |
| **Superseded by** | — |

## Context

Today a qualification is assembled at the command line: the operator names a
**profile** (an EV-dimension weighting preset) and lists the **competency
areas** by hand (`--profile enterprise --area CA-04 --area CA-05 …`). The engine
is already pleasingly data-driven — the profiles `enterprise`, `coder`,
`security`, etc. are **YAML files**, not code; `grep` for those names in
`profiles.py`/`scoring.py` finds nothing, and the [RuntimeAdapter](../platform/RUNTIMES.md)
is frozen at contract v1.0. So the engine does not "know" what *Enterprise*
means — good.

But there is no first-class object that says **"the Enterprise qualification is
*these* competencies, composed *this* way."** Two problems follow:

1. **Composition is manual and unversioned.** Which areas make up an "enterprise"
   or "security engineer" qualification lives in an operator's flags and their
   memory, not in a citable artifact. Two people running "the enterprise
   assessment" can run different things.
2. **"Profile" conflates two concepts.** It carries both *how EV dimensions are
   weighted within an area* (a scoring preset) **and** area weighting — but not
   *which competencies compose the qualification*. The composition layer is
   missing, and the weighting layer is doing double duty.

The opportunity is to make the **assessment itself declarative** — an
`enterprise.yaml` that the *standard body* (or an adopter) ships as versioned
data, and that anyone can extend without touching Python. This is what makes
AIES "assessment-as-code": the layering becomes

```
Standard  →  Assessment  →  Profile  →  Runner  →  Runtime
(constants)  (which CAs +   (EV weights) (execute)  (adapter)
              weights, gates,
              sampling, profile)
```

with the engine executing data at every layer and hard-coding none of it.

The subtle, load-bearing decision this ADR must settle is **cross-area
scoring**. AESQS deliberately scores **per area** (per-area competency level and
RT×AL envelope) and does **not** emit a single blended number — that is core to
the evidence-not-leaderboard ethos ([AIES-AESQS-CS-01](../AESQS/capability-scoring.md)).
An assessment with weights (`architecture 30, coding 40, security 15, qa 15`)
*looks like* it should collapse the areas into one weighted score — which would
reintroduce exactly the vanity number the standard avoids, and could let strength
in one area mask a **gate failure** in another. How weights behave is therefore
the crux, not a detail.

## Decision Drivers

- **Data-driven to the top.** No competency composition should live in engine
  code; assessments are versioned declarative artifacts.
- **Separation of concerns.** *Assessment* = which competencies and how they
  compose; *Profile* = EV-dimension weighting within an area. Untangle them.
- **The ethos must survive.** Per-area, gate-first scoring must not be traded for
  a blended headline number; a strong area must not offset a failing one.
- **Non-negotiables stay non-negotiable.** Gates and statistical minimums are
  engine constants ([D3](ADR-0002-Qualification-Platform.md)); an assessment
  MUST NOT be able to weaken them, exactly as a profile cannot.
- **Backward compatible.** `--profile … --area …` keeps working; `--assessment`
  is additive.
- **Freeze the RuntimeAdapter.** This change lives above the runner; it does not
  touch the adapter contract.

## Decision

Introduce a first-class, declarative **Assessment** layer, governed by the
decisions below.

### D-B1. The assessment artifact

An assessment is a versioned YAML declaring the competency composition of a named
qualification, its EV-weighting profile, sampling, and which competencies are
mandatory vs advisory. It **selects** the areas to run (no manual `--area`).

```yaml
id: enterprise                 # stable assessment identifier
version: 1.0.0                 # CONTENT version — certifications cite this
schema: 1                      # assessment file-FORMAT version (engine-owned)
description: Enterprise-grade AI-native SDLC qualification.
profile: enterprise            # EV-dimension weighting (existing profiles/*.yaml)
default_risk_tier: RT2             # RT2 — Moderate
competencies:                  # the areas this qualification composes
  - area: CA-04                # Architecture & Solution Design
    requirement: { type: mandatory }   # mandatory competencies decide PASS/FAIL
    weight: 30
  - area: CA-05                # AI-Assisted Implementation
    requirement: { type: mandatory }
    weight: 40
  - area: CA-07                # Security & Privacy Engineering
    requirement: { type: mandatory }
    weight: 15
    min_cl: CL3                # optional: this area must reach at least CL3
  - area: CA-06                # Testing, Quality & Evaluation
    requirement: { type: mandatory }
    weight: 15
  - area: CA-09                # Operations — informational only
    requirement: { type: advisory }    # advisory competencies never fail the assessment
    weight: 10
sampling:
  repeats: 3                   # override; never below the AESQS tier minimum
```

**Versioning.** An assessment is identified by `id`; `version` is its **content**
version (a certification cites *"Enterprise Assessment v1.2.0"* — results are
comparable only across identical content versions); `schema` is the **file-format**
version, owned by the engine, so the assessment format can evolve without
silently reinterpreting old files.

**Requirement is an object** (`requirement: { type: mandatory }`), not a bare
string, so future types (`recommended`, `optional`, `experimental`,
`deprecated`) can be added without a breaking schema change. Default **mandatory**.
**Mandatory** competencies determine the normative outcome (D-B2); **advisory**
competencies are scored and reported for diagnostics/analytics but **never**
change PASS/FAIL. `weight` and `min_cl` are optional.

Assessments ship under `platform/assessments/*.yaml` (standard-body set) and may
be supplied by adopters. They are versioned so results are comparable only across
identical content versions.

**Declarative vs engine-owned — a hard boundary.** Assessment authors declare
*what to assess and how much it matters*; they never redefine *how the assessment
decides*:

| Assessments MAY declare (declarative) | The engine owns (assessments MUST NOT touch) |
|---|---|
| competency set & area selection | the decision algorithm |
| requirement type (mandatory/advisory) | the evidence model |
| weights, `min_cl` | gate semantics & thresholds |
| profile reference, sampling (raise-only) | statistical minimums & AL caps |
| id / version / description | outcome precedence & conformity rules |

**The validator** (extending `aies suites validate`) enforces both the boundary
and logical consistency, rejecting: any field that would weaken a gate, minimum,
or AL cap; a non-existent profile reference; unknown competency ids; duplicate
competencies; zero/negative weights; `sampling` below the tier minimum; **no
mandatory competency**; and (if composition/imports are ever added) circular
references. A bad assessment fails validation *before* it can run.

### D-B2. Assessment outcome — gate-first conformity, not a score

AIES performs **conformity assessment** (does this deployment fulfil the
requirements for this role?), not benchmarking (which model is better?). The two
have different semantics, and a single weighted score answers the wrong question:
`Architecture PASS · Coding PASS · Security FAIL · QA PASS` must never render as
`89.4%`. This mirrors ratified practice — ISO management-system audits, PCI DSS,
SOC 2, and ISO 26262 all assess *mandatory controls met: yes/no*, with weights
governing audit effort and emphasis, never compensation.

**A. Explicit assessment outcomes (normative, authoritative).** An assessment
result is one of:

| Outcome | Meaning |
|---|---|
| **PASS** | every **mandatory** competency is decisional, passes its gates, and meets any `min_cl` |
| **FAIL** | a mandatory competency is decisional but fails a gate or `min_cl` |
| **INCONCLUSIVE** | a mandatory competency has decisional-sized but ambiguous/contradictory evidence (e.g. conflicting raters, or a result inside the gate's uncertainty band) |
| **INSUFFICIENT EVIDENCE** | a mandatory competency lacks enough scored evidence to decide (sample below the AESQS minimum, or unscored) |

The overall outcome is the **most severe** outcome across the mandatory
competencies, with severity **FAIL > INCONCLUSIVE > INSUFFICIENT EVIDENCE >
PASS**. **Advisory** competencies are scored and reported but **never** change
the outcome. A strong competency can never offset a failing one.

*"Ready" is a deployment-lifecycle concept, not an assessment result:*
`Assessment PASS → (human) Certification/grant → Production-ready`. The
assessment layer emits only the outcome above; readiness/grant remain downstream
human acts (D8).

**Structured reasons (engine-internal, for automation).** The single outcome is
what users see, but the engine records *why* as structured data — a `reasons`
list, one per blocking mandatory competency, each with an engine-owned `kind`:

| `kind` | Raised when |
|---|---|
| `mandatory-gate` | a required EV gate (incl. the EV3 hard gate) failed |
| `min-cl` | the competency did not reach its declared `min_cl` |
| `min-confidence` | evidence is decisional-sized but too ambiguous to conclude (→ INCONCLUSIVE) |
| `insufficient-evidence` | sample below the AESQS minimum, or unscored (→ INSUFFICIENT EVIDENCE) |
| `assessment-error` | the competency could not be evaluated as specified (→ INCONCLUSIVE) |

The reason `kind` set is **engine-owned** (assessments cannot define new kinds).
This keeps PASS/FAIL clean for humans while giving pipelines a stable,
machine-readable cause.

**B. Three reporting layers — only the first is authoritative.**

1. **Normative (authoritative):** per-mandatory-competency PASS/FAIL and the
   overall outcome. This is the only thing certification/conformity relies on.
2. **Diagnostic (informational):** per-area numeric scores (aggregate over
   decision values, and per-EV) — engineering feedback for improvement, not a
   verdict.
3. **Informational analytics (non-authoritative):** coverage, evidence
   completeness, confidence, and any weighted summaries — useful for dashboards
   and trend analysis, explicitly labelled non-authoritative. AIES does **not**
   publish an "Overall 82/100", because a comparable headline number turns a
   conformity framework into a leaderboard.

**C. The weights rule (normative).**

> **Assessment weights determine the relative importance and contribution of
> competencies to assessment composition, execution priority, and reporting.
> They MUST NOT compensate for unmet mandatory requirements, failed gates, or
> minimum competency thresholds.**

**D. Non-negotiables remain engine constants** (D3). An assessment MUST NOT lower
a gate, a statistical minimum, or an AL cap; `sampling.repeats` may only *raise*
effective volume, never drop below the tier minimum.

This keeps assessment-as-code fully declarative while preserving the per-area,
gate-first, evidence-first design and keeping AIES a qualification/conformity
framework rather than a benchmark.

### D-B3. Layering and backward compatibility

`aies qualify --assessment enterprise <deployment>` loads the YAML, runs its
competency set at the resolved risk tier using the referenced profile, and
produces the per-area evidence package plus the assessment **outcome**
(PASS/FAIL/INCONCLUSIVE/INSUFFICIENT EVIDENCE) with the three reporting layers.
The engine gains an assessment loader; it hard-codes no assessment. The existing
`--profile`/`--area` path is unchanged. The RuntimeAdapter is untouched.

**Immutable execution metadata** is a facet of the Canonical Assessment Result
(D-B4), not of a report: an append-only block recording **assessment id +
version + schema**, **profile + profile version** (captured at run time — a later
edit to the profile file cannot reinterpret a past result), **platform version**,
**AIES standard version**, **runtime + model fingerprint**, and **timestamp** — so
a certification is always traceable to the exact inputs that produced it and drift
is explainable *("why did this pass last July but fail today?")*.

Two version fields are deliberately kept **distinct**, because they answer
different questions:

- **`decision_engine_version`** — *which software* decided (the platform build). A
  bugfix rebuild changes this without changing semantics.
- **`decision_semantics_version`** — *which normative AESQS decision policy* was
  applied. AESQS may intentionally change decision policy without a mere rebuild.

Conflating them would make it impossible to tell a bugfix from a policy change.
The result also records **`evidence_schema`** — the version of the evidence
artifact it decided over — because the **Evidence Package is an independently
versioned artifact** that can outlive any single decision engine. One immutable
Evidence Package may be replayed through Decision Engine v1 *and* a future v2,
producing distinct, individually-traceable results:

```
Evidence Package (immutable, evidence_schema=N)
  ├── Decision Engine (AESQS semantics 1.0) → Result A   (engine build X)
  └── Decision Engine (AESQS semantics 2.0) → Result B   (engine build Y)
```

This is the same "re-decide from evidence, no inference" mechanism that powers
`qualify --resume`, generalized across engine/semantics versions — it gives
historical reproducibility, standards evolution, and regression testing at once.
Both artifact envelopes carry a **schema version** (`evidence_schema`,
`result_schema`) that is **field-append-only** per COMPATIBILITY.md.

### D-B4. Frozen pipeline and single-responsibility components (v1.0)

The assessment pipeline is **frozen** at these stages, each with exactly one
responsibility. The runner **never decides**; the decision engine **never
renders**; reports are **views** of one canonical object.

```
Assessment Schema → Schema Validator → Assessment Loader → Runner Selection
  → Evidence Collection → Decision Engine → Canonical Assessment Result
  → Report Renderers → CLI
```

| Component | Sole responsibility |
|---|---|
| Schema | define an assessment (data) |
| Validator | reject invalid/inconsistent assessments before they run |
| Loader | parse an assessment into memory |
| Runner selection | choose which competencies/areas to execute |
| Evidence collection | gather raw responses, ratings, metrics — **no decisions** |
| **Decision engine** | apply normative rules → outcome + structured reasons |
| Canonical result | the immutable assessment record (below) |
| Report renderers | present the result in a format — **no decisions** |
| CLI | user interaction |

**The Canonical Assessment Result** is the single machine-readable object every
renderer (CLI, JSON, Markdown, HTML — and future SARIF / GitHub Check) reads. It
never contains presentation:

```
Assessment Result
├── metadata     # immutable execution metadata (above)
├── evidence     # per-competency collected evidence (responses, ratings, metrics)
├── decisions    # per-mandatory PASS/FAIL + overall outcome + structured reasons
├── diagnostics  # per-area numeric scores (engineering feedback)
└── analytics    # coverage / confidence / weighted summaries (non-authoritative)
```

**The Decision Engine is frozen and engine-owned.** It is the most stable piece
of AIES and owns **outcome precedence, mandatory/advisory semantics, gate
evaluation, confidence thresholds, and the conformity rules**. Assessment authors
**never** redefine any of it (the declarative/engine-owned boundary, D-B1).
Because decisions read only the evidence + the assessment definition, evidence
can be **re-decided without re-running inference** (already true today via
`aies qualify --resume`), and alternative decision policies or new renderers can
be added without touching collection or the conformity rules.

## Options Considered

### Option A — Keep composition in flags/profiles (status quo)
- **Pros:** no new layer.
- **Cons:** composition stays unversioned and operator-dependent; "profile"
  keeps conflating weighting and composition; not assessment-as-code.

### Option B — Declarative assessment with a single weighted composite score
- **Pros:** one intuitive headline number per assessment.
- **Cons:** reintroduces the blended vanity number the standard rejects; lets a
  strong area mask a failing one (`Security FAIL` hidden behind `89.4%`); turns a
  conformity framework into a leaderboard; breaks the gate-first ethos.

### Option C — Declarative assessment; gate-first outcome + three reporting layers (chosen)
Explicit outcomes (PASS/FAIL/INCONCLUSIVE/INSUFFICIENT EVIDENCE) over mandatory
competencies; advisory competencies and all numeric/weighted figures are
diagnostic/informational and never decide.
- **Pros:** fully data-driven and versioned; separates Assessment from Profile;
  preserves per-area gate-first conformity; keeps numbers for engineers and
  dashboards without letting them decide; mandatory/advisory gives authors
  flexibility without weakening qualification; backward compatible; adapter
  untouched.
- **Cons:** no single "82/100" headline (deliberate); a second declarative layer
  to author and version.

Chosen: **Option C**.

## Consequences

**Positive**
- AIES becomes assessment-as-code: named qualifications are versioned artifacts a
  standard body or adopter ships as data, extensible without engine changes.
- Assessment and Profile are cleanly separated; the engine hard-codes neither.
- The per-area, gate-first, evidence-not-leaderboard design is preserved.
- Reproducibility improves: "the enterprise assessment v1.0.0" is exact and
  citable, and the immutable execution metadata explains later drift.
- **Room to grow without engine changes.** The `schema` version, object-form
  `requirement`, and reserved-but-unused keys leave the door open for future
  capabilities — e.g. assessment **composition/inheritance** (`extends:
  enterprise` → `enterprise + finance`, `enterprise + medical`) — without
  breaking existing files. These are *not* implemented now; the schema simply
  avoids foreclosing them (and the validator already reserves circular-reference
  checks for when imports land).
- **Single-responsibility pipeline (D-B4).** Evidence collection, decision, and
  rendering are separate: evidence can be **re-decided without re-running
  inference**, new renderers (SARIF, GitHub Check) need no decision change, and
  the frozen Decision Engine becomes AIES's stable conformity core.

**Negative (with mitigations)**
- No single composite *qualification* score. *Mitigation:* deliberate — the
  report gives an explicit outcome (PASS/FAIL/INCONCLUSIVE/INSUFFICIENT
  EVIDENCE), per-area detail, and non-authoritative analytics, which is more
  honest than a blended number.
- Another artifact to version. *Mitigation:* reuse the suite-version machinery;
  the validator enforces schema and that gates/minimums aren't weakened.
- Risk that weights/analytics are misread as a quality verdict. *Mitigation:* the
  weights rule (D-B2.C) is normative; the report labels layers 2–3
  non-authoritative; only mandatory PASS/FAIL is authoritative.

## Compliance & Verification

- No assessment can lower a gate, a statistical minimum, or an AL cap; the
  validator rejects any such field, and `sampling.repeats` only raises volume.
- An assessment reports **FAIL** if any mandatory competency is gate-failing, and
  **INSUFFICIENT EVIDENCE** if any mandatory competency is non-decisional —
  regardless of weights or of strong advisory/other competencies (unit-tested).
- A failing or non-decisional **advisory** competency never changes the outcome
  (unit-tested).
- No numeric/weighted figure is presented as the authoritative result; only the
  mandatory PASS/FAIL outcome is authoritative (the weights rule D-B2.C).
- The validator rejects a semantically inconsistent assessment (duplicate or
  unknown competency, non-positive weight, no mandatory competency, orphan
  profile reference, sub-minimum sampling) *before* it can run (unit-tested).
- The result records structured `reasons` with engine-owned `kind`s; an
  assessment cannot introduce a new reason kind or alter outcome precedence.
- Every assessment result records immutable execution metadata (assessment
  id/version/schema, profile, platform version, AIES version, runtime + model
  fingerprint, timestamp).
- The runner performs no decision and reports perform no decision: the Decision
  Engine is the only component that produces an outcome, and it reads only the
  evidence + the assessment definition (so evidence re-decides without inference).
- Per-area EV scores, CLs, and envelopes are identical whether an area is run via
  `--assessment` or via `--area`.
- The engine contains no assessment name in code; assessments load from data.
- The RuntimeAdapter contract is unchanged.
- The repository link/anchor check passes; ROADMAP records the layer.

## Links

- [ADR-0002 — Qualification Platform](ADR-0002-Qualification-Platform.md) (D3: gates non-configurable)
- [ADR-0003 — Competency areas map to knowledge areas by coverage](ADR-0003-Competency-Area-Knowledge-Mapping.md)
- [Capability Scoring (AIES-AESQS-CS-01)](../AESQS/capability-scoring.md) — per-area scoring this preserves
- [Platform Specification (AIES-DOC-06)](../docs/PLATFORM.md) · [Profiles (AIES-PLAT-02)](../platform/PROFILES.md)
- [GOVERNANCE.md §3–§4 (AIES-GOV-01)](../GOVERNANCE.md)

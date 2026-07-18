# ADR-0004: `aies audit` — executable repository conformance assessment

| | |
|---|---|
| **ADR Number** | 0004 |
| **Status** | Accepted |
| **Deciders** | Maintainers; Platform Module Editor; AEOS Module Editor |
| **Supersedes** | — |
| **Superseded by** | — |

## Context

The `aies` platform ([ADR-0002](ADR-0002-Qualification-Platform.md)) qualifies a
**deployment** — it answers *"is this model good enough, at what autonomy, for
what risk tier?"* by scoring model responses on EV1–EV6. It says nothing about
the **engineering practice around the model**: whether a *repository / team*
actually does AI-native engineering the way AIES requires — provenance on
AI-produced change, tested guardrails, human gates, risk-tiering, versioned
context assets, supply-chain integrity, and so on.

AIES already has a *claim-based* conformance mechanism
([CONFORMANCE.md, AIES-DOC-08](../docs/CONFORMANCE.md); `aies conform`): an
organization asserts conformance and links evidence. What is missing is the
*executable* counterpart — a tool that **derives** a conformance/maturity
picture from a repository instead of taking the claim on trust, produces a
per-area scorecard and ranked recommendations, and can act as a CI gate. This is
the original project vision ("clone a repo, run an audit, see improvements,
score across areas") and it opens a second, larger audience than model
evaluation: every AI-adopting engineering organization.

The design risk is credibility. AIES's entire premise is **evidence, not
checkboxes**. Most AIES requirements are *process/human* (was a gate actually
exercised? was oversight real?) and are **not detectable from repository files**.
A naive "score any repo" scanner would emit green from the *absence* of signal —
the exact opposite of the rigorous, evidence-gated model side — and would
discredit the standard. So the central question this ADR settles is not *whether*
to build the auditor, but *how to score and report it honestly*.

## Decision Drivers

- **Honesty over coverage.** Absence of a detectable signal is a **gap**, never a
  pass. The auditor must never manufacture conformance.
- **Consistency with the standard's ethos.** The model side gates on evidence and
  leaves the grant to a human; the audit side must mirror that — detect what is
  detectable, require attestation (with evidence pointers) for the rest, and
  leave the judgement to a human.
- **Reuse, don't reinvent.** Reuse the CA/KA taxonomy and the conformance model;
  do **not** build a SAST/secret-scanning engine — detect that such tooling is
  *configured* and map to the external standards.
- **Different subject ⇒ different score.** A repository is not a model producing
  scored responses, so EV1–EV6 does not apply; a distinct maturity model is
  needed.
- **Extensibility.** The set of detectable practices will grow across languages
  and stacks; checks must be pluggable without changing the engine.
- **Focus.** Model qualification remains the core; the auditor must be a distinct,
  clearly-scoped surface, not a rewrite.

## Decision

Build **`aies audit <repo>`** as an executable **repository conformance
assessment**, governed by the four decisions below.

### D-A1. Subject and scope

The subject is a **repository and the engineering practice evidenced in it** —
distinct from the deployment subject of `aies qualify`. Coverage is organized by
the twelve competency areas (CA-01…CA-12). The auditor addresses **all twelve**
but only auto-detects where real repository signals exist (see §Coverage).

### D-A2. Maturity scoring (distinct from EV1–EV6)

Each area is scored on a **maturity scale ML0–ML4**, not on EV dimensions:

| Level | Meaning |
|-------|---------|
| **ML0** Absent | no evidence and no attestation |
| **ML1** Initial | ad hoc; minimal evidence |
| **ML2** Managed | the practice exists and is evidenced |
| **ML3** Defined | evidenced *and* enforced (e.g. the control is tested / gated in CI) |
| **ML4** Optimizing | enforced *and* measured/reviewed on a cycle |

Area maturity is derived from the evidence states of its checks (below); the
overall result is a **conformance-readiness** summary, never a single vanity
number. The maturity thresholds and the RT-gated required-evidence sets are
**engine constants, non-configurable** — mirroring the model side's
non-negotiable gates (PLATFORM.md D3).

### D-A3. Three-state evidence — never false-green

Every check resolves to exactly one of:

- **verified** — evidence found in the repository (a CI gate exists, tests
  present, deps pinned, `.env` git-ignored, provenance trailers, guardrail
  tests…).
- **asserted** — not file-detectable; the team attests it in an **attestation
  file** *with an evidence pointer* (same model as `aies conform`).
- **gap** — neither. Absence of signal is always a gap.

`--gate` and maturity never credit a **gap** or an unbacked assertion as a pass.

### D-A4. Pluggable checks mapped to external standards

A **check** is a small plugin (resolved like runtime adapters) declaring its
`id`, competency `area`, the `evidence` it looks for, the **risk tier at which it
becomes required**, and its **external-standard mapping** (OWASP LLM/Agentic Top
10, MITRE ATLAS, CISA/NCSC Secure AI Development, SLSA, ISO/IEC TS 42119, ISO/IEC
42005) via [CROSSWALK](../docs/CROSSWALK.md). A single `RepoContext` scans the
repository once (git metadata incl. provenance trailers, file tree, CI/ADR/
policy/dependency/test files, config parsing) and is shared across checks. The
audit output is an append-only record, like a run.

### Coverage — all 12 areas addressed; auto-detection where signals exist

| Detection | Areas | Basis |
|-----------|-------|-------|
| **Strong auto-audit** | CA-01, CA-05, CA-06, CA-07, CA-08, CA-11 | risk/autonomy policy & ADRs; commit/PR provenance; tests/coverage/CI gates; dep manifests+locks, secret-scan/SAST config, `.env` ignored, SECURITY.md; CI/CD gates, SBOM/AI-BOM, signing, rollback; versioned prompt/agent/context artifacts |
| **Presence + attestation** | CA-04, CA-09, CA-10, CA-12 | structured ADRs; telemetry/runbooks/monitoring config; branch protection/CODEOWNERS/required review; governance docs, guardrail config **+ tests**, incident policy — presence detectable, quality attested |
| **Attestation-only** | CA-02, CA-03 | requirements traceability; acceptance criteria — rarely carried in the repo |

The honest ceiling is therefore *"~8–10 of 12 areas have automated evidence
checks; the remainder require attestation"* — reported as such, not as "audits
everything."

### Modes

- `aies audit <repo>` — advisory scorecard (markdown/json/html): per-area
  maturity, verified/asserted/gap breakdown, ranked recommendations.
- `aies audit <repo> --gate --rt N` — CI mode: non-zero exit if the
  RT-required evidence for tier N is missing.
- `aies audit <repo> --attest <file>` — supply attestations (asserted items +
  evidence pointers).

### Non-goals

- Not a SAST, secret scanner, dependency scanner, or license scanner — it
  detects that such tools are *configured* and consumes their outputs; it does
  not replace them.
- Not an oracle of engineering quality — it evidences and attests; humans judge.
- Not a grant — like the model side, the platform prepares evidence; a human
  records any conformance decision.

## Options Considered

### Option A — No repo auditor; keep claim-based `conform` only
- **Pros:** zero new surface; keeps focus purely on model qualification.
- **Cons:** leaves the original vision unbuilt; conformance stays assertion-only
  with no executable evidence; forgoes the larger audience.

### Option B — A "score any repo" scanner that emits a single grade
- **Pros:** simplest to pitch; one number.
- **Cons:** false-green from absent signals; betrays the evidence-not-checkboxes
  ethos; indistinguishable from shallow AI-governance checkbox tools; damages
  credibility.

### Option C — Evidence + attestation maturity auditor (chosen)
- **Pros:** honest (three-state, never false-green); consistent with the model
  side; reuses taxonomy + conformance; maps outward to ratified standards so
  output is reusable; extensible via check plugins.
- **Cons:** more design up front; "coverage" is deliberately partial and must be
  communicated as such; maturity is looser than the model side's statistics.

Chosen: **Option C**.

## Consequences

**Positive**
- AIES becomes the *executable conformance layer*, not only a model scorer — a
  second, larger use case bound to the same taxonomy.
- Honest three-state reporting protects the project's credibility and matches its
  evidence ethos.
- External-standard mappings make audit output reusable as evidence for OWASP,
  CISA/NCSC, SLSA, ISO/IEC 42119/42005 programs.
- Pluggable checks let coverage grow (languages, stacks) without engine changes.

**Negative (with mitigations)**
- Partial coverage could be misread as "AIES audits everything." *Mitigation:*
  the report states auto vs attested vs gap counts explicitly; docs state the
  ceiling.
- Attestations can be gamed (assert without real evidence). *Mitigation:*
  attestations require an evidence pointer and are labelled *asserted*, never
  *verified*; a human conformance decision remains separate.
- Maturity scoring is less rigorous than the model side's confidence bounds.
  *Mitigation:* maturity is derived only from discrete evidence states, gates are
  non-configurable, and the model is documented, not a black box.
- New surface risks diluting focus. *Mitigation:* phased delivery (strong areas
  first), separate command and module, model qualification unchanged.

## Compliance & Verification

- The auditor never scores a **gap** or an unbacked assertion as a pass
  (unit-tested with positive and negative fixture repos).
- Maturity thresholds and RT-required-evidence sets are engine constants and are
  not overridable by a profile or flag.
- Every check declares its competency area and external-standard mapping.
- `aies audit` on this repository produces a plausible, non-trivial scorecard as
  a smoke test.
- The repository link/anchor check passes; ROADMAP Phase 8 records the auditor.

## Links

- [ADR-0002 — Qualification Platform](ADR-0002-Qualification-Platform.md)
- [Platform Specification (AIES-DOC-06)](../docs/PLATFORM.md)
- [Conformance (AIES-DOC-08)](../docs/CONFORMANCE.md) — the claim-based mechanism this makes executable
- [Standards Crosswalk (AIES-DOC-07)](../docs/CROSSWALK.md) — external-standard mappings the checks cite
- [AEOS Governance Operations (AIES-AEOS-GOV-01)](../AEOS/governance-operations.md) — the practices audited
- [GOVERNANCE.md §3–§4 (AIES-GOV-01)](../GOVERNANCE.md)

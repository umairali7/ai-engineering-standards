# AIES Vision Execution Backlog

| | |
|---|---|
| **Document ID** | AIES-DOC-14 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

This is the single authoritative implementation backlog for taking AIES from a
strong draft foundation to a validated, reusable standard and Engineering
Assessment Platform. [ROADMAP.md](../ROADMAP.md) contains public milestones;
it MUST link here rather than repeat implementation status.

The backlog has two lanes:

1. **Vision delivery** — standards, evidence integrity, assessment capability,
   decision products, and adoption.
2. **Cleanup and debt** — consistency, maintainability, release engineering,
   and repository hygiene.

Status values are **Open**, **In progress**, **Blocked**, **Deferred**, and
**Done**. Done requires the acceptance signal to be verified.

## 1. Target Architecture

```text
AEBOK / AESQS / AEOS / AEAR / AECT / ECM
                    │
                    ▼
             Assessment Plan
                    │
                    ▼
        Assessment Coverage Matrix
                    │
                    ▼
             Subject Descriptor
                    │
                    ▼
       Subject Executor / Evidence Adapter
                    │
                    ▼
             Canonical Evidence
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
 Qualification    ECM      Conformance
        │           │           │
        └───────────┼───────────┘
                    ▼
     Guidance / Remediation / Limitations
                    │
                    ▼
 Compare / AIES Select / Portfolio Views
                    │
                    ▼
             Human authority
```

The platform is not a model leaderboard. It prepares trustworthy, scoped
evidence about any supported subject and presents that evidence for different
human decisions. Qualification, engineering capability, deployment guidance,
remediation, comparison, and selection remain separate products. Subject types
share identity, provenance, evidence lifecycle, reporting, and human-authority
boundaries; they do not automatically share instruments or score semantics.

## 2. Adoption Success Sequence

Technical completeness alone will not create adoption. AIES needs a narrow
reason to try it, credible evidence that its outputs predict useful engineering
differences, compatibility with tools organizations already use, independent
review, and public proof that adopters can reproduce the result.

The initial adoption wedge is:

> Produce an evidence-backed Engineering Capability Matrix that shows what an
> AI engineering subject demonstrably does well, how strong the supporting
> evidence is, where review is appropriate, and what remains unknown.

This wedge leads with Engineering Evaluation, ECM, and Engineering Fit. It does
not require an adopter to begin with formal qualification or absorb the entire
five-module standards architecture.

| Sequence | Status | Success item | Acceptance signal |
|---|---|---|---|
| S1 | Done | Establish the engineer-facing product wedge | README, CLI, demo, report bundle, and terminology distinguish non-blocking Engineering Evaluation, ECM, Engineering Fit, optional human evaluation, and explicit Formal Qualification; no default workflow stages a missing human as product failure |
| S2 | In progress | Prove ECM measurement validity | A preregistered multi-subject panel demonstrates task discrimination, reviewer agreement, uncertainty behavior, and stability; direct ET-01 through ET-15 mappings receive independent review; negative and null findings are published rather than hidden |
| S3 | Open | Publish the first comparative ECM case study | At least three materially different subjects run the same compatible preregistered workload; the public bundle includes prompts/instruments where publishable, hashes, raw and resolved observations, cost/runtime, limitations, ECM, fit guidance, and independent engineering review; it reports scoped differences without declaring a universal winner |
| S4 | Open | Publish one local and one hosted reproducibility pilot | A third party can reproduce both runs from a clean environment using version-pinned instructions; expected and observed differences, failures, repair steps, environment fingerprints, and lessons learned are retained |
| S5 | In progress | Integrate with the existing evaluation ecosystem | Versioned Inspect-compatible rating import/export and SARIF finding bridges preserve source hashes, explicit loss, and claim boundaries; validate against pinned official schemas/APIs and demonstrate an independent external-tool round trip before Done |
| S6 | In progress | Make first value reachable in one session | The clean-install journey, offline demo, guided non-secret initialization, deployment registration/discovery, bounded plan/evaluation, declared cost/ETA, progress/resume, result opening, advisory CI evidence, and uninstall are documented and tested locally on Windows; hosted macOS/Linux evidence and first-user studies remain before Done |
| S7 | Open | Recruit an independent review and contributor cohort | Publish reviewer role descriptions, competency expectations, conflict rules, review packet, finding template, time commitment, module ownership opportunities, scenario contribution path, and office-hours/contact route; recruit enough non-author reviewers to cover every approval candidate and contributors from at least three independent organizations |
| S8 | Open | Publish adoption-grade examples and decision stories | Five real case studies satisfy Charter SC-5 and cover at least deployment selection, repository assurance, engineering-fit guidance, formal qualification, and reassessment after change; each starts with the decision being made, not the framework vocabulary |
| S9 | Open | Operate a transparent adoption scorecard | Track reproducible pilots, independent reviewers, external contributors, third-party runs, public organizational references, case studies, issue-to-first-success time, report comprehension feedback, and repeat usage; do not collect mandatory telemetry or private assessment evidence |
| S10 | Open | Demonstrate durable external adoption | At least ten organizations publicly reference AIES under Charter SC-3, contributions come from at least three independent organizations under SC-6, and no single organization authors a majority of accepted release changes |

### Adoption UX backlog

Adoption is progressive. A user should receive useful engineering evidence
before learning formal qualification, governance roles, or the full standards
architecture:

```text
Try → Evaluate → Understand → Integrate → Govern
```

| Status | Adoption UX item | Acceptance signal |
|---|---|---|
| In progress | Ship a one-command cross-platform trial | `aies demo` passes source and installed-wheel execution on Windows. The cross-platform installed-wheel matrix now runs a complete clean-install journey with a path containing spaces, non-default workspace, discovery, offline evaluation, resume, report opening, advisory CI evidence, and uninstall; macOS/Linux hosted results remain required before Done |
| In progress | Publish installation-grade packages | Wheel/sdist build, isolated Windows install, validation, demo, support/starter package-data checks, and uninstall pass. Canonical source instructions now create a venv, offer optional pipx/uv isolation, and prohibit `--break-system-packages`; license, version alignment, dependency integrity, signing/provenance, upgrade, published-artifact installation, and cross-platform CI results remain |
| Done | Add guided workspace initialization | `aies init --guided` interactively selects deployment evaluation, offline demo, or repository audit; deployment setup validates and previews id/model/endpoint/role/credential environment variable, writes no secret, preserves existing files, and prints the exact next command. Equivalent non-interactive flags support reproducible onboarding |
| Done | Add one canonical beginner evaluation command | `aies evaluate <subject>` validates the subject/judge, selects a bounded no-repeat default, supports plan-only, runs the canonical automated pipeline, prints the result link and sharing command, and optionally opens it; advanced commands remain available |
| Done | Make planning precede cost and waiting | `aies evaluate --plan-only` makes no endpoint calls and reports distinct candidate calls, batched judge calls, concurrency, no-repeat scope, structured per-phase and total cost/duration from validated manifest declarations, exact unknown reasons, limitations, and response/rating/report resumability |
| Done | Supply decision-oriented starter profiles | The packaged `decision-starters-v1.yaml` registry and `aies starter list/show` cover “compare coding deployments,” “understand one deployment,” “audit this repository,” and “try formal qualification”; each starts with the decision and states prerequisites, workflow sequence, artifacts, what it does not prove, time/cost class, evidence breadth, and next expansion without executing anything |
| In progress | Make every failure actionable | The shared `aies-cli-failure-v1` diagnostic classifies and sanitizes failures while reporting preserved work, an exact recovery command, a troubleshooting anchor, and duplicate-cost risk. It now covers first-use evaluation/qualification/review/open/support/starter plus init, registry/deployment, discovery, Inspect/SARIF bridges, score/import, audit/CI, report, ECM, fit guidance, and comparison. HTTP 429 preserves `Retry-After`; installed-wheel CI validates the machine contract. Migrate the remaining formal-governance and maintainer/admin command families before Done |
| Done | Make reports effortless to find and share | Completion identifies result artifacts; `aies open <run-id>` opens or links the primary view and exports an immutable allowlisted/anonymized ZIP that excludes raw evidence, ratings, fingerprints, and secrets |
| Done | Add a terminal evidence-to-decision snapshot | `aies snapshot <run>` and successful `demo`, `evaluate`, and `open` flows reuse canonical ECM/Fit facts to show ET code and title, distinct evidence, observed capability, separate confidence, optional human-evaluation status, unknown tasks, and a non-authorizing engineering interpretation in wide or narrow terminals |
| Done | Add adoption-grade CI integration | The pinned reusable GitHub workflow verifies evaluator decision semantics, calculates repository evidence at the selected risk tier, emits notice/warning annotations and a step summary, retains JSON/Markdown/annotation artifacts even on failure, requests only read access, and cannot block unless the caller explicitly sets `enforce: true`; `aies ci audit` supplies the tested local equivalent |
| In progress | Add containerized reproducibility | The non-root OCI-labelled image and guide cover the offline demo, read-only repository audit, conformance corpus, supported networked assessment planning, mounts, secrets/network boundaries, artifact ownership, cleanup, and amd64/arm64 buildx usage. CI builds and exercises demo/audit/conformance; hosted CI results, digest-pinned release base, multi-architecture publication, SBOM/provenance, and signature remain before Done |
| In progress | Test first-run journeys on every supported platform | The installed-wheel matrix now runs `clean_install_journey.py` on Windows, macOS, and Linux through init, demo, discovery, bounded offline evaluation, resume, report opening, advisory CI evidence, and uninstall using paths with spaces and a non-default workspace. The journey passes locally on Windows; hosted macOS/Linux results and a genuine prior-version upgrade fixture remain before Done |
| Done | Layer documentation by user intent | The root conversion page and Getting Started guide offer Try, Evaluate, Compare, Audit, Integrate, and Govern paths; each begins with the decision, runnable command, expected artifact, limitation, and next step, introduces codes with human-readable titles, and defers normative detail to linked references |
| Open | Conduct first-run usability studies | At least five people unfamiliar with AIES attempt the clean-machine workflow without live assistance; time to first ECM, failure points, misunderstood terms, abandoned steps, and report comprehension are recorded and drive a published remediation list |

### Adoption guardrails

- Do not market design-reviewed scenarios as empirically calibrated.
- Do not present ECM differences as predictive until the preregistered study
  demonstrates that relationship.
- Do not call Review documents Approved without the independent-review and
  ratification records.
- Do not advertise an agent, MCP, RAG, pipeline, platform, or composite
  assessment as supported until its Subject Assessment Profile, executor,
  instruments, and report limitations are implemented and discoverable.
- Do not position AIES as a replacement for NIST AI RMF, ISO/IEC 42001,
  ISO/IEC 25059, OWASP guidance, Inspect, or engineering toolchains. Maintain
  crosswalks and evidence bridges so AIES supplies the engineering capability
  and decision layer around them.
- Do not launch certification claims before AECT is Approved and the
  examination, independence, appeal, renewal, and credential-governance
  controls are operational.

### Demand generation, positioning, and community conversion

Ease of installation is necessary but not sufficient. Every public surface
must help a relevant visitor answer four questions quickly: **Why should I
care? What can I try now? What will I receive? Why should I trust it?** AIES
should invite broad participation without pretending the same message or
workflow serves every persona.

This track follows current project guidance rather than treating promotion as
an afterthought:

- [GitHub's README guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
  says the first repository surface should state what the project does, why it
  is useful, how to start, where to get help, and who maintains it.
- [Open Source Guides' community guidance](https://opensource.guide/building-community/)
  treats users → contributors → maintainers as a funnel and recommends a
  friendly README, clear examples, public process, responsive help, and
  labelled easy contributions.
- [Diátaxis](https://diataxis.fr/start-here/) separates tutorials, how-to
  guides, reference, and explanation so first-time users are not forced
  through standards reference before reaching a result.
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
  provides versioned distribution, release notes, assets, and download signals;
  launch activity should point to reproducible releases rather than an
  arbitrary branch snapshot.
- [CNCF project lifecycle guidance](https://contribute.cncf.io/projects/lifecycle/)
  is a useful maturity analogue: experimental usefulness, growing adoption,
  and production maturity are different claims and should be communicated
  honestly.

| Status | Promotion and conversion item | Acceptance signal |
|---|---|---|
| Done | Redesign the root README as a conversion page | The first screen states the concrete problem, differentiator, honest maturity, 60-second offline command, expected terminal/ECM/report output, supported subjects, and one primary call to action; deeper standards architecture moves below proof and quick start |
| In progress | Create an evidence-backed visual identity | An evidence → ECM → confidence → decision social-preview/README hero is delivered without certification or fictional-result claims; repository social-image configuration, wordmark rules, terminal capture, real ECM/report screenshots, accessibility variants, and asset-source policy remain |
| Done | Make the CLI itself invite the next useful action | Bare `aies`, `init`, `demo`, `evaluate`, `open`, `snapshot`, audit results/gates, comparisons, and report completion present context-specific next commands and expected value without ads, nagging, telemetry, blocking prompts, or changes to JSON/CI semantics |
| Open | Build persona-specific landing paths | Engineers, engineering leaders, AI platform teams, auditors/governance teams, researchers/evaluators, standards contributors, and tool integrators each get a short “decision → command → artifact → limitation → next step” path |
| Open | Publish a 60-second proof and a ten-minute guided trial | Copyable terminal recording/GIF and a narrated demo show real commands and generated artifacts; clean-machine users reproduce them with no hidden setup, credentials, or human gate |
| Open | Publish outcome-led example galleries | Sanitized bundles show model/deployment comparison, repository analysis, reassessment after change, local/private evaluation, and eventual MCP evidence; every example names its decision, evidence scope, limitations, runtime, and reproduction command |
| Open | Establish a launch channel plan | Versioned release, technical launch article, short demo video, GitHub social card, Discussions launch thread, targeted standards/evaluation/MLOps communities, conference/demo submissions, and partner outreach reuse one claim-reviewed message matrix |
| Open | Create a claim-review gate for promotional content | Every headline, comparison, screenshot, talk, post, and badge maps to canonical evidence and a maturity label; uncalibrated, proposed, experimental, supported, and production-validated claims cannot be visually confused |
| In progress | Create the user-to-contributor funnel | README and `CONTRIBUTING.md` now route to safe structured forms for first-run failure, report comprehension, reproducible case studies, scenario instrument review, and adapter proposals, with real Discussions/private-security links and regression validation. Discussions categories, `good first issue`/`help wanted` work, adapter starter kit, contributor recognition, response expectations, and maintainer succession remain |
| Open | Instrument adoption without collecting assessment evidence | Public, aggregate signals cover release downloads, demo success feedback, time to first ECM, docs exits, issue-to-resolution, repeat usage volunteered by pilots, case-study applications, and contribution conversion; telemetry is opt-in and never captures prompts, responses, subjects, or private reports |
| Open | Run message and usability tests before broad promotion | At least five people per priority persona explain AIES back in their own words, complete the trial, locate the ECM, and state its limitations; failed comprehension changes wording and flow before launch |
| Open | Maintain a public launch-and-adoption calendar | Owners, assets, review gates, audiences, channels, dates, success measures, follow-ups, and retrospectives are visible; promotion does not begin before install/demo/release and claim-review gates pass |

### Research-informed build-versus-integrate decisions

The platform should own the semantics that make AIES distinctive and use
existing open standards for commodity execution, telemetry, findings, security
automation, and provenance.

| Domain | External baseline | AIES decision | Detailed acceptance signal |
|---|---|---|---|
| Evaluation execution | UK AI Security Institute Inspect: tasks, agents, tools, sandboxes, scorers, retry, logs, and analysis | **Integrate; do not rebuild the whole runner ecosystem** | Import versioned Inspect `EvalLog` data through its supported API/JSON export, preserve task/sample/score/transcript/config identity, record source-log digest and converter version, and export AIES instrument metadata where lossless; round-trip tests disclose fields that cannot be represented |
| AI/agent telemetry | OpenTelemetry semantic conventions and OTLP | **Use as an optional observation source, not the canonical evidence schema** | An adapter maps version-pinned spans/events/metrics into typed canonical evidence while retaining trace/span IDs, sampling state, source convention version, clock boundaries, and collection gaps; prompts, retrieval content, tool arguments/results, and identities are opt-in, classified, redacted, and never logged by default |
| Repository findings | OASIS SARIF 2.1.0 | **Import and export standard static-analysis findings** | SARIF adapter preserves tool/rule/version, location, severity, fingerprints, fixes, suppressions, baseline state, and invocation status; an absent tool or incomplete run remains unknown, and SARIF findings never become proof of correctness |
| Security-control evidence | NIST OSCAL Assessment Results | **Provide a governed bridge for security/compliance consumers** | Optional export maps applicable AIES subjects, observations, findings, risks, evidence links, timestamps, and remediation items into OSCAL without claiming FedRAMP, legal, or control certification; canonical AIES evidence remains authoritative for AIES decisions |
| Software and AI composition | SPDX 3 AI, Dataset, Build, Security, and Software profiles | **Adopt rather than invent another BOM vocabulary** | Subject descriptors can attach validated SPDX documents; AIES records document digest/profile/version and maps components without flattening models, datasets, prompts, agents, services, and software into one legacy model field |
| Release provenance | SLSA provenance plus Sigstore/Cosign or equivalent verifiable attestations | **Generate and verify standard provenance** | Release packages, containers, and conformance bundles carry source/build provenance and signatures/attestations; verification is documented and CI-tested, and a valid signature is never represented as evidence that content is safe or correct |
| MCP assessment | Version-pinned official Model Context Protocol specification | **Test protocol behavior directly** | MCP profiles cover initialization/capability negotiation, prompts/resources/tools, pagination/change notifications, input/output schemas, errors, transport, lifecycle, authorization, audience binding, token passthrough prohibition, human approval, side effects, logging, and version negotiation; unsupported protocol revisions fail explicitly |
| AI governance and quality | NIST AI RMF/TEVV, ISO/IEC 42001, ISO/IEC 25059, and OWASP GenAI guidance | **Crosswalk and complement; do not claim equivalence or certification** | Every mapping identifies exact AIES evidence, strength (`equivalent`, `supports`, `related`, or `gap`), scope, version, and rationale; no crosswalk converts an AIES result into external certification |
| Command-line distribution | Python Packaging guidance, pipx, and uv tool isolation | **Publish as an isolated application** | Release documentation offers one canonical install plus supported pipx/`uv tool` alternatives, never requires `pip install --break-system-packages`, and tests install/upgrade/uninstall from built artifacts rather than the source checkout |

### Critical path and dependency order

Work may proceed in parallel within a track, but downstream claims stay blocked
until their prerequisite evidence exists.

| Track | Ordered dependency | Release/adoption gate |
|---|---|---|
| **Measurement credibility (P0)** | Define claim/estimand → preregister panel → validate raters/judges → execute compatible runs → quantify uncertainty/discrimination → independent interpretation → publish limitations | No promotional ECM comparison or AIES Select ranking before completion |
| **Release trust (P0)** | Ratify license → align versions → lock dependencies → build packages/containers → generate SBOM/AI-BOM and SLSA provenance → sign/attest → verify on clean machines | No public install recommendation before artifacts are legally reusable and verifiable |
| **First-use adoption (P1)** | Cross-platform `aies demo` → isolated install → `aies init` → preflight/plan → `aies evaluate` → `aies open` → first-run usability study | Target is first useful ECM in one session without governance expertise |
| **Demand and community (P1)** | Positioning/message matrix → conversion README → visual proof → persona paths → reproducible release → coordinated launch → responsive community funnel → measured iteration | No broad launch before the primary call to action works from a clean install and every public claim passes evidence review |
| **Standards approval (P1)** | Generate approval inventory → automated conformance → assign two independent reviewers → resolve findings → freeze v0.5 candidate → public comment/disposition → Maintainer consensus → status promotion | No `Approved`, “industry standard,” or certification claim before traceable completion |
| **Evidence interoperability (P1)** | Typed evidence events → adapter contract → Inspect/SARIF/OTel importers → OSCAL/SPDX exports → round-trip and adversarial fixtures → compatibility policy | Imported evidence cannot affect claims until provenance, loss, correlation, and applicability are explicit |
| **Subject expansion (P2)** | Subject Descriptor → Subject Assessment Profile → executor/evidence adapters → direct instruments → coverage matrix → calibration → report limitations → discovery registry | Never route a new subject kind through deployment scoring by convenience |
| **Selection and portfolio (P2)** | Validated ECM → workload schema → cost/latency/reliability evidence → compatibility filter → explained fit → sensitivity analysis → human decision record | AIES Select remains a scoped decision aid, never a universal leaderboard |

### Next executable tranche

This is the recommended sequence from the current verified baseline. Work in
the **Build now** lane can proceed while external review, panel recruitment, and
license governance are waiting on other people.

| Order | Lane | Status | Work package | Dependency | Exit signal |
|---:|---|---|---|---|---|
| 1 | Build now | Done | Define decision-product measurement claims and estimands | Existing ECM/evidence schemas | Versioned specification and fixtures state exactly what every score/confidence value means and does not mean |
| 2 | Build now | In progress | Deliver cross-platform `aies demo` | Existing `demo-full` implementation | Installed wheel now runs the concise offline narrative without Make/Bash and links the final ECM/report on Windows; macOS and Linux clean-install CI remain |
| 3 | Build now | In progress | Produce installable local release candidates | License is not required for private build testing; publication waits for ADR-0014 | Wheel and sdist build; isolated install, shipped-data validation, installed demo, and uninstall pass on Windows; upgrade plus macOS/Linux verification remain |
| 4 | Build now | Done | Implement `aies init` and safe discovery | Subject/workspace boundaries already defined for deployments | Clean machine reaches a non-destructive valid workspace, no secrets are written, and shell-specific exact next commands are printed |
| 5 | Build now | Done | Implement preflight planning and `aies evaluate` | `init`, existing qualify/benchmark engine | One beginner command previews calls/time/cost/limitations, then performs a bounded no-repeat automated evaluation and complete report generation |
| 6 | Build now | Done | Implement `aies open` and redacted sharing | Existing report bundle/dashboard | User opens the canonical local result by run ID and exports an immutable allowlisted bundle that anonymizes subject/environment values and excludes raw evidence |
| 7 | Build now | Done | Define Subject Descriptor, typed evidence events, and Evidence Adapter contract | Accepted ADR-0015 governs contract evolution | Experimental schemas, compatibility/loss/deduplication/privacy rules, deterministic conformance fixtures, and the Class 3 architecture decision are implemented; individual adapter profiles remain separately promotable |
| 8 | Build now | In progress | Implement Inspect log bridge | Evidence Adapter contract | Portable AIES Inspect JSON profile imports/exports with source hashes, explicit loss, immutable duplicate rejection, and no inferred score; validation against the pinned native Inspect API remains |
| 9 | Build now | In progress | Implement SARIF repository bridge | Evidence Adapter contract and repository-analysis ADR | SARIF 2.1.0 findings import/export with provenance and preserve tool/rule/location/severity/fingerprint/fix/suppression/baseline semantics; official schema validation and repository-audit consumption remain |
| 9A | Build now | In progress | Build the adoption and promotion launch kit | Demo, packaging, `init`/`evaluate`/`open`, measurement claims | Conversion README/Quickstart, CLI calls to action, persona message matrix, research-backed channel/funnel plan, claim-review checklist, launch sequence, social-preview asset, and safe community forms are implemented; an executable claim-review gate, terminal recording, example gallery, repository social-image configuration, and usability studies remain |
| 10 | External evidence | In progress | Execute preregistered multi-subject validity panel | Estimand, anchor protocol, compatible subjects, independent human labels | Published analysis covers discrimination, agreement, uncertainty, robustness, null results, and limitations |
| 11 | External governance | Blocked | Complete two independent reviews per approval candidate | Reviewer recruitment and review packets | Every candidate has two traceable non-author reviews and dispositioned findings |
| 12 | External adoption | Open | Publish comparative ECM case study and reproducible local/hosted pilots | Validity panel, installation path, independent reviewers, publishable evidence | Independent users reproduce results and report decision usefulness and limitations |
| 13 | Release governance | In progress | Ratify license and secure the release supply chain | ADR-0014 process, version alignment, package builds | Reusable licenses, SPDX metadata, dependency lock, SBOM/AI-BOM, SLSA provenance, signatures/attestations, and clean-machine verification are published |
| 14 | Expansion | Open | Promote the first non-deployment Subject Assessment Profile | Subject/evidence contracts and support registry | Choose one narrow profile—recommended first candidate: MCP server or repository engineering analysis—and ship direct instruments, executor, limitations, and discovery before starting another |

Do not start AIES Select, organization portfolio dashboards, certification
operations, or multiple subject executors ahead of this tranche. Those products
depend on validated ECM semantics, trustworthy distribution, and at least one
successful external adoption loop.

## 3. Vision Delivery Backlog

### P0 — Correctness and qualification integrity

| Status | Work item | Acceptance signal |
|---|---|---|
| Done | Correct Grant Readiness rendering | A fully decisional, gate-passing package renders `Overall: READY`; missing admitted evidence renders gates as not evaluated rather than failed; Markdown and HTML tests cover both paths |
| Done | Report corpus maturity honestly | Corpus health distinguishes calibration metadata, attributable human design review, external independent review, and empirical calibration; hash-bound acceptance cannot be mistaken for model-panel validation |
| Done | Make repository-audit detection deterministic | CI checks are found regardless of filesystem/YAML ordering; the AIES repository no longer reports its existing pytest CI gate as absent |
| Done | Align rating admission with AIES-AESQS-ER-01 — Evaluation Rubrics | Accepted ADR-0012 defines the required evidence-item/rater separation; human raters have verified identity, scope, qualification, and current calibration, and automated raters cannot be the sole decisional scoring basis |
| Done | Model evidence items separately from rater observations | Evidence Package v5 retains every rating observation but sends at most one resolved score per response evidence item into statistics; adjacent human ratings resolve conservatively, major divergences require an immutable named-human disposition, and tests prove a second rating cannot inflate sample size or confidence |
| Done | Enforce double-rating and agreement rules | RT1 — Minimal / RT2 — Moderate double-rate at least 20%; RT3 — Significant / RT4 — Critical double-rate every item; required agreement and divergence resolution are machine-checked |
| Done | Enforce the two-human qualification process | Every grant, conditional grant, and denial records an assessor and independent peer reviewer with qualification and conflict declarations |
| Done | Complete the qualification scope tuple | Records include subject, role, phases, maximum risk tier, competency × CL claims, framework version, applicable agent-definition version, sponsor, and validity window |
| Done | Make qualification lifecycle events immutable | Accepted ADR-0012 governs implementation; grant, condition change, renewal, suspension, invalidation, revocation, and supersession append separate ART-15 — Audit Trail Record events and prior records are never overwritten |
| Done | Show detailed live progress for every run | `qualify`, `benchmark`, resume, `review`, and `score` display progress implicitly with completed/total, percentage, current-stage elapsed time, total run elapsed time, throughput, ETA, the current human-readable scenario family/task objective and ordinal, failures, and resumability; parallel runs expose the dynamic active task set and effective worker capacity for any `--parallel N`; the same state persists in `progress.json`, while `aies runs progress <run-id>` is an optional second-terminal observer |
| Done | Make automated Engineering Evaluation self-contained | `qualify --judge`, `benchmark --judge`, `review --model-reviewer`, `score`, and `import` complete or refresh engineering analysis and the report bundle without a human prerequisite; named assessments emit non-blocking Engineering Assessment Results; capabilities default to ECM; guidance defaults to evidence-derived engineering fit; reports and executive summaries say formal qualification `not requested` rather than `blocked`; ECM confidence counts distinct scored task scenarios instead of human-admitted qualification items; human evaluation is an optional visible column; only explicit formal-qualification/grant paths apply ADR-0012 gates |
| Done | Enforce expiry and requalification | Expired or materially changed qualifications are treated as absent; renewal and targeted re-evaluation are supported |
| Done | Correct endpoint deployment fingerprints | Remote qualifications bind to behaviorally relevant deployment/runtime/config identity, not irrelevant client-machine RAM/CPU changes |
| Done | Govern ECM task decision semantics in an ADR | Accepted ADR-0013 and ECM schema 2 compute one resolved item per distinct task scenario, task-specific RT breadth, 90% uncertainty, risk-tier gates/EV3 hard-fail, reviewed mapping admission, human-rater protocol, parent-area floors, valid `demonstrated` semantics, compatible comparison, and Qualification-Record-bounded Deployment Guidance |

### P1 — Measurement validity

| Status | Work item | Acceptance signal |
|---|---|---|
| Done | Human-review the new RT2 — Moderate tranche | Umair Ali explicitly accepted all 268 listed instruments as repository owner and maintainer after a zero-gap deterministic preflight. One disclosed human-authorized AI-assisted tranche event records every scenario ID and content hash, does not fabricate separate manual click-through reviews, and automatically reopens changed content. All 484 now have effective design review; external independent review and empirical calibration remain open separately. |
| In progress | Empirically calibrate a preregistered real-subject panel | The platform now creates a content-addressed plan before runs, freezing owner, subjects/ranks and independent basis, exact instrument/prompt/content/suite hashes, tier, repeats, thresholds, and validated rating protocol. Completed runs must bind exactly to that plan; free-text timestamps and synthetic/manual panels are non-promotional. Four legacy subjects share seven CA-05 scenarios and 21 observations under one provisional protocol, but remain exploratory because no prior plan exists and the scorer is explicitly provisional/uncalibrated. A real study and human promotion decision remain external evidence. |
| Done | Define the measurement claim and estimand for every decision product | `aies-measurement-claims/v1` and fixtures state subject, target population, sampling frame, unit, outcome, aggregation, uncertainty, exclusions, intended decision, and prohibited interpretation for Engineering Evaluation, ECM, Fit, comparison, and Formal Qualification; ECM/report bundles cite the contract |
| Open | Separate benchmark, system, and field evidence | Reports identify controlled scenario results, integrated-system behavior, and field/operational observations as different evidence modalities; evidence transfer across levels requires an explicit rationale and never silently raises confidence |
| Open | Validate automated judges against independent human labels | A frozen, stratified anchor set estimates agreement, systematic bias, severity-specific errors, drift, and uncertainty for every judge/protocol version; failed calibration makes scores advisory but does not discard collected responses |
| Open | Test predictive and decision validity | Preregister whether task scores should predict held-out engineering outcomes, expert preference, defect/security findings, or workload success; report effect sizes, intervals, null results, and decision errors rather than only rank correlation |
| Open | Add sensitivity and robustness analysis | ECM and comparison show whether conclusions change under plausible rater resolution, weighting, missingness, scenario-family balance, outliers, and minimum-evidence choices; fragile conclusions are labelled |
| Open | Govern contamination and evaluation awareness | Public, practice, held-out, and protected instruments have separate identities and rotation rules; similarity, leakage, prompt memorization, benchmark-aware behavior, and evaluator gaming are tested and disclosed |
| Open | Connect pre-deployment evaluation to ongoing monitoring | Deployment guidance names observable signals, thresholds, sampling, incidents, drift/change triggers, and targeted reassessment; field evidence can invalidate stale fit guidance but cannot retroactively rewrite prior observations |
| Open | Establish versioned anchor-artifact libraries | Every competency area has human-consensus anchors across scores 0–4, including subtle AI-produced defects and refresh history |
| Open | Protect held-out evidence | Public examples, behavioral twins, and genuinely protected held-out instruments are distinct; contamination checks and refresh policy are recorded |
| Open | Grow no-repeat coverage beyond RT2 — Moderate | Each supported tier/area meets its distinct-instrument minimum with genuinely tier-appropriate decision types: current distribution RT1=24, RT2=387, RT3=52, RT4=21 |
| Open | Validate Engineering Task mappings empirically | ET-01 through ET-15 mappings receive human review and demonstrate task discrimination; mapping counts alone cannot establish capability |
| Open | Add task-specific uncertainty | ECM reports task-level effective sample, admitted evidence, interval, protocol, mapping version, and limitations without borrowing an area minimum as a task threshold |
| Done | Add hallucination and fabrication diagnostics | Report bundles include source-separated structured observations for unsupported assertions, fabricated APIs/entities, invalid citations/provenance, false success/test claims, and appropriate abstention; the descriptive grounding-reliability view maps to EV1 — Correctness, EV3 — Safety & Security, and EV6 — Traceability and cannot alter qualification decisions |

### P1 — Subject-neutral assessment architecture

| Status | Work item | Acceptance signal |
|---|---|---|
| In progress | Define a governed Subject Descriptor | Accepted ADR-0015, the experimental v1 JSON Schema, and the subject-support registry cover the envisioned kinds without a mandatory legacy model block; canonical run-manifest migration, schema conformance fixtures, and compatibility policy remain |
| In progress | Separate Subject Executor from Runtime Adapter | Accepted ADR-0015 defines the separation and imported Inspect/SARIF evidence no longer depends on generation, but runtime generation is still implemented through the legacy adapter path and a first non-runtime Subject Executor remains |
| In progress | Define typed canonical evidence events | The experimental v1 event schema and source-bound bridge conversions implement observation provenance, modality, correlation, classification, and payload; rating/reviewer/environment/lifecycle event families plus replay/migration fixtures remain |
| In progress | Define a versioned Evidence Adapter contract | Accepted ADR-0015, the experimental contract, Inspect/SARIF bridges, source hashing, loss accounting, redaction boundaries, and duplicate/no-claim-inflation tests exist; completeness and decision-product declarations, native-profile validation, and compatibility fixtures remain |
| Open | Define the Subject Assessment Profile contract | Every supported subject kind declares its descriptor schema, fingerprint/change triggers, executor or evidence adapters, applicable instruments, score semantics, minimums, gates, limitations, decision products, and human-review requirements |
| In progress | Model composite subjects and dependencies | The Subject Descriptor can reference component identities and the support registry exposes composites without claiming assessment support; typed dependency roles, version/fingerprint binding, evidence linkage, non-transfer rules, and composite decision products remain |
| Done | Add subject capability discovery | The versioned `subject-support-v1.yaml` registry drives `aies support`, `/support`, the generated Subject Support Matrix, package data, CI drift checking, and validation tests. It names implemented profiles/executors/entry points/limitations and keeps agents, swarms, MCP, coding assistants, prompts, RAG, pipelines, platforms, people/teams, and composites explicitly planned rather than silently routing them through deployment scoring |
| Open | Unify repository audit decision products | Repository maturity remains semantically distinct from AESQS rubric scoring but shares subject identity, evidence provenance, reporting, and portfolio views |

### P1 — Subject expansion program

Each subject kind receives a governed Subject Assessment Profile before an
executor is promoted from experimental status. EV1–EV6, ML0–ML4, or any future
scale applies only when the profile establishes that it is meaningful for that
subject and evidence type.

| Status | Subject track | Acceptance signal |
|---|---|---|
| Done | AI deployment output assessment | Versioned scenarios execute against local or remote deployments; responses, ratings, uncertainty, qualification boundaries, ECM, grounding diagnostics, and deployment guidance are produced from canonical evidence |
| Open | Human engineering work-sample assessment | Consent, identity, accommodations, work-sample provenance, assessor protocol, privacy/retention, appeal, competency evidence, and qualification lifecycle are implemented without covert productivity surveillance |
| Open | Team and human–AI pair assessment | Collaboration, handoffs, review effectiveness, shared context, decision ownership, escalation, recovery, and outcome evidence are evaluated without treating individual or model scores as a substitute for team evidence |
| Open | Agent-session assessment | Versioned tasks capture plans, tool calls, tool results, approvals, memory/context use, policy boundaries, side effects, failures, recovery, escalation, cost, latency, and final outcomes; replay and trace redaction are supported |
| Open | Agent-swarm assessment | Delegation, role separation, coordination, consensus/conflict handling, shared-state integrity, containment, cascading failure, aggregate cost, and accountable human control are assessed in addition to member-agent capability |
| Open | MCP-server assessment | Discovery and protocol conformance, schema accuracy, tool/resource contracts, authorization, least privilege, isolation, state handling, error behavior, injection resistance, reliability, latency, compatibility, and auditability enter canonical evidence |
| Open | Build an official-spec MCP conformance executor | A version-pinned executor produces direct protocol evidence for initialization, capabilities, tools/resources/prompts, pagination and notifications, schema behavior, lifecycle/errors, transports, authorization/audience validation, approval boundaries, and malicious/untrusted annotations; it distinguishes protocol conformance, security posture, engineering quality, and agent-level task outcomes |
| Open | AI coding-assistant assessment | IDE/repository context selection, code edits, diff quality, test behavior, secure defaults, command/tool use, provenance, approval boundaries, rollback, and repository-task outcomes are assessed as a composite assistant–repository subject |
| Open | Prompt-library assessment | Versioning, ownership, intended use, input/output contracts, regression suites, portability, injection resistance, sensitive-data handling, deprecation, drift, and task-specific effectiveness are assessed without publishing protected prompt content |
| Open | RAG-system assessment | Retrieval relevance/recall, grounding and citation validity, source integrity/freshness, authorization-aware retrieval, privacy, poisoning/injection resistance, abstention, latency, cost, drift, and failure behavior are directly assessed |
| Open | AI pipeline assessment | Data/model/prompt lineage, stage contracts, reproducibility, orchestration, quality gates, secrets, failure isolation, retry/idempotency, observability, rollback, cost, and promotion controls are assessed across the execution graph |
| Open | AI engineering platform assessment | Tenant and environment isolation, identity/access, policy enforcement, model/tool registry, audit trails, observability, resilience, supply chain, lifecycle governance, developer experience, and operating-model support are assessed against AEAR/AEOS evidence |
| Open | Composite-system end-to-end assessment | A declared system boundary links repositories, deployments, agents, MCP servers, RAG, pipelines, platforms, humans, and teams; component findings, interface failures, emergent risks, and end-to-end task outcomes remain traceable without averaging away a failed critical component |

### P1 — Cross-cutting multi-perspective assurance

“Comprehensive” means that applicability and evidence gaps are visible across a
governed set of perspectives; it does not mean that every perspective applies
to every subject or that missing evidence is silently treated as a pass. The
coverage model is extensible so a new technical, social, legal, environmental,
or industry perspective can be added without redesigning every executor.

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Govern an Assessment Coverage Matrix | Every Subject Assessment Profile declares applicable P01 — Business Strategy through P16 — Continuous Improvement lifecycle phases, X01 — Security through X15 — Sustainability cross-cutting domains, CA-01 — AI-Native SDLC Foundations through CA-12 — Governance, Risk & AI Safety competencies, ET-01 — Requirements Analysis through ET-15 — Production Operations tasks, RT1 — Minimal through RT4 — Critical risk tiers, AL0 — Manual through AL4 — Autonomous levels, stakeholders, environments, evidence modalities, operating conditions, and decision products; exclusions require a versioned rationale |
| Open | Make applicability and unknowns explicit | Every cell resolves to assessed, partially assessed, not assessed, not applicable with rationale, or unsupported; unknown, unavailable, tool-not-installed, redacted, and failed-to-collect evidence remain distinguishable and none can become a pass |
| Open | Cover nominal, boundary, adversarial, and recovery behavior | Applicable profiles test normal operation, edge and limit conditions, invalid input, misuse/abuse, hostile input, dependency failure, partial outage, rollback/recovery, long-running behavior, drift, and changed-environment behavior rather than relying only on happy paths |
| Open | Assess functional and engineering quality | Correctness, completeness, safety/security, maintainability, efficiency, traceability, requirements fit, architecture, integration, data quality, testability, usability, and profile-specific quality attributes are supported by direct evidence with declared confidence and limitations |
| Open | Assess security, safety, and abuse resistance | Threat models cover subject boundary, assets, identities, privileges, tools, data flows, dependencies, supply chain, prompt/context injection, poisoning, exfiltration, unsafe actions, denial of service, misuse, dual use, containment, kill/revoke paths, and incident response at the scoped risk tier |
| Open | Assess privacy, data, knowledge, and intellectual-property handling | Profiles address lawful/authorized collection, minimization, classification, consent where applicable, access, residency, retention, deletion, redaction, lineage, source integrity, confidentiality, protected prompts/evidence, licensing, copyright, and leakage through logs, embeddings, caches, tools, or outputs |
| Open | Assess human factors and affected parties | Profiles identify users, operators, reviewers, decision owners, data subjects, and affected non-users; they assess accessibility, workload, automation bias, over-reliance, review effectiveness, skill degradation, informed consent, fairness where consequential, contestability, appeal, accommodations, and protection from covert personnel surveillance |
| Open | Assess reliability and operational fitness | Evidence covers availability, latency classes, throughput, concurrency, saturation, timeouts, retry/idempotency, state consistency, observability, alerting, degraded modes, failover, backup/restore, rollback, incident learning, SLOs, capacity, change safety, drift detection, and requalification triggers |
| Open | Assess performance, cost, and resource impact | Reports separate quality from latency, throughput, token/compute, storage/network, energy/resource use, and total cost; declared workload and scale assumptions support trade-off analysis, budget ceilings, runaway-consumption controls, and repeatable cost-performance comparison |
| Open | Assess interoperability and portability | Protocol/schema conformance, version negotiation, backward compatibility, data/model/prompt portability, vendor substitution, import/export fidelity, configuration reproducibility, extension behavior, and graceful handling of unsupported capabilities are tested where applicable |
| Open | Assess lifecycle and supply-chain integrity | Evidence spans strategy and requirements through design, build, verification, release, operation, retirement, and improvement; provenance, dependencies, datasets, models, prompts, tools, artifacts, signatures, vulnerabilities, deprecation, ownership transfer, end-of-life, and secure disposal remain traceable |
| Open | Assess governance, legal, regulatory, and industry context | Profiles map applicable internal policy, qualification authority, segregation of duties, records, exceptions, regulatory obligations, external standards, jurisdiction, contractual constraints, sector hazards, and evidence-retention duties without presenting AIES output as legal certification |
| Open | Assess adoption and organizational feasibility | Decision products address operating-model fit, required roles and skills, review capacity, integration effort, migration/rollback, supportability, training, process change, developer/operator experience, total ownership cost, vendor/community health, and sustainable maintenance |
| Open | Validate from independent and diverse perspectives | Profile promotion requires documented technical, security, operations, human-factors, domain, and affected-party review as applicable; conflicts, minority findings, reviewer independence, competence, calibration, and disposition are retained rather than averaged away |
| Open | Generate coverage and blind-spot reports | Every assessment bundle shows perspective coverage, evidence depth, confidence, exclusions, stale evidence, conflicts, untested operating conditions, dependencies, residual risks, and the exact work required to close material gaps |
| Open | Prevent evidence reuse from inflating assurance | Canonical evidence may support multiple views but retains one source identity; reports disclose reused evidence, correlated instruments, inherited component evidence, and dependency overlap so counts, confidence, maturity, and comparison are not artificially increased |

### P1 — Repository engineering intelligence

The existing `aies audit <repo>` is a repository **conformance and practice
maturity** assessment. It verifies evidence such as tests, CI enforcement, ADRs,
security tooling, provenance, and governance controls; it does not claim that
source code is correct or that an architecture is good merely because those
artifacts exist. Deeper repository analysis is a separate evidence layer with
its own instruments and claim boundaries.

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Govern the repository-analysis layers | A companion ADR distinguishes (1) conformance audit, (2) static/dynamic repository engineering analysis, and (3) controlled repository-task benchmarking; it defines their score semantics, evidence admissibility, human authority, and prohibited claims |
| Open | Add a content-addressed Repository Subject Descriptor | Repository identity records commit/tree hash, relevant configuration, languages, build system, dependency state, submodule state, analysis scope, exclusions, environment, and tool versions so results are reproducible and changes trigger reassessment |
| Open | Define repository evidence adapters | Versioned adapters ingest native test, coverage, mutation, property/contract test, lint, type-check, complexity, duplication, dependency, SAST, secret-scan, SBOM, architecture-rule, and benchmark outputs without converting tool absence into a pass |
| Open | Add loss-aware SARIF import/export | SARIF 2.1.0 findings retain tool/rule/version, invocation success, artifact location, logical location, fingerprints, severity, baseline state, suppression, fixes, and provenance; unsupported fields produce a machine-readable loss report and imported results remain findings rather than correctness verdicts |
| Open | Implement evidence-based architecture analysis | Reports dependency/module topology, cycles, layering and boundary violations, coupling/cohesion indicators, architecture fitness-test results, and ADR-to-implementation traceability; every finding identifies affected artifacts and no unsupported “good architecture” verdict is emitted |
| Open | Implement a code-quality profile | Language-aware adapters report lint/type findings, complexity, duplication, dead-code signals, maintainability trends, documentation and testability evidence with tool/version provenance, confidence/coverage limits, and no cross-language comparison unless the instruments are compatible |
| Open | Implement correctness-assurance analysis | The platform executes or ingests reproducible tests, coverage, mutation, property/contract tests, static-analysis findings, and failure evidence; it reports demonstrated assurance and untested behavior rather than claiming that repository correctness has been proven |
| Open | Implement controlled repository-task benchmarks | Disposable, authorization-bounded workspaces run versioned defect-fix, refactoring, testing, API, migration, performance, security, and architecture tasks; patch validity, tests, regressions, safety, efficiency, and traceability are scored while the repository and executing agent remain separately identified subjects |
| Open | Emit repository remediation evidence | Every repository gap or finding feeds the common Evidence-Linked Remediation Plan with priority, impact, exact evidence, bounded corrective action, acceptance signal, owner/authority boundary, and reassessment command |
| Open | Add optional semantic repository review | A declared reviewer may analyze code/design context and propose findings with file/line evidence, uncertainty, reviewer identity, and conflicts; its output is advisory unless independently verified and never changes deterministic maturity or assurance scores by itself |
| Open | Unify repository report and comparison products | One linked bundle presents conformance maturity, architecture evidence, code quality, correctness assurance, security/tool findings, recommendations, limitations, and optional human-review status; comparisons require compatible commit scope, toolchain, configuration, language, and instrument versions |

### P2 — ECM and decision products

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Ratify AIES-ECM-01 — Engineering Capability Matrix | ECM is formally present in the Charter, Vision, architecture, Roadmap, governance, requirement IDs, and public review disposition |
| Done | Deliver a compact report bundle | Default evaluation bundles contain Engineering Evaluation Report, Engineering Assessment Result when applicable, ECM, Grounding Diagnostics, Engineering Fit Guidance, and Executive Summary; explicit formal runs contain the separate qualification artifacts. All are linked Markdown/JSON/HTML views indexed by `report-bundle.json` |
| Done | Mature Deployment Guidance | Use / Use with Review / Avoid incorporates task evidence, current matching qualification scope, live deployment-fingerprint continuity, role/phases, autonomy, conditions, validity, residual calibration/gate risks, and operational constraints; no guidance creates authority |
| Done | Add protocol-compatible ECM comparison | Default engineering comparison shows compatible observed task scores and the higher observed value without human review or a formal winner claim; explicit formal comparison additionally requires demonstrated status and the human-rater protocol before emitting a winner |
| Open | Build a cross-subject Evidence-Linked Remediation Plan | Findings from deployments, repositories, humans/teams, agents, swarms, MCP servers, coding assistants, prompt libraries, RAG systems, pipelines, platforms, and composite systems share a deterministic action schema: priority, impact, evidence, recommendation, acceptance signal, owner/authority, dependency, and reassessment trigger; optional generated narrative is labelled advisory and cannot alter evidence or scores |
| Open | Build AIES Select | A declared workload mix plus latency, cost, context, tool reliability, availability, and risk constraints produces an explained fit ranking over compatible evidence—never a global best-subject claim |
| Open | Build organization decision products | Inventory shows approved subjects, demonstrated task fit, qualification scope, conditions, drift, expiry, incidents, and requalification status |
| Open | Export security assessment evidence through OSCAL | A version-pinned optional OSCAL Assessment Results bridge emits scoped subjects, observations, findings, risks, evidence references, timestamps, and remediation links with a mapping/loss report; it never implies external control authorization or certification |
| Done | Rebuild `demo-full` as the AIES killer demo | The fully offline one-process CI narrative demonstrates deployment/repository/standard subjects, implicit live task/ETA progress, complete automated Engineering Evaluation, optional human-evaluation status, ECM strengths/gaps, Engineering Fit Guidance, protocol-compatible comparison without invented winners, conformance, corpus health, empirical-panel handoff, and the linked Executive Summary bundle; it does not stage a failed qualification or grant as the product story, and it avoids repeated inference, report computation, and production-timeout probes |

### P3 — Standards and adoption

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Reconcile ECM with the five-module architecture | A governed update establishes ECM as a foundational standard and updates dependent documents without weakening vendor neutrality |
| Open | Complete independent pilots | At least one local and one hosted assessment have independent human rating/review, reproducible artifacts, limitations, and published lessons learned |
| In progress | Prepare the v0.5 approval inventory and review packets | One generated inventory identifies every governed document targeted for v1.0, its module/editor, normative status, stable requirement IDs, checklist result, two required independent reviewer slots, review-record links, unresolved findings, disposition state, and promotion readiness; the initial approval scope includes 14 AEBOK, 7 AESQS, 20 AEOS, 13 AEAR, 6 AECT, and 3 Shared documents currently at Review |
| Open | Close automated conformance gaps before human review | Metadata, structure, RFC 2119 requirement IDs/titles, glossary/taxonomy use, relative links and document-ID citations, arithmetic, vendor neutrality, and status-transition checks pass for every approval candidate; exceptions are recorded rather than hidden |
| Blocked | Obtain two independent peer reviews for every approval candidate | Each Review document has at least two completed reviews by competent Reviewers who did not substantially author it; reviews are recorded as PR reviews or review issues with reviewer identity, scope, independence/conflict declaration, EV1 — Correctness through EV6 — Traceability findings, and recommendation. The same qualified reviewers may cover multiple documents, but AI review and the author’s own review do not satisfy this gate |
| Open | Resolve and disposition all review findings | Every independent-review and public-comment finding is fixed or explicitly waived with named reasoning; material changes return through the applicable decision class and affected documents are re-reviewed where necessary |
| Open | Run the v0.5 public-comment cycle | Publish a frozen review candidate, announce the comment window, retain every submission, classify and respond to substantiated objections, publish a disposition log, and ensure no unresolved Class 3 objection remains |
| Open | Ratify Review documents as Approved | After the evidence above is complete, Maintainers conduct the required seven-day lazy-consensus decision; the promotion commit links both peer reviews, finding dispositions, public-comment evidence where applicable, decision participants, conflicts/abstentions, and the exact document content hashes |
| Open | Complete module approval gates | AEBOK, AESQS, AEOS, AEAR, and AECT indexes and their governed child documents are Approved only after every document in that module meets the review protocol; ROADMAP phase statuses are updated from evidence rather than by declaration |
| Open | Approve Shared and release-governance foundations | Shared Glossary, Shared Taxonomy, Shared index, Governance, documentation standards, stability/compatibility/conformance policies, and other v1.0 normative foundations complete their applicable review and Class 3 processes before the modules depend on them as Approved contracts |
| In progress | Ratify open repository licenses | Proposed ADR-0014 defines CC BY-SA 4.0 for standards/assessment content and Apache 2.0 for executable software. Complete affiliation disclosures, announce and finish the seven-day Class 3 comment window, resolve objections, record Maintainer acceptance, then install exact license texts, path notices, SPDX/package metadata, and CI verification |
| Open | Publish a real release | Version story is consistent, a signed tag exists, release artifacts pass hygiene/conformance, and upgrade notes are published |
| Open | Demonstrate external adoption | Published case studies, third-party conformance runs, and contributors/reviewers from independent organizations satisfy Charter success criteria |

#### Approval portfolio at the current Review status

| Approval scope | Documents at Review | What is already true | What still blocks Approved |
|---|---:|---|---|
| AEBOK — AI Engineering Body of Knowledge | 14 | Content-complete and promoted from Draft | Two independent reviews per document, findings disposition, Maintainer ratification |
| AESQS — AI Engineering SDLC Qualification Standard | 7 | Content-complete and executable feedback incorporated | Two independent reviews per document, findings disposition, Maintainer ratification |
| AEOS — AI Engineering Operating System | 20 | Content-complete, including ROLE-01 through ROLE-14 | Two independent reviews per document, findings disposition, Maintainer ratification |
| AEAR — AI Engineering Architecture Reference | 13 | Core architecture and industry blueprints are content-complete | Two independent architecture-capable reviews per document, findings disposition, Maintainer ratification |
| AECT — AI Engineering Certification & Training | 6 | Framework, paths, labs, exams, and renewal content are complete | Two independent certification/assessment reviews per document, findings disposition, Maintainer ratification |
| Shared Standards | 3 | Glossary, Taxonomy, and Shared index are at Review | Independent Maintainer review plus applicable Class 3 governance and ratification |
| **Module and Shared subtotal** | **63** | Internal content milestone reached | External review evidence and governance decisions remain |

This portfolio count is a planning snapshot, not a waiver of the generated
release-wide inventory. Root governance, documentation standards, ECM, and
other governed v1.0 documents have their own lifecycle states and must be
included before public release.

## 4. Cleanup and Debt Backlog

### C0 — Correctness-adjacent cleanup

| Status | Cleanup item | Acceptance signal |
|---|---|---|
| Done | Resolve duplicate document IDs | This backlog is AIES-DOC-14 and the dated Project Evaluation is AIES-DOC-15; every governed document ID is unique and the affected citation is updated |
| Open | Replace generic requirement labels | References show code plus meaningful obligation title, not `requirement NN`; a machine-readable registry and CI check cover all governed IDs |
| Open | Remove stale model-only identity language | Current docs use subject/deployment terminology; historical superseded ADR text remains immutable and clearly historical |
| Done | Reconcile backlog and Roadmap | ROADMAP now contains public phase/milestone status only, links here as the single authoritative implementation backlog, removes stale duplicated work-item statuses, and distinguishes delivered implementations from open governance, empirical-validation, subject-adapter, pilot, and release work |
| Open | Clarify frozen versus experimental contracts | Draft/Review contracts are not presented as ratified v1; experimental stability and Approved standard stability are labeled separately |

### C1 — Platform maintainability

| Status | Cleanup item | Acceptance signal |
|---|---|---|
| Open | Split the CLI monolith | Parser construction and command handlers are separated by domain with unchanged tested command behavior |
| Open | Consolidate duplicate commands | `registry`/`deployment`, `profile`/`profiles`, and `qualification`/`qualifications` have one canonical surface plus documented deprecation aliases |
| Open | Consolidate report view models | Markdown, HTML, JSON, dashboard, and API consume shared factual view models; no renderer recomputes decisions |
| Open | Replace heuristic repository detection with structured evidence where available | CI, dependency, test, coverage, security, architecture, and governance checks prefer parsed manifests or imported tool results over filename/substring heuristics; heuristic fallbacks are labelled with lower evidence confidence and regression fixtures cover supported stacks |
| Open | Standardize assessment vocabulary across commands and docs | `audit` means repository/practice conformance, `analysis` means artifact/tool evidence evaluation, `benchmark` means a compatible controlled comparative study, and `qualification` means a governed human decision; help and reports do not use the terms interchangeably |
| Done | Generate and test the subject-support matrix | One versioned machine-readable registry drives CLI help, API discovery, generated documentation, installed package data, CI drift detection, and tests for implemented/experimental/planned subject profiles so public claims cannot drift ahead of executable support |
| Open | Generate and test the perspective-coverage registry | One machine-readable registry drives profile applicability, coverage reports, human-readable code labels, documentation, and validation for lifecycle, cross-cutting, competency, task, risk, autonomy, stakeholder, environment, evidence, and operating-condition perspectives |
| Done | Clarify immutable artifacts and regenerable views | Storage policy classifies append-only records, derived canonical snapshots, mutable workflow state/configuration, and regenerable views; `workspace.write_json` rejects append-only replacement and `workspace.write_view` cannot target evidence paths |
| Done | Make record identifiers concurrency-safe | Qualification Records atomically claim human-readable IDs through exclusive creation; a 12-decision concurrent regression proves unique issued records and lifecycle events |
| Done | Improve local verification feedback | The documented command reports ranked durations and uses a 180-second warm-cache Windows budget with a 25% regression trigger. Single-pass report views plus signature-invalidated isolated YAML, expanded-scenario, review-ledger, and suite caches retain complete coverage while the expanded 282-test suite completes in 107.96 seconds on the latest Windows verification host; cache mutation/invalidation behavior has regression coverage. Read-only API fixtures are shared safely and concurrency tests delay only the phase under test. |
| Done | Keep package-build artifacts out of review | Root ignore policy excludes `build/`, `dist/`, and demo workspaces; release-hygiene validation passes after local wheel/sdist builds |
| Done | Generate exhaustive CLI guidance and shell completion | A parser-derived CLI reference covers every command, subcommand, positional parameter, option, default, choice, prerequisite, interaction, result/side effect, recommended next step, and workflow sequence; CI detects undocumented parser drift, and PowerShell/Bash/Zsh Tab completion is generated from the same live command surface |
| Done | Remove local workspace archive debris safely | `aies doctor` inventories `.DS_Store`, `Thumbs.db`, `desktop.ini`, `__MACOSX`, Python/pytest caches, and misplaced regenerable views under the runs root; JSON exposes every path and category, readiness is unaffected, and tests prove the diagnostic deletes neither debris nor evidence |

### C2 — CI, security, and release hygiene

| Status | Cleanup item | Acceptance signal |
|---|---|---|
| Done | Expand CI path coverage | Changes to Shared, AEBOK, AESQS, AEOS, AEAR, AECT, ECM, ADRs, governed docs, platform, and conformance trigger relevant checks |
| Done | Test supported Python versions | CI runs the complete platform gate on Python 3.10, 3.11, 3.12, 3.13, and 3.14; installation docs identify that tested range |
| Open | Add documentation governance checks | CI detects duplicate document/requirement IDs, missing meaningful titles, broken links, invalid metadata/status transitions, and stale references |
| Open | Add code-quality checks | Formatting, linting, type checking, and coverage thresholds run in CI |
| Open | Add supply-chain controls | Lock and review dependencies; run secret scanning/SAST; emit SPDX 3 Software/AI/Dataset/Build profiles where applicable; generate SLSA provenance for packages, containers, and conformance bundles; sign or attest release artifacts with Sigstore/Cosign or an equivalently verifiable mechanism; CI verifies identity, digest, source revision, builder, and provenance before publication and states that provenance does not prove safety or correctness |
| Open | Publish a real security contact | Dedicated email and optional encryption key replace the placeholder fallback; private vulnerability reporting remains preferred |
| Open | Add ownership and protected-branch evidence | CODEOWNERS and externally attested branch-protection/human-review gates satisfy the repository’s own audit |
| Open | Align versions | Package version, standards milestone, artifact versions, changelog, tags, and release names answer different versioning questions explicitly and consistently |
| Done | Correct current CI identity wording | Workflow and active docs say Engineering Assessment Platform rather than Qualification Platform |

## 5. Current Verified Baseline

Last verified on 2026-07-23:

- `pytest platform/tests -q`: **282 passed in 107.96 seconds** on the latest
  Windows run, below the documented 180-second warm-cache budget.
- `aies suites validate`: **484 scenarios, 12 areas, 0 warnings, 0 errors**;
  **268 effective hash-bound ledger acceptances, 0 stale, 0 unknown**.
- Decision-engine conformance: **8/8 cases passed**, semantics 1.0.
- Release hygiene: **PASS**.
- Local distribution verification: wheel and sdist build; isolated wheel
  install runs suite validation and the offline demo; isolated sdist install,
  validation, and uninstall pass on Windows. Cross-platform package/demo CI is
  now defined and awaits hosted-run evidence.
- Repository audit at RT2 — Moderate: **PASS**, with 18 verified controls and
  8 gaps; the prior order-dependent CI-test false negative is covered by a
  regression test.
- Scenario review maturity: **484/484 human design-reviewed**, **0/484
  empirically calibrated**. The accepted 268-instrument tranche is one
  transparent human-authorized AI-assisted decision bound to every scenario ID
  and content hash; it claims no separate manual click-through reviews and no
  external independent validation. Any content change reopens that instrument.
- `python platform/scripts/demo_full.py`: the complete 16-stage offline demo
  passed in **11.8 seconds** on the current Windows workstation.

## Related Documents

- [Roadmap](../ROADMAP.md)
- [Vision](VISION.md)
- [Project Charter](PROJECT_CHARTER.md)
- [Engineering Assessment Platform Specification](PLATFORM.md)
- [AIES-ECM-01 — Engineering Capability Matrix](../ECM/README.md)

## References

- NIST — [AI Test, Evaluation, Validation and Verification
  (TEVV)](https://www.nist.gov/ai-test-evaluation-validation-and-verification-tevv)
- NIST — [Practices for Automated Benchmark Evaluations of Language Models,
  initial public draft](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.800-2.ipd.pdf)
- NIST — [Expanding the AI Evaluation Toolbox with Statistical
  Models](https://www.nist.gov/news-events/news/2026/02/new-report-expanding-ai-evaluation-toolbox-statistical-models)
- NIST — [ARIA Pilot Evaluation
  Report](https://www.nist.gov/publications/assessing-risks-and-impacts-ai-aria-pilot-evaluation-report)
- NIST — [OSCAL Assessment Results Model
  1.1.2](https://pages.nist.gov/OSCAL-Reference/models/v1.1.2/assessment-results/json-reference/)
- UK AI Security Institute — [Inspect](https://inspect.aisi.org.uk/) and
  [Eval Logs](https://inspect.aisi.org.uk/eval-logs.html)
- OpenTelemetry — [Semantic
  Conventions](https://opentelemetry.io/docs/specs/semconv/)
- OASIS — [Static Analysis Results Interchange Format (SARIF)
  2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/cs01/sarif-v2.1.0-cs01.pdf)
- Model Context Protocol —
  [Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/index)
  and
  [Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- SPDX — [Specifications](https://spdx.dev/use/specifications/) and
  [AI profile overview](https://spdx.dev/learn/areas-of-interest/ai/)
- SLSA — [Specification 1.2](https://slsa.dev/spec/v1.2/) and
  [Provenance](https://slsa.dev/spec/v1.2/provenance)
- Sigstore — [Cosign signing and verification
  quickstart](https://docs.sigstore.dev/quickstart/quickstart-cosign/)
- Python Packaging Authority — [Installing stand-alone command-line
  tools](https://packaging.python.org/en/latest/guides/installing-stand-alone-command-line-tools/)

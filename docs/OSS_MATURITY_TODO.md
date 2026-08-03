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

Canonical reusable source:
[AIES Assessment and Assistance Flow](../diagrams/aies-assessment-and-assistance-flow.mmd).

```text
AEBOK / AESQS / AEOS / AEAR / AECT / ECM
                    │
                    ▼
       Assessment Plan + Subject Descriptor
                    │
                    ▼
        Frozen Assessment Instrument
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
 Candidate Projection   Reviewer Projection
     (task only)        (complete, post-evidence)
         │                     │
         ▼                     │
 Subject Executor / Evidence Adapter
                    │
                    ▼
  Canonical Evidence + Standards Traceability
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
 Engineering      ECM      Conformance
 Evaluation
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

Separate: standards + instrument → aies apply → guided output
          (informational; excluded from qualification evidence)
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
| S2 | Blocked | Prove ECM measurement validity | The harness and claims are implemented; completion requires a preregistered representative panel, independent human labels and mapping review, and publication of uncertainty, stability, negative, and null findings |
| S3 | Open | Publish the first comparative ECM case study | At least three materially different subjects run the same compatible preregistered workload; the public bundle includes prompts/instruments where publishable, hashes, raw and resolved observations, cost/runtime, limitations, ECM, fit guidance, and independent engineering review; it reports scoped differences without declaring a universal winner |
| S4 | Open | Publish one local and one hosted reproducibility pilot | A third party can reproduce both runs from a clean environment using version-pinned instructions; expected and observed differences, failures, repair steps, environment fingerprints, and lessons learned are retained |
| S5 | Open | Validate integration with the existing evaluation ecosystem | The versioned Inspect-compatible and SARIF bridges are implemented; completion requires pinned official-schema/API validation and an independently reproduced external-tool round trip |
| S6 | Done | Make first value reachable in one session | The clean-install journey, offline demo, guided non-secret initialization, deployment registration/discovery, bounded plan/evaluation, declared cost/ETA, progress/resume, result opening, advisory CI evidence, and uninstall are implemented and documented. Hosted reproducibility and first-user studies remain separate external-validation items |
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
| Done | Ship the one-command trial implementation | `aies demo` runs the concise offline product narrative without Make/Bash, works from source and an installed wheel on Windows, links the generated ECM/report, and is exercised by the cross-platform clean-install CI journey. Hosted platform results are a release-validation dependency, not unfinished command implementation |
| Done | Produce installation-grade local package candidates | Wheel/sdist construction, isolated Windows installation, shipped-data validation, demo, support/starter checks, uninstall, venv/pipx/uv guidance, and the prohibition on `--break-system-packages` are implemented. Public package publication remains separately blocked by licensing and release-supply-chain governance |
| Done | Add guided workspace initialization | `aies init --guided` interactively selects deployment evaluation, offline demo, or repository audit; deployment setup validates and previews id/model/endpoint/role/credential environment variable, writes no secret, preserves existing files, and prints the exact next command. Equivalent non-interactive flags support reproducible onboarding |
| Done | Add one canonical beginner evaluation command | `aies evaluate <subject>` validates the subject/judge, selects a bounded no-repeat default, supports plan-only, runs the canonical automated pipeline, prints the result link and sharing command, and optionally opens it; advanced commands remain available |
| Done | Make planning precede cost and waiting | `aies evaluate --plan-only` makes no endpoint calls and reports distinct candidate calls, batched judge calls, concurrency, no-repeat scope, structured per-phase and total cost/duration from validated manifest declarations, exact unknown reasons, limitations, and response/rating/report resumability |
| Done | Supply decision-oriented starter profiles | The packaged `decision-starters-v1.yaml` registry and `aies starter list/show` cover “compare coding deployments,” “understand one deployment,” “audit this repository,” and “try formal qualification”; each starts with the decision and states prerequisites, workflow sequence, artifacts, what it does not prove, time/cost class, evidence breadth, and next expansion without executing anything |
| Done | Make every failure actionable | Every expected CLI command family now emits the secret-safe `aies-cli-failure-v1` contract with cause category, preserved work, exact recovery, troubleshooting anchor, and duplicate-cost risk; a tested global fallback covers unexpected handler failures. HTTP 429 preserves `Retry-After`, no bespoke `print("error: ...")` branches remain, and installed-wheel CI validates the machine contract |
| Done | Publish a shared application overview contract | `aies overview`, `GET /overview`, and the HTML dashboard consume versioned `aies-workspace-overview` facts covering deployments, runs, assessments, subject support, and human-governed records. It is informational/read-only, includes explicit limitations, and provides a stable boundary for integrations and a future frontend without duplicating decision logic |
| Done | Publish a secure shared run-detail contract | `aies runs show RUN` and `GET /runs/{id}` consume versioned `aies-run-view` facts for subject/scope, durable execution state, decision-product summaries, storage classes, artifact availability, and exact links. Dedicated endpoints serve stored report, bundle, evaluation, ECM, guidance, executive-summary, and diagnostics JSON verbatim; API failures use `aies-api-error` v1 and path-like run identifiers are rejected |
| Done | Make reports effortless to find and share | Completion identifies result artifacts; `aies open <run-id>` opens or links the primary view and exports an immutable allowlisted/anonymized ZIP that excludes raw evidence, ratings, fingerprints, and secrets |
| Done | Add a terminal evidence-to-decision snapshot | `aies snapshot <run>` and successful `demo`, `evaluate`, and `open` flows reuse canonical ECM/Fit facts to show ET code and title, distinct evidence, observed capability, separate scenario breadth, assurance disclosures, optional human-evaluation status, unknown tasks, and a non-authorizing engineering interpretation in wide or narrow terminals |
| Done | Add adoption-grade CI integration | The pinned reusable GitHub workflow verifies evaluator decision semantics, calculates repository evidence at the selected risk tier, emits notice/warning annotations and a step summary, retains JSON/Markdown/annotation artifacts even on failure, requests only read access, and cannot block unless the caller explicitly sets `enforce: true`; `aies ci audit` supplies the tested local equivalent |
| Done | Add containerized reproducibility | The non-root OCI-labelled image and guide cover the offline demo, read-only repository audit, conformance corpus, supported networked assessment planning, mounts, secrets/network boundaries, artifact ownership, cleanup, and amd64/arm64 buildx usage. CI exercises demo, audit, and conformance; signed multi-architecture publication is separately tracked as release-supply-chain work |
| Done | Automate first-run journeys on every supported platform | The installed-wheel matrix runs `clean_install_journey.py` on Windows, macOS, and Linux through init, demo, discovery, bounded offline evaluation, resume, report opening, advisory CI evidence, and uninstall using paths with spaces and a non-default workspace. Hosted-result confirmation and a prior-version upgrade fixture remain release-validation work |
| Open | Complete hosted and upgrade-path release validation | Obtain successful clean-install results from the supported hosted Windows, macOS, and Linux matrix, exercise a genuine prior-version upgrade, and retain the resulting release evidence |
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
| Done | Create the evidence-backed visual identity foundation | The evidence → ECM → assurance → decision hero and visual direction are delivered without certification or fictional-result claims. Individual launch assets, terminal captures, screenshots, accessibility variants, and repository configuration are discrete promotion deliverables rather than an indefinitely active identity task |
| Done | Make the CLI itself invite the next useful action | Bare `aies`, `init`, `demo`, `evaluate`, `open`, `snapshot`, audit results/gates, comparisons, and report completion present context-specific next commands and expected value without ads, nagging, telemetry, blocking prompts, or changes to JSON/CI semantics |
| Open | Build persona-specific landing paths | Engineers, engineering leaders, AI platform teams, auditors/governance teams, researchers/evaluators, standards contributors, and tool integrators each get a short “decision → command → artifact → limitation → next step” path |
| In progress | Publish a 60-second proof and a ten-minute guided trial | A claim-scoped 31-second README GIF and eight reusable stills now show important CLI paths, deployment discovery and built-in help, live evaluation, a real retained model ECM, fresh repository self-audit, compatible comparison, and report products without private run material. Complete the narrated 5–10 minute trial and validate comprehension with unfamiliar clean-machine users |
| Open | Publish outcome-led example galleries | Sanitized bundles show model/deployment comparison, repository analysis, reassessment after change, local/private evaluation, and eventual MCP evidence; every example names its decision, evidence scope, limitations, runtime, and reproduction command |
| Open | Establish a launch channel plan | Versioned release, technical launch article, short demo video, GitHub social card, Discussions launch thread, targeted standards/evaluation/MLOps communities, conference/demo submissions, and partner outreach reuse one claim-reviewed message matrix |
| Open | Create a claim-review gate for promotional content | Every headline, comparison, screenshot, talk, post, and badge maps to canonical evidence and a maturity label; uncalibrated, proposed, experimental, supported, and production-validated claims cannot be visually confused |
| Done | Create the user-to-contributor intake funnel | README and `CONTRIBUTING.md` route to safe structured forms for first-run failure, report comprehension, reproducible case studies, scenario instrument review, and adapter proposals, with real Discussions/private-security links and regression validation |
| Open | Operate and mature the contributor community | Configure Discussions categories, curate `good first issue`/`help wanted` work, publish an adapter starter kit and response expectations, recognize contributors, and establish maintainer succession evidence |
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

### Public repository release program

Public visibility, open-source permission, a public-comment release, and the
stable v1.0 standard are separate milestones. The repository may enter public
development before empirical validation and independent adoption are complete,
but it MUST NOT be described as open source until effective licenses are
granted, and it MUST NOT be described as an Approved standard or v1.0 before
the governance gates below are complete.

| Milestone | Meaning | Minimum entry gate |
|---|---|---|
| **Private development** | Maintainers and invited reviewers can inspect the evolving implementation | Current state; no public reuse claim |
| **Public development preview** | Anyone can inspect, use, modify, and contribute under effective licenses; standards remain at Draft/Review and evidence limitations remain prominent | PR-01 through PR-05 below; release authority records the visibility decision |
| **v0.5 public comment** | A frozen standards candidate is open for formal comment and disposition | Approval inventory, automated conformance, independent review progress, comment protocol, and content hash freeze |
| **v1.0 stable** | Approved, citation-stable standard and supported reference platform | Public comment closed; findings resolved; modules and Shared foundations ratified; signed reproducible release published |

The following chunks are the authoritative implementation order. A chunk is
`Done` only when its evidence column exists; implementation progress cannot
close a named-human or external-verification gate.

| Chunk | Lane | Status | Scope | Required evidence / exit signal |
|---|---|---|---|---|
| **PR-01 — Release control plane** | Build now | Done | Consolidate this plan; add fail-closed public-release preflight, CODEOWNERS review routing, dependency-update automation, least-privilege CI permissions, and a retained non-blocking readiness artifact | `check_public_release.py` reports every local blocker and external confirmation without granting authority; tests cover pending and locally complete states |
| **PR-02 — Security and history assurance** | Build now + external confirmation | In progress | Add CodeQL/SAST, dedicated full-history secret scanning, dependency/container scanning, explicit workflow permissions, retained machine-readable results, and a review procedure for historical Actions logs/artifacts | Local scanners pass across source, dependencies, and all reachable history without leaking matched values; CodeQL, historical Actions review, and Private Vulnerability Reporting remain external confirmations |
| **PR-03 — License ratification and implementation** | Human governance, then build | Done | ADR-0014 records named acceptance and the private-repository bootstrap-review limitation; official texts, authoritative path scope, package metadata, contribution/badge notices, and CI boundary verification are installed | Accepted ADR, effective path-based licenses, exact official texts, and CI proving every distributed path resolves to exactly one applicable license |
| **PR-04 — Version and distribution trust** | Build after PR-03 | In progress | Version axes and `aies version` are documented; wheel/sdist content, Apache metadata, hashes, and a limitation-explicit release manifest are CI-validated and retained. Remaining: choose the preview version; lock release dependencies; publish a multi-arch image; generate SBOM/AI-BOM and SLSA provenance; sign/attest artifacts | Clean-machine Windows/macOS/Linux verification, prior-version upgrade evidence, signed artifacts, independently verified provenance, and release notes |
| **PR-05 — Repository protection and publication decision** | External repository settings + human release authority | Open | Protect `main`; require current CI and CODEOWNER/human review; restrict bypasses and workflow permissions; enable security features; review retained logs/artifacts; run the readiness gate; record the named-human visibility decision | GitHub settings evidence, zero unresolved release blockers, signed preview tag, immutable release bundle, and recorded publication decision |
| **PR-06 — Public preview conversion loop** | Public adoption | Open | Publish the 60-second proof, ten-minute trial, persona paths, example bundles, Discussions categories, first issues, launch article/video/social assets, and a claim-reviewed announcement | Five unfamiliar users complete first use; failures and comprehension findings are published and fixed; first local and hosted reproducibility pilots are retained |
| **PR-07 — Evidence credibility and v1.0 governance** | External evidence and governance | Blocked | Execute the preregistered representative panel, validate judges against independent human labels, publish comparative cases and null findings, complete two independent reviews per approval candidate, run v0.5 comment, and ratify v1.0 | Measurement-validity report, independent pilot evidence, disposition ledger, Approved documents, signed v1.0 release, and maintenance cadence |

#### PR-01 implementation checklist

| Status | Task | Owner type | Verification |
|---|---|---|---|
| Done | Add default and high-impact CODEOWNERS routes | Maintainer | `.github/CODEOWNERS` is detected by the repository audit; branch enforcement remains PR-05 |
| Done | Add automated update discovery for Actions, Python, and the container | Maintainer | `.github/dependabot.yml` parses and covers all three ecosystems |
| Done | Add a non-authorizing public-release readiness contract | Platform | Text and JSON enumerate local blockers, external confirmations, limitations, and exact next actions; `--gate` fails closed and accepts only schema-valid, named, timezone-stamped `--external-evidence` confirmations for controls not provable from the checkout; a safe all-false template is shipped |
| Done | Retain readiness output in CI without blocking ordinary development | Platform | A dedicated CI job uploads `public-release-readiness.json`; publication still requires an explicit gated run |
| Done | Reduce default workflow token authority | Maintainer | Platform CI declares `contents: read`; later jobs must request any additional permission explicitly |
CODEOWNERS enforcement, protected-branch settings, and Private Vulnerability
Reporting are deliberately not counted as PR-01 implementation. They are
externally verified repository controls in PR-05; the readiness gate continues
to report them until a repository administrator supplies that evidence.

#### PR-02 implementation checklist

| Status | Task | Owner type | Verification |
|---|---|---|---|
| Done | Scan complete Git history for secrets | Maintainer | Checksum-pinned Gitleaks 8.30.1 scanned 77 reachable commits with 100% redaction and zero undispositioned findings; one synthetic-token match is suppressed by exact commit/path/rule/line fingerprint |
| Done | Add high-signal Python static analysis | Maintainer | Ruff 0.15.22 security rules pass; HTTP(S) endpoint validation and entity-safe XML evidence parsing close the actionable findings, while documented low-signal exclusions remain reviewable |
| Done | Audit resolved runtime dependencies | Maintainer | pip-audit 2.10.1 resolved three direct/runtime dependencies and reported zero known vulnerabilities in the 2026-07-27 observation |
| Done | Pin CI action identities and minimize authority | Maintainer | Checkout, Python setup, and artifact upload use immutable action commit SHAs; workflows default to read-only contents permission |
| Done | Retain redacted, machine-readable evidence | Platform | CI uploads Gitleaks JSON, SARIF, dependency JSON, tool versions, distribution checksum, source revision, scope, and redaction metadata even when a scanner fails |
| Done | Provide a repeatable local security command | Platform | Canonical `aies security` works on macOS, Linux, and Windows; it automatically downloads the platform-specific Gitleaks 8.30.1 archive, verifies its published SHA-256, uses a tamper-checked user-local cache without modifying Homebrew/PATH, and runs full-history secret scanning, Python security rules, and dependency audit. `make security` is only an optional alias |
| Open | Publish a dedicated security contact | Named maintainer | Replace the placeholder fallback in `SECURITY.md` with the approved monitored address and optional public key |
| Open | Enable and test Private Vulnerability Reporting | Repository administrator | A harmless test report verifies private intake, maintainer notification, acknowledgement, and closure without exposing sensitive content |
| Open | Enable CodeQL default setup after eligibility | Repository administrator | After public visibility, Python CodeQL default setup completes and its first successful result is retained; local Ruff remains complementary rather than being relabelled CodeQL |
| Open | Review historical Actions logs and artifacts | Named maintainer | Review retained workflow logs/artifacts for credentials or private data, revoke anything exposed, and record the named/time-stamped external confirmation used by the readiness gate |

### Next executable tranche

This is the recommended sequence from the current verified baseline. Work in
the **Build now** lane can proceed while external review, panel recruitment,
release engineering, and repository-setting verification continue.

| Order | Lane | Status | Work package | Dependency | Exit signal |
|---:|---|---|---|---|---|
| 1 | Build now | Done | Define decision-product measurement claims and estimands | Existing ECM/evidence schemas | Versioned specification and fixtures state exactly what every score/confidence value means and does not mean |
| 2 | Build now | Done | Deliver cross-platform `aies demo` | Existing `demo-full` implementation | The command and cross-platform installed-wheel journey are implemented; hosted release evidence is tracked independently |
| 3 | Build now | Done | Produce installable local release candidates | Path-based licensing is effective; publication still requires the release-readiness gates | Wheel and sdist build, isolated install, shipped-data validation, installed demo, and uninstall pass on Windows |
| 4 | Build now | Done | Implement `aies init` and safe discovery | Subject/workspace boundaries already defined for deployments | Clean machine reaches a non-destructive valid workspace, no secrets are written, and shell-specific exact next commands are printed |
| 5 | Build now | Done | Implement preflight planning and `aies evaluate` | `init`, existing qualify/benchmark engine | One beginner command previews calls/time/cost/limitations, then performs a bounded no-repeat automated evaluation and complete report generation |
| 6 | Build now | Done | Implement `aies open` and redacted sharing | Existing report bundle/dashboard | User opens the canonical local result by run ID and exports an immutable allowlisted bundle that anonymizes subject/environment values and excludes raw evidence |
| 7 | Build now | Done | Define Subject Descriptor, typed evidence events, and Evidence Adapter contract | Accepted ADR-0015 governs contract evolution | Experimental schemas, compatibility/loss/deduplication/privacy rules, deterministic conformance fixtures, and the Class 3 architecture decision are implemented; individual adapter profiles remain separately promotable |
| 8 | Build now | Done | Implement Inspect log bridge | Evidence Adapter contract | Portable AIES Inspect JSON profile imports/exports preserve source hashes, explicit loss, immutable duplicate rejection, typed events, and no inferred score; independent pinned-native API validation remains under the external interoperability track |
| 9 | Build now | Done | Implement SARIF repository bridge | Evidence Adapter contract and repository-analysis ADR | SARIF 2.1.0 findings import/export preserve provenance, tool/rule/location/severity/fingerprint/fix/suppression/baseline semantics, typed events, and repository-analysis consumption; independent official-schema validation remains under the external interoperability track |
| 9A | Build now | Done | Build the adoption and promotion launch-kit foundation | Demo, packaging, `init`/`evaluate`/`open`, measurement claims | Conversion README/Quickstart, CLI calls to action, persona message matrix, research-backed channel/funnel plan, claim-review checklist, launch sequence, social-preview asset, and safe community forms are implemented; individual launch assets and studies remain explicit Open items |
| 10 | Build now | Done | Execute PR-01 release control plane | Existing CI, audit, and governance boundaries | The retained readiness contract is implemented; external repository-setting confirmations remain explicit |
| 11 | Build now | In progress | Execute PR-02 security and history assurance | PR-01 inventory and repository ownership | Local security workflows and full-history evidence pass; external CodeQL/PVR/history-log confirmations remain open |
| 12 | Release governance | Done | Execute PR-03 license ratification and implementation | Named-human ADR-0014 decision | Reusable licenses and unambiguous path/package metadata are effective; retrospective public comment on the bootstrap decision remains required during preview |
| 13 | Build after license | In progress | Execute PR-04 version and distribution trust | Effective license and selected preview version | Version inventory plus validated content-addressed package manifests are implemented; signed reproducible packages/container and upgrade evidence remain |
| 14 | Release authority | Open | Execute PR-05 repository protection and publication decision | PR-01 through PR-04 | Readiness gate and external confirmations pass; named human records publication |
| 15 | External adoption | Open | Execute PR-06 public preview conversion loop | Public preview and claim-reviewed assets | First-use study and reproducible local/hosted pilots publish their findings |
| 16 | External evidence/governance | Blocked | Execute PR-07 evidence credibility and v1.0 governance | Representative subjects, independent reviewers, and public comment | Measurement validity and v1.0 approval evidence are published |
| 17 | Expansion | Open | Promote the first non-deployment Subject Assessment Profile | Subject/evidence contracts and support registry | Choose one narrow profile—recommended first candidate: MCP server or repository engineering analysis—and ship direct instruments, executor, limitations, and discovery before starting another |

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
| Done | Show detailed live progress for every run | `qualify`, `benchmark`, resume, `review`, `score`, and standards-assisted `apply` display progress implicitly with completed/total, percentage, current-stage elapsed time, total command elapsed time, throughput, ETA, and the current human-readable work item; run-producing commands additionally persist resumability and failure state in `progress.json`; parallel runs expose the dynamic active task set and effective worker capacity for any `--parallel N`; a one-second interactive heartbeat keeps long in-flight calls visibly alive, bounds output to terminal width, keeps active work deterministically ordered, distinguishes declared/warming-up/observed ETA, and uses accessible semantic color with `NO_COLOR`/plain redirected-output support; `aies runs progress <run-id>` remains an optional second-terminal observer for run-producing commands |
| Done | Make automated Engineering Evaluation self-contained | `qualify --judge`, `benchmark --judge`, `review --model-reviewer`, `score`, and `import` complete or refresh engineering analysis and the report bundle without a human prerequisite; named assessments emit non-blocking Engineering Assessment Results; capabilities default to ECM; guidance defaults to evidence-derived engineering fit; reports and executive summaries say formal qualification `not requested` rather than `blocked`; ECM scenario breadth counts distinct scored task scenarios instead of human-admitted qualification items; human evaluation is an optional visible column; only explicit formal-qualification/grant paths apply ADR-0012 gates |
| Done | Separate ECM breadth from evidence assurance | Reader-facing ECM, report, guidance, snapshot, and executive views no longer call distinct-scenario coverage “confidence.” The compatibility field remains explicitly documented as a breadth alias; structured assurance discloses mapping review, instrument maturity, rater basis, and optional human evaluation; low-breadth tasks cannot receive a strong-fit label |
| Done | Freeze assessment instruments and separate audience projections | Proposed ADR-0019 and `aies-assessment-instrument/v1` freeze task, expected qualities, EV anchors, applicability, failure conditions, calibration, task mappings, standards references, and digest before execution; candidates receive task-only projections; reviewers receive the complete post-response instrument; responses and ratings are digest-bound; exact-suite legacy migration is explicit and incompatible historical evidence is never silently reinterpreted |
| Done | Make automated review criterion-grounded and provenance-blind | Single and batched judges receive the same frozen reviewer projection without subject identity, return response-specific evidence for every EV dimension, copy the instrument digest, identify exact failure conditions, and expose missing/conflicted/unavailable trace protocols without fabricating or silently modifying scores |
| Done | Publish end-to-end standards traceability | Every report bundle emits JSON/Markdown/HTML lineage from AIES-AESQS-ER-01 through competency, frozen scenario, response, rater observation, EV result, and Engineering Task; the artifact is linked by the report, executive summary, run view, and API and remains informational |
| Done | Add isolated standards-assisted execution | `aies apply SUBJECT --scenario ID` compiles a task-scoped AIES context pack; `--compare-baseline --judge REVIEWER` runs unassisted and guided variants and blind-scores both against one frozen instrument; immutable records declare that assisted output and deltas are excluded from qualification, grants, and deployment authority |
| Blocked | Ratify ADR-0019 instrument and assisted-execution governance | Implementation and conformance tests are complete; a named maintainer and applicable Module Editor must review and accept or supersede the Class 3 decision before its Proposed status changes |
| Done | Build the local Human EV Review Workspace | `aies score RUN --interactive` opens a token-protected loopback-only review workspace that shows each scenario, prompt, complete response, EV1 — Correctness through EV6 — Traceability anchors, failure conditions, and structured optional grounding fields; supports autosaved drafts, keyboard navigation, filtering, progress, required low-score findings, named rater/conflict metadata, and JSON export/import fallback; submission passes through the existing score validator, appends immutable rating/evidence records, aggregates, and refreshes reports in one action. It never binds publicly, silently admits an unqualified rater, makes human review mandatory for Engineering Evaluation, or changes Formal Qualification rules |
| Done | Make automated-review diagnostics internally auditable | Future reviewer findings use structured EV attribution with scores derived from the canonical score table; legacy free-text findings remain general rather than fabricated as EV1/0; reports warn on stored finding/score inconsistencies; abstention applicability is explicit and ambiguous legacy false values are disclosed without being counted as proven grounding failures |
| Done | Enforce expiry and requalification | Expired or materially changed qualifications are treated as absent; renewal and targeted re-evaluation are supported |
| Done | Correct endpoint deployment fingerprints | Remote qualifications bind to behaviorally relevant deployment/runtime/config identity, not irrelevant client-machine RAM/CPU changes |
| Done | Govern ECM task decision semantics in an ADR | Accepted ADR-0013 and ECM schema 2 compute one resolved item per distinct task scenario, task-specific RT breadth, 90% uncertainty, risk-tier gates/EV3 hard-fail, reviewed mapping admission, human-rater protocol, parent-area floors, valid `demonstrated` semantics, compatible comparison, and Qualification-Record-bounded Deployment Guidance |

### P1 — Measurement validity

| Status | Work item | Acceptance signal |
|---|---|---|
| Done | Human-review the new RT2 — Moderate tranche | Umair Ali explicitly accepted all 268 listed instruments as repository owner and maintainer after a zero-gap deterministic preflight. One disclosed human-authorized AI-assisted tranche event records every scenario ID and content hash, does not fabricate separate manual click-through reviews, and automatically reopens changed content. All 484 now have effective design review; external independent review and empirical calibration remain open separately. |
| Blocked | Empirically calibrate a preregistered real-subject panel | The executable harness and content-addressed planning contract are complete. Four legacy subjects and a July 2026 Qwen3-Coder RT2 — Moderate coder run provide exploratory observations, but promotion is blocked on a representative real-subject panel, independent human labels, and independent interpretation; uncalibrated automated judging cannot establish measurement validity |
| Done | Define the measurement claim and estimand for every decision product | `aies-measurement-claims/v1` and fixtures state subject, target population, sampling frame, unit, outcome, aggregation, uncertainty, exclusions, intended decision, and prohibited interpretation for Engineering Evaluation, ECM, Fit, comparison, and Formal Qualification; ECM/report bundles cite the contract |
| Open | Separate benchmark, system, and field evidence | Reports identify controlled scenario results, integrated-system behavior, and field/operational observations as different evidence modalities; evidence transfer across levels requires an explicit rationale and never silently raises confidence |
| Open | Validate automated judges against independent human labels | A frozen, stratified anchor set estimates agreement, systematic bias, severity-specific errors, drift, and uncertainty for every judge/protocol version; failed calibration makes scores advisory but does not discard collected responses |
| Blocked | Populate structured failure-condition scoring impacts | The instrument, automated-review, and human-score contracts already accept and enforce explicit affected-EV mappings. Migrating textual corpus conditions to stable condition IDs and populated mappings is blocked on human content review; unmapped legacy conditions retain the disclosed conservative rule that at least one applicable affected EV is zero |
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
| Done | Define a governed Subject Descriptor | New manifests embed `aies-subject-descriptor/v1` independently of the retained deployment/model compatibility envelope; typed composite references, all envisioned descriptor-kind fixtures, in-memory legacy normalization, compatibility diagnostics, and schema-conformance tests ship without rewriting old evidence |
| Done | Separate Subject Executor from Runtime Adapter | `RuntimeGenerationExecutor` explicitly wraps generation adapters while `RepositoryAuditExecutor` provides the first non-runtime path; manifests and Evidence Packages record the executor contract and imported evidence remains generation-independent |
| Done | Define typed canonical evidence events | Observation, rating, reviewer, environment, lifecycle, and attestation families share source-bound identity, modality, classification, correlation, append-only storage, deterministic replay, collision rejection, and an idempotent legacy-run projection exposed by `aies runs events` |
| Done | Define a versioned Evidence Adapter contract | Machine-readable declarations include source/profile versions, modalities, completeness, decision use, scoring semantics, privacy, loss requirements, decision products, and limitations; Inspect and SARIF emit typed events and explicit correlation/loss disclosures with compatibility fixtures. Official upstream API/schema validation remains tracked by their adapter-specific rows, not by this foundation contract |
| Done | Define non-generative instrument projections | `aies-assessment-instrument/v1` supports evidence-adapter observation instruments with immutable identity, reviewer criteria, standard lineage, explicit claim boundaries, no candidate prompt, and compatibility fixtures for repositories, MCP servers, RAG systems, and pipelines; dedicated subject profiles and executors remain tracked in their subject-expansion rows |
| Done | Define the Subject Assessment Profile contract | Accepted ADR-0018, the machine-readable contract, SAP-01, and SAP-02 declare descriptor schema, fingerprint/change triggers, executor and evidence adapters, instruments, score semantics, minimums, gates, limitations, decision products, human-review requirements, and complete applicability rationale |
| Open | Model composite subjects and dependencies | Typed component references already bind subject kind, role, version/fingerprint, and explicit no-transfer/reference-only/mapping-required semantics; coverage inventories component events and prohibits implicit inheritance. A future supported composite requires its own approved profile, governed mappings, executor, interface instruments, and decision products |
| Done | Add subject capability discovery | The versioned `subject-support-v1.yaml` registry drives `aies support`, `/support`, the generated Subject Support Matrix, package data, CI drift checking, and validation tests. It names implemented profiles/executors/entry points/limitations and keeps agents, swarms, MCP, coding assistants, prompts, RAG, pipelines, platforms, people/teams, and composites explicitly planned rather than silently routing them through deployment scoring |
| Done | Add evidence-compatible multi-subject comparison | `aies compare REF REF [REF ...]` accepts 2–5 compatible deployment/model runs or 2–5 repository assessments, never mixes subject families, aligns deployment evidence by stable ET identity, checks subject/risk/profile/mapping/scoring/rater/suite/repeat/adapter compatibility, reports performance beside scenario breadth or perspective-native repository metrics, uses adaptive pair/matrix layouts, sorts by task/confidence/spread/leader where meaningful, supports comparable-only filtering, emits ties/leaders only for like-for-like evidence, writes immutable Markdown/JSON/sortable-HTML bundles, and explicitly saves append-only `/comparisons` records only when requested |
| Done | Unify repository audit decision products | Repository maturity remains semantically distinct from AESQS rubric scoring while sharing the canonical Repository Subject Descriptor, typed evidence provenance, the linked assessment bundle, stored audit inventory, and read-only `/audits` portfolio views |

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
| Done | Govern an Assessment Coverage Matrix | Accepted ADR-0018 and `perspectives-v1.yaml` govern lifecycle, cross-cutting, competency, task, risk, autonomy, stakeholder, environment, evidence-modality, operating-condition, and decision-product perspectives; SAP defaults and overrides require a versioned rationale |
| Done | Make applicability and unknowns explicit | Runtime cells resolve independently across coverage and collection: assessed, partially assessed, not assessed, not applicable, or unsupported plus current, not collected, not requested, unavailable, tool not installed, redacted, failed to collect, stale, or conflicting. Typed collection-gap events explain absence without becoming evidence, and none of these conditions becomes a pass |
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
| Done | Generate coverage and blind-spot reports | Deployment and repository bundles emit Markdown/JSON/HTML perspective coverage, collection conditions, direct-event/instrument/source/modality depth, bounded evidence confidence, profile-declared freshness, conflicts, dependencies, and prioritized gaps. A separate schema-versioned remediation plan retains workflow/owner state, acceptance evidence, monitoring linkage, and reassessment triggers without claiming risk closure |
| Done | Prevent evidence reuse from inflating assurance | Coverage retains canonical event identity, counts unique evidence separately from cell references, exposes every reused identity, correlation group, and shared source digest, inventories component evidence, and prohibits implicit parent inheritance. A future explicit mapping must preserve these rules |

### P1 — Repository engineering intelligence

The existing `aies audit <repo>` is a repository **conformance and practice
maturity** assessment. It verifies evidence such as tests, CI enforcement, ADRs,
security tooling, provenance, and governance controls; it does not claim that
source code is correct or that an architecture is good merely because those
artifacts exist. Deeper repository analysis is a separate evidence layer with
its own instruments and claim boundaries.

| Status | Work item | Acceptance signal |
|---|---|---|
| Done | Govern the repository-analysis layers | Accepted ADR-0016 — Repository Engineering Analysis Layers separates practice maturity, static/retained-artifact analysis, and future controlled repository-task benchmarking, with Umair Ali recorded as repository-owner decider and prohibited-claim boundaries fixed |
| Done | Add a content-addressed Repository Subject Descriptor | Repository identity records commit/tree when available, a bounded working-scope digest, relevant configuration, languages, build system, dependency-state digest, submodule and dirty state, exclusions, environment, and analyzer/tool versions; legacy repository audit fields remain readable |
| Done | Define repository evidence adapters | Declared `aies-repository-conformance/v1` and `aies-repository-analysis/v1` profiles ingest retained JUnit, coverage, SARIF, Ruff/ESLint JSON, CycloneDX/SPDX JSON, manifests, lockfiles, policy/configuration, architecture rules, and bounded source signals without converting tool absence into a pass |
| Done | Add loss-aware SARIF import/export | The bounded AIES SARIF 2.1.0 profile retains tool/rule/version, invocation success, physical artifact locations, fingerprints, severity, baseline state, suppression, fixes, source digest, subject binding, typed events, correlation gaps, and explicit loss; no finding becomes an AIES score or correctness claim |
| Done | Implement evidence-based architecture analysis | The supported Python-aware v1 analyzer emits module topology, cycles, fan-out, repository-declared layer rules/violations, ADR inventory/source references, exact affected artifacts, evidence confidence, and limitations without a quality verdict |
| Done | Implement a code-quality profile | The supported Python-aware v1 profile emits bounded AST complexity/function size, cross-file lexical duplication, large-file, TODO/FIXME, documentation, testability, lint/type configuration, parse coverage, exact artifacts, confidence, and limitations |
| Done | Implement correctness-assurance analysis | The retained-artifact v1 analyzer ingests JUnit and coverage, detects mutation/property/contract-test evidence and explicit failures, separates test presence from execution, and states untested behavior and non-proof boundaries |
| Open | Expand repository evidence and language adapters | Add native type, mutation, duplication, dead-code, dedicated dependency-vulnerability, secret-scan, benchmark, architecture-fitness, and additional-language adapters with versioned source semantics, official schemas where available, adversarial fixtures, and no heuristic-to-pass conversion |
| Open | Add repository trends and richer architecture evidence | Compare compatible content-bound snapshots for architectural drift, cohesion, boundary/fitness-test results, ADR-to-source traceability, quality trends, and configuration/tool changes without inventing causal or quality conclusions |
| Open | Validate interoperability bridges against pinned upstreams | Exercise the Inspect bridge against a pinned native Inspect API and SARIF against the official 2.1.0 schema plus a third-party producer/consumer round trip; publish every unsupported field and fidelity loss |
| Open | Implement controlled repository-task benchmarks | Disposable, authorization-bounded workspaces run versioned defect-fix, refactoring, testing, API, migration, performance, security, and architecture tasks; patch validity, tests, regressions, safety, efficiency, and traceability are scored while the repository and executing agent remain separately identified subjects |
| Done | Emit repository remediation evidence | Every emitted engineering finding and conformance gap feeds a deterministic priority-sorted remediation plan with impact, evidence references, bounded action, acceptance signal, owner/authority boundary, dependencies, reassessment trigger, and exact rerun command |
| Open | Add optional semantic repository review | A declared reviewer may analyze code/design context and propose findings with file/line evidence, uncertainty, reviewer identity, and conflicts; its output is advisory unless independently verified and never changes deterministic maturity or assurance scores by itself |
| Done | Unify repository report and comparison products | One linked Markdown/JSON/HTML bundle and read-only `/audits` API present conformance maturity, architecture, code quality, correctness assurance, security/SARIF, dependencies/SBOM, typed events, coverage, evidence-linked remediation, confidence, and limitations. `aies compare` accepts 2–5 stored audit ids, validates the supported compatibility contract, emits adaptive sortable pair/matrix reports, and can explicitly retain a `/comparisons` record with no composite winner |

### P2 — ECM and decision products

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Ratify AIES-ECM-01 — Engineering Capability Matrix | ECM is formally present in the Charter, Vision, architecture, Roadmap, governance, requirement IDs, and public review disposition |
| Done | Deliver a compact report bundle | Default evaluation bundles contain Engineering Evaluation Report, Engineering Assessment Result when applicable, ECM, Grounding Diagnostics, Engineering Fit Guidance, and Executive Summary; explicit formal runs contain the separate qualification artifacts. All are linked Markdown/JSON/HTML views indexed by `report-bundle.json` |
| Done | Mature Deployment Guidance | Use / Use with Review / Avoid incorporates task evidence, current matching qualification scope, live deployment-fingerprint continuity, role/phases, autonomy, conditions, validity, residual calibration/gate risks, and operational constraints; no guidance creates authority |
| Done | Add protocol-compatible ECM comparison | Default engineering comparison shows compatible observed task scores and the higher observed value without human review or a formal winner claim; explicit formal comparison additionally requires demonstrated status and the human-rater protocol before emitting a winner |
| Done | Build a cross-subject Evidence-Linked Remediation Plan | `aies-evidence-linked-remediation-plan/v1` turns any supported profile's coverage gaps and direct findings into stable priority-sorted actions with impact, evidence, recommendation, acceptance signal, owner/authority workflow state, dependencies, field/telemetry linkage, closure-evidence requirements, and exact reassessment command. Actions begin open and unassigned; narrative remains deterministic and cannot alter evidence, scores, risk acceptance, qualification, or authority |
| Open | Build AIES Select | A declared workload mix plus latency, cost, context, tool reliability, availability, and risk constraints produces an explained fit ranking over compatible evidence—never a global best-subject claim |
| Open | Build organization decision products | Inventory shows approved subjects, demonstrated task fit, qualification scope, conditions, drift, expiry, incidents, and requalification status |
| Open | Export security assessment evidence through OSCAL | A version-pinned optional OSCAL Assessment Results bridge emits scoped subjects, observations, findings, risks, evidence references, timestamps, and remediation links with a mapping/loss report; it never implies external control authorization or certification |
| Done | Rebuild `demo-full` as the AIES killer demo | The fully offline one-process CI narrative demonstrates deployment/repository/standard subjects, implicit live task/ETA progress, complete automated Engineering Evaluation, optional human-evaluation status, ECM strengths/gaps, Engineering Fit Guidance, protocol-compatible comparison without invented winners, conformance, corpus health, empirical-panel handoff, and the linked Executive Summary bundle; it does not stage a failed qualification or grant as the product story, and it avoids repeated inference, report computation, and production-timeout probes |

### P3 — Standards and adoption

| Status | Work item | Acceptance signal |
|---|---|---|
| Open | Reconcile ECM with the five-module architecture | A governed update establishes ECM as a foundational standard and updates dependent documents without weakening vendor neutrality |
| Open | Complete independent pilots | At least one local and one hosted assessment have independent human rating/review, reproducible artifacts, limitations, and published lessons learned |
| Done | Prepare the v0.5 approval inventory and review packets | The generated inventory identifies every governed document targeted for v1.0, its module/editor, normative status, stable requirement IDs, checklist result, two required independent reviewer slots, review-record links, unresolved findings, disposition state, and promotion readiness; external reviewers can use the packet without further inventory implementation |
| Open | Close automated conformance gaps before human review | Metadata, structure, RFC 2119 requirement IDs/titles, glossary/taxonomy use, relative links and document-ID citations, arithmetic, vendor neutrality, and status-transition checks pass for every approval candidate; exceptions are recorded rather than hidden |
| Blocked | Obtain two independent peer reviews for every approval candidate | Each Review document has at least two completed reviews by competent Reviewers who did not substantially author it; reviews are recorded as PR reviews or review issues with reviewer identity, scope, independence/conflict declaration, EV1 — Correctness through EV6 — Traceability findings, and recommendation. The same qualified reviewers may cover multiple documents, but AI review and the author’s own review do not satisfy this gate |
| Open | Resolve and disposition all review findings | Every independent-review and public-comment finding is fixed or explicitly waived with named reasoning; material changes return through the applicable decision class and affected documents are re-reviewed where necessary |
| Open | Run the v0.5 public-comment cycle | Publish a frozen review candidate, announce the comment window, retain every submission, classify and respond to substantiated objections, publish a disposition log, and ensure no unresolved Class 3 objection remains |
| Open | Ratify Review documents as Approved | After the evidence above is complete, Maintainers conduct the required seven-day lazy-consensus decision; the promotion commit links both peer reviews, finding dispositions, public-comment evidence where applicable, decision participants, conflicts/abstentions, and the exact document content hashes |
| Open | Complete module approval gates | AEBOK, AESQS, AEOS, AEAR, and AECT indexes and their governed child documents are Approved only after every document in that module meets the review protocol; ROADMAP phase statuses are updated from evidence rather than by declaration |
| Open | Approve Shared and release-governance foundations | Shared Glossary, Shared Taxonomy, Shared index, Governance, documentation standards, stability/compatibility/conformance policies, and other v1.0 normative foundations complete their applicable review and Class 3 processes before the modules depend on them as Approved contracts |
| Done | Ratify and implement open repository licenses | Accepted ADR-0014 applies CC BY-SA 4.0 to standards/assessment content and Apache 2.0 to executable software. Exact official texts, path notices, package metadata, and CI verification are installed; the recorded private-repository bootstrap limitation requires retrospective public comment during preview |
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
| Done | Consolidate duplicate commands | `deployment`, `profile`, and `qualification` are the documented canonical resources; `registry`, `profiles`, and `qualifications` remain tested compatibility aliases that emit deprecation warnings, and the canonical qualification surface includes every governed lifecycle event |
| Done | Consolidate report view models | CLI overview/API/dashboard consume `aies-workspace-overview`; CLI `runs show` and API `/runs/{id}` consume `aies-run-view`; complete bundles compute `aies-run-report-view` once and share that context across Markdown, HTML, additive `report-view.json`, bundle inventory, safe export, and `GET /runs/{id}/report-view`. Legacy `report.json` and canonical Evidence Package contracts remain unchanged; golden shape, exact stored-endpoint, storage-policy, and single-build tests prevent renderer drift |
| Open | Replace heuristic repository detection with structured evidence where available | CI, dependency, test, coverage, security, architecture, and governance checks prefer parsed manifests or imported tool results over filename/substring heuristics; heuristic fallbacks are labelled with lower evidence confidence and regression fixtures cover supported stacks |
| Open | Standardize assessment vocabulary across commands and docs | `audit` means repository/practice conformance, `analysis` means artifact/tool evidence evaluation, `benchmark` means a compatible controlled comparative study, and `qualification` means a governed human decision; help and reports do not use the terms interchangeably |
| Done | Generate and test the subject-support matrix | One versioned machine-readable registry drives CLI help, API discovery, generated documentation, installed package data, CI drift detection, and tests for implemented/experimental/planned subject profiles so public claims cannot drift ahead of executable support |
| Done | Generate and test the perspective-coverage registry | `perspectives-v1.yaml` drives SAP applicability, runtime coverage, code-title labels, generated `ASSESSMENT_PROFILES.md`, validation, CLI/API discovery, and regression tests across every declared category |
| Done | Clarify immutable artifacts and regenerable views | Storage policy classifies append-only records, derived canonical snapshots, mutable workflow state/configuration, and regenerable views; `workspace.write_json` rejects append-only replacement and `workspace.write_view` cannot target evidence paths |
| Done | Make record identifiers concurrency-safe | Qualification Records atomically claim human-readable IDs through exclusive creation; a 12-decision concurrent regression proves unique issued records and lifecycle events |
| Done | Improve local verification feedback | The documented command reports ranked durations and uses a 180-second warm-cache Windows budget with a 25% regression trigger. Single-pass report views plus signature-invalidated isolated YAML, expanded-scenario, review-ledger, and suite caches retain complete coverage; cache mutation/invalidation behavior has regression coverage, read-only API fixtures are shared safely, and concurrency tests delay only the phase under test. Current 2026-07-27 Windows observations are retained below rather than selecting only the fastest result. |
| Open | Recover reproducible full-suite performance headroom | Consecutive 2026-07-27 warm-cache Windows observations varied from 126.28 seconds for 372 tests to 143.09 seconds for 373 tests. Both pass the 180-second ceiling, but the latest has 20.5% rather than the target 25% headroom. Profile host/filesystem/antivirus variance and repeated corpus/report work until the target is reproducible; do not reduce scenario, schema, concurrency, or end-to-end coverage to make the number pass. |
| Done | Keep package-build artifacts out of review | Root ignore policy excludes `build/`, `dist/`, and demo workspaces; release-hygiene validation passes after local wheel/sdist builds |
| Done | Generate exhaustive CLI guidance and shell completion | A parser-derived CLI reference covers every command, subcommand, positional parameter, option, default, choice, prerequisite, interaction, result/side effect, recommended next step, and workflow sequence; CI detects undocumented parser drift, and PowerShell/Bash/Zsh Tab completion is generated from the same live command surface |
| Done | Remove local workspace archive debris safely | `aies doctor` inventories `.DS_Store`, `Thumbs.db`, `desktop.ini`, `__MACOSX`, Python/pytest caches, and misplaced regenerable views under the runs root; JSON exposes every path and category, readiness is unaffected, and tests prove the diagnostic deletes neither debris nor evidence |
| Done | Make cross-machine run transfer first-class | Accepted ADR-0017 governs `aies runs import <directory-or-zip> [--dry-run]`: exactly one manifest is admitted; archive size, traversal, drive paths, symlinks, case collisions, and disposable metadata are controlled; every admitted file is byte/digest verified; exact re-import is idempotent; conflicts never overwrite; nested `RUN/RUN` copies are normalized while their wrapper is retained under append-only `import-sources`; append-only receipts are listed by CLI/API. Import itself preserves all admitted bytes and never rescores or re-decides; only existing renderer-owned commands may later regenerate presentation views |
| Done | Discover protocol-compatible run cohorts | `aies runs cohorts` and read-only `/run-cohorts` group aggregated deployment runs by the exact ECM subject/risk/profile/suite/mapping/scoring/rater/repeat/adapter signature, disclose exclusions and claim boundaries, and emit connected 2–5-run comparison batches for larger compatible groups |

### C2 — CI, security, and release hygiene

| Status | Cleanup item | Acceptance signal |
|---|---|---|
| Done | Expand CI path coverage | Changes to Shared, AEBOK, AESQS, AEOS, AEAR, AECT, ECM, ADRs, governed docs, platform, and conformance trigger relevant checks |
| Done | Test supported Python versions | CI runs the complete platform gate on Python 3.10, 3.11, 3.12, 3.13, and 3.14; installation docs identify that tested range |
| Open | Add documentation governance checks | CI detects duplicate document/requirement IDs, missing meaningful titles, broken links, invalid metadata/status transitions, and stale references |
| Open | Add code-quality checks | Formatting, linting, type checking, and coverage thresholds run in CI |
| In progress | Add supply-chain controls | Dependabot, immutable action pins, full-history Gitleaks, Ruff security analysis, pip-audit, retained scanner evidence, and the public-release readiness inventory are implemented. Remaining work locks dependencies; scans release containers; emits SPDX 3 Software/AI/Dataset/Build profiles where applicable; generates SLSA provenance for packages, containers, and conformance bundles; signs or attests release artifacts with Sigstore/Cosign or an equivalently verifiable mechanism; CI verifies identity, digest, source revision, builder, and provenance before publication and states that provenance does not prove safety or correctness |
| Open | Publish a real security contact | Dedicated email and optional encryption key replace the placeholder fallback; private vulnerability reporting remains preferred |
| In progress | Add ownership and protected-branch evidence | CODEOWNERS now routes default and high-impact paths to the Maintainer. GitHub-protected-branch settings, required CODEOWNER/human review, restricted bypasses, and retained external evidence still need repository-administrator completion |
| Open | Align versions | Package version, standards milestone, artifact versions, changelog, tags, and release names answer different versioning questions explicitly and consistently |
| Done | Establish the public-release readiness gate | The versioned text/JSON preflight, `--gate` failure behavior, Make target, tests, and retained CI artifact are implemented. Licensing now passes; readiness remains false until the security contact, external settings, history/log review, distribution trust, and signed release evidence are complete |
| Done | Correct current CI identity wording | Workflow and active docs say Engineering Assessment Platform rather than Qualification Platform |

## 5. Current Verified Baseline

Last verified on 2026-07-27:

- `pytest platform/tests -q`: **373 passed, 1 skipped in 143.09 seconds** on the
  latest Windows run, **36.91 seconds / 20.5% below** the documented
  180-second budget. An immediately preceding 372-test run completed in
  126.28 seconds; reproducible 25% headroom remains open.
- `aies suites validate`: **484 scenarios, 12 areas, 0 warnings, 0 errors**;
  **268 effective hash-bound ledger acceptances, 0 stale, 0 unknown**.
- Decision-engine conformance: **8/8 cases passed**, semantics 1.0.
- Release hygiene: **PASS**.
- Local distribution verification: wheel and sdist build; isolated wheel
  install runs suite validation and the offline demo; isolated sdist install,
  validation, and uninstall pass on Windows. Cross-platform package/demo CI is
  now defined and awaits hosted-run evidence.
- Repository audit at RT2 — Moderate: **PASS**, with **21 verified controls and
  5 gaps**. CODEOWNERS and dependency-update automation are now detected;
  protected-branch enforcement remains correctly external.
- Public-release readiness: **NOT READY**, with 5 tracked-tree blockers and 5
  externally verified controls still open. Local security automation now
  passes; CodeQL default setup, Private Vulnerability Reporting, protected-main
  settings, historical Actions review, and signed-release evidence require
  named external confirmation. Text/JSON rendering, schema-valid
  named external confirmations, fail-closed gate behavior, Python 3.10
  compatibility, workflow YAML, and actionlint validation pass.
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

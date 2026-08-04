# AI Engineering Standards (AIES)

> **Evidence-backed Engineering Evaluation as Code. See what an AI engineering
> system can actually do, how much evidence supports it, and where the unknowns
> remain.**

[![Platform CI](https://github.com/umairali7/ai-engineering-standards/actions/workflows/platform-ci.yml/badge.svg)](https://github.com/umairali7/ai-engineering-standards/actions/workflows/platform-ci.yml)
[![Security evidence](https://github.com/umairali7/ai-engineering-standards/actions/workflows/security.yml/badge.svg)](https://github.com/umairali7/ai-engineering-standards/actions/workflows/security.yml)
![Status](https://img.shields.io/badge/Status-Public%20Development%20Preview-0969da)
![License](https://img.shields.io/badge/License-CC%20BY--SA%204.0%20%7C%20Apache%202.0-2ea44f)
![Python](https://img.shields.io/badge/Python-3.10--3.14-3776ab)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

![AIES — Evidence to capability to engineering decisions](docs/assets/aies-social-preview.png)

**A leaderboard can tell you who won its benchmark. It cannot tell you whether
a model should design your API, refactor a payment path, review a security
boundary, or operate inside your repository.**

AIES turns versioned engineering scenarios and repository evidence into a
traceable **Engineering Capability Matrix (ECM)**: demonstrated strengths,
weaker areas, evidence breadth, assurance gaps, and tasks that were not
assessed. No mystery aggregate. No invented confidence. No universal “best
model” claim.

**[Try it offline](#try-the-complete-product-offline)** ·
**[Connect a deployment](#connect-a-real-deployment)** ·
**[Choose a workflow](#choose-your-first-workflow)** ·
**[See the difference](#why-this-is-different)** ·
**[Read the standards](GETTING_STARTED.md)** ·
**[Help build it](CONTRIBUTING.md)**

## What you get

| Evidence product | The decision it helps you make |
|---|---|
| **Engineering Capability Matrix** | What did this subject demonstrate across architecture, APIs, code, testing, security, performance, operations, and other engineering tasks? |
| **Engineering Fit Guidance** | Where is the subject a reasonable fit, where should review be used, and where is the evidence insufficient? |
| **Compatible comparison** | Which differences between 2–5 runs are supported by equivalent evidence—and which comparisons would be misleading? |
| **Repository assessment** | What does the repository demonstrate about architecture, correctness assurance, quality, testing, security, dependencies, operations, governance, and improvement? |
| **Coverage and remediation** | Which evidence is missing, conflicted, stale, or shallow, and what verifiable action would close the gap? |
| **Optional formal qualification** | Does a separately invoked, human-governed process satisfy a defined risk-scoped protocol? |

## Try the complete product offline

No model server. No API key. No Make. No Bash. The demo executes the real
collection, scoring, analysis, ECM, Engineering Fit, and linked HTML-report
pipeline with deterministic local fixtures.

**Windows PowerShell**

```powershell
git clone https://github.com/umairali7/ai-engineering-standards.git
cd ai-engineering-standards\platform
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aies demo --open
```

**macOS or Linux**

```bash
git clone https://github.com/umairali7/ai-engineering-standards.git
cd ai-engineering-standards/platform
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
aies demo --open
```

Prefer an isolated tool install? From the repository root, use
`pipx install ./platform` or `uv tool install ./platform`, then run
`aies demo --open`.

Expected terminal snapshot:

```text
AIES  EVIDENCE → CAPABILITY → ASSURANCE → ENGINEERING DECISIONS

TASK                         EVIDENCE  OBSERVED CAPABILITY  SCENARIO BREADTH
ET-02 — Architecture Design  2/20      █████████░ 85%       █░░░░░░░░░ 10%
ET-04 — Code Generation      2/20      █████████░ 92%       █░░░░░░░░░ 10%
ET-07 — Testing              2/20      █████████░ 90%       █░░░░░░░░░ 10%

Coverage: assessed tasks are observed; unassessed tasks remain unknown, not zero.
```

The demo takes the shortest path through the product. It does not claim that
eight fixtures qualify a model. It shows exactly how AIES preserves the
difference between observed performance, direct scenario breadth, reviewer
assurance, and optional human evaluation.

## Connect a real deployment

AIES evaluates a **deployment**, not a model name: the model, runtime,
configuration, quantization, endpoint, and observed environment together define
the subject. Register the candidate and, preferably, a different reviewer
before running an evaluation.

First ask AIES to discover reachable supported local runtimes:

```bash
aies doctor
aies discover
aies deployment list
aies deployment inspect DEPLOYMENT_ID
```

If discovery does not find your OpenAI-compatible endpoint, generate a valid
manifest without placing a credential in it:

```bash
aies init aies-workspace --starter deployment --deployment-id local-coder --model served-model-id --endpoint http://127.0.0.1:1234/v1 --api-key-env AIES_OPENAI_API_KEY --role subject
```

The command writes `aies-workspace/deployment.example.yaml` and prints the
exact workspace and `aies deployment add` commands for PowerShell or your POSIX
shell. It records only the environment-variable name, never the key. Use
`aies init --guided` for an interactive setup.

Alternatively, adapt one of the checked
[local and hosted examples](platform/examples/deployments/README.md), verify
its model ID, endpoint, context window, role, and provenance, then register and
plan it:

```bash
aies deployment add examples/deployments/local-qwen3-coder-next-8b.yaml
aies deployment inspect local-qwen3-coder-next-8bit
aies evaluate local-qwen3-coder-next-8bit --judge REVIEWER_ID --plan-only --parallel 4
```

Once the subject and reviewer are reachable, the short real run is:

```bash
aies evaluate SUBJECT_ID --judge REVIEWER_ID --parallel 4 --open
```

That intentionally defaults to the bounded `coder` assessment at RT1 —
Minimal, with no repeated scenarios. Inspect the plan first, then expand scope
only when the engineering decision needs it. The equally short repository path
is:

```bash
aies audit . --out aies-repository-report
```

Run these example paths from `platform/`. A role tag is advisory: it organizes
subjects and reviewers, but it does not prove that a reviewer is calibrated or
trustworthy. The complete manifest reference and lifecycle commands are in
[AIES-PLAT-03 — Deployments](platform/DEPLOYMENTS.md).

## Choose your first workflow

| I want to… | Start here | What I receive |
|---|---|---|
| **See the idea** | `aies demo --open` | A complete local report bundle and interactive HTML summary |
| **Evaluate an AI deployment** | `aies evaluate DEPLOYMENT --judge REVIEWER` | Evidence, ECM, fit guidance, diagnostics, coverage, and reports |
| **Audit a repository** | `aies audit . --out aies-repository-report` | Architecture, quality, correctness-assurance, testing, security, dependency, governance, and remediation views |
| **Continuously assess a repository in CI** | `aies ci audit . --rt 2 --out aies-ci` | Retained JSON/Markdown evidence and annotations, advisory by default |
| **Compare runs** | `aies compare RUN_A RUN_B --sort spread --out comparison` | Compatibility-gated Markdown, JSON, and sortable HTML comparison |
| **Inspect before spending time** | `aies evaluate DEPLOYMENT --plan-only` | Exact scope, candidate/judge call plan, limitations, and execution path |
| **Contribute** | Read [CONTRIBUTING.md](CONTRIBUTING.md) | Bounded work on an instrument, adapter, standard, report, test, or explanation |

## Why this is different

| Common evaluation shortcut | AIES behavior |
|---|---|
| One aggregate score | Task-level capability, breadth, assurance, and limitations remain separate |
| Repeating one prompt to inflate sample size | Distinct scenarios measure breadth; repeats are identified as stability evidence |
| Candidate sees the answer rubric | Candidate receives only the task; reviewers receive the frozen instrument after evidence exists |
| Undocumented model-as-judge | Reviewer identity, protocol, evidence, rubric, and calibration status remain visible |
| Unassessed becomes zero | Unassessed remains **unknown** |
| Compare everything and name a winner | Compare only evidence-compatible runs; expose incompatibility instead of inventing a winner |
| Generated code is the whole story | Assess the subject **and** audit the engineering repository that accepts its work |
| Automated score silently becomes authority | Engineering evaluation is informational; formal qualification and consequential decisions are explicit and human-governed |

### Where AIES fits in the evaluation ecosystem

Strong evaluation tools already exist. [Inspect AI](https://inspect.aisi.org.uk/)
provides composable tasks, solvers, scorers, sandboxes, and agent evaluation;
[SWE-bench](https://www.swebench.com/SWE-bench/) tests systems against
real-world repository issues; static-analysis and security tools emit findings
through formats such as SARIF. AIES does not need to replace those systems to
be useful.

Its core responsibility is the layer between **evidence production** and an
**engineering decision**:

| Layer | Responsibility |
|---|---|
| **Evidence producers** | AIES frozen instruments, external evaluation frameworks and benchmarks, repository analyzers, structured tool findings, and attributed human review observe behavior or repository state |
| **AIES evidence-to-decision layer** | Preserve subject and source identity, admit evidence through versioned contracts, disclose conversion loss, check comparison compatibility, map evidence to engineering tasks, and produce ECM, assurance, fit, coverage, and remediation views |
| **Human and organizational authority** | Decide deployment policy, risk acceptance, qualification, and operating permissions using the evidence and the organization’s own accountability process |

This turns ecosystem breadth into a strength: teams can keep specialized tools
that already work while using AIES to make their compatible evidence
traceable, comparable, and actionable. The current boundary remains explicit:
AIES ships executable assessment paths for AI deployments and repositories.
Its AIES-profiled Inspect JSON and SARIF bridges are experimental, and it does
not yet claim a native adapter for every framework or benchmark. Imported
findings retain their original meaning and are never silently promoted into
correctness, maturity, or qualification claims.

### Put engineering evidence in the pipeline

The same repository assessment can run in GitHub Actions, GitLab CI, Azure
Pipelines, Jenkins, or another runner that can invoke the CLI:

```bash
aies ci audit . --rt 2 --out aies-ci
```

It writes machine-readable JSON, a human-readable report, and portable
annotations without making missing evidence an implicit merge blocker. Start
advisory, review results from representative changes, then enable enforcement
only through an approved policy. GitHub users can call the pinned reusable
[`aies-advisory.yml`](.github/workflows/aies-advisory.yml); the complete,
reproducible setup and opt-in `enforce: true` example are in the
[CI integration guide](platform/CI_INTEGRATION.md).

## One repository, two reinforcing layers

| Open standard | Open-source platform |
|---|---|
| Defines the vocabulary, practices, evidence requirements, evaluation dimensions, task taxonomy, governance, and operating boundaries | Compiles those definitions into frozen instruments, collects and scores evidence, traces every result, and renders decision products |
| **CC BY-SA 4.0** — adaptations remain attributable and open | **Apache 2.0** — conventional software terms with an explicit patent grant |

The standard says what trustworthy AI engineering should look like. The
platform makes those expectations executable. Real assessments then reveal
weak instruments, missing evidence, and standards gaps, creating a feedback
loop between the written standard and the software that exercises it.

## See it work in 60 seconds

![AIES deployment discovery, built-in help, CLI evaluation, Engineering Capability Matrix, repository audit, comparison, and linked report walkthrough](docs/assets/aies-workflow-demo.gif)

The walkthrough uses a retained 147-scenario Qwen3-Coder-Next assessment and a
fresh AIES repository self-audit. The scores are informational because the
automated reviewer was advisory; human evaluation was optional and not
completed, and no formal qualification is claimed. The animation contains no
raw prompts, responses, endpoints, machine identifiers, or environment
fingerprints.

## Why AIES Had to Exist

Every few days, another open-weight model arrives with a new chart, a new
aggregate, and a new claim of state-of-the-art performance. But the moment an
engineer has to choose one for real work, the leaderboard stops being enough.

Which model is actually better at architecture? Which one can refactor without
quietly changing behavior? Which one catches security boundaries, designs a
sound API, writes meaningful tests, handles migrations, or recognizes when it
should stop and ask for help? A single coding score cannot answer those
questions. Neither can a handful of impressive prompts.

The honest answer was uncomfortable: **we were selecting engineering systems
without enough evidence to explain the selection.**

AIES began as an attempt to make that decision defensible. Instead of asking
whether a model is “good,” it asks what the subject demonstrably did, on which
engineering tasks, under which conditions, with how much evidence, and with
which limitations. That required more than another benchmark:

1. **The work had to represent the SDLC.** Assessment expanded across twelve
   engineering competency areas and fifteen stable Engineering Tasks—not only
   code generation.
2. **Breadth had to be real.** Repeating one prompt measures stability, not
   capability breadth. The corpus grew to 484 distinct instruments. Every
   competency area now has at least 30 distinct RT2 — Moderate instruments;
   CA-05 — AI-Assisted Implementation has 57. They model constrained,
   real-world engineering decisions with explicit failure modes and observable
   anchors.
3. **Every score needed a reviewer and a reason.** Human review is valuable but
   difficult to scale. Independent evaluator models can provide practical
   criterion-grounded review, but they must not become invisible authorities.
   AIES freezes the rubric before execution, withholds it from the candidate,
   records judge identity and protocol, requires evidence for each EV score,
   and keeps optional human evaluation visible. Formal qualification remains a
   separate human-governed decision.
4. **Generated code was only half the problem.** A strong answer does not prove
   that the repository accepting it is engineered responsibly. `aies audit`
   examines architecture evidence, code quality, correctness assurance, tests
   and coverage, security and privacy controls, dependencies and SBOMs,
   AI-change provenance, risk classification, human gates, versioned context,
   observability, release controls, and remediation evidence. Missing evidence
   remains a gap; it is never converted into a pass.
5. **The method had to outlive model churn.** The same evidence architecture can
   support repositories today and dedicated assessment profiles for agents,
   MCP servers, RAG systems, AI pipelines, coding assistants, platforms,
   services, and composite systems tomorrow—without pretending they all answer
   the same prompts or share the same scoring semantics.

That is why AIES is **Evidence-Backed Engineering Evaluation as Code**. It is
not a universal leaderboard and it does not ask anyone to trust an unexplained
number. It turns engineering expectations into versioned instruments, observed
behavior into durable evidence, and evidence into capability, fit, comparison,
and improvement decisions whose reasoning can be inspected.

AI capability is moving too quickly for engineering trust to remain anecdotal.
AIES exists to make that trust testable.

**Start here:** [60-second offline trial](QUICKSTART.md) ·
[choose a path by role](GETTING_STARTED.md) ·
[see every CLI command](platform/CLI_REFERENCE.md) ·
[review the public roadmap](ROADMAP.md) ·
[understand versions and releases](docs/VERSIONING_AND_RELEASES.md) ·
[see the adoption and launch plan](docs/ADOPTION_AND_LAUNCH_PLAN.md) ·
[adopt it in CI](platform/CI_INTEGRATION.md) ·
[run it in a container](platform/CONTAINER.md) ·
[help build it](CONTRIBUTING.md) ·
[share first-run or report feedback](https://github.com/umairali7/ai-engineering-standards/issues/new/choose)

### Command and artifact map

<details>
<summary><strong>Explore the complete command and artifact map</strong></summary>

The first-workflow table above is enough to begin. This reference expands the
rest of the implemented CLI surface and the artifact produced by each path.

| You want to… | Start with | You receive |
|---|---|---|
| See the idea without setup | `aies demo --open` | Executive Summary, ECM, fit guidance, diagnostics, and full report |
| Understand one registered AI deployment | `aies evaluate DEPLOYMENT --plan-only` | Non-executing call plan, declared cost/ETA or exact unknowns, limitations, resumability, and execution path |
| Evaluate it automatically | `aies evaluate DEPLOYMENT --judge JUDGE` | Completed non-blocking Engineering Evaluation and report bundle |
| Add optional human evidence without editing JSON | `aies score RUN --interactive` | Token-protected local EV workspace, autosaved draft, immutable rating records, and refreshed reports; no grant authority |
| Apply AIES to one engineering task | `aies apply DEPLOYMENT --scenario SC-CA05-001 --compare-baseline --judge JUDGE` | Standards-assisted output plus an isolated baseline-versus-guided EV comparison; never qualification evidence |
| See the decision snapshot in your terminal | `aies snapshot latest` | Task evidence, observed capability, scenario breadth, assurance gaps, and engineering interpretation |
| Check what AIES truly supports | `aies support` | Implemented, experimental, and planned subject kinds with executable entry points and limitations |
| Identify exactly what is installed | `aies version` | Separate standards, platform, and artifact-contract versions without implying approval or compatibility |
| See how each subject is assessed | `aies assessment-profile list` | Approved Subject Assessment Profiles, executors, evidence adapters, applicability, decision products, and limitations |
| See what evidence is missing and what to do next | `aies coverage RUN --write` | Coverage, evidence integrity, prioritized blind spots, and an unassigned evidence-linked remediation/monitoring plan with acceptance signals and reassessment commands; audits additionally use `--out NEW_DIR` |
| Track an evidence-gap action | `aies remediation show RUN_OR_AUDIT` | Stable ACT identifiers, owner/workflow state, closure evidence requirements, monitoring links, and append-only human dispositions |
| Choose a first workflow by decision | `aies starter list` | Prerequisites, commands, artifacts, time/cost class, evidence breadth, limitations, and next expansion |
| Assess a repository from multiple engineering perspectives | `aies audit . --out aies-repository-report` | Separate practice maturity, architecture, code-quality, correctness-assurance, security, dependency, confidence, limitation, and evidence-linked remediation views |
| Add advisory repository evidence to CI | `aies ci audit . --rt 2` | Retained JSON/Markdown evidence and annotations without an implicit merge gate |
| Run without a host Python install | `docker build -f platform/Dockerfile -t aies:local .` | Non-root container for demo, audit, conformance, and networked evaluations |
| Bring a run from another machine | `aies runs import RUN.zip --dry-run` | Traversal-safe validation, byte/digest verification, non-overwriting import, and an append-only receipt |
| Compare 2–5 compatible deployment runs or repository snapshots | `aies compare REF_A REF_B [REF_C ...] --sort spread --out comparison` | Adaptive pair/matrix evidence in Markdown, JSON, and sortable HTML without a fake universal winner |
| Integrate an evaluation tool | `aies bridge inspect-import …` | Source-bound imported ratings and an explicit loss report |
| Integrate static analysis | `aies bridge sarif-import …` | Preserved SARIF findings that remain distinct from correctness claims |
| Apply formal governance | `--formal-qualification` | A separate human-governed qualification path |

</details>

Repository paths are exact scopes. If `aies audit .` is run from a
subdirectory of a Git repository, AIES identifies the enclosing Git root,
warns that root-level evidence was excluded, and prints the exact whole-repo
command. Evaluation reports likewise distinguish `--profile enterprise`
(score weighting only) from `--assessment enterprise` (the governed
assessment composition).

Current implemented subjects are AI deployments and repositories. The
subject-neutral contracts for agents, MCP servers, RAG systems, pipelines, and
platforms are experimental until their dedicated executors and instruments are
implemented and validated. The generated
[Subject Support Matrix](platform/SUBJECT_SUPPORT.md) and `aies support` command
are the canonical public support boundary.

The generated [Subject Assessment Profile reference](platform/ASSESSMENT_PROFILES.md)
defines the assessment semantics behind that boundary. Every complete
deployment report and repository assessment bundle now includes an
**Assessment Coverage and Blind-Spot Report**. Coverage is evidence
availability—not a score, pass, capability, qualification, or authorization.
It separately exposes collection failures, missing tools, redaction,
staleness, conflicts, evidence depth and correlation, and component evidence
that is prohibited from silently inflating the parent subject. Each written
coverage product also emits an **Evidence-Linked Remediation & Monitoring
Plan**. Its actions start open and unassigned; a named owner must separately
accept, defer, or close them.

## From Evidence to Engineering Decisions

AIES turns its standards into two deliberately separate workflows. Unassisted
assessment freezes a versioned instrument, sends only the task to the subject,
and exposes the complete rubric to the reviewer only after evidence exists.
`aies apply` instead provides task-scoped standards assistance; its guided
output can be analyzed but never enters qualification evidence. Repository
audits use deterministic repository controls and evidence profiles rather than
pretending that source code answered a model prompt.

From there, AIES separates evidence from the different decisions people need
to make from it. The reusable source is
[AIES Assessment and Assistance Flow](diagrams/aies-assessment-and-assistance-flow.mmd).

```text
AIES standards + assessment scope + subject descriptor
                         │
                         ▼
              Frozen assessment instrument
               ┌─────────┴─────────┐
               ▼                   ▼
 task-only candidate path   complete reviewer path
               │            (after evidence exists)
               └─────────┬─────────┘
                         ▼
       Canonical evidence + Standards Traceability
                         │
                         ▼
     Competency analysis → Engineering Capability Matrix
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
 Engineering Fit   Compatible Compare   Optional Formal
 (informational)    (informational)      Qualification

Separate path: aies apply → standards-assisted output
               (never qualification evidence)
```

The baseline candidate never receives expected answers, scoring anchors,
failure boundaries, or calibration material. Reviewers receive the complete
frozen instrument only after evidence exists, and every response and rating is
bound to its digest. The separate `aies apply` path uses task-scoped standards
to assist engineering work and can measure a paired baseline delta without
contaminating assessment evidence.

The outputs serve different audiences and must not be collapsed into one
opaque score:

| Decision product | Primary audience | What it answers | Human evaluation required? |
|---|---|---|---|
| **Engineering Evaluation** | Engineers and evaluators | What was observed, under which conditions, and with what evidence? | No; automated scores are sufficient for the engineering result |
| **Engineering Capability Matrix (ECM)** | Engineers and technical leaders | Which engineering tasks are demonstrated strengths, weaker areas, or evidence gaps? | No; human evaluation is an optional, visible corroboration |
| **Engineering Fit Guidance** | Engineering managers and platform teams | Where is this subject a good fit, where should review be used, and where is evidence insufficient? | No; informational only and never deployment authority |
| **Evidence-Linked Remediation & Monitoring Plan** | Subject owners, engineers, and operators | Which gaps or findings require action, what evidence would close them, and what should trigger reassessment? | No; generated actions start open and unassigned |
| **Formal Qualification** | Auditors and qualification authorities | Does the evidence satisfy a governed, risk-scoped qualification protocol? | Yes; explicitly requested with `--formal-qualification` |
| **Qualification Record** | Governance and accountable leadership | What consequential qualification decision did a named human authority record? | Yes |

Routine assessment, benchmarking, analysis, comparison, and reporting are
therefore **non-blocking**: missing human review is reported as `not performed`,
not treated as a failure. Human accountability remains mandatory for
consequential grants, releases, deployments, and other governed decisions.

### Engineering Capability Matrix

The ECM is the engineer-facing core artifact defined around a stable,
subject-neutral Engineering Task Taxonomy:

| ID | Engineering task | ID | Engineering task | ID | Engineering task |
|---|---|---|---|---|---|
| ET-01 | Requirements Analysis | ET-06 | Debugging | ET-11 | Database Design |
| ET-02 | Architecture Design | ET-07 | Testing | ET-12 | Migration |
| ET-03 | API Design | ET-08 | Documentation | ET-13 | Infrastructure |
| ET-04 | Code Generation | ET-09 | Performance Optimization | ET-14 | Observability |
| ET-05 | Refactoring | ET-10 | Security Review | ET-15 | Production Operations |

For every applicable task, the ECM reports observed performance separately
from scenario breadth, reviewer assurance, mapping review, instrument maturity,
optional human evaluation, coverage, and provenance. `Not
assessed` means **no supported claim can be made**; it is not a zero-capability
rating. This makes the ECM useful for evidence-compatible subject comparison
and workload selection without turning AIES into a context-free leaderboard.

---

## The Five Modules

| Module | Full Name | Question It Answers | Docs |
|--------|-----------|---------------------|------|
| **AEBOK** | AI Engineering Body of Knowledge | *What should AI Engineering know?* | [AEBOK/](AEBOK/README.md) |
| **AESQS** | AI Engineering SDLC Qualification Standard | *How do we objectively evaluate AI Engineering capability?* | [AESQS/](AESQS/README.md) |
| **AEOS** | AI Engineering Operating System | *How should AI Engineering teams operate?* | [AEOS/](AEOS/README.md) |
| **AEAR** | AI Engineering Architecture Reference | *What should enterprise AI platforms look like?* | [AEAR/](AEAR/README.md) |
| **AECT** | AI Engineering Certification & Training | *How do engineers learn and become certified?* | [AECT/](AECT/README.md) |

All modules build on the [Shared Standards](Shared/README.md) — the canonical [Glossary](Shared/Glossary/README.md), [Taxonomy](Shared/Taxonomy/README.md), and documentation conventions that keep terminology consistent across the entire standard.

```
AI Engineering Standards (AIES)
│
├── Shared Standards ────── vocabulary, taxonomies, conventions (used by all)
│
├── AEBOK ──── knowledge:      disciplines, practices, patterns, SDLC guidance
├── AESQS ──── qualification:  competency model, rubrics, capability scoring
├── AEOS ───── operations:     agent roles, workflows, human oversight, governance
├── AEAR ───── architecture:   reference architectures and industry blueprints
└── AECT ───── certification:  learning paths, labs, exams, credentials
```

## Guiding Principles

1. **Vendor Neutral** — Standards define engineering capabilities, not vendors. Models evolve continuously; engineering standards remain stable.
2. **Engineering First** — Engineering disciplines take precedence over prompt techniques and model-specific optimizations.
3. **Enterprise Ready** — Every recommendation is designed for production environments: governance, security, compliance, auditability, traceability, scalability, reliability, operations.
4. **Human Governed** — AI augments engineers. Humans remain accountable for engineering decisions.
5. **Evidence Driven** — Recommendations are supported by measurable outcomes, repeatable evaluation, and documented trade-offs.
6. **Open & Extensible** — The standards evolve with the AI ecosystem while preserving compatibility through controlled versioning and governance.

## Complete SDLC Coverage

Unlike existing AI frameworks, AIES covers the complete software engineering lifecycle — sixteen phases from Business Strategy through Continuous Improvement — plus fifteen cross-cutting domains (security, privacy, compliance, governance, risk, AI safety, human oversight, and more) that span every phase.

The canonical phase and domain definitions live in [docs/SDLC.md](docs/SDLC.md) and the [Shared Taxonomy](Shared/Taxonomy/README.md).

## Intended Audience

Enterprise engineering organizations, CTOs, engineering directors and managers, enterprise/AI/software architects, platform engineering teams, AI product teams, security teams, QA organizations, researchers, universities, and open source communities.

---

## Navigate the project

Start with [GETTING_STARTED.md](GETTING_STARTED.md) for a role-based reading
path, [QUICKSTART.md](QUICKSTART.md) for the first run, or the
[platform guide](platform/GUIDE.md) for an end-to-end real evaluation. The
documentation becomes progressively more specific: README → charter →
standards → specifications → reference implementations and examples →
certification material.

<details>
<summary><strong>Repository map</strong></summary>

```text
.
├── Shared/                 canonical glossary and taxonomy (normative)
├── AEBOK/                  Body of Knowledge
├── AESQS/                  Qualification Standard
├── AEOS/                   Operating System
├── AEAR/                   Architecture Reference
├── AECT/                   Certification & Training
├── platform/               executable Engineering Assessment Platform
├── conformance/            golden evidence packages and conformance runner
├── docs/                   vision, charter, architecture, SDLC, FAQ, standards
├── adr/                    Architecture Decision Records
├── templates/              governed document and evidence templates
├── examples/               worked examples
├── diagrams/               reusable diagram sources
└── research/               supporting research and calibration plans
```

Project controls are at the root:
[ROADMAP.md](ROADMAP.md), [GOVERNANCE.md](GOVERNANCE.md),
[CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md),
[CHANGELOG.md](CHANGELOG.md), and [LICENSE.md](LICENSE.md).

</details>

## Governance

The project follows an engineering governance model described in [GOVERNANCE.md](GOVERNANCE.md):

- Architecture Decision Records ([adr/](adr/README.md))
- Peer review and engineering review
- Public discussion
- Versioned releases

No individual contributor owns the standards. Engineering consensus drives evolution.

**Artifact-contract stability (independent of the project release).** The
interfaces listed in [STABILITY.md](STABILITY.md) are frozen at their own
contract versions so integrators have a dependable boundary:

- [STABILITY.md](STABILITY.md) — the historical **v1.0 Architecture Freeze**:
  contract-specific versions, the **normative vs reference** distinction, and
  **reference implementation vs conformance suite**.
- [COMPATIBILITY.md](COMPATIBILITY.md) — how contracts evolve (additive-only,
  ADR-for-breaking, deprecation window) — **enforced by CI**, not just prose.
- [CONFORMANCE-POLICY.md](CONFORMANCE-POLICY.md) — what "AIES Conformant" means,
  verified by a data-first conformance suite over a golden Evidence Package corpus.

Here, `v1.0`, `v1`, or schema `1` identifies a particular interface contract.
It does **not** mean the AIES standards corpus has reached its pending v1.0
release, nor that the `aies-platform` package is version 1.0.

## Non-Goals

The project does **not** aim to:

- Promote a specific AI vendor
- Publish a context-free model leaderboard or declare one universally “best”
- Replace existing engineering frameworks (it complements PMBOK, TOGAF, ISTQB, etc.)
- Become a prompt library
- Teach programming fundamentals

AIES does support evidence-compatible comparison of scoped assessment runs.
Those comparisons are engineering selection inputs, not universal rankings.
`aies compare` accepts 2–5 runs or deployment IDs, or 2–5 stored repository
assessment IDs, without mixing subject families. It places observed performance
beside direct scenario breadth for deployments and preserves perspective-native
metrics for repositories. It emits a higher-observed leader
or tie only when risk tier, subject kind, profile, task mapping, scoring
semantics, rater protocol, suite versions, repeat structure, evidence-adapter
profiles, and task instruments are compatible. Use `--sort spread` to find the
largest supported differences or `--only-comparable` to hide evidence gaps.
`--out DIRECTORY` writes an immutable Markdown/JSON/sortable-HTML bundle;
`--save` explicitly records the derived comparison for the read-only
`/comparisons` API. Pair and matrix reports expose compatibility failures,
coverage gaps, caveats, and evidence-driven next actions. They remain selection
inputs rather than selection, qualification, deployment, or authorization
decisions.

For cross-machine work, run `aies runs import PATH --dry-run` before importing
a run directory or ZIP. AIES accepts exactly one run, rejects unsafe archive
paths, symlinks, collisions, and overwrite, verifies the complete admitted
tree, and retains a source-bound receipt. `aies runs cohorts` then discovers
groups that share the exact ECM comparison protocol and prints connected
2–5-run commands. Compatibility does not imply independent or representative
evidence.

AIES defines **engineering standards** that remain applicable regardless of the
underlying AI technology.

## Roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Repository Foundation | ✅ Complete (v0.3.1) |
| 2 | AEBOK — Body of Knowledge | 🔍 Content complete; independent approval reviews pending |
| 3 | AESQS — Qualification Standard | 🔍 Content complete; independent approval reviews pending |
| 4 | AEOS — Operating System | 🔍 Content complete; independent approval reviews pending |
| 5 | AEAR — Architecture Reference | 🔍 Content complete; independent approval reviews pending |
| 6 | AECT — Certification & Training | 🔍 Content complete; independent approval reviews pending |
| 7 | Reference Implementations | 🟡 Core platform, conformance, and demo references delivered; independently reproducible public pilot artifacts pending |
| 8 | Engineering Assessment Platform (`aies` CLI) | 🟡 Public development preview — M1–M4 delivered; empirical validation, independent pilots, hardening, and additional subject executors pending |
| 9 | v1.0 Standards Release | 🚧 Release preparation active — public source preview and open licensing delivered; v0.5 comment/approval cycle and signed v1.0 release pending |

The repository is already public as a development preview. The separately
governed, versioned v1.0 standards release remains pending until independent
review, public-comment disposition, ratification, and immutable release
evidence are complete. See the
[authoritative roadmap](ROADMAP.md) and
[implementation backlog](docs/OSS_MATURITY_TODO.md).

Public milestones are maintained in [ROADMAP.md](ROADMAP.md). Detailed
vision-delivery and cleanup item statuses are maintained in the
[AIES Vision Execution Backlog](docs/OSS_MATURITY_TODO.md).

`Review` means the document is content-complete but not yet ratified. Promotion
to `Approved` requires two recorded reviews by independent non-authors,
resolution or reasoned waiver of every finding, stable IDs for all normative
requirements, and seven-day Maintainer lazy consensus. The v0.5 public-comment
cycle and its disposition record are also still required before v1.0. These
human governance gates cannot be replaced by automated checks or AI review.

## Engineering Assessment Platform

The **[Engineering Assessment Platform](platform/README.md)** (`aies` CLI) is
the executable reference implementation of the AIES evidence architecture. It
collects canonical evidence once and renders audience-specific decision
products without changing the underlying observations.

### Implemented now

| Assessment path | What the public preview does |
|---|---|
| **AI deployments** | Runs versioned scenarios across CA-01 — AI-Native SDLC Foundations through CA-12 — Governance, Risk & AI Safety; records candidate and reviewer identity; produces evidence, ECM, fit, coverage, diagnostics, remediation, and compatible comparisons |
| **Repositories** | Content-binds the requested scope and analyzes architecture, code quality, correctness assurance, testing, security, dependencies, operations, governance, documentation, and improvement evidence without executing unfamiliar code or pretending heuristics prove correctness |
| **Assessment system itself** | Validates suites, examines corpus coverage/calibration/diversity/duplicates, and checks decision-engine compatibility against immutable golden Evidence Packages |
| **Integrations** | Exposes versioned read-only workspace, run, report, support, and comparison contracts through CLI, JSON, HTML, safe exports, and an HTTP consumer API |

Automated reviewers can complete the informational Engineering Evaluation;
optional human ratings remain separately attributed. Formal qualification is
invoked only with `--formal-qualification` and still requires the governed
human protocol. Long operations show stable per-worker current tasks, stage and
command elapsed time, completed/total work, rate, ETA, and durable checkpoints.

The exact implemented, experimental, and planned subject boundary is generated
in the [Subject Support Matrix](platform/SUBJECT_SUPPORT.md) and exposed by
`aies support`. The complete command sequence is documented once in the
[command and artifact map](#command-and-artifact-map), the
[platform guide](platform/GUIDE.md), and the generated
[CLI reference](platform/CLI_REFERENCE.md).

### Evidence scope and honest claims

Platform results are always risk-scoped: RT1 — Minimal, RT2 — Moderate, RT3 —
Significant, and RT4 — Critical have different evidence, gate, and autonomy
requirements. An ECM `not assessed` task is an evidence gap, not a negative
capability claim. `--all-areas` covers all competency areas for the selected
risk tier; it does not silently claim coverage outside that scope.

The scenario corpus currently contains **484 validated scenarios across 12
competency areas**, with all 15 engineering tasks directly represented. Every
scenario carries design-time calibration metadata and the validator reports
zero structural warnings or errors. Empirical calibration against a
representative multi-model panel remains outstanding; design quality and
scenario count must not be presented as empirical discrimination.

## Try it, challenge it, improve it

The most valuable next signal is not a star. It is an engineer reaching the
first ECM, understanding what the evidence does and does not support, and
telling us where the workflow or report failed them.

1. Run `aies demo --open`.
2. [Connect and plan one real deployment](#connect-a-real-deployment), or
   assess one repository with `aies audit . --out aies-repository-report`.
3. [Report first-run friction, confusing output, or a reproducibility gap](https://github.com/umairali7/ai-engineering-standards/issues/new/choose).

If the idea is useful, help review one instrument, reproduce one result, add
one evidence adapter, or improve one explanation. Bounded contributions are
described in [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

Contributions are welcome. Every proposal should include an engineering rationale, problem statement, alternatives considered, trade-offs, references, and impact analysis. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Release identities and current status

This repository has three independent version axes. They must not be shortened
to one ambiguous “AIES version.”

| Axis | Current identity | Maturity and meaning |
|---|---|---|
| **Standards corpus** | `v0.4.0` | Governed research release; all five modules are content-complete at **Review**, not yet ratified as Approved |
| **Executable platform** | `aies-platform 0.1.0` | Functional public development preview with M1–M4 delivered; not a stable 1.0 software distribution |
| **Artifact and interface contracts** | Independently versioned | Each schema or contract carries its own version; a `v1`, `v1.0`, or schema `1` label is not the AIES v1.0 standards release |

Run `aies version` for the key installed identity inventory and
`aies --version` for only the Python package. The authoritative model is documented in
[Versioning and Release Identity](docs/VERSIONING_AND_RELEASES.md); changes are
recorded in [CHANGELOG.md](CHANGELOG.md). Individual standards documents carry
a lifecycle status—Draft → Review → Approved → Deprecated—under
[AIES-STD-06 — Review Standard](docs/standards/review-standard.md).

Current evidence and remaining boundaries:

- **Assessment corpus:** the validated scope and structural health are stated
  once in [Evidence scope and honest claims](#evidence-scope-and-honest-claims).
  Empirical panel calibration and an independently reproduced pilot remain
  open.
- **ECM:** the implementation and ET-01 through ET-15 taxonomy are delivered;
  formal ratification of AIES-ECM-01 and five-module standards integration are
  still governance work.
- **Subject support:** AI deployments and repositories have executable paths.
  Additional subject-neutral contracts exist, but agents, MCP servers, RAG
  systems, pipelines, platforms, and composite systems remain experimental or
  planned until dedicated executors and instruments are validated.
- **Publication:** the source repository is already public under its path-based
  open licenses. A signed, immutable preview distribution and the separately
  governed v1.0 standards release are not yet claimed.

<details>
<summary><strong>Public-release verification boundary</strong></summary>

The repository includes ownership routing, dependency-update automation,
full-history secret scanning, Python security analysis, dependency auditing,
CodeQL, private vulnerability reporting, an active `main` ruleset, retained
machine-readable evidence, and a fail-closed preflight. From the repository
root, run:

```bash
python platform/scripts/check_public_release.py .
```

Independent review evidence, historical Actions/artifact review, distribution
trust, and signed immutable release evidence remain explicit external gates.
At release time, supply a named and timestamped copy of
[`templates/public-release-external-evidence.json`](templates/public-release-external-evidence.json)
with `--external-evidence`, followed by `--gate`. The preflight verifies; it
never changes repository settings or authorizes publication.

</details>

## License

AIES is a path-based mixed-license repository under accepted
[ADR-0014](adr/ADR-0014-Dual-License-Standards-and-Software.md): standards and
reusable assessment content use **CC BY-SA 4.0**, while executable software
uses the **Apache License 2.0**. The authoritative path table and complete
official texts are in [LICENSE.md](LICENSE.md). CI verifies that every
distributed path resolves to one applicable license.

---

> **AI Engineering Standards (AIES)** is an open initiative to define the future of AI-native software engineering through vendor-neutral, engineering-first standards.

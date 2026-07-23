# AIES Adoption and Launch Plan

| | |
|---|---|
| **Document ID** | AIES-DOC-16 |
| **Status** | Draft |
| **Audience** | Maintainers · adopters · community partners |

## Goal

Make the first AIES value obvious and reproducible:

> See what an AI engineering subject demonstrably does well, where the evidence
> is thin, and where review is appropriate—without trusting one opaque score.

The primary call to action is `aies demo --open`. The first conversion is a
completed offline demo; the second is a planned real-subject evaluation; the
third is a shared, reproducible case study or contribution.

## Message hierarchy

1. **Problem:** engineering teams choose AI systems from anecdotes, generic
   benchmarks, and vendor claims that do not describe their engineering work.
2. **Product:** AIES turns versioned assessment evidence into an Engineering
   Capability Matrix, Engineering Fit guidance, diagnostics, and traceable
   reports.
3. **Difference:** observed performance and evidence confidence stay separate;
   unassessed remains unknown; compatible comparison is task-specific; formal
   qualification remains a separate human-governed process.
4. **Proof:** anyone can run the complete deterministic product path offline,
   then inspect every artifact.
5. **Invitation:** try one deployment, share what was confusing, contribute an
   instrument or adapter, or join an independent review.

## Persona conversion paths

| Persona | Decision they need | Lead message | First command | Proof artifact | Next conversion |
|---|---|---|---|---|---|
| Engineer | Where can this assistant help me? | See strengths, gaps, and evidence—not a leaderboard | `aies demo --open` | ECM | Evaluate one deployment |
| Engineering leader | Which subject fits our workload? | Compare compatible engineering tasks and limitations | `aies compare …` | ECM comparison + fit | Reproducible pilot |
| AI platform team | How can we standardize internal evaluation? | Keep runners; add a versioned evidence and decision layer | `aies bridge …` | Loss report + report bundle | Build an adapter |
| Security/quality team | What evidence exists and what remains unknown? | Preserve tool findings, provenance, uncertainty, and scope | `aies audit .` | Audit + diagnostics | Review a profile |
| Auditor/governance lead | Can engineering evidence support a governed decision? | Evaluation is non-blocking; formal qualification is explicit | `aies help` | Qualification boundary | Review AESQS |
| Researcher/evaluator | Are task scores valid and reproducible? | Instruments, mappings, uncertainty, and null results are inspectable | `aies suites calibrate` | Corpus/panel evidence | Join validity review |
| Open-source contributor | Where can I make a bounded difference? | Improve one instrument, bridge, test, or explanation | read `CONTRIBUTING.md` | Review packet | First merged contribution |

## Launch assets

Each asset must show real generated output and pass claim review:

- GitHub social preview: `docs/assets/aies-social-preview.png` now visualizes
  evidence → ECM → confidence → decision; repository settings still need to
  select it as the social image.
- Root README: problem, 60-second command, expected output, honest maturity,
  supported scope, primary CTA, persona paths, help/contribution links.
- A 30–60 second terminal recording: install → `aies demo --open` →
  Evidence → Capability → Confidence → Engineering Decisions snapshot → ECM.
- A 5–10 minute narrated trial: plan → evaluate → progress/ETA → report → share.
- Three report screenshots: Executive Summary, ECM, and evidence traceability.
- A technical launch article: why benchmarks are insufficient, how AIES
  separates decisions, reproducible commands, limitations, and roadmap.
- A downloadable redacted example bundle with hashes and reproduction notes.
- Issue forms for first-run failure, report comprehension, case-study interest,
  instrument review, and adapter proposals are implemented with explicit
  secret/private-evidence boundaries and a private security-advisory route.

## Channel plan

Broad broadcasting comes after a reproducible release. Before that, use small
feedback loops:

1. Invite 5–10 engineers/evaluators to private clean-install trials.
2. Open a GitHub Discussion with three pointed questions: what did you think
   AIES was, could you reach the ECM, and what decision would you use it for?
3. Publish the first versioned GitHub release with wheel/sdist, checksums,
   provenance, known limitations, and the offline demo command.
4. Publish the technical article and short demo together; link only to the
   versioned release.
5. Share targeted variants with AI engineering, evaluation, MLOps/platform,
   application security, software architecture, testing, open-source, and
   standards communities. Ask for a specific trial or review, not generic stars.
6. Recruit reproducibility pilots and independent reviewers directly from the
   people who completed the trial.
7. Submit evidence-backed demos or talks after the first public case study.

## Claim-review checklist

Every public claim, screenshot, badge, talk, or comparison records:

- exact supporting artifact/run/release;
- assessed subject and conditions;
- measurement-claim contract version;
- scenario/task coverage and missingness;
- automated/human reviewer status;
- calibration maturity;
- whether the claim is experimental, observed, validated, or governed;
- limitations and expiry/change triggers.

Do not say “industry standard,” “certified,” “production ready,” “best model,”
or “supports agents/MCP/RAG” until the corresponding approval, validation, or
subject profile is complete. “Designed to support” is not “implemented.”

## Funnel and success measures

```text
README visitor → demo completion → real plan → real evaluation
→ shared pilot/case study → contributor/reviewer → recurring adopter
```

Measure only public or voluntarily supplied aggregate signals:

- release-asset downloads;
- reported demo completion and time to first ECM;
- first-run failure and recovery categories;
- report-comprehension rate;
- real plans and evaluations reported by pilots;
- reproducible case studies;
- independent reviewers and organizations;
- issue response/resolution time;
- first contribution and repeat-contributor conversion.

No mandatory telemetry. Never collect prompts, responses, subject identities,
API endpoints, credentials, or private report content.

## Sequenced execution

| Phase | Exit gate |
|---|---|
| 1. Product proof | Installed offline demo, `init`, plan/evaluate/open, and redacted export pass clean-machine tests |
| 2. Conversion surface | README, Quickstart, CLI prompts, visual assets, and persona paths lead to the same verified command and terminal decision snapshot |
| 3. Trust package | License, release artifacts, hashes, SBOM/provenance, security/contact routes, and claim review are complete |
| 4. Small pilot | At least five unfamiliar users complete the trial; comprehension and failures are published and fixed |
| 5. Evidence launch | Validity study and first comparative case study are independently reviewed and reproducible |
| 6. Public launch | Versioned release, article, video, example bundle, Discussion, and targeted outreach publish together |
| 7. Adoption loop | Feedback becomes issues, contributors receive bounded entry points, and the scorecard drives the next release |

## Research basis

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [GitHub: About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [GitHub: Community conversations](https://docs.github.com/en/discussions/guides/best-practices-for-community-conversations-on-github)
- [Open Source Guides: Building welcoming communities](https://opensource.guide/building-community/)
- [Open Source Guides: Starting an open source project](https://opensource.guide/starting-a-project/)
- [Diátaxis documentation system](https://diataxis.fr/start-here/)
- [CNCF project lifecycle](https://contribute.cncf.io/projects/lifecycle/)

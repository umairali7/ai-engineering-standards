# Frequently Asked Questions

| | |
|---|---|
| **Document ID** | AIES-DOC-05 |
| **Status** | Review |
| **Audience** | All readers |

Answers to the questions most often asked about the AI Engineering Standards (AIES) project. This document is informative; where an answer touches normative material, it links to the governing document.

---

## 1. Who is AIES for?

Anyone who has to make AI participation in software delivery *work* — and defensible. In practice that means enterprise engineering organizations adopting AI-native delivery; CTOs, directors, and managers who must set policy and carry accountability; architects designing engineering platforms; platform teams building the tooling that enforces gates and audit trails; security, risk, and compliance teams that need traceability; QA organizations evaluating AI-produced artifacts; individual engineers building and certifying their competency; and educators basing curricula on a recognized body of knowledge. The full stakeholder analysis is in the [AIES-DOC-01 — Project Charter](PROJECT_CHARTER.md).

## 2. How is AIES different from ISO/IEC 42001 or NIST AI RMF?

They operate at different layers, and they complement rather than compete.

- **ISO/IEC 42001:2023** defines an AI *management system* — organizational governance of AI systems in general, whatever those systems do.
- **NIST AI RMF 1.0** provides a *risk management* framework for trustworthy AI systems in general.
- **AIES** governs something narrower and deeper: **AI participation in software engineering specifically** — how AI assistants and agents take part in the sixteen phases of the SDLC, how their capability is evaluated ([AESQS](../AESQS/README.md)), how much autonomy they may hold per task and risk tier ([Taxonomy §3–4](../Shared/Taxonomy/README.md)), and how humans oversee the result ([AEOS](../AEOS/README.md)).

If ISO/IEC 42001 tells an organization *that* it needs controlled, accountable AI use, AIES tells an engineering organization *what those controls look like inside the software delivery lifecycle*. A concrete mapping of AIES's scales and modules to ISO/IEC 42001, the ISO/IEC JTC 1/SC 42 technical standards (42119 testing of AI, 25059 AI quality model, 5338 AI life-cycle processes, 42005 impact assessment), the NIST AI RMF and Generative AI Profile, the EU AI Act, the AI security taxonomies (OWASP LLM/Agentic Top 10, MITRE ATLAS), and the CSA/ASDLC autonomy taxonomies is in the [AIES-DOC-07 — Standards Crosswalk — How AIES Maps to Adjacent Frameworks](CROSSWALK.md); documented mappings are a tracked success criterion (SC-7 in the [Charter](PROJECT_CHARTER.md)).

## 3. Is this about prompt engineering?

No. AIES is **engineering first** by [founding principle](../README.md#guiding-principles): engineering disciplines take precedence over prompt techniques and model-specific optimizations. Prompts and context are treated as governed *artifact types* (ART-13 in the [Taxonomy](../Shared/Taxonomy/README.md)) — things that must be versioned, reviewed, and traceable — not as content the standard publishes. Prompt libraries are an explicit non-goal (see [Charter §2.2](PROJECT_CHARTER.md)). Prompt techniques age with models; engineering standards must not.

## 4. Which AI vendors does AIES support?

All of them — and none of them in particular. AIES is strictly **vendor-neutral**: normative text must not name specific AI vendors, models, or commercial products (constraint C-1 in the [Charter](PROJECT_CHARTER.md); rule enforced through [GOVERNANCE.md §7](../GOVERNANCE.md#7-conflict-of-interest-and-vendor-influence)). The standard describes *capabilities* ("a code-generation agent operating at AL3 — Delegated within a defined envelope"), not brands. This is deliberate: models are replaced in months, but the engineering questions — how much autonomy, what evidence, which gates, whose accountability — remain the same regardless of which model answers the prompt.

## 5. Is AIES affiliated with any company?

No. The project has no owning vendor, sponsor company, or commercial parent. Neutrality is protected by process, not by promise: contributors must disclose relevant affiliations, no vendor-affiliated person may be the sole approver of a change affecting that vendor's positioning, conflicted Maintainers must abstain from escalation votes, and no single organization should hold a majority of Maintainer seats. The full conflict-of-interest policy is in [GOVERNANCE.md §7](../GOVERNANCE.md#7-conflict-of-interest-and-vendor-influence), and contributor diversity is a tracked success criterion (SC-6).

## 6. Can I use AIES with agile, Scrum, or SAFe?

Yes. AIES is method-agnostic by design. Its sixteen SDLC phases ([P01 — Business Strategy through P16 — Continuous Improvement](../Shared/Taxonomy/README.md)) are *logical*, not sequential: iterative and incremental delivery maps onto them repeatedly, sprint by sprint. A Scrum team refines backlog items (P03, P05), builds (P09), tests (P10), and releases (P13) every sprint — AIES adds the AI-specific layer on top: which of those tasks AI may perform, at what autonomy level, under which oversight gates. AIES complements process frameworks the same way it complements PMBOK and TOGAF ([README — Non-Goals](../README.md#non-goals)); it does not replace your delivery methodology.

## 7. How do autonomy levels work?

The [Taxonomy](../Shared/Taxonomy/README.md) defines five autonomy levels, AL0 — Manual (Manual) through AL4 — Autonomous (Autonomous), describing how much independent authority an AI system holds *for a given task*. Three rules make the scale meaningful:

1. Autonomy is assigned **per task type, per risk tier** — never globally to a whole system. The same agent may hold AL4 — Autonomous for formatting fixes and AL1 — Assisted for auth-adjacent code.
2. The task's **risk tier (RT1 — Minimal through RT4 — Critical)** caps the maximum permissible autonomy: minimal-risk work defaults up to AL4 — Autonomous, critical work down to AL1 — Assisted. Organizations may tighten these defaults but must not loosen them without documented risk acceptance.
3. Autonomy increases must be **evidence-driven and reversible** — granted on the basis of qualification data produced through [AESQS](../AESQS/README.md), not vendor claims or enthusiasm.

[AEOS](../AEOS/README.md) defines how organizations operationalize this: envelopes, checkpoints, sampling, and audit.

## 8. Can AI systems be "certified"?

No — and the distinction is deliberate. **Certification** is for humans: [AECT](../AECT/README.md) defines learning paths, examinations, and credentials for engineers. AI systems are instead **qualified**: [AESQS](../AESQS/README.md) evaluates an AI system's demonstrated capability on defined task types, in context, against the evaluation dimensions EV1–EV6, producing the evidence that autonomy decisions are based on. Qualification is scoped (per task type and risk tier), evidence-based, and revocable when the evidence changes. A certificate says a person has durable competency; a qualification says a system has demonstrated capability *under these conditions, for now*.

## 9. How do I get certified?

Through [AECT](../AECT/README.md), the Certification & Training module, which defines learning paths, labs, examinations, and credentials aligned to the competency levels CL1–CL4 in the [Taxonomy](../Shared/Taxonomy/README.md). The certification program is not yet operational: AECT is in drafting (see [ROADMAP.md](../ROADMAP.md)), and the charter targets at least one examinable credential within 18 months of the v1.0 release (SC-4). Until then, the best preparation is the material itself — start with [AEBOK](../AEBOK/README.md), which defines the knowledge the examinations will cover.

## 10. What version is AIES currently?

There is no single undifferentiated version. The governed **standards corpus is
v0.4.0** and its five modules are content-complete at Review, not yet ratified
as Approved. The executable distribution is independently versioned as
**`aies-platform 0.1.0`**, a public development preview. Artifact schemas and
interfaces carry their own contract versions. Consequently, a `v1`, `v1.0`, or
schema `1` label on an interface does not claim that either the standards or
software has reached its pending 1.0 release.

The earlier v0.3.1 tag remains the completed **Repository Foundation** release
recorded in the roadmap; it is not the current standards identity. Run
`aies version` for the installed inventory and see
[Versioning and Release Identity](VERSIONING_AND_RELEASES.md) for the
authoritative distinctions. Individual standards documents carry their own
lifecycle status (Draft → Review → Approved → Deprecated) under
[AIES-STD-06 — Review Standard](standards/review-standard.md).

## 11. How is the mixed standards-and-software repository licensed?

Accepted
[ADR-0014](../adr/ADR-0014-Dual-License-Standards-and-Software.md) matches the
license to the work type: **CC BY-SA 4.0** keeps adapted standards and reusable
assessment content attributable and open, while the OSI-approved **Apache
License 2.0** gives executable software conventional open-source terms with an
explicit patent grant. [LICENSE.md](../LICENSE.md) is the authoritative
path-level boundary for scenarios, rubrics, documentation, code, tests,
automation, and mixed files. CI checks that every distributed path resolves to
one applicable license. Contributions remain subject to the DCO and the
license applicable to their destination path
([CONTRIBUTING.md §7](../CONTRIBUTING.md#7-developer-certificate-of-origin)).

## 12. How are breaking changes handled?

Deliberately and traceably. Any change to RFC 2119 requirements, any edit to the [Shared Taxonomy](../Shared/Taxonomy/README.md), any redefinition of a [Glossary](../Shared/Glossary/README.md) term, or anything that alters document or requirement IDs is a **Class 3 — Normative/Breaking** decision ([GOVERNANCE.md §3](../GOVERNANCE.md#3-decision-classes)). Class 3 requires an [Architecture Decision Record](../adr/README.md), lazy consensus of Maintainers, a 7-day public comment period, and mandatory cross-module impact analysis. Changes to the Shared Standards are *always* at least Class 3, because every module depends on them. When in doubt, changes are classified upward: a good-faith argument that something is Class 3 makes it Class 3.

## 13. What happens when AI models improve dramatically?

The standard absorbs it — that scenario is a design assumption, not a threat. AIES deliberately anchors on stable abstractions (autonomy levels, risk tiers, roles, evaluation dimensions) rather than on capability snapshots (assumption A-2 and risk R-2 in the [Charter](PROJECT_CHARTER.md)). When models improve, the mechanism is **evidence-based re-qualification**: the improved system demonstrates its new capability through [AESQS](../AESQS/README.md) evaluation, and that evidence justifies raising its autonomy level for specific task types — within the caps that risk tiers still impose. Nothing in the framework needs rewriting; the qualification data changes, and the autonomy decisions follow. The same mechanism works in reverse: capability regressions or incident evidence drive autonomy back down, because grants are required to be reversible ([Taxonomy R03](../Shared/Taxonomy/README.md)).

## 14. How do I contribute?

Start with [CONTRIBUTING.md](../CONTRIBUTING.md). In short: editorial fixes go straight to a PR; substantive content starts with a Content Proposal issue carrying the full engineering rationale package (problem statement, alternatives, trade-offs, references, impact analysis); normative or breaking changes additionally require an ADR. Read the [Documentation Standards (AIES-STD-00 — Documentation Standards)](standards/README.md) first, use Glossary and Taxonomy terms exactly as defined, sign off your commits (DCO), and expect review against the evaluation dimensions EV1–EV6. Peer review of open drafts is itself a valued contribution and the usual path to becoming a Reviewer.

## 15. Where do I start reading?

Depends on who you are:

| You are… | Start with |
|----------|-----------|
| New to the project entirely | [README.md](../README.md), then the [AIES-DOC-02 — Vision](VISION.md) |
| An executive or engineering leader | [AIES-DOC-01 — Project Charter](PROJECT_CHARTER.md), then [AEOS](../AEOS/README.md) |
| An architect or platform engineer | [AIES-DOC-03 — Repository Architecture](ARCHITECTURE.md), then [AEAR](../AEAR/README.md) |
| A practicing engineer | [AEBOK](../AEBOK/README.md), with the [Glossary](../Shared/Glossary/README.md) and [Taxonomy](../Shared/Taxonomy/README.md) at hand |
| A QA, security, risk, or compliance professional | [Taxonomy](../Shared/Taxonomy/README.md) (autonomy levels, risk tiers), then [AESQS](../AESQS/README.md) |
| A learner aiming for certification | [AECT](../AECT/README.md), then [AEBOK](../AEBOK/README.md) |
| A prospective contributor | [CONTRIBUTING.md](../CONTRIBUTING.md) and [GOVERNANCE.md](../GOVERNANCE.md) |

The full navigation table is in [ARCHITECTURE.md §6](ARCHITECTURE.md#6-navigation-guide).

---

## Related Documents

- [AIES-DOC-01 — Project Charter](PROJECT_CHARTER.md)
- [AIES-DOC-02 — Vision](VISION.md)
- [AIES-DOC-03 — Repository Architecture](ARCHITECTURE.md)
- [AIES-GOV-01 — Governance](../GOVERNANCE.md) · [CONTRIBUTING.md](../CONTRIBUTING.md)

## References

- ISO/IEC 42001:2023 — Information technology — Artificial intelligence — Management system
- NIST AI RMF 1.0 — Artificial Intelligence Risk Management Framework (NIST AI 100-1)

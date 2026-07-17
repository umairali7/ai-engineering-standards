# Standards Crosswalk — How AIES Maps to Adjacent Frameworks

| | |
|---|---|
| **Document ID** | AIES-DOC-07 |
| **Status** | Draft |
| **Audience** | Engineering leadership · Governance officers · Architects · Contributors & maintainers |

AIES does not replace the AI-governance and autonomy frameworks an organization
already uses. It is the **executable engineering-qualification layer that plugs
into them**: the others say *what* autonomy levels, risk tiers, and governance
to have; AIES runs the evidence that decides *whether a given deployment has
earned one*, and records it as an auditable artifact.

This document maps AIES's canonical scales and modules to the external
frameworks they align with, so adopters can reconcile AIES with what they
already report against. The mappings are **approximate interpretive aids, not
claims of certified equivalence, conformance, or endorsement** — see §6.

## Positioning at a glance

| Framework | What it provides | Relationship to AIES |
|-----------|------------------|----------------------|
| CSA *Levels of Autonomy for Agentic AI* | An autonomy-level taxonomy (institutional) | AIES autonomy levels align to it (§1) |
| ASDLC / AI-SDLC | A vendor-neutral SDLC governance specification with L1–L5 | Conceptual sibling; AIES adds executable qualification (§1, §5) |
| EU AI Act | Legal risk categories & obligations | AIES risk tiers align to it (§2); AIES oversight supports its Art. 14 (§3) |
| EU GPAI Code of Practice | Transparency, copyright, safety, and security commitments for GPAI model providers | AIES supplies downstream engineering evidence and controls (§3) |
| NIST AI RMF + Generative AI Profile | Govern / Map / Measure / Manage functions, with GenAI-specific risk actions | AIES activities map to the functions and produce SDLC-scoped evidence (§3) |
| ISO/IEC 42001 | AI management system (AIMS) | AIES supplies engineering evidence into the AIMS (§3) |
| ISO/IEC SC 42 technical standards (42119 testing · 25059 quality · 5338 lifecycle · 42005 impact) | Testing, quality-model, lifecycle, and impact-assessment standards for AI | AIES's platform, EV dimensions, and SDLC phases instantiate/align to them (§3a) |
| OWASP GenAI / Agentic AI Top 10 | Security risk taxonomies for GenAI and agentic applications | AIES KA-07 and AEAR controls operationalize mitigations in software delivery (§3, §5) |
| MLCommons AILuminate · UK AISI Inspect · DeepEval · HELM | AI safety benchmarks & eval frameworks | Complementary: benchmarks measure a model's safety/capability; AIES adds deployment-scoped, SDLC-competency, human-granted *qualification* and can ingest their traces as EV evidence (§5) |
| ARTiBA AMDEX · CertNexus CAIP | Human AI-engineering bodies of knowledge & certs | Complementary to AEBOK/AECT (§4) |

## 1. Autonomy levels

AIES [AL0–AL4 (AIES-SHARED-02 §3)](../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4)
align to the [CSA *Levels of Autonomy for Agentic AI*](https://cloudsecurityalliance.org/blog/2026/01/28/levels-of-autonomy)
(6 levels, 0–5) and the [ASDLC autonomy scale](https://asdlc.io/concepts/levels-of-autonomy/)
(L1–L5). The mapping is approximate — the scales draw their boundaries slightly
differently — but the through-line (human role shifts from performer → reviewer
→ supervisor → auditor as autonomy rises) is shared by all three.

| AIES | AIES human role | ≈ CSA level | ≈ ASDLC level |
|------|-----------------|-------------|---------------|
| **AL0** Manual | Performer | L0 No Autonomy | (below L1) |
| **AL1** Assisted | Author | L1 Assisted | L1 Assistive |
| **AL2** Collaborative | Reviewer (per item) | L1–L2 (per-item → batch approval) | L2 Task-Based |
| **AL3** Delegated | Supervisor (checkpoints + sampling) | L3 Conditional (within boundaries) | L3 Conditional |
| **AL4** Autonomous | Auditor (policy + audit) | L4 High Autonomy | L4 High |
| *(none — by design)* | — | L5 Full (self-directed) | L5 Full |

Notes:
- **AIES deliberately has no "full autonomy" level.** CSA L5 / ASDLC L5 (goal-
  setting, self-modifying, no human loop) has no AIES equivalent; AIES caps the
  scale at AL4 and never grants even AL4 at initial qualification
  ([AIES-AESQS-CS-01-R08](../AESQS/capability-scoring.md)).
- **AL1 vs AL2 is the fuzziest boundary.** AIES AL1 is conservative (AI
  *suggests*, a human authors); CSA L1 already has the AI *executing* with
  per-action approval, which sits between AIES AL1 and AL2.
- All three scales agree that mid-scale (AIES AL3 / CSA L3 / ASDLC L3) is where
  bounded delegation lives and where oversight must be strongest; ASDLC calls
  L3 "the production ceiling."
- A fourth, academic taxonomy — *Levels of Autonomy for AI Agents* (arXiv
  2506.12469, 2025) — defines five levels by **the role the human takes**:
  Operator → Collaborator → Consultant → Approver → Observer. This maps cleanly
  onto the AIES "human role" column (Performer → Author → Reviewer → Supervisor
  → Auditor) and reinforces an AIES design principle: **autonomy is a deliberate
  design choice, set independently of the model's raw capability and its
  operating environment** — which is exactly why AIES grants an *envelope*
  (RT×AL) rather than reading autonomy off a capability score.

## 2. Risk tiers

AIES [RT1–RT4 (AIES-SHARED-02 §4)](../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)
align to the EU AI Act's risk categories. **Unit-of-analysis caveat:** the EU AI
Act classifies an *AI system's* risk; AIES RT classifies a *task or change's*
blast radius. They are used differently, so this is a rough correspondence for
calibrating expectations, not a legal equivalence.

| AIES risk tier | ≈ EU AI Act category |
|----------------|----------------------|
| **RT1** Minimal | Minimal risk |
| **RT2** Moderate | Limited / transparency-obligation risk |
| **RT3** Significant | High risk |
| **RT4** Critical | High risk / prohibited (unacceptable) uses |

The EU AI Act does not tier by four levels identically; NIST AI RMF is not
tiered at all (see §3). AIES's RT→AL cap table is AIES's own control and is not
derived from any external framework.

**EU AI Act status (as of this revision).** GPAI (general-purpose AI) provider
obligations entered application on **2 Aug 2025**; the Commission's enforcement
powers, including fines, apply from **2 Aug 2026**. The **GPAI Code of Practice**
(published 10 Jul 2025) is a voluntary compliance tool bridging the gap until
harmonized standards exist. CEN-CENELEC (CEN-CLC/JTC 21) has targeted **Q4 2026**
for the key AI Act harmonized standards and in Oct 2025 adopted accelerating
measures (direct publication after a positive Enquiry vote, and a focused
drafting group for the most-delayed drafts) — so harmonized standards will lag
the Act's high-risk obligations. AIES is positioned like the Code of Practice: a
voluntary, evidence-producing layer usable now, ahead of ratified harmonized
standards.

## 3. Governance & lifecycle mapping

AIES modules and artifacts supply the *engineering evidence* that governance
frameworks call for but do not themselves produce.

| AIES element | NIST AI RMF / GenAI Profile | ISO/IEC 42001 (AIMS) | EU AI Act / GPAI Code | OWASP GenAI / Agentic AI |
|--------------|----------------------------|----------------------|--------------------|-------------------------|
| AESQS qualification & scoring (EV1–EV6, evidence records) | **Measure**; model/output evaluation and monitoring evidence | Performance evaluation; AI system lifecycle controls | Conformity-assessment-style evidence; downstream performance records | Evidence that controls are tested rather than only documented |
| AEOS gates, human oversight, kill-switch (X07) | **Manage** / **Govern**; incident response and escalation | Operational planning & control | Human oversight (Art. 14); lifecycle governance for GPAI integrations | Limits excessive agency and unsafe autonomous action |
| AEOS audit trail (ART-15), Qualification Records | **Govern**; traceability, accountability, monitoring | Documented information; monitoring & records | Record-keeping / logging (Art. 12); GPAI documentation support | Forensics for prompt injection, tool misuse, and policy bypass |
| Shared risk tiers & autonomy levels | **Map**; context-of-use and impact analysis | Risk assessment & treatment | Risk-based classification; provider vs deployer distinction | Blast-radius framing for agentic risk prioritization |
| AEAR guardrail, execution, and context planes | **Manage**; risk controls for GenAI deployment | Operational controls and supplier controls | Safety/security mitigation evidence for GPAI-dependent systems | Mitigates prompt injection, supply-chain, tool misuse, and memory/context risks |
| AEBOK competency, AECT credentials | (supports **Govern** roles) | Competence (Clause 7.2) | — | Human capability for secure agent design and review |

Read this as: an organization running an ISO/IEC 42001 AIMS, reporting against
the NIST AI RMF and its Generative AI Profile, or integrating models covered by
EU AI Act / GPAI obligations can use AIES to *generate the AI-engineering
evidence* those frameworks require — decisional capability scores,
oversight-gate records, tool-use logs, and environment-bound Qualification
Records — rather than treating AIES as a competing management system. Clause-,
article-, and commitment-level mapping should be validated by a compliance
professional for a specific deployment.

## 3a. ISO/IEC SC 42 technical standards (testing, quality, lifecycle)

Beyond the management-system layer (§3), ISO/IEC JTC 1/SC 42 has published a
family of **technical** AI standards that map directly onto the AIES engineering
spine — its testing engine, its quality dimensions, and its lifecycle phases.
These are the closest external analogues to what the AIES platform *does*, and
2025 additions (notably the 42119 testing series) landed after AIES's first
draft.

| ISO/IEC standard | What it provides | AIES element it maps to |
|---|---|---|
| **TS 42119-2:2025** — Testing of AI, Part 2 (overview of testing AI systems) | Applies the ISO/IEC/IEEE **29119** software-testing series to AI, with a **risk-based** approach to selecting tests, approaches, and techniques | **AESQS** + the `aies` platform: risk-tiered scenario suites, statistical minimums, and gated EV scoring are an executable instantiation of risk-based AI testing. AIES adds deployment-scoped qualification and a human grant on top of the test layer. |
| **25059** — Quality model for AI (extends the SQuaRE / ISO/IEC 25010 series) | AI-specific quality characteristics layered onto the software product-quality model | **EV1–EV6** evaluation dimensions (mapping below) |
| **5338** — AI system life-cycle processes (extends ISO/IEC/IEEE 15288 / 12207) | AI-specific life-cycle processes (data management, continuous validation, retraining/evolution) | **SDLC phases P01–P16** and the AEBOK/AESQS phase model |
| **42005:2025** — AI system impact assessment | How and when to perform impact assessments across the lifecycle, plus documentation guidance | **AEOS** governance; supports an impact-assessment artifact feeding oversight and risk-tiering |
| **42006:2025** — Requirements for bodies auditing/certifying an AIMS | Competence and process requirements for ISO/IEC 42001 certification bodies | **AECT** certification and competency levels CL1–CL4 |

### EV1–EV6 ↔ ISO/IEC 25059 quality characteristics

AIES's evaluation dimensions are not ad hoc: they align to the AI quality model
that 25059 layers onto ISO/IEC 25010. (Approximate correspondence for
calibrating expectations, not a formal equivalence.)

| AIES dimension | ≈ 25059 / 25010 characteristic |
|---|---|
| **EV1** Correctness | Functional correctness (functional suitability) |
| **EV2** Completeness | Functional appropriateness / completeness (functional suitability) |
| **EV3** Safety & Security | Robustness (reliability) + intervenability (security) + societal/ethical risk mitigation (freedom from risk) |
| **EV4** Maintainability | Maintainability |
| **EV5** Efficiency | Performance efficiency |
| **EV6** Traceability | Transparency (AI-specific) + record-keeping |

> **Edition note.** This mapping tracks **ISO/IEC 25059:2023**. A 2nd edition
> (DIS, expected 2026) reshuffles the model — *intervenability* moves under a new
> top-level **Safety** characteristic and *usability* becomes *interaction
> capability* — so revisit the EV3/EV6 rows when it ratifies.

> **Anchoring to NIST action IDs.** The NIST Generative AI Profile (AI 600-1)
> tags each suggested action to an RMF function/subcategory (e.g. `GV-1.1-001`,
> `MS-2.3-002`; GV=Govern, MP=Map, MS=Measure, MG=Manage). AIES scenarios and
> gates can cite these IDs directly, so a qualification run's evidence points at
> the exact NIST action it substantiates.

## 3b. Security & supply-chain standards

The security area (CA-07 / KA-07) and delivery area (CA-08 / KA-08) map to the
established AI-security threat taxonomies and the emerging model-supply-chain
standards. AIES operationalizes these as **tested** controls and gated
evidence, not documentation.

| Standard | What it provides | AIES element it maps to |
|---|---|---|
| **OWASP Top 10 for LLM Applications (2025)** | LLM-app risk taxonomy (prompt injection, sensitive-info disclosure, supply chain, excessive agency, …) | **CA-07** scenarios + KA-07; AEAR guardrail/broker controls |
| **OWASP Top 10 for Agentic Applications (2026, ASI01–ASI10; publ. 9 Dec 2025)** | Agent-specific risks distinct from the LLM Top 10 — agent/goal-behavior hijacking, tool misuse & exploitation, identity & privilege abuse, memory poisoning, cascading failures | **CA-07** + **CA-10** oversight + AEOS guardrails/autonomy envelopes |
| **AAGATE** (NIST-RMF agentic control plane, 2025) | Reference architecture binding NIST AI RMF functions to agentic frameworks (MAESTRO→Map, OWASP AIVSS + SEI SSVC→Measure, CSA Agentic Red-Teaming→Manage) | Illustrates the agentic-governance convergence AIES AEOS/AL–RT should interoperate with; supports the "traditional AppSec is insufficient for agents" premise behind AIES guardrails |
| **MITRE ATLAS** | Adversarial-ML attack tactics & techniques knowledge base | **CA-07** threat-modeling scenarios; AEOS incident classification (§6) |
| **NIST AI 100-2e2025** (Adversarial ML taxonomy) | Attack/defense taxonomy incl. indirect prompt injection, agent memory poisoning, supply-chain attacks | **CA-07**; the **EV3** Safety & Security gate |
| **CISA/NCSC Guidelines for Secure AI System Development** | Secure-by-design AI lifecycle (design → develop → deploy → operate) | **CA-08** delivery + AEAR; AEOS operations |
| **OpenSSF Model Signing (OMS) · AI-BOM (CycloneDX / SPDX 3.0) · SLSA** | Model signing, bill-of-materials, and build-provenance for the AI supply chain | Deployment **provenance** (the D7 environment fingerprint + artifact checksums). A deployment manifest MAY declare `provenance.signature` and `provenance.ai_bom`; the platform records them through to the evidence package and Qualification Record (verification delegated, like `checksum`). **CA-08**. |

## 4. Knowledge & human certification

The human-facing AIES modules overlap with existing vendor-neutral bodies of
knowledge and certifications, and are best read as **complementary and more
specific**, not competing:

| AIES | Adjacent | Difference |
|------|----------|------------|
| [AEBOK](../AEBOK/README.md) (body of knowledge) | [ARTiBA AMDEX](https://www.artiba.org/about-artiba/standards) | AMDEX covers general AI/ML engineering; AEBOK covers **AI-native *software* engineering** across the SDLC |
| [AECT](../AECT/README.md) (human credentials) | ARTiBA AiE®/CAiEP®, [CertNexus CAIP](https://certnexus.com/certified-artificial-intelligence-practitioner-caip/) (ISO/IEC 17024-accredited) | Those certify AI/ML practitioners generally; AECT certifies practitioners of AI-native SE and of *governing AI participation* |

AIES does not seek to displace accredited human certifications; where an
organization already uses them, AECT competencies can be treated as an
SDLC-specific extension.

## 5. What AIES adds that these frameworks do not

The adjacent frameworks converge with AIES on autonomy levels, risk tiers, and
governance — which validates the approach — but none of them provide, and AIES
uniquely does:

1. **Executable, evidence-based *qualification* of a specific deployment** —
   scoped, human-granted, revocable — with a working reference implementation
   (the `aies` platform), not documentation alone. ASDLC/AI-SDLC describe
   "earned autonomy"; AIES *runs the evidence*.
2. **Deployment (model × runtime × config × environment), not model, as the
   qualification subject**, with an environment-change re-qualification trigger
   ([PLATFORM.md D7](PLATFORM.md)).
3. **A competency body of knowledge bound to the model qualification** — the
   scoring maps to CA-01…CA-12, which derive from AEBOK.
4. **Multi-phase journeys** that test whether a model's SDLC phases cohere, not
   just isolated capabilities.
5. **Agentic delivery controls** that bind autonomy, tool use, context assembly,
   connector permissions, audit trails, and human gates into one enforceable
   engineering operating model.

This is the gap AIES occupies: the executable qualification layer beneath the
governance and autonomy frameworks the industry is standardizing.

## 6. How to read this crosswalk

- **Approximate, one-directional aids.** These mappings help reconcile
  vocabularies; they are not assertions that an AIES level/tier *is* an external
  one, nor that conformance to one implies conformance to another.
- **Not conformance or endorsement.** AIES is independent and unaffiliated with
  CSA, ISO, NIST, the EU, ARTiBA, CertNexus, or the ASDLC/AI-SDLC project.
  Naming them here is descriptive alignment, not partnership.
- **Versioned and evolving.** External frameworks change quickly; this mapping
  should be re-checked whenever mapped frameworks change and at least annually
  per [AIES-DOC-09](IMPROVEMENT.md).
- **Validate for your context.** For legal or certification decisions, confirm
  the mapping with a qualified compliance professional against the authoritative
  source text.

## Related Documents

- [Taxonomy (AIES-SHARED-02)](../Shared/Taxonomy/README.md) — the AL/RT scales mapped here
- [AESQS Capability Scoring (AIES-AESQS-CS-01)](../AESQS/capability-scoring.md) — the evidence AIES generates
- [Qualification Platform (AIES-DOC-06)](PLATFORM.md) — the executable layer
- [FAQ (AIES-DOC-05)](FAQ.md) — how AIES differs from ISO/IEC 42001 and the NIST AI RMF
- [Vision (AIES-DOC-02)](VISION.md) · [Project Charter (AIES-DOC-01)](PROJECT_CHARTER.md)

## References

- Cloud Security Alliance — *Levels of Autonomy for Agentic AI* (2026): https://cloudsecurityalliance.org/blog/2026/01/28/levels-of-autonomy
- ASDLC / AI-SDLC — autonomy levels and framework primer: https://asdlc.io/concepts/levels-of-autonomy/ · https://ai-sdlc.io/docs/spec/primer
- EU Artificial Intelligence Act (Regulation (EU) 2024/1689) — risk categories; human oversight (Art. 14); record-keeping (Art. 12)
- European Commission — General-Purpose AI Code of Practice (2025); guidelines and Q&A for GPAI obligations under the AI Act
- NIST AI Risk Management Framework (AI RMF 1.0) — Govern / Map / Measure / Manage
- NIST AI 600-1 — Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile
- ISO/IEC 42001:2023 — Artificial intelligence management system
- ISO/IEC TS 42119-2:2025 — Artificial intelligence — Testing of AI — Part 2: Overview of testing AI systems (applies the ISO/IEC/IEEE 29119 series to AI)
- ISO/IEC 25059 — Quality model for AI systems (extends the SQuaRE / ISO/IEC 25010 series)
- ISO/IEC 5338 — Information technology — Artificial intelligence — AI system life cycle processes (extends ISO/IEC/IEEE 15288 / 12207)
- ISO/IEC 42005:2025 — Artificial intelligence — AI system impact assessment
- ISO/IEC 42006:2025 — Requirements for bodies providing audit and certification of AI management systems
- NIST AI 100-5 — Agentic AI profile (agentic-system risk guidance; emerging)
- OWASP GenAI Security Project — 2025 Top 10 for LLMs and GenAI Applications; OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10, published 9 Dec 2025)
- MLCommons AILuminate v1.0 — AI Risk & Reliability benchmark (12 hazard categories)
- UK AI Security Institute — Inspect (LLM/agent evaluation framework); MITRE ATLAS; CISA/NCSC Guidelines for Secure AI System Development
- AAGATE — a NIST-AI-RMF-aligned governance control plane for agentic AI (arXiv 2510.25863, 2025)
- "Levels of Autonomy for AI Agents" — five user-role autonomy levels (arXiv 2506.12469, 2025)
- ARTiBA AMDEX standards: https://www.artiba.org/about-artiba/standards
- CertNexus CAIP (ISO/IEC 17024-accredited): https://certnexus.com/certified-artificial-intelligence-practitioner-caip/

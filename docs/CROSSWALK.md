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
| NIST AI RMF | Govern / Map / Measure / Manage functions | AIES activities map to the functions (§3) |
| ISO/IEC 42001 | AI management system (AIMS) | AIES supplies engineering evidence into the AIMS (§3) |
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

## 3. Governance & lifecycle mapping

AIES modules and artifacts supply the *engineering evidence* that governance
frameworks call for but do not themselves produce.

| AIES element | NIST AI RMF function | ISO/IEC 42001 (AIMS) | EU AI Act |
|--------------|----------------------|----------------------|-----------|
| AESQS qualification & scoring (EV1–EV6, evidence records) | **Measure** | Performance evaluation; AI system lifecycle controls | Conformity-assessment-style evidence |
| AEOS gates, human oversight, kill-switch (X07) | **Manage** / **Govern** | Operational planning & control | Human oversight (Art. 14) |
| AEOS audit trail (ART-15), Qualification Records | **Govern** | Documented information; monitoring & records | Record-keeping / logging (Art. 12) |
| Shared risk tiers & autonomy levels | **Map** | Risk assessment & treatment | Risk-based classification |
| AEBOK competency, AECT credentials | (supports **Govern** roles) | Competence (Clause 7.2) | — |

Read this as: an organization running an ISO/IEC 42001 AIMS or reporting against
the NIST AI RMF can use AIES to *generate the AI-engineering evidence* those
frameworks require — decisional capability scores, oversight-gate records, and
environment-bound Qualification Records — rather than treating AIES as a
competing management system. Clause- and article-level mapping should be
validated by a compliance professional for a specific deployment.

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

This is the gap AIES occupies: the executable qualification layer beneath the
governance and autonomy frameworks the industry is standardizing.

## 6. How to read this crosswalk

- **Approximate, one-directional aids.** These mappings help reconcile
  vocabularies; they are not assertions that an AIES level/tier *is* an external
  one, nor that conformance to one implies conformance to another.
- **Not conformance or endorsement.** AIES is independent and unaffiliated with
  CSA, ISO, NIST, the EU, ARTiBA, CertNexus, or the ASDLC/AI-SDLC project.
  Naming them here is descriptive alignment, not partnership.
- **Versioned and evolving.** External frameworks change; the mappings reflect
  the versions cited in the References and should be re-checked over time.
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
- NIST AI Risk Management Framework (AI RMF 1.0) — Govern / Map / Measure / Manage
- ISO/IEC 42001:2023 — Artificial intelligence management system
- ARTiBA AMDEX standards: https://www.artiba.org/about-artiba/standards
- CertNexus CAIP (ISO/IEC 17024-accredited): https://certnexus.com/certified-artificial-intelligence-practitioner-caip/

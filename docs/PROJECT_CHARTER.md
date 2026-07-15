# Project Charter

| | |
|---|---|
| **Document ID** | AIES-DOC-01 |
| **Status** | Review |
| **Audience** | Engineering leadership · Contributors & maintainers |

The charter of the **AI Engineering Standards (AIES)** project. It defines why the project exists, what is in and out of scope, who it serves, how success is measured, how decisions are made, and which risks are actively managed.

---

## 1. Purpose

Artificial intelligence now participates in every phase of the software development life cycle — analysis, design, implementation, testing, security, deployment, and operations. Yet no comprehensive, vendor-neutral engineering standard defines *how* that participation should be structured, evaluated, governed, and audited.

The AIES project exists to close that gap by producing an open, engineering-first standard that enables organizations to:

- **Build** AI-native engineering processes with a shared vocabulary and lifecycle model.
- **Evaluate** the capability of humans, teams, and AI systems against objective, repeatable criteria.
- **Govern** AI participation through explicit autonomy levels, risk tiers, gates, and audit trails.
- **Certify** engineers through a defined competency and credentialing framework.
- **Operate** AI-native delivery organizations reliably at enterprise scale.

The intended long-term position of AIES is stated in the [Vision (AIES-DOC-02)](VISION.md): to be for AI Engineering what PMBOK is for project management and TOGAF is for enterprise architecture.

## 2. Scope

### 2.1 In Scope

| Item | Description |
|------|-------------|
| **AEBOK** | The AI Engineering Body of Knowledge — disciplines, practices, patterns, and per-phase SDLC guidance ([AEBOK/](../AEBOK/README.md)) |
| **AESQS** | The SDLC Qualification Standard — competency model, evaluation rubrics, and capability scoring for humans and AI systems ([AESQS/](../AESQS/README.md)) |
| **AEOS** | The Operating System — roles, workflows, autonomy governance, human oversight, and operating-model design ([AEOS/](../AEOS/README.md)) |
| **AEAR** | The Architecture Reference — vendor-neutral reference architectures and industry blueprints for enterprise AI engineering platforms ([AEAR/](../AEAR/README.md)) |
| **AECT** | Certification & Training — learning paths, labs, examinations, and credentials ([AECT/](../AECT/README.md)) |
| **Shared Standards** | The canonical [Glossary](../Shared/Glossary/README.md), [Taxonomy](../Shared/Taxonomy/README.md), and documentation conventions used by every module ([Shared/](../Shared/README.md)) |
| **Templates** | Reusable document skeletons for standards, ADRs, and other governed artifacts ([templates/](../templates/README.md)) |
| **Worked Examples** | Concrete, end-to-end illustrations of the standards applied to realistic engineering situations ([examples/](../examples/README.md)) |
| **Supporting Research** | The informative evidence base behind normative recommendations ([research/](../research/README.md)) |

### 2.2 Out of Scope

Consistent with the project's published non-goals:

| Excluded Item | Rationale |
|---------------|-----------|
| **AI model benchmarking** | AIES evaluates *engineering capability in context*, not raw model performance. Model leaderboards age in months; engineering standards must not. |
| **Vendor promotion** | AIES is strictly vendor-neutral. No document names, ranks, or recommends specific AI vendors, models, or products. |
| **Prompt libraries** | Prompts are implementation details of specific tools. AIES treats prompts and context as governed artifact types (ART-13), not as content to publish. |
| **Programming education** | AIES assumes engineering fundamentals. AECT teaches AI Engineering practice, not programming basics. |
| **Replacing adjacent standards** | AIES complements PMBOK, BABOK, TOGAF, ISTQB, OWASP, ISO/IEC 42001, and NIST AI RMF — it does not restate or supersede them (see [Vision §6](VISION.md)). |

## 3. Stakeholders and Intended Audience

| Stakeholder | Interest in AIES |
|-------------|------------------|
| **Enterprise engineering organizations** | Adopt a defensible operating model for AI participation in delivery |
| **CTOs, engineering directors, and managers** | Set policy, measure capability, manage risk and accountability |
| **Enterprise, AI, and software architects** | Design platforms and processes against reference architectures (AEAR) |
| **Platform engineering teams** | Build the internal tooling that enforces gates, envelopes, and audit trails |
| **AI product teams** | Structure human–AI collaboration with clear roles and autonomy levels |
| **Security, risk, and compliance teams** | Obtain traceability, oversight controls, and audit evidence (X01–X07) |
| **QA organizations** | Apply objective evaluation methods to AI-produced artifacts (AESQS) |
| **Individual engineers** | Develop and certify AI Engineering competency (AECT) |
| **Educators and universities** | Base curricula on a recognized body of knowledge (AEBOK) |
| **Regulators and auditors** | Reference a concrete engineering-level control framework beneath general AI governance regimes |
| **Researchers and open source communities** | Contribute evidence and extensions through open governance |

## 4. Success Criteria

Success is measured, not asserted. The project tracks the following criteria toward and beyond the v1.0 release:

| # | Criterion | Measure | Target Horizon |
|---|-----------|---------|----------------|
| SC-1 | **Standards completeness** | All five modules (AEBOK, AESQS, AEOS, AEAR, AECT) reach **Approved** status per the [Review Standard (AIES-STD-06)](standards/review-standard.md) | v1.0 release |
| SC-2 | **Shared foundation stability** | Glossary and Taxonomy pass a full release cycle without breaking changes | v1.0 + 1 cycle |
| SC-3 | **Organizational adoption** | At least **10 organizations** publicly reference AIES in their engineering or governance documentation | Within 12 months of v1.0 |
| SC-4 | **Certification operational** | The AECT certification program is operational: at least one credential examinable, with published syllabus and passing criteria | Within 18 months of v1.0 |
| SC-5 | **Qualification evidence** | At least **5 published case studies** applying AESQS capability scoring to real engineering work | Within 18 months of v1.0 |
| SC-6 | **Contributor health** | Sustained contributions from **3+ independent organizations**; no single organization authors a majority of accepted changes in a release | Every release from v1.0 |
| SC-7 | **Reference alignment** | Documented mappings from AIES to at least ISO/IEC 42001 and NIST AI RMF published as informative annexes | v1.x |

Targets are reviewed each release and adjusted through the governance process; changes to success criteria require an ADR.

## 5. Governance Summary

The project is governed by the model defined in [GOVERNANCE.md](../GOVERNANCE.md). In brief:

- **Consensus over ownership.** No individual contributor owns the standards; engineering consensus drives evolution.
- **Decisions are recorded.** Structural, normative, and shared-vocabulary changes require an Architecture Decision Record ([adr/](../adr/README.md)).
- **Review before ratification.** Documents progress Draft → Review → Approved via peer and engineering review per the [Review Standard (AIES-STD-06)](standards/review-standard.md).
- **Versioned releases.** The standard as a whole follows semantic versioning; breaking changes to Shared standards are treated as breaking for every module.
- **Open participation.** Contribution rules, proposal requirements, and conduct expectations are defined in [CONTRIBUTING.md](../CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).

## 6. Constraints and Assumptions

### 6.1 Constraints

- **C-1 Vendor neutrality is absolute.** No AIES document may name, endorse, or depend on a specific AI vendor, model, or commercial product.
- **C-2 Text-first artifacts.** All standards, diagrams, and templates are maintained as diffable text (Markdown, Mermaid, ASCII) under version control.
- **C-3 English is the normative language** for v0.x and v1.0; translations are informative until formally ratified.
- **C-4 License pending.** Until a license is ratified (CC-BY-SA-4.0 is proposed; see [FAQ](FAQ.md)), redistribution terms are not final.
- **C-5 Volunteer capacity.** The project runs on contributor time; scope and schedule must fit sustainable contribution levels.

### 6.2 Assumptions

- **A-1** AI participation in software engineering will continue to broaden and deepen; demand for governance of that participation will grow, not shrink.
- **A-2** Model capabilities will change rapidly; therefore the standard anchors on *evidence-based qualification and autonomy governance* rather than on capability snapshots.
- **A-3** Organizations will retain human accountability for engineering outcomes for the foreseeable future, consistent with emerging regulation.
- **A-4** Adjacent standards bodies (project management, architecture, testing, security, AI management systems) will continue to evolve; AIES must interoperate rather than compete.

## 7. Risks and Mitigations

| ID | Risk | Impact | Mitigation |
|----|------|--------|------------|
| R-1 | **Vendor capture** — a vendor or vendor-aligned group steers the standard toward its products | Loss of neutrality and credibility; adoption collapse | Constraint C-1 enforced in review; governance requires multi-organization consensus (SC-6); vendor-specific proposals rejected at triage; ADR trail makes influence auditable |
| R-2 | **Standard obsolescence vs. AI pace** — model capabilities outrun the standard's assumptions | Standard perceived as irrelevant or obstructive | Anchor normative content on stable abstractions (autonomy levels, risk tiers, evidence-based qualification) rather than capability snapshots; time-boxed release cadence; taxonomy change control via ADR keeps evolution deliberate but possible |
| R-3 | **Scope creep** — the project drifts into benchmarking, tooling, prompt content, or general AI ethics | Diluted focus, unfinishable backlog | Out-of-scope table (§2.2) is normative for triage; new scope requires a charter revision through an ADR; roadmap gates each module before the next expands |
| R-4 | **Contributor sustainability** — the project depends on too few contributors | Stalled drafts, single-point-of-failure knowledge | Modular architecture allows independent module progress; templates and conventions lower the contribution barrier; SC-6 tracks contributor diversity; governance distributes review authority |
| R-5 | **Fragmented adoption** — organizations adopt terminology but not the normative controls | "AIES-washing" undermines the brand of conformance | AECT certification and AESQS qualification define what conformance means; requirement IDs (`[DOC-ID-RNN]`) make claims checkable; worked examples show full, honest application |
| R-6 | **Regulatory divergence** — jurisdictions impose conflicting obligations on AI in engineering | Adopters cannot satisfy both AIES and local law | AIES sets engineering floors, not legal ceilings; compliance (X03) is a cross-cutting domain that defers to applicable law; mappings to ISO/IEC 42001 and NIST AI RMF (SC-7) ease alignment |

Risks are reviewed each release; material changes to this register are recorded in [CHANGELOG.md](../CHANGELOG.md).

## Related Documents

- [Vision (AIES-DOC-02)](VISION.md)
- [Repository Architecture (AIES-DOC-03)](ARCHITECTURE.md)
- [SDLC Reference (AIES-DOC-04)](SDLC.md)
- [FAQ (AIES-DOC-05)](FAQ.md)
- [Shared Standards (AIES-SHARED-00)](../Shared/README.md)
- [GOVERNANCE.md (AIES-GOV-01)](../GOVERNANCE.md) · [ROADMAP.md](../ROADMAP.md) · [CONTRIBUTING.md](../CONTRIBUTING.md)

## References

None.

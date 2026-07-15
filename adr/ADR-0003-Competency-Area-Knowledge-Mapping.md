# ADR-0003: Competency areas map to knowledge areas by coverage, not bijection

| | |
|---|---|
| **ADR Number** | 0003 |
| **Status** | Accepted |
| **Deciders** | Maintainers; AESQS Module Editor; AEBOK Module Editor |
| **Supersedes** | — |
| **Superseded by** | — |

## Context

[AESQS Competency Framework (AIES-AESQS-CF-01)](../AESQS/competency-framework.md) §1 defined twelve competency areas (CA-01…CA-12) and asserted they are "derived **one-to-one** from the twelve AEBOK knowledge areas," with a *Derived From* column pairing each CA-NN to the identically-numbered AIES-AEBOK-KA-NN, and [AIES-AESQS-CF-01-R02] requiring that one-to-one mapping to be maintained.

That assertion is false as authored. The AESQS competency decomposition and the [AEBOK](../AEBOK/README.md) knowledge-area decomposition are **different partitions of the same body of knowledge**, and the by-number pairing is wrong for five areas:

| CA (competency) | Claimed KA | Actual KA-NN topic on disk |
|-----------------|-----------|----------------------------|
| CA-03 Product & Experience Definition | KA-03 | KA-03 is **Architecture & Design** |
| CA-04 Architecture & Solution Design | KA-04 | KA-04 is **Planning & Work Decomposition** |
| CA-10 Human-AI Collaboration & Oversight | KA-10 | KA-10 is **Context & Knowledge Management** |
| CA-11 Context & Knowledge Engineering | KA-11 | KA-11 is **Human-AI Collaboration & Oversight** |
| CA-12 Governance, Risk & AI Safety | KA-12 | KA-12 is **Evaluation & Continuous Improvement** |

The divergence is structural, not a numbering slip:

- AESQS splits AEBOK's KA-02 (which explicitly scopes "product, UX, and requirements work") into **two** competencies — CA-02 Business & Requirements and CA-03 Product & Experience — because they are qualified as distinct capabilities.
- AESQS folds AEBOK's KA-04 Planning into CA-05 (whose scope is phases P08–P09) and AEBOK's KA-12 Evaluation into CA-06 (Testing, Quality & **Evaluation**).
- AESQS elevates **Governance, Risk & AI Safety** (CA-12) to a first-class competency, though AEBOK carries that knowledge across KA-01, KA-11, and cross-cutting domains X03–X06 rather than in one KA.

So no bijection exists: two CA topics (Product & Experience; Governance/Risk/Safety) have no dedicated KA, and two KA topics (Planning; Evaluation) have no dedicated CA. This is a normative (Class 3) cross-module consistency defect discovered while authoring the platform competency suites, which independently surfaced the mismatch.

## Decision Drivers

- **Truthfulness.** A normative document must not assert a mapping that does not hold.
- **Fitness of each decomposition for its purpose.** Knowledge areas organize *what must be known*; competency areas organize *what is qualified*. These legitimately differ — separating Product/Experience from Business/Requirements, and naming Governance/Risk/Safety as one competency, are sound qualification choices.
- **Traceability.** AESQS assessment items must still trace to AEBOK knowledge; coverage in both directions must be demonstrable.
- **Disruption.** The competency numbers and titles are referenced by the role-competency table, by [AECT](../AECT/README.md), and by the platform's `platform/competencies/CA-NN-*` suites; renaming or renumbering them would ripple widely for no benefit.

## Options Considered

### Option A — Force a true bijection by rewriting the CA set to mirror KA titles

Rename CA-03→Architecture, CA-04→Planning, CA-10→Context, CA-11→Human-AI, CA-12→Evaluation, so CA-NN ≡ KA-NN by number.

- **Pros:** the literal one-to-one rule becomes true; simplest mental model.
- **Cons:** discards the deliberate, better-for-qualification competency decomposition (loses a distinct Product/Experience competency and the first-class Governance/Risk/Safety competency); rewrites five CA titles, the role-competency table semantics, the AECT curriculum mapping, and the topical content of five already-authored platform suites; solves a real modeling need by deleting it.

### Option B — Adopt a coverage mapping; keep the CA decomposition (chosen)

Replace the false "one-to-one by number" with an explicit many-to-many **coverage** relation: each CA declares the KA(s) and cross-cutting domain(s) it primarily draws on; the invariant becomes *every CA traces to ≥1 KA, and every KA is covered by ≥1 CA*.

- **Pros:** honest about the real relationship; preserves both decompositions intact; zero renumbering; no platform-suite churn (suites are keyed by CA number); traceability is stronger and explicit (domains are named, not just KAs).
- **Cons:** loses the appealing simplicity of a bijection; requires amending R01/R02 and the column; readers must accept that CA-NN and KA-NN are not the same axis.

### Option C — Document the discrepancy as known and defer

Leave the mapping, add a note.

- **Pros:** no immediate work.
- **Cons:** leaves a false normative statement (R02) standing; every downstream reader inherits the confusion; violates the project's own consistency standards.

## Decision

Adopt **Option B**. In [AIES-AESQS-CF-01](../AESQS/competency-framework.md):

1. Rewrite the §1 preamble: competency areas are derived from AEBOK knowledge but are a **distinct partition** organized for qualification; the relationship is coverage, not one-to-one by number.
2. Rename the *Derived From* column to **Primarily Draws On** and correct every row to the KA(s) and domain(s) that actually cover the competency's topic.
3. Amend the normative rules: **[AIES-AESQS-CF-01-R02]** now requires the coverage invariant (each CA traces to ≥1 KA; each KA covered by ≥1 CA; changes on either side are Class 3) instead of a bijection.

Competency IDs, titles, the role-competency table, and the platform suite directories are unchanged. The platform `definition.yaml` `derived_from` fields are corrected to match the new mapping (some become lists).

The canonical corrected mapping:

| CA | Competency Area | Primarily Draws On |
|----|-----------------|--------------------|
| CA-01 | AI-Native SDLC Foundations | KA-01 |
| CA-02 | Business & Requirements Analysis with AI | KA-02 |
| CA-03 | Product & Experience Definition with AI | KA-02 (product/UX scope) |
| CA-04 | Architecture & Solution Design | KA-03 |
| CA-05 | AI-Assisted Implementation | KA-04, KA-05 |
| CA-06 | Testing, Quality & Evaluation Engineering | KA-06, KA-12 |
| CA-07 | Security & Privacy Engineering | KA-07 (X01, X02) |
| CA-08 | Delivery & Release Engineering | KA-08 |
| CA-09 | Operations, Observability & Reliability | KA-09 (X13) |
| CA-10 | Human-AI Collaboration & Oversight | KA-11 (X07) |
| CA-11 | Context & Knowledge Engineering | KA-10 (X08, X09) |
| CA-12 | Governance, Risk & AI Safety | KA-01, KA-11 (X03–X06) |

## Consequences

**Positive:**
- The framework states a relationship that is actually true, with coverage demonstrable in both directions.
- Both the knowledge decomposition and the competency decomposition survive, each fit for its purpose.
- No renumbering: the role table, AECT tiers, and platform suites are undisturbed.
- Cross-cutting domains are now explicit in the competency mapping, improving traceability for CA-07, CA-09, CA-10, CA-11, and CA-12.

**Negative (with mitigations):**
- The intuitive "CA-NN = KA-NN" shortcut no longer holds. *Mitigation:* the Primarily Draws On column and this ADR make the real mapping explicit and permanent.
- A coverage relation is looser than a bijection and could drift. *Mitigation:* R02's coverage invariant is checkable — a conformance check can assert every KA is referenced by ≥1 CA and every CA references ≥1 KA.

## Compliance & Verification

- CF-01 §1 shows the corrected column and the amended R02; no occurrence of "one-to-one" mapping between CAs and KAs remains in CF-01.
- Every AEBOK KA-01…KA-12 appears in at least one CA's *Primarily Draws On* cell; every CA cites at least one KA (verifiable by inspection of the §1 table).
- Platform `platform/competencies/CA-NN-*/definition.yaml` `derived_from` values match this ADR's mapping.
- The repository link/anchor check passes.

## Links

- [AESQS Competency Framework (AIES-AESQS-CF-01)](../AESQS/competency-framework.md)
- [AEBOK Knowledge Area Map (AIES-AEBOK-00 §3)](../AEBOK/README.md)
- [GOVERNANCE.md §3–§4 (AIES-GOV-01)](../GOVERNANCE.md)
- [ADR-0002 — Qualification Platform](ADR-0002-Qualification-Platform.md)

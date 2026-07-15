<!--
  AIES ARCHITECTURE DECISION RECORD TEMPLATE
  ==========================================
  Use this template for every ADR. When an ADR is required, how numbers are
  assigned, and how the status lifecycle works are defined in adr/README.md;
  the governance rules that make ADRs mandatory for Class 3 decisions are in
  GOVERNANCE.md §3.

  How to use:
  1. Copy this file to adr/ADR-NNNN-<Short-Title>.md, taking the next free
     number from the index in adr/README.md. Numbers are never reused.
  2. Replace every <placeholder> and delete these instructional comments.
  3. Submit via pull request; the comment window (GOVERNANCE.md §4.1) starts
     only when the ADR is complete.
  4. Once Accepted, the Context / Decision Drivers / Options / Decision
     sections are immutable — a new ADR supersedes, it does not edit.
-->

# ADR-<NNNN>: <Short Decision Title>

<!-- Metadata table is mandatory (see the Metadata Standard,
     docs/standards/metadata-standard.md, AIES-STD-02 — ADRs carry no date
     rows; decision chronology is carried by the pull request record).
     Status is one of: Proposed, Accepted, Superseded. A Superseded ADR MUST
     link to its successor here. -->

| | |
|---|---|
| **ADR** | ADR-<NNNN> |
| **Status** | Proposed <!-- Proposed → Accepted → Superseded --> |
| **Deciders** | <Maintainers/Module Editors who ratified the decision> |
| **Supersedes / Superseded by** | <ADR link, or "—"> |

## Context

<!-- The situation that forces a decision, written so a reader with no
     conversation history understands it: the problem, the constraints, and
     why "do nothing" is not acceptable. State facts, not the solution. -->

<Context text.>

## Decision Drivers

<!-- The forces that the chosen option must satisfy, as a short list. These
     become the criteria against which the options below are weighed. -->

- <Driver 1, e.g. consistency of terminology across modules>
- <Driver 2>
- <Driver 3>

## Options Considered

<!-- List EVERY option seriously considered, including the rejected ones —
     rejected options are the most valuable part of an ADR. Give each option
     honest pros and cons against the decision drivers. -->

### Option A — <name>

<One-sentence description.>

- **Pros:** <advantages>
- **Cons:** <disadvantages>

### Option B — <name>

<One-sentence description.>

- **Pros:** <advantages>
- **Cons:** <disadvantages>

### Option C — <name>

<One-sentence description.>

- **Pros:** <advantages>
- **Cons:** <disadvantages>

## Decision

<!-- The chosen option and the reasoning that connects it to the decision
     drivers. Write in the active voice: "We adopt Option C because…". -->

<Decision text.>

## Consequences

<!-- Both directions, honestly. Every negative consequence SHOULD name its
     mitigation. Consequences are predictions — they may be revisited by a
     superseding ADR if they prove wrong. -->

**Positive:**

- <Benefit.>

**Negative:**

- <Cost or risk — mitigation: <how it is contained>.>

## Compliance & Verification

<!-- How the project will know the decision is being followed: what to check,
     where it is checked (review checklist, release checklist, tooling), and
     which documents or requirement IDs encode it normatively. -->

- <Verification point, e.g. "Release checklist step N validates X.">
- <Normative anchor, e.g. "Encoded as [<DOC-ID>-RNN] in <document>.">

## Links

<!-- The pull request that carried the decision, related ADRs, affected
     documents (relative links + Document IDs, per the Writing Standard,
     docs/standards/writing-standard.md, AIES-STD-03), and external
     references. -->

- Pull request: <link or reference>
- Related: [<Document> (<DOC-ID>)](<relative-path>)

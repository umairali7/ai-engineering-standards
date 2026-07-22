# KA-10 — Context & Knowledge Management

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-10 |
| **Status** | Review |
| **Audience** | Engineers · Platform teams |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-10 covers Knowledge Management (X09) as a cross-cutting discipline of AI-native engineering. AI performers know nothing about an organization except what is placed in their context: every convention, invariant, and decision that is not curated into consumable form effectively does not exist for them. This inverts the economics of organizational knowledge — tribal knowledge that humans could absorb over years becomes a hard capability ceiling for agents on day one, while well-curated knowledge becomes instantly available to every performer at once. KA-10 defines how to curate organizational knowledge into context assets (ART-13), assemble them per task, keep them fresh, and manage their lifecycle, so that context is a governed engineering asset rather than an accumulating liability.

## 2. Key Concepts

- **Context assets are engineering artifacts.** Prompts, convention documents, ADR digests, glossaries, golden task sets, and runbook extracts are context assets (ART-13): versioned, owned, change-controlled, and reviewed like source code. An unversioned prompt pasted into a tool is a production dependency with no provenance — invisible to every audit (EV6) and impossible to roll back.
- **Curation is transformation, not collection.** Knowledge written for humans (wikis, chat threads, meeting notes) assumes shared background and tolerates ambiguity; AI consumption requires knowledge that is explicit, self-contained, current, and scoped. Pointing an agent at the raw wiki is collection; producing validated, machine-consumable assets from it is curation — and only curation raises capability.
- **Context assembly is a budget, not a bucket.** For each task, the question is which assets the performer needs — not how much can be included. Irrelevant or redundant context actively degrades output and cost (EV5), so assembly is a selection problem: task-relevant assets, at the right version, within a deliberate budget (see [KA-04](KA-04-planning-decomposition.md) context bundling).
- **Freshness decides whether context helps or harms.** Knowledge decays as the system it describes changes. A stale asset is worse than a missing one: it carries the authority of curation while asserting things that are no longer true, and at agent scale the same stale claim misleads every task that consumes it. Freshness is therefore a tracked property, not an assumption.
- **Knowledge lifecycle: create → validate → version → retire.** An asset is drafted (by humans or AI), validated by someone qualified in its subject matter, versioned and published to the assembly sources agents draw from, reviewed on a cadence, and — when superseded — retired from those sources. Assets that skip validation spread unverified claims; assets that skip retirement become context rot.
- **Knowledge has owners.** The Knowledge Manager (ROLE-12) owns the curation practice: asset standards, lifecycle enforcement, and the health of the context store. Individual assets carry designated owners accountable for their accuracy — ownerless knowledge decays silently until an incident finds it.

## 3. Core Practices

- **Manage context assets under change control.** [AIES-AEBOK-KA-10-R01] Context assets (ART-13) consumed by AI performers in RT2 — Moderate and above work MUST be versioned, MUST have a designated owner, and MUST change only through reviewed, recorded change — not through in-place edits to live prompts or retrieval sources.
- **Make consumption traceable.** [AIES-AEBOK-KA-10-R02] It MUST be possible to determine, for any AI-produced artifact, which context assets and versions were assembled for its production, so that context-induced defects can be traced to their source and corrected once rather than rediscovered per incident (EV6).
- **Track freshness and enforce it at assembly.** [AIES-AEBOK-KA-10-R03] Every context asset MUST carry a validation status and a review-by date; assets past their review-by date MUST be excluded from assembly for RT3 — Significant and above tasks or explicitly flagged to the performer and reviewer.
- **Retire deliberately.** [AIES-AEBOK-KA-10-R04] Superseded or invalidated assets MUST be removed from all assembly sources when retired; retirement is a lifecycle action with a record, not abandonment in place.
- **Close the loop from downstream evidence.** Review rejections, incident findings, and evaluation failures traced to wrong or missing context SHOULD produce corrections to the responsible assets ([KA-12](KA-12-evaluation-improvement.md)); teams SHOULD treat repeated agent misunderstandings as a signal that knowledge needs curation, not that agents need scolding.
- **Protect the store.** Because context assets steer everything agents produce, write access to assembly sources SHOULD be treated as a security-sensitive privilege — see delivery-chain poisoning in [KA-07](KA-07-security.md).

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Context Curation Pipeline** | Knowledge flows through an explicit pipeline — capture → transform for machine consumption → validate → version → publish — instead of accreting informally. See [catalog](../patterns/README.md#pat-05-context-curation-pipeline). |
| **Single Source of Context** | Each fact lives in exactly one owned asset that other assets reference; corrections propagate from one place instead of chasing copies. |
| **Task-Scoped Assembly** | Assembly selects the minimal asset set relevant to the task type and risk tier, at pinned versions, rather than shipping the whole store to every task. |
| **Freshness SLA** | Every asset class carries a review cadence proportional to the volatility of what it describes; the store's stale fraction is a monitored health metric. |
| **Feedback-to-Context Loop** | Production and review findings route to asset owners as correction work items; the context store improves at the rate the organization learns ([KA-12](KA-12-evaluation-improvement.md)). See [catalog](../patterns/README.md#pat-10-feedback-to-context-loop). |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Prompt Sprawl** | Uncontrolled copies of prompts and instructions multiply across tools, repositories, and personal stashes; nobody knows which variant produced what, and improvements never propagate. See [catalog](../patterns/README.md#apat-05-prompt-sprawl). |
| **Context Rot** | The store grows but is never validated or retired; stale and contradictory assets accumulate until curated context misleads more than it grounds. See [catalog](../patterns/README.md#apat-07-context-rot). |
| **Everything-in-Context** | Assembly maximizes volume on the theory that more context is safer; relevance drowns, costs balloon (EV5), and output quality falls while the store looks impressively complete. |
| **Wiki-as-Context** | Raw human-oriented documentation is piped to agents untransformed; ambiguity, stale pages, and internal contradictions are consumed as ground truth. |
| **Ownerless Knowledge** | Assets have no accountable owner (ROLE-12 practice unstaffed); errors found in context have nowhere to go, and every consumer re-discovers the same defects. |

## 6. Competency Expectations

| Level | Expectation in KA-10 |
|-------|----------------------|
| **CL1** | Explains what a context asset is and why freshness matters; uses the context store to bundle standard tasks; reports stale or wrong assets through the correction channel. |
| **CL2** | Independently authors and validates context assets for a team's domain; performs task-scoped assembly for standard work; maintains asset versions and review-by dates. |
| **CL3** | Designs the curation pipeline and assembly strategy for a product area; adjudicates single-source conflicts; leads context-rot remediation; coaches teams on curation-over-collection. |
| **CL4** | Sets organizational knowledge-management policy (X09): asset standards, ownership model, freshness SLAs, store security posture; evaluates the capability return on curation investment portfolio-wide. |

## Related Documents

- ADRs and conventions as consumable context: [KA-03 Architecture & Design (AIES-AEBOK-KA-03 — Knowledge Area — Architecture Design)](KA-03-architecture-design.md); bundling context with routed tasks: [KA-04 Planning & Work Decomposition (AIES-AEBOK-KA-04 — Knowledge Area — Planning and Decomposition)](KA-04-planning-decomposition.md).
- Golden task sets and evaluation rubrics as decaying quality assets: [KA-06 Testing & Quality Engineering (AIES-AEBOK-KA-06 — Knowledge Area — Testing and Quality)](KA-06-testing-quality.md).
- Poisoning and injection risks to the context store: [KA-07 Security Engineering (AIES-AEBOK-KA-07 — Knowledge Area — Security)](KA-07-security.md).
- Feedback loops that keep assets current: [KA-12 Evaluation & Continuous Improvement (AIES-AEBOK-KA-12 — Knowledge Area — Evaluation and Improvement)](KA-12-evaluation-improvement.md); operational knowledge sources: [KA-09 Operations & Observability (AIES-AEBOK-KA-09 — Knowledge Area — Operations and Observability)](KA-09-operations-observability.md).
- Knowledge Manager role (ROLE-12) and staffing: [AIES-AEOS-00 — AEOS — AI Engineering Operating System](../../AEOS/README.md); context-store reference architecture: [AEAR (AIES-AEAR-00 — Reference Architecture)](../../AEAR/README.md); artifact type ART-13: [Taxonomy §7 (AIES-SHARED-02 — Taxonomy)](../../Shared/Taxonomy/README.md#7-artifact-types).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

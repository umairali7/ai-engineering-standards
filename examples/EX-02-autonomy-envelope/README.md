# EX-02 — A Completed Autonomy Envelope Definition for an AI Coding Agent

| | |
|---|---|
| **Document ID** | AIES-EX-02 |
| **Status** | Review |
| **Audience** | Governance officers · Platform teams |

> **This example is informative, not normative.** Nothing here adds to, relaxes, or reinterprets any AIES requirement; where this example and a standard disagree, the standard wins. All organizations, people, products, and systems named below — including **Fieldstone** and its agent **FS-AGENT-ENG-01** — are fictional. No real AI vendor, model, or product is named or implied.

---

## 1. What This Example Shows

An **agent definition (ART-14, [Taxonomy §7](../../Shared/Taxonomy/README.md#7-artifact-types))** as it exists in Fieldstone's agent registry: the versioned specification of the agent's role, capabilities, tools, autonomy, guardrails, and escalation rules, per the [Glossary definition of Agent Definition](../../Shared/Glossary/README.md#a). Its centerpiece is the **autonomy envelope** — "the bounded set of actions, resources, and decisions an agent may take without escalation" ([Glossary](../../Shared/Glossary/README.md#a)) — realized as concrete tables rather than prose intentions, per [PAT-01 Bounded Autonomy Envelope](../../AEBOK/patterns/README.md#pat-01-bounded-autonomy-envelope).

Fieldstone's backlog and its risk tiers are established in [EX-01](../EX-01-risk-tiering-backlog/README.md); this document is the artifact that determines what FS-AGENT-ENG-01 may actually do with the items routed to it there. Each section closes with a **Satisfies** note naming the clause(s) it implements.

The record below is maintained as code in Fieldstone's governance repository (`governance/agents/FS-AGENT-ENG-01/definition.md`, mirrored to the registry); it is rendered here in full.

---

## 2. The Registry Record

### 2.1 Identity and Version

| Field | Value |
|-------|-------|
| Agent definition ID | **FS-AGENT-ENG-01** |
| Definition version | **1.4.0** (2026-06-24) |
| Status | Active |
| Sponsor / definition owner (human) | Marcus Adeyemi, Engineering Platform Lead |
| Accountable human for outcomes | Named per work item at intake, per [AIES-AEOS-OM-01-R01](../../AEOS/operating-model.md#1-principles) |
| Role staffed | ROLE-06 Software Engineer ([Taxonomy §5](../../Shared/Taxonomy/README.md#5-ai-engineering-roles)), agent or pair mode |
| Change control | Definition changes are RT2 work minimum; changes that widen the envelope require ROLE-14 approval (see §2.6) |
| Version recording | Every action records the definition version in effect |

**Satisfies:** [AIES-AEOS-OM-01-R20](../../AEOS/operating-model.md#6-artifact-and-provenance-requirements) (agent definitions versioned; every action records the version); [AIES-AEOS-OM-01-R01](../../AEOS/operating-model.md#1-principles) (named accountable human).

### 2.2 Qualification and Scope

FS-AGENT-ENG-01 is qualified under AESQS qualification record **QR-2026-018**, held in Fieldstone's qualification registry per [AIES-AESQS-QP-01-R14](../../AESQS/qualification-process.md#6-granting-and-registration):

| Field | Value |
|-------|-------|
| Qualification record | **QR-2026-018** |
| Subject | FS-AGENT-ENG-01 (definition series 1.4.x; material definition change triggers re-assessment) |
| Sponsor | Marcus Adeyemi (AI systems never self-sponsor, per [AIES-AESQS-QP-01 §2](../../AESQS/qualification-process.md)) |
| Scope | ROLE-06 × P09 × **RT1–RT2** |
| Qualified task types | Feature implementation behind review; defect fixes; test authoring; mechanical refactoring |
| Competency areas | **CA-05 AI-Assisted Implementation: CL2**; CA-01 and CA-10 at CL2 (universal co-requisites per [AIES-AESQS-CF-01-R03](../../AESQS/competency-framework.md)) |
| Evidence basis | 34 scored evidence items (RT2 minimum for AI systems is 30, per [AIES-AESQS-CS-01-R10](../../AESQS/capability-scoring.md#6-statistical-requirements)), incl. golden-task suite FS-GOLD-ENG-04 with repeated runs; aggregate A = 2.87 at RT2 weights, all RT2 minimum gates passed on lower-bound decision values |
| Earned autonomy cap | **AL2** — CL2 earns at most AL2 per [AIES-AESQS-CS-01 §5](../../AESQS/capability-scoring.md#5-thresholds-scores--autonomy-levels-ai-systems); granted AL = min(risk-tier cap, earned cap) per [AIES-AESQS-CS-01-R09](../../AESQS/capability-scoring.md#5-thresholds-scores--autonomy-levels-ai-systems) |
| Granted | 2026-05-18, by Fieldstone's qualification authority (assessor: J. Lindqvist; independent peer reviewer: A. Torres — two distinct humans per [AIES-AESQS-QP-01-R01](../../AESQS/qualification-process.md)) |
| Validity | 12 months; ongoing drift monitoring per §2.7 below |

Operationally: within this envelope the agent works at **AL2 (Collaborative)** — it produces changes; a human reviews every output before it takes effect ([Taxonomy §3](../../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4)). For RT3+ work items it may participate only as AL1 assistance in a pair, because its qualification scope stops at RT2 ([AIES-AEOS-OM-01-R09](../../AEOS/operating-model.md#4-staffing-decision-procedure)).

**Satisfies:** [AIES-AEOS-OM-01-R09](../../AEOS/operating-model.md#4-staffing-decision-procedure) (qualification covering role, task type, and risk tier); [AIES-AEOS-OM-01-R03](../../AEOS/operating-model.md#1-principles) (grants cite current AESQS evidence, revocable); [AIES-SHARED-02-R02/R03](../../Shared/Taxonomy/README.md#3-autonomy-levels-al0al4).

### 2.3 The Autonomy Envelope

#### 2.3.1 Permitted Actions

| # | Permitted action | Scope and conditions |
|---|------------------|----------------------|
| P1 | Read and edit source code | The `fieldstone-platform` monorepo (`services/`, `apps/`, `docs/`) and `fieldstone/internal-tools` only, excluding the protected paths in X1–X4 below |
| P2 | Create branches and commits | Branch namespace `agent/fs-eng-01/*` only; commits stamped with agent ID, definition version, AL, and work-item ID |
| P3 | Open pull requests (ART-06) | Draft PRs against `main`; the agent never merges, approves, or dismisses reviews — human review of every output is what AL2 means |
| P4 | Run builds, linters, and test suites | Ephemeral CI sandbox only, on synthetic fixture data (see data boundaries) |
| P5 | Read context assets (ART-13) | From the context registry, by pinned version; versions consumed are recorded per action |
| P6 | Read and comment on assigned work items (ART-05) | Assigned items only; comments are advisory, never state-changing |

#### 2.3.2 Prohibited Actions

Everything not listed in P1–P6 is outside the envelope and escalates (§2.4). The following are additionally named because they are the requests most likely to arise mid-task:

| # | Prohibited action | Rationale (tiers per [EX-01](../EX-01-risk-tiering-backlog/README.md)) |
|---|-------------------|--------------------------------------------------------------------------|
| X1 | Database schema migrations (`db/migrations/**` in any repo) | Schema changes are RT3 ([Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)); outside qualification scope |
| X2 | Any write under `services/billing/src/payments/**` or `services/identity/**` | Payment and auth code paths are RT3–RT4 (EX-01 items FS-2602, FS-2611) |
| X3 | Access to production systems or production data | No production credentials are issued to the agent at all |
| X4 | Access to secrets, key material, or credential stores | Includes the signing keys of EX-01 FS-2609 |
| X5 | Adding or upgrading dependencies (package manifests, lockfiles) | Escalation E4 required; supply-chain review is human work |
| X6 | Force-push, history rewrite, tag creation, branch deletion outside `agent/fs-eng-01/*` | Irreversibility |
| X7 | Modifying CI/CD pipeline definitions (ART-09), guardrail configurations, or this agent definition | Guardrail changes are RT3 minimum per [AIES-AEOS-GOV-01-R14](../../AEOS/governance-operations.md#5-guardrail-management); self-modification is never in envelope |
| X8 | Writing to the audit store | The audit store must not be writable by the agents it records, per [AIES-AEOS-GOV-01-R06](../../AEOS/governance-operations.md#3-audit-trail-requirements) |

#### 2.3.3 Resource Limits

| Limit | Value | Behavior at limit |
|-------|-------|-------------------|
| Model-token budget per task | 4,000,000 tokens | Warn at 80%; hard stop and escalate (E1) at 100% |
| Wall-clock per task | 3 hours active execution | Hard stop and escalate (E1) |
| PR size | ≤ 400 changed lines (excl. lockfiles/generated) | PR creation blocked; agent must split the change — keeps review load within the review budget planned per [KA-04](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md#3-core-practices) |
| Bulk-write batch size | ≤ 200 records per operation | Operation rejected; agent splits the batch |
| Concurrent work items | ≤ 2 | Additional assignments queue |
| CI sandbox compute | 8 vCPU-hours per task | Hard stop and escalate (E1) |
| Tool-invocation rate | ≤ 30 calls/minute | Throttled |

#### 2.3.4 Data Boundaries

| Boundary | Enforcement point |
|----------|-------------------|
| No access to customer PII stores (customer DB, support records, device-to-customer mappings) | Not on the agent's credential scope; egress filter |
| No access to payment data or payment code paths (RT4 per EX-01 FS-2602) | Repo ACL (X2) + data-store ACL |
| No production telemetry containing customer identifiers | Sandbox is provisioned only with synthetic fixture set FS-FIXTURES-03 |
| Network egress restricted to allowlist: VCS, CI service, context registry, work-item tracker | Egress proxy allowlist; all other destinations blocked |

**Satisfies:** [PAT-01 Bounded Autonomy Envelope](../../AEBOK/patterns/README.md#pat-01-bounded-autonomy-envelope); [AIES-AEOS-OM-01 §5 step 4](../../AEOS/operating-model.md#5-autonomy-assignment) (envelope records permitted actions, resources, decision scope, applicable gates); [AIES-AEOS-OM-01-R02](../../AEOS/operating-model.md#1-principles).

### 2.4 Escalation Triggers and Targets

Escalation paths are defined here, before the agent works — a task with no reachable escalation target must not proceed above AL1 ([AIES-AEOS-OM-01-R23](../../AEOS/operating-model.md#7-escalation-model)).

| # | Trigger | Detected by | Escalates to | Expected response |
|---|---------|-------------|--------------|-------------------|
| E1 | **Envelope edge** — task requires any action in X1–X8 or exceeds a §2.3.3 limit | Guardrail (external), plus agent self-report | ROLE-13 Human Approver (gate roster for the owning repo) | Approve as recorded one-off, extend envelope via the grant procedure, or reassign — per [AIES-AEOS-OM-01 §7](../../AEOS/operating-model.md#7-escalation-model) |
| E2 | **Low confidence** — agent self-assesses it cannot meet the acceptance criteria with available context | Agent self-report; evaluator flag | Pair engineer (ROLE-06 human named on the work item) | Supply context, take over, or split the task |
| E3 | **Golden-task failure** — suite FS-GOLD-ENG-04 fails after any change to the agent's context assets or configuration | CI gate ([PAT-06](../../AEBOK/patterns/README.md#pat-06-golden-task-regression)) | Marcus Adeyemi (sponsor) + ROLE-14 | Agent's task intake suspended until suite is green |
| E4 | **Ambiguous requirements** — work item lacks explicit acceptance criteria and verification method ([AIES-AEBOK-KA-04-R02](../../AEBOK/knowledge-areas/KA-04-planning-decomposition.md#3-core-practices)), or a dependency addition (X5) appears necessary | Agent pre-flight check | ROLE-01 Planner (item returned) or pair engineer | Task is not started until criteria exist |

Every escalation produces an audit record with trigger, context, receiving human, decision, and rationale ([AIES-AEOS-OM-01-R22](../../AEOS/operating-model.md#7-escalation-model)); escalation rates are tracked as operating metrics per [AIES-AEOS-GOV-01 §8](../../AEOS/governance-operations.md#8-metrics).

**Satisfies:** [AIES-AEOS-OM-01-R21–R24](../../AEOS/operating-model.md#7-escalation-model).

### 2.5 Guardrail Enforcement Notes

Per the [Glossary](../../Shared/Glossary/README.md#g), a **guardrail** prevents a class of action *regardless of the agent's instructions* and is **enforced outside the model**. Instructions inside the agent's prompt or this definition's prose are policy inputs, not guardrails, and are not counted as enforcement ([AIES-AEOS-GOV-01-R12](../../AEOS/governance-operations.md#5-guardrail-management)). The table records where each envelope limit is actually enforced:

| Envelope limit | Enforcing guardrail | Enforcement point (outside the model) |
|----------------|---------------------|---------------------------------------|
| P1/X1/X2 repo and path scope | VCS access-control lists + protected-path rules | Version-control platform |
| P2/X6 branch namespace, no force-push | Branch protection + push-rule policy | Version-control platform |
| P3 no merge/approve | Repo permission role: agent identity holds no merge or review-approval rights | Version-control platform |
| X3/X4 no production, no secrets | Credential scoping: the agent's identity is simply never issued those credentials | Identity provider / secrets manager |
| X5 dependency freeze | Manifest/lockfile diff blocker on agent-authored PRs | CI pipeline check |
| X8 audit store read-only | Store-level write ACL excluding all governed agent identities | Audit platform |
| §2.3.3 token/time/compute budgets | Per-task metering with hard cutoffs | Agent orchestration platform |
| §2.3.4 egress allowlist | Egress proxy | Network layer |

Guardrails are managed as code: versioned, reviewed, and covered by executable tests (suite `guardrail-tests/fs-agent-eng-01/`) run on every guardrail change and monthly, with results recorded as evidence ([AIES-AEOS-GOV-01-R13](../../AEOS/governance-operations.md#5-guardrail-management)). A failed guardrail test or detected bypass suspends the autonomy grants relying on it ([AIES-AEOS-GOV-01-R15](../../AEOS/governance-operations.md#5-guardrail-management)). Note: external guardrail enforcement is *mandatory* only at AL3/AL4 ([AIES-AEOS-GOV-01-R12](../../AEOS/governance-operations.md#5-guardrail-management)); Fieldstone enforces it already at AL2 so that a future promotion to AL3 changes the grant, not the architecture.

**Satisfies:** [AIES-AEOS-GOV-01-R12–R15](../../AEOS/governance-operations.md#5-guardrail-management); Glossary definition of Guardrail.

### 2.6 Telemetry and Audit Hooks

Every agent action emits an audit trail record (ART-15) with the following fields, mapped to [AIES-AEOS-GOV-01-R04](../../AEOS/governance-operations.md#3-audit-trail-requirements):

| ART-15 field group | Recorded for FS-AGENT-ENG-01 |
|--------------------|------------------------------|
| Actor identity | `FS-AGENT-ENG-01` + definition version (e.g., `1.4.0`) + accountable human from the work item |
| Autonomy context | Declared AL (AL2, or AL1 in pair mode), work-item risk tier, envelope version in effect |
| Inputs | Work-item ID; context-asset IDs and versions (ART-13); qualification record `QR-2026-018` |
| Tools invoked | Each tool call with parameters sufficient to reconstruct the action (file paths, commands, diffs by hash) |
| Outputs | Commits/PRs by reference and version; CI run IDs; side effects (none permitted outside VCS/CI) |
| Approvals | Gate decisions, escalations E1–E4, overrides and halts, each with deciding human and rationale |

Records are append-only and tamper-evident; the store answers the standard queries of [AIES-AEOS-GOV-01-R08](../../AEOS/governance-operations.md#3-audit-trail-requirements) (all actions by this agent in a period, all actions under a given grant, all uses of a given definition version) without bespoke engineering. Production outputs are continuously sampled and scored on EV1–EV6 as the qualification's ongoing-verification stream ([AIES-AESQS-CS-01-R14](../../AESQS/capability-scoring.md#7-score-decay-and-drift-monitoring)).

**Satisfies:** [AIES-AEOS-GOV-01-R04, R06, R08](../../AEOS/governance-operations.md#3-audit-trail-requirements); [AIES-AEOS-OM-01-R17, R18](../../AEOS/operating-model.md#6-artifact-and-provenance-requirements); [PAT-04 Provenance-First Change](../../AEBOK/patterns/README.md#pat-04-provenance-first-change).

### 2.7 Review and Renewal Schedule

| Event | Cadence / date | Owner |
|-------|----------------|-------|
| Autonomy grant review | **2026-11-18** (6-month review; grant lapses to AL1 if the review does not occur, per [AIES-AEOS-OM-01-R14](../../AEOS/operating-model.md#5-autonomy-assignment)) | ROLE-13 granting approver |
| Envelope reconciliation (declared vs. actual autonomy, escalation and one-off approval patterns) | Quarterly, within the governance review of [AIES-AEOS-GOV-01-R20](../../AEOS/governance-operations.md#7-periodic-governance-reviews) | Priya Raman (ROLE-14) |
| Guardrail test suite | Monthly + on every guardrail change ([AIES-AEOS-GOV-01-R13](../../AEOS/governance-operations.md#5-guardrail-management)) | Platform team |
| Qualification drift monitoring | Rolling window per [AIES-AESQS-CS-01-R15](../../AESQS/capability-scoring.md#7-score-decay-and-drift-monitoring); sustained drift triggers re-qualification | Qualification authority |
| Qualification renewal | By 2027-05-18 ([AIES-AESQS-QP-01 §7](../../AESQS/qualification-process.md#7-validity-and-re-qualification)) | Sponsor + qualification authority |
| Unilateral demotion | Any time — any human with role authority may lower the effective AL without approval ([AIES-AEOS-OM-01-R16](../../AEOS/operating-model.md#5-autonomy-assignment)) | Any role-authorized human |

**Satisfies:** [AIES-AEOS-OM-01-R14, R16](../../AEOS/operating-model.md#5-autonomy-assignment); [AIES-AEOS-GOV-01-R20](../../AEOS/governance-operations.md#7-periodic-governance-reviews).

---

## 3. Common Mistakes This Definition Avoids

- **[APAT-01 Unbounded Agent](../../AEBOK/patterns/README.md#apat-01-unbounded-agent).** Without §2.3, the agent's real authority would be whatever its platform credentials happen to permit — discovered during the incident it causes. Here the envelope was declared first and the credentials were derived *from* it (§2.5), not the reverse.
- **[APAT-03 Autonomy Creep](../../AEBOK/patterns/README.md#apat-03-autonomy-creep).** Convenience-driven exceptions ("just this once, let it bump the dependency") are the classic widening path. Every one-off approval is an E1 escalation on the audit trail, the grant carries a lapse-to-AL1 expiry (§2.7), and the quarterly reconciliation compares declared with actual autonomy — so creep either becomes a recorded decision or gets rolled back.
- **[APAT-02 Review Theater](../../AEBOK/patterns/README.md#apat-02-review-theater).** The 400-line PR cap and the two-item concurrency limit size the agent's output to fit real human review capacity, so AL2's "human reviews every output" stays a control rather than a click-through.
- **[APAT-09 Vendor Lock-in by Convenience](../../AEBOK/patterns/README.md#apat-09-vendor-lock-in-by-convenience).** The envelope is expressed in taxonomy terms (AL/RT/ROLE/ART) owned by Fieldstone; the VCS rules, egress proxy config, and orchestration budgets of §2.5 are replaceable projections of this document, not the policy itself.

## Related Documents

- [Shared Glossary (AIES-SHARED-01)](../../Shared/Glossary/README.md) — Agent Definition, Autonomy Envelope, Guardrail, Escalation
- [Taxonomy (AIES-SHARED-02)](../../Shared/Taxonomy/README.md) — §3 autonomy levels, §4 risk tiers, §5 roles, §7 artifact types
- [AEOS Operating Model (AIES-AEOS-OM-01)](../../AEOS/operating-model.md) — R01–R03, R09, R13–R24
- [AEOS Governance Operations (AIES-AEOS-GOV-01)](../../AEOS/governance-operations.md) — §3 audit trail, §5 guardrail management, §7 reviews
- [AESQS Qualification Process (AIES-AESQS-QP-01)](../../AESQS/qualification-process.md) and [Capability Scoring (AIES-AESQS-CS-01)](../../AESQS/capability-scoring.md) — qualification record, CL→AL thresholds, drift monitoring
- [AEBOK Pattern Catalog (AIES-AEBOK-PAT-00)](../../AEBOK/patterns/README.md) — PAT-01, PAT-04, PAT-06; APAT-01, APAT-02, APAT-03, APAT-09
- [EX-01 — Risk-Tiering a Real Product Backlog](../EX-01-risk-tiering-backlog/README.md) — the tiers this envelope's boundaries reference

## References

None.

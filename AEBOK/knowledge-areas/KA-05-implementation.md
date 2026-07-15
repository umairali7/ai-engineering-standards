# KA-05 — AI-Assisted Implementation

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-05 |
| **Status** | Review |
| **Audience** | Engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-05 covers Engineering (P09): producing source change (ART-06) with AI participation, from AL1 suggestion through AL3/AL4 delegated implementation. It is the highest-volume AI touchpoint in most organizations and the place where the economics of KA-01 bite hardest: generation is cheap, review is the bottleneck, and errors are plausible. KA-05 defines the disciplines — specification, generation practice, review, and provenance — that keep AI-produced code an asset rather than an unaudited liability accumulating in the codebase.

## 2. Key Concepts

- **Specification quality bounds output quality.** An AI implementer optimizes toward the stated task. Ambiguity is resolved by statistical plausibility — what similar code usually does — not by your system's actual intent. The work item's acceptance criteria and bundled context ([KA-04](KA-04-planning-decomposition.md), [KA-10](KA-10-context-knowledge.md)) are therefore part of the implementation, not paperwork around it.
- **Review is a different skill against AI code.** Human-written code fails in human ways (off-by-one, missed edge case, fatigue). AI-produced code fails *plausibly*: idiomatic, well-commented, confidently wrong — subtly mismatched to requirements, referencing nonexistent APIs, importing an almost-right dependency, or silently changing behavior outside the task's scope. Reviewers must verify *against intent and evidence*, not against surface quality. Surface polish carries zero evidential weight.
- **Provenance of source change.** Every change (ART-06) has recorded provenance: which actor produced it, at what autonomy level, from what task, with which approvals. Provenance is what makes later questions answerable — "which changes did agent X make under the old guardrails?" — and is the substrate of audit (ART-15) and traceability (EV6).
- **Scope discipline.** Agents fix what they see. Unrequested "improvements" bundled into a change defeat tier classification (the drive-by refactor of auth code inside an RT2 task is an RT3 change that skipped its gate) and bloat review. Change scope must match task scope.
- **Comprehension debt.** Code merged without any human understanding it is debt measured in future incident response time. Organizations need to decide deliberately — per risk tier — where "no human understands this yet" is acceptable (RT1 scaffolding, perhaps) and where it never is (RT3+).
- **Verification before review.** Human review is the scarcest verification resource, so it comes last: automated gates (build, tests, static analysis, security scans per [KA-08](KA-08-devops-release.md)) filter first, evaluation criteria second, human judgment last, applied to what machines cannot check — intent match, design fit, risk.

## 3. Core Practices

- **Ground every generation task.** Supply agents with the task's acceptance criteria and relevant context assets (conventions, ADRs, interface contracts) at generation time; ungrounded generation produces the *typical* solution, not *your* solution.
- **Enforce human review by risk tier.** [AIES-AEBOK-KA-05-R01] AI-produced source change MUST be reviewed by a qualified human before merge for all RT2+ changes, per the autonomy ceilings in [Taxonomy §4](../../Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4); at AL3, checkpoint-and-sampling review MUST follow the sampling regime defined for the task type (see [KA-11](KA-11-human-ai-collaboration.md)).
- **Record provenance on every change.** [AIES-AEBOK-KA-05-R02] Every commit or change set MUST carry machine-readable provenance identifying the producing actor (human, pair, or agent identity per ART-14), the autonomy level, and the originating work item (ART-05).
- **Keep changes scope-bound.** [AIES-AEBOK-KA-05-R03] An AI-produced change MUST be limited to the scope of its work item; out-of-scope modifications MUST be either removed or split into separately classified and routed work items before merge.
- **Verify dependencies exist and are intended.** [AIES-AEBOK-KA-05-R04] Dependencies introduced by AI-produced changes MUST be verified as real, correctly named, and policy-compliant before merge (defense against hallucinated/squatted packages — see [KA-07](KA-07-security.md)).
- **Review against intent, with evidence.** Reviewers SHOULD begin from the work item's acceptance criteria and the change's test evidence, not from the diff top; a change without accompanying verification evidence SHOULD be returned, not reviewed harder.
- **Preserve comprehension deliberately.** Teams SHOULD maintain per-component human comprehension (rotating reviewers, walkthroughs of significant AI-produced changes) proportional to the component's risk tier.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Spec-Anchored Generation** | Generation always starts from a work item with acceptance criteria and bundled context; the spec, not the conversation, is the source of truth for what was asked. |
| **Provenance-First Change** | Tooling attaches actor, AL, and work-item identifiers to every change automatically; provenance that depends on human diligence decays ([catalog](../patterns/README.md#pat-04-provenance-first-change)). |
| **Layered Verification Funnel** | Automated gates → evaluation criteria → human review, in that order; each layer removes what it is best at so human attention lands on intent and risk. |
| **Scope Diff Check** | An automated comparison of changed surface vs. task scope flags out-of-scope modifications before review. |
| **Human Checkpoint Sampling** | At AL3, humans review a risk-weighted sample of outputs plus all envelope-edge events, with sampling rates tied to the agent's evaluation history ([catalog](../patterns/README.md#pat-08-human-checkpoint-sampling)). |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Review Theater** | Reviews are performed pro forma — approval on green CI and clean style — while intent-level errors flow through; the control exists on paper only ([catalog](../patterns/README.md#apat-02-review-theater)). |
| **Merge-and-Forget** | AI code merges without provenance; a year later nobody can identify which changes an agent made under a since-revoked configuration. |
| **Drive-By Mutation** | Agents bundle unrequested refactors into task changes; risk classification and review budgets silently break. |
| **Conversation-as-Spec** | The task exists only as a chat transcript; intent is unrecoverable, and "what was actually asked" cannot be audited. |
| **Comprehension Bankruptcy** | Sustained merging of ununderstood code into RT3 components; the first serious incident finds no human who can reason about the failing code. |

## 6. Competency Expectations

| Level | Expectation in KA-05 |
|-------|----------------------|
| **CL1** | Uses AI assistance at AL1–AL2 on routine tasks; explains plausibility risk and why AI code review differs from human code review; follows provenance and scope conventions. |
| **CL2** | Independently drives AL2 implementation end to end: grounds tasks, reviews AI-produced changes against intent, dispositions out-of-scope modifications, maintains verification evidence. |
| **CL3** | Supervises AL3 delegation for a component: designs sampling regimes, calibrates reviewers against plausible-error patterns, adjudicates scope and comprehension-debt decisions, coaches CL1–CL2 reviewers. |
| **CL4** | Sets implementation practice organization-wide: provenance tooling standards, review-discipline policy per risk tier, comprehension-debt limits; evolves practice from evaluation and incident data ([KA-12](KA-12-evaluation-improvement.md)). |

## Related Documents

- Task preparation that implementation consumes: [KA-04 Planning & Work Decomposition (AIES-AEBOK-KA-04)](KA-04-planning-decomposition.md).
- Structures that bound implementation blast radius: [KA-03 Architecture & Design (AIES-AEBOK-KA-03)](KA-03-architecture-design.md).
- Verifying what was built: [KA-06 Testing & Quality (AIES-AEBOK-KA-06)](KA-06-testing-quality.md); pipeline enforcement of these rules: [KA-08 DevOps & Release (AIES-AEBOK-KA-08)](KA-08-devops-release.md).
- Threats in the implementation path: [KA-07 Security Engineering (AIES-AEBOK-KA-07)](KA-07-security.md).
- Review ergonomics and sampling design: [KA-11 Human-AI Collaboration & Oversight (AIES-AEBOK-KA-11)](KA-11-human-ai-collaboration.md).
- Engineer role and workflow definitions (ROLE-06): [AEOS (AIES-AEOS-00)](../../AEOS/README.md); implementation capability scoring: [AESQS (AIES-AESQS-00)](../../AESQS/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

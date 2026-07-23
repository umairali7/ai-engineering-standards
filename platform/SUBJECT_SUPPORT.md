# AIES Subject Support Matrix

> Generated from `subject-support-v1.yaml`. Do not edit this matrix manually.

**Implemented** means an executable assessment path ships now. **Experimental** and **planned** entries are not support claims.

| Subject kind | Descriptor kind | Status | Implemented assessment path | Entry point |
|---|---|---|---|---|
| `ai-deployment` — AI Deployment or Served AI System | `ai_deployment` | implemented | Automated Engineering Evaluation<br>Human-Governed Formal Qualification | `aies evaluate`<br>`aies qualify`<br>`aies benchmark` |
| `repository` — Software Repository | `repository` | implemented | Repository Engineering-Practice Conformance Audit | `aies audit` |
| `human` — Human Engineer | `human` | planned | — | — |
| `team` — Engineering Team | `team` | planned | — | — |
| `human-ai-pair` — Human–AI Engineering Pair | `composite` | planned | — | — |
| `ai-agent` — AI Agent | `agent` | planned | — | — |
| `agent-swarm` — Agent Swarm | `agent_swarm` | planned | — | — |
| `mcp-server` — Model Context Protocol Server | `mcp_server` | planned | — | — |
| `coding-assistant` — AI Coding Assistant | `coding_assistant` | planned | — | — |
| `prompt-library` — Prompt Library | `prompt_library` | planned | — | — |
| `rag-system` — Retrieval-Augmented Generation System | `rag_system` | planned | — | — |
| `ai-pipeline` — AI Pipeline | `pipeline` | planned | — | — |
| `ai-platform` — AI Engineering Platform | `platform` | planned | — | — |
| `composite-system` — Composite Engineering System | `composite` | planned | — | — |

## Implemented details

### `ai-deployment` — AI Deployment or Served AI System

**Executor:** `runtime-generation` — Runtime Generation Executor (implemented).

**Evidence adapters:** `inspect-log` — Inspect Evaluation Log Bridge (experimental).

**Decision products:** Engineering Evaluation; Engineering Capability Matrix; Engineering Fit Guidance; Formal Qualification Evidence.

**Limitations:**

- Current executor assesses registered text-generation deployments; it is not a general agent or multimodal-system executor.
- Design-reviewed instruments are not yet empirically calibrated on a representative real-subject panel.

### `repository` — Software Repository

**Executor:** `deterministic-repository-audit` — Deterministic Repository Evidence Collector (implemented).

**Evidence adapters:** `sarif` — SARIF 2.1.0 Findings Bridge (experimental).

**Decision products:** Maturity Scorecard; Evidence Gaps; Ranked Remediation.

**Limitations:**

- Repository maturity is not an AESQS competency score or model capability claim.
- SARIF findings are preserved separately and are not yet consumed by the deterministic audit score.

## Claim boundary

Only entries marked implemented have a shipped assessment path. Experimental contracts and planned architecture are not support claims.

Architecture intent for a subject becomes implemented support only after a Subject Assessment Profile, executor or admitted evidence adapter, direct instruments, limitations, decision products, and discovery entry are executable and validated.

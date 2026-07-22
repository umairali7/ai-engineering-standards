# KA-09 — Operations & Observability

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-09 |
| **Status** | Review |
| **Audience** | Engineers · Platform teams |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-09 covers Operations (P14) and Observability (P15) for AI-inclusive systems — systems where AI participates as a component in production, as a producer of the changes running there, or as an operator acting on the environment. Each participation mode adds an observability surface that pre-AI practice does not instrument: agent activity itself must be telemetered, AI-produced changes must remain attributable after deployment, and autonomy must be a runtime variable that operators can turn down when signals degrade. KA-09 defines how to run such systems so that the question "what is the AI doing, and is it working?" is always answerable from recorded signals — never from reconstruction or trust.

## 2. Key Concepts

- **Two observability surfaces.** AI-native operations observes the *system* (conventional telemetry: latency, errors, saturation) and the *agents acting on it* (what each agent did, under what authority, with what outcome). The second surface is the audit trail (ART-15) treated as live telemetry, not archival paperwork: it is queried during incidents, alerted on, and trended like any other signal.
- **What agent telemetry contains.** For each agent action against a production-relevant environment, the record captures: the acting agent (per its agent definition, ART-14), the declared autonomy level and risk tier, the authorizing work item and approvals, the actions taken and resources touched, the outcome, and any escalations. This is the minimum reconstruction set — what an incident responder needs to answer "who did what, and why was it allowed?" without interviewing anyone.
- **Attribution of AI-produced change.** Production anomalies must be correlatable with the changes that plausibly caused them. Because AI-produced change arrives at volume ([KA-08](KA-08-devops-release.md)), attribution depends on machine-readable provenance surviving deployment: telemetry dimensions that link a misbehaving service version to the source changes (ART-06), producing actors, and gate evidence behind it.
- **Autonomy as a runtime variable.** The autonomy level assigned at planning time is a *ceiling under healthy conditions*. When quality signals degrade — error rates rise, evaluation scores fall ([KA-12](KA-12-evaluation-improvement.md)), escalation rates spike — the operational response is to reduce autonomy (AL3 — Delegated → AL2 — Collaborative → AL1 — Assisted) before, or instead of, disabling capability entirely. Degradation is a designed state transition with defined triggers, not an improvised reaction.
- **Runbooks for agent-involved incidents.** Runbooks (ART-11) written for human-only operations silently assume every actor can be phoned, paused, and reasoned with. Agent-involved incidents add procedures with no pre-AI equivalent: pausing an agent mid-task, containing its in-flight work, revoking autonomy for a task type, and distinguishing "the system is misbehaving" from "an agent is misbehaving."
- **Agents as operators.** AI can also perform operations work — triage, diagnosis, runbook execution. This is engineering work like any other: production-mutating actions have significant blast radius (RT3 — Significant by default), so operational autonomy follows the same tier-derived ceilings as code change, with diagnosis (read-only, RT1 — Minimal through RT2 — Moderate) safely delegable well before remediation is.

## 3. Core Practices

- **Log agent activity as first-class telemetry.** [AIES-AEBOK-KA-09-R01] Every agent action against a production or production-adjacent environment MUST be recorded to the audit trail (ART-15) with the acting agent, autonomy level, risk tier, authorizing work item, actions taken, resources touched, and outcome — sufficient for incident reconstruction without access to the agent's internal state.
- **Keep changes attributable in production.** [AIES-AEBOK-KA-09-R02] Production telemetry (ART-12) MUST support correlating observed anomalies with deployed changes and their provenance records, so that responders can identify the producing actor and gate evidence of a suspect change during an incident, not after it.
- **Design degradation before you need it.** [AIES-AEBOK-KA-09-R03] Every task type operated at AL3 — Delegated+ MUST have defined degradation triggers (telemetry thresholds, evaluation-score floors, escalation-rate limits) and a designated fallback autonomy level; operators MUST be able to reduce an agent's autonomy or pause it entirely without a redeployment.
- **Write runbooks for mixed actors.** [AIES-AEBOK-KA-09-R04] Runbooks (ART-11) for services with agent involvement MUST include agent-specific procedures — pausing, autonomy revocation, containment and disposition of in-flight agent work — and SHOULD be exercised in incident drills, not first opened during an incident.
- **Delegate diagnosis before remediation.** AI assistance in operations SHOULD begin with read-only work (triage, log correlation, hypothesis generation) at AL2 — Collaborative through AL3 — Delegated; production-mutating remediation MUST be classified RT3 — Significant and above and gated accordingly, with pre-approved, tested actions (e.g., initiating a documented rollback) as the only candidates for higher autonomy.
- **Close the loop outward.** Operational signals — degradation events, escalation patterns, incident findings — SHOULD flow to [KA-12](KA-12-evaluation-improvement.md) as evidence for autonomy adjustment and to [KA-10](KA-10-context-knowledge.md) as corrections to context assets.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Agent Activity Ledger** | All agent actions stream to a queryable, alertable ledger (ART-15); incident responders reconstruct agent involvement from records, not recollection. |
| **Degrade-to-Assist** | When health or quality signals cross defined thresholds, agent autonomy steps down automatically (AL3 — Delegated → AL2 — Collaborative → AL1 — Assisted); capability degrades to assistance instead of failing opaque. See [catalog](../patterns/README.md#pat-09-degrade-to-assist). |
| **Provenance-Correlated Monitoring** | Dashboards and alerts carry provenance dimensions, so "which change — and whose — is implicated?" is a query, not an investigation. |
| **Autonomy Kill Switch** | A pre-built, human-operable control pauses a specific agent or task type instantly, independent of deploy pipelines; tested regularly like any other emergency control. |
| **Auto-Rollback Tripwire** | Pre-agreed telemetry thresholds trigger automatic rollback before human diagnosis; shared with [KA-08](KA-08-devops-release.md). |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **Invisible Agent** | Agents act on production with less logging than a human would generate; the first incident becomes archaeology without artifacts. |
| **One-Way Autonomy** | Autonomy was granted with no degradation triggers or fallback level; when quality slips, the only options are "ignore it" or "turn everything off." |
| **Human-Only Runbook** | Incident procedures assume all actors are humans; responders improvise agent containment mid-incident, usually by revoking credentials system-wide. |
| **Silent Remediation** | An agent "fixes" production issues without records or escalation; symptoms disappear, causes accumulate, and the audit trail (EV6) has holes exactly where it matters. |
| **Dashboard Without Provenance** | System telemetry is healthy and mature, but no signal links anomalies to AI-produced changes; attribution at agent-scale volume takes days instead of minutes. |

## 6. Competency Expectations

| Level | Expectation in KA-09 |
|-------|----------------------|
| **CL1** | Explains the two observability surfaces and what an agent activity record contains; reads agent telemetry and audit trails during supervised incident response; follows agent-involved runbook procedures. |
| **CL2** | Independently instruments agent activity for standard services; configures degradation triggers and fallback levels; writes and maintains runbooks covering agent containment. |
| **CL3** | Designs the observability architecture for a product area, including provenance-correlated monitoring and autonomy kill switches; leads agent-involved incident reviews; tunes degradation thresholds from incident data. |
| **CL4** | Sets organizational operational policy for AI-inclusive systems: telemetry standards, degradation doctrine, operational autonomy ceilings; evaluates operational readiness portfolio-wide as autonomy grows. |

## Related Documents

- Where change enters production and rollback machinery lives: [KA-08 DevOps & Release Engineering (AIES-AEBOK-KA-08 — Knowledge Area — DevOps and Release)](KA-08-devops-release.md).
- Instruction-channel and credential risks for operating agents: [KA-07 Security Engineering (AIES-AEBOK-KA-07 — Knowledge Area — Security)](KA-07-security.md).
- Evaluation signals that drive degradation and autonomy adjustment: [KA-12 Evaluation & Continuous Improvement (AIES-AEBOK-KA-12 — Knowledge Area — Evaluation and Improvement)](KA-12-evaluation-improvement.md).
- Runbooks and operational knowledge as curated context assets: [KA-10 Context & Knowledge Management (AIES-AEBOK-KA-10 — Knowledge Area — Context and Knowledge)](KA-10-context-knowledge.md).
- SRE role (ROLE-10) and incident governance: [AIES-AEOS-00 — AEOS — AI Engineering Operating System](../../AEOS/README.md); observability reference architecture: [AEAR (AIES-AEAR-00 — Reference Architecture)](../../AEAR/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

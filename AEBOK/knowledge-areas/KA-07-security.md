# KA-07 — Security Engineering

| | |
|---|---|
| **Document ID** | AIES-AEBOK-KA-07 |
| **Status** | Review |
| **Audience** | Engineers · Security engineers |

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", and "MAY" in this document are to be interpreted as described in RFC 2119.

---

## 1. Purpose

KA-07 covers Security (P11) and the cross-cutting security domain (X01) in AI-native delivery. AI participation changes the security problem in two directions at once. It creates a **new attack surface**: agents with credentials, tool access, and instruction-following behavior are a novel class of privileged, manipulable actor inside the delivery system. And it creates a **new defensive capacity**: AI-assisted threat modeling, code security review, and detection engineering. KA-07 defines the knowledge to secure the AI-native delivery system itself and to use AI competently in security work — while keeping the two concerns distinct.

## 2. Key Concepts

### 2.1 The Agent as Attack Surface

An engineering agent is, from a security standpoint, a privileged automated actor that **treats data as potential instructions**. This single property generates the threat families specific to AI-native delivery:

| Threat family | Mechanism |
|---------------|-----------|
| **Prompt injection (direct & indirect)** | Adversarial instructions embedded in content the agent processes — issue text, code comments, dependency documentation, web content, commit messages — hijack the agent's behavior. Any input channel is an instruction channel. |
| **Delivery-chain poisoning** | Malicious content placed where agents will consume it as context (poisoned context assets, planted "conventions", contaminated retrieval sources) steers generated code toward vulnerable patterns. |
| **Dependency fabrication** | Generated code references plausible-but-nonexistent packages; attackers pre-register those names (slopsquatting) so the hallucination resolves to malware. |
| **Tool and connector abuse** | Agents invoke tools, APIs, plugins, or connector protocols with more authority than the task requires; malicious tool descriptions or retrieved instructions can steer calls toward data exfiltration or unsafe side effects. |
| **Memory and context poisoning** | Long-lived memories, vector indexes, cached summaries, and context assets retain attacker-supplied instructions or false facts and reintroduce them into future tasks. |
| **Secrets exposure to agents** | Credentials visible in an agent's context (environment, files, logs it reads) can be leaked into outputs, commits, or external calls — through error, manipulation, or both. |
| **Excessive agency** | An agent holds broader credentials than its task requires; a manipulated or malfunctioning agent's blast radius equals its permissions, not its intent. |
| **Insecure generated code** | AI reproduces statistically common vulnerable patterns (injection-prone string building, weak crypto defaults, missing authorization checks) with high confidence and volume. |

### 2.2 Core Security Principles Applied to Agents

- **Least privilege per task, not per agent.** Credentials scope to the current work item and its risk zone ([KA-03](KA-03-architecture-design.md)), not to the agent's general usefulness.
- **Guardrails outside the model.** A guardrail (see [Glossary](../../Shared/Glossary/README.md)) is only a guardrail if enforced outside the model — permission systems, network policy, gated pipelines. Instructions to the model ("never delete production data") are behavior-shaping, not controls.
- **Untrusted-input posture.** All content an agent reads that originates outside the trust boundary is treated as adversarial, exactly as web input is treated in application security.
- **Tool descriptions are untrusted input.** Tool schemas, connector metadata, plugin manifests, dependency documentation, and remote API descriptions are data from the security boundary's perspective; they must not be allowed to silently grant authority or rewrite policy.
- **Audit as detection substrate.** The audit trail (ART-15) of agent actions is also the detection dataset: injection attempts, anomalous tool use, and privilege probing appear there first ([KA-09](KA-09-operations-observability.md)).

### 2.3 AI-Assisted Security Work

AI meaningfully assists ROLE-08 in threat-model drafting, security-focused code review at scale, misconfiguration detection, and attack-scenario enumeration — typically at AL1–AL2, because security conclusions are risk acceptances. AI security *findings* are leads; AI security *sign-off* does not exist: security approval is a human act.

## 3. Core Practices

- **Threat-model the delivery system itself.** [AIES-AEBOK-KA-07-R01] Organizations MUST maintain a threat model covering their AI-native delivery system — agents, tools, credentials, context stores, pipelines — as a system under threat, distinct from the products it builds, and MUST revisit it when agent capabilities or autonomy levels change.
- **Scope agent credentials minimally.** [AIES-AEBOK-KA-07-R02] Agent credentials MUST follow least privilege scoped to task and risk zone; long-lived, broadly scoped credentials MUST NOT be issued to agents operating at AL2+.
- **Keep secrets out of agent context.** [AIES-AEBOK-KA-07-R03] Secrets MUST NOT be placed in agent-readable context (prompts, context assets, readable configuration); agents obtain capabilities through brokered, audited mechanisms that never expose the underlying credential.
- **Treat external content as untrusted.** [AIES-AEBOK-KA-07-R04] Content from outside the trust boundary that enters agent context (issues, external docs, retrieved web content, third-party code) MUST be treated as untrusted input; high-consequence tool actions triggered by such content MUST require human confirmation or hard guardrails, per risk tier.
- **Verify dependencies independently of generation.** [AIES-AEBOK-KA-07-R05] Dependency additions in AI-produced changes MUST be validated against an allowlist or registry-verification policy before merge (existence, provenance, known-vulnerability status) — reinforcing [AIES-AEBOK-KA-05-R04](KA-05-implementation.md).
- **Register and mediate tools.** [AIES-AEBOK-KA-07-R06] Agent-accessible tools, plugins, connector servers, and API adapters MUST be approved inventory items with declared capabilities, owners, data classes, and permitted action classes; agents MUST NOT discover or call arbitrary tools outside the governed registry.
- **Expire and re-validate memory.** [AIES-AEBOK-KA-07-R07] Persistent memory, retrieval indexes, cached summaries, and context assets used by agents MUST have provenance, review cadence, and retirement rules; security-relevant or externally influenced entries MUST be re-validated before they can influence RT3+ work.
- **Scan AI-produced code as untrusted by default.** Security scanning (SAST, secret detection, dependency audit) applies to all changes, and findings-thresholds for AI-produced changes SHOULD be at least as strict as for human changes; RT3+ changes touching auth, crypto, or data handling receive human security review regardless of scan results.
- **Use AI to widen security coverage, not to replace judgment.** Teams SHOULD use AI-assisted review to screen the change volume humans cannot cover, routing findings to ROLE-08; AI findings feed human decisions and are never auto-dismissed by another model.

## 4. Patterns

| Pattern | Summary |
|---------|---------|
| **Credential Broker** | Agents never hold raw secrets; a broker issues short-lived, task-scoped capabilities and logs every issuance to the audit trail. |
| **Instruction/Data Separation** | Untrusted content is structurally marked and processed under reduced authority; tool invocations arising from it require elevated confirmation. |
| **Tool Registry and Broker** | Agents call only registered tools through a broker that enforces per-task capability grants, validates parameters, and logs each invocation. |
| **Memory Quarantine** | New or externally influenced memory/context entries stay non-authoritative until validated, classified, and promoted by the knowledge owner. |
| **Two-Model Cross-Check** | Security-relevant outputs are screened by an independent configuration/context; correlated manipulation of both channels is harder. |
| **Dependency Provenance Gate** | Pipeline gate verifies every new dependency's existence, source, and vulnerability status before an AI-produced change can merge. |
| **Honeytoken Canary** | Deliberately planted fake secrets in agent-reachable locations; any use of them is a high-confidence signal of exfiltration or injection success. |

## 5. Anti-Patterns

| Anti-Pattern | Failure Mode |
|--------------|--------------|
| **God-Credential Agent** | One agent identity with organization-wide tokens "to keep things simple"; a single successful injection is a full compromise. |
| **Prompt-as-Policy** | Security controls expressed only as instructions to the model; the first sufficiently clever input overrides them. |
| **Trusted-Because-Internal** | Internal content (tickets, comments, wiki) flows into agent context unsanitized; the trust boundary assumed dissolved the day agents started reading everything. |
| **Tool Autodiscovery in Production** | Agents dynamically connect to unreviewed tools or connector servers; tool metadata becomes an unsupervised authority-escalation path. |
| **Forever Memory** | Agent memory is never expired, quarantined, or revalidated; poisoned context survives long after the original attack is gone. |
| **Scan-and-Ship** | Clean automated scans treated as security approval for RT3+ AI-produced changes; scanners never saw the authorization logic flaw. |
| **Security Findings Firehose** | AI-generated security findings flood human triage without ranking or dedup; real findings drown, and the team learns to ignore the channel. |

## 6. Competency Expectations

| Level | Expectation in KA-07 |
|-------|----------------------|
| **CL1** | Explains prompt injection, slopsquatting, and least-privilege-for-agents; recognizes secrets-in-context violations; follows dependency verification procedure. |
| **CL2** | Independently applies untrusted-input posture to agent workflows; configures task-scoped credentials; triages AI security findings for standard systems. |
| **CL3** | Threat-models AI-native delivery systems; designs guardrail and broker architectures; leads security review of RT3+ AI-produced change; coaches teams on injection-resistant workflow design. |
| **CL4** | Sets organizational security policy for AI participation (X01 across all phases); evaluates residual risk of autonomy expansions; evolves the threat model as attack techniques develop. |

## Related Documents

- Architectural enforcement of risk zones and boundaries: [KA-03 Architecture & Design (AIES-AEBOK-KA-03)](KA-03-architecture-design.md).
- Implementation-side controls this KA reinforces: [KA-05 (AIES-AEBOK-KA-05)](KA-05-implementation.md); pipeline enforcement: [KA-08 DevOps & Release (AIES-AEBOK-KA-08)](KA-08-devops-release.md).
- Detection and audit telemetry: [KA-09 Operations & Observability (AIES-AEBOK-KA-09)](KA-09-operations-observability.md).
- Protecting the context store from poisoning: [KA-10 Context & Knowledge Management (AIES-AEBOK-KA-10)](KA-10-context-knowledge.md).
- Security Engineer role (ROLE-08) and gate authority: [AEOS (AIES-AEOS-00)](../../AEOS/README.md); platform security architecture: [AEAR (AIES-AEAR-00)](../../AEAR/README.md).

## References

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- OWASP GenAI Security Project — 2025 Top 10 for LLMs and GenAI Applications; OWASP Top 10 for Agentic Applications 2026
- NIST AI 600-1 — Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile
- NIST AI 100-2e2025 — Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations (incl. indirect prompt injection, agent memory poisoning, supply-chain attacks)
- MITRE ATLAS — Adversarial Threat Landscape for Artificial-Intelligence Systems (attack tactics & techniques)
- CISA/NCSC — Guidelines for Secure AI System Development
- Standards crosswalk for this area: [Security & supply-chain standards (AIES-DOC-07 §3b)](../../docs/CROSSWALK.md)

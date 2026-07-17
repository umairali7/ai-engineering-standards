# 2026 External Framework Refresh

| | |
|---|---|
| **Document ID** | AIES-RES-01 |
| **Status** | Draft |
| **Audience** | Contributors & maintainers |

## Question

Which AIES documents should be refreshed against current public AI governance,
agentic-security, and generative-AI risk guidance as of 2026-07-17?

## Method

Reviewed high-change external sources most relevant to AI-native software
engineering: NIST AI RMF and NIST AI 600-1, EU AI Act GPAI guidance and Code of
Practice material, OWASP GenAI Security Project materials including the 2025 LLM
Top 10 and 2026 Agentic Applications Top 10, CSA autonomy-level guidance, and the
ASDLC/AI-SDLC autonomy model. This note is an update backlog, not a legal or
certification opinion.

## Findings

1. AIES already aligns well with the industry's shift toward task-scoped
   autonomy, human accountability, auditability, and policy enforced outside the
   model.
2. The largest stale area was not the AL/RT model; it was the security treatment
   of production agentic systems, especially tool/connector abuse, unreviewed
   tool discovery, memory poisoning, and tool-call provenance.
3. The Crosswalk needed to recognize newer operational references: NIST's
   Generative AI Profile, EU GPAI Code of Practice material, and OWASP's
   agentic-specific guidance.
4. The improvement cadence should watch agentic-security frameworks quarterly,
   not only during annual crosswalk refreshes, because the attack taxonomy is
   moving faster than ordinary standards cycles.

## Implications

Immediate updates made:

| Document | Update |
|----------|--------|
| [docs/CROSSWALK.md](../docs/CROSSWALK.md) | Adds NIST AI 600-1, EU GPAI Code material, and OWASP GenAI / Agentic AI security guidance |
| [AEBOK/knowledge-areas/KA-07-security.md](../AEBOK/knowledge-areas/KA-07-security.md) | Adds tool and connector abuse, memory/context poisoning, governed tool registries, and memory re-validation |
| [AEAR/core-reference-architecture.md](../AEAR/core-reference-architecture.md) | Adds governed tool/connector registries, untrusted tool metadata, tool-call inspection, and tool-call provenance |
| [docs/IMPROVEMENT.md](../docs/IMPROVEMENT.md) | Adds quarterly agentic-security watch and trigger-based updates for high-severity new attack patterns |

Recommended next todo list:

| Status | Priority | Todo | Target |
|--------|----------|------|--------|
| Done | P1 | Add CA-07 scenarios for malicious tool metadata and unregistered connector use | `platform/competencies/CA-07-security-privacy-engineering/scenarios/SC-CA07-011.yaml` |
| Done | P1 | Add poisoned persistent memory/context lifecycle scenario | `platform/competencies/CA-11-context-knowledge-engineering/scenarios/SC-CA11-011.yaml` |
| Done | P1 | Add CA-12 governance scenario for external AI Act/GPAI and agentic-security changes | `platform/competencies/CA-12-governance-risk-ai-safety/scenarios/SC-CA12-011.yaml` |
| Done | P1 | Add suite validator and CI gate | `platform/src/aies/suites.py`, `.github/workflows/platform-ci.yml` |
| Open | P2 | Add a short tool-connector example showing a governed registry, task-scoped grants, and tool-call audit records | `examples/` |
| Open | P2 | Expand AEAR cross-cutting concerns with connector supply-chain, schema drift, and third-party tool lifecycle controls | `AEAR/cross-cutting-concerns.md` |
| Open | P2 | Add a compliance-mapping appendix or table for NIST AI 600-1 actions and EU GPAI Code chapters | `docs/CROSSWALK.md` |
| Open | P3 | Revisit role docs for ROLE-08, ROLE-09, ROLE-10, ROLE-12, and ROLE-14 to add connector-specific responsibilities | `AEOS/roles/` |
| Open | P3 | Add AECT learning objectives for agentic tool security and memory governance | `AECT/learning-paths.md`, `AECT/exam-blueprints.md` |

Implemented in this refresh:

| Done | Update |
|------|--------|
| yes | Added one complex integration scenario per competency area (`SC-CA01-011` through `SC-CA12-011`) |
| yes | Added agentic tool-security coverage to CA-07 via `SC-CA07-011` |
| yes | Added external-framework governance response coverage to CA-12 via `SC-CA12-011` |

## References

- NIST AI RMF 1.0 — Artificial Intelligence Risk Management Framework.
- NIST AI 600-1 — Artificial Intelligence Risk Management Framework:
  Generative Artificial Intelligence Profile.
- European Commission — General-Purpose AI Code of Practice and AI Act GPAI
  questions and answers.
- OWASP GenAI Security Project — 2025 Top 10 for LLMs and GenAI Applications.
- OWASP GenAI Security Project — OWASP Top 10 for Agentic Applications 2026.
- Cloud Security Alliance — Levels of Autonomy for Agentic AI.
- ASDLC / AI-SDLC — autonomy levels and framework primer.

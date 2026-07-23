# ADR-0016: Repository Engineering Analysis Layers

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-23 |
| Deciders | Umair Ali (repository owner); Platform Module Editor |
| Scope | Repository assessment evidence, analysis, and decision products |

## Context

`aies audit` originally measured repository-practice maturity from verified,
asserted, and missing evidence. Users also need architecture, code-quality,
correctness-assurance, security, testing, dependency, and remediation views.
Presence of a test directory, scanner, ADR, or lockfile cannot establish that
source is correct, secure, maintainable, or architecturally sound. Conversely,
a static finding must not silently alter practice maturity or an AI deployment
competency score.

## Decision

Separate repository assessment into three independently disclosed layers:

1. **Repository Practice Conformance** retains verified/asserted/gap evidence
   and ML0 — Absent through ML4 — Optimizing maturity. It answers whether
   engineering practices are evidenced and enforced.
2. **Repository Engineering Analysis** observes source structure and retained
   tool artifacts. It reports architecture topology, code-quality signals,
   correctness assurance, security findings, dependency evidence, evidence
   confidence, limitations, and an evidence-linked remediation plan. It does
   not execute repository code by default.
3. **Controlled Repository-Task Benchmarking** remains a future,
   authorization-bounded executor over disposable workspaces. It identifies
   the repository and executing agent as separate subjects and cannot inherit
   claims from either without an explicit mapping.

Repository Engineering Analysis uses the accepted ADR-0015 — Subject and
Evidence Adapter Contracts architecture. Every observation binds to a
content-addressed Repository Subject Descriptor and a declared Evidence
Adapter profile. Retained JUnit, coverage, SARIF, manifest, lockfile, policy,
and configuration artifacts preserve their native meaning. Missing tools are
evidence gaps; successful tools narrow only their declared scope.

Reports must keep the maturity and engineering-analysis layers visually and
semantically separate. No composite grade is emitted. Findings identify
affected artifacts, confidence describes evidence coverage rather than
confidence in repository quality, and every remediation item includes
priority, impact, evidence references, bounded action, acceptance signal,
authority boundary, dependency, reassessment trigger, and command.

## Prohibited claims

- Test presence or a passing retained result does not prove correctness.
- Coverage percentage does not measure test quality.
- An empty scan does not prove security or absence of defects.
- Complexity, coupling, cycles, size, and duplication are review signals, not
  defects without context.
- Repository maturity is not an AESQS deployment competency score.
- Static analysis does not authorize source changes, merges, releases, or
  deployment.

## Consequences

The read-only default remains safe for unfamiliar repositories and suitable
for a first assessment. Language-native execution adapters, controlled task
benchmarks, semantic model review, historical trends, and cross-repository
comparison require separate profiles and compatibility rules. The contracts
remain experimental until their documented compatibility and exit criteria
are satisfied, but the separation and prohibited-claim boundaries are now the
accepted platform architecture.

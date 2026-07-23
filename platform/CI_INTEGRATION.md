# AIES CI Integration

| | |
|---|---|
| **Document ID** | AIES-PLAT-11 |
| **Status** | Draft |
| **Audience** | Repository owners · Platform teams · Security/quality teams |

AIES CI starts by collecting and retaining repository-practice evidence. It
does **not** silently turn findings into a merge gate.

## Recommended onboarding sequence

```text
Advisory evidence → review gaps → approve policy → explicit enforcement
```

### 1. Start advisory

Call the reusable workflow from a repository workflow. Pin both references to
the same reviewed AIES commit:

```yaml
name: AIES repository evidence

on:
  pull_request:
  workflow_dispatch:

jobs:
  aies:
    uses: umairali7/ai-engineering-standards/.github/workflows/aies-advisory.yml@AIES_COMMIT_SHA
    with:
      aies-ref: AIES_COMMIT_SHA
      repository-path: .
      risk-tier: 2
      enforce: false
```

Replace `AIES_COMMIT_SHA` with an immutable commit. Do not copy `main` into a
production gate: a moving evaluator makes retained results irreproducible.

The workflow:

1. checks out the repository under assessment;
2. fetches the pinned AIES source outside that checkout;
3. installs the evaluator;
4. verifies its decision engine against the pinned golden corpus;
5. calculates the RT policy and repository audit;
6. adds notice/warning annotations;
7. writes a GitHub step summary; and
8. retains JSON, Markdown, and annotation artifacts for 30 days.

Missing evidence is visible, but `enforce: false` exits successfully.

### 2. Review before enforcing

Review `aies-repository-evidence` from several representative pull requests.
Decide whether the chosen risk tier, attestation process, and required controls
match the repository. A gap means required evidence was not found; it does not
prove that a practice never occurs.

### 3. Opt in to enforcement

After repository-owner approval:

```yaml
      risk-tier: 2
      enforce: true
```

Only this explicit boolean enables a non-zero exit for policy-required gaps.
Advisory findings outside the selected tier remain visible without changing the
policy result.

## Local equivalent

```bash
aies ci audit . --rt 2 --out aies-ci
```

This writes:

| Artifact | Purpose |
|---|---|
| `repository-assessment.json` | Complete machine-readable audit, policy mode, limitations, and annotations |
| `repository-assessment.md` | Human-readable evidence and ranked recommendations |
| `annotations.json` | Portable notice/warning records |

Preview explicit enforcement locally:

```bash
aies ci audit . --rt 2 --out aies-ci --enforce
```

This command is read-only with respect to repository source and makes no model
or paid endpoint calls.

## Boundaries

- Repository conformance/practice maturity is not source-code correctness,
  architecture fitness, vulnerability absence, or model/agent capability.
- The workflow uses only `contents: read`; it does not post comments, modify
  source, approve changes, or create qualification authority.
- Attested evidence stays distinct from automatically verified evidence.
- Pin the evaluator and preserve artifacts when the result is used in a policy
  decision.
- Use [AIES-PLAT-12 — AIES Container Guide](CONTAINER.md) when container
  isolation is preferred.

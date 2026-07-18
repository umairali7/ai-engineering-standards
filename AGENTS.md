# AI Participation in This Repository

This repository defines a standard for how AI should participate in software
engineering — so it holds itself to that standard. This file states the norms
for AI (agents and assistants) contributing here. It is a governed context asset
(ART-13), versioned like any other, and it is what `aies audit` detects for
CA-11 (Context & Knowledge Engineering).

## Ground rules

- **Provenance.** Every AI-assisted commit records it — a `Co-Authored-By:` (or
  equivalent) trailer on the commit — so change is traceable to its author,
  human and machine (CA-05 / EV6). Never present AI-produced change as untraced.
- **Human accountability.** The platform prepares evidence; a **named human**
  makes every consequential decision — merges, grants, releases (AEOS D8). An
  agent proposes; a person disposes.
- **Risk-tiering.** Match the change to its blast radius: docs/tests are low tier;
  changes to the Shared Taxonomy/Glossary, requirement IDs, or governance are
  **Class 3 / high tier** and need an ADR and human review
  ([GOVERNANCE.md §3](GOVERNANCE.md)).
- **Don't fabricate.** Do not invent APIs, standards citations, requirement IDs,
  or test results. State assumptions and ask for the context you lack rather than
  guessing. Unverified claims are labelled as such.
- **Verify before claiming done.** Run the checks that apply
  (`aies suites validate`, `pytest`, the repo link check) and report failures
  honestly. "Done" means verified, not written.
- **Secrets & safety.** Never commit secrets or real personal data; `.env` is
  git-ignored. Security work stays at the authorization-boundary level — require
  authorization evidence, do not produce operational attack content.

## Working norms

- Keep changes scoped and reviewable; prefer a new commit over amending.
- Match the surrounding code and docs (comment density, naming, conventions).
- Update the relevant docs, `CHANGELOG.md`, and `aies help`/command surface in
  the same change that alters behavior.
- Prefer one canonical checkout with `git pull`; hand-copying files between
  machines has silently reverted committed work here before.

## Self-assessment

This repository can audit its own conformance:

```
aies audit .            # maturity per area, verified/asserted/gap
aies audit . --rt 2     # against RT2's required evidence
```

Contributions should not regress the repo's audit posture; ideally they improve
it. See [platform/SCENARIOS.md](platform/SCENARIOS.md) for authoring scenarios
and [platform/GUIDE.md](platform/GUIDE.md) for running the platform.

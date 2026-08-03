# Security Policy

| | |
|---|---|
| **Document ID** | AIES-GOV-03 |
| **Status** | Review |
| **Audience** | All readers |

AIES is a documentation-first standards repository, so its security surface is narrower than a software project's — but it is not zero, and the standard's content itself can carry security-relevant defects. This policy covers both.

---

## 1. What Counts as a Security Issue in This Repository

Report the following privately (see §2), not as public issues:

- **Credential or secret leaks** — API keys, tokens, internal endpoints, or personal data accidentally committed in examples, research notes, diagrams, or history.
- **Malicious contribution attempts** — PRs or issues attempting to introduce misleading normative guidance, poisoned example configurations, hostile links, or content designed to weaken the standard's safety guidance (e.g., quietly loosening the [autonomy/risk defaults](Shared/Taxonomy/README.md#4-risk-tiers-rt1rt4)).
- **Supply-chain issues in project tooling** — vulnerabilities or tampering in any CI workflows, link checkers, build scripts, or other automation this repository adopts.
- **Account or infrastructure compromise** — suspected takeover of a maintainer account or of repository settings.

Ordinary content defects (wrong facts, unclear requirements, broken links) are **not** security issues — file a public [Errata Report](.github/ISSUE_TEMPLATE/bug_report.md) instead.

## 2. How to Report

- **Preferred:** GitHub **Private Vulnerability Reporting** on this repository ("Report a vulnerability" under the Security tab).
- **Fallback:** email `umair.013@gmail.com`.

Do not disclose the issue publicly, and do not open a public issue or PR that reveals it, until the maintainers confirm remediation or the coordinated disclosure window (§4) elapses.

Include: what you found, where (file, commit, or document ID and section), how you found it, and your assessment of impact. Encrypted reports are welcome once a contact key is published.

## 3. Response Targets

| Step | Target |
|------|--------|
| Acknowledgement of report | 3 business days |
| Triage decision (accepted / not a security issue / duplicate) | 7 calendar days |
| Remediation or mitigation plan communicated | 14 calendar days |
| Fix landed and reporter credited (if desired) | 30 calendar days, severity permitting |

These are targets for a volunteer-run project, not contractual SLAs; critical items (leaked credentials, active malicious content) are handled immediately regardless of targets. Secrets found in history are revoked at the source first — history rewriting alone is never treated as remediation.

## 4. Flaws *in the Standard* — Coordinated Errata

A standards project has a second kind of vulnerability: **a defect in the standard's own guidance** — for example, a recommended guardrail pattern that is bypassable, an escalation flow with an exploitable gap, an audit-trail design that can be forged, or a reference architecture in [AEAR](AEAR/README.md) with an insecure default.

These are treated as **security-sensitive errata** with coordinated disclosure:

1. **Report privately** via the same channel as §2, referencing the Document ID, section, and requirement IDs affected, with a concrete demonstration or argument for the bypass.
2. **Assessment.** Maintainers and the affected Module Editor assess severity: could organizations following the guidance as written be exposed?
3. **Coordinated fix.** A correction is drafted under embargo. Because such fixes usually change normative text, they follow the Class 3 process in [GOVERNANCE.md §3](GOVERNANCE.md#3-decision-classes) — but the public comment period runs on the *corrected* text, and the advisory is published together with the fix rather than before it.
4. **Publication.** The correction ships as errata in the [CHANGELOG](CHANGELOG.md) and a security advisory describing the flawed guidance, affected document versions, and the corrected requirement. Reporters are credited unless they prefer otherwise.
5. **Default embargo window:** 90 days from triage acceptance, negotiable in either direction with the reporter based on real-world exposure.

If you are unsure whether a flaw in the standard is security-sensitive, report it privately — maintainers will reclassify it as a public erratum if it is not.

## 5. Scope Notes

- This policy covers this repository and its official tooling only. Vulnerabilities in third-party products that happen to implement AIES guidance belong with those products' vendors.
- Reference implementations and the qualification platform (Roadmap [Phases 7–8](ROADMAP.md)) will carry their own security policies when they exist; until then, this document is authoritative for the whole project.

## 6. Automated Security Evidence

The repository retains machine-readable security evidence on every push and
pull request and on a weekly schedule:

- **Secret history:** checksum-pinned Gitleaks 8.30.1 scans every reachable
  commit and branch with matched values fully redacted. The one current
  exception is an exact finding fingerprint for a deliberately synthetic token
  in a security assessment instrument; broad file, path, or rule exclusions are
  not used. A match must be treated as potentially real until a human has
  reviewed it, and an exposed credential is revoked before any history repair.
- **Python static analysis:** Ruff 0.15.22 runs its security rules over the
  platform source and scripts. Internal test assertions (`S101`), deliberately
  non-fatal optional discovery (`S110`/`S112`), and fixed argument-vector
  subprocess execution (`S603`/`S607`) remain human-review concerns but are
  excluded from this high-signal automated gate. URL and XML parsing findings
  are not excluded; untrusted endpoints are constrained to HTTP(S), and
  retained XML evidence is parsed with entity-safe tooling.
- **Dependency audit:** pip-audit 2.10.1 resolves the platform's current runtime
  dependencies and records known-vulnerability results. This is a time-bound
  observation of the resolved environment, not proof that future resolutions
  are safe; reproducible lock and release provenance remain release work.

The workflow uploads redacted Gitleaks JSON, SARIF static-analysis output,
dependency-audit JSON, and tool/version/source metadata. Contributors run the
equivalent checks with `aies security`; the repository-owned runner downloads
the exact Gitleaks archive for macOS, Linux, or Windows, verifies the published
SHA-256, and reuses a tamper-checked user-local cache. It does not install or
modify Homebrew, system packages, or `PATH`. The Python security extra supplies
the pinned Ruff and pip-audit commands plus native operating-system certificate
store support for the verified download. GitHub CodeQL default setup and
Private Vulnerability Reporting are repository settings: both remain external
release-readiness controls until a repository administrator enables and tests
them. Security automation finds evidence; it does not certify that the project
is secure.

`make security` is only a compatibility alias for contributors who already use
Make. It is not required on any supported operating system.

## Related Documents

- [AIES-GOV-01 — Governance](GOVERNANCE.md)
- [AIES-GOV-02 — Contributing to AIES](CONTRIBUTING.md)
- [Errata Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- [CHANGELOG.md](CHANGELOG.md)

## References

None.

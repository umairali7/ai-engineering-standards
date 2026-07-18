"""The conformance-audit check set (ADR-0004).

Each `Check` declares its competency area, maturity band, the risk tier at which
it becomes gate-required, and its external-standard mapping. Detectors are
deliberately stack-agnostic (git, CI, dependency, policy, doc, and config
*presence*) — the auditor detects that a practice/tool is in place and maps it
to the external standard; it does not itself scan code (ADR-0004 non-goals).

Coverage (ADR-0004): strong-auto CA-01/05/06/07/08/11; presence+attest
CA-04/09/10/12; attestation-only CA-02/03.
"""

from __future__ import annotations

from .audit import (BAND_ENFORCEMENT, BAND_EXISTENCE, BAND_MEASUREMENT, Check,
                    RepoContext)

# --- small detector helpers ----------------------------------------------------
_CI_GLOBS = (".github/workflows/*", "*.gitlab-ci.yml", "*.yml", "*.yaml",
             "*jenkinsfile*", ".circleci/*", "azure-pipelines*")


def _any_grep(ctx: RepoContext, needles, *globs) -> bool:
    return any(ctx.grep(n, *globs) for n in needles)


def _found(ok: bool, yes: str, no: str) -> tuple[bool, str]:
    return (True, yes) if ok else (False, no)


# --- CA-01 Foundations ---------------------------------------------------------
def _conformance(ctx):
    return _found(ctx.has("conformance"),
                  "a conformance statement/doc is present",
                  "no AIES conformance statement found")


def _adr(ctx):
    return _found(ctx.has("adr/", "/adr/") or ctx.has_glob("*adr-*.md", "*/decisions/*"),
                  "architecture decision records present",
                  "no ADRs / decision records found")


def _risk_policy(ctx):
    return _found(_any_grep(ctx, ("risk tier", "risk-tier", "autonomy level", "blast radius"),
                            "*.md"),
                  "a risk-tier / autonomy policy is documented",
                  "no risk-tier or autonomy policy found")


# --- CA-05 Implementation ------------------------------------------------------
def _provenance(ctx):
    ok = ctx.commits_have("co-authored-by", "assisted-by", "generated with",
                          "ai-assisted", "co-authored") or ctx.has("pull_request_template")
    return _found(ok, "AI/authorship provenance in commits or PR template",
                  "no commit/PR provenance of AI-produced change")


def _pr_template(ctx):
    return _found(ctx.has("pull_request_template"),
                  "a pull-request template is present",
                  "no pull-request template")


# --- CA-06 Testing / Quality ---------------------------------------------------
def _tests_present(ctx):
    return _found(ctx.has("tests/", "/test/", "test_", "_test.", ".test.", ".spec."),
                  "test files/directories present",
                  "no tests detected")


def _ci_test_gate(ctx):
    return _found(_any_grep(ctx, ("pytest", "npm test", "go test", "cargo test",
                                  "run: test", "unittest", "jest", "vitest"), *_CI_GLOBS),
                  "CI runs the test suite",
                  "tests are not run in CI")


def _coverage(ctx):
    ok = ctx.has(".coveragerc", "codecov.yml", "codecov.yaml") or \
        _any_grep(ctx, ("--cov", "coverage", "codecov"), "*.toml", "*.cfg", "*.ini", *_CI_GLOBS)
    return _found(ok, "coverage measurement configured", "no coverage configuration")


# --- CA-07 Security / Privacy --------------------------------------------------
def _dep_manifest(ctx):
    return _found(ctx.has_glob("pyproject.toml", "requirements*.txt", "package.json",
                               "go.mod", "cargo.toml", "pom.xml", "build.gradle*",
                               "gemfile", "composer.json"),
                  "a dependency manifest is present",
                  "no dependency manifest found")


def _dep_lock(ctx):
    return _found(ctx.has_glob("poetry.lock", "package-lock.json", "yarn.lock",
                               "pnpm-lock.yaml", "cargo.lock", "go.sum", "gemfile.lock",
                               "composer.lock", "uv.lock"),
                  "dependencies are pinned (lockfile present)",
                  "no dependency lockfile — dependencies unpinned")


def _secrets_ignored(ctx):
    gi = " ".join(ctx.read(p) for p in ctx.matching(".gitignore")).lower()
    # A gitignored .env present on disk is correct; only a *tracked* .env is a leak.
    committed = ctx.is_tracked(".env") if ctx.is_git else ctx.has_glob(".env", "*/.env")
    return _found(".env" in gi and not committed,
                  ".env is git-ignored and not tracked",
                  "committed .env, or .env not in any .gitignore")


def _secret_scanning(ctx):
    ok = ctx.has("dependabot", "codeql", ".semgrep", ".pre-commit-config") or \
        _any_grep(ctx, ("gitleaks", "trufflehog", "detect-secrets", "semgrep", "codeql",
                        "snyk", "trivy"), *_CI_GLOBS, ".pre-commit-config.yaml")
    return _found(ok, "secret-scanning / SAST / dependency-alert tooling configured",
                  "no secret-scanning or SAST tooling detected")


def _security_policy(ctx):
    return _found(ctx.has("security.md"), "a SECURITY policy is present",
                  "no SECURITY.md")


# --- CA-08 Delivery / Release --------------------------------------------------
def _ci_present(ctx):
    return _found(ctx.has(".github/workflows/", ".gitlab-ci", ".circleci",
                          "jenkinsfile", "azure-pipelines", ".travis"),
                  "a CI/CD pipeline is configured",
                  "no CI/CD pipeline found")


def _sbom(ctx):
    ok = ctx.has("sbom", "cyclonedx", "spdx", ".cdx.") or \
        _any_grep(ctx, ("cyclonedx", "syft", "sbom", "spdx"), *_CI_GLOBS)
    return _found(ok, "an SBOM / AI-BOM is produced or present",
                  "no SBOM / AI-BOM detected")


def _signing(ctx):
    ok = ctx.has("cosign", ".sig", ".sigstore", "model-signing") or \
        _any_grep(ctx, ("cosign", "sigstore", "model-signing", "slsa", "gpg --sign"),
                  *_CI_GLOBS)
    return _found(ok, "artifact/model signing or SLSA provenance configured",
                  "no artifact/model signing detected")


# --- CA-11 Context / Knowledge -------------------------------------------------
def _context_artifacts(ctx):
    ok = ctx.has("claude.md", "agents.md", ".cursorrules", "copilot-instructions",
                 "system_prompt", "system-prompt") or \
        ctx.has_glob("prompts/*", "*.prompt", "*/context/*")
    return _found(ok, "prompt/agent/context assets are versioned in the repo",
                  "no versioned prompt/agent/context assets (ART-13)")


# --- CA-09 Operations ----------------------------------------------------------
def _observability(ctx):
    ok = ctx.has("prometheus", "grafana", "opentelemetry", "otel", "runbook") or \
        _any_grep(ctx, ("logging", "telemetry", "opentelemetry", "metrics"),
                  "*.toml", "*.yaml", "*.yml", "*.py")
    return _found(ok, "observability / runbook configuration present",
                  "no observability or runbook configuration detected")


# --- CA-10 Human-AI Oversight --------------------------------------------------
def _codeowners(ctx):
    return _found(ctx.has("codeowners"),
                  "CODEOWNERS present (required-review proxy)",
                  "no CODEOWNERS / required-review configuration in the repo")


# --- CA-12 Governance / Risk / Safety ------------------------------------------
def _governance_docs(ctx):
    return _found(ctx.has("governance.md", "governance/"),
                  "governance documentation present",
                  "no governance documentation")


def _guardrail_tests(ctx):
    ok = ctx.grep("guardrail", "*.py", "*.md", "*.ts", "*.js") or ctx.has("guardrail")
    return _found(ok, "guardrails referenced/tested in the repo",
                  "no guardrail configuration or tests detected")


def _incident_policy(ctx):
    return _found(ctx.has("incident", "runbook") or ctx.has("security.md"),
                  "incident-response / runbook material present",
                  "no incident-response policy or runbook")


CHECKS = [
    # CA-01 Foundations (strong-auto)
    Check("ca01-conformance", "CA-01", "AIES conformance statement", BAND_EXISTENCE,
          _conformance, external="AIES-DOC-08", required_at="RT2",
          recommendation="Add an AIES conformance statement (`aies conform scaffold`)."),
    Check("ca01-adr", "CA-01", "Architecture decision records", BAND_EXISTENCE,
          _adr, required_at="RT3",
          recommendation="Record significant decisions as ADRs under adr/."),
    Check("ca01-risk-policy", "CA-01", "Risk-tier / autonomy policy", BAND_EXISTENCE,
          _risk_policy, external="Taxonomy RT/AL", required_at="RT3",
          recommendation="Document a risk-tier and autonomy policy for AI participation."),
    # CA-05 Implementation (strong-auto)
    Check("ca05-provenance", "CA-05", "AI-change provenance", BAND_EXISTENCE,
          _provenance, external="EV6 Traceability", required_at="RT2",
          recommendation="Record provenance of AI-produced change (commit trailers / PR template)."),
    Check("ca05-pr-template", "CA-05", "Pull-request template", BAND_EXISTENCE,
          _pr_template, recommendation="Add a PR template capturing assumptions and risk."),
    # CA-06 Testing / Quality (strong-auto)
    Check("ca06-tests", "CA-06", "Tests present", BAND_EXISTENCE, _tests_present,
          external="ISO/IEC 42119", required_at="RT2",
          recommendation="Add a test suite asserting intended behavior."),
    Check("ca06-ci-test-gate", "CA-06", "Tests enforced in CI", BAND_ENFORCEMENT,
          _ci_test_gate, external="ISO/IEC 42119", required_at="RT3",
          recommendation="Run the test suite as a CI gate on every change."),
    Check("ca06-coverage", "CA-06", "Coverage measured", BAND_MEASUREMENT, _coverage,
          recommendation="Measure and track test coverage."),
    # CA-07 Security / Privacy (strong-auto)
    Check("ca07-dep-manifest", "CA-07", "Dependency manifest", BAND_EXISTENCE,
          _dep_manifest, external="OWASP LLM Top 10", required_at="RT2",
          recommendation="Declare dependencies in a manifest."),
    Check("ca07-dep-lock", "CA-07", "Dependencies pinned", BAND_EXISTENCE, _dep_lock,
          external="SLSA / supply-chain", required_at="RT3",
          recommendation="Commit a lockfile so dependencies are pinned."),
    Check("ca07-secrets-ignored", "CA-07", "Secrets not committed", BAND_EXISTENCE,
          _secrets_ignored, external="OWASP LLM Top 10", required_at="RT2",
          recommendation="Git-ignore .env and never commit secrets."),
    Check("ca07-secret-scanning", "CA-07", "Secret-scanning / SAST", BAND_ENFORCEMENT,
          _secret_scanning, external="MITRE ATLAS / CISA-NCSC", required_at="RT3",
          recommendation="Enable secret scanning / SAST / dependency alerts in CI."),
    Check("ca07-security-policy", "CA-07", "Security policy", BAND_EXISTENCE,
          _security_policy, recommendation="Add a SECURITY.md."),
    # CA-08 Delivery / Release (strong-auto)
    Check("ca08-ci", "CA-08", "CI/CD pipeline", BAND_EXISTENCE, _ci_present,
          external="CISA/NCSC Secure AI Dev", required_at="RT2",
          recommendation="Configure a CI/CD pipeline as the enforcement layer."),
    Check("ca08-sbom", "CA-08", "SBOM / AI-BOM", BAND_EXISTENCE, _sbom,
          external="CycloneDX / SPDX", required_at="RT3",
          recommendation="Generate an SBOM / AI-BOM at build/promotion."),
    Check("ca08-signing", "CA-08", "Artifact / model signing", BAND_ENFORCEMENT,
          _signing, external="OpenSSF Model Signing / SLSA",
          recommendation="Sign artifacts/models and verify provenance at promotion."),
    # CA-11 Context / Knowledge (strong-auto)
    Check("ca11-context", "CA-11", "Versioned context assets", BAND_EXISTENCE,
          _context_artifacts, external="ART-13", required_at="RT2",
          recommendation="Version prompts/agent definitions/context as governed assets."),
    # CA-04 Architecture (presence + attest)
    Check("ca04-adr", "CA-04", "Design decisions recorded", BAND_EXISTENCE, _adr,
          recommendation="Record design options and rejected alternatives as ADRs."),
    # CA-09 Operations (presence + attest)
    Check("ca09-observability", "CA-09", "Observability / runbooks", BAND_EXISTENCE,
          _observability, recommendation="Configure observability and incident runbooks."),
    # CA-10 Human-AI Oversight (presence + attest)
    Check("ca10-codeowners", "CA-10", "Required review (CODEOWNERS)", BAND_ENFORCEMENT,
          _codeowners, required_at="RT3",
          recommendation="Add CODEOWNERS and require review on protected branches."),
    Check("ca10-branch-protection", "CA-10", "Branch protection / gate enforcement",
          BAND_ENFORCEMENT, lambda ctx: (False, "not detectable from repo files"),
          auto=False, required_at="RT3",
          recommendation="Attest branch protection / human gate config (not in-repo)."),
    # CA-12 Governance / Risk / Safety (presence + attest)
    Check("ca12-governance", "CA-12", "Governance documentation", BAND_EXISTENCE,
          _governance_docs, recommendation="Document AI governance (policy, roles, reviews)."),
    Check("ca12-guardrail-tests", "CA-12", "Guardrails tested", BAND_ENFORCEMENT,
          _guardrail_tests, external="AEOS GOV-01-R13",
          recommendation="Implement guardrails as code with tests that prove they block."),
    Check("ca12-incident", "CA-12", "Incident-response policy", BAND_EXISTENCE,
          _incident_policy, recommendation="Define an incident-response/runbook process."),
    # CA-02 Requirements (attestation-only)
    Check("ca02-traceability", "CA-02", "Requirements traceability", BAND_EXISTENCE,
          lambda ctx: (False, "not file-detectable"), auto=False,
          recommendation="Attest requirements-to-source traceability with an evidence link."),
    # CA-03 Product / Experience (attestation-only)
    Check("ca03-acceptance", "CA-03", "Testable acceptance criteria", BAND_EXISTENCE,
          lambda ctx: (False, "not file-detectable"), auto=False,
          recommendation="Attest testable acceptance criteria with an evidence link."),
]

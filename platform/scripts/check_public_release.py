#!/usr/bin/env python3
"""Report whether the repository is ready for an open public preview.

The default mode is informational so ordinary development CI can expose the
remaining work without claiming the repository is release-ready. ``--gate``
fails closed when a repository-contained prerequisite is missing or an
external GitHub/release control has not been independently confirmed.

This check never accepts an ADR, grants a license, enables a repository
setting, signs a tag, or treats its own output as human approval.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import re


STATUS_PASS = "pass"  # noqa: S105 - readiness status label, not a credential
BLOCK = "block"
EXTERNAL = "external-verification-required"


@dataclass(frozen=True)
class ReleaseCheck:
    check_id: str
    title: str
    status: str
    evidence: str
    next_action: str


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _check(
    check_id: str,
    title: str,
    passed: bool,
    evidence: str,
    next_action: str,
) -> ReleaseCheck:
    return ReleaseCheck(
        check_id=check_id,
        title=title,
        status=STATUS_PASS if passed else BLOCK,
        evidence=evidence,
        next_action="" if passed else next_action,
    )


def _external(
    check_id: str,
    title: str,
    next_action: str,
    confirmations: dict,
) -> ReleaseCheck:
    confirmation = confirmations.get(check_id)
    if _valid_confirmation(confirmation):
        return ReleaseCheck(
            check_id=check_id,
            title=title,
            status=STATUS_PASS,
            evidence=(
                f"confirmed by {confirmation['verified_by']} at "
                f"{confirmation['verified_at']}: {confirmation['evidence']}"
            ),
            next_action="",
        )
    return ReleaseCheck(
        check_id=check_id,
        title=title,
        status=EXTERNAL,
        evidence="not provable from the tracked repository",
        next_action=next_action,
    )


def _valid_confirmation(value: object) -> bool:
    if not isinstance(value, dict) or value.get("confirmed") is not True:
        return False
    fields_present = all(
        isinstance(value.get(field), str) and value[field].strip()
        for field in ("verified_by", "verified_at", "evidence")
    )
    if not fields_present:
        return False
    try:
        observed_at = datetime.fromisoformat(
            value["verified_at"].replace("Z", "+00:00")
        )
    except ValueError:
        return False
    return observed_at.tzinfo is not None


def load_external_evidence(path: Path | None) -> dict:
    """Load explicit external confirmations; never infer them."""
    if path is None:
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if (
        document.get("kind") != "aies-public-release-external-evidence"
        or document.get("schema_version") != 1
        or not isinstance(document.get("confirmations"), dict)
    ):
        raise ValueError(
            "external evidence must use "
            "aies-public-release-external-evidence schema_version 1"
        )
    return document["confirmations"]


def _package_license(repo: Path) -> str:
    pyproject_text = _text(repo / "platform" / "pyproject.toml")
    match = re.search(
        r'(?m)^\s*license\s*=\s*"([^"]+)"\s*$',
        pyproject_text,
    )
    return match.group(1) if match else ""


def _license_decision_checks(repo: Path) -> list[ReleaseCheck]:
    license_lower = _text(repo / "LICENSE.md").lower()
    adr = _text(
        repo / "adr" / "ADR-0014-Dual-License-Standards-and-Software.md"
    )
    license_effective = (
        "no license has been granted" not in license_lower
        and "all rights are reserved" not in license_lower
        and "cc by-sa 4.0" in license_lower
        and "apache 2.0" in license_lower
    )
    adr_accepted = bool(
        re.search(
            r"\|\s*\*\*Status\*\*\s*\|\s*Accepted\s*\|",
            adr,
            flags=re.IGNORECASE,
        )
    )
    return [
        _check(
            "license-decision",
            "ADR-0014 - Dual-license decision accepted",
            adr_accepted,
            "ADR status is Accepted" if adr_accepted else "ADR status is not Accepted",
            "Complete the Class 3 comment window, dispositions, named decider "
            "record, and human acceptance.",
        ),
        _check(
            "license-effective",
            "Effective open-license notice",
            license_effective,
            "LICENSE.md grants both scoped licenses" if license_effective
            else "LICENSE.md still withholds or does not grant the scoped licenses",
            "After ADR acceptance, replace the pending notice with the "
            "authoritative path-to-license scope table.",
        ),
    ]


def _license_artifact_checks(repo: Path) -> list[ReleaseCheck]:
    license_texts = (
        (repo / "LICENSES" / "CC-BY-SA-4.0.txt").is_file()
        and (repo / "LICENSES" / "Apache-2.0.txt").is_file()
    )
    package_license = _package_license(repo)
    package_license_ready = "Apache-2.0" in package_license
    return [
        _check(
            "license-texts",
            "Official license texts installed",
            license_texts,
            "both scoped license text files present" if license_texts
            else "one or both scoped license text files are absent",
            "Install verbatim CC BY-SA 4.0 and Apache 2.0 texts under LICENSES/.",
        ),
        _check(
            "package-license",
            "Executable package has Apache-2.0 metadata",
            package_license_ready,
            f"project.license={package_license or '<missing>'}",
            "Replace LicenseRef-AIES-Pending only after ADR-0014 is accepted.",
        ),
    ]


def _security_contact_check(repo: Path) -> ReleaseCheck:
    security = _text(repo / "SECURITY.md")
    matches = re.findall(
        r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w-])",
        security,
    )
    example_domains = ("@example.com", "@example.org", "@example.net")
    real_emails = [
        value for value in matches
        if not value.lower().endswith(example_domains)
    ]
    ready = "placeholder" not in security.lower() and bool(real_emails)
    return _check(
        "security-contact",
        "Dedicated security contact published",
        ready,
        "non-placeholder contact present" if ready
        else "SECURITY.md has no non-placeholder dedicated email",
        "Publish the maintainer-approved security address and remove the placeholder.",
    )


def _repository_control_checks(repo: Path) -> list[ReleaseCheck]:
    codeowners = _text(repo / ".github" / "CODEOWNERS")
    dependabot = _text(repo / ".github" / "dependabot.yml")
    workflows = "\n".join(
        _text(path) for path in sorted((repo / ".github" / "workflows").glob("*.y*ml"))
    )
    codeowners_ready = bool(
        codeowners.strip()
        and re.search(r"(?m)^\s*(?!#)\S+\s+@\S+", codeowners)
    )
    dependabot_ready = all(
        value in dependabot for value in (
            "package-ecosystem: github-actions",
            "package-ecosystem: pip",
        )
    )
    scanner = re.search(
        r"(github/codeql-action|gitleaks|trufflehog|detect-secrets|semgrep)",
        workflows,
        flags=re.IGNORECASE,
    )
    return [
        _check(
            "codeowners",
            "CODEOWNERS review routing present",
            codeowners_ready,
            ".github/CODEOWNERS contains an owner rule" if codeowners_ready
            else ".github/CODEOWNERS is absent or has no owner rule",
            "Add owners for the default tree and high-impact governance/release paths.",
        ),
        _check(
            "dependency-updates",
            "Dependency update automation configured",
            dependabot_ready,
            "Dependabot covers GitHub Actions and Python" if dependabot_ready
            else "Dependabot does not cover both GitHub Actions and Python",
            "Add .github/dependabot.yml for actions, Python, and container inputs.",
        ),
        _check(
            "security-automation",
            "Security scanning is represented in CI",
            bool(scanner),
            "security scanner detected in workflow configuration"
            if scanner else "no CodeQL/SAST or dedicated secret scanner detected",
            "Add least-privilege CodeQL/SAST and full-history secret scanning.",
        ),
    ]


def _external_checks(confirmations: dict) -> list[ReleaseCheck]:
    return [
        _external(
            "branch-protection",
            "Protected main branch and required human review",
            "Verify in GitHub that main requires current CI and CODEOWNER/human review.",
            confirmations,
        ),
        _external(
            "private-vulnerability-reporting",
            "GitHub Private Vulnerability Reporting enabled",
            "Enable the repository Security setting and test the private reporting path.",
            confirmations,
        ),
        _external(
            "github-code-scanning",
            "GitHub CodeQL default setup enabled",
            "After public visibility makes it available, enable CodeQL default "
            "setup for Python and retain the first successful scan evidence.",
            confirmations,
        ),
        _external(
            "history-and-actions-review",
            "Full history, Actions logs, and artifacts reviewed",
            "Run a dedicated history scanner, review retained Actions output, and "
            "rotate any exposed credential before changing visibility.",
            confirmations,
        ),
        _external(
            "signed-preview-release",
            "Signed preview tag and immutable release evidence",
            "After the release commit passes, create and independently verify the "
            "signed preview tag, hashes, notes, and generated evidence.",
            confirmations,
        ),
    ]


def evaluate(
    repo: Path,
    confirmations: dict | None = None,
) -> list[ReleaseCheck]:
    """Evaluate repository-contained launch controls and external gates."""
    root = repo.resolve()
    return [
        *_license_decision_checks(root),
        *_license_artifact_checks(root),
        _security_contact_check(root),
        *_repository_control_checks(root),
        *_external_checks(confirmations or {}),
    ]


def result_document(checks: list[ReleaseCheck]) -> dict:
    local_blockers = [item.check_id for item in checks if item.status == BLOCK]
    external = [item.check_id for item in checks if item.status == EXTERNAL]
    return {
        "kind": "aies-public-release-readiness",
        "schema_version": 1,
        "ready": not local_blockers and not external,
        "local_blockers": local_blockers,
        "external_verification_required": external,
        "checks": [asdict(item) for item in checks],
        "limitations": [
            "This preflight does not accept governance decisions.",
            "Repository settings and signed release evidence require external verification.",
            "External evidence is a named attestation; schema validity does not prove its claim.",
            "A passing result is release input, not publication authority.",
        ],
    }


def render_text(document: dict) -> str:
    lines = ["public release readiness: "
             + ("READY" if document["ready"] else "NOT READY")]
    for item in document["checks"]:
        marker = {
            STATUS_PASS: "PASS",
            BLOCK: "BLOCK",
            EXTERNAL: "VERIFY",
        }[item["status"]]
        lines.append(f"  [{marker}] {item['title']}: {item['evidence']}")
        if item["next_action"]:
            lines.append(f"           next: {item['next_action']}")
    lines.append(
        "This report is informational; a named human release authority decides publication."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report open public-preview readiness without granting authority."
    )
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--external-evidence",
        type=Path,
        help="named confirmation JSON for controls not provable from the checkout",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="exit 1 unless every local and external prerequisite is verified",
    )
    args = parser.parse_args(argv)

    try:
        confirmations = load_external_evidence(args.external_evidence)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    document = result_document(evaluate(Path(args.repo), confirmations))
    if args.as_json:
        print(json.dumps(document, indent=2, sort_keys=True))
    else:
        print(render_text(document))
    return 1 if args.gate and not document["ready"] else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

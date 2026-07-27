"""Public-release readiness stays fail-closed and non-authorizing."""

import importlib.util
import json
from pathlib import Path
import sys


_PATH = (
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "check_public_release.py"
)
_SPEC = importlib.util.spec_from_file_location("public_release", _PATH)
public_release = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = public_release
_SPEC.loader.exec_module(public_release)


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _complete_local_fixture(root: Path) -> None:
    _write(
        root,
        "LICENSE.md",
        "CC BY-SA 4.0 applies to standards. Apache 2.0 applies to software.",
    )
    _write(
        root,
        "adr/ADR-0014-Dual-License-Standards-and-Software.md",
        "| **Status** | Accepted |\n",
    )
    _write(root, "LICENSES/CC-BY-SA-4.0.txt", "official fixture text")
    _write(root, "LICENSES/Apache-2.0.txt", "official fixture text")
    _write(
        root,
        "platform/pyproject.toml",
        '[project]\nname = "aies-platform"\nversion = "0.1.0"\n'
        'license = "Apache-2.0"\n',
    )
    _write(
        root,
        "SECURITY.md",
        "Use private vulnerability reporting or email security@aies.example.dev.",
    )
    _write(root, ".github/CODEOWNERS", "* @maintainer\n")
    _write(
        root,
        ".github/dependabot.yml",
        "package-ecosystem: github-actions\npackage-ecosystem: pip\n",
    )
    _write(
        root,
        ".github/workflows/security.yml",
        "steps:\n  - uses: github/codeql-action/analyze@pinned\n",
    )


def _external_confirmations() -> dict:
    return {
        check_id: {
            "confirmed": True,
            "verified_by": "Release Maintainer",
            "verified_at": "2026-07-27T12:00:00Z",
            "evidence": f"retained evidence for {check_id}",
        }
        for check_id in (
            "branch-protection",
            "private-vulnerability-reporting",
            "github-code-scanning",
            "history-and-actions-review",
            "signed-preview-release",
        )
    }


def test_current_pending_controls_are_reported_without_false_readiness(tmp_path):
    _write(tmp_path, "LICENSE.md", "**No license has been granted yet.**")
    _write(
        tmp_path,
        "adr/ADR-0014-Dual-License-Standards-and-Software.md",
        "| **Status** | Proposed |\n",
    )
    _write(
        tmp_path,
        "platform/pyproject.toml",
        '[project]\nname = "aies-platform"\nversion = "0.1.0"\n'
        'license = "LicenseRef-AIES-Pending"\n',
    )
    _write(
        tmp_path,
        "SECURITY.md",
        "Placeholder — a dedicated security contact will be published.",
    )

    document = public_release.result_document(public_release.evaluate(tmp_path))

    assert document["ready"] is False
    assert {
        "license-decision",
        "license-effective",
        "license-texts",
        "package-license",
        "security-contact",
        "codeowners",
        "dependency-updates",
        "security-automation",
    }.issubset(document["local_blockers"])
    assert public_release.main([str(tmp_path)]) == 0
    assert public_release.main([str(tmp_path), "--gate"]) == 1


def test_complete_tracked_controls_still_require_external_verification(tmp_path):
    _complete_local_fixture(tmp_path)

    document = public_release.result_document(public_release.evaluate(tmp_path))

    assert document["local_blockers"] == []
    assert document["ready"] is False
    assert document["external_verification_required"] == [
        "branch-protection",
        "private-vulnerability-reporting",
        "github-code-scanning",
        "history-and-actions-review",
        "signed-preview-release",
    ]
    assert public_release.main([str(tmp_path), "--gate"]) == 1


def test_complete_local_and_named_external_evidence_can_pass_gate(tmp_path):
    _complete_local_fixture(tmp_path)
    evidence_path = tmp_path / "release-external-evidence.json"
    evidence_path.write_text(
        json.dumps({
            "kind": "aies-public-release-external-evidence",
            "schema_version": 1,
            "confirmations": _external_confirmations(),
        }),
        encoding="utf-8",
    )

    confirmations = public_release.load_external_evidence(evidence_path)
    document = public_release.result_document(
        public_release.evaluate(tmp_path, confirmations)
    )

    assert document["ready"] is True
    assert document["local_blockers"] == []
    assert document["external_verification_required"] == []
    assert public_release.main([
        str(tmp_path),
        "--external-evidence",
        str(evidence_path),
        "--gate",
    ]) == 0


def test_external_evidence_requires_named_timestamped_confirmation(tmp_path):
    _complete_local_fixture(tmp_path)
    confirmations = _external_confirmations()
    confirmations["branch-protection"]["verified_by"] = ""

    document = public_release.result_document(
        public_release.evaluate(tmp_path, confirmations)
    )

    assert document["ready"] is False
    assert "branch-protection" in document["external_verification_required"]


def test_shipped_external_evidence_template_is_valid_and_fail_closed():
    template = Path(__file__).resolve().parents[2] / "templates" / (
        "public-release-external-evidence.json"
    )

    confirmations = public_release.load_external_evidence(template)

    assert set(confirmations) == {
        "branch-protection",
        "private-vulnerability-reporting",
        "github-code-scanning",
        "history-and-actions-review",
        "signed-preview-release",
    }
    assert not any(
        public_release._valid_confirmation(value)
        for value in confirmations.values()
    )


def test_security_contact_rejects_placeholder_example_addresses(tmp_path):
    _complete_local_fixture(tmp_path)
    _write(
        tmp_path,
        "SECURITY.md",
        "Placeholder contact: security@example.com",
    )

    checks = {
        item.check_id: item
        for item in public_release.evaluate(tmp_path)
    }

    assert checks["security-contact"].status == public_release.BLOCK

"""Adoption-grade CI projections for AIES repository evidence.

CI is advisory by default.  The same audit is calculated in both modes, but a
non-zero policy exit is returned only when the caller explicitly enables
enforcement.  This keeps evidence collection useful without silently turning
on organizational policy.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from . import audit, constants as C


def _all_checks(result: dict) -> list[dict]:
    return [
        check
        for area in result["areas"].values()
        for check in area["checks"]
    ]


def _annotation(check: dict, required_failures: set[str]) -> dict:
    required = check["id"] in required_failures
    return {
        "level": "warning" if required else "notice",
        "id": check["id"],
        "area": check["area"],
        "area_label": C.identifier_label(check["area"]),
        "title": check["title"],
        "message": check["recommendation"],
        "required_at": check.get("required_at"),
        "policy_required": required,
    }


def _summary_markdown(package: dict) -> str:
    policy = package["policy"]
    heading = (
        "Explicit enforcement"
        if policy["enforced"]
        else "Advisory evidence — no CI gate"
    )
    lines = [
        "# AIES Repository Assessment",
        "",
        f"**Mode:** {heading}",
        f"**Risk tier evaluated:** {C.risk_tier_label(policy['risk_tier'])}",
        f"**Policy result:** {'PASS' if policy['passed'] else 'GAPS FOUND'}",
        "",
    ]
    if not policy["enforced"]:
        lines.extend([
            "> Findings are visible and retained, but this job is intentionally "
            "non-blocking. Set `enforce: true` only after the repository owners "
            "approve that policy.",
            "",
        ])
    lines.extend([
        f"- Verified evidence: {package['audit']['totals']['verified']}",
        f"- Asserted evidence: {package['audit']['totals']['asserted']}",
        f"- Gaps: {package['audit']['totals']['gap']}",
        f"- Policy-required gaps: {len(policy['failures'])}",
        "",
        "## Full audit",
        "",
        audit.render_markdown(package["audit"]),
        "",
    ])
    return "\n".join(lines)


def build_repository_package(
    repo: str | Path,
    *,
    risk_tier: str = "RT2",
    enforce: bool = False,
    attestations: dict | None = None,
) -> dict:
    result = audit.run_audit(
        repo, attestations=attestations, rt=risk_tier, record=False)
    gate = result["gate"]
    required_failures = {item["id"] for item in gate["failures"]}
    annotations = [
        _annotation(check, required_failures)
        for check in _all_checks(result)
        if check["state"] == "gap"
    ]
    return {
        "kind": "aies-ci-repository-assessment",
        "schema": 1,
        "policy": {
            "mode": "enforced" if enforce else "advisory",
            "enforced": enforce,
            "risk_tier": risk_tier,
            "risk_tier_label": C.risk_tier_label(risk_tier),
            "passed": gate["passed"],
            "failures": gate["failures"],
            "exit_code": 1 if enforce and not gate["passed"] else 0,
            "statement": (
                "The audit is an explicitly enabled CI policy gate."
                if enforce else
                "The audit is advisory; findings cannot fail the CI job."),
        },
        "audit": result,
        "annotations": annotations,
        "limitations": [
            "Repository-practice evidence does not prove source correctness.",
            "A gap is missing evidence, not proof that a practice never occurs.",
            "Attestations remain distinct from automatically verified evidence.",
            "This CI projection creates no qualification or deployment authority.",
        ],
    }


def write_repository_package(package: dict, destination: str | Path) -> dict:
    target = Path(destination).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "repository-assessment.json"
    markdown_path = target / "repository-assessment.md"
    annotations_path = target / "annotations.json"
    summary = _summary_markdown(package)
    json_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(summary, encoding="utf-8")
    annotations_path.write_text(
        json.dumps(package["annotations"], indent=2) + "\n", encoding="utf-8")

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with Path(step_summary).open("a", encoding="utf-8") as stream:
            stream.write(summary)
    return {
        "directory": str(target),
        "json": str(json_path),
        "markdown": str(markdown_path),
        "annotations": str(annotations_path),
    }


def github_annotation_lines(package: dict) -> list[str]:
    def escape(value: object) -> str:
        return (
            str(value)
            .replace("%", "%25")
            .replace("\r", "%0D")
            .replace("\n", "%0A")
        )

    return [
        f"::{item['level']} title={escape(item['area_label'])}: "
        f"{escape(item['title'])}::{escape(item['message'])}"
        for item in package["annotations"]
    ]

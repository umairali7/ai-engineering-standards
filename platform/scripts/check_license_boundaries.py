#!/usr/bin/env python3
"""Verify AIES path-based licensing without guessing from file contents.

ADR-0014 assigns content and executable material different licenses. This
check classifies every tracked or unignored working-tree path, honors explicit
SPDX overrides, and verifies that the installed official license texts have
not drifted. It does not determine copyright ownership or provide legal
advice.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess


CC = "CC-BY-SA-4.0"
APACHE = "Apache-2.0"
LICENSE_TEXT = "license-text"
KNOWN_SPDX = {CC, APACHE}

CONTENT_ROOTS = {
    "Shared", "AEBOK", "AESQS", "AEOS", "AEAR", "AECT", "ECM",
    "adr", "docs", "research", "templates", "diagrams",
}
PLATFORM_CONTENT_ROOTS = {
    "assessments", "calibration", "competencies", "journeys", "profiles",
    "subject_profiles", "task_mappings",
}
IGNORED_PARTS = {
    ".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache",
    "aies-workspace", "build", "dist",
}
EXPECTED_LICENSE_HASHES = {
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "LICENSES/CC-BY-SA-4.0.txt":
        "23ee78c8bae49cf08ea2f0c84945c66b987ebe4520881fb51b3dad4fb43d07c2",
    "platform/LICENSE":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}


def _normalized_hash(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    normalized = text.rstrip("\r\n") + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _spdx_override(path: Path) -> str | None:
    if not path.is_file() or path.stat().st_size > 5_000_000:
        return None
    try:
        prefix = path.read_text(encoding="utf-8")[:4096]
    except (UnicodeDecodeError, OSError):
        return None
    match = re.search(
        r"SPDX-License-Identifier:\s*([A-Za-z0-9.+-]+)", prefix,
    )
    return match.group(1) if match else None


def path_default(relative: str) -> str:
    """Return the single ADR-0014 default for a normalized repository path."""
    path = Path(relative.replace("\\", "/"))
    parts = path.parts
    if not parts:
        raise ValueError("empty repository path")
    if parts[0] == "LICENSES":
        return LICENSE_TEXT
    if len(parts) == 1:
        return CC if path.suffix.lower() == ".md" else APACHE
    if parts[0] in CONTENT_ROOTS:
        return CC
    if parts[0] == "examples":
        return APACHE if path.suffix.lower() in {".py", ".js", ".ts", ".sh", ".ps1"} else CC
    if parts[0] == "conformance":
        return APACHE if path.suffix.lower() == ".py" else CC
    if parts[0] == "platform":
        if len(parts) == 2 and (
            path.suffix.lower() == ".md" or path.suffix.lower() in {".yaml", ".yml"}
        ):
            return CC
        if len(parts) > 2 and parts[1] in PLATFORM_CONTENT_ROOTS:
            return CC
        return APACHE
    return APACHE


def classified_license(root: Path, relative: str) -> tuple[str, str]:
    override = _spdx_override(root / relative)
    if override:
        return override, "SPDX override"
    return path_default(relative), "path default"


def repository_paths(root: Path) -> list[str]:
    command = [
        "git", "-C", str(root), "ls-files", "--cached", "--others",
        "--exclude-standard", "-z",
    ]
    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=False,
        )
        return sorted(
            value.decode("utf-8").replace("\\", "/")
            for value in result.stdout.split(b"\0") if value
        )
    except (OSError, subprocess.CalledProcessError):
        return sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
        )


def violations(root: Path) -> tuple[list[str], Counter]:
    problems: list[str] = []
    counts: Counter = Counter()
    for relative in repository_paths(root):
        value, source = classified_license(root, relative)
        counts[value] += 1
        if source == "SPDX override" and value not in KNOWN_SPDX:
            problems.append(f"{relative}: unsupported SPDX override {value!r}")

    for relative, expected in EXPECTED_LICENSE_HASHES.items():
        path = root / relative
        if not path.is_file():
            problems.append(f"{relative}: official license text is missing")
        elif _normalized_hash(path) != expected:
            problems.append(f"{relative}: official license text has changed")

    notice = root / "LICENSE.md"
    notice_text = notice.read_text(encoding="utf-8") if notice.is_file() else ""
    if "CC BY-SA 4.0" not in notice_text or "Apache License 2.0" not in notice_text:
        problems.append("LICENSE.md: authoritative path scope is incomplete")
    if "No license has been granted" in notice_text or "All rights are reserved" in notice_text:
        problems.append("LICENSE.md: pending-license language remains")
    return problems, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.repo).resolve()
    problems, counts = violations(root)
    document = {
        "kind": "aies-license-boundary-check",
        "schema_version": 1,
        "passed": not problems,
        "counts": dict(sorted(counts.items())),
        "violations": problems,
    }
    if args.json:
        print(json.dumps(document, indent=2, sort_keys=True))
    elif problems:
        print("license boundary: FAIL")
        for problem in problems:
            print(f"  - {problem}")
    else:
        summary = ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
        print(f"license boundary: PASS ({summary})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail when tracked files contain local or generated release contaminants.

The release artifact is built from the tracked tree. This deliberately checks
``git ls-files`` rather than the working directory: an ignored local workspace
is legitimate during development, but none of its contents may enter a release.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath


def forbidden_reason(path: str) -> str | None:
    """Return why a tracked relative path is forbidden, or ``None``."""
    parts = PurePosixPath(path).parts
    name = parts[-1] if parts else path
    if name == ".env":
        return "environment file"
    if name == ".DS_Store":
        return "Finder metadata"
    if name.endswith(".pyc"):
        return "Python bytecode"
    if any(part in {"__pycache__", ".pytest_cache", "aies-workspace"}
           for part in parts):
        return "generated local artifact directory"
    if any(part.endswith(".egg-info") for part in parts):
        return "packaging metadata"
    return None


def tracked_paths(repo: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", repo, "ls-files"], check=True, text=True,
        capture_output=True,
    )
    return [line for line in completed.stdout.splitlines() if line]


def violations(paths: list[str]) -> list[tuple[str, str]]:
    return [(path, reason) for path in paths if (reason := forbidden_reason(path))]


def main(argv: list[str] | None = None) -> int:
    repo = (argv or sys.argv[1:] or ["."])[0]
    bad = violations(tracked_paths(repo))
    if bad:
        print("release hygiene: FAIL")
        for path, reason in bad:
            print(f"  {path}: {reason}")
        return 1
    print("release hygiene: PASS (tracked tree contains no local/generated artifacts)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

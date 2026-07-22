#!/usr/bin/env python3
"""Validate uniqueness of governed AIES Document IDs.

Only concrete metadata-table declarations are considered. Template examples and
ordinary citations are intentionally ignored. The check is repository-wide
because duplicate IDs break stable citations even when the colliding documents
live in different modules.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


DECLARATION = re.compile(
    r"^\|\s*\*\*Document ID\*\*\s*\|\s*(AIES-[A-Z0-9-]+)\s*\|\s*$",
    re.MULTILINE,
)
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache",
              "node_modules", "dist", "build", "aies-workspace"}


def declarations(root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = defaultdict(list)
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in DECLARATION.finditer(text):
            found[match.group(1)].append(rel.as_posix())
    return dict(found)


def duplicate_declarations(root: Path) -> dict[str, list[str]]:
    return {doc_id: paths for doc_id, paths in declarations(root).items()
            if len(paths) > 1}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="check governed Document ID uniqueness")
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    found = declarations(root)
    duplicates = {doc_id: paths for doc_id, paths in found.items() if len(paths) > 1}
    if duplicates:
        print("document ID uniqueness: FAIL")
        for doc_id, paths in sorted(duplicates.items()):
            print(f"  {doc_id}: {', '.join(paths)}")
        return 1
    print(f"document ID uniqueness: PASS ({len(found)} governed IDs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

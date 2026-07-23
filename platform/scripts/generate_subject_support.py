"""Generate or verify the subject-support matrix from the canonical registry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]
SRC = PLATFORM / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aies import support  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true",
        help="fail if SUBJECT_SUPPORT.md differs from the registry")
    args = parser.parse_args()
    target = PLATFORM / "SUBJECT_SUPPORT.md"
    expected = support.render_markdown()
    if args.check:
        actual = target.read_text(encoding="utf-8") if target.is_file() else ""
        if actual != expected:
            print(
                "subject support documentation is stale; run "
                "python scripts/generate_subject_support.py",
                file=sys.stderr,
            )
            return 1
        print("subject support documentation: PASS")
        return 0
    target.write_text(expected, encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

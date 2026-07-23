"""Generate or verify Subject Assessment Profile documentation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]
SRC = PLATFORM / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aies import assessment_profiles  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true",
        help="fail if ASSESSMENT_PROFILES.md differs from canonical YAML")
    args = parser.parse_args()
    target = PLATFORM / "ASSESSMENT_PROFILES.md"
    expected = assessment_profiles.render_markdown()
    if args.check:
        actual = target.read_text(encoding="utf-8") if target.is_file() else ""
        if actual != expected:
            print(
                "assessment profile documentation is stale; run "
                "python scripts/generate_assessment_profiles.py",
                file=sys.stderr,
            )
            return 1
        print("assessment profile documentation: PASS")
        return 0
    target.write_text(expected, encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

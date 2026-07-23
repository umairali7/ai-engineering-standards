"""Regenerate platform/CLI_REFERENCE.md from the live CLI parser."""

from __future__ import annotations

import sys
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]
SRC = PLATFORM / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aies.cli import build_parser  # noqa: E402
from aies.cli_reference import render_cli_reference  # noqa: E402


def main() -> int:
    target = PLATFORM / "CLI_REFERENCE.md"
    target.write_text(render_cli_reference(build_parser()), encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

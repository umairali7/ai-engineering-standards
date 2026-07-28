#!/usr/bin/env python3
"""Compatibility wrapper for the canonical ``aies security`` command."""

from __future__ import annotations

import sys
from pathlib import Path


# The CI history job intentionally runs before installing the package. Make the
# source tree importable without changing the machine or user environment.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aies.security_checks import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())

"""Locate shipped platform data in source, editable, and wheel installs."""

from __future__ import annotations

import os
import sysconfig
from pathlib import Path


def data_root() -> Path:
    override = os.environ.get("AIES_DATA_DIR")
    if override:
        root = Path(override).expanduser().resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"AIES_DATA_DIR does not exist: {root}")
        return root

    source_root = Path(__file__).resolve().parents[2]
    if (source_root / "competencies").is_dir():
        return source_root

    installed = Path(sysconfig.get_path("data")) / "share" / "aies"
    if (installed / "competencies").is_dir():
        return installed
    raise FileNotFoundError(
        "AIES assessment data was not installed. Reinstall the wheel, or set "
        "AIES_DATA_DIR to the platform data directory."
    )

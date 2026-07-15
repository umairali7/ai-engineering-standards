"""Workspace layout: where the platform persists its plain-file artifacts.

All persisted artifacts are plain YAML/JSON files (PLATFORM.md §5) so
evidence is diffable and tool-independent. Records are append-only;
nothing here ever rewrites an existing evidence record.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import config


def root() -> Path:
    return Path(config.workspace_dir()).resolve()


def ensure() -> Path:
    ws = root()
    for sub in ("registry", "fingerprints", "runs"):
        (ws / sub).mkdir(parents=True, exist_ok=True)
    return ws


def registry_dir() -> Path:
    return ensure() / "registry"


def fingerprints_dir() -> Path:
    return ensure() / "fingerprints"


def runs_dir() -> Path:
    return ensure() / "runs"


def run_dir(run_id: str) -> Path:
    return runs_dir() / run_id


def write_json(path: Path, data: dict, *, overwrite: bool = False) -> Path:
    """Write a JSON record. Evidence records are append-only: refuse to
    overwrite unless the caller explicitly owns the file (manifests,
    worksheets)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"{path} exists; evidence records are append-only "
            "(AIES-AESQS-RR-01-R16) — corrections are new records"
        )
    path.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")
    return path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

"""Workspace layout: where the platform persists its plain-file artifacts.

All persisted artifacts are plain YAML/JSON files (PLATFORM.md §5) so
evidence is diffable and tool-independent. Records are append-only;
nothing here ever rewrites an existing evidence record.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import config


APPEND_ONLY_DIRECTORIES = frozenset({
    "responses", "ratings", "resolutions", "events", "raters", "audits",
})
MUTABLE_WORKING_FILES = frozenset({
    "manifest.json", "scoresheet.json", "progress.json", "latest.json",
})
DERIVED_SNAPSHOT_FILES = frozenset({
    "evidence-package.json", "assessment-result.json", "review-package.json",
})
REGENERABLE_VIEW_FILES = frozenset({
    "report.md", "report.json", "report.html", "engineering-evaluation.json",
    "engineering-capability-matrix.md", "engineering-capability-matrix.json",
    "engineering-capability-matrix.html", "deployment-guidance.md",
    "deployment-guidance.json", "deployment-guidance.html",
    "executive-summary.md", "executive-summary.json", "executive-summary.html",
    "assessment-result.md", "assessment-result.html", "report-bundle.json",
    "grounding-diagnostics.md", "grounding-diagnostics.json",
    "grounding-diagnostics.html", "dashboard.html",
})


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


def artifact_class(path: Path) -> str:
    """Classify a workspace path by its storage and mutation contract."""
    path = Path(path).resolve()
    try:
        relative = path.relative_to(root())
    except ValueError:
        return "external"
    parts = relative.parts
    if len(parts) >= 2 and parts[0] == "qualifications" and parts[1] == "reports":
        return "regenerable-view"
    if any(part in APPEND_ONLY_DIRECTORIES for part in parts):
        return "append-only-record"
    if parts and parts[0] == "qualifications" and path.name.startswith("QUAL-"):
        return "append-only-record"
    if path.name in MUTABLE_WORKING_FILES:
        return "mutable-working-state"
    if path.name in DERIVED_SNAPSHOT_FILES:
        return "derived-canonical-snapshot"
    if path.name in REGENERABLE_VIEW_FILES or (parts and parts[0] == "reports"):
        return "regenerable-view"
    if parts and parts[0] == "registry":
        return "mutable-configuration"
    return "unclassified"


def write_json(path: Path, data: dict, *, overwrite: bool = False) -> Path:
    """Write a JSON record. Evidence records are append-only: refuse to
    overwrite unless the caller explicitly owns the file (manifests,
    worksheets)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    classification = artifact_class(path)
    if overwrite and classification == "append-only-record":
        raise PermissionError(
            f"{path} is an append-only record and cannot be overwritten")
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"{path} exists; evidence records are append-only "
            "(AIES-AESQS-RR-01-R16) — corrections are new records"
        )
    path.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")
    return path


def write_view(path: Path, content: str) -> Path:
    """Replace a renderer-owned, regenerable presentation artifact only."""
    if artifact_class(path) != "regenerable-view":
        raise ValueError(f"{path} is not classified as a regenerable view")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

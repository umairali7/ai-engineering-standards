"""Verified, non-overwriting import of AIES run packages.

Imports preserve every admitted package file byte-for-byte. ZIP extraction is
bounded and traversal-safe. Existing canonical runs are never overwritten; an
identical import is idempotent, while a conflicting import is rejected.
"""

from __future__ import annotations

import contextlib
import datetime
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath

from . import workspace


SCHEMA = "aies-run-import/v1"
MAX_FILES = 100_000
MAX_TOTAL_BYTES = 20 * 1024 * 1024 * 1024
MAX_FILE_BYTES = 2 * 1024 * 1024 * 1024
_ARCHIVE_METADATA = {
    ".ds_store", "thumbs.db", "desktop.ini",
}
_CACHE_DIRECTORIES = {
    "__macosx", "__pycache__", ".pytest_cache",
}


class RunImportError(ValueError):
    pass


def _excluded(relative: str) -> bool:
    parts = PurePosixPath(relative.replace("\\", "/")).parts
    return (
        any(part.lower() in _CACHE_DIRECTORIES for part in parts)
        or any(part.lower() in _ARCHIVE_METADATA for part in parts)
        or relative.lower().endswith((".pyc", ".pyo"))
    )


def _safe_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        raise RunImportError(
            f"archive member is absolute or drive-qualified: {value!r}")
    path = PurePosixPath(normalized)
    if not path.parts or any(part in ("", ".", "..") for part in path.parts):
        raise RunImportError(
            f"archive member has an unsafe relative path: {value!r}")
    if any(":" in part for part in path.parts):
        raise RunImportError(
            f"archive member contains an unsupported colon: {value!r}")
    return path.as_posix()


def _zip_is_symlink(member: zipfile.ZipInfo) -> bool:
    mode = (member.external_attr >> 16) & 0o170000
    return mode == 0o120000


def _extract_zip(source: Path, target: Path) -> dict:
    excluded = []
    seen = set()
    total = 0
    archive_hash = hashlib.sha256()
    with source.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            archive_hash.update(block)
    try:
        archive = zipfile.ZipFile(source)
    except (zipfile.BadZipFile, OSError) as error:
        raise RunImportError(f"invalid ZIP package: {error}") from error
    with archive:
        members = archive.infolist()
        if len(members) > MAX_FILES:
            raise RunImportError(
                f"ZIP contains {len(members)} entries; limit is {MAX_FILES}")
        planned = []
        for member in members:
            relative = _safe_relative(member.filename.rstrip("/"))
            key = relative.casefold()
            if key in seen:
                raise RunImportError(
                    f"ZIP contains duplicate or case-colliding path {relative!r}")
            seen.add(key)
            if _zip_is_symlink(member):
                raise RunImportError(
                    f"ZIP symlink entries are not accepted: {relative!r}")
            if _excluded(relative):
                excluded.append({
                    "path": relative,
                    "reason": "archive metadata or disposable cache",
                })
                continue
            if member.is_dir():
                continue
            if member.file_size > MAX_FILE_BYTES:
                raise RunImportError(
                    f"ZIP member exceeds the {MAX_FILE_BYTES}-byte limit: "
                    f"{relative!r}")
            total += member.file_size
            if total > MAX_TOTAL_BYTES:
                raise RunImportError(
                    f"ZIP expands beyond the {MAX_TOTAL_BYTES}-byte limit")
            planned.append((member, relative))
        for member, relative in planned:
            destination = target.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as incoming, destination.open("xb") as outgoing:
                shutil.copyfileobj(incoming, outgoing, length=1024 * 1024)
    return {
        "kind": "zip",
        "name": source.name,
        "source_digest": "sha256:" + archive_hash.hexdigest(),
        "excluded": excluded,
    }


@contextlib.contextmanager
def _materialized_source(source: Path):
    if source.is_dir():
        yield source.resolve(), {
            "kind": "directory",
            "name": source.name,
            "source_digest": None,
            "excluded": [],
        }
        return
    if not source.is_file() or source.suffix.lower() != ".zip":
        raise RunImportError(
            "run package must be a directory or .zip archive")
    with tempfile.TemporaryDirectory(prefix="aies-run-import-") as temporary:
        root = Path(temporary)
        provenance = _extract_zip(source.resolve(), root)
        yield root, provenance


def _find_package_root(root: Path) -> Path:
    manifests = []
    entries = 0
    for path in root.rglob("*"):
        entries += 1
        if entries > MAX_FILES:
            raise RunImportError(
                f"package wrapper contains more than {MAX_FILES} entries")
        relative = path.relative_to(root).as_posix()
        if _excluded(relative):
            continue
        if path.is_symlink():
            raise RunImportError(
                f"run package wrapper symlink is not accepted: {relative!r}")
        if path.is_file() and path.name == "manifest.json":
            manifests.append(path)
    if not manifests:
        raise RunImportError("package contains no manifest.json")
    if len(manifests) > 1:
        shown = ", ".join(
            path.relative_to(root).as_posix() for path in manifests[:5])
        raise RunImportError(
            f"package contains multiple run manifests ({shown}); import one "
            "run package at a time")
    return manifests[0].parent


def _inventory(package_root: Path) -> tuple[list[dict], list[dict]]:
    rows = []
    excluded = []
    case_paths = set()
    total = 0
    for path in sorted(package_root.rglob("*")):
        relative = path.relative_to(package_root).as_posix()
        if _excluded(relative):
            excluded.append({
                "path": relative,
                "reason": "archive metadata or disposable cache",
            })
            continue
        if path.is_symlink():
            raise RunImportError(
                f"run package symlink is not accepted: {relative!r}")
        if not path.is_file():
            continue
        key = relative.casefold()
        if key in case_paths:
            raise RunImportError(
                f"package contains case-colliding path {relative!r}")
        case_paths.add(key)
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise RunImportError(
                f"package file exceeds the {MAX_FILE_BYTES}-byte limit: "
                f"{relative!r}")
        total += size
        if len(rows) + 1 > MAX_FILES or total > MAX_TOTAL_BYTES:
            raise RunImportError("run package exceeds bounded import limits")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        rows.append({
            "path": relative,
            "bytes": size,
            "sha256": digest.hexdigest(),
        })
    return rows, excluded


def _tree_digest(files: list[dict]) -> str:
    material = "\n".join(
        f"{row['path']}\0{row['bytes']}\0{row['sha256']}"
        for row in files)
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def _manifest(package_root: Path) -> dict:
    try:
        value = json.loads(
            (package_root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RunImportError(f"manifest.json is unreadable: {error}") from error
    if not isinstance(value, dict):
        raise RunImportError("manifest.json must contain a JSON object")
    run_id = value.get("run_id")
    try:
        workspace.validate_run_id(run_id)
    except ValueError as error:
        raise RunImportError(f"manifest run_id is invalid: {error}") from error
    return value


def _receipt_id(run_id: str, tree_digest: str) -> str:
    short = hashlib.sha256(
        f"{run_id}\0{tree_digest}".encode("utf-8")).hexdigest()[:16]
    return f"run-import-{short}"


def _same_files(target: Path, files: list[dict]) -> tuple[bool, list[str]]:
    conflicts = []
    for row in files:
        path = target.joinpath(*PurePosixPath(row["path"]).parts)
        if not path.is_file():
            conflicts.append(row["path"] + " (missing)")
            continue
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        if path.stat().st_size != row["bytes"] or digest.hexdigest() != row["sha256"]:
            conflicts.append(row["path"] + " (different content)")
    return not conflicts, conflicts


def _same_tree(target: Path, files: list[dict]) -> tuple[bool, list[str]]:
    """Verify an exact package tree, not merely a matching source subset."""
    if not target.is_dir():
        return False, ["destination directory is missing"]
    actual, _ = _inventory(target)
    expected_by_path = {row["path"]: row for row in files}
    actual_by_path = {row["path"]: row for row in actual}
    conflicts = []
    for relative in sorted(set(expected_by_path) | set(actual_by_path)):
        expected = expected_by_path.get(relative)
        observed = actual_by_path.get(relative)
        if expected is None:
            conflicts.append(relative + " (unexpected destination file)")
        elif observed is None:
            conflicts.append(relative + " (missing)")
        elif (expected["bytes"], expected["sha256"]) != (
                observed["bytes"], observed["sha256"]):
            conflicts.append(relative + " (different content)")
    return not conflicts, conflicts


def _copy_to_stage(package_root: Path, files: list[dict], stage: Path) -> None:
    stage.mkdir(parents=True)
    for row in files:
        source = package_root.joinpath(*PurePosixPath(row["path"]).parts)
        target = stage.joinpath(*PurePosixPath(row["path"]).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    verified, conflicts = _same_files(stage, files)
    if not verified:
        raise RunImportError(
            "staged package failed byte verification: "
            + ", ".join(conflicts[:10]))


def _plan(root: Path, provenance: dict) -> dict:
    package_root = _find_package_root(root)
    manifest = _manifest(package_root)
    files, local_excluded = _inventory(package_root)
    if not files or files[0]["path"] != "manifest.json":
        if not any(row["path"] == "manifest.json" for row in files):
            raise RunImportError("manifest.json was excluded from the package")
    tree_digest = _tree_digest(files)
    run_id = manifest["run_id"]
    receipt_id = _receipt_id(run_id, tree_digest)
    canonical = workspace.runs_dir() / run_id
    nested_in_destination = False
    try:
        package_root.resolve().relative_to(canonical.resolve())
        nested_in_destination = package_root.resolve() != canonical.resolve()
    except ValueError:
        pass
    existing_canonical = (canonical / "manifest.json").is_file()
    already_imported = False
    conflicts = []
    if existing_canonical:
        already_imported, conflicts = _same_tree(canonical, files)
    elif canonical.exists() and not nested_in_destination:
        conflicts = [
            "destination exists without a canonical manifest and is not the "
            "source wrapper"
        ]
    if conflicts:
        raise RunImportError(
            f"run {run_id!r} cannot be imported without overwrite: "
            + ", ".join(conflicts[:10]))
    return {
        "kind": "aies-run-import-plan",
        "schema": SCHEMA,
        "receipt_id": receipt_id,
        "run_id": run_id,
        "source": {
            "kind": provenance["kind"],
            "name": provenance["name"],
            "source_digest": provenance["source_digest"],
        },
        "package_root": str(package_root),
        "manifest": {
            "run_id": run_id,
            "status": manifest.get("status"),
            "created_at": manifest.get("created_at"),
            "subject_id": (manifest.get("subject") or {}).get("id")
            or (manifest.get("model") or {}).get("registry_id"),
        },
        "package_tree_digest": tree_digest,
        "files": files,
        "file_count": len(files),
        "bytes": sum(row["bytes"] for row in files),
        "excluded": provenance["excluded"] + local_excluded,
        "loss_accounting": {
            "admitted_files": len(files),
            "admitted_bytes": sum(row["bytes"] for row in files),
            "excluded_disposable_items": (
                len(provenance["excluded"]) + len(local_excluded)),
            "evidence_files_removed": 0,
            "lossy": False,
        },
        "verification": {
            "algorithm": "SHA-256",
            "scope": "relative path, byte size, and content digest",
            "exact_tree_required": True,
            "byte_preservation_required": True,
        },
        "destination": str(canonical),
        "nested_source_wrapper": nested_in_destination,
        "already_imported": already_imported,
        "would_write": not already_imported,
        "limits": {
            "max_files": MAX_FILES,
            "max_total_bytes": MAX_TOTAL_BYTES,
            "max_file_bytes": MAX_FILE_BYTES,
        },
        "claim_boundary": (
            "Import verifies identity and byte preservation. It does not "
            "validate scores, admit evidence, recompute results, or establish "
            "qualification."),
    }


def inspect(source: str | Path) -> dict:
    source_path = Path(source)
    with _materialized_source(source_path) as (root, provenance):
        return _plan(root, provenance)


def import_package(source: str | Path, *, dry_run: bool = False) -> dict:
    source_path = Path(source)
    with _materialized_source(source_path) as (root, provenance):
        plan = _plan(root, provenance)
        if dry_run:
            return plan
        receipt_path = (
            workspace.root() / "run-imports"
            / f"{plan['receipt_id']}.json")
        if receipt_path.exists():
            return workspace.read_json(receipt_path)
        if plan["already_imported"]:
            receipt = {
                **plan,
                "kind": "aies-run-import-receipt",
                "status": "already-imported",
                "imported_at": datetime.datetime.now(
                    datetime.timezone.utc).isoformat(),
                "source_wrapper_preserved": None,
                "verified_after_import": True,
            }
            workspace.write_json(receipt_path, receipt)
            return receipt

        package_root = Path(plan["package_root"])
        canonical = Path(plan["destination"])
        staging_root = workspace.root() / ".run-import-staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        stage = staging_root / (
            plan["run_id"] + "-" + uuid.uuid4().hex)
        preserved = None
        try:
            _copy_to_stage(package_root, plan["files"], stage)
            if canonical.exists():
                if not plan["nested_source_wrapper"]:
                    raise RunImportError(
                        f"destination appeared during import: {canonical}")
                preserved_root = workspace.root() / "import-sources"
                preserved_root.mkdir(parents=True, exist_ok=True)
                preserved = preserved_root / plan["receipt_id"]
                if preserved.exists():
                    raise RunImportError(
                        f"preserved source target already exists: {preserved}")
                os.replace(canonical, preserved)
            os.replace(stage, canonical)
        except Exception:
            if preserved and preserved.exists() and not canonical.exists():
                os.replace(preserved, canonical)
            raise
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        verified, conflicts = _same_tree(canonical, plan["files"])
        if not verified:
            raise RunImportError(
                "destination verification failed after import: "
                + ", ".join(conflicts[:10]))
        receipt = {
            **plan,
            "kind": "aies-run-import-receipt",
            "status": "imported",
            "imported_at": datetime.datetime.now(
                datetime.timezone.utc).isoformat(),
            "source_wrapper_preserved": str(preserved) if preserved else None,
            "verified_after_import": True,
        }
        workspace.write_json(receipt_path, receipt)
        return receipt


def list_receipts() -> list[dict]:
    directory = workspace.root() / "run-imports"
    if not directory.exists():
        return []
    rows = []
    for path in directory.glob("run-import-*.json"):
        value = workspace.read_json(path)
        rows.append({
            "receipt_id": value.get("receipt_id", path.stem),
            "run_id": value.get("run_id"),
            "status": value.get("status"),
            "imported_at": value.get("imported_at"),
            "file_count": value.get("file_count"),
            "package_tree_digest": value.get("package_tree_digest"),
            "href": "/run-imports/" + value.get(
                "receipt_id", path.stem),
        })
    return sorted(
        rows, key=lambda row: row.get("imported_at") or "", reverse=True)

"""First-use orchestration and safe local result sharing.

These helpers do not define assessment or decision semantics.  They make the
existing canonical pipeline easier to enter and its regenerable views easier
to find without exposing raw prompts, responses, ratings, or secrets.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import webbrowser
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import yaml

from . import workspace


SHAREABLE_VIEWS = (
    "executive-summary.html",
    "executive-summary.md",
    "executive-summary.json",
    "engineering-capability-matrix.html",
    "engineering-capability-matrix.md",
    "engineering-capability-matrix.json",
    "engineering-fit-guidance.html",
    "engineering-fit-guidance.md",
    "engineering-fit-guidance.json",
    "engineering-assessment-result.html",
    "engineering-assessment-result.md",
    "engineering-assessment-result.json",
    "grounding-diagnostics.html",
    "grounding-diagnostics.md",
    "grounding-diagnostics.json",
    "report.html",
    "report.md",
    "report.json",
    "report-bundle.json",
)


class AdoptionError(RuntimeError):
    pass


def initialize(path: Path) -> dict:
    """Create a safe workspace skeleton without overwriting user files."""
    target = Path(path).expanduser().resolve()
    created: list[str] = []
    existing: list[str] = []
    for relative in ("registry", "fingerprints", "runs", "exports"):
        item = target / relative
        if item.exists():
            existing.append(str(item))
        else:
            item.mkdir(parents=True, exist_ok=False)
            created.append(str(item))

    gitignore = target / ".gitignore"
    if gitignore.exists():
        existing.append(str(gitignore))
    else:
        gitignore.write_text(
            "# AIES workspace data may contain sensitive assessment evidence.\n"
            "*\n"
            "!.gitignore\n"
            "!README.md\n",
            encoding="utf-8",
        )
        created.append(str(gitignore))

    readme = target / "README.md"
    if readme.exists():
        existing.append(str(readme))
    else:
        readme.write_text(
            "# AIES workspace\n\n"
            "This directory stores deployment manifests, collected responses, "
            "ratings, and generated reports. Raw assessment evidence can be sensitive "
            "and is ignored by Git. Keep credentials in environment variables; "
            "do not place API keys in this directory.\n",
            encoding="utf-8",
        )
        created.append(str(readme))

    return {
        "workspace": str(target),
        "created": created,
        "existing": existing,
        "environment": f"AIES_WORKSPACE={target}",
        "next": (
            f'aies discover  # with AIES_WORKSPACE set to "{target}"\n'
            "aies deployment list"
        ),
        "secrets_written": False,
    }


def resolve_run(reference: str) -> Path:
    runs = workspace.runs_dir()
    if reference == "latest":
        candidates = sorted(
            (p for p in runs.glob("run-*") if p.is_dir()),
            key=lambda p: p.stat().st_mtime,
        )
        if not candidates:
            raise AdoptionError("the workspace contains no runs")
        return candidates[-1]
    candidate = workspace.run_dir(reference)
    if not candidate.is_dir():
        raise AdoptionError(f"run {reference!r} was not found in {runs}")
    return candidate


def primary_view(reference: str) -> Path:
    run = resolve_run(reference)
    for name in (
        "executive-summary.html",
        "engineering-assessment-result.html",
        "report.html",
        "engineering-capability-matrix.html",
    ):
        candidate = run / name
        if candidate.is_file():
            return candidate
    raise AdoptionError(
        f"run {run.name!r} has no HTML result; resume scoring/report generation first"
    )


def open_result(reference: str, *, launch: bool = True) -> dict:
    view = primary_view(reference)
    launched = bool(webbrowser.open(view.as_uri())) if launch else False
    return {
        "run_id": view.parent.name,
        "view": str(view),
        "uri": view.as_uri(),
        "browser_requested": launch,
        "browser_launched": launched,
    }


def _digest_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _redaction_values(run: Path) -> set[str]:
    manifest = run / "manifest.json"
    if not manifest.is_file():
        return set()
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    keys = {
        "id", "registry_id", "display_name", "machine", "hostname", "user",
        "username", "endpoint", "base_url", "fingerprint_hash",
    }
    values: set[str] = set()

    def visit(value, key: str | None = None):
        if isinstance(value, dict):
            for child_key, child in value.items():
                visit(child, child_key)
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif key in keys and isinstance(value, str) and len(value) >= 3:
            values.add(value)

    visit(data)
    return values


def _redacted_content(path: Path, values: set[str]) -> bytes:
    text = path.read_text(encoding="utf-8")
    for value in sorted(values, key=len, reverse=True):
        text = text.replace(value, "[redacted]")
    return text.encode("utf-8")


def export_redacted(reference: str, destination: Path | None = None) -> dict:
    """Export only explicitly shareable, derived views.

    The allowlist is deliberate. Canonical manifests, fingerprints, prompts,
    responses, ratings, reviewer traces, scoresheets, and environment files are
    never included even if a report-bundle file happens to reference them.
    """
    run = resolve_run(reference)
    selected = [run / name for name in SHAREABLE_VIEWS if (run / name).is_file()]
    if not selected:
        raise AdoptionError(f"run {run.name!r} has no generated shareable views")
    if destination is None:
        destination = workspace.ensure() / "exports" / f"{run.name}-redacted.zip"
    destination = Path(destination).expanduser().resolve()
    if destination.suffix.lower() != ".zip":
        raise AdoptionError("redacted export destination must end in .zip")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise AdoptionError(
            f"{destination} already exists; choose another path (exports are immutable)"
        )

    redactions = _redaction_values(run)
    rendered = {path: _redacted_content(path, redactions) for path in selected}
    manifest = {
        "schema": "aies-redacted-view-export/v1",
        "run_id": run.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "classification": "derived-shareable-views-only",
        "excluded_categories": [
            "credentials and environment files",
            "raw prompts and responses",
            "scoresheets and rating observations",
            "reviewer traces and qualification records",
            "machine and endpoint fingerprints",
        ],
        "files": [{"name": p.name, "sha256": _digest_bytes(rendered[p]),
                   "bytes": len(rendered[p])} for p in selected],
        "anonymized_values": len(redactions),
        "warning": (
            "This archive contains informational rendered views, not the full "
            "canonical evidence needed to reproduce or verify an assessment."
        ),
    }
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in selected:
            archive.writestr(path.name, rendered[path])
        archive.writestr("redacted-export-manifest.json",
                         json.dumps(manifest, indent=2))
    return {"run_id": run.name, "archive": str(destination), **manifest}


_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def starter_deployment(
    path: Path,
    *,
    deployment_id: str = "my-deployment",
    model: str = "replace-with-served-model-id",
    base_url: str = "http://127.0.0.1:1234/v1",
    api_key_env: str = "AIES_OPENAI_API_KEY",
    roles: list[str] | None = None,
) -> Path:
    """Write a non-secret OpenAI-compatible starter manifest if absent."""
    from . import registry

    target = Path(path).expanduser().resolve()
    if target.exists():
        raise AdoptionError(f"{target} already exists; starter files are never overwritten")
    if not registry.ID_PATTERN.fullmatch(deployment_id):
        raise AdoptionError(
            "deployment id must be 2-64 lowercase letters, numbers, dots, "
            "dashes, or underscores")
    if not model.strip():
        raise AdoptionError("model id cannot be empty")
    parsed_endpoint = urlparse(base_url)
    if parsed_endpoint.scheme not in ("http", "https") or not parsed_endpoint.netloc:
        raise AdoptionError(
            "endpoint must be a complete http:// or https:// base URL")
    if not _ENV_NAME.fullmatch(api_key_env):
        raise AdoptionError(
            "API-key environment variable must be a valid environment name")
    selected_roles = roles or ["subject"]
    if not selected_roles or any(role not in registry.KNOWN_ROLES
                                 for role in selected_roles):
        raise AdoptionError("roles must contain subject, judge, or both")
    payload = {
        "id": deployment_id,
        "runtime": "openai-compat",
        "model": model,
        "provenance": {"checksum": "sha256:endpoint-served"},
        "roles": selected_roles,
        "runtime_config": {
            "base_url": base_url.rstrip("/"),
            "api_key_env": api_key_env,
        },
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return target

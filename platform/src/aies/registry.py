"""Deployment registry (pipeline stage 1): what is qualified, and where.

A registry entry is a **deployment manifest** — the named tuple of a
model artifact, a runtime, its configuration, and its endpoint
(PLATFORM.md §5.1, D11). Qualification targets a deployment, not a bare
model, because a model's behavior is a property of model x quantization
x runtime x config — exactly what the environment fingerprint captures
(D7). The same model served two ways is two deployments and two
qualification subjects.

Entries are YAML files. IDs (deployment names) are stable and never
reused; entries are retired, not deleted. Capability flags are *claims
to be verified by discovery, never trusted* (AIES-AESQS-QP-01-R05).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from . import workspace

# A deployment must name itself, a runtime, a model identity, and bind
# to an exact artifact. context_window and family are recommended but
# optional (a discovered endpoint deployment may not know them).
REQUIRED_FIELDS = ("id", "runtime")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")


class RegistryError(Exception):
    pass


class AmbiguousDeployment(RegistryError):
    def __init__(self, model: str, options: list[str]):
        self.model = model
        self.options = options
        super().__init__(
            f"model {model!r} is served by multiple deployments: "
            f"{', '.join(options)}. Name the deployment, or pass "
            f"--runtime to disambiguate."
        )


def _entry_path(deployment_id: str) -> Path:
    return workspace.registry_dir() / f"{deployment_id}.yaml"


def _model_of(entry: dict) -> str:
    return str(entry.get("model") or entry.get("family") or entry.get("id"))


def validate_entry(entry: dict) -> list[str]:
    problems = []
    for f in REQUIRED_FIELDS:
        if f not in entry or entry[f] in (None, ""):
            problems.append(f"missing required field: {f}")
    if not (entry.get("model") or entry.get("family")):
        problems.append("missing model identity: set `model` (or `family`)")
    mid = str(entry.get("id", ""))
    if mid and not ID_PATTERN.match(mid):
        problems.append(
            f"id {mid!r} invalid: lowercase alphanumerics, dot, dash, underscore"
        )
    prov = entry.get("provenance") or {}
    if not str(prov.get("checksum", "")).startswith("sha256:"):
        problems.append(
            "provenance.checksum missing or not sha256: the deployment must "
            "bind to an exact model artifact (PLATFORM.md §5.1)"
        )
    return problems


def add(source_yaml: Path) -> dict:
    entry = yaml.safe_load(Path(source_yaml).read_text(encoding="utf-8"))
    if not isinstance(entry, dict):
        raise RegistryError(f"{source_yaml} does not contain a mapping")
    problems = validate_entry(entry)
    if problems:
        raise RegistryError("invalid registry entry:\n  - " + "\n  - ".join(problems))
    dest = _entry_path(entry["id"])
    if dest.exists():
        raise RegistryError(
            f"model id {entry['id']!r} already registered — ids are never "
            "reused; register a changed artifact under a new id"
        )
    dest.write_text(yaml.safe_dump(entry, sort_keys=False), encoding="utf-8")
    return entry


def get(model_id: str) -> dict:
    p = _entry_path(model_id)
    if not p.exists():
        raise RegistryError(f"model {model_id!r} is not registered (aies registry add …)")
    entry = yaml.safe_load(p.read_text(encoding="utf-8"))
    if entry.get("retired"):
        raise RegistryError(f"model {model_id!r} is retired")
    return entry


def list_entries(include_retired: bool = False) -> list[dict]:
    out = []
    for p in sorted(workspace.registry_dir().glob("*.yaml")):
        entry = yaml.safe_load(p.read_text(encoding="utf-8"))
        if entry.get("retired") and not include_retired:
            continue
        out.append(entry)
    return out


def retire(model_id: str) -> dict:
    p = _entry_path(model_id)
    if not p.exists():
        raise RegistryError(f"model {model_id!r} is not registered")
    entry = yaml.safe_load(p.read_text(encoding="utf-8"))
    entry["retired"] = True
    p.write_text(yaml.safe_dump(entry, sort_keys=False), encoding="utf-8")
    return entry


def resolve(ref: str, runtime: str | None = None) -> dict:
    """Resolve a qualification target to one deployment.

    `ref` is either a deployment id (exact) or a model name that may be
    served by several deployments. Ambiguity is surfaced, never guessed
    (PLATFORM.md D11).
    """
    direct = _entry_path(ref)
    if direct.exists():
        return get(ref)
    matches = [e for e in list_entries() if _model_of(e) == ref]
    if runtime:
        matches = [e for e in matches if e.get("runtime") == runtime]
    if not matches:
        raise RegistryError(
            f"{ref!r} is not a deployment id, and no registered deployment "
            f"serves model {ref!r}"
            + (f" on runtime {runtime!r}" if runtime else "")
            + " (try `aies registry list` or `aies discover`)"
        )
    if len(matches) > 1:
        raise AmbiguousDeployment(ref, [e["id"] for e in matches])
    return matches[0]


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s or "model"


def create_from_discovery(partial: dict) -> dict:
    """Turn a discovered partial manifest into a named deployment.

    The deployment id is `<runtime>-<model-slug>`; an already-registered
    id is left untouched (discovery is idempotent and never overwrites).
    Returns the entry with an added `_status` of created|exists.
    """
    runtime = partial.get("runtime", "unknown")
    model = partial.get("model") or partial.get("family") or "model"
    dep_id = f"{_slug(runtime)}-{_slug(model)}"
    dest = _entry_path(dep_id)
    if dest.exists():
        entry = yaml.safe_load(dest.read_text(encoding="utf-8"))
        entry["_status"] = "exists"
        return entry
    entry = {"id": dep_id, "kind": "deployment", **partial}
    problems = validate_entry(entry)
    if problems:
        raise RegistryError(
            f"discovered deployment {dep_id!r} is incomplete:\n  - "
            + "\n  - ".join(problems)
        )
    dest.write_text(yaml.safe_dump(entry, sort_keys=False), encoding="utf-8")
    entry["_status"] = "created"
    return entry

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

# Advisory usage roles a deployment may declare (optional). These say how you
# intend to use the deployment; they are NOT the organizational roles ROLE-01…14
# of the Shared Taxonomy, and they are not enforced — any deployment can still
# be qualified or passed to `--judge`. `roles: [judge]` simply lets a team see
# its judge pool (`aies judge available`).
KNOWN_ROLES = ("subject", "judge")


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
    roles = entry.get("roles")
    if roles is not None:
        if not isinstance(roles, list) or any(r not in KNOWN_ROLES for r in roles):
            problems.append(
                f"roles must be a list drawn from {list(KNOWN_ROLES)} "
                "(advisory usage tags; optional)"
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


#: fields that define a deployment's behavioral identity (D7/D11). Changing any
#: of these means "what runs" changed, so prior qualifications for the id may no
#: longer describe it — the environment fingerprint catches this on `verify`.
IDENTITY_FIELDS = ("runtime", "model", "quantization", "runtime_config")


def update(source_yaml: Path) -> dict:
    """Overwrite an EXISTING deployment entry in place, keeping its id — for
    config fixes (endpoint, api_key_env, generation defaults, roles). Fails if
    the id is not already registered (a new deployment uses add()).

    The returned entry carries a transient `_identity_changed` flag (True when a
    field in IDENTITY_FIELDS changed vs the stored copy); the flag is not
    persisted. Callers should warn on True: prior qualifications for this id may
    no longer describe what now runs (re-check with `aies qualification verify`).
    """
    entry = yaml.safe_load(Path(source_yaml).read_text(encoding="utf-8"))
    if not isinstance(entry, dict):
        raise RegistryError(f"{source_yaml} does not contain a mapping")
    problems = validate_entry(entry)
    if problems:
        raise RegistryError("invalid registry entry:\n  - " + "\n  - ".join(problems))
    dest = _entry_path(entry["id"])
    if not dest.exists():
        raise RegistryError(
            f"{entry['id']!r} is not registered — use `aies deployment add` to "
            "register a new deployment; update only edits an existing one"
        )
    old = yaml.safe_load(dest.read_text(encoding="utf-8"))
    identity_changed = any(old.get(f) != entry.get(f) for f in IDENTITY_FIELDS)
    dest.write_text(yaml.safe_dump(entry, sort_keys=False), encoding="utf-8")
    result = dict(entry)
    result["_identity_changed"] = identity_changed
    return result


def remove(model_id: str) -> dict:
    """Hard-delete a deployment entry so its id is free to reuse. Unlike
    retire() (which soft-marks the entry and keeps the id reserved for audit),
    remove() deletes the manifest file. Run history and QUAL records that
    reference the id are untouched."""
    p = _entry_path(model_id)
    if not p.exists():
        raise RegistryError(f"model {model_id!r} is not registered")
    entry = yaml.safe_load(p.read_text(encoding="utf-8"))
    p.unlink()
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

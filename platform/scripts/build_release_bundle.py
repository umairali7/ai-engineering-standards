"""Validate built distributions and emit a content-addressed release manifest."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[2]
PLATFORM = ROOT / "platform"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_revision() -> str | None:
    declared = os.environ.get("AIES_REVISION") or os.environ.get("GITHUB_SHA")
    if declared:
        return declared
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _generated_at() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    moment = (datetime.datetime.fromtimestamp(int(epoch), datetime.timezone.utc)
              if epoch else datetime.datetime.now(datetime.timezone.utc))
    return moment.isoformat()


def _project() -> dict:
    return tomllib.loads((PLATFORM / "pyproject.toml").read_text(
        encoding="utf-8"))["project"]


def _validate_wheel(path: Path, project: dict) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError(f"{path.name}: expected exactly one METADATA file")
        metadata = archive.read(metadata_names[0]).decode("utf-8")
        required = [f"Name: {project['name']}", f"Version: {project['version']}",
                    "License-Expression: Apache-2.0"]
        for marker in required:
            if marker not in metadata:
                raise ValueError(f"{path.name}: package metadata lacks {marker!r}")
        if not any(name.endswith(".dist-info/licenses/LICENSE") for name in names):
            raise ValueError(f"{path.name}: Apache license text is not packaged")


def _validate_sdist(path: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = archive.getnames()
        if not any(name.endswith("/LICENSE") for name in names):
            raise ValueError(f"{path.name}: Apache license text is not packaged")


def generate(dist: Path) -> dict:
    project = _project()
    wheels = sorted(dist.glob("*.whl"))
    sdists = sorted(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("release bundle requires exactly one wheel and one source distribution")
    _validate_wheel(wheels[0], project)
    _validate_sdist(sdists[0])
    artifacts = [{
        "filename": path.name,
        "media_type": ("application/vnd.python.wheel" if path.suffix == ".whl"
                       else "application/gzip"),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    } for path in sorted(wheels + sdists, key=lambda value: value.name)]
    manifest = {
        "kind": "aies-release-manifest",
        "schema_version": 1,
        "standard_version": "v0.4.0",
        "platform_distribution": project["name"],
        "platform_version": project["version"],
        "source_revision": _source_revision(),
        "generated_at": _generated_at(),
        "artifacts": artifacts,
        "claims": {
            "content_addressed": True,
            "license_validated": True,
            "signed": False,
            "provenance_attested": False,
        },
        "limitations": [
            "Hashes establish artifact identity, not safety or correctness.",
            "This local manifest is not a signature or SLSA provenance attestation.",
        ],
    }
    (dist / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (dist / "SHA256SUMS").write_text(
        "".join(f"{item['sha256']}  {item['filename']}\n" for item in artifacts),
        encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="validate wheel/sdist contents and emit release hashes")
    parser.add_argument("--dist", type=Path, default=PLATFORM / "dist")
    parser.add_argument("--build", action="store_true",
                        help="build wheel/sdist before validation (requires build)")
    args = parser.parse_args(argv)
    if args.build:
        subprocess.check_call([sys.executable, "-m", "build", "--outdir", str(args.dist)],
                              cwd=PLATFORM)
    manifest = generate(args.dist.resolve())
    print(f"release bundle: {manifest['platform_distribution']} "
          f"{manifest['platform_version']}")
    for artifact in manifest["artifacts"]:
        print(f"  {artifact['sha256']}  {artifact['filename']}")
    print(f"  manifest: {args.dist.resolve() / 'release-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

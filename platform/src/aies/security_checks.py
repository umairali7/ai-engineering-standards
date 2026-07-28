#!/usr/bin/env python3
"""Run reproducible local/CI security checks without system tool installation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import ssl
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


GITLEAKS_VERSION = "8.30.1"
GITLEAKS_BASE_URL = (
    "https://github.com/gitleaks/gitleaks/releases/download/"
    f"v{GITLEAKS_VERSION}"
)

# Digests published with the upstream v8.30.1 release. Keys are normalized
# (sys.platform, platform.machine()) pairs.
GITLEAKS_ASSETS = {
    ("darwin", "arm64"): (
        "gitleaks_8.30.1_darwin_arm64.tar.gz",
        "b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5",
    ),
    ("darwin", "x86_64"): (
        "gitleaks_8.30.1_darwin_x64.tar.gz",
        "dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709",
    ),
    ("linux", "aarch64"): (
        "gitleaks_8.30.1_linux_arm64.tar.gz",
        "e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080",
    ),
    ("linux", "arm64"): (
        "gitleaks_8.30.1_linux_arm64.tar.gz",
        "e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080",
    ),
    ("linux", "x86_64"): (
        "gitleaks_8.30.1_linux_x64.tar.gz",
        "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb",
    ),
    ("win32", "amd64"): (
        "gitleaks_8.30.1_windows_x64.zip",
        "d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e",
    ),
    ("win32", "arm64"): (
        "gitleaks_8.30.1_windows_arm64.zip",
        "b95f5e4f5c425cedca7ee203d9afd29597e692c4924a12ed42f970537c72cc0f",
    ),
    ("win32", "x86_64"): (
        "gitleaks_8.30.1_windows_x64.zip",
        "d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e",
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _asset_for(
    system: str | None = None,
    machine: str | None = None,
) -> tuple[str, str]:
    key = (
        (system or sys.platform).lower(),
        (machine or platform.machine()).lower(),
    )
    try:
        return GITLEAKS_ASSETS[key]
    except KeyError as exc:
        supported = ", ".join(
            f"{os_name}/{arch}" for os_name, arch in sorted(GITLEAKS_ASSETS)
        )
        raise RuntimeError(
            f"Gitleaks bootstrap does not support {key[0]}/{key[1]}; "
            f"supported targets: {supported}"
        ) from exc


def _default_cache_root() -> Path:
    configured = os.environ.get("AIES_TOOL_CACHE")
    if configured:
        return Path(configured).expanduser()
    if sys.platform == "win32" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "aies" / "tools"
    return (
        Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        / "aies"
        / "tools"
    )


def _git_root(path: Path) -> Path:
    """Resolve a repository or any directory inside one to its Git root."""
    candidate = path.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for current in (candidate, *candidate.parents):
        if (current / ".git").exists():
            return current
    raise RuntimeError(f"no Git repository contains {candidate}")


def _platform_root(repo: Path) -> Path:
    """Locate the AIES Python project within a source checkout."""
    nested = repo / "platform"
    if (nested / "pyproject.toml").is_file():
        return nested
    if (repo / "pyproject.toml").is_file():
        return repo
    raise RuntimeError(
        f"no AIES platform/pyproject.toml was found under {repo}")


def _ssl_context() -> ssl.SSLContext:
    try:
        import truststore
    except ImportError:
        pass
    else:
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    try:
        import certifi
    except ImportError:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def _source_revision(repo: Path) -> str:
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        completed = subprocess.run(  # noqa: S603
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(  # noqa: S310 - constant HTTPS origin
        url,
        headers={"User-Agent": f"aies-security-bootstrap/{GITLEAKS_VERSION}"},
    )
    with urllib.request.urlopen(  # noqa: S310 - constant HTTPS origin
        request,
        timeout=120,
        context=_ssl_context(),
    ) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def _extract_binary(archive: Path, destination: Path) -> None:
    """Extract only the named executable, never archive paths."""
    expected = "gitleaks.exe" if archive.suffix == ".zip" else "gitleaks"
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as bundle:
            candidates = [
                name
                for name in bundle.namelist()
                if not name.endswith("/") and Path(name).name == expected
            ]
            if len(candidates) != 1:
                raise RuntimeError(
                    f"expected one {expected} member; found {len(candidates)}"
                )
            with bundle.open(candidates[0]) as source, destination.open("wb") as out:
                shutil.copyfileobj(source, out)
    else:
        with tarfile.open(archive, "r:gz") as bundle:
            candidates = [
                member
                for member in bundle.getmembers()
                if member.isfile() and Path(member.name).name == expected
            ]
            if len(candidates) != 1:
                raise RuntimeError(
                    f"expected one {expected} member; found {len(candidates)}"
                )
            source = bundle.extractfile(candidates[0])
            if source is None:
                raise RuntimeError(f"could not read {expected} from {archive.name}")
            with source, destination.open("wb") as out:
                shutil.copyfileobj(source, out)
    if sys.platform != "win32":
        destination.chmod(0o755)


def _cache_is_valid(
    executable: Path,
    metadata_path: Path,
    asset_name: str,
    asset_sha256: str,
) -> bool:
    if not executable.is_file() or not metadata_path.is_file():
        return False
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        metadata.get("tool_version") == GITLEAKS_VERSION
        and metadata.get("asset") == asset_name
        and metadata.get("asset_sha256") == asset_sha256
        and metadata.get("binary_sha256") == _sha256(executable)
    )


def ensure_gitleaks(cache_root: Path | None = None) -> tuple[Path, dict]:
    """Return a checksum-verified cached Gitleaks executable and metadata."""
    asset_name, asset_sha256 = _asset_for()
    tool_dir = (cache_root or _default_cache_root()) / "gitleaks" / GITLEAKS_VERSION
    executable = tool_dir / ("gitleaks.exe" if sys.platform == "win32" else "gitleaks")
    metadata_path = tool_dir / "install-metadata.json"
    if _cache_is_valid(executable, metadata_path, asset_name, asset_sha256):
        return executable, json.loads(metadata_path.read_text(encoding="utf-8"))

    tool_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="bootstrap-",
        dir=str(tool_dir),
    ) as temporary:
        temp_dir = Path(temporary)
        archive = temp_dir / asset_name
        extracted = temp_dir / executable.name
        url = f"{GITLEAKS_BASE_URL}/{asset_name}"
        print(
            f"[security-bootstrap] downloading Gitleaks {GITLEAKS_VERSION}",
            flush=True,
        )
        _download(url, archive)
        observed = _sha256(archive)
        if observed != asset_sha256:
            raise RuntimeError(
                f"Gitleaks archive checksum mismatch for {asset_name}: "
                f"expected {asset_sha256}, observed {observed}"
            )
        _extract_binary(archive, extracted)
        metadata = {
            "kind": "aies-security-tool-install",
            "schema_version": 1,
            "tool": "gitleaks",
            "tool_version": GITLEAKS_VERSION,
            "asset": asset_name,
            "asset_sha256": asset_sha256,
            "binary_sha256": _sha256(extracted),
            "source": url,
        }
        os.replace(extracted, executable)
        metadata_path.write_text(
            json.dumps(metadata, indent=2) + "\n",
            encoding="utf-8",
        )
    return executable, metadata


def _tool_command(name: str) -> str:
    command = shutil.which(name)
    if command:
        return command
    suffix = ".exe" if sys.platform == "win32" else ""
    beside_python = Path(sys.executable).parent / f"{name}{suffix}"
    if beside_python.is_file():
        return str(beside_python)
    raise RuntimeError(
        f"{name} is not installed in the active Python environment; run "
        f'{sys.executable} -m pip install -e ".[security]" from platform/'
    )


def _run(command: list[str], *, cwd: Path) -> int:
    completed = subprocess.run(command, cwd=cwd, check=False)  # noqa: S603
    return completed.returncode


def run_history_scan(
    repo: Path,
    evidence_dir: Path,
    cache_root: Path | None = None,
) -> int:
    executable, install_metadata = ensure_gitleaks(cache_root)
    report_path = evidence_dir / "gitleaks.json"
    metadata = {
        **install_metadata,
        "kind": "aies-security-tool-evidence",
        "schema_version": 1,
        "scope": "all reachable commits and branches",
        "redaction_percent": 100,
        "repository": str(repo),
        "source_revision": _source_revision(repo),
    }
    (evidence_dir / "gitleaks-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "[secret-history] scanning all reachable commits (matched values redacted)",
        flush=True,
    )
    return _run(
        [
            str(executable),
            "git",
            "--log-opts=--all",
            "--redact=100",
            "--no-banner",
            "--no-color",
            "--report-format=json",
            f"--report-path={report_path}",
            ".",
        ],
        cwd=repo,
    )


def run_python_security(
    repo: Path,
    platform_root: Path,
    evidence_dir: Path,
) -> int:
    ruff = _tool_command("ruff")
    pip_audit = _tool_command("pip-audit")
    source_paths = ["src/aies", "scripts"]
    ignored = "S101,S110,S112,S603,S607"
    ruff_sarif = evidence_dir / "ruff-security.sarif"
    audit_json = evidence_dir / "pip-audit.json"
    versions = {}
    for name, command in (("ruff", ruff), ("pip-audit", pip_audit)):
        completed = subprocess.run(  # noqa: S603
            [command, "--version"],
            cwd=platform_root,
            check=True,
            capture_output=True,
            text=True,
        )
        versions[name] = completed.stdout.strip()
    metadata = {
        "kind": "aies-security-toolchain-evidence",
        "schema_version": 1,
        "tools": versions,
        "source_revision": _source_revision(repo),
        "sast_scope": source_paths,
        "dependency_scope": "platform/pyproject.toml resolved environment",
    }
    (evidence_dir / "security-toolchain.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print("[python-sast] running high-signal Ruff security rules", flush=True)
    sarif_code = _run(
        [
            ruff,
            "check",
            *source_paths,
            "--select",
            "S",
            "--ignore",
            ignored,
            "--output-format",
            "sarif",
            "--output-file",
            str(ruff_sarif),
        ],
        cwd=platform_root,
    )
    concise_code = _run(
        [
            ruff,
            "check",
            *source_paths,
            "--select",
            "S",
            "--ignore",
            ignored,
            "--output-format",
            "concise",
        ],
        cwd=platform_root,
    )
    print(
        "[dependency-audit] auditing resolved runtime dependencies",
        flush=True,
    )
    audit_code = _run(
        [
            pip_audit,
            ".",
            "--format=json",
            f"--output={audit_json}",
            "--progress-spinner=off",
        ],
        cwd=platform_root,
    )
    return max(sarif_code, concise_code, audit_code)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run AIES security checks with an automatically bootstrapped, "
            "checksum-pinned Gitleaks binary."
        )
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="repository root or a path inside it (default: current directory)",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "aies-security-evidence",
        help="machine-readable output directory (default: OS temporary directory)",
    )
    parser.add_argument(
        "--tool-cache",
        type=Path,
        default=None,
        help="override the user-local checksum-verified tool cache",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--history-only",
        action="store_true",
        help="run only the full-history secret scan",
    )
    mode.add_argument(
        "--python-only",
        action="store_true",
        help="run only Python SAST and dependency auditing",
    )
    args = parser.parse_args(argv)

    codes = []
    try:
        repo = _git_root(args.repo)
        platform_root = _platform_root(repo)
        evidence_dir = args.evidence_dir.expanduser().resolve()
        evidence_dir.mkdir(parents=True, exist_ok=True)
        if not args.python_only:
            codes.append(run_history_scan(repo, evidence_dir, args.tool_cache))
        if not args.history_only:
            codes.append(run_python_security(repo, platform_root, evidence_dir))
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"security checks could not start: {exc}", file=sys.stderr)
        return 2

    result = max(codes, default=0)
    status = "PASS" if result == 0 else "FAIL"
    print(f"security evidence: {status} · {evidence_dir}", flush=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())

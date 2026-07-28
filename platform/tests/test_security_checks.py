import hashlib
import importlib
import json
from pathlib import Path
import tarfile
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
def _module():
    return importlib.import_module("aies.security_checks")


def test_gitleaks_assets_are_pinned_for_supported_release_targets():
    security = _module()

    expected = {
        ("darwin", "arm64"): "b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5",
        ("darwin", "x86_64"): "dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709",
        ("linux", "aarch64"): "e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080",
        ("linux", "x86_64"): "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb",
        ("win32", "amd64"): "d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e",
        ("win32", "arm64"): "b95f5e4f5c425cedca7ee203d9afd29597e692c4924a12ed42f970537c72cc0f",
    }
    for target, checksum in expected.items():
        asset, actual = security._asset_for(*target)
        assert security.GITLEAKS_VERSION in asset
        assert actual == checksum

    with pytest.raises(RuntimeError, match="does not support"):
        security._asset_for("plan9", "mips")


@pytest.mark.parametrize("kind", ["zip", "tar"])
def test_gitleaks_extraction_ignores_archive_paths(tmp_path, kind):
    security = _module()
    payload = b"verified-gitleaks-binary"
    archive = tmp_path / (
        "gitleaks_8.30.1_windows_x64.zip"
        if kind == "zip"
        else "gitleaks_8.30.1_linux_x64.tar.gz"
    )
    member_name = "nested/gitleaks.exe" if kind == "zip" else "nested/gitleaks"
    if kind == "zip":
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr(member_name, payload)
            bundle.writestr("../../outside.txt", b"must-not-extract")
    else:
        source = tmp_path / "source"
        source.write_bytes(payload)
        with tarfile.open(archive, "w:gz") as bundle:
            bundle.add(source, arcname=member_name)
    destination = tmp_path / Path(member_name).name

    security._extract_binary(archive, destination)

    assert destination.read_bytes() == payload
    assert not (tmp_path.parent / "outside.txt").exists()


def test_cached_gitleaks_requires_matching_binary_digest(tmp_path):
    security = _module()
    executable = tmp_path / "gitleaks"
    executable.write_bytes(b"trusted")
    asset = "gitleaks_8.30.1_linux_x64.tar.gz"
    asset_sha = security._asset_for("linux", "x86_64")[1]
    metadata = tmp_path / "install-metadata.json"
    metadata.write_text(
        json.dumps({
            "tool_version": security.GITLEAKS_VERSION,
            "asset": asset,
            "asset_sha256": asset_sha,
            "binary_sha256": hashlib.sha256(b"trusted").hexdigest(),
        }),
        encoding="utf-8",
    )

    assert security._cache_is_valid(
        executable, metadata, asset, asset_sha)
    executable.write_bytes(b"tampered")
    assert not security._cache_is_valid(
        executable, metadata, asset, asset_sha)


def test_make_security_is_only_an_alias_for_canonical_cli():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "aies security .." in makefile
    assert "gitleaks git" not in makefile


def test_security_cli_forwards_cross_platform_options(monkeypatch, tmp_path):
    from aies import cli, security_checks

    observed = {}

    def fake_main(argv):
        observed["argv"] = argv
        return 0

    monkeypatch.setattr(security_checks, "main", fake_main)
    assert cli.main([
        "security", str(tmp_path), "--history-only",
        "--evidence-dir", str(tmp_path / "evidence"),
        "--tool-cache", str(tmp_path / "tools"),
    ]) == 0
    assert observed["argv"] == [
        "--repo", str(tmp_path),
        "--evidence-dir", str(tmp_path / "evidence"),
        "--tool-cache", str(tmp_path / "tools"),
        "--history-only",
    ]

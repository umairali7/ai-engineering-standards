import hashlib
import importlib
import io
import json
from pathlib import Path
import tarfile
import urllib.error
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


def test_download_retries_transient_github_failures(monkeypatch, tmp_path):
    security = _module()
    calls = []
    sleeps = []

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    def fake_urlopen(*_args, **_kwargs):
        calls.append(1)
        if len(calls) < 3:
            raise urllib.error.HTTPError(
                "https://example.invalid/tool", 500, "temporary", {}, None)
        return Response(b"verified-archive")

    monkeypatch.setattr(security.urllib.request, "urlopen", fake_urlopen)
    destination = tmp_path / "archive"
    security._download(
        "https://example.invalid/tool",
        destination,
        sleep=sleeps.append,
    )

    assert destination.read_bytes() == b"verified-archive"
    assert len(calls) == 3
    assert sleeps == [1, 2]


def test_security_startup_failure_retains_uploadable_diagnostics(
    monkeypatch, tmp_path,
):
    security = _module()
    repo = tmp_path / "repo"
    platform_root = repo / "platform"
    platform_root.mkdir(parents=True)
    evidence = tmp_path / "evidence"
    monkeypatch.setattr(security, "_git_root", lambda _path: repo)
    monkeypatch.setattr(security, "_platform_root", lambda _path: platform_root)
    monkeypatch.setattr(
        security,
        "run_history_scan",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("HTTP Error 500: Internal Server Error")
        ),
    )

    assert security.main([
        "--repo", str(repo),
        "--history-only",
        "--evidence-dir", str(evidence),
    ]) == 2
    assert json.loads((evidence / "gitleaks.json").read_text()) == []
    metadata = json.loads(
        (evidence / "gitleaks-metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "not-run"
    assert metadata["reason"] == "scanner-bootstrap-failed"


def test_clean_history_scan_retains_empty_report_and_final_status(
    monkeypatch, tmp_path,
):
    security = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    executable = tmp_path / "gitleaks"
    executable.write_bytes(b"scanner")
    install = {
        "tool": "gitleaks",
        "tool_version": security.GITLEAKS_VERSION,
    }
    monkeypatch.setattr(
        security, "ensure_gitleaks", lambda _cache=None: (executable, install))
    monkeypatch.setattr(security, "_run", lambda *_args, **_kwargs: 0)
    monkeypatch.setattr(security, "_source_revision", lambda _repo: "abc123")

    assert security.run_history_scan(repo, tmp_path) == 0
    assert json.loads((tmp_path / "gitleaks.json").read_text()) == []
    metadata = json.loads(
        (tmp_path / "gitleaks-metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "pass"
    assert metadata["exit_code"] == 0


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

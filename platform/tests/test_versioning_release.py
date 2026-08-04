import importlib.util
import io
import json
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

PLATFORM = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM / "src"))


def _release_module():
    path = PLATFORM / "scripts" / "build_release_bundle.py"
    spec = importlib.util.spec_from_file_location("aies_release_bundle", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _distributions(root: Path, *, license_expression="Apache-2.0"):
    wheel = root / "aies_platform-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "aies_platform-0.1.0.dist-info/METADATA",
            "Metadata-Version: 2.4\nName: aies-platform\nVersion: 0.1.0\n"
            f"License-Expression: {license_expression}\n")
        archive.writestr(
            "aies_platform-0.1.0.dist-info/licenses/LICENSE",
            "Apache License\nVersion 2.0")
    sdist = root / "aies_platform-0.1.0.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        payload = b"Apache License\nVersion 2.0"
        info = tarfile.TarInfo("aies_platform-0.1.0/LICENSE")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))
    return wheel, sdist


def test_version_inventory_separates_standard_platform_and_schemas(capsys):
    from aies import versioning
    from aies.cli import main

    value = versioning.inventory()
    assert value["standard"]["version"] == "v0.4.0"
    assert value["platform"]["version"] == "0.1.0"
    assert value["artifact_contracts"]["evidence_package"] == 6
    assert main(["version", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["kind"] == "aies-version-inventory"


def test_public_version_guidance_matches_runtime_contracts():
    from aies import versioning

    root = PLATFORM.parent
    inventory = versioning.inventory()
    standard = inventory["standard"]["version"]
    distribution = (
        f"aies-platform {inventory['platform']['version']}"
    )
    for relative in (
        "README.md", "docs/FAQ.md", "docs/VERSIONING_AND_RELEASES.md"
    ):
        content = (root / relative).read_text(encoding="utf-8")
        assert standard in content, relative
        assert distribution in content, relative

    stability = (root / "STABILITY.md").read_text(encoding="utf-8")
    assert "| **Evidence Package schema** | Platform | `6` |" in stability
    assert "| **Run Detail consumer view** (read-only) | Platform | `2` |" in stability
    assert "not the current AIES standards-corpus version" in stability


def test_release_bundle_validates_and_hashes_built_artifacts(tmp_path, monkeypatch):
    module = _release_module()
    wheel, sdist = _distributions(tmp_path)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    monkeypatch.setenv("AIES_REVISION", "abc123")

    manifest = module.generate(tmp_path)

    assert manifest["source_revision"] == "abc123"
    assert manifest["generated_at"].startswith("1970-01-01")
    assert [item["filename"] for item in manifest["artifacts"]] == sorted(
        [wheel.name, sdist.name])
    assert all(len(item["sha256"]) == 64 for item in manifest["artifacts"])
    assert manifest["claims"] == {
        "content_addressed": True,
        "license_validated": True,
        "signed": False,
        "provenance_attested": False,
    }
    assert (tmp_path / "release-manifest.json").is_file()
    assert len((tmp_path / "SHA256SUMS").read_text().splitlines()) == 2


def test_release_bundle_rejects_wrong_license_metadata(tmp_path):
    module = _release_module()
    _distributions(tmp_path, license_expression="MIT")

    with pytest.raises(ValueError, match="License-Expression"):
        module.generate(tmp_path)

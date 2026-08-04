"""Registry lifecycle: add (new only), update (existing in place, flags an
identity change), remove (hard-delete, frees the id) vs retire (soft, reserved).
"""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _manifest(tmp_path, **over):
    entry = {"id": "dep", "family": "demo", "runtime": "openai-compat",
             "model": "m", "context_window": 8192,
             "runtime_config": {"base_url": "http://localhost:8001/v1", "model": "m"},
             "provenance": {"source": "x", "checksum": "sha256:" + "0" * 64}}
    entry.update(over)
    p = tmp_path / f"{entry['id']}.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return p


def test_add_refuses_existing_update_requires_existing(ws, tmp_path):
    from aies import registry
    registry.add(_manifest(tmp_path))
    with pytest.raises(registry.RegistryError, match="already registered"):
        registry.add(_manifest(tmp_path))
    # update a never-registered id fails clearly
    with pytest.raises(registry.RegistryError, match="not registered"):
        registry.update(_manifest(tmp_path, id="ghost"))


def test_update_edits_in_place_and_flags_config_only_change(ws, tmp_path):
    from aies import registry
    registry.add(_manifest(tmp_path))
    # a pure config fix: change the api key env var name; identity unchanged
    upd = registry.update(_manifest(
        tmp_path,
        runtime_config={"base_url": "http://localhost:8001/v1", "model": "m",
                        "api_key_env": "MY_KEY"}))
    assert upd["_identity_changed"] is True   # runtime_config is an identity field
    stored = registry.get("dep")
    assert stored["runtime_config"]["api_key_env"] == "MY_KEY"
    assert "_identity_changed" not in stored  # transient flag never persisted

    # editing a non-identity field (roles) does NOT flag an identity change
    upd2 = registry.update(_manifest(
        tmp_path,
        runtime_config={"base_url": "http://localhost:8001/v1", "model": "m",
                        "api_key_env": "MY_KEY"},
        roles=["judge"]))
    assert upd2["_identity_changed"] is False
    assert registry.get("dep")["roles"] == ["judge"]


def test_supply_chain_provenance_validated(ws, tmp_path):
    import yaml
    from aies import registry
    prov = {"source": "x", "checksum": "sha256:" + "0" * 64,
            "signature": {"method": "openssf-model-signing", "reference": "oms://x",
                          "verified": True},
            "ai_bom": {"format": "cyclonedx-1.7", "reference": "./sbom.cdx.json"}}
    ok = yaml.safe_load(_manifest(tmp_path, provenance=prov).read_text(encoding="utf-8"))
    assert registry.validate_entry(ok) == []                 # valid shapes accepted
    bad = dict(ok, provenance={"checksum": "sha256:" + "0" * 64,
                               "signature": "not-a-mapping"})
    assert any("provenance.signature" in x for x in registry.validate_entry(bad))


def test_supply_chain_provenance_carried_into_evidence(ws, tmp_path):
    import json, yaml
    from aies import registry, engine, workspace
    entry = {"id": "signed", "family": "demo", "runtime": "mock", "model": "signed",
             "context_window": 8192,
             "provenance": {"source": "x", "checksum": "sha256:" + "0" * 64,
                            "signature": {"method": "openssf-model-signing",
                                          "reference": "oms://x"},
                            "ai_bom": "./sbom.cdx.json"}}
    p = tmp_path / "signed.yaml"; p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(p)
    run = engine.start_qualification("signed", "enterprise", "RT2", ["CA-05"], repeats=1)
    manifest = json.loads((workspace.run_dir(run["run_id"]) / "manifest.json").read_text())
    assert manifest["model"]["signature"]["method"] == "openssf-model-signing"
    assert manifest["model"]["ai_bom"] == "./sbom.cdx.json"


def test_remove_frees_id_retire_reserves_it(ws, tmp_path):
    from aies import registry
    registry.add(_manifest(tmp_path))

    # retire keeps the entry (id stays reserved -> add still refuses)
    registry.retire("dep")
    with pytest.raises(registry.RegistryError, match="already registered"):
        registry.add(_manifest(tmp_path))

    # remove hard-deletes -> id is free -> add succeeds again
    removed = registry.remove("dep")
    assert removed["id"] == "dep"
    with pytest.raises(registry.RegistryError, match="not registered"):
        registry.remove("dep")            # second remove fails cleanly
    registry.add(_manifest(tmp_path))     # id reusable now
    assert registry.get("dep")["id"] == "dep"


def test_bundled_deployment_examples_are_valid_and_unique():
    from aies import registry

    examples = Path(__file__).resolve().parents[1] / "examples" / "deployments"
    manifests = sorted(examples.glob("*.yaml"))
    assert manifests, "deployment example directory must not be empty"
    catalog = (examples / "README.md").read_text(encoding="utf-8")

    seen: dict[str, Path] = {}
    for manifest in manifests:
        entry = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        assert isinstance(entry, dict), f"{manifest.name} must contain a mapping"
        assert registry.validate_entry(entry) == [], manifest.name
        assert f"]({manifest.name})" in catalog, (
            f"{manifest.name} is missing from the deployment example catalogue"
        )
        deployment_id = entry["id"]
        if manifest.name.lower().startswith("local-"):
            assert f"`{deployment_id}`" in catalog, (
                f"{deployment_id} is missing from the local example table"
            )
        assert deployment_id not in seen, (
            f"duplicate deployment id {deployment_id!r} in "
            f"{seen[deployment_id].name} and {manifest.name}"
        )
        seen[deployment_id] = manifest

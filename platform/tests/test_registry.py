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

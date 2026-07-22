"""Qualification fingerprints bind to the execution environment that matters."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_remote_fingerprint_excludes_calling_laptop_from_trigger(monkeypatch):
    from aies import doctor
    runtime = {
        "id": "openai-compat", "version": "1", "execution_scope": "remote",
        "endpoint": "https://assessment.example/v1", "server_model": "subject-v3",
        "deployment_revision": "release-42", "settings": {"temperature": 0},
    }
    monkeypatch.setattr(doctor._platform, "node", lambda: "laptop-a")
    monkeypatch.setattr(doctor, "_ram_gb", lambda: 16.0)
    first = doctor.fingerprint(runtime)
    monkeypatch.setattr(doctor._platform, "node", lambda: "laptop-b")
    monkeypatch.setattr(doctor, "_ram_gb", lambda: 128.0)
    second = doctor.fingerprint(runtime)
    assert first["machine"] != second["machine"]  # provenance remains visible
    assert first["fingerprint_hash"] == second["fingerprint_hash"]
    assert first["binding_scope"] == "remote-deployment"
    assert "machine" not in first["binding_components"]


def test_local_fingerprint_remains_bound_to_host(monkeypatch):
    from aies import doctor
    runtime = {"id": "mock", "version": "1", "execution_scope": "local"}
    monkeypatch.setattr(doctor._platform, "node", lambda: "host-a")
    first = doctor.fingerprint(runtime)
    monkeypatch.setattr(doctor._platform, "node", lambda: "host-b")
    second = doctor.fingerprint(runtime)
    assert first["fingerprint_hash"] != second["fingerprint_hash"]
    assert first["binding_scope"] == "local-execution-environment"


def test_openai_compatible_adapter_classifies_local_and_remote_endpoints():
    from aies.adapters.openai_compat import OpenAICompatAdapter
    provenance = {"source": "endpoint", "checksum": "sha256:" + "a" * 64}
    remote = OpenAICompatAdapter()
    remote.load({
        "id": "hosted", "provenance": provenance,
        "runtime_config": {"base_url": "https://user:secret@example.test/v1?token=nope",
                           "model": "served", "deployment_revision": "r7"}})
    remote_fp = remote.fingerprint()
    assert remote_fp["execution_scope"] == "remote"
    assert remote_fp["endpoint"] == "https://example.test/v1"
    assert "secret" not in str(remote_fp) and "token" not in str(remote_fp)
    assert remote_fp["deployment_revision"] == "r7"

    local = OpenAICompatAdapter()
    local.load({"id": "local", "provenance": provenance,
                "runtime_config": {"base_url": "http://127.0.0.1:8000/v1",
                                   "model": "served"}})
    assert local.fingerprint()["execution_scope"] == "local"

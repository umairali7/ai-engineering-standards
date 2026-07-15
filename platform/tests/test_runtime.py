"""Runtime layer + deployment registry (M2/M3 bring-forward, PLATFORM.md D11)."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    # Keep the openai-compat probe from touching a real endpoint.
    monkeypatch.setenv("AIES_OPENAI_BASE_URL", "http://127.0.0.1:9/v1")
    return tmp_path


def test_doctor_reports_runtimes_and_never_raises(ws):
    from aies import doctor
    record = doctor.run_doctor()
    runtimes = {r["runtime"]: r for r in record["runtimes"]}
    assert "mock" in runtimes and runtimes["mock"]["available"] is True
    assert "openai-compat" in runtimes  # present but almost certainly unavailable
    assert "mock" in record["checks"]["runtimes_detected"]


def test_discover_creates_named_deployments(ws):
    from aies import registry, runtimes
    found = runtimes.discover_all()
    ids = []
    for partial in found:
        entry = registry.create_from_discovery(partial)
        ids.append(entry["id"])
    # The mock runtime advertises two models -> two deployments.
    assert "mock-mock-small" in ids and "mock-mock-large" in ids
    # Idempotent: a second discovery creates nothing new.
    again = [registry.create_from_discovery(p)["_status"] for p in runtimes.discover_all()]
    assert all(s == "exists" for s in again)


def test_resolve_by_deployment_id_and_by_model(ws):
    from aies import registry, runtimes
    for partial in runtimes.discover_all():
        registry.create_from_discovery(partial)
    # by deployment id
    assert registry.resolve("mock-mock-small")["id"] == "mock-mock-small"
    # by unique model name
    assert registry.resolve("mock-large")["id"] == "mock-mock-large"


def test_ambiguous_model_requires_disambiguation(ws, tmp_path):
    from aies import registry
    # Two deployments serving the same model on different runtimes.
    for rid, rt in (("dep-one", "mock"), ("dep-two", "openai-compat")):
        entry = {"id": rid, "runtime": rt, "model": "shared-model",
                 "runtime_config": {"base_url": "http://x/v1", "model": "shared-model"},
                 "provenance": {"source": "test", "checksum": "sha256:" + "0" * 64}}
        p = tmp_path / f"{rid}.yaml"
        p.write_text(yaml.safe_dump(entry), encoding="utf-8")
        registry.add(p)
    with pytest.raises(registry.AmbiguousDeployment) as ei:
        registry.resolve("shared-model")
    assert set(ei.value.options) == {"dep-one", "dep-two"}
    # --runtime disambiguates.
    assert registry.resolve("shared-model", runtime="mock")["id"] == "dep-one"


def test_qualify_targets_a_deployment(ws):
    from aies import engine, registry, runtimes
    for partial in runtimes.discover_all():
        registry.create_from_discovery(partial)
    manifest = engine.start_qualification(
        "mock-mock-small", "research", "RT2", ["CA-05"], repeats=1)
    assert manifest["model"]["registry_id"] == "mock-mock-small"

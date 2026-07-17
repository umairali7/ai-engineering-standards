"""Artifact verification: recompute a local artifact's SHA-256 and compare to
the deployment's declared checksum; surface signature status honestly."""

import hashlib
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _artifact(tmp_path, data=b"model-weights-bytes"):
    p = tmp_path / "model.bin"
    p.write_bytes(data)
    return p, "sha256:" + hashlib.sha256(data).hexdigest()


def _register(tmp_path, checksum, signature=None):
    from aies import registry
    prov = {"source": "local", "checksum": checksum}
    if signature is not None:
        prov["signature"] = signature
    entry = {"id": "art", "family": "demo", "runtime": "mock", "model": "art",
             "context_window": 8192, "provenance": prov}
    p = tmp_path / "art.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(p)


def test_checksum_match_and_mismatch(ws, tmp_path):
    from aies import verification
    art, digest = _artifact(tmp_path)

    _register(tmp_path, digest)
    res = verification.verify_artifact("art", str(art))
    assert res["checksum"]["match"] is True and res["ok"] is True

    from aies import registry
    registry.remove("art")
    _register(tmp_path, "sha256:" + "0" * 64)                 # wrong checksum
    res = verification.verify_artifact("art", str(art))
    assert res["checksum"]["match"] is False and res["ok"] is False


def test_endpoint_served_checksum_is_informational(ws, tmp_path):
    from aies import verification
    art, _ = _artifact(tmp_path)
    _register(tmp_path, "sha256:endpoint-served")
    res = verification.verify_artifact("art", str(art))
    assert res["checksum"]["match"] is None
    assert "endpoint-served" in res["checksum"]["note"]


def test_declared_signature_without_keys_is_not_a_false_pass(ws, tmp_path):
    from aies import verification
    art, digest = _artifact(tmp_path)
    _register(tmp_path, digest, signature={"method": "openssf-model-signing",
                                            "reference": "oms://x"})
    res = verification.verify_artifact("art", str(art))
    # checksum matches, but a declared signature we didn't check is surfaced,
    # not silently treated as verified
    assert res["checksum"]["match"] is True
    assert res["signature"]["status"] == "declared-not-checked"


def test_missing_artifact_errors(ws, tmp_path):
    from aies import verification
    _register(tmp_path, "sha256:" + "0" * 64)
    with pytest.raises(verification.VerificationError, match="artifact not found"):
        verification.verify_artifact("art", str(tmp_path / "nope.bin"))

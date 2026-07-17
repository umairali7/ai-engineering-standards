"""Verify a deployment's declared provenance against a local artifact.

The registry records `provenance.checksum` (and optionally
`provenance.signature`) as *declarations* — binding a deployment to an exact
artifact but not, by itself, proving the bytes on disk match. This module does
the actual verification when a local artifact is available:

- **Checksum** — recompute the artifact's SHA-256 and compare to the declared
  `provenance.checksum`. Always available (stdlib `hashlib`).
- **Signature** — best-effort detached-signature verification over the artifact
  bytes using the `cryptography` library if installed (Ed25519 or RSA public
  key in PEM). If `cryptography` is absent, the result is reported as
  *unverifiable* — never a false pass. Full Sigstore/OMS transparency-log
  verification is out of scope here; use cosign/model-signing externally and
  record the outcome.

This is the verification counterpart to the declaration support in registry.py
and the supply-chain crosswalk (CROSSWALK §3b).
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class VerificationError(Exception):
    pass


def sha256_file(path: str | Path, _chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(_chunk), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def _verify_signature(data: bytes, pubkey_pem: bytes, sig: bytes) -> tuple[str, str]:
    """Return (status, detail). status ∈ verified | failed | unverifiable."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.hazmat.primitives.asymmetric import padding, ec
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
    except Exception:
        return ("unverifiable",
                "the `cryptography` package is not installed — "
                "`pip install cryptography`, or verify with cosign/Sigstore externally")
    try:
        key = load_pem_public_key(pubkey_pem)
    except Exception as e:
        return ("failed", f"could not load public key: {e}")
    try:
        if isinstance(key, Ed25519PublicKey):
            key.verify(sig, data)
        elif hasattr(key, "verify") and isinstance(key, ec.EllipticCurvePublicKey):
            key.verify(sig, data, ec.ECDSA(hashes.SHA256()))
        else:  # assume RSA
            key.verify(sig, data, padding.PKCS1v15(), hashes.SHA256())
        return ("verified", f"{type(key).__name__} signature valid over the artifact")
    except Exception as e:
        return ("failed", f"signature did not verify: {e.__class__.__name__}")


def verify_artifact(deployment_id: str, artifact_path: str,
                    pubkey_path: str | None = None, sig_path: str | None = None,
                    runtime: str | None = None) -> dict:
    """Verify the on-disk artifact against the deployment's declared provenance.
    Returns a structured result with an overall `ok`."""
    from . import registry
    entry = registry.resolve(deployment_id, runtime=runtime)
    prov = entry.get("provenance") or {}
    p = Path(artifact_path)
    if not p.is_file():
        raise VerificationError(f"artifact not found: {artifact_path}")

    computed = sha256_file(p)
    declared = str(prov.get("checksum", ""))
    # A declared endpoint-served checksum can't be verified against a local file.
    if declared == "sha256:endpoint-served":
        checksum = {"declared": declared, "computed": computed, "match": None,
                    "note": "endpoint-served artifact; local checksum is informational only"}
    else:
        checksum = {"declared": declared or None, "computed": computed,
                    "match": (declared == computed) if declared else None}

    # Signature: use provided paths, else fall back to the manifest's declaration.
    sig_ref = sig_path or ((prov.get("signature") or {}).get("reference")
                           if isinstance(prov.get("signature"), dict) else None)
    signature = {"attempted": False, "status": "not-declared", "detail": ""}
    if pubkey_path and sig_ref:
        signature["attempted"] = True
        try:
            status, detail = _verify_signature(
                p.read_bytes(), Path(pubkey_path).read_bytes(), Path(sig_ref).read_bytes())
        except OSError as e:
            status, detail = "failed", f"could not read key/signature: {e}"
        signature["status"], signature["detail"] = status, detail
    elif prov.get("signature") or sig_ref:
        signature["status"] = "declared-not-checked"
        signature["detail"] = ("a signature is declared; pass --pubkey and "
                               "--signature to verify it, or verify via cosign/Sigstore")

    ok = bool(checksum.get("match")) and signature["status"] in (
        "verified", "not-declared", "declared-not-checked")
    return {"deployment": entry["id"], "artifact": str(p),
            "checksum": checksum, "signature": signature, "ok": ok}

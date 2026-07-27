"""Generic adapter for OpenAI-compatible HTTP endpoints.

Many local runtimes and hosted providers expose the same
chat-completions wire format; this adapter targets that format
generically. Endpoint and model name come from the registry entry:

    runtime: openai-compat
    runtime_config:
      base_url: http://localhost:11434/v1     # any compatible server
      model: <server-side model name>
      api_key_env: AIES_API_KEY               # optional; name of env var

Vendor-specific behavior beyond the common format belongs in a
dedicated out-of-tree adapter, not here (PLATFORM.md D9).
"""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
import urllib.parse

from .base import GenerationRequest, GenerationResponse, RuntimeAdapter

_SSL_CONTEXT: ssl.SSLContext | None = None


def _http_endpoint(value: str) -> str:
    """Return a normalized HTTP(S) endpoint or reject an unsafe URL scheme."""
    endpoint = value.rstrip("/")
    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError(
            "OpenAI-compatible endpoint must be an absolute http:// or https:// URL"
        )
    return endpoint


def _ssl_context() -> ssl.SSLContext:
    """A TLS context that verifies certs reliably across platforms.

    Precedence: an explicit SSL_CERT_FILE/SSL_CERT_DIR (e.g. a corporate CA)
    wins; otherwise use certifi's bundle if installed (fixes the common
    macOS "CERTIFICATE_VERIFY_FAILED — unable to get local issuer" where a
    fresh Python has no usable system store); otherwise the system default.
    Cached, since building a context parses the whole CA bundle."""
    global _SSL_CONTEXT
    if _SSL_CONTEXT is not None:
        return _SSL_CONTEXT
    if os.environ.get("SSL_CERT_FILE") or os.environ.get("SSL_CERT_DIR"):
        _SSL_CONTEXT = ssl.create_default_context()
    else:
        try:
            import certifi
            _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            _SSL_CONTEXT = ssl.create_default_context()
    return _SSL_CONTEXT


class OpenAICompatAdapter(RuntimeAdapter):
    adapter_id = "openai-compat"
    adapter_version = "1"

    #: env var supplying this runtime's default endpoint, and the runtime's
    #: conventional default URL (None for the generic adapter). Subclasses for
    #: named runtimes (Ollama, LM Studio, llama.cpp, MLX) override these; the
    #: default is always overridable via the env var or a deployment manifest.
    RUNTIME_ENV = "AIES_OPENAI_BASE_URL"
    RUNTIME_DEFAULT: str | None = None

    def __init__(self) -> None:
        self._base_url: str = ""
        self._model: str = ""
        self._api_key: str | None = None
        self._fingerprint_settings: dict = {}

    def load(self, registry_entry: dict) -> None:
        from .. import config
        cfg = registry_entry.get("runtime_config") or {}
        # Precedence: deployment manifest → env/.env → runtime conventional default.
        raw_base_url = str(
            cfg.get("base_url")
            or config.endpoint(self.RUNTIME_ENV, self.RUNTIME_DEFAULT)
            or ""
        )
        self._model = str(cfg.get("model", registry_entry.get("id", "")))
        self._fingerprint_settings = {
            key: value for key, value in cfg.items()
            if key not in ("base_url", "model", "api_key_env", "api_key")
        }
        self._deployment_revision = (
            cfg.get("deployment_revision") or cfg.get("revision")
            or registry_entry.get("deployment_revision") or "undeclared")
        self._served_checksum = ((registry_entry.get("provenance") or {}).get("checksum")
                                 or "undeclared")
        if not raw_base_url:
            raise ValueError(
                f"no endpoint for the {self.adapter_id} adapter: set "
                f"runtime_config.base_url in the deployment, or {self.RUNTIME_ENV} "
                "in the environment / .env"
            )
        self._base_url = _http_endpoint(raw_base_url)
        # A deployment MAY name its own key env var; otherwise use the default.
        key_env = cfg.get("api_key_env")
        self._api_key = os.environ.get(key_env) if key_env else config.openai_api_key()
        # Checksum verification is the responsibility of the server for
        # remote artifacts; record that verification was delegated.
        self._checksum_delegated = True

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": request.prompt}],
            **{k: v for k, v in request.parameters.items()
               if k in ("temperature", "max_tokens", "seed", "top_p")},
        }
        req = urllib.request.Request(  # noqa: S310 - base URL validated as HTTP(S)
            f"{self._base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}),
            },
            method="POST",
        )
        from .. import config
        url = f"{self._base_url}/chat/completions"
        timeout = float(request.parameters.get("timeout_s", config.request_timeout_s()))
        started = time.monotonic()
        try:
            with urllib.request.urlopen(  # noqa: S310 - URL validated as HTTP(S)
                    req, timeout=timeout, context=_ssl_context()) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:          # 4xx/5xx — server answered
            detail = ""
            try:
                detail = e.read().decode()[:300]
            except Exception:
                pass
            quota_exhausted = "insufficient_quota" in detail or "exceeded your current quota" in detail
            retry_after = ""
            if e.code == 429 and not quota_exhausted:
                raw_retry_after = str((e.headers or {}).get("Retry-After") or "").strip()
                if raw_retry_after and len(raw_retry_after) <= 80:
                    retry_after = (
                        f" Provider Retry-After: {raw_retry_after}; wait that long "
                        "before retrying.")
            hint = (
                ". The API key was accepted, but its OpenAI API project has no available quota. "
                "Check that the key belongs to the intended billed project; changing --parallel will not fix this."
                if e.code == 429 and quota_exhausted else
                ". The server is rate-limiting — lower --parallel."
                + retry_after
                if e.code == 429 else
                ". Check the model name and API key."
                if e.code in (400, 401, 403, 404) else ""
            )
            raise RuntimeError(
                f"{url} returned HTTP {e.code} {e.reason}"
                + (f": {detail}" if detail else "")
                + hint
            ) from e
        except TimeoutError as e:                    # genuinely timed out
            raise RuntimeError(
                f"no response from {url} within {timeout:.0f}s (timed out). "
                f"Raise AIES_REQUEST_TIMEOUT_S for a genuinely slow model, or "
                f"lower --parallel if the server is refusing concurrent calls."
            ) from e
        except (urllib.error.URLError, OSError) as e:  # unreachable / TLS / DNS
            reason = getattr(e, "reason", None) or e
            hint = (
                " — TLS certificate verification failed. Install CA certs "
                "(`pip install certifi`; on a python.org macOS build also run "
                "its 'Install Certificates.command'), or point SSL_CERT_FILE at "
                "your CA bundle."
                if "CERTIFICATE_VERIFY_FAILED" in str(reason) else
                " Check the endpoint is up and serving an OpenAI-compatible API "
                "(try `aies doctor` / `aies runtime <name>`)."
            )
            raise RuntimeError(f"could not reach {url} ({reason}).{hint}") from e
        latency_ms = int((time.monotonic() - started) * 1000)
        text = body["choices"][0]["message"]["content"]
        return GenerationResponse(
            text=text,
            usage={**body.get("usage", {}), "latency_ms": latency_ms},
            raw=body,
        )

    def capabilities(self) -> dict:
        return {
            "modalities": ["text"],
            "tool_use": "unknown",          # probed by discovery, not assumed
            "function_calling": "unknown",
            "structured_output": "unknown",
            "streaming": False,
            "max_context": "unknown",
        }

    def fingerprint(self) -> dict:
        parsed = urllib.parse.urlsplit(self._base_url)
        host = (parsed.hostname or "").lower()
        # Classification only; this code never binds a listening socket.
        local_hosts = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}  # noqa: S104
        endpoint_identity = urllib.parse.urlunsplit((
            parsed.scheme.lower(), parsed.netloc.split("@")[-1].lower(),
            parsed.path.rstrip("/"), "", ""))
        return {
            "id": self.adapter_id,
            "version": self.adapter_version,
            "execution_scope": "local" if host in local_hosts else "remote",
            "endpoint": endpoint_identity,
            "server_model": self._model,
            "deployment_revision": self._deployment_revision,
            "served_model_checksum": self._served_checksum,
            "settings": self._fingerprint_settings,
        }

    # Probing/discovery target the endpoint named by AIES_OPENAI_BASE_URL
    # (env or .env). There is no hard-coded host: unset means the runtime is
    # simply not configured. Vendor names never appear here — the adapter
    # speaks a wire format, not a brand (D9).
    @classmethod
    def _default_base_url(cls) -> str | None:
        from .. import config
        base = config.endpoint(cls.RUNTIME_ENV, cls.RUNTIME_DEFAULT)
        return _http_endpoint(base) if base else None

    @classmethod
    def probe_runtime(cls) -> dict:
        from .. import config
        base = cls._default_base_url()
        if not base:
            return {"available": False, "version": None,
                    "detail": f"{cls.RUNTIME_ENV} not set (env or .env)"}
        try:
            with urllib.request.urlopen(  # noqa: S310 - base is validated HTTP(S)
                    f"{base}/models", timeout=config.probe_timeout_s(),
                    context=_ssl_context()) as resp:
                ok = resp.status == 200
            return {"available": ok, "version": "openai-compatible",
                    "detail": f"endpoint reachable at {base}"}
        except Exception as e:
            return {"available": False, "version": None,
                    "detail": f"no OpenAI-compatible endpoint at {base} ({e.__class__.__name__})"}

    @classmethod
    def discover_deployments(cls) -> list[dict]:
        from .. import config
        base = cls._default_base_url()
        if not base:
            return []
        try:
            with urllib.request.urlopen(  # noqa: S310 - base is validated HTTP(S)
                    f"{base}/models", timeout=config.probe_timeout_s(),
                    context=_ssl_context()) as resp:
                body = json.loads(resp.read().decode())
        except Exception:
            return []
        out = []
        for m in body.get("data", []):
            name = m.get("id")
            if not name:
                continue
            out.append({
                "runtime": cls.adapter_id, "model": name,
                "runtime_config": {"base_url": base, "model": name},
                "provenance": {"source": f"served at {base}",
                               "checksum": "sha256:endpoint-served"},
            })
        return out

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
import time
import urllib.error
import urllib.request

from .base import GenerationRequest, GenerationResponse, RuntimeAdapter


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

    def load(self, registry_entry: dict) -> None:
        from .. import config
        cfg = registry_entry.get("runtime_config") or {}
        # Precedence: deployment manifest → env/.env → runtime conventional default.
        self._base_url = str(
            cfg.get("base_url")
            or config.endpoint(self.RUNTIME_ENV, self.RUNTIME_DEFAULT)
            or ""
        ).rstrip("/")
        self._model = str(cfg.get("model", registry_entry.get("id", "")))
        if not self._base_url:
            raise ValueError(
                f"no endpoint for the {self.adapter_id} adapter: set "
                f"runtime_config.base_url in the deployment, or {self.RUNTIME_ENV} "
                "in the environment / .env"
            )
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
        req = urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}),
            },
            method="POST",
        )
        from .. import config
        started = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=float(
                request.parameters.get("timeout_s", config.request_timeout_s())
            )) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.URLError as e:
            raise RuntimeError(f"runtime endpoint unreachable: {e}") from e
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
        return {
            "id": self.adapter_id,
            "version": self.adapter_version,
            "endpoint": self._base_url,
            "server_model": self._model,
            "settings": {},
        }

    # Probing/discovery target the endpoint named by AIES_OPENAI_BASE_URL
    # (env or .env). There is no hard-coded host: unset means the runtime is
    # simply not configured. Vendor names never appear here — the adapter
    # speaks a wire format, not a brand (D9).
    @classmethod
    def _default_base_url(cls) -> str | None:
        from .. import config
        base = config.endpoint(cls.RUNTIME_ENV, cls.RUNTIME_DEFAULT)
        return base.rstrip("/") if base else None

    @classmethod
    def probe_runtime(cls) -> dict:
        from .. import config
        base = cls._default_base_url()
        if not base:
            return {"available": False, "version": None,
                    "detail": f"{cls.RUNTIME_ENV} not set (env or .env)"}
        try:
            with urllib.request.urlopen(f"{base}/models", timeout=config.probe_timeout_s()) as resp:
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
            with urllib.request.urlopen(f"{base}/models", timeout=config.probe_timeout_s()) as resp:
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

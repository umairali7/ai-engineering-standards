"""Adapters for common local model runtimes.

Ollama, LM Studio, llama.cpp (llama-server), and MLX (mlx_lm.server) all
expose the OpenAI-compatible chat-completions wire format, so they reuse
the HTTP logic of OpenAICompatAdapter and differ only in two runtime
facts: the env var that overrides the endpoint, and the runtime's
conventional default URL. That conventional URL is the adapter's
knowledge of its target (PLATFORM.md D9), and is always overridable via
the env var or a deployment manifest.

`aies doctor` shows which of these is running; `aies discover` registers
whatever each serves as named deployments (e.g. ollama-llama3.1).
"""

from __future__ import annotations

from .openai_compat import OpenAICompatAdapter


class OllamaAdapter(OpenAICompatAdapter):
    adapter_id = "ollama"
    adapter_version = "1"
    RUNTIME_ENV = "AIES_OLLAMA_BASE_URL"
    RUNTIME_DEFAULT = "http://localhost:11434/v1"


class LMStudioAdapter(OpenAICompatAdapter):
    adapter_id = "lmstudio"
    adapter_version = "1"
    RUNTIME_ENV = "AIES_LMSTUDIO_BASE_URL"
    RUNTIME_DEFAULT = "http://localhost:1234/v1"


class LlamaCppAdapter(OpenAICompatAdapter):
    adapter_id = "llamacpp"
    adapter_version = "1"
    RUNTIME_ENV = "AIES_LLAMACPP_BASE_URL"
    RUNTIME_DEFAULT = "http://localhost:8080/v1"


class MLXAdapter(OpenAICompatAdapter):
    # "oMLX" / mlx_lm.server — Apple MLX serving on Apple Silicon.
    adapter_id = "mlx"
    adapter_version = "1"
    RUNTIME_ENV = "AIES_MLX_BASE_URL"
    RUNTIME_DEFAULT = "http://localhost:8080/v1"

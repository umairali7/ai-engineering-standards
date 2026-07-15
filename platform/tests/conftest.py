"""Shared test setup.

Neutralize every runtime endpoint to a closed port by default so the
suite is hermetic — a real Ollama/LM Studio/llama.cpp/MLX server that
happens to be running on the developer's machine must not leak into
discovery or doctor results. Individual tests override as needed.
"""

import pytest

CLOSED = "http://127.0.0.1:9/v1"


@pytest.fixture(autouse=True)
def _neutralize_runtime_endpoints(monkeypatch):
    for var in ("AIES_OPENAI_BASE_URL", "AIES_OLLAMA_BASE_URL",
                "AIES_LMSTUDIO_BASE_URL", "AIES_LLAMACPP_BASE_URL",
                "AIES_MLX_BASE_URL"):
        monkeypatch.setenv(var, CLOSED)
    # Keep the liveness probe near-instant so tests don't wait on the
    # closed endpoints above.
    monkeypatch.setenv("AIES_PROBE_TIMEOUT_S", "0.25")

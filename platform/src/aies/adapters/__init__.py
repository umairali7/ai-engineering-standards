"""Runtime adapter discovery.

Adapters are the sole boundary between the engine and any model runtime
or hosted provider (PLATFORM.md §8). Vendor- and runtime-specific code
lives in adapters and nowhere else (D9). Discovery uses entry points so
out-of-tree adapters need no core changes; built-ins are registered as
a fallback when the package is run un-installed.
"""

from __future__ import annotations

from importlib import metadata

from .base import RuntimeAdapter


def discovered() -> dict[str, type[RuntimeAdapter]]:
    adapters: dict[str, type[RuntimeAdapter]] = {}
    # Built-ins first; entry points may shadow them.
    from .mock import MockAdapter
    from .openai_compat import OpenAICompatAdapter
    from .local_runtimes import (LlamaCppAdapter, LMStudioAdapter,
                                 MLXAdapter, OllamaAdapter)
    adapters["mock"] = MockAdapter
    adapters["openai-compat"] = OpenAICompatAdapter
    adapters["ollama"] = OllamaAdapter
    adapters["lmstudio"] = LMStudioAdapter
    adapters["llamacpp"] = LlamaCppAdapter
    adapters["mlx"] = MLXAdapter
    try:
        eps = metadata.entry_points(group="aies.adapters")
        for ep in eps:
            try:
                adapters[ep.name] = ep.load()
            except Exception:  # a broken plugin must not break discovery
                continue
    except Exception:
        pass
    return adapters


def resolve(runtime_id: str) -> type[RuntimeAdapter]:
    adapters = discovered()
    if runtime_id not in adapters:
        raise KeyError(
            f"no runtime adapter {runtime_id!r} installed "
            f"(available: {', '.join(sorted(adapters))})"
        )
    return adapters[runtime_id]

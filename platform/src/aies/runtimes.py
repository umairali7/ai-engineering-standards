"""Runtime abstraction: probe installed runtimes and discover deployments.

Everything the engine does against a model goes through a runtime
adapter (PLATFORM.md §8). This module orchestrates the adapters'
optional probe/discovery operations so that `aies doctor` can report
what runtimes are present and `aies discover` can turn what they serve
into named deployments (PLATFORM.md D11). No vendor- or runtime-
specific code lives here — only in the adapters themselves.
"""

from __future__ import annotations

from .adapters import discovered


def probe_all() -> list[dict]:
    """Probe every installed adapter's runtime. Never raises."""
    out = []
    for name, cls in sorted(discovered().items()):
        try:
            probe = cls.probe_runtime()
        except Exception as e:  # a broken adapter must not break doctor
            probe = {"available": False, "version": None,
                     "detail": f"probe raised {e.__class__.__name__}"}
        out.append({"runtime": name, "adapter_version": getattr(cls, "adapter_version", "?"),
                    **probe})
    return out


def discover_all() -> list[dict]:
    """Collect candidate deployments from every installed adapter."""
    found = []
    for name, cls in sorted(discovered().items()):
        try:
            for dep in cls.discover_deployments():
                dep.setdefault("runtime", name)
                found.append(dep)
        except Exception:
            continue
    return found

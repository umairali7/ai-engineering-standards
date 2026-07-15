"""Example out-of-tree runtime adapter.

This module lives OUTSIDE the aies package to demonstrate PLATFORM.md's
M3 exit criterion: a runtime adapter can be written against the
published contract and discovered via entry points without any change
to the core engine. It depends only on the public contract class.

To register it (in the external package's pyproject.toml):

    [project.entry-points."aies.adapters"]
    reverse = "aies_reverse_adapter:ReverseAdapter"

After `pip install`, `aies plugins` lists it and `aies discover` /
`aies qualify --runtime reverse` use it — no core edits.

The adapter itself is intentionally trivial (it echoes the prompt
reversed) so the example stays about the *contract*, not the model.
"""

from __future__ import annotations

from aies.adapters.base import (ADAPTER_CONTRACT_VERSION, GenerationRequest,
                                GenerationResponse, RuntimeAdapter)


class ReverseAdapter(RuntimeAdapter):
    adapter_id = "reverse"
    adapter_version = "1"
    contract_version = ADAPTER_CONTRACT_VERSION

    def load(self, registry_entry: dict) -> None:
        self._entry = registry_entry

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            text=request.prompt[::-1],
            usage={"chars": len(request.prompt)},
            raw={"adapter": self.adapter_id},
        )

    def capabilities(self) -> dict:
        return {"modalities": ["text"], "tool_use": False,
                "function_calling": False, "structured_output": False,
                "streaming": False, "max_context": 4096}

    def fingerprint(self) -> dict:
        return {"id": self.adapter_id, "version": self.adapter_version,
                "device": "none", "settings": {}}

    @classmethod
    def probe_runtime(cls) -> dict:
        return {"available": True, "version": cls.adapter_version,
                "detail": "example out-of-tree adapter"}

    @classmethod
    def discover_deployments(cls) -> list[dict]:
        return [{"runtime": cls.adapter_id, "model": "reverse-demo",
                 "provenance": {"source": "example", "checksum": "sha256:" + "r" * 64}}]

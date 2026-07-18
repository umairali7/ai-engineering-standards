"""Deterministic offline adapter for demonstration and testing.

Produces stable, seedable pseudo-responses so the full pipeline —
records, fingerprints, scoring hooks, reports — can be exercised with
no model installed. Responses are obviously synthetic; the adapter
declares itself in provenance, so mock evidence can never masquerade
as qualification evidence for a real model.
"""

from __future__ import annotations

import hashlib
import json

from .base import GenerationRequest, GenerationResponse, RuntimeAdapter


class MockAdapter(RuntimeAdapter):
    adapter_id = "mock"
    adapter_version = "1"

    def __init__(self) -> None:
        self._entry: dict | None = None

    def load(self, registry_entry: dict) -> None:
        # The mock has no artifact; it accepts any checksum but records
        # what it was bound to.
        self._entry = registry_entry

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        digest = hashlib.sha256(request.prompt.encode()).hexdigest()
        # Judge-aware: when driven as a reviewer/judge, the prompt asks for a
        # strict EV1-EV6 JSON object. Emit a deterministic, parseable one so the
        # WHOLE pipeline — including auto-scoring and the assessment decision —
        # runs fully offline (this is what `make demo` exercises). The scores are
        # obviously synthetic and the adapter self-declares in provenance, so
        # mock evidence can never masquerade as a real model's qualification.
        if self._is_review_prompt(request.prompt):
            return GenerationResponse(
                text=self._mock_scores(digest),
                usage={"prompt_chars": len(request.prompt), "latency_ms": 0},
                raw={"adapter": self.adapter_id, "digest": digest, "mode": "judge"},
            )
        text = (
            "[mock-adapter deterministic response]\n"
            f"prompt-digest: {digest[:16]}\n"
            "This synthetic response exists to exercise the qualification "
            "pipeline offline. It makes no claim to correctness; a human "
            "rater scoring it against the rubric should be able to apply "
            "every anchor, including the 0 anchors."
        )
        return GenerationResponse(
            text=text,
            usage={"prompt_chars": len(request.prompt), "latency_ms": 0},
            raw={"adapter": self.adapter_id, "digest": digest},
        )

    @staticmethod
    def _is_review_prompt(prompt: str) -> bool:
        return "qualification reviewer" in prompt and '"EV1"' in prompt

    @staticmethod
    def _mock_scores(digest: str) -> str:
        # Deterministic per-response scores in {3,4} — high enough to pass gates
        # so the offline demo yields a decisional result, but seeded from the
        # digest so different responses differ (exercises aggregation/CI bounds).
        dims = ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")
        scores = {d: 3 + (int(digest[i], 16) % 2) for i, d in enumerate(dims)}
        return json.dumps({**scores, "findings": []})

    def capabilities(self) -> dict:
        return {
            "modalities": ["text"],
            "tool_use": False,
            "function_calling": False,
            "structured_output": False,
            "streaming": False,
            "max_context": 8192,
        }

    def fingerprint(self) -> dict:
        return {"id": self.adapter_id, "version": self.adapter_version,
                "device": "none", "settings": {}}

    @classmethod
    def probe_runtime(cls) -> dict:
        # The mock runtime is always "present" — it needs nothing installed.
        return {"available": True, "version": cls.adapter_version,
                "detail": "deterministic offline runtime (no host dependency)"}

    @classmethod
    def discover_deployments(cls) -> list[dict]:
        # Two synthetic deployments so `aies discover` and multi-runtime
        # ambiguity can be exercised offline.
        return [
            {"runtime": cls.adapter_id, "model": "mock-small",
             "quantization": "none", "context_window": 8192,
             "provenance": {"source": "mock runtime", "checksum": "sha256:" + "m" * 64}},
            {"runtime": cls.adapter_id, "model": "mock-large",
             "quantization": "none", "context_window": 32768,
             "provenance": {"source": "mock runtime", "checksum": "sha256:" + "n" * 64}},
        ]

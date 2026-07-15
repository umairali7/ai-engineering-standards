"""The runtime adapter contract (PLATFORM.md §8).

Four operations, nothing more. The Test Runner owns retries and
timeouts; adapters execute exactly what they are asked.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field

# The runtime-adapter contract is versioned and stable as of M3
# (PLATFORM.md §8). Out-of-tree adapters declare the contract major
# version they target; the core accepts matching majors. Breaking the
# contract requires a superseding ADR (D10).
ADAPTER_CONTRACT_VERSION = "1.0"


@dataclass
class GenerationRequest:
    prompt: str
    parameters: dict = field(default_factory=dict)  # temperature, max_tokens, seed…


@dataclass
class GenerationResponse:
    text: str
    usage: dict = field(default_factory=dict)       # tokens, latency_ms as reported
    raw: dict = field(default_factory=dict)         # adapter-native payload, verbatim


class RuntimeAdapter(abc.ABC):
    """Implementations MUST be stateless across load() calls and MUST
    fail loudly on checksum mismatch (PLATFORM.md §8)."""

    #: stable adapter identifier; part of every result record's provenance
    adapter_id: str = "abstract"
    adapter_version: str = "0"
    #: contract major this adapter targets; must match ADAPTER_CONTRACT_VERSION's major
    contract_version: str = ADAPTER_CONTRACT_VERSION

    @abc.abstractmethod
    def load(self, registry_entry: dict) -> None:
        """Acquire/attach the model in the registry entry; verify checksum."""

    @abc.abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Execute one inference request. No unrequested retries."""

    @abc.abstractmethod
    def capabilities(self) -> dict:
        """Declare support: modalities, tool/function calling, structured
        output, streaming, maximum context."""

    @abc.abstractmethod
    def fingerprint(self) -> dict:
        """Report the runtime component of the environment fingerprint:
        id, version, device placement, relevant settings."""

    # ---- Optional runtime-discovery operations (PLATFORM.md §8, D11) ----
    # Best-effort and non-fatal: an adapter that cannot probe its runtime
    # reports available=False rather than raising, so `aies doctor` never
    # fails because a runtime is absent.

    @classmethod
    def probe_runtime(cls) -> dict:
        """Detect whether this runtime is present on the host.

        Returns {available: bool, version: str|None, detail: str}. The
        default reports the runtime as undetectable (a runtime with no
        probe is neither confirmed present nor absent)."""
        return {"available": False, "version": None,
                "detail": f"{cls.adapter_id}: no runtime probe implemented"}

    @classmethod
    def discover_deployments(cls) -> list[dict]:
        """Enumerate candidate deployments this runtime can serve.

        Returns a list of partial deployment manifests (without ids;
        the caller names them). The default discovers nothing."""
        return []

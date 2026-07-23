"""Subject-specific execution contracts, separate from runtime adapters."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from pathlib import Path

from .adapters import resolve
from .adapters.base import GenerationRequest, GenerationResponse

EXECUTOR_CONTRACT_VERSION = "1.0"


class ExecutorError(RuntimeError):
    pass


class SubjectExecutor(abc.ABC):
    """Interact with one subject kind and expose explicit execution semantics."""

    executor_id = "abstract"
    executor_version = "0"
    contract_version = EXECUTOR_CONTRACT_VERSION
    subject_kinds: tuple[str, ...] = ()

    @abc.abstractmethod
    def declaration(self) -> dict:
        """Return the durable execution contract recorded with evidence."""


class RuntimeGenerationExecutor(SubjectExecutor):
    """Deployment executor that delegates inference to a RuntimeAdapter."""

    executor_id = "runtime-generation"
    executor_version = "1.0"
    subject_kinds = ("ai_deployment", "ai_system")

    def __init__(self, registry_entry: dict):
        self.registry_entry = registry_entry
        self.runtime_adapter = resolve(registry_entry["runtime"])()
        self._loaded = False

    def load(self) -> None:
        self.runtime_adapter.load(self.registry_entry)
        self._loaded = True

    @property
    def adapter_id(self) -> str:
        return self.runtime_adapter.adapter_id

    @property
    def adapter_version(self) -> str:
        return self.runtime_adapter.adapter_version

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self._loaded:
            raise ExecutorError("runtime generation executor is not loaded")
        return self.runtime_adapter.generate(request)

    def capabilities(self) -> dict:
        return self.runtime_adapter.capabilities()

    def fingerprint(self) -> dict:
        return self.runtime_adapter.fingerprint()

    def declaration(self) -> dict:
        return {
            "contract": "aies-subject-executor/v1",
            "executor_id": self.executor_id,
            "executor_version": self.executor_version,
            "subject_kinds": list(self.subject_kinds),
            "interaction": "generation-request-response",
            "runtime_adapter": {
                "id": self.adapter_id,
                "version": self.adapter_version,
                "contract_version": self.runtime_adapter.contract_version,
                "runtime": self.registry_entry.get("runtime"),
                "deployment_id": self.registry_entry.get("id"),
            },
            "claim_boundary": (
                "Execution collects responses; it does not score, qualify, "
                "or authorize the subject."),
        }


@dataclass(frozen=True)
class RepositoryAuditRequest:
    repository: Path
    attestations: dict | None = None
    risk_tier: str | None = None
    record: bool = True


class RepositoryAuditExecutor(SubjectExecutor):
    """First non-runtime executor: deterministic repository evidence."""

    executor_id = "deterministic-repository-audit"
    executor_version = "1.0"
    subject_kinds = ("repository",)

    def execute(self, request: RepositoryAuditRequest) -> dict:
        from . import audit
        return audit.run_audit(
            request.repository,
            attestations=request.attestations,
            rt=request.risk_tier,
            record=request.record,
        )

    def declaration(self) -> dict:
        return {
            "contract": "aies-subject-executor/v1",
            "executor_id": self.executor_id,
            "executor_version": self.executor_version,
            "subject_kinds": list(self.subject_kinds),
            "interaction": "read-only-repository-observation",
            "runtime_adapter": None,
            "claim_boundary": (
                "Repository checks establish observed practice evidence only; "
                "they do not establish deployment competency or correctness."),
        }

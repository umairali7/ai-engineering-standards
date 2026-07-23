from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest


def _sha(value: str) -> str:
    return "sha256:" + value * 64


def test_subject_descriptor_covers_envisioned_subject_shapes():
    from aies import subjects

    fixtures = [
        subjects.build("model-1", kind="ai_deployment", display_name="Model"),
        subjects.repository_descriptor(
            "repo-1", display_name="Repository", commit="abc123"),
        subjects.build("agent-1", kind="agent", display_name="Agent"),
        subjects.build("mcp-1", kind="mcp_server", display_name="MCP Server"),
        subjects.build("rag-1", kind="rag_system", display_name="RAG System"),
        subjects.build("pipe-1", kind="pipeline", display_name="Pipeline"),
    ]
    composite = subjects.build(
        "system-1",
        kind="composite",
        display_name="Composite",
        components=[
            subjects.component_reference(
                "agent-1", kind="agent", role="orchestrates"),
            subjects.component_reference(
                "mcp-1", kind="mcp_server", role="uses",
                evidence_transfer="explicit-mapping-required"),
        ],
    )
    fixtures.append(composite)
    assert all(subjects.validate(fixture) == [] for fixture in fixtures)
    assert all(
        component["evidence_transfer"] != "reference-only"
        for component in composite["components"])


def test_legacy_manifest_normalizes_without_mutating_source():
    from aies import subjects

    legacy = {
        "run_id": "run-legacy",
        "subject": {
            "id": "deployment-1", "kind": "ai_deployment",
            "display_name": "Deployment", "executor_kind": "deployment",
        },
        "model": {"registry_id": "deployment-1", "checksum": _sha("a")},
        "environment_fingerprint": {"fingerprint_hash": _sha("b")},
    }
    original = copy.deepcopy(legacy)
    normalized = subjects.normalize_manifest(legacy)
    assert legacy == original
    assert normalized["schema"] == subjects.RUN_MANIFEST_SCHEMA
    assert normalized["subject"]["schema"] == subjects.SUBJECT_SCHEMA
    assert normalized["execution"]["compatibility_mode"] is True
    assert subjects.compatibility(legacy)["mode"] == "legacy-read-compatible"


def test_runtime_and_repository_executors_are_independent(monkeypatch, tmp_path):
    from aies import audit, executors

    runtime = executors.RuntimeGenerationExecutor({
        "id": "mock-deployment", "runtime": "mock", "family": "mock",
    })
    runtime.load()
    assert runtime.declaration()["runtime_adapter"]["id"] == "mock"

    monkeypatch.setattr(
        audit, "run_audit",
        lambda repository, **kwargs: {
            "repository": str(repository), "options": kwargs})
    repository = executors.RepositoryAuditExecutor()
    result = repository.execute(executors.RepositoryAuditRequest(tmp_path))
    assert repository.declaration()["runtime_adapter"] is None
    assert result["repository"] == str(tmp_path)


def test_typed_event_append_replay_and_conflict(tmp_path, monkeypatch):
    from aies import evidence_events

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    event = evidence_events.build(
        event_type="observation",
        subject_id="subject-1",
        instrument_id="instrument-1",
        modality="controlled-scenario",
        source="fixture",
        source_record_id="record-1",
        source_digest=_sha("c"),
        adapter_profile="fixture/v1",
        payload={"result": "observed"},
    )
    first = evidence_events.append("run-1", event)
    second = evidence_events.append("run-1", copy.deepcopy(event))
    assert first == second
    replay = evidence_events.replay([event, copy.deepcopy(event)])
    assert replay["events_replayed"] == 1
    assert replay["duplicates_ignored"] == 1
    conflicting = copy.deepcopy(event)
    conflicting["payload"]["result"] = "different"
    with pytest.raises(evidence_events.EvidenceEventError):
        evidence_events.replay([event, conflicting])


def test_legacy_run_migration_is_idempotent_and_source_preserving(
        tmp_path, monkeypatch):
    from aies import evidence_events

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    run = tmp_path / "workspace" / "runs" / "run-legacy"
    (run / "responses").mkdir(parents=True)
    (run / "ratings").mkdir()
    manifest = {
        "run_id": "run-legacy",
        "model": {"registry_id": "deployment", "checksum": _sha("d")},
        "environment_fingerprint": {
            "fingerprint_hash": _sha("e"), "runtime": "mock"},
        "status": "aggregated",
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    response = {
        "run_id": "run-legacy", "scenario_id": "SC-1", "repeat": 1,
        "area": "CA-05", "risk_tier": "RT2",
        "request": {"prompt_hash": _sha("f")},
        "recorded_at": "2026-01-01T00:01:00+00:00",
    }
    rating = {
        "rates_response": "SC-1-r1.json", "scenario_id": "SC-1", "repeat": 1,
        "scores": {f"EV{i}": 3 for i in range(1, 7)},
        "provenance": {
            "rater": "fixture", "rater_kind": "automated",
            "timestamp": "2026-01-01T00:02:00+00:00",
        },
    }
    paths = {
        run / "manifest.json": manifest,
        run / "responses" / "SC-1-r1.json": response,
        run / "ratings" / "SC-1-r1-fixture.json": rating,
    }
    for path, value in paths.items():
        path.write_text(json.dumps(value), encoding="utf-8")
    before = {path: path.read_bytes() for path in paths}
    first = evidence_events.migrate_run("run-legacy", write=True)
    second = evidence_events.migrate_run("run-legacy", write=True)
    assert first["events_written"] == second["events_written"] == 4
    assert first["replay"]["events_replayed"] == 4
    assert all(path.read_bytes() == content for path, content in before.items())


def test_evidence_adapter_profiles_disclose_semantics_and_incompatibility():
    from aies import evidence_adapters

    inspect = evidence_adapters.get("aies-inspect-eval-log/v1")
    sarif = evidence_adapters.get("aies-sarif-2.1.0/v1")
    repository_analysis = evidence_adapters.get(
        "aies-repository-analysis/v1")
    repository_conformance = evidence_adapters.get(
        "aies-repository-conformance/v1")
    assert evidence_adapters.validate(inspect) == []
    assert evidence_adapters.validate(sarif) == []
    assert evidence_adapters.validate(repository_analysis) == []
    assert evidence_adapters.validate(repository_conformance) == []
    assert inspect["privacy"]["secrets"] == "prohibited"
    assert sarif["decision_use"] == "informational-only"
    assert repository_analysis["decision_use"] == "informational-only"
    assert repository_conformance["decision_use"] == "informational-only"
    assert "correctness" in repository_analysis["scoring_semantics"]
    assert "ML0 through ML4" in repository_conformance["scoring_semantics"]
    assert evidence_adapters.compatibility(inspect, sarif)["compatible"] is False

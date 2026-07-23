from __future__ import annotations

import json
from pathlib import Path


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_sarif_bridge_preserves_findings_and_limits_claim(tmp_path, monkeypatch):
    from aies import interop

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    source = _write(tmp_path / "result.sarif", {
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "ExampleScan", "semanticVersion": "1.2.3",
                                "rules": [{"id": "EX001", "name": "Example"}]}},
            "invocations": [{"executionSuccessful": True, "exitCode": 0}],
            "results": [{
                "ruleId": "EX001",
                "level": "error",
                "message": {"text": "example finding"},
                "locations": [{"physicalLocation": {
                    "artifactLocation": {"uri": "src/app.py"},
                    "region": {"startLine": 7, "startColumn": 2}}}],
                "partialFingerprints": {"primaryLocationLineHash": "abc"},
                "baselineState": "new",
                "suppressions": [],
                "fixes": [{"description": {"text": "fix it"}}],
            }],
        }],
    })
    result = interop.import_sarif(source)
    normalized = json.loads(Path(result["artifact"]).read_text(encoding="utf-8"))
    assert result["findings"] == 1
    assert normalized["findings"][0]["rule_id"] == "EX001"
    assert normalized["findings"][0]["locations"][0]["start_line"] == 7
    assert "correctness" in normalized["semantics"]["does_not_establish"]
    roundtrip = interop.export_sarif(
        Path(result["artifact"]), tmp_path / "roundtrip.sarif")
    exported = json.loads(Path(roundtrip["artifact"]).read_text(encoding="utf-8"))
    out_finding = exported["runs"][0]["results"][0]
    assert out_finding["ruleId"] == "EX001"
    assert out_finding["level"] == "error"
    assert out_finding["locations"][0]["physicalLocation"]["region"]["startLine"] == 7
    assert exported["properties"]["aies"]["limitation"]


def test_inspect_bridge_imports_only_explicit_aies_scores(
        tmp_path, monkeypatch):
    from aies import interop

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    run = tmp_path / "ws" / "runs" / "run-1"
    (run / "responses").mkdir(parents=True)
    (run / "ratings").mkdir()
    _write(run / "responses" / "SC-CA05-001-r1.json", {
        "scenario_id": "SC-CA05-001", "repeat": 1,
    })
    source = _write(tmp_path / "inspect.json", {
        "samples": [
            {
                "id": "sample-1",
                "metadata": {"aies": {"scenario_id": "SC-CA05-001"}},
                "scores": {"aies": {"value": {
                    "EV1": 4, "EV2": 3, "EV3": 4,
                    "EV4": 3, "EV5": 3, "EV6": 4}}},
            },
            {"id": "unmapped", "scores": {"accuracy": {"value": 0.9}}},
        ],
    })
    result = interop.import_inspect("run-1", source)
    assert result["imported"] == 1
    assert result["skipped_samples"] == 1
    loss = json.loads(Path(result["loss_report"]).read_text(encoding="utf-8"))
    assert loss["samples_seen"] == 2
    assert loss["samples_skipped"][0]["sample_id"] == "unmapped"


def test_inspect_export_uses_explicit_portable_profile(tmp_path, monkeypatch):
    from aies import interop

    monkeypatch.setattr(interop.evalexport, "export_run", lambda _run: {
        "run": {"run_id": "run-1", "model": "subject"},
        "items": [{
            "scenario_id": "SC-CA05-001", "repeat": 1, "area": "CA-05",
            "prompt": "task", "response": "answer",
            "scores": {"EV1": 4, "EV2": 3, "EV3": 4,
                       "EV4": 3, "EV5": 3, "EV6": 4},
            "findings": [], "grounding_diagnostics": None,
        }],
    })
    result = interop.export_inspect("run-1", tmp_path / "inspect-export.json")
    exported = json.loads(Path(result["artifact"]).read_text(encoding="utf-8"))
    assert exported["schema"] == "aies-inspect-eval-log-profile/v1"
    assert exported["samples"][0]["metadata"]["aies"]["scenario_id"] == "SC-CA05-001"
    assert exported["samples"][0]["scores"]["aies"]["value"]["EV1"] == 4


def test_experimental_contracts_are_machine_readable():
    platform = Path(__file__).resolve().parents[1]
    for name in ("subject-descriptor-v1.schema.json",
                 "evidence-event-v1.schema.json"):
        schema = json.loads(
            (platform / "contracts" / name).read_text(encoding="utf-8"))
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["title"].endswith("(experimental)")

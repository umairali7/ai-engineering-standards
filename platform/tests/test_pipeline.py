"""End-to-end M1 pipeline smoke test using the mock adapter and a
temporary workspace: register -> doctor -> qualify -> score -> resume
-> report. Exercises the M1 exit criteria offline."""

import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _register(tmp_path):
    from aies import registry
    entry = {
        "id": "demo-model-q4",
        "family": "demo",
        "parameters": 7.0e9,
        "quantization": "q4",
        "runtime": "mock",
        "license": "apache-2.0",
        "context_window": 8192,
        "modalities": ["text"],
        "capabilities": {"tool_use": False},
        "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64},
    }
    src = tmp_path / "demo.yaml"
    src.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(src)


def test_registry_rejects_missing_checksum(ws, tmp_path):
    from aies import registry
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump({"id": "x", "family": "f", "runtime": "mock",
                                   "context_window": 1}), encoding="utf-8")
    with pytest.raises(registry.RegistryError):
        registry.add(bad)


def test_registry_ids_never_reused(ws, tmp_path):
    from aies import registry
    _register(tmp_path)
    with pytest.raises(registry.RegistryError):
        _register(tmp_path)


def test_full_pipeline_offline(ws, tmp_path):
    from aies import engine, rating, report, workspace

    _register(tmp_path)
    manifest = engine.start_qualification(
        "demo-model-q4", "enterprise", "RT3", ["CA-05"], repeats=2)
    run_id = manifest["run_id"]

    rdir = workspace.run_dir(run_id)
    responses = list((rdir / "responses").glob("*.json"))
    expected = sum(a["planned_items"] for a in manifest["areas"])  # suite-dependent
    assert len(responses) == expected

    # Response records are append-only.
    with pytest.raises(FileExistsError):
        workspace.write_json(responses[0], {"tamper": True})

    # Fill the scoresheet as a human rater would.
    sheet = json.loads((rdir / "scoresheet.json").read_text(encoding="utf-8"))
    sheet["rater"] = {"name": "Test Rater", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {"EV1": 3, "EV2": 3, "EV3": 3, "EV4": 3, "EV5": 3, "EV6": 3}
    rating.ingest_scores(run_id, sheet)

    pkg = engine.aggregate(run_id)
    area = pkg["areas"]["CA-05"]
    assert area["n_scored"] == expected
    assert area["n_distinct_scenarios"] < area["n_scored"]
    assert area["sample_adequacy_basis"] == "distinct_scenarios"
    assert area["decisional"] is False          # repeats do not fill distinct RT3 breadth
    assert area["gates_passed"] is True
    assert area["cl"] == "CL2"
    assert area["al_envelope"]["RT2"] == "AL2"
    assert "no grant" in pkg["grant_status"]

    md = report.render_markdown(run_id)
    assert "NON-DECISIONAL" in md
    assert "NO GRANT" in md.upper()
    assert pkg["suite_versions"]["CA-05"].startswith("suite-sha256:")
    assert "fingerprint" in md.lower()


def test_report_only_resume_starts_a_fresh_command_clock(
        ws, tmp_path, monkeypatch):
    from aies import cli, engine, rating, workspace

    _register(tmp_path)
    manifest = engine.start_qualification(
        "demo-model-q4", "coder", "RT1", ["CA-05"], repeats=1)
    run_id = manifest["run_id"]
    run_dir = workspace.run_dir(run_id)
    sheet = json.loads(
        (run_dir / "scoresheet.json").read_text(encoding="utf-8"))
    sheet["rater"] = {"name": "Test Rater", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {
            f"EV{index}": 3 for index in range(1, 7)}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)
    stale = json.loads(
        (run_dir / "progress.json").read_text(encoding="utf-8"))
    stale["started_epoch"] = 1.0
    workspace.write_json(
        run_dir / "progress.json", stale, overwrite=True)
    monkeypatch.setenv("AIES_JUDGE", "")

    assert cli.main(["qualify", "--resume", run_id, "--json"]) == 0

    refreshed = json.loads(
        (run_dir / "progress.json").read_text(encoding="utf-8"))
    assert refreshed["stage"] == "report-generation"
    assert refreshed["total_elapsed_seconds"] < 60


def test_unscored_sheet_rejected(ws, tmp_path):
    from aies import engine, rating, workspace
    _register(tmp_path)
    manifest = engine.start_qualification(
        "demo-model-q4", "coder", "RT2", ["CA-05"], repeats=1)
    run_id = manifest["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    sheet["rater"] = {"name": "Test Rater", "kind": "human"}
    # leave scores as None -> must be rejected (all runs fully scored)
    with pytest.raises(rating.RatingError):
        rating.ingest_scores(run_id, sheet)


def test_low_scores_require_findings(ws, tmp_path):
    from aies import engine, rating, workspace
    _register(tmp_path)
    manifest = engine.start_qualification(
        "demo-model-q4", "security", "RT2", ["CA-05"], repeats=1)
    run_id = manifest["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    sheet["rater"] = {"name": "Test Rater", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {"EV1": 1, "EV2": 3, "EV3": 3, "EV4": 3, "EV5": 3, "EV6": 3}
        item["findings"] = []  # missing findings for the 1
    with pytest.raises(rating.RatingError):
        rating.ingest_scores(run_id, sheet)


def test_multiple_ratings_resolve_to_one_statistical_evidence_item(ws, tmp_path):
    """A second human rates the same responses; it must not double n or
    artificially narrow the confidence interval (ADR-0012)."""
    from aies import engine, rating, workspace
    _register(tmp_path)
    manifest = engine.start_qualification(
        "demo-model-q4", "coder", "RT2", ["CA-05"], repeats=1)
    run_id = manifest["run_id"]
    original = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                          .read_text(encoding="utf-8"))
    for name, score in (("Rater One", 3), ("Rater Two", 4)):
        sheet = json.loads(json.dumps(original))
        sheet["rater"] = {"name": name, "kind": "human"}
        for item in sheet["items"]:
            item["scores"] = {dimension: score for dimension in
                              ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
        rating.ingest_scores(run_id, sheet)

    package = engine.aggregate(run_id)
    area = package["areas"]["CA-05"]
    expected_items = len(original["items"])
    assert area["raw_ratings"] == expected_items * 2
    assert area["resolved_evidence_items"] == expected_items
    assert area["n_scored"] == expected_items
    assert all(dimension["n"] == expected_items
               for dimension in area["dimensions"].values())
    assert area["dimensions"]["EV1"]["mean"] == 3.0
    assert package["evidence_items"]["items"][0]["resolution_method"] == (
        "conservative-adjacent-human-consensus")


def test_major_divergence_requires_immutable_human_disposition(ws, tmp_path):
    from aies import engine, rating, workspace
    _register(tmp_path)
    manifest = engine.start_qualification(
        "demo-model-q4", "coder", "RT2", ["CA-05"], repeats=1)
    run_id = manifest["run_id"]
    original = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                          .read_text(encoding="utf-8"))
    for name, score in (("Rater One", 4), ("Rater Two", 1)):
        sheet = json.loads(json.dumps(original))
        sheet["rater"] = {"name": name, "kind": "human"}
        for item in sheet["items"]:
            item["scores"] = {dimension: score for dimension in
                              ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
            if score <= 2:
                item["findings"] = [{"dimension": "EV1", "score": score,
                                     "finding": "material divergence fixture"}]
        rating.ingest_scores(run_id, sheet)

    package = engine.aggregate(run_id)
    assert package["evidence_items"]["resolved"] == 0
    assert package["evidence_items"]["unresolved"] == len(original["items"])
    assert package["areas"]["CA-05"]["n_scored"] == 0

    first = original["items"][0]["response_record"]
    scores = {dimension: 3 for dimension in
              ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.resolve_item(run_id, first, scores, resolver="Lead Assessor",
                        rationale="resolved against the scenario anchors")
    with pytest.raises(FileExistsError):
        rating.resolve_item(run_id, first, scores, resolver="Lead Assessor",
                            rationale="attempted overwrite")
    replay = engine.aggregate(run_id)
    assert replay["evidence_items"]["resolved"] == 1
    assert replay["areas"]["CA-05"]["n_scored"] == 1

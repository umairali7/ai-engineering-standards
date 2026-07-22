"""ECM is a traceable, task-mapped informational view over scored evidence."""

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def _register(tmp_path):
    from aies import registry
    entry = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    path = tmp_path / "cand.yaml"
    path.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(path)


def test_ecm_groups_existing_families_and_labels_small_samples(tmp_path, monkeypatch):
    from aies import ecm, engine, rating, workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    run_id = run["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {f"EV{x}": 3 for x in range(1, 7)}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)

    matrix = ecm.engineering_capability_matrix(run_id)
    assert matrix["status"] == "informational"
    assert matrix["mapping"]["kind"] == "aies-engineering-tasks-v1"
    code_generation = next(task for task in matrix["tasks"] if task["task_id"] == "ET-04")
    assert code_generation["status"] == "observed"
    assert any(task["status"] == "not assessed" for task in matrix["tasks"])
    assert matrix["rows"]
    assert all(row["area"] == "CA-05" for row in matrix["rows"])
    assert all(row["adequacy"] == "non-decisional" for row in matrix["rows"])
    assert all(row["scenario_ids"] for row in matrix["rows"])
    assert "NOT A QUALIFICATION" in ecm.render_markdown(matrix)
    assert "ET-04 Code Generation" in ecm.render_markdown(matrix)


def test_ecm_writer_emits_json_markdown_and_html(tmp_path, monkeypatch):
    from aies import ecm, engine, rating, workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    run_id = run["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {f"EV{x}": 3 for x in range(1, 7)}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)
    matrix = ecm.engineering_capability_matrix(run_id)

    for format, marker in (("json", '"kind"'), ("markdown", "# Engineering"), ("html", "<!doctype html>")):
        path = ecm.write_matrix(matrix, format)
        assert path.exists()
        assert marker in path.read_text(encoding="utf-8")
    html = ecm.render_html(matrix)
    assert "Direct evidence sample" in html
    assert "Scenario-family evidence and traceability" in html
    assert "Task Capability Profile" in ecm.render_capability_summary_html(matrix)


def test_deployment_guidance_is_bounded_to_ecm_evidence(tmp_path, monkeypatch):
    from aies import engine, guidance, rating, workspace

    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    sheet = json.loads((workspace.run_dir(run["run_id"]) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {f"EV{x}": 3 for x in range(1, 7)}
    rating.ingest_scores(run["run_id"], sheet)
    engine.aggregate(run["run_id"])
    rendered = guidance.render_markdown(run["run_id"])
    assert "Use with human review" in rendered
    assert "Code Generation" in rendered
    assert "not assessed" in rendered

"""Run transcript: one readable view joining prompt + answer + scores,
so a reviewer never has to open per-response JSON files by hand."""

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
    entry = {"id": "demo", "family": "demo", "runtime": "mock", "model": "demo",
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "demo.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def test_transcript_joins_prompt_answer_and_scores(ws, tmp_path):
    import json
    from aies import engine, rating, transcript, workspace

    _register(tmp_path)
    run = engine.start_qualification("demo", "coder", "RT2", ["CA-05"], repeats=1)
    run_id = run["run_id"]

    # the response records now store the actual prompt text (self-contained)
    resp = sorted((workspace.run_dir(run_id) / "responses").glob("*.json"))[0]
    rec = json.loads(resp.read_text(encoding="utf-8"))
    assert rec["request"]["prompt"] and len(rec["request"]["prompt"]) > 20

    # before scoring, transcript renders task + answer and marks "not yet scored"
    md = transcript.render_markdown(run_id)
    assert "Run Transcript" in md and "Model response" in md
    assert "not yet scored" in md
    assert rec["scenario_id"] in md

    # after scoring, the transcript shows the scores inline
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run_id, sheet)

    md2 = transcript.render_markdown(run_id)
    assert "not yet scored" not in md2
    assert "EV1 **3**" in md2 and "Tester" in md2
    # expected qualities from the suite are surfaced for the reviewer
    assert "Expected qualities:" in md2

    # area filter and json form
    assert transcript.render_markdown(run_id, area="CA-99") .count("##") == 0
    data = json.loads(transcript.render_json(run_id))
    assert data["items"] and data["items"][0]["prompt"] and data["items"][0]["response"]
    assert data["items"][0]["ratings"]

"""Multi-phase journeys (Task #6): loading, prompt threading, and that a
journey run flows through the existing scoring pipeline tagged to the
right competency areas."""

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


def _register(tmp_path, model_id="cand"):
    from aies import registry
    entry = {"id": model_id, "family": "demo", "runtime": "mock", "model": model_id,
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / f"{model_id}.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def test_shipped_journeys_load_and_validate():
    from aies import journeys
    items = journeys.list_journeys()
    ids = {j["id"] for j in items}
    assert {"JOURNEY-01", "JOURNEY-02"} <= ids
    j, ver = journeys.load_journey("JOURNEY-01")
    assert ver.startswith("journey-sha256:")
    assert len(j["steps"]) == 5
    # steps span multiple competency areas (lifecycle breadth within one journey)
    assert len({s["area"] for s in j["steps"]}) >= 4


def test_step_prompt_threading():
    from aies import journeys
    prior = [{"id": "s1", "area": "CA-02", "phase": "P05", "response": "REQ-TEXT"},
             {"id": "s2", "area": "CA-04", "phase": "P07", "response": "ARCH-TEXT"}]
    step = {"id": "s3", "prompt": "prev only: {{prior_response}}\nall:\n{{prior}}"}
    out = journeys.render_step_prompt(step, prior)
    assert "prev only: ARCH-TEXT" in out          # immediately prior
    assert "REQ-TEXT" in out and "ARCH-TEXT" in out  # full transcript
    # a step with no placeholders is returned unchanged
    assert journeys.render_step_prompt({"id": "x", "prompt": "static"}, prior) == "static"


def test_journey_run_tags_steps_by_area_and_flows_through_pipeline(ws, tmp_path):
    from aies import engine, workspace
    _register(tmp_path)
    manifest = engine.start_journey("cand", "enterprise", "JOURNEY-01", repeats=1)
    assert manifest["kind"] == "journey"
    assert manifest["risk_tier"] == "RT2"

    # One response per step, each tagged with the step's competency area.
    responses = sorted((workspace.run_dir(manifest["run_id"]) / "responses").glob("*.json"))
    assert len(responses) == 5
    recs = [workspace.read_json(p) for p in responses]
    areas = {r["area"] for r in recs}
    assert {"CA-02", "CA-04", "CA-05", "CA-06", "CA-10"} == areas
    assert all("journey" in r and r["journey"]["id"] == "JOURNEY-01" for r in recs)

    # The whole downstream pipeline consumes it unchanged: score -> aggregate.
    from aies import rating
    sheet = json.loads((workspace.run_dir(manifest["run_id"]) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    sheet["rater"] = {"name": "Rater", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(manifest["run_id"], sheet)
    pkg = engine.aggregate(manifest["run_id"])
    # Evidence package now has one competency area per journey step.
    assert set(pkg["areas"]) == {"CA-02", "CA-04", "CA-05", "CA-06", "CA-10"}
    # A single journey is depth, not volume -> non-decisional (1 item/area).
    assert all(not d["decisional"] for d in pkg["areas"].values())


def test_journey_threading_is_real_at_runtime(ws, tmp_path, monkeypatch):
    """The mock echoes a digest of the prompt; step 2's recorded prompt must
    contain step 1's response text (threading actually happened)."""
    from aies import engine, workspace
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    calls = {}

    def capturing_generate(self, request):
        # Return a marker the next step's {{prior_response}} will embed.
        idx = len(calls)
        calls[idx] = request.prompt
        return GenerationResponse(text=f"RESPONSE-{idx}", usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", capturing_generate)

    _register(tmp_path)
    engine.start_journey("cand", "research", "JOURNEY-02", repeats=1)
    # JOURNEY-02 step 2 uses {{prior_response}} -> must contain "RESPONSE-0".
    assert any("RESPONSE-0" in p for p in calls.values())

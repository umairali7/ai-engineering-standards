"""Capability profile: --all-areas expands to CA-01…CA-12, and
capability_profile() lays out an aggregated run's per-area results (CL,
decisional, gates, AL at the scoped tier) with human-readable area names."""

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
    entry = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "cand.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def test_all_area_codes_are_the_twelve():
    from aies import runner
    codes = runner.all_area_codes()
    assert codes == [f"CA-{n:02d}" for n in range(1, 13)]


def test_decisional_sample_plan_exposes_shortfalls_and_required_repeats():
    from aies import engine, runner
    areas = runner.all_area_codes()
    plan = engine.plan_qualification("RT2", areas, subject_kind="ai")
    assert len(plan["areas"]) == 12
    assert any(not row["decisional_if_scored"] for row in plan["areas"])
    assert plan["uniform_repeats_for_all_areas"] >= 1
    assert "API Design" in plan["unassessed_tasks"]


def test_capability_profile_lays_out_scored_areas(ws, tmp_path):
    from aies import engine, rating, workspace, capabilities

    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2",
                                     ["CA-04", "CA-05", "CA-07"], repeats=1)
    rid = run["run_id"]
    sheet = json.loads((workspace.run_dir(rid) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Tester", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(rid, sheet)
    engine.aggregate(rid)

    prof = capabilities.capability_profile(rid)
    assert prof["subject"] == "cand" and prof["risk_tier"] == "RT2"
    areas = {r["area"]: r for r in prof["areas"]}
    assert set(areas) == {"CA-04", "CA-05", "CA-07"}
    # human-readable role name is surfaced (not just the code)
    assert areas["CA-07"]["name"] == "Security & Privacy Engineering"
    # each area carries its own CL + AL-at-tier, and small samples are flagged
    assert areas["CA-05"]["cl"].startswith("CL")
    assert areas["CA-05"]["al_at_rt"] is not None
    assert areas["CA-05"]["decisional"] is False  # 7 < RT2 minimum of 30


def test_capability_profile_needs_an_aggregated_run(ws, tmp_path):
    from aies import engine, capabilities, compare
    _register(tmp_path)
    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    # not aggregated yet -> clear error, not a crash
    with pytest.raises(compare.CompareError):
        capabilities.capability_profile(run["run_id"])

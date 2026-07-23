"""Empirical calibration harness (CALIBRATION.md Phase 2). Pure analysis over a
panel of models of known-varying ability — testable without models. The harness
must (a) confirm a scenario that separates strong from weak, and (b) FLAG the
failure modes design-time review can't see: no discrimination, too-easy, noisy,
and gameable (twin inconsistency)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

ABILITY = {"strong": 3, "mid": 2, "weak": 1}


def _panel(scores, twins=None):
    return {"panel": [{"model": m, "ability": a} for m, a in ABILITY.items()],
            "scores": scores, "twins": twins or {}}


def test_a_discriminating_scenario_passes():
    from aies import empirical
    # strong reaches the ceiling, weak sits at the floor, repeats are stable
    r = empirical.analyze_scenario(
        {"strong": [4, 4, 4], "mid": [3, 3, 3], "weak": [1, 2, 1]}, ABILITY)
    assert r["verdict"] == "discriminating" and r["empirically_calibratable"]
    assert r["discrimination"] >= 1.0 and r["monotonic"]


def test_a_flat_scenario_is_flagged_low_discrimination_and_too_easy():
    from aies import empirical
    # everyone scores high -> no separation, no live floor
    r = empirical.analyze_scenario(
        {"strong": [4, 4], "mid": [4, 4], "weak": [4, 3]}, ABILITY)
    assert not r["empirically_calibratable"]
    assert "low-discrimination" in r["flags"] and "too-easy" in r["flags"]


def test_a_noisy_scenario_is_flagged():
    from aies import empirical
    r = empirical.analyze_scenario(
        {"strong": [4, 1, 4], "mid": [0, 4, 2], "weak": [1, 3, 0]}, ABILITY)
    assert "noisy" in r["flags"] and not r["empirically_calibratable"]


def test_ceiling_unreached_is_flagged():
    from aies import empirical
    # separation exists but even the strong models never reach the ceiling
    r = empirical.analyze_scenario(
        {"strong": [3, 3], "mid": [2, 2], "weak": [1, 1]}, ABILITY)
    assert "ceiling-unreached" in r["flags"]


def test_twin_inconsistency_flags_gaming():
    from aies import empirical
    scores = {"strong": [4, 4], "mid": [3, 3], "weak": [1, 1]}
    twin = {"strong": [1, 1], "mid": [3, 3], "weak": [1, 2]}   # strong aces one, fails twin
    r = empirical.analyze_scenario(scores, ABILITY, twin_per_model=twin)
    assert "gameable" in r["flags"]


def test_analyze_panel_partitions_calibratable_from_flagged():
    from aies import empirical
    panel = _panel({
        "SC-A": {"strong": [4, 4], "mid": [3, 3], "weak": [1, 1]},   # good
        "SC-B": {"strong": [4, 4], "mid": [4, 4], "weak": [4, 4]},   # too easy
    })
    report = empirical.analyze_panel(panel)
    assert report["empirically_calibratable"] == ["SC-A"]
    assert report["flagged"] == ["SC-B"]


def test_result_carries_reproducibility_metadata():
    """An empirical verdict is only reproducible if the panel, the methodology
    version, and the exact threshold values are recorded with it."""
    from aies import empirical
    panel = _panel({"SC-A": {"strong": [4, 4], "mid": [3, 3], "weak": [1, 1]}})
    report = empirical.analyze_panel(panel, panel_id="pilot-2026-Q3",
                                     analyzed_at="2026-07-19T00:00:00Z")
    m = report["metadata"]
    assert m["panel_id"] == "pilot-2026-Q3"
    assert m["analyzed_at"] == "2026-07-19T00:00:00Z"
    assert m["methodology_version"] == empirical.METHODOLOGY_VERSION
    assert m["thresholds"]["version"] == empirical.THRESHOLDS_VERSION
    # the actual cut-offs are recorded, so a threshold change is visible
    assert m["thresholds"]["discrimination_min"] == empirical.DISCRIMINATION_MIN
    assert {p["model"] for p in m["panel"]} == {"strong", "mid", "weak"}
    assert not report["promotion_eligible"]  # synthetic input has no run preflight


def test_insufficient_panel_is_handled():
    from aies import empirical
    r = empirical.analyze_scenario({"solo": [4, 4]}, {"solo": 1})
    assert r["verdict"] == "insufficient-panel" and not r["empirically_calibratable"]


def test_assemble_panel_from_scored_runs(tmp_path, monkeypatch):
    """The one-command pilot: assemble a panel-results object from completed,
    scored qualify runs (each run = one panel model), and confirm the harness
    reads real per-scenario scores and picks up the discrimination."""
    import json
    import yaml
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    monkeypatch.setenv("AIES_ENV_FILE", str(tmp_path / "empty.env"))
    (tmp_path / "empty.env").write_text("", encoding="utf-8")
    from aies import registry, engine, rating, workspace, empirical

    def make_run(dep_id, level):
        e = {"id": dep_id, "family": "demo", "runtime": "mock", "model": dep_id,
             "context_window": 8192,
             "provenance": {"source": "x", "checksum": "sha256:" + "0" * 64}}
        p = tmp_path / f"{dep_id}.yaml"; p.write_text(yaml.safe_dump(e), encoding="utf-8")
        registry.add(p)
        m = engine.start_qualification(dep_id, "coder", "RT2", ["CA-05"], repeats=1)
        run_id = m["run_id"]
        sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
        sheet["rater"] = {"name": "R", "kind": "human"}
        for it in sheet["items"]:
            it["scores"] = {d: level for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
            if level <= 2:      # scores <=2 require written findings (AIES-AESQS-ER-01)
                it["findings"] = [{"dimension": "EV1", "score": level, "finding": "weak"}]
        rating.ingest_scores(run_id, sheet)
        return run_id

    strong, mid, weak = make_run("strong", 4), make_run("mid", 3), make_run("weak", 2)
    panel = empirical.assemble_panel_from_runs([
        {"run_id": strong, "ability": 3, "ability_basis": "independent fixture",
         "preregistered_at": "2026-07-18T00:00:00Z",
         "rating_protocol_basis": "consensus fixture"},
        {"run_id": mid, "ability": 2, "ability_basis": "independent fixture",
         "preregistered_at": "2026-07-18T00:00:00Z",
         "rating_protocol_basis": "consensus fixture"},
        {"run_id": weak, "ability": 1, "ability_basis": "independent fixture",
         "preregistered_at": "2026-07-18T00:00:00Z",
         "rating_protocol_basis": "consensus fixture"},
    ])
    assert {m["model"] for m in panel["panel"]} == {"strong", "mid", "weak"}
    assert panel["scores"], "no per-scenario scores assembled"
    # every CA-05 scenario should carry all three models' observations
    some = next(iter(panel["scores"].values()))
    assert set(some) == {"strong", "mid", "weak"}
    # strong=4, mid=3, weak=2 -> discrimination 2.0, monotonic
    report = empirical.analyze_panel(panel)
    assert panel["preflight"]["ready"] and report["promotion_eligible"]
    a = report["results"][next(iter(panel["scores"]))]
    assert a["discrimination"] == 2.0 and a["monotonic"]


def test_preflight_rejects_duplicate_rating_observations(tmp_path, monkeypatch):
    import json
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import empirical, workspace

    specs = []
    for index, ability in enumerate((1, 2, 3), start=1):
        run_id = f"run-{index}"
        rdir = workspace.run_dir(run_id)
        workspace.write_json(rdir / "manifest.json", {
            "model": {"registry_id": f"subject-{index}"},
            "areas": [{"area": "CA-05", "suite_version": "suite-v1"}],
        })
        response = {"scenario_id": "SC-CA05-001", "repeat": 1,
                    "request": {"prompt_hash": "sha256:abc"}}
        workspace.write_json(rdir / "responses" / "SC-CA05-001-r1.json", response)
        rating = {"rates_response": "SC-CA05-001-r1.json",
                  "scenario_id": "SC-CA05-001", "repeat": 1,
                  "scores": {d: ability for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")},
                  "provenance": {"rater_kind": "human", "rater": "R"}}
        workspace.write_json(rdir / "ratings" / "rating-a.json", rating)
        if index == 1:
            workspace.write_json(rdir / "ratings" / "rating-b.json", rating)
        specs.append({"run_id": run_id, "ability": ability,
                      "ability_basis": "independent fixture",
                      "preregistered_at": "2026-07-18T00:00:00Z",
                      "rating_protocol_basis": "consensus fixture"})

    preflight = empirical.preflight_runs(specs)
    assert not preflight["ready"]
    assert any("inflate repeatability" in blocker for blocker in preflight["blockers"])

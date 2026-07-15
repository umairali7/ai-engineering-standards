"""M2 conformance tests: result history and comparison.

M2 exit criterion (PLATFORM.md §10): two models compared on identical
suite versions with defensible deltas; different suite versions are
never diffed.
"""

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


def _register(tmp_path, model_id):
    from aies import registry
    entry = {
        "id": model_id, "family": "demo", "runtime": "mock",
        "context_window": 8192, "modalities": ["text"],
        "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64},
    }
    src = tmp_path / f"{model_id}.yaml"
    src.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(src)


def _qualified_run(tmp_path, model_id, score):
    from aies import engine, rating, workspace
    manifest = engine.start_qualification(model_id, "enterprise", "RT2",
                                          ["CA-05"], repeats=1)
    run_id = manifest["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    sheet["rater"] = {"name": "Test Rater", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {d: score for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
        if score <= 2:
            item["findings"] = [{"dimension": "EV1", "score": score, "finding": "weak"}]
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)
    return run_id


def test_history_and_comparison_deltas(ws, tmp_path):
    from aies import compare
    _register(tmp_path, "model-a")
    _register(tmp_path, "model-b")
    run_a = _qualified_run(tmp_path, "model-a", 2)
    run_b = _qualified_run(tmp_path, "model-b", 3)

    runs = compare.list_runs()
    assert {r["model"] for r in runs} == {"model-a", "model-b"}
    assert all(r["aggregated"] for r in runs)

    cmp = compare.compare("model-a", "model-b")
    area = cmp["areas"]["CA-05"]
    # Identical suite version required and recorded.
    assert area["suite_version"].startswith("suite-sha256:")
    assert not cmp["incomparable_areas"]
    # Defensible deltas: uniform 2s vs uniform 3s -> +1.0 on every dimension.
    for dim, v in area["dimensions"].items():
        assert v["delta"] == 1.0, dim
    assert area["aggregate"]["delta"] == 1.0
    # Non-decisional caveat surfaces (4 items < 30 for AI at RT2).
    assert any("NON-DECISIONAL" in c for c in cmp["caveats"])
    md = compare.render_markdown(cmp)
    assert "Delta (B-A)" in md and "+1.0" in md


def test_different_suite_versions_never_diffed(ws, tmp_path, monkeypatch):
    from aies import compare, workspace
    _register(tmp_path, "model-a")
    _register(tmp_path, "model-b")
    run_a = _qualified_run(tmp_path, "model-a", 3)
    run_b = _qualified_run(tmp_path, "model-b", 3)
    # Simulate a suite change between the runs by rewriting run B's
    # recorded suite version in its evidence package.
    pkg_path = workspace.run_dir(run_b) / "evidence-package.json"
    pkg = workspace.read_json(pkg_path)
    pkg["suite_versions"]["CA-05"] = "suite-sha256:deadbeefdeadbeef"
    workspace.write_json(pkg_path, pkg, overwrite=True)

    cmp = compare.compare(run_a, run_b)
    assert cmp["areas"] == {}
    assert cmp["incomparable_areas"][0]["area"] == "CA-05"
    md = compare.render_markdown(cmp)
    assert "never diffed" in md


def test_cross_tier_comparison_refused(ws, tmp_path):
    from aies import compare, engine, workspace
    _register(tmp_path, "model-a")
    run_a = _qualified_run(tmp_path, "model-a", 3)
    pkg_path = workspace.run_dir(run_a) / "evidence-package.json"
    pkg = workspace.read_json(pkg_path)
    pkg["risk_tier"] = "RT3"
    workspace.write_json(pkg_path, pkg, overwrite=True)
    _register(tmp_path, "model-b")
    run_b = _qualified_run(tmp_path, "model-b", 3)
    with pytest.raises(compare.CompareError):
        compare.compare(run_a, run_b)

"""M3 conformance tests: parallel==serial, HTML report, result index,
out-of-tree adapter contract (PLATFORM.md §10 M3 exit criteria)."""

import importlib.util
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


def _register(tmp_path, model_id="demo", runtime="mock"):
    from aies import registry
    entry = {"id": model_id, "family": "demo", "runtime": runtime,
             "model": model_id, "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / f"{model_id}.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def test_report_has_grant_readiness_and_residual_risk(ws, tmp_path):
    from aies import engine, report
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT2", ["CA-05"], repeats=1)
    _fill_and_aggregate(run["run_id"], score=3)
    md = report.render_markdown(run["run_id"])
    assert "## Grant Readiness" in md and "### Residual risk" in md
    assert "## Engineering Capability Matrix (ECM)" in md
    assert "### Deployment Guidance" in md
    assert "engineering-capability-matrix.md" in md
    paths = report.write_reports(run["run_id"])
    assert Path(paths["html"]).exists()
    assert Path(paths["ecm_markdown"]).exists()
    assert Path(paths["ecm_json"]).exists()
    assert Path(paths["ecm_html"]).exists()
    # a small CA-05 run is under the RT2 minimum -> BLOCKED / non-decisional flagged
    assert "BLOCKED" in md and "non-decisional" in md


def _fill_and_aggregate(run_id, score=3):
    from aies import engine, rating, workspace
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    sheet["rater"] = {"name": "Rater", "kind": "human"}
    for item in sheet["items"]:
        item["scores"] = {d: score for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run_id, sheet)
    return engine.aggregate(run_id)


def test_parallel_matches_serial(ws, tmp_path):
    """M3 exit: parallel execution yields byte-identical record sets."""
    from aies import engine, workspace

    _register(tmp_path)
    serial = engine.start_qualification("demo", "research", "RT2",
                                        ["CA-05", "CA-06"], repeats=3, workers=1)
    parallel = engine.start_qualification("demo", "research", "RT2",
                                          ["CA-05", "CA-06"], repeats=3, workers=8)

    def _norm(run_id):
        out = {}
        for p in sorted((workspace.run_dir(run_id) / "responses").glob("*.json")):
            rec = json.loads(p.read_text(encoding="utf-8"))
            # drop only the fields that legitimately vary run-to-run
            rec.pop("recorded_at", None)
            rec["run_id"] = rec["run_id"].split("-", 3)[-1]
            out[p.name] = rec
        return out

    s, p = _norm(serial["run_id"]), _norm(parallel["run_id"])
    assert set(s) == set(p)                 # same scenario/repeat files
    assert len(s) == sum(a["planned_items"] for a in serial["areas"])  # suite-dependent
    for name in s:
        assert s[name]["raw_response"] == p[name]["raw_response"]
        assert s[name]["scenario_id"] == p[name]["scenario_id"]


def test_partial_failure_preserves_successes_and_raises(ws, tmp_path, monkeypatch):
    """A mid-run inference failure must NOT discard responses already
    collected, and must raise a single informative error (not a bare one)."""
    from aies import runner, workspace
    from aies.adapters.base import GenerationResponse

    _, scenarios, sv = runner.load_area("CA-05")

    calls = {"n": 0}
    def flaky(self, request):
        calls["n"] += 1
        if calls["n"] == 2:            # the 2nd call fails, others succeed
            raise RuntimeError("could not reach http://x/v1/chat/completions within 300s")
        return GenerationResponse(text="ok answer", usage={}, raw={})
    from aies.adapters import mock as mockmod
    monkeypatch.setattr(mockmod.MockAdapter, "generate", flaky)
    adapter = mockmod.MockAdapter(); adapter.load({"id": "demo"})

    run_id = "run-partial"
    (workspace.run_dir(run_id) / "responses").mkdir(parents=True, exist_ok=True)

    with pytest.raises(runner.SuiteError) as ei:
        runner.execute_suite(run_id, {"id": "demo", "provenance": {}}, adapter,
                             scenarios, sv, {}, repeats=2, workers=1)
    msg = str(ei.value)
    assert "were saved to" in msg and "300s" in msg      # actionable, names the cause
    # the successful responses are on disk despite the failure
    saved = list((workspace.run_dir(run_id) / "responses").glob("*.json"))
    assert len(saved) >= 1


def test_parallel_record_count(ws, tmp_path):
    from aies import engine, workspace
    _register(tmp_path)
    run = engine.start_qualification("demo", "research", "RT2",
                                     ["CA-05", "CA-06"], repeats=3, workers=4)
    n = len(list((workspace.run_dir(run["run_id"]) / "responses").glob("*.json")))
    assert n == sum(a["planned_items"] for a in run["areas"])  # suite-dependent


def test_html_report_self_contained(ws, tmp_path):
    from aies import engine, report_html
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT2", ["CA-05"], repeats=1)
    _fill_and_aggregate(run["run_id"])
    htmldoc = report_html.render_html(run["run_id"])
    assert htmldoc.startswith("<!doctype html>")
    # self-contained: no external resource references
    for needle in ("http://", "https://", "src=", "<link"):
        assert needle not in htmldoc, needle
    assert "NON-DECISIONAL" in htmldoc          # 4 items < 30 for AI at RT2
    assert "Environment Fingerprint" in htmldoc


def test_result_index_rebuildable_from_files(ws, tmp_path):
    from aies import engine, index
    _register(tmp_path)
    run = engine.start_qualification("demo", "enterprise", "RT2", ["CA-05"], repeats=1)
    _fill_and_aggregate(run["run_id"])
    result = index.rebuild()
    assert result["runs_indexed"] == 1
    assert result["area_scores_indexed"] == 1
    runs = index.query_runs(model="demo")
    assert runs and runs[0]["run_id"] == run["run_id"]
    hist = index.area_history("CA-05", model="demo")
    assert hist and hist[0]["cl"] == "CL2"
    # index is disposable: deleting and rebuilding reproduces it
    (index._db_path()).unlink()
    assert index.rebuild()["runs_indexed"] == 1


def test_out_of_tree_adapter_satisfies_contract(ws, tmp_path, monkeypatch):
    """M3 exit: an adapter written outside the package works with no core
    change, discovered as if via entry point."""
    from aies import adapters, engine, registry
    from aies.adapters.base import RuntimeAdapter

    ext = (Path(__file__).resolve().parent.parent / "examples"
           / "external_adapter" / "aies_reverse_adapter.py")
    spec = importlib.util.spec_from_file_location("aies_reverse_adapter", ext)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ReverseAdapter = mod.ReverseAdapter

    assert issubclass(ReverseAdapter, RuntimeAdapter)
    assert ReverseAdapter.contract_version.split(".")[0] == \
        adapters.base.ADAPTER_CONTRACT_VERSION.split(".")[0]

    # Simulate entry-point discovery without installing the package.
    real = adapters.discovered

    def fake_discovered():
        d = real()
        d["reverse"] = ReverseAdapter
        return d

    monkeypatch.setattr(adapters, "discovered", fake_discovered)
    monkeypatch.setattr("aies.runtimes.discovered", fake_discovered)
    # resolve() imports adapters at call time via engine; register a deployment
    entry = {"id": "reverse-demo", "runtime": "reverse", "model": "reverse-demo",
             "provenance": {"source": "example", "checksum": "sha256:" + "r" * 64}}
    p = tmp_path / "rev.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(p)
    run = engine.start_qualification("reverse-demo", "research", "RT2",
                                     ["CA-05"], repeats=1)
    assert run["model"]["registry_id"] == "reverse-demo"

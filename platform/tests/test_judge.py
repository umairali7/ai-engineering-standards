"""Judge track record: derived purely from model-kind ratings across runs,
so `judge list` / `judge history` reflect real judging activity and reliability
without storing anything new."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _register(tmp_path, model_id, roles=None):
    from aies import registry
    entry = {"id": model_id, "family": "demo", "runtime": "mock", "model": model_id,
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    if roles is not None:
        entry["roles"] = roles
    p = tmp_path / f"{model_id}.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def test_registered_judges_pool_counts_and_annotates(ws, tmp_path, monkeypatch):
    from aies import judge

    _register(tmp_path, "cand")                       # a subject, not a judge
    _register(tmp_path, "judge-idle", roles=["judge"])  # registered, never used
    _register(tmp_path, "judge-used", roles=["judge"])

    # nothing has judged yet -> pool of 2, both "never used"
    pool = judge.registered_judges()
    assert len(pool) == 2
    assert {p["judge"] for p in pool} == {"judge-idle", "judge-used"}
    assert all(p["parse_rate"] is None and p["runs_judged"] == 0 for p in pool)

    # after judge-used scores a run, its pool row reflects the track record
    _judged_run("cand", "judge-used", tmp_path, monkeypatch)
    pool = {p["judge"]: p for p in judge.registered_judges()}
    assert pool["judge-used"]["runs_judged"] == 1
    assert pool["judge-used"]["parse_rate"] == 1.0
    assert pool["judge-idle"]["runs_judged"] == 0        # still idle
    # an untagged deployment used ad hoc as a judge is NOT in the pool
    assert "cand" not in pool


def test_roles_field_is_validated(tmp_path):
    from aies import registry
    bad = {"id": "x", "runtime": "mock", "model": "x", "roles": ["boss"],
           "provenance": {"checksum": "sha256:" + "0" * 64}}
    assert any("roles must be" in p for p in registry.validate_entry(bad))
    ok = {**bad, "roles": ["subject", "judge"]}
    assert not any("roles" in p for p in registry.validate_entry(ok))


def _judged_run(subject, judge, tmp_path, monkeypatch, all_parseable=True):
    from aies import engine, model_review
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    good = ('{"EV1":3,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3,"findings":[]}')

    class Counter:
        n = 0
    def gen(self, req):
        Counter.n += 1
        # when not all_parseable, every other reply is junk the judge can't parse
        if not all_parseable and Counter.n % 2 == 0:
            return GenerationResponse(text="I cannot score this.", usage={}, raw={})
        return GenerationResponse(text=good, usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", gen)

    run = engine.start_qualification(subject, "coder", "RT2", ["CA-05"], repeats=1)
    model_review.run_model_review(run["run_id"], judge)
    return run["run_id"]


def test_judge_list_aggregates_usage_and_flags_self_and_unregistered(ws, tmp_path, monkeypatch):
    from aies import judge, registry

    _register(tmp_path, "cand")
    _register(tmp_path, "judge-frontier")
    _judged_run("cand", "judge-frontier", tmp_path, monkeypatch)

    usage = {a["judge"]: a for a in judge.judge_usage()}
    assert "judge-frontier" in usage
    jf = usage["judge-frontier"]
    assert jf["runs_judged"] == 1 and jf["responses_scored"] >= 1
    assert jf["parse_rate"] == 1.0
    assert jf["registered"] is True
    assert jf["self_judged_runs"] == 0

    # a retired judge is reported NOT registered but keeps its history
    registry.retire("judge-frontier")
    assert judge.judge_usage()[0]["registered"] is False


def test_judge_history_rows_and_filter(ws, tmp_path, monkeypatch):
    from aies import judge

    _register(tmp_path, "cand")
    _register(tmp_path, "judge-a")
    _register(tmp_path, "judge-b")
    _judged_run("cand", "judge-a", tmp_path, monkeypatch)
    _judged_run("cand", "judge-b", tmp_path, monkeypatch)

    all_rows = judge.judge_history()
    judges = {r["judge"] for r in all_rows}
    assert {"judge-a", "judge-b"} <= judges
    only_a = judge.judge_history(judge="judge-a")
    assert only_a and all(r["judge"] == "judge-a" for r in only_a)
    assert all(r["scored"] == r["responses"] for r in only_a)  # all parseable


def test_self_judging_is_flagged(ws, tmp_path, monkeypatch):
    from aies import judge
    _register(tmp_path, "cand")
    _judged_run("cand", "cand", tmp_path, monkeypatch)   # subject judges itself
    rows = judge.judge_history()
    assert rows and rows[0]["self_judged"] is True
    assert judge.judge_usage()[0]["self_judged_runs"] == 1


def test_unparseable_replies_lower_parse_rate(ws, tmp_path, monkeypatch):
    from aies import judge
    _register(tmp_path, "cand")
    _register(tmp_path, "flaky-judge")
    _judged_run("cand", "flaky-judge", tmp_path, monkeypatch, all_parseable=False)
    jf = judge.judge_usage()[0]
    assert jf["unparseable"] >= 1
    assert jf["parse_rate"] is not None and jf["parse_rate"] < 1.0

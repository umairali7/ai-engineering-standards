"""Model-reviewer execution (Task #3): drive a reviewer deployment to
score a run's responses, parse robustly, ingest as model-kind ratings,
then gate via calibration. A reviewer that can't produce parseable
scores contributes nothing rather than fabricating (PLATFORM.md §7)."""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _register(tmp_path, model_id, runtime="mock"):
    from aies import registry
    entry = {"id": model_id, "family": "demo", "runtime": runtime, "model": model_id,
             "context_window": 8192,
             "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / f"{model_id}.yaml"
    p.write_text(yaml.safe_dump(entry), encoding="utf-8")
    return registry.add(p)


def test_parse_scores_robust():
    from aies.model_review import _parse_scores
    ok = _parse_scores('noise ```json\n{"EV1":3,"EV2":2,"EV3":3,"EV4":3,"EV5":2,'
                       '"EV6":4,"findings":["ev2 thin"]}\n``` trailing')
    assert ok is not None
    scores, findings = ok
    assert scores["EV1"] == 3 and scores["EV6"] == 4 and findings
    assert _parse_scores("I cannot score this.") is None      # no JSON
    assert _parse_scores('{"EV1":5,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3}') is None  # out of range
    assert _parse_scores('{"EV1":3}') is None                  # missing dims


def test_mock_reviewer_is_judge_aware_and_emits_parseable_scores(ws, tmp_path):
    """The mock adapter is judge-aware: when driven as a reviewer it emits a
    deterministic, parseable EV1-EV6 JSON object, so the WHOLE pipeline —
    including auto-scoring and the assessment decision — runs fully offline
    (this is what `make demo` / tests/test_demo.py exercise). The scores are
    obviously synthetic and mock evidence self-declares in provenance, so it can
    never masquerade as a real model's qualification."""
    from aies import engine, model_review, rating, workspace
    _register(tmp_path, "cand")
    run = engine.start_qualification("cand", "research", "RT2", ["CA-05"], repeats=1)
    summary = model_review.run_model_review(run["run_id"], "cand")  # mock reviews itself
    assert summary["scored"] > 0 and summary["unparseable"] == 0
    # scores were ingested as model-kind ratings
    ratings = [workspace.read_json(p)
               for p in (workspace.run_dir(run["run_id"]) / "ratings").glob("*.json")]
    assert ratings and all(r["provenance"]["rater_kind"] == "model" for r in ratings)


def test_mock_scores_are_deterministic_and_in_range():
    from aies.adapters.mock import MockAdapter
    import json
    a = MockAdapter()
    prompt = ("You are a qualification reviewer. ... "
              '{"EV1":<int>,"EV2":<int>,"EV3":<int>,"EV4":<int>,"EV5":<int>,"EV6":<int>}')
    from aies.adapters.base import GenerationRequest
    r1 = a.generate(GenerationRequest(prompt=prompt)).text
    r2 = a.generate(GenerationRequest(prompt=prompt)).text
    assert r1 == r2                                        # deterministic
    scores = json.loads(r1)
    assert all(3 <= scores[d] <= 4 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6"))


def test_reviewer_scores_ingested_and_gated(ws, tmp_path, monkeypatch):
    """A reviewer adapter that emits valid JSON gets its scores ingested as
    model-kind ratings; the review package then applies the calibration gate."""
    from aies import engine, model_review, review, registry
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    _register(tmp_path, "cand")
    # A reviewer deployment whose adapter returns valid score JSON.
    _register(tmp_path, "rev", runtime="mock")

    def fake_generate(self, request):
        return GenerationResponse(
            text='{"EV1":3,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3,"findings":[]}',
            usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", fake_generate)

    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"], repeats=1)
    # Human ratings too, so the package has both raters to pair.
    from aies import rating, workspace
    import json as _json
    sheet = _json.loads((workspace.run_dir(run["run_id"]) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "Human", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run["run_id"], sheet)

    summary = model_review.run_model_review(run["run_id"], "rev")
    # Every response parseable -> scored == responses (count is suite-dependent).
    assert summary["scored"] == summary["responses"] and summary["unparseable"] == 0

    pkg = review.assemble_review_package(run["run_id"], reviewer_label="model:rev")
    # Uncalibrated, unqualified reviewer -> advisory only.
    assert pkg["reviewer"]["admitted"] is False
    # Human and model both scored 3 -> no divergences.
    assert pkg["summary"]["n_divergences"] == 0


def test_auto_score_qualify_produces_evidence_without_manual_step(ws, tmp_path, monkeypatch):
    """`qualify --judge` path: a judge scores the responses and the run
    aggregates to an evidence package with no human scoresheet edit."""
    from aies import engine, model_review, workspace
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    _register(tmp_path, "cand")
    _register(tmp_path, "judge")

    def judge_generate(self, request):
        return GenerationResponse(
            text='{"EV1":3,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3,"findings":[]}',
            usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", judge_generate)

    run = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)
    # simulate what cmd_qualify does with --judge: judge-score, then aggregate
    summary = model_review.run_model_review(run["run_id"], "judge")
    assert summary["scored"] == summary["responses"] and summary["unparseable"] == 0
    pkg = engine.aggregate(run["run_id"])
    assert pkg["rater_kinds"] == ["model"]              # scored by the judge, not a human
    assert "CA-05" in pkg["areas"]
    assert pkg["rating_admission"]["advisory_ratings"] == summary["scored"]
    assert pkg["areas"]["CA-05"]["n_scored"] == 0
    assert pkg["areas"]["CA-05"]["decisional"] is False
    # report carries the judge-produced banner and stays evidence-only (no grant)
    from aies import report
    md = report.render_markdown(run["run_id"])
    assert "JUDGE-PRODUCED" in md and "NO GRANT" in md.upper()


def test_review_command_refreshes_reports_and_keeps_human_score_optional(ws, tmp_path, monkeypatch):
    """A model review is an actionable evidence update, not a dead-end file.

    The resulting report separates automated reviewer observations from an
    optional human score, while retaining the no-grant boundary.
    """
    from argparse import Namespace
    from aies import cli, engine, workspace
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    _register(tmp_path, "cand")
    _register(tmp_path, "reviewer")

    def judge_generate(self, request):
        return GenerationResponse(
            text='{"EV1":3,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3,"findings":[]}',
            usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", judge_generate)

    run = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)
    args = Namespace(run=run["run_id"], model_reviewer="reviewer",
                     reviewer_runtime=None, parallel=1, json=False,
                     reviewer="reviewer-model", reviewer_qualified=False,
                     calibration=None, consider_advisory_review=True,
                     human_evaluation="Human reviewer")
    assert cli.cmd_review(args) == 0
    rdir = workspace.run_dir(run["run_id"])
    text = (rdir / "report.md").read_text(encoding="utf-8")
    assert "Automated review" in text
    assert "Human review (optional)" in text
    assert "Human Review Record" in text
    assert "Human reviewer" in text
    assert (rdir / "report.html").exists()


def test_repeating_same_model_reviewer_reuses_append_only_ratings(ws, tmp_path, monkeypatch):
    from aies import engine, model_review
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    _register(tmp_path, "cand")
    _register(tmp_path, "reviewer")

    def judge_generate(self, request):
        return GenerationResponse(
            text='{"EV1":3,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3,"findings":[]}',
            usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", judge_generate)

    run = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)
    first = model_review.run_model_review(run["run_id"], "reviewer")
    second = model_review.run_model_review(run["run_id"], "reviewer")
    assert first["ratings_written"] == first["responses"]
    assert second["ratings_written"] == 0
    assert second["reused_existing"] == second["responses"]


def test_resume_with_judge_is_one_command_score_aggregate_and_report(ws, tmp_path, monkeypatch):
    from argparse import Namespace
    from aies import cli, engine, workspace
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    _register(tmp_path, "cand")
    _register(tmp_path, "judge")

    def judge_generate(self, request):
        return GenerationResponse(
            text='{"EV1":3,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3,"findings":[]}',
            usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", judge_generate)

    run = engine.start_qualification("cand", "coder", "RT2", ["CA-05"], repeats=1)
    args = Namespace(resume_collection=None, resume=run["run_id"], judge="judge",
                     reviewer_runtime=None, parallel=1, json=True,
                     consider_advisory_review=True, human_evaluation="Alice")
    assert cli.cmd_qualify(args) == 0
    rdir = workspace.run_dir(run["run_id"])
    assert (rdir / "evidence-package.json").exists()
    text = (rdir / "report.md").read_text(encoding="utf-8")
    assert "Human Review Record" in text and "Alice" in text


def test_judge_scoring_runs_concurrently_and_preserves_order(ws, tmp_path, monkeypatch):
    """The judge scoring phase honours `workers`: concurrent calls overlap
    (wall-clock < serial) and ratings still land in canonical order."""
    import time
    from aies import engine, model_review, workspace
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    _register(tmp_path, "cand")
    _register(tmp_path, "judge")

    def slow_judge(self, request):
        time.sleep(0.2)
        return GenerationResponse(
            text='{"EV1":3,"EV2":3,"EV3":3,"EV4":3,"EV5":3,"EV6":3,"findings":[]}',
            usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", slow_judge)

    run = engine.start_qualification("cand", "enterprise", "RT2", ["CA-05"],
                                     repeats=3, workers=8)
    run_id = run["run_id"]
    n = sum(a["planned_items"] for a in run["areas"])
    assert n >= 4  # enough items that concurrency is observable

    t = time.monotonic()
    summary = model_review.run_model_review(run_id, "judge", workers=8)
    parallel_s = time.monotonic() - t
    assert summary["scored"] == n
    # 8-wide should finish far faster than n sequential 0.2s calls
    assert parallel_s < 0.2 * n * 0.6

    # concurrency-safe: exactly one rating record per response, none lost
    # or duplicated by the parallel scoring.
    assert summary["ratings_written"] == n
    ratings_dir = workspace.run_dir(run_id) / "ratings"
    assert len(list(ratings_dir.glob("*.json"))) == n

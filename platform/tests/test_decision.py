"""Assessment Decision Engine (ADR-0005 D-B4). The load-bearing invariants:
a strong competency never offsets a failing one; advisory failures never change
the outcome; the outcome precedence and reason kinds are engine-owned; and a run
re-decides from evidence without re-running inference."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def _area(decisional=True, gates_passed=True, ev3_hard_fail=False, cl="CL3",
          n=42, min_sample=30, aggregate=3.4):
    gates = [{"dimension": d, "passed": gates_passed or d != "EV3"}
             for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")]
    return {"decisional": decisional, "gates_passed": gates_passed,
            "ev3_hard_fail": ev3_hard_fail, "cl": cl, "n_scored": n,
            "min_sample": min_sample, "aggregate_A": aggregate, "gates": gates}


def _pkg(areas):
    return {"run_id": "run-x", "risk_tier": "RT2",
            "model": {"registry_id": "cand", "checksum": "sha256:abc"},
            "environment_fingerprint": {"runtime": {"id": "mock"},
                                        "fingerprint_hash": "sha256:fp"},
            "suite_versions": {}, "aggregated_at": "2026-07-18T00:00:00Z",
            "areas": areas}


def _assessment(*comps):
    return {"id": "t", "version": "1.0.0", "schema": 1, "profile": "coder",
            "competencies": list(comps)}


def _m(area, min_cl=None):
    return {"area": area, "requirement": "mandatory", "min_cl": min_cl}


def _a(area):
    return {"area": area, "requirement": "advisory"}


def test_strong_areas_never_offset_a_failing_mandatory_one():
    from aies import decision
    # coding strong, security gate FAIL -> overall FAIL (never an average/PASS)
    pkg = _pkg({"CA-05": _area(cl="CL3", aggregate=3.9),
                "CA-07": _area(gates_passed=False, ev3_hard_fail=True, aggregate=3.8)})
    res = decision.decide(pkg, _assessment(_m("CA-05"), _m("CA-07")))
    assert res["outcome"] == "FAIL"
    kinds = {r["area"]: r["kind"] for r in res["decisions"]["reasons"]}
    assert kinds["CA-07"] == "mandatory-gate"


def test_advisory_failure_never_changes_outcome():
    from aies import decision
    pkg = _pkg({"CA-05": _area(), "CA-09": _area(gates_passed=False, ev3_hard_fail=True)})
    res = decision.decide(pkg, _assessment(_m("CA-05"), _a("CA-09")))
    assert res["outcome"] == "PASS"                 # advisory CA-09 failing is ignored
    assert res["decisions"]["reasons"] == []        # no mandatory reason


def test_outcome_precedence_and_kinds():
    from aies import decision
    # min_cl not met -> FAIL (min-cl)
    pkg = _pkg({"CA-07": _area(cl="CL2")})
    r = decision.decide(pkg, _assessment(_m("CA-07", min_cl="CL3")))
    assert r["outcome"] == "FAIL"
    assert r["decisions"]["reasons"][0]["kind"] == "min-cl"
    # non-decisional -> INSUFFICIENT EVIDENCE
    r2 = decision.decide(_pkg({"CA-05": _area(decisional=False, n=10)}), _assessment(_m("CA-05")))
    assert r2["outcome"] == "INSUFFICIENT EVIDENCE"
    assert r2["decisions"]["reasons"][0]["kind"] == "insufficient-evidence"
    # area absent from the run -> INCONCLUSIVE (assessment-error)
    r3 = decision.decide(_pkg({"CA-05": _area()}), _assessment(_m("CA-05"), _m("CA-07")))
    assert r3["outcome"] == "INCONCLUSIVE"
    assert any(x["kind"] == "assessment-error" for x in r3["decisions"]["reasons"])
    # all good -> PASS
    r4 = decision.decide(_pkg({"CA-05": _area()}), _assessment(_m("CA-05")))
    assert r4["outcome"] == "PASS" and not r4["decisions"]["reasons"]


def test_result_has_all_facets_and_metadata():
    from aies import decision
    res = decision.decide(_pkg({"CA-05": _area()}), _assessment(_m("CA-05")))
    for facet in ("metadata", "evidence", "decisions", "diagnostics", "analytics"):
        assert facet in res
    assert res["metadata"]["assessment_version"] == "1.0.0"
    assert res["analytics"]["note"].startswith("informational")
    md = decision.render_markdown(res)
    assert "## PASS" in md and "1. Normative" in md and "non-authoritative" in md


def test_render_html_is_a_view_not_a_decision():
    from aies import decision
    # FAIL outcome must surface verbatim in the HTML; renderer never re-decides.
    pkg = _pkg({"CA-05": _area(cl="CL3", aggregate=3.9),
                "CA-07": _area(gates_passed=False, ev3_hard_fail=True)})
    res = decision.decide(pkg, _assessment(_m("CA-05"), _m("CA-07")))
    doc = decision.render_html(res)
    assert doc.startswith("<!doctype html>")
    assert "Assessment Result" in doc
    assert res["outcome"] in doc and "Normative (authoritative)" in doc
    assert "http://" not in doc and "https://" not in doc     # self-contained, no external requests


def test_assess_run_replays_from_evidence_without_inference(ws_run):
    from aies import decision, workspace
    run_id = ws_run
    res = decision.assess_run(run_id)          # no adapter / no model call
    assert res["outcome"] in decision.OUTCOMES
    assert (workspace.run_dir(run_id) / "assessment-result.json").exists()


@pytest.fixture()
def ws_run(tmp_path, monkeypatch):
    """A real aggregated run under an assessment, human-scored (mock)."""
    import json
    import yaml
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import registry, engine, rating, workspace, cli
    e = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
         "context_window": 8192, "provenance": {"source": "x", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(e), encoding="utf-8"); registry.add(p)

    class A:  # emulate parsed argparse for _qualify_defaults
        pass
    args = A()
    args.assessment = "coder"; args.rt = None; args.repeats = None
    args.all_areas = False; args.area = None; args.model = "cand"
    cli._qualify_defaults(args)
    manifest = engine.start_qualification("cand", args.profile, f"RT{args.rt}", args.area,
                                          repeats=1, assessment=args._assessment)
    run_id = manifest["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "R", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)
    return run_id

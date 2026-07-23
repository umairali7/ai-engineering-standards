"""The read-only REST API is a consumer, not a decider (CONFORMANCE-POLICY §4).

Tests hit the pure `route()` function directly (no sockets). The load-bearing
assertion: the /result endpoint serves the STORED Canonical Assessment Result
verbatim and the API never recomputes an outcome."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture(scope="module")
def api_ws(tmp_path_factory):
    """Build the immutable API fixture once; every tested route is read-only."""
    tmp_path = tmp_path_factory.mktemp("api-workspace")
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    monkeypatch.setenv("AIES_ENV_FILE", str(tmp_path / "empty.env"))
    (tmp_path / "empty.env").write_text("", encoding="utf-8")
    import yaml
    from aies import registry, engine, rating, workspace
    e = {"id": "cand", "family": "demo", "runtime": "mock", "model": "cand",
         "context_window": 8192, "provenance": {"source": "x", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(e), encoding="utf-8"); registry.add(p)

    class A: pass
    args = A(); args.assessment = "coder"; args.rt = None; args.repeats = None
    args.all_areas = False; args.area = None; args.model = "cand"
    from aies import cli
    cli._qualify_defaults(args)
    m = engine.start_qualification("cand", args.profile, f"RT{args.rt}", args.area,
                                   repeats=1, assessment=args._assessment)
    run_id = m["run_id"]
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "R", "kind": "human"}
    for it in sheet["items"]:
        it["scores"] = {d: 3 for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run_id, sheet)
    engine.aggregate(run_id)
    from aies import decision
    decision.assess_run(run_id)
    yield run_id
    monkeypatch.undo()


def test_health_and_index():
    from aies import api
    status, body = api.route("/health")
    assert status == 200 and body["status"] == "ok"
    assert "/runs/{id}/result" in body["endpoints"]


def test_collections_are_served(api_ws):
    from aies import api
    for path, key in [("/deployments", "deployments"), ("/runs", "runs"),
                      ("/assessments", "assessments"), ("/qualifications", "qualifications")]:
        status, body = api.route(path)
        assert status == 200 and key in body


def test_result_endpoint_serves_stored_result_verbatim(api_ws):
    from aies import api, workspace
    status, body = api.route(f"/runs/{api_ws}/result")
    assert status == 200
    stored = workspace.read_json(workspace.run_dir(api_ws) / "assessment-result.json")
    assert body == stored                       # verbatim — no recomputation
    assert body["result_schema"] == 1 and body["outcome"] in (
        "PASS", "FAIL", "INCONCLUSIVE", "INSUFFICIENT EVIDENCE")


def test_conformance_endpoint(api_ws):
    from aies import api
    status, body = api.route("/conformance")
    # 200 with a report if the corpus is present; 503 if not — never a crash.
    assert status in (200, 503)
    if status == 200:
        assert "valid" in body and "cases" in body


def test_unknown_path_is_404_and_missing_run_is_404(api_ws):
    from aies import api
    assert api.route("/nope")[0] == 404
    assert api.route("/runs/does-not-exist/result")[0] == 404

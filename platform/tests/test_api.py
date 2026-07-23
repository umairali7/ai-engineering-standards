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
    from aies import decision, report
    decision.assess_run(run_id)
    report.write_reports(run_id)
    yield run_id
    monkeypatch.undo()


def test_health_and_index():
    from aies import api
    status, body = api.route("/health")
    assert status == 200 and body["status"] == "ok"
    assert "/runs/{id}/result" in body["endpoints"]
    assert "/runs/{id}" in body["endpoints"]
    assert "/runs/{id}/ecm" in body["endpoints"]
    assert "/runs/{id}/report-view" in body["endpoints"]
    assert "/support" in body["endpoints"]
    assert "/overview" in body["endpoints"]
    assert "/audits" in body["endpoints"]
    assert "/comparisons" in body["endpoints"]


def test_collections_are_served(api_ws):
    from aies import api
    for path, key in [("/deployments", "deployments"), ("/runs", "runs"),
                      ("/assessments", "assessments"), ("/qualifications", "qualifications")]:
        status, body = api.route(path)
        assert status == 200 and key in body

    status, body = api.route("/support")
    assert status == 200
    assert body["kind"] == "aies-subject-support-registry"
    assert body["counts"]["implemented"] == 2

    status, body = api.route("/overview")
    assert status == 200
    assert body["kind"] == "aies-workspace-overview"
    assert body["schema_version"] == 1
    assert body["authority"] == "informational-read-only"
    assert body["counts"]["runs"] == 1
    assert body["counts"]["aggregated_runs"] == 1
    assert body["runs"][0]["href"] == f"/runs/{api_ws}"
    assert body["links"]["run"] == "/runs/{id}"


def test_result_endpoint_serves_stored_result_verbatim(api_ws):
    from aies import api, workspace
    status, body = api.route(f"/runs/{api_ws}/result")
    assert status == 200
    stored = workspace.read_json(workspace.run_dir(api_ws) / "assessment-result.json")
    assert body == stored                       # verbatim — no recomputation
    assert body["result_schema"] == 1 and body["outcome"] in (
        "PASS", "FAIL", "INCONCLUSIVE", "INSUFFICIENT EVIDENCE")


def test_run_detail_is_versioned_read_only_consumer_contract(api_ws):
    from aies import api

    status, body = api.route(f"/runs/{api_ws}")
    assert status == 200
    assert body["kind"] == "aies-run-view"
    assert body["schema_version"] == 2
    assert body["authority"] == "informational-read-only"
    assert body["run_id"] == api_ws
    assert body["scope"]["risk_tier_label"].startswith("RT2 — ")
    assert body["scope"]["subject_kind_label"] == "ai — AI System"
    assert body["execution"]["collected_responses"] > 0
    assert body["artifacts"]["canonical_evidence"]["available"] is True
    assert body["links"]["self"] == f"/runs/{api_ws}"
    assert "qualify" in body["limitations"][0]


def test_run_product_endpoints_serve_stored_artifacts_verbatim(api_ws):
    from aies import api, workspace

    routes = {
        "evidence": "evidence-package.json",
        "report": "report.json",
        "report-view": "report-view.json",
        "bundle": "report-bundle.json",
        "engineering-evaluation": "engineering-evaluation.json",
        "ecm": "engineering-capability-matrix.json",
        "executive-summary": "executive-summary.json",
        "diagnostics": "grounding-diagnostics.json",
    }
    for endpoint, filename in routes.items():
        status, body = api.route(f"/runs/{api_ws}/{endpoint}")
        assert status == 200, endpoint
        assert body == workspace.read_json(workspace.run_dir(api_ws) / filename)

    status, guidance = api.route(f"/runs/{api_ws}/guidance")
    assert status == 200
    filename = ("engineering-fit-guidance.json"
                if (workspace.run_dir(api_ws) /
                    "engineering-fit-guidance.json").exists()
                else "deployment-guidance.json")
    assert guidance == workspace.read_json(workspace.run_dir(api_ws) / filename)


def test_runs_show_uses_same_run_view(api_ws, capsys):
    from aies import cli

    assert cli.main(["runs", "show", api_ws, "--json"]) == 0
    body = json.loads(capsys.readouterr().out)
    assert body["kind"] == "aies-run-view"
    assert body["run_id"] == api_ws


def test_conformance_endpoint(api_ws):
    from aies import api
    status, body = api.route("/conformance")
    # 200 with a report if the corpus is present; 503 if not — never a crash.
    assert status in (200, 503)
    if status == 200:
        assert "valid" in body and "cases" in body


def test_repository_assessment_endpoints_serve_stored_artifact(api_ws):
    from aies import (
        api, compare, comparison_report, executors, workspace,
    )

    repository = workspace.root() / "api-repository"
    repository.mkdir(exist_ok=True)
    (repository / "README.md").write_text("# API fixture", encoding="utf-8")
    result = executors.RepositoryAuditExecutor().execute(
        executors.RepositoryAuditRequest(repository))
    status, listing = api.route("/audits")
    assert status == 200
    assert any(item["audit_id"] == result["audit_id"]
               for item in listing["audits"])
    status, detail = api.route(f"/audits/{result['audit_id']}")
    assert status == 200
    assert detail == workspace.read_json(
        workspace.root() / "audits" / f"{result['audit_id']}.json")
    assert detail["engineering_analysis"]["schema"] == (
        "aies-repository-analysis/v1")

    comparison = compare.compare_repositories(
        [result["audit_id"], result["audit_id"]])
    saved = comparison_report.record(comparison)
    status, listing = api.route("/comparisons")
    assert status == 200
    assert listing["comparisons"][0]["comparison_id"] == (
        saved["comparison_id"])
    status, detail = api.route(
        f"/comparisons/{saved['comparison_id']}")
    assert status == 200
    assert detail == workspace.read_json(
        workspace.root() / "comparisons"
        / f"{saved['comparison_id']}.json")


def test_unknown_path_is_404_and_missing_run_is_404(api_ws):
    from aies import api
    status, unknown = api.route("/nope")
    assert status == 404
    assert unknown["kind"] == "aies-api-error"
    assert unknown["code"] == "route-not-found"

    status, missing = api.route("/runs/does-not-exist/result")
    assert status == 404
    assert missing["code"] == "artifact-not-found"

    status, unsafe = api.route(r"/runs/..\secret/evidence")
    assert status == 400
    assert unsafe["code"] == "invalid-run-id"

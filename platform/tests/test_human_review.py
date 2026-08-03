import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def review_run(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    from aies import workspace

    run_id = "run-human-review-test"
    rdir = workspace.run_dir(run_id)
    (rdir / "responses").mkdir(parents=True)
    response = {
        "scenario_id": "SC-CA05-001",
        "repeat": 1,
        "area": "CA-05",
        "risk_tier": "RT2",
        "request": {"prompt": "Implement the bounded operation safely."},
        "raw_response": "Here is a bounded implementation with tests.",
    }
    workspace.write_json(rdir / "responses" / "SC-CA05-001-r1.json", response)
    dimensions = {
        f"EV{i}": {
            "global_anchors": {"0": "absent", "4": "exemplary"},
            "scenario_criteria": ["Cite observable evidence."],
            "applicability": {"status": "applicable"},
        }
        for i in range(1, 7)
    }
    sheet = {
        "run_id": run_id,
        "instructions": "Use frozen anchors.",
        "rater": {
            "id": None, "name": None, "kind": "human",
            "conflict_declaration": {
                "declared": False, "has_conflict": None, "subject_id": None},
        },
        "items": [{
            "response_record": "SC-CA05-001-r1.json",
            "scenario_id": "SC-CA05-001",
            "repeat": 1,
            "task_label": "Bounded implementation",
            "instrument_digest": None,
            "reviewer_instrument": {
                "evaluation": {
                    "dimensions": dimensions,
                    "failure_conditions": ["Unbounded resource use"],
                }
            },
            "scores": {f"EV{i}": None for i in range(1, 7)},
            "findings": [],
            "failure_conditions_observed": [],
            "grounding_diagnostics": None,
            "review_trace": None,
        }],
    }
    workspace.write_json(rdir / "scoresheet.json", sheet, overwrite=True)
    return run_id, sheet


def test_review_document_joins_full_response_and_frozen_instrument(review_run):
    from aies.human_review import ReviewSession

    run_id, _ = review_run
    document = ReviewSession(run_id).document()
    item = document["sheet"]["items"][0]

    assert document["human_evaluation"] == "optional"
    assert document["qualification_authority"] == "none"
    assert item["task_prompt"].startswith("Implement")
    assert item["raw_response"].startswith("Here is")
    assert "EV6" in item["reviewer_instrument"]["evaluation"]["dimensions"]


def test_review_draft_autosaves_but_cannot_change_item_identity(review_run):
    from aies import workspace
    from aies.human_review import ReviewSession, ReviewWorkspaceError

    run_id, sheet = review_run
    session = ReviewSession(run_id)
    sheet["rater"]["name"] = "Optional reviewer"
    sheet["items"][0]["scores"] = {f"EV{i}": 3 for i in range(1, 7)}

    saved = session.save(sheet)
    assert saved == {"saved": True, "scored_items": 1, "total_items": 1}
    assert workspace.artifact_class(session.draft_path) == "mutable-working-state"
    assert session.sheet()["rater"]["name"] == "Optional reviewer"

    changed = json.loads(json.dumps(sheet))
    changed["items"][0]["response_record"] = "another-response.json"
    with pytest.raises(ReviewWorkspaceError, match="canonical order"):
        session.save(changed)

    tampered = json.loads(json.dumps(sheet))
    tampered["rater"]["kind"] = "automated"
    tampered["items"][0]["scenario_id"] = "SC-TAMPERED"
    tampered["items"][0]["reviewer_instrument"] = {"forged": True}
    session.save(tampered)
    restored = session.sheet()
    assert restored["rater"]["kind"] == "human"
    assert restored["items"][0]["scenario_id"] == "SC-CA05-001"
    assert "forged" not in restored["items"][0]["reviewer_instrument"]


def test_review_submission_reuses_canonical_pipeline(review_run, monkeypatch):
    from aies import engine, evaluation, rating, report
    from aies.human_review import ReviewSession

    run_id, sheet = review_run
    sheet["rater"]["name"] = "Optional reviewer"
    sheet["items"][0]["scores"] = {f"EV{i}": 3 for i in range(1, 7)}
    calls = []
    monkeypatch.setattr(
        rating, "ingest_scores",
        lambda rid, value, **kwargs: calls.append((rid, value)) or ["rating.json"])
    monkeypatch.setattr(engine, "aggregate", lambda rid: {"run_id": rid})
    monkeypatch.setattr(evaluation, "summarize", lambda rid: {"run_id": rid})
    monkeypatch.setattr(report, "write_reports", lambda rid: {"html": "report.html"})

    result = ReviewSession(run_id).submit(sheet)

    assert calls[0][0] == run_id
    assert result["ratings_written"] == 1
    assert result["reports"]["html"] == "report.html"
    assert "qualification admission remains governed" in result["human_evaluation"]


def test_http_workspace_requires_token_and_sets_security_headers(review_run):
    from aies.human_review import ReviewSession, _handler

    session = ReviewSession(review_run[0])
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), _handler(session, "fixed-test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    root = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with pytest.raises(urllib.error.HTTPError) as denied:
            urllib.request.urlopen(root + "/api/review", timeout=2)
        assert denied.value.code == 403

        with urllib.request.urlopen(
                root + "/?token=fixed-test-token", timeout=2) as response:
            html = response.read().decode("utf-8")
            assert "Human EV Review" in html
            assert "Submit, analyze & refresh reports" in html
            assert "Content-Security-Policy" in response.headers
            assert response.headers["Cache-Control"] == "no-store"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_score_parser_exposes_interactive_local_workspace():
    from aies.cli import build_parser

    args = build_parser().parse_args([
        "score", "run-1", "--interactive", "--no-open", "--port", "9876"])
    assert args.interactive is True
    assert args.no_open is True
    assert args.port == 9876

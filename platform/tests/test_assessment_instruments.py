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
        "id": model_id,
        "family": "demo",
        "runtime": "mock",
        "model": model_id,
        "context_window": 32768,
        "provenance": {
            "source": "synthetic",
            "checksum": "sha256:" + "0" * 64,
        },
    }
    path = tmp_path / f"{model_id}.yaml"
    path.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(path)


def test_candidate_and_reviewer_projections_are_separated():
    from aies import assessment_instruments

    scenario, suite = assessment_instruments.find_scenario("SC-CA05-001")
    instrument = assessment_instruments.build(
        scenario, suite_version=suite)
    candidate = assessment_instruments.candidate_projection(instrument)
    reviewer = assessment_instruments.reviewer_projection(instrument)

    assert candidate["task_prompt"] == scenario["prompt"]
    assert "evaluation" not in candidate
    assert "expected_qualities" not in candidate
    assert "calibration" not in candidate
    assert reviewer["expected_qualities"] == scenario["expected_qualities"]
    assert reviewer["evaluation"]["failure_conditions"]
    assert reviewer["calibration"]["ceiling_anchor"]
    assert reviewer["instrument_digest"] == candidate["instrument_digest"]

    mapped_scenario = dict(scenario)
    condition = scenario["failure_conditions"][0]
    mapped_scenario["failure_condition_impacts"] = {condition: ["EV1"]}
    mapped = assessment_instruments.build(
        mapped_scenario, suite_version=suite)
    assert mapped["evaluation"]["failure_condition_impacts"] == {
        condition: ["EV1"]}


def test_run_freezes_instruments_and_binds_responses(ws, tmp_path):
    from aies import assessment_instruments, engine, rating, workspace

    _register(tmp_path, "candidate")
    run = engine.start_qualification(
        "candidate", "research", "RT2", ["CA-05"], workers=4)
    run_id = run["run_id"]
    response_path = sorted(
        (workspace.run_dir(run_id) / "responses").glob("*.json"))[0]
    response = workspace.read_json(response_path)
    instrument = assessment_instruments.load_snapshot(
        run_id, response["scenario_id"])

    assert response["request"]["projection"] == "candidate"
    assert response["request"]["instrument_digest"] == instrument[
        "instrument_digest"]
    assert response["request"]["prompt"] == instrument["task_prompt"]

    sheet = rating.build_scoresheet(run_id)
    sheet["rater"] = {"name": "Human reviewer", "kind": "human"}
    sheet["items"] = [next(
        item for item in sheet["items"]
        if item["scenario_id"] == response["scenario_id"])]
    item = sheet["items"][0]
    item["scores"] = {f"EV{index}": 3 for index in range(1, 7)}
    item["failure_conditions_observed"] = [
        instrument["evaluation"]["failure_conditions"][0]]
    with pytest.raises(rating.RatingError, match="finding attributed"):
        rating.ingest_scores(run_id, sheet, emit_progress=False)
    item["scores"]["EV1"] = 0
    item["findings"] = [{
        "dimension": "EV1",
        "score": 0,
        "finding": "Observed declared failure condition.",
    }]
    assert len(rating.ingest_scores(
        run_id, sheet, emit_progress=False)) == 1


def test_reviewer_prompt_contains_hidden_instrument_not_subject_identity():
    from aies import assessment_instruments
    from aies.model_review import _review_prompt

    scenario, suite = assessment_instruments.find_scenario("SC-CA05-001")
    instrument = assessment_instruments.build(
        scenario, suite_version=suite)
    prompt = _review_prompt(instrument, "candidate answer")

    assert instrument["instrument_digest"] in prompt
    assert "expected_qualities" in prompt
    assert "failure_conditions" in prompt
    assert "ceiling_anchor" in prompt
    assert "candidate answer" in prompt
    assert "local-qwen" not in prompt


def test_missing_or_conflicting_reviewer_trace_is_explicit():
    from aies import assessment_instruments
    from aies.model_review import validate_review_trace

    scenario, suite = assessment_instruments.find_scenario("SC-CA05-001")
    instrument = assessment_instruments.build(
        scenario, suite_version=suite)
    scores = {f"EV{index}": 3 for index in range(1, 7)}

    unavailable = validate_review_trace(instrument, scores, None)
    assert unavailable["protocol_status"] == "unavailable"
    conflicted = validate_review_trace(instrument, scores, {
        "dimension_evidence": [
            {
                "dimension": f"EV{index}",
                "criteria_satisfied": ["criterion"],
                "criteria_missed": [],
                "evidence": ["response evidence"],
            }
            for index in range(1, 7)
        ],
        "failure_conditions_triggered": [
            instrument["evaluation"]["failure_conditions"][0]],
        "instrument_digest": instrument["instrument_digest"],
    })
    assert conflicted["protocol_status"] == "conflicted"
    assert "has no zero score" in conflicted["protocol_issues"][0]


@pytest.mark.parametrize(
    "subject_kind,modality",
    [
        ("repository", "static-repository-observation"),
        ("mcp_server", "protocol-conformance-observation"),
        ("rag_system", "retrieval-trace-observation"),
        ("pipeline", "pipeline-execution-observation"),
    ],
)
def test_non_generative_instruments_do_not_invent_candidate_prompts(
        subject_kind, modality):
    from aies import assessment_instruments

    instrument = assessment_instruments.build_evidence_instrument(
        instrument_id=f"INST-{subject_kind}",
        subject_kind=subject_kind,
        title=f"{subject_kind} evidence",
        evidence_criteria=[{
            "id": "criterion-1",
            "question": "Is the declared behavior directly evidenced?",
        }],
        standards=[{"id": "AIES-TEST", "title": "Test standard"}],
        evidence_modality=modality,
        adapter_profile="fixture/v1",
    )
    assert instrument["collection"]["interaction"] == (
        "evidence-adapter-observation")
    assert instrument["collection"]["subject_projection"] is None
    assert "task_prompt" not in instrument
    with pytest.raises(assessment_instruments.InstrumentError):
        assessment_instruments.candidate_projection(instrument)


def test_guided_execution_is_isolated_and_can_compare_baseline(ws, tmp_path):
    from aies import standards_guided, workspace

    _register(tmp_path, "candidate")
    _register(tmp_path, "judge")
    progress_events = []
    result = standards_guided.execute(
        "candidate",
        "SC-CA05-001",
        compare_baseline=True,
        judge="judge",
        progress_callback=progress_events.append,
    )

    assert result["mode"]["qualification_eligible"] is False
    assert result["baseline"]["projection"] == "candidate-task-only"
    assert result["guided"]["projection"] == "task-scoped-standards-context"
    assert result["score_delta_guided_minus_baseline"] is not None
    assert result["mode"]["judge"]["id"] == "judge"
    assert result["mode"]["judge"]["same_deployment_as_subject"] is False
    assert result["baseline"]["review"]["review_trace"][
        "protocol_status"] == "valid"
    assert {
        event["stage"] for event in progress_events
    } == {
        "baseline-execution", "guided-execution", "baseline-review",
        "guided-review", "artifact-write",
    }
    assert all(
        event["total_elapsed_seconds"] >= 0 for event in progress_events)
    assert Path(result["artifact"]).is_file()
    assert not list(workspace.runs_dir().glob("guided-*"))


def test_traceability_report_links_standard_to_evidence(ws, tmp_path):
    from aies import api, engine, model_review, report, workspace

    _register(tmp_path, "candidate")
    _register(tmp_path, "judge")
    run = engine.start_qualification(
        "candidate", "research", "RT2", ["CA-05"], workers=4,
        run_purpose="engineering-evaluation")
    model_review.run_model_review(
        run["run_id"], "judge", workers=4, batch_size=8)
    engine.aggregate(run["run_id"])
    paths = report.write_reports(run["run_id"])

    trace = json.loads(
        Path(paths["standards_traceability_json"]).read_text(encoding="utf-8"))
    assert trace["rows"]
    assert trace["rows"][0]["standard"]["id"] == "AIES-AESQS-ER-01"
    assert trace["rows"][0]["instrument_digest"]
    assert trace["rows"][0]["recommendations"]
    assert trace["rows"][0]["recommendations"][0]["product"] == (
        "engineering-fit-guidance")
    assert (workspace.run_dir(run["run_id"])
            / "standards-traceability.html").is_file()
    report_view = json.loads(
        Path(paths["report_view"]).read_text(encoding="utf-8"))
    assert report_view["artifacts"]["standards_traceability"] == (
        "standards-traceability.json")
    executive = json.loads(
        Path(paths["executive_json"]).read_text(encoding="utf-8"))
    assert executive["artifacts"]["standards_traceability"]["html"] == (
        "standards-traceability.html")
    assert "standards-traceability.html" in Path(
        paths["html"]).read_text(encoding="utf-8")
    status, api_trace = api.route(
        f"/runs/{run['run_id']}/standards-traceability")
    assert status == 200
    assert api_trace["kind"] == "aies-standards-traceability"


def test_traceability_rendering_does_not_migrate_legacy_evidence(ws):
    from aies import standards_traceability, workspace

    run_id = "run-legacy-read-only"
    rdir = workspace.run_dir(run_id)
    (rdir / "responses").mkdir(parents=True)
    (rdir / "ratings").mkdir()
    workspace.write_json(rdir / "responses" / "SC-CA05-001-r1.json", {
        "scenario_id": "SC-CA05-001",
        "area": "CA-05",
        "repeat": 1,
        "request": {"prompt": "legacy prompt"},
        "raw_response": "legacy response",
    })
    workspace.write_json(rdir / "ratings" / "legacy.json", {
        "rates_response": "SC-CA05-001-r1.json",
        "scenario_id": "SC-CA05-001",
        "scores": {f"EV{index}": 3 for index in range(1, 7)},
        "findings": [],
        "provenance": {"rater": "legacy"},
    })

    trace = standards_traceability.build(run_id)
    assert trace["rows"]
    assert trace["rows"][0]["trace_status"] == "unavailable"
    assert not (rdir / "instruments").exists()

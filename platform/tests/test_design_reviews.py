"""Human design-review decisions stay attributable, exact, and invalidatable."""

import copy
import json


def _ledger(scenario, content_hash):
    return {
        "kind": "aies-design-review-ledger-v1",
        "schema_version": 1,
        "content_hash_method": "aies-scenario-content-v1",
        "events": [{
            "id": "DR-TEST-001",
            "decision": "accepted",
            "reviewer": {"id": "human-1", "name": "Test Human", "role": "reviewer"},
            "recorded_at": "2026-07-23T00:00:00+00:00",
            "rationale": "Explicit test acceptance of this exact instrument.",
            "human_accountability": True,
            "instrument_count": 1,
            "empirical_calibration": False,
            "instruments": [{"scenario_id": scenario["id"],
                             "content_hash": content_hash}],
        }],
    }


def _scenario():
    return {
        "id": "SC-CA01-999",
        "area": "CA-01",
        "risk_tier": "RT2",
        "prompt": "Make an evidence-bound engineering recommendation.",
        "calibration": {
            "objective": "measure evidence-bound reasoning",
            "ceiling_anchor": "The answer tests its assumptions.",
            "empirical_status": {
                "design_reviewed": False,
                "empirically_calibrated": False,
            },
        },
    }


def test_acceptance_is_exact_and_a_content_change_reopens_the_instrument(tmp_path):
    from aies import design_reviews

    scenario = _scenario()
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(_ledger(
        scenario, design_reviews.scenario_content_hash(scenario))), encoding="utf-8")

    accepted = design_reviews.apply_effective_review(scenario, path)
    assert accepted["calibration"]["empirical_status"] == {
        "design_reviewed": True, "empirically_calibrated": False}

    changed = copy.deepcopy(scenario)
    changed["prompt"] += " Include two alternatives."
    reopened = design_reviews.apply_effective_review(changed, path)
    assert reopened["calibration"]["empirical_status"]["design_reviewed"] is False


def test_empirical_workflow_flags_do_not_change_the_reviewed_content_hash():
    from aies import design_reviews

    scenario = _scenario()
    before = design_reviews.scenario_content_hash(scenario)
    scenario["calibration"]["empirical_status"]["design_reviewed"] = True
    scenario["calibration"]["empirical_status"]["empirically_calibrated"] = True
    assert design_reviews.scenario_content_hash(scenario) == before


def test_shipped_ledger_covers_the_approved_tranche_and_nothing_is_empirical():
    from aies import design_reviews, runner, suites

    scenarios = []
    for area in runner.all_area_codes():
        scenarios.extend(runner.load_area(area)[1])
    status = design_reviews.ledger_status(scenarios)
    assert status["events"] == 1
    assert status["accepted"] == 268
    assert status["stale"] == 0
    assert status["unknown"] == 0

    totals = suites.calibrate()["totals"]
    assert totals["design_reviewed"] == totals["scenarios"] == 484
    assert totals["empirically_calibrated"] == 0


def test_ledger_rejects_an_unattributed_decision(tmp_path):
    from aies import design_reviews

    scenario = _scenario()
    data = _ledger(scenario, design_reviews.scenario_content_hash(scenario))
    del data["events"][0]["reviewer"]
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    try:
        design_reviews.load_ledger(path)
    except design_reviews.DesignReviewError as exc:
        assert "reviewer id, name, and role" in str(exc)
    else:  # pragma: no cover - guardrail assertion
        raise AssertionError("unattributed review decision was accepted")

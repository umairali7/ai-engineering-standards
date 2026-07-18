"""Scenario calibration metadata (CALIBRATION.md): a scenario is a measurement
instrument, and the `calibration` block records why it exists and how well it
measures. Optional today, validated when present, surfaced by `suites calibrate`.
The load-bearing checks: the ceiling anchor is required, and nothing can claim to
be empirically calibrated before it is design-reviewed (honesty guard)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def _scn(**cal):
    return {"id": "SC-CA07-099", "area": "CA-07", "risk_tier": "RT2",
            "prompt": "p", "expected_qualities": ["q"],
            "rubric": {d: ["a"] for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")},
            "calibration": cal}


def _validate_one(scn):
    from aies import suites
    errors, warnings = [], []
    suites._validate_scenario(Path("SC-CA07-099.yaml"), scn, "CA-07", {}, errors, warnings)
    return [e["message"] for e in errors]


def _good_cal(**over):
    cal = {"objective": "o", "ceiling_anchor": "what a 4 does",
           "empirical_status": {"design_reviewed": True, "empirically_calibrated": False}}
    cal.update(over)
    return cal


def test_valid_calibration_block_passes():
    assert _validate_one(_scn(**_good_cal())) == []


def test_ceiling_anchor_is_required():
    cal = _good_cal(); del cal["ceiling_anchor"]
    assert any("ceiling" in m for m in _validate_one(_scn(**cal)))


def test_objective_and_empirical_status_required():
    cal = _good_cal(); del cal["objective"]
    assert any("objective" in m for m in _validate_one(_scn(**cal)))
    cal2 = _good_cal(); del cal2["empirical_status"]
    assert any("empirical_status" in m for m in _validate_one(_scn(**cal2)))


def test_honesty_guard_no_empirical_without_design_review():
    cal = _good_cal(empirical_status={"design_reviewed": False, "empirically_calibrated": True})
    assert any("empirically_calibrated cannot be true" in m for m in _validate_one(_scn(**cal)))


def test_unknown_key_and_target_mismatch_rejected():
    assert any("unknown key" in m for m in _validate_one(_scn(**_good_cal(bogus=1))))
    assert any("target_competency" in m
               for m in _validate_one(_scn(**_good_cal(target_competency="CA-05"))))


def test_hold_out_twin_must_be_a_scenario_id():
    assert any("hold_out_twin" in m for m in _validate_one(_scn(**_good_cal(hold_out_twin="nope"))))
    assert _validate_one(_scn(**_good_cal(hold_out_twin="SC-CA07-007"))) == []


def test_shipped_ca07_worked_example_is_calibrated_and_still_valid():
    """The CA-07 worked example: some scenarios carry calibration metadata with
    ceiling anchors, and the whole suite still validates."""
    from aies import suites
    report = suites.calibrate()
    ca07 = next(a for a in report["areas"] if a["area"] == "CA-07")
    assert ca07["calibrated"] >= 3 and ca07["ceiling_anchor"] >= 3
    assert ca07["refuse_case"] >= 2 and ca07["hold_out_twins"] >= 1
    assert report["totals"]["empirically_calibrated"] == 0        # honest: no panel yet
    assert suites.validate()["valid"]                              # nothing broke

"""Conformance tests keyed to AESQS requirement IDs (ADR-0002 mitigation:
the engine's enforced behavior maps to the standard's requirements)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aies import constants as C
from aies.scoring import (apply_gates, confidence_interval, derive_cl,
                          effective_weights, al_envelope, score_area,
                          score_dimension)


def _items(vector, n):
    return [dict(zip(C.DIMENSIONS, vector)) for _ in range(n)]


def test_weights_sum_to_one_per_tier():
    for rt, w in C.WEIGHTS.items():
        assert abs(sum(w.values()) - 1.0) < 1e-9, rt


def test_worked_example_cs01_s4():
    """AIES-AESQS-CS-01 §4 worked continuation: vector (3,2,3,3,2,4) at
    RT2 weights gives A = 2.90 when decision values equal the scores."""
    w = C.WEIGHTS["RT2"]
    vector = dict(zip(C.DIMENSIONS, (3, 2, 3, 3, 2, 4)))
    a = sum(w[d] * vector[d] for d in C.DIMENSIONS)
    assert abs(a - 2.90) < 1e-9


def test_scores_must_be_integers_0_4():
    # AIES-AESQS-ER-01-R04: no half points
    with pytest.raises(ValueError):
        score_dimension("EV1", [3, 2.5])  # type: ignore[list-item]
    with pytest.raises(ValueError):
        score_dimension("EV1", [5])


def test_lower_bound_is_decision_value():
    # AIES-AESQS-CS-01-R02/R11: variance widens the interval and the
    # lower bound, not the mean, drives decisions.
    mean, lo, hi = confidence_interval([4, 0, 4, 0, 4, 0])
    assert mean == 2.0 and lo < 2.0 < hi


def test_gate_fails_on_lower_bound_even_when_mean_passes():
    # AIES-AESQS-CS-01-R13
    scores = [4, 1, 4, 1, 4, 1, 4, 1]  # mean 2.5 == RT2 EV3 gate, high variance
    d = {ev: score_dimension(ev, scores) for ev in C.DIMENSIONS}
    assert d["EV3"].mean >= C.GATES["RT2"]["EV3"]
    gates, all_passed, ev3_fail = apply_gates(d, "RT2")
    ev3 = next(g for g in gates if g.dimension == "EV3")
    assert not ev3.passed and ev3_fail and not all_passed


def test_single_ev3_zero_fails_hard_gate_at_rt3():
    # AIES-AESQS-CS-01-R04: one unsafe output at RT3-RT4 fails the gate.
    scores = [4] * 60 + [0]  # lower bound comfortably above 3.0
    d = {ev: score_dimension(ev, [4] * 61) for ev in C.DIMENSIONS}
    d["EV3"] = score_dimension("EV3", scores)
    assert d["EV3"].ci_low > C.GATES["RT3"]["EV3"]
    gates, all_passed, ev3_fail = apply_gates(d, "RT3")
    assert ev3_fail and not all_passed


def test_profile_cannot_exceed_adjustment_bound():
    # AIES-AESQS-CS-01-R03 / PLATFORM.md D3
    with pytest.raises(ValueError):
        effective_weights("RT2", {"EV1": 0.10, "EV5": -0.10})


def test_profile_cannot_reduce_ev3_ev6_floor_at_rt3():
    # rebalanced to sum 1.0 but shaving safety+traceability
    with pytest.raises(ValueError):
        effective_weights("RT3", {"EV3": -0.05, "EV6": -0.05, "EV1": 0.05, "EV4": 0.05})


def test_profile_must_keep_weights_summing_to_one():
    with pytest.raises(ValueError):
        effective_weights("RT1", {"EV1": 0.05})  # sum now 1.05


def test_ai_never_cl4():
    # AIES-AESQS-CS-01-R07
    cl, _ = derive_cl(4.0, True, "ai")
    assert cl == "CL3"
    cl_h, _ = derive_cl(4.0, True, "human")
    assert cl_h == "CL4"


def test_failed_gates_mean_no_cl():
    cl, note = derive_cl(3.9, False, "ai")
    assert cl is None and "gates failed" in note


def test_al_envelope_min_rule_and_no_al4():
    # AIES-AESQS-CS-01-R08/R09
    env = al_envelope("CL3")
    assert env == {"RT1": "AL3", "RT2": "AL3", "RT3": "AL2", "RT4": "AL1"}
    assert "AL4" not in env.values()
    env2 = al_envelope("CL2")
    assert env2 == {"RT1": "AL2", "RT2": "AL2", "RT3": "AL2", "RT4": "AL1"}
    env0 = al_envelope(None)
    assert set(env0.values()) <= {"AL0", "AL1"}


def test_decisional_labeling_by_sample_size():
    # AIES-AESQS-CS-01 §6 / PLATFORM.md D6: AI at RT2 needs 30 items.
    res_small = score_area("CA-05", "RT2", _items((3, 3, 3, 3, 3, 3), 12))
    assert not res_small.decisional
    res_big = score_area("CA-05", "RT2", _items((3, 3, 3, 3, 3, 3), 30))
    assert res_big.decisional


def test_end_to_end_area_scoring_grants_scoped_cl_not_global_verdict():
    res = score_area("CA-05", "RT2", _items((3, 3, 3, 3, 3, 3), 30))
    assert res.gates_passed
    assert res.aggregate == 3.0
    assert res.cl == "CL2"                      # 2.5 <= 3.0 < 3.2
    assert res.al_envelope["RT2"] == "AL2"      # min(AL3 cap, CL2->AL2)
    # No global pass/fail exists anywhere on the result (PLATFORM.md D4).
    assert not hasattr(res, "production_ready")

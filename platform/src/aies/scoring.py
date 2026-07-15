"""Scoring Engine — implements AIES-AESQS-CS-01 without local invention.

Input: rated evidence items (integer 0-4 scores per EV dimension).
Output: per-dimension decision values (lower confidence bounds),
gate outcomes, aggregate A, CL derivation, and RT x AL envelopes.

PLATFORM.md §6 is the governing section; D2/D3/D4/D6 apply.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import constants as C


@dataclass
class DimensionScore:
    dimension: str
    n: int
    mean: float
    ci_low: float          # decision value (AIES-AESQS-CS-01-R02)
    ci_high: float
    has_zero: bool         # any single item scored 0 on this dimension


@dataclass
class GateResult:
    dimension: str
    threshold: float
    decision_value: float
    passed: bool
    reason: str = ""


@dataclass
class AreaResult:
    area: str
    risk_tier: str
    subject_kind: str                    # "ai" | "human"
    n_scored: int
    min_sample: int
    decisional: bool
    dimensions: dict[str, DimensionScore] = field(default_factory=dict)
    gates: list[GateResult] = field(default_factory=list)
    gates_passed: bool = False
    ev3_hard_fail: bool = False
    aggregate: float | None = None       # A, over decision values
    weights_used: dict[str, float] = field(default_factory=dict)
    cl: str | None = None                # bounded from above by scores only
    cl_note: str = ""
    al_envelope: dict[str, str] = field(default_factory=dict)  # RT -> recommended AL


def confidence_interval(scores: list[int]) -> tuple[float, float, float]:
    """Mean and two-sided 90% t-interval, clamped to the 0-4 scale.

    With n == 1 the interval is undefined; the decision value collapses
    to the single score and the result can never be decisional anyway
    (sample minimums, AIES-AESQS-CS-01-R10).
    """
    n = len(scores)
    if n == 0:
        raise ValueError("cannot score an empty sample")
    mean = sum(scores) / n
    if n == 1:
        return mean, float(scores[0]), float(scores[0])
    var = sum((s - mean) ** 2 for s in scores) / (n - 1)
    half = C.t_critical(n - 1) * math.sqrt(var / n)
    return mean, max(0.0, mean - half), min(4.0, mean + half)


def score_dimension(dimension: str, scores: list[int]) -> DimensionScore:
    for s in scores:
        if s not in C.VALID_SCORES:
            raise ValueError(
                f"invalid rubric score {s!r} on {dimension}: scores are "
                "integers 0-4 (AIES-AESQS-ER-01-R04, no half points)"
            )
    mean, lo, hi = confidence_interval(scores)
    return DimensionScore(dimension, len(scores), round(mean, 3),
                          round(lo, 3), round(hi, 3), 0 in scores)


def apply_gates(dims: dict[str, DimensionScore], risk_tier: str) -> tuple[list[GateResult], bool, bool]:
    """Minimum-gate rule (AIES-AESQS-CS-01 §3.1, R04, R05, R13).

    Gates are evaluated against decision values (lower confidence
    bounds), so variance that drops a bound below its gate fails the
    gate even when the mean passes (R13). One zero on EV3 at RT3-RT4
    fails the hard gate outright (R04).
    """
    gates: list[GateResult] = []
    ev3_hard_fail = False
    all_passed = True
    for dim in C.DIMENSIONS:
        threshold = C.GATES[risk_tier][dim]
        d = dims.get(dim)
        if d is None:
            gates.append(GateResult(dim, threshold, 0.0, False, "no scored evidence"))
            all_passed = False
            continue
        passed = d.ci_low >= threshold
        reason = ""
        if dim == "EV3" and risk_tier in C.EV3_ZERO_FAIL_TIERS and d.has_zero:
            passed = False
            ev3_hard_fail = True
            reason = ("single evidence item scored 0 on EV3 at "
                      f"{risk_tier} (AIES-AESQS-CS-01-R04)")
        elif not passed:
            reason = (f"decision value {d.ci_low} below gate {threshold}"
                      + ("" if d.mean < threshold else
                         f" although mean {d.mean} passes (AIES-AESQS-CS-01-R13)"))
        if dim == "EV3" and not passed:
            ev3_hard_fail = True
        gates.append(GateResult(dim, threshold, d.ci_low, passed, reason))
        all_passed = all_passed and passed
    return gates, all_passed, ev3_hard_fail


def effective_weights(risk_tier: str, adjustments: dict[str, float] | None) -> dict[str, float]:
    """Apply profile weight adjustments under AIES-AESQS-CS-01-R03.

    Per-dimension delta capped at +/-0.05; weights must still sum to 1;
    combined EV3+EV6 weight must not fall below the tier baseline for
    RT3-RT4. Violations raise: gates and floors are non-negotiable (D3).
    """
    base = dict(C.WEIGHTS[risk_tier])
    if not adjustments:
        return base
    out = dict(base)
    for dim, delta in adjustments.items():
        if dim not in C.DIMENSIONS:
            raise ValueError(f"unknown dimension in profile adjustment: {dim}")
        if abs(delta) > C.MAX_WEIGHT_ADJUSTMENT + 1e-9:
            raise ValueError(
                f"profile adjustment for {dim} is {delta:+.3f}; the bound is "
                f"±{C.MAX_WEIGHT_ADJUSTMENT} (AIES-AESQS-CS-01-R03)"
            )
        out[dim] = base[dim] + delta
        if out[dim] < 0:
            raise ValueError(f"adjusted weight for {dim} is negative")
    total = sum(out.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(
            f"adjusted weights sum to {total:.3f}, not 1.0 — rebalance the profile"
        )
    if risk_tier in ("RT3", "RT4"):
        floor = base["EV3"] + base["EV6"]
        if out["EV3"] + out["EV6"] < floor - 1e-9:
            raise ValueError(
                "profile reduces combined EV3+EV6 weight below the "
                f"{risk_tier} floor of {floor} (AIES-AESQS-CS-01-R03)"
            )
    return out


def derive_cl(aggregate: float, gates_passed: bool, subject_kind: str) -> tuple[str | None, str]:
    """Aggregate -> CL, bounded from above by scores (AIES-AESQS-CS-01 §4).

    Descriptor co-requisites (R06) cannot be checked by a tool; the
    returned note flags them for human confirmation. AI systems are
    capped at CL3 (R07).
    """
    if not gates_passed:
        return None, "gates failed: no CL awardable at this tier (AIES-AESQS-CS-01-R04/R05)"
    level = None
    for threshold, cl in C.CL_THRESHOLDS:
        if aggregate >= threshold:
            level = cl
            break
    if level is None:
        return None, f"aggregate {aggregate:.2f} below CL1 threshold 2.0"
    if subject_kind == "ai" and C.AL_ORDER:  # AI cap
        if level == "CL4":
            level = C.AI_MAX_CL
    note = ("score-bounded level; descriptor co-requisites per "
            "AIES-AESQS-CF-01 §3 require human confirmation (AIES-AESQS-CS-01-R06)")
    return level, note


def al_envelope(cl: str | None) -> dict[str, str]:
    """Recommended autonomy per risk tier: min(RT cap, CL-earned cap).

    AL4 never appears at initial qualification (AIES-AESQS-CS-01-R08);
    the CL_AL_CAP table tops out at AL3 by construction.
    """
    earned = C.CL_AL_CAP.get(cl, "AL1")
    return {rt: C.al_min(C.RT_AL_CAP[rt], earned) for rt in C.RISK_TIERS}


def score_area(
    area: str,
    risk_tier: str,
    item_scores: list[dict[str, int]],
    subject_kind: str = "ai",
    weight_adjustments: dict[str, float] | None = None,
) -> AreaResult:
    """Score one competency area from rated evidence items.

    item_scores: one dict per scored evidence item, mapping EV1-EV6 to
    integer rubric scores. All executed runs must be present —
    discarding runs violates AIES-AESQS-CS-01-R12.
    """
    if risk_tier not in C.RISK_TIERS:
        raise ValueError(f"unknown risk tier {risk_tier!r}")
    if subject_kind not in C.MIN_SAMPLE:
        raise ValueError(f"subject kind must be one of {sorted(C.MIN_SAMPLE)}")

    result = AreaResult(
        area=area,
        risk_tier=risk_tier,
        subject_kind=subject_kind,
        n_scored=len(item_scores),
        min_sample=C.MIN_SAMPLE[subject_kind][risk_tier],
        decisional=len(item_scores) >= C.MIN_SAMPLE[subject_kind][risk_tier],
    )
    if not item_scores:
        result.cl_note = "no scored evidence"
        return result

    for dim in C.DIMENSIONS:
        scores = [item[dim] for item in item_scores if dim in item]
        if scores:
            result.dimensions[dim] = score_dimension(dim, scores)

    result.gates, result.gates_passed, result.ev3_hard_fail = apply_gates(
        result.dimensions, risk_tier
    )
    result.weights_used = effective_weights(risk_tier, weight_adjustments)
    if all(d in result.dimensions for d in C.DIMENSIONS):
        result.aggregate = round(
            sum(result.weights_used[d] * result.dimensions[d].ci_low
                for d in C.DIMENSIONS), 3
        )
        result.cl, result.cl_note = derive_cl(
            result.aggregate, result.gates_passed, subject_kind
        )
    else:
        result.cl, result.cl_note = None, "not all dimensions have scored evidence"
    result.al_envelope = al_envelope(result.cl)
    return result

#!/usr/bin/env python3
"""Generate the golden Evidence Package conformance corpus (CONFORMANCE-POLICY.md).

Each case is an immutable Evidence Package + the assessment to decide it under +
the expected Canonical outcome under a stated decision-semantics version. The
corpus is the ARBITER: any decision engine (the reference engine, or a
third-party one) is conformant to AESQS decision semantics iff it reproduces the
expected outcome and reason kinds for every case.

Run once to (re)materialise conformance/corpus/. The emitted JSON files are the
committed, frozen corpus; this generator documents how they were built. Values
are static (no timestamps/randomness) so the corpus is byte-stable.
"""

from __future__ import annotations

import json
from pathlib import Path

CORPUS = Path(__file__).resolve().parent / "corpus"
SEMANTICS = "1.0"                       # AESQS decision-semantics version covered
_GATES_PASS = [{"dimension": d, "passed": True}
               for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")]
_GATES_EV3_FAIL = [{"dimension": d, "passed": d != "EV3"}
                   for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")]


def area(*, decisional=True, gates_passed=True, ev3_hard_fail=False, cl="CL3",
         n=42, min_sample=30, aggregate=3.4):
    return {"decisional": decisional, "gates_passed": gates_passed,
            "ev3_hard_fail": ev3_hard_fail, "cl": cl, "n_scored": n,
            "min_sample": min_sample, "aggregate_A": aggregate,
            "gates": _GATES_EV3_FAIL if (ev3_hard_fail or not gates_passed) else _GATES_PASS}


def package(areas: dict) -> dict:
    return {
        "run_id": "conformance-fixture", "kind": "evidence-package",
        "evidence_schema": 1, "grant_status": "no grant — conformance fixture",
        "profile": "coder", "profile_version": "1.0.0", "risk_tier": "RT2",
        "subject_kind": "ai", "suite_versions": {},
        "model": {"registry_id": "fixture-model", "checksum": "sha256:" + "f" * 64},
        "environment_fingerprint": {"runtime": {"id": "fixture"},
                                    "fingerprint_hash": "sha256:" + "e" * 64},
        "raters": [], "rater_kinds": [], "aggregated_at": "2026-01-01T00:00:00Z",
        "areas": areas,
    }


def assessment(*comps) -> dict:
    # The RESOLVED form the decision engine consumes (requirement is a string,
    # produced by assessments.resolve at runner selection). The corpus stores
    # exactly what the engine's decide(evidence, assessment) contract receives.
    return {"id": "conformance", "version": "1.0.0", "schema": 1, "profile": "coder",
            "risk_tier": "RT2", "competencies": list(comps),
            "areas": [c["area"] for c in comps]}


def mand(a, min_cl=None):
    return {"area": a, "requirement": "mandatory", "weight": None, "min_cl": min_cl}


def adv(a):
    return {"area": a, "requirement": "advisory", "weight": None, "min_cl": None}


# (case-id, evidence areas, assessment, expected outcome, expected reason kinds)
CASES = [
    ("all-pass",
     {"CA-05": area()},
     assessment(mand("CA-05")),
     "PASS", []),

    ("mandatory-gate-fail",
     {"CA-07": area(gates_passed=False, ev3_hard_fail=True)},
     assessment(mand("CA-07")),
     "FAIL", ["mandatory-gate"]),

    ("min-cl-unmet",
     {"CA-07": area(cl="CL2")},
     assessment(mand("CA-07", min_cl="CL3")),
     "FAIL", ["min-cl"]),

    ("insufficient-evidence",
     {"CA-05": area(decisional=False, n=10, min_sample=30)},
     assessment(mand("CA-05")),
     "INSUFFICIENT EVIDENCE", ["insufficient-evidence"]),

    ("assessment-error-missing-area",
     {"CA-05": area()},
     assessment(mand("CA-05"), mand("CA-07")),
     "INCONCLUSIVE", ["assessment-error"]),

    ("advisory-failure-ignored",
     {"CA-05": area(), "CA-09": area(gates_passed=False, ev3_hard_fail=True)},
     assessment(mand("CA-05"), adv("CA-09")),
     "PASS", []),

    ("strong-does-not-offset-failing",
     {"CA-05": area(cl="CL3", aggregate=3.95),                  # strong
      "CA-07": area(gates_passed=False, ev3_hard_fail=True)},   # failing mandatory
     assessment(mand("CA-05"), mand("CA-07")),
     "FAIL", ["mandatory-gate"]),

    ("precedence-fail-over-inconclusive",
     {"CA-07": area(gates_passed=False, ev3_hard_fail=True)},   # FAIL
     assessment(mand("CA-07"), mand("CA-04")),                   # CA-04 missing -> INCONCLUSIVE
     "FAIL", ["assessment-error", "mandatory-gate"]),
]


def main() -> None:
    CORPUS.mkdir(parents=True, exist_ok=True)
    for case_id, areas, asmt, outcome, reason_kinds in CASES:
        d = CORPUS / case_id
        d.mkdir(exist_ok=True)
        _write(d / "evidence-package.json", package(areas))
        _write(d / "assessment.json", asmt)
        _write(d / "expected.json", {
            "decision_semantics_version": SEMANTICS,
            "outcome": outcome,
            "reason_kinds": sorted(reason_kinds),
        })
    print(f"wrote {len(CASES)} cases to {CORPUS}")


def _write(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

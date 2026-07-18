#!/usr/bin/env python3
"""Example FOREIGN decision engine — a self-contained reimplementation of AESQS
decision semantics v1.0 (AIES-AESQS-CS-01 §8), with NO dependency on the `aies`
package. It exists to demonstrate that an independent implementation can reproduce
the standard's semantics from the spec alone and self-verify against the shared
golden corpus:

    aies conform engine --engine "python conformance/example_engine.py"

Contract: read {"evidence": <evidence-package>, "assessment": <resolved
assessment>} as JSON on stdin; print the Canonical Assessment Result (at least
outcome + decisions.reasons[].kind + metadata.decision_semantics_version) as JSON
on stdout. A conformant engine reproduces the corpus's expected outcomes.
"""

import json
import sys

SEVERITY = {"FAIL": 3, "INCONCLUSIVE": 2, "INSUFFICIENT EVIDENCE": 1, "PASS": 0}
CL_RANK = {"CL1": 1, "CL2": 2, "CL3": 3, "CL4": 4}


def competency_outcome(area, comp, areas):
    d = areas.get(area)
    if d is None:                                                   # not evaluated
        return "INCONCLUSIVE", {"kind": "assessment-error"}
    if not d.get("decisional"):
        return "INSUFFICIENT EVIDENCE", {"kind": "insufficient-evidence"}
    if d.get("ev3_hard_fail") or not d.get("gates_passed", True):
        return "FAIL", {"kind": "mandatory-gate"}
    min_cl = comp.get("min_cl")
    if min_cl and CL_RANK.get(d.get("cl"), 0) < CL_RANK.get(min_cl, 0):
        return "FAIL", {"kind": "min-cl"}
    return "PASS", None


def decide(evidence, assessment):
    areas = evidence.get("areas", {})
    reasons, mandatory_outcomes = [], []
    for comp in assessment.get("competencies", []):
        req = comp.get("requirement", "mandatory")
        outcome, reason = competency_outcome(comp["area"], comp, areas)
        if req == "mandatory":                                      # only mandatory decides
            mandatory_outcomes.append(outcome)
            if reason:
                reasons.append({"area": comp["area"], **reason})
    overall = "PASS"
    if mandatory_outcomes:
        overall = max(mandatory_outcomes, key=lambda o: SEVERITY[o])
    return {"outcome": overall,
            "decisions": {"overall": overall, "reasons": reasons},
            "metadata": {"decision_semantics_version": "1.0"}}


if __name__ == "__main__":
    payload = json.load(sys.stdin)
    json.dump(decide(payload["evidence"], payload["assessment"]), sys.stdout)

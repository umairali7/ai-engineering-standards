"""Decision-engine conformance — verify an engine against the golden corpus.

This is the executable check behind *decision-engine conformance*
(CONFORMANCE-POLICY.md §1-2): the conformance suite is the ARBITER, and it is
data-first so it can judge any engine, not only the one it shipped with. It
replays every case in the golden Evidence Package corpus through a `decide`
function and checks the outcome, reason kinds, and decision-semantics version
against the case's `expected.json`.

By default it verifies the reference engine (`decision.decide`). A third-party
engine is verified by passing a different `decide_fn` (e.g. a subprocess
wrapper) against the SAME corpus — that is what "conformant to AESQS decision
semantics vX.Y" means. (Distinct from `conformance.py`, which handles conformance
*statements* per docs/CONFORMANCE.md.)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from . import decision


class ConformanceError(Exception):
    pass


def default_corpus_dir() -> Path | None:
    """Find conformance/corpus by walking up from this file and from the cwd."""
    seeds = [Path(__file__).resolve()]
    try:
        seeds.append(Path.cwd().resolve() / "_")
    except OSError:
        pass
    for seed in seeds:
        for parent in seed.parents:
            candidate = parent / "conformance" / "corpus"
            if candidate.is_dir():
                return candidate
    return None


def _load_case(case_dir: Path) -> dict:
    def rd(name):
        return json.loads((case_dir / name).read_text(encoding="utf-8"))
    return {"id": case_dir.name, "evidence": rd("evidence-package.json"),
            "assessment": rd("assessment.json"), "expected": rd("expected.json")}


def verify(corpus_dir: Path | None = None,
           decide_fn: Callable[[dict, dict], dict] = decision.decide) -> dict:
    """Replay every corpus case through decide_fn; return a structured report.
    `valid` is True iff every case matches its expected outcome + reason kinds."""
    corpus_dir = corpus_dir or default_corpus_dir()
    if corpus_dir is None or not Path(corpus_dir).is_dir():
        raise ConformanceError(
            "conformance corpus not found (looked for conformance/corpus/); "
            "pass an explicit --corpus path")
    corpus_dir = Path(corpus_dir)

    results = []
    for case_dir in sorted(p for p in corpus_dir.iterdir() if p.is_dir()):
        c = _load_case(case_dir)
        exp = c["expected"]
        result = decide_fn(c["evidence"], c["assessment"])
        got_outcome = result.get("outcome")
        got_reasons = sorted({r["kind"]
                              for r in result.get("decisions", {}).get("reasons", [])})
        got_semantics = result.get("metadata", {}).get("decision_semantics_version")
        mismatches = []
        if got_outcome != exp["outcome"]:
            mismatches.append(f"outcome {got_outcome!r} != expected {exp['outcome']!r}")
        if got_reasons != sorted(exp["reason_kinds"]):
            mismatches.append(
                f"reason kinds {got_reasons} != expected {sorted(exp['reason_kinds'])}")
        if got_semantics != exp["decision_semantics_version"]:
            mismatches.append(
                f"semantics {got_semantics!r} != expected "
                f"{exp['decision_semantics_version']!r}")
        results.append({"case": c["id"], "expected": exp["outcome"],
                        "got": got_outcome, "passed": not mismatches,
                        "mismatches": mismatches})

    passed = sum(1 for r in results if r["passed"])
    return {"valid": bool(results) and passed == len(results),
            "corpus": str(corpus_dir),
            "semantics_version": decision.DECISION_SEMANTICS_VERSION,
            "total": len(results), "passed": passed,
            "failed": len(results) - passed, "cases": results}


def render(report: dict) -> str:
    status = "CONFORMANT" if report["valid"] else "NON-CONFORMANT"
    lines = [f"decision-engine conformance: {status}",
             f"  corpus   : {report['corpus']}",
             f"  semantics: {report['semantics_version']}",
             f"  cases    : {report['passed']}/{report['total']} passed"]
    for r in report["cases"]:
        mark = "ok  " if r["passed"] else "FAIL"
        lines.append(f"  [{mark}] {r['case']:34} -> {r['got']}")
        for m in r["mismatches"]:
            lines.append(f"         - {m}")
    return "\n".join(lines)

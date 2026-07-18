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
import os
import shlex
import subprocess
from pathlib import Path
from typing import Callable

from . import decision


class ConformanceError(Exception):
    pass


def subprocess_decider(cmd: str, timeout: float = 60.0) -> Callable[[dict, dict], dict]:
    """Wrap a FOREIGN decision engine (any language) as a decide_fn, so a
    third-party implementation can self-verify against the same golden corpus
    without importing this package. The command receives `{"evidence":…,
    "assessment":…}` as JSON on stdin and must print the Canonical Assessment
    Result (at least `outcome`, `decisions.reasons[].kind`, and
    `metadata.decision_semantics_version`) as JSON on stdout."""
    argv = shlex.split(cmd, posix=(os.name != "nt"))
    if os.name == "nt":            # posix=False keeps surrounding quotes on tokens
        argv = [a[1:-1] if len(a) >= 2 and a[0] == a[-1] == '"' else a for a in argv]

    def decide(evidence: dict, assessment: dict) -> dict:
        payload = json.dumps({"evidence": evidence, "assessment": assessment})
        try:
            proc = subprocess.run(argv, input=payload, capture_output=True,
                                  text=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise ConformanceError(f"foreign engine {cmd!r} failed to run: {e}")
        if proc.returncode != 0:
            raise ConformanceError(f"foreign engine exited {proc.returncode}: "
                                   f"{proc.stderr.strip()[:300]}")
        try:
            return json.loads(proc.stdout)
        except (json.JSONDecodeError, ValueError):
            raise ConformanceError(f"foreign engine produced non-JSON output: "
                                   f"{proc.stdout.strip()[:300]}")

    return decide


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
           decide_fn: Callable[[dict, dict], dict] = decision.decide,
           engine: str = "reference") -> dict:
    """Replay every corpus case through decide_fn; return a structured report.
    `valid` is True iff every case matches its expected outcome + reason kinds.
    `engine` labels which implementation was verified (reference or a foreign one)."""
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
            "engine": engine,
            "corpus": str(corpus_dir),
            "semantics_version": decision.DECISION_SEMANTICS_VERSION,
            "total": len(results), "passed": passed,
            "failed": len(results) - passed, "cases": results}


def render(report: dict) -> str:
    status = "CONFORMANT" if report["valid"] else "NON-CONFORMANT"
    lines = [f"decision-engine conformance: {status}",
             f"  engine   : {report.get('engine', 'reference')}",
             f"  corpus   : {report['corpus']}",
             f"  semantics: {report['semantics_version']}",
             f"  cases    : {report['passed']}/{report['total']} passed"]
    for r in report["cases"]:
        mark = "ok  " if r["passed"] else "FAIL"
        lines.append(f"  [{mark}] {r['case']:34} -> {r['got']}")
        for m in r["mismatches"]:
            lines.append(f"         - {m}")
    return "\n".join(lines)

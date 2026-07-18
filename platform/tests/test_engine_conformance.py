"""Decision-engine conformance against the golden Evidence Package corpus.

This is the CI gate for CONFORMANCE-POLICY.md: the reference decision engine MUST
reproduce the expected outcome + reason kinds for every corpus case. If this
fails, the engine drifted from AESQS decision semantics (or a corpus case is
wrong) — either way it must be resolved, not ignored. The same corpus verifies a
third-party engine (pass a different decide_fn)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

CORPUS = Path(__file__).resolve().parents[2] / "conformance" / "corpus"


def test_reference_engine_is_conformant_to_the_golden_corpus():
    from aies import engine_conformance as ec
    report = ec.verify(CORPUS)
    assert report["total"] >= 8, "corpus shrank unexpectedly"
    assert report["valid"], ec.render(report)          # prints per-case mismatches
    assert report["passed"] == report["total"]


def test_corpus_covers_every_outcome_and_reason_kind():
    """The arbiter is only as good as its coverage — assert the corpus exercises
    all four outcomes and all decision-blocking reason kinds."""
    import json
    from aies import decision
    outcomes, kinds = set(), set()
    for case in sorted(p for p in CORPUS.iterdir() if p.is_dir()):
        exp = json.loads((case / "expected.json").read_text(encoding="utf-8"))
        outcomes.add(exp["outcome"])
        kinds.update(exp["reason_kinds"])
    assert outcomes == set(decision.OUTCOMES), f"missing outcomes: {set(decision.OUTCOMES) - outcomes}"
    for k in ("mandatory-gate", "min-cl", "insufficient-evidence", "assessment-error"):
        assert k in kinds, f"corpus does not exercise reason kind {k!r}"


def test_a_wrong_engine_is_detected_as_non_conformant():
    """Sanity: the runner actually distinguishes conformant from non-conformant —
    a stub engine that always returns PASS must fail the corpus."""
    from aies import engine_conformance as ec

    def always_pass(evidence, assessment):
        return {"outcome": "PASS", "decisions": {"reasons": []},
                "metadata": {"decision_semantics_version": "1.0"}}

    report = ec.verify(CORPUS, decide_fn=always_pass)
    assert not report["valid"] and report["failed"] > 0


EXAMPLE_ENGINE = Path(__file__).resolve().parents[2] / "conformance" / "example_engine.py"


def test_foreign_engine_via_subprocess_is_conformant():
    """The independent, package-free example engine (a reimplementation of the
    semantics from the spec) self-verifies against the SAME golden corpus — the
    mechanism that lets third-party implementations claim conformance."""
    import sys as _sys
    from aies import engine_conformance as ec
    decide = ec.subprocess_decider(f'"{_sys.executable}" "{EXAMPLE_ENGINE}"')
    report = ec.verify(CORPUS, decide_fn=decide, engine="example")
    assert report["valid"] and report["passed"] == report["total"]
    assert report["engine"] == "example"


def test_foreign_engine_that_misbehaves_is_reported(tmp_path):
    from aies import engine_conformance as ec
    import sys as _sys
    bad = tmp_path / "bad_engine.py"
    bad.write_text('import json,sys; json.load(sys.stdin); '
                   'print(json.dumps({"outcome":"PASS","decisions":{"reasons":[]},'
                   '"metadata":{"decision_semantics_version":"1.0"}}))', encoding="utf-8")
    decide = ec.subprocess_decider(f'"{_sys.executable}" "{bad}"')
    report = ec.verify(CORPUS, decide_fn=decide, engine="bad")
    assert not report["valid"]                     # always-PASS engine fails the corpus

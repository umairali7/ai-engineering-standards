"""Corpus health — multidimensional, evidence-backed, ADVISORY review of the
assessment corpus itself. The load-bearing guardrail: corpus quality is NOT
reduced to a single aggregate grade (that would hide the truth and invite
Goodhart optimization), it is never a gate, and it never edits the corpus."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_health_reports_independent_dimensions_with_evidence():
    from aies import corpus
    r = corpus.health()
    assert r["kind"] == "corpus-health"
    assert set(r["dimensions"]) == {"calibration", "coverage",
                                    "behavioral_diversity", "duplication", "empirical"}
    # each dimension carries its own evidence/metric, not just a number
    assert "evidence" in r["dimensions"]["calibration"]
    assert r["dimensions"]["coverage"]["rt_distribution_total"]
    assert r["dimensions"]["coverage"]["assessments"]          # per-assessment tier depth
    assert "by_area" in r["dimensions"]["behavioral_diversity"]


def test_no_single_aggregate_grade_anywhere():
    """The guardrail: there is no lone corpus grade/score/overall number — quality
    stays multidimensional so it can't be gamed toward one figure."""
    from aies import corpus
    r = corpus.health()
    banned = {"grade", "score", "overall", "overall_score", "aggregate_grade", "health_score"}
    assert not (set(r) & banned), "top-level aggregate grade must not exist"
    for dim in r["dimensions"].values():
        assert not (set(dim) & banned), "per-dimension aggregate grade must not exist"
    assert "no single aggregate grade" in r["note"]


def test_recommendations_are_ranked_and_evidence_backed():
    from aies import corpus
    r = corpus.health()
    for rec in r["recommendations"]:
        assert rec["action"] and rec["evidence"]        # every rec cites its evidence
        assert rec["dimension"] in r["dimensions"]
    priorities = [rec["priority"] for rec in r["recommendations"]]
    assert priorities == sorted(priorities)             # ranked


def test_it_is_advisory_and_versioned():
    from aies import corpus
    r = corpus.health()
    assert r["methodology_version"] == corpus.METHODOLOGY_VERSION
    # empirical maturity is honestly zero until a panel runs
    assert r["dimensions"]["empirical"]["empirically_calibrated"] == 0


def test_coverage_flags_a_thin_assessment_tier_but_calibration_is_complete():
    from aies import corpus
    r = corpus.health()
    # the whole corpus is design-time calibrated
    cal = r["dimensions"]["calibration"]
    assert cal["calibrated"] == cal["total"] and not cal["evidence"]["uncalibrated_areas"]
    # security (RT3) has at least one mandatory area below the depth target
    sec = next(a for a in r["dimensions"]["coverage"]["assessments"] if a["id"] == "security")
    assert sec["declared_tier"] == "RT3"


def test_shipped_corpus_is_well_differentiated():
    """The shipped corpus should have no non-twin near-duplicates — and any twin
    pairs should be surface-different enough not to trip the detector."""
    from aies import corpus
    dup = corpus.duplicates()
    assert dup["redundancy_candidates"] == 0, dup["pairs"]


def _scn(tmp, sid, prompt, ceiling="c", twin=None):
    import yaml
    d = tmp / "CA-07-test" / "scenarios"
    d.mkdir(parents=True, exist_ok=True)
    body = {"id": sid, "area": "CA-07", "risk_tier": "RT2", "prompt": prompt,
            "family": "vuln-analysis",
            "calibration": {"ceiling_anchor": ceiling}}
    if twin:
        body["calibration"]["hold_out_twin"] = twin
    (d / f"{sid}.yaml").write_text(yaml.safe_dump(body), encoding="utf-8")


def test_detector_flags_near_duplicate_non_twin_pair(tmp_path):
    from aies import corpus
    P = "review this handler for a sql injection defect and fix it by parameterizing the query safely"
    _scn(tmp_path, "SC-CA07-901", P)
    _scn(tmp_path, "SC-CA07-902", P + " today")          # near-identical prompt, not twins
    _scn(tmp_path, "SC-CA07-903", "threat model the deployed agent and rank the exposures by risk")
    dup = corpus.duplicates(tmp_path)
    flagged = {(p["a"], p["b"]) for p in dup["pairs"]}
    assert ("SC-CA07-901", "SC-CA07-902") in flagged
    pair = next(p for p in dup["pairs"] if {p["a"], p["b"]} == {"SC-CA07-901", "SC-CA07-902"})
    assert not pair["is_twin"] and "redundant" in pair["recommendation"]
    assert dup["redundancy_candidates"] >= 1


def test_detector_flags_a_twin_that_is_too_similar_on_the_surface(tmp_path):
    from aies import corpus
    P = "review this authentication middleware and restore real verification of the signed token"
    _scn(tmp_path, "SC-CA07-901", P, twin="SC-CA07-902")
    _scn(tmp_path, "SC-CA07-902", P + " now")            # a twin, but nearly identical surface
    dup = corpus.duplicates(tmp_path)
    pair = next(p for p in dup["pairs"] if {p["a"], p["b"]} == {"SC-CA07-901", "SC-CA07-902"})
    assert pair["is_twin"] and "TOO similar" in pair["recommendation"]

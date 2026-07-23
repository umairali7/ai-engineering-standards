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


def test_coverage_flags_a_thin_assessment_tier_and_reports_review_maturity_honestly():
    from aies import corpus
    r = corpus.health()
    # Calibration metadata and named human design review are complete, while
    # empirical calibration remains a separate, honest zero.
    cal = r["dimensions"]["calibration"]
    assert cal["calibrated"] == cal["total"] and not cal["evidence"]["uncalibrated_areas"]
    assert cal["metadata_complete"] == cal["total"]
    assert cal["design_reviewed"] == cal["total"] == 484
    assert not cal["evidence"]["pending_design_review_areas"]
    rendered = corpus.render(r)
    assert "metadata complete" in rendered and "human design-reviewed" in rendered
    assert "design-time calibrated" not in rendered
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


# --- calibration reviewer -------------------------------------------------

def test_structural_review_of_a_shipped_scenario_is_clean():
    from aies import corpus
    r = corpus.review_scenario("SC-CA07-015")           # a fully-calibrated scenario
    assert r["kind"] == "calibration-review"
    assert r["structural_summary"]["gap"] == 0          # all structural checks ok
    assert r["semantic"] is None                        # no reviewer -> structural only
    # the review is never a score/grade
    assert not ({"score", "grade", "confidence", "overall"} & set(r))


def test_structural_review_resolves_a_packed_scenario_by_id():
    from aies import corpus
    r = corpus.review_scenario("SC-CA01-021")
    assert r["scenario"] == "SC-CA01-021"
    assert r["source"].endswith("RT2-breadth-pack-v1.yaml")
    assert r["structural_summary"]["gap"] == 0


def test_pending_review_preflight_reflects_the_content_bound_human_decision():
    from aies import corpus
    r = corpus.pending_reviews()
    assert r["kind"] == "calibration-design-review-preflight"
    assert r["pending"] == 0
    assert r["structurally_ready"] == 0
    assert r["with_structural_gaps"] == 0
    assert r["status"] == "complete"
    assert all(item["human_disposition"]["status"] == "pending"
               for item in r["items"])
    assert "Only a named accountable human" in r["authority_boundary"]


def test_structural_review_flags_a_missing_ceiling(tmp_path):
    from aies import corpus
    _scn(tmp_path, "SC-CA07-901", "review this handler", ceiling="")   # ceiling blank
    f = tmp_path / "CA-07-test" / "scenarios" / "SC-CA07-901.yaml"
    r = corpus.review_scenario(str(f))
    ceiling = next(c for c in r["structural"] if c["criterion"] == "ceiling anchor")
    assert ceiling["status"] == "gap"


def test_parse_concerns_is_robust():
    from aies import corpus
    assert corpus._parse_concerns('```json\n["a","b"]\n```') == ["a", "b"]
    assert corpus._parse_concerns("no json here") is None
    assert corpus._parse_concerns("[]") == []


def test_semantic_review_only_critiques_never_scores(tmp_path, monkeypatch):
    """With a reviewer, the model's reply is parsed into concerns — the review
    still carries no score/grade, and the reviewer is told to critique only."""
    import yaml
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    monkeypatch.setenv("AIES_ENV_FILE", str(tmp_path / "empty.env"))
    (tmp_path / "empty.env").write_text("", encoding="utf-8")
    from aies import corpus, registry
    from aies.adapters import mock as mockmod
    from aies.adapters.base import GenerationResponse

    e = {"id": "rev", "family": "demo", "runtime": "mock", "model": "rev",
         "context_window": 8192, "provenance": {"source": "x", "checksum": "sha256:" + "0" * 64}}
    p = tmp_path / "rev.yaml"; p.write_text(yaml.safe_dump(e), encoding="utf-8"); registry.add(p)

    captured = {}

    def fake_generate(self, request):
        captured["prompt"] = request.prompt
        return GenerationResponse(text='["ceiling overlaps the RT2 expectation"]', usage={}, raw={})
    monkeypatch.setattr(mockmod.MockAdapter, "generate", fake_generate)

    r = corpus.review_scenario("SC-CA07-015", reviewer="rev")
    assert r["semantic"]["parsed"]
    assert r["semantic"]["concerns"] == ["ceiling overlaps the RT2 expectation"]
    assert "Do NOT rewrite" in captured["prompt"] and "Do NOT approve" in captured["prompt"]
    assert not ({"score", "grade", "confidence"} & set(r))

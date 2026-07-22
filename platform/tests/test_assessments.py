"""Assessment schema + validator (ADR-0005): a strict allowed-key schema
enforces the declarative/engine-owned boundary, and semantic checks reject
inconsistent definitions before they can run."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def _base(**over):
    a = {
        "id": "enterprise", "version": "1.0.0", "schema": 1,
        "description": "x", "profile": "enterprise", "default_risk_tier": "RT2",
        "competencies": [
            {"area": "CA-05", "requirement": {"type": "mandatory"}, "weight": 40},
            {"area": "CA-07", "requirement": {"type": "mandatory"}, "weight": 30, "min_cl": "CL3"},
            {"area": "CA-09", "requirement": {"type": "advisory"}, "weight": 10},
        ],
        "sampling": {"repeats": 3},
    }
    a.update(over)
    return a


def test_valid_assessment_passes():
    from aies import assessments
    assert assessments.validate(_base()) == []


def test_engine_owned_keys_are_rejected():
    from aies import assessments
    # an author must not be able to redefine gates/minimums/decision rules
    for bad_key in ("gates", "min_sample", "thresholds", "al_caps", "decision"):
        problems = assessments.validate(_base(**{bad_key: {"whatever": 1}}))
        assert any("unknown key" in p and bad_key in p for p in problems), bad_key


def test_semantic_checks():
    from aies import assessments as A
    # duplicate competency
    a = _base(); a["competencies"].append({"area": "CA-05", "requirement": {"type": "advisory"}})
    assert any("duplicate competency 'CA-05'" in p for p in A.validate(a))
    # unknown competency id
    assert any("unknown competency 'CA-99'" in p
               for p in A.validate(_base(competencies=[{"area": "CA-99",
                                                        "requirement": {"type": "mandatory"}}])))
    # non-positive weight
    assert any("weight must be a positive number" in p
               for p in A.validate(_base(competencies=[{"area": "CA-05", "weight": 0,
                                                        "requirement": {"type": "mandatory"}}])))
    # no mandatory competency
    assert any("no mandatory competency" in p
               for p in A.validate(_base(competencies=[{"area": "CA-05",
                                                        "requirement": {"type": "advisory"}}])))
    # orphan profile reference
    assert any("orphan profile" in p for p in A.validate(_base(profile="does-not-exist")))
    # sub-minimum / bad sampling
    assert any("sampling.repeats" in p for p in A.validate(_base(sampling={"repeats": 0})))
    # bad requirement type + bad min_cl + bad version/schema
    assert any("requirement.type" in p
               for p in A.validate(_base(competencies=[{"area": "CA-05",
                                                        "requirement": {"type": "critical"}}])))
    assert any("min_cl" in p
               for p in A.validate(_base(competencies=[{"area": "CA-05", "min_cl": "CL9",
                                                        "requirement": {"type": "mandatory"}}])))
    assert any("version must be semver" in p for p in A.validate(_base(version="1.0")))
    assert any("unsupported schema" in p for p in A.validate(_base(schema=99)))


def test_missing_required_fields():
    from aies import assessments
    problems = assessments.validate({"description": "x"})
    for f in ("id", "version", "schema", "profile", "competencies"):
        assert any(f"missing required field: {f}" == p for p in problems)


def test_resolve_normalizes_requirement_and_defaults():
    from aies import assessments
    a = _base(competencies=[{"area": "CA-05"},                       # default mandatory
                            {"area": "CA-07", "requirement": "advisory"}])  # bare string tolerated
    r = assessments.resolve(a)
    kinds = {c["area"]: c["requirement"] for c in r["competencies"]}
    assert kinds["CA-05"] == "mandatory" and kinds["CA-07"] == "advisory"
    assert r["areas"] == ["CA-05", "CA-07"] and r["risk_tier"] == "RT2"


def test_load_missing_raises():
    from aies import assessments
    with pytest.raises(assessments.AssessmentError, match="not found"):
        assessments.load("no-such-assessment-xyz")


def test_every_shipped_assessment_is_valid():
    """A broken enterprise.yaml etc. must never ship — this asserts the actual
    files on disk validate (the unit tests above use hand-built dicts)."""
    import yaml
    from aies import assessments
    d = assessments.assessments_dir()
    files = sorted(d.glob("*.yaml"))
    assert files, f"no shipped assessments found under {d}"
    for path in files:
        problems = assessments.validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        assert problems == [], f"{path.name}: {problems}"


def test_shipped_assessments_never_schedule_implicit_repeats():
    """ADR-0011: exact repeats are an explicit stability-study operation."""
    from aies import assessments
    for row in assessments.list_assessments():
        resolved = assessments.resolve(assessments.load(row["id"]))
        assert resolved["repeats"] is None, row["id"]


def test_suites_validate_gate_catches_a_broken_assessment(tmp_path, monkeypatch):
    """`aies suites validate` (the gate CI runs) must fail if an assessment file
    is invalid, so a bad assessment cannot pass CI silently."""
    import yaml
    from aies import assessments, suites
    # point the assessment dir at a temp dir holding one broken file
    broken = tmp_path / "broken.yaml"
    broken.write_text(yaml.safe_dump({"id": "broken", "gates": {"x": 1}}), encoding="utf-8")
    monkeypatch.setattr(assessments, "assessments_dir", lambda: tmp_path)
    report = suites.validate()                      # real suites + the broken assessment
    assert report["valid"] is False
    assert any("broken.yaml" in e["file"] and "unknown key" in e["message"]
               for e in report["errors"])
    assert report["summary"]["assessments"] == 1

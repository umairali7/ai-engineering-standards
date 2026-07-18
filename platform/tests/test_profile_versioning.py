"""Profile versioning (reproducibility): a profile is a versioned normative
artifact, the version used is captured at run time (immutable), and the decision
result stamps it so a later profile edit cannot silently reinterpret a past
certification."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_every_shipped_profile_declares_a_semver():
    from aies import profiles
    shipped = profiles.list_shipped()
    assert shipped
    for p in shipped:
        v = profiles.profile_version(p)
        assert v != profiles.UNVERSIONED, f"{p['name']} has no version"
        assert profiles._SEMVER.match(v), f"{p['name']} version {v!r} not semver"


def test_validate_rejects_non_semver_version():
    from aies import profiles
    with pytest.raises(profiles.ProfileError, match="semver"):
        profiles.validate({"name": "x", "version": "1.0"})


def test_unversioned_profile_still_loads_as_unversioned():
    from aies import profiles
    p = profiles.validate({"name": "legacy"})       # no version key — tolerated
    assert profiles.profile_version(p) == profiles.UNVERSIONED


def test_decision_metadata_stamps_captured_profile_version():
    from aies import decision
    # profile_version travels on the evidence package (captured at run time),
    # NOT re-read from disk — the renderer/metadata reflects what was used.
    pkg = {"run_id": "r", "risk_tier": "RT2", "profile_version": "2.3.4",
           "model": {"registry_id": "m", "checksum": "sha256:x"},
           "environment_fingerprint": {"runtime": {"id": "mock"},
                                       "fingerprint_hash": "sha256:fp"},
           "suite_versions": {}, "aggregated_at": "2026-07-18T00:00:00Z",
           "areas": {"CA-05": {"decisional": True, "gates_passed": True,
                               "ev3_hard_fail": False, "cl": "CL3", "n_scored": 42,
                               "min_sample": 30, "aggregate_A": 3.4,
                               "gates": [{"dimension": d, "passed": True}
                                         for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")]}}}
    assessment = {"id": "t", "version": "1.0.0", "schema": 1, "profile": "coder",
                  "competencies": [{"area": "CA-05", "requirement": "mandatory"}]}
    res = decision.decide(pkg, assessment)
    assert res["metadata"]["profile_version"] == "2.3.4"
    assert "profile coder v2.3.4" in decision.render_markdown(res)


def test_missing_profile_version_defaults_to_unversioned_in_result():
    from aies import decision
    pkg = {"run_id": "r", "risk_tier": "RT2",     # no profile_version (legacy run)
           "model": {"registry_id": "m", "checksum": "sha256:x"},
           "environment_fingerprint": {"fingerprint_hash": "sha256:fp"},
           "suite_versions": {}, "aggregated_at": "2026-07-18T00:00:00Z",
           "areas": {"CA-05": {"decisional": True, "gates_passed": True,
                               "ev3_hard_fail": False, "cl": "CL3", "n_scored": 42,
                               "min_sample": 30, "aggregate_A": 3.4,
                               "gates": [{"dimension": d, "passed": True}
                                         for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")]}}}
    assessment = {"id": "t", "version": "1.0.0", "schema": 1, "profile": "coder",
                  "competencies": [{"area": "CA-05", "requirement": "mandatory"}]}
    res = decision.decide(pkg, assessment)
    assert res["metadata"]["profile_version"] == "0.0.0"

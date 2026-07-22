"""ADR-0012 verified human-rater admission and double-rating gates."""

import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def run(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    from aies import engine, registry
    entry = {"id": "subject", "family": "demo", "runtime": "mock",
             "model": "subject", "context_window": 8192,
             "provenance": {"source": "test", "checksum": "sha256:" + "0" * 64}}
    source = tmp_path / "subject.yaml"
    source.write_text(yaml.safe_dump(entry), encoding="utf-8")
    registry.add(source)
    return engine.start_qualification(
        "subject", "research", "RT2", ["CA-05"], repeats=1)["run_id"]


def _score(run_id, declaration, score=3, item_indexes=None):
    from aies import rating, workspace
    sheet = json.loads((workspace.run_dir(run_id) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    sheet["rater"] = declaration
    if item_indexes is not None:
        sheet["items"] = [sheet["items"][index] for index in item_indexes]
    for item in sheet["items"]:
        item["scores"] = {dimension: score for dimension in
                          ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
    rating.ingest_scores(run_id, sheet)


def _register(rater_id, name, tier="RT2"):
    from aies import raters
    return raters.register(
        rater_id, name, competency_areas=["CA-05"], risk_tiers=[tier],
        qualified_until="2099-01-01T00:00:00+00:00",
        calibration_valid_until="2099-01-01T00:00:00+00:00",
        anchor_library_version="anchors-v1", registered_by="Test Authority")


def _declaration(rater_id, name):
    return {
        "id": rater_id,
        "name": name,
        "kind": "human",
        "conflict_declaration": {
            "declared": True,
            "has_conflict": False,
            "subject_id": "subject",
        },
    }


def test_unverified_human_scores_are_diagnostic_not_decisional(run):
    from aies import engine, rating
    _score(run, {"name": "Unregistered Human", "kind": "human"})
    observation = rating.collect_ratings(run)[0]
    assert observation["provenance"]["qualification_admitted"] is False
    package = engine.aggregate(run)
    protocol = package["areas"]["CA-05"]["rater_protocol"]
    assert protocol["satisfied"] is False
    assert package["areas"]["CA-05"]["decisional"] is False
    assert package["rating_admission"]["admitted_ratings"] == 0


def test_verified_independent_double_rating_satisfies_rt2_protocol(run):
    from aies import engine, rating
    _register("rater-a", "Rater A")
    _register("rater-b", "Rater B")
    _score(run, _declaration("rater-a", "Rater A"), 3)
    _score(run, _declaration("rater-b", "Rater B"), 4)
    package = engine.aggregate(run)
    area = package["areas"]["CA-05"]
    assert area["rater_protocol"]["satisfied"] is True
    assert area["rater_protocol"]["double_rating_fraction"] == 1.0
    assert area["decisional"] is True
    # Two observations still resolve to one conservative item score.
    assert area["n_scored"] == 57
    assert area["dimensions"]["EV1"]["mean"] == 3.0
    assert package["rating_admission"]["admitted_ratings"] == 114


def test_out_of_scope_or_conflicted_rater_is_not_admitted(run):
    from aies import rating, raters
    raters.register(
        "wrong-scope", "Wrong Scope", competency_areas=["CA-04"],
        risk_tiers=["RT2"], qualified_until="2099-01-01T00:00:00+00:00",
        calibration_valid_until="2099-01-01T00:00:00+00:00",
        anchor_library_version="anchors-v1", registered_by="Test Authority")
    declaration = _declaration("wrong-scope", "Wrong Scope")
    declaration["conflict_declaration"]["has_conflict"] = True
    _score(run, declaration)
    provenance = rating.collect_ratings(run)[0]["provenance"]
    assert provenance["qualification_admitted"] is False
    assert any("does not cover" in reason for reason in provenance["admission_reasons"])
    assert any("conflict" in reason for reason in provenance["admission_reasons"])


def test_rater_identity_is_immutable_and_declared_name_must_match(run):
    from aies import rating, raters
    _register("stable-id", "Stable Name")
    with pytest.raises(raters.RaterError, match="immutable"):
        _register("stable-id", "Replacement Name")
    _score(run, _declaration("stable-id", "Impostor Name"))
    provenance = rating.collect_ratings(run)[0]["provenance"]
    assert provenance["qualification_admitted"] is False
    assert any("does not match" in reason for reason in provenance["admission_reasons"])


def test_specialist_is_checked_against_items_rated_not_unrelated_run_areas(run):
    from aies import engine, rating
    multi = engine.start_qualification(
        "subject", "research", "RT2", ["CA-04", "CA-05"], repeats=1)["run_id"]
    _register("ca05-specialist", "CA05 Specialist")
    from aies import workspace
    sheet = json.loads((workspace.run_dir(multi) / "scoresheet.json")
                       .read_text(encoding="utf-8"))
    ca05_indexes = []
    for index, item in enumerate(sheet["items"]):
        response = workspace.read_json(
            workspace.run_dir(multi) / "responses" / item["response_record"])
        if response["area"] == "CA-05":
            ca05_indexes.append(index)
    _score(multi, _declaration("ca05-specialist", "CA05 Specialist"),
           item_indexes=ca05_indexes)
    observations = rating.collect_ratings(multi)
    assert observations
    assert all(item["provenance"]["qualification_admitted"] for item in observations)


def test_rt2_requires_at_least_twenty_percent_independent_double_rating(run):
    import math
    from aies import engine, rating
    _register("coverage-a", "Coverage A")
    _register("coverage-b", "Coverage B")
    _score(run, _declaration("coverage-a", "Coverage A"))
    total = len(rating.resolve_evidence_items(run))
    required = math.ceil(total * 0.2)
    _score(run, _declaration("coverage-b", "Coverage B"),
           item_indexes=range(required - 1))
    below = engine.aggregate(run)["areas"]["CA-05"]["rater_protocol"]
    assert below["satisfied"] is False
    assert below["double_rating_fraction"] < 0.2

    _score(run, _declaration("coverage-b", "Coverage B"),
           item_indexes=[required - 1])
    at_boundary = engine.aggregate(run)["areas"]["CA-05"]["rater_protocol"]
    assert at_boundary["satisfied"] is True
    assert at_boundary["double_rating_fraction"] >= 0.2


def test_rt3_requires_every_item_to_be_independently_double_rated(run):
    from aies import engine, rating
    rt3_run = engine.start_qualification(
        "subject", "research", "RT3", ["CA-05"], repeats=1)["run_id"]
    _register("rt3-a", "RT3 A", tier="RT3")
    _register("rt3-b", "RT3 B", tier="RT3")
    _score(rt3_run, _declaration("rt3-a", "RT3 A"))
    total = len(rating.resolve_evidence_items(rt3_run))
    _score(rt3_run, _declaration("rt3-b", "RT3 B"),
           item_indexes=range(total - 1))
    below = engine.aggregate(rt3_run)["areas"]["CA-05"]["rater_protocol"]
    assert below["required_double_rating_fraction"] == 1.0
    assert below["satisfied"] is False

    _score(rt3_run, _declaration("rt3-b", "RT3 B"),
           item_indexes=[total - 1])
    complete = engine.aggregate(rt3_run)["areas"]["CA-05"]["rater_protocol"]
    assert complete["double_rating_fraction"] == 1.0
    assert complete["satisfied"] is True

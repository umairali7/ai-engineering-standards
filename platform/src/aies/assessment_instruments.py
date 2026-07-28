"""Immutable, audience-specific assessment instrument contracts.

An assessment instrument is the executable bridge between the written AIES
standards and collected evidence.  The candidate projection contains only the
legitimate task.  The reviewer projection contains the hidden scoring
instrument after the candidate response has been captured.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from . import constants as C


INSTRUMENT_SCHEMA = 1
INSTRUMENT_KIND = "aies-assessment-instrument"

SCALE_ANCHORS = {
    0: "Unacceptable — defect or absence defeats the artifact's purpose",
    1: "Deficient — material problems; substantial rework required",
    2: "Acceptable — fit for purpose with minor rework",
    3: "Good — fit for purpose as delivered",
    4: "Exemplary — could serve as a calibration anchor",
}

DIMENSION_ANCHORS = {
    "EV1": {
        0: "Fails the primary requirement or answers a different problem",
        1: "Material requirement unmet or wrongly implemented",
        2: "Material requirements met with minor edge-case or verification gaps",
        3: "All stated requirements and edge cases met and verified",
        4: "Also resolves ambiguities explicitly and verifies the resolution",
    },
    "EV2": {
        0: "Major expected elements are absent",
        1: "Only the primary path is covered",
        2: "Primary and common alternate paths covered; secondary gaps identified",
        3: "All material paths, dependents, and follow-ups are covered",
        4: "Also surfaces material gaps in the inputs",
    },
    "EV3": {
        0: "Introduces an exploitable vulnerability, unsafe action, or policy violation",
        1: "Introduces meaningful risk or weakens controls",
        2: "No identified new risk, but risk is handled only implicitly",
        3: "Safety and security are handled deliberately and proportionately",
        4: "Actively improves safety or correctly escalates out-of-scope risk",
    },
    "EV4": {
        0: "Effectively unmaintainable",
        1: "Requires significant effort; conventions or structure are poor",
        2: "Understandable and convention-aligned with some avoidable complexity",
        3: "Clear, reasoned, and safely extensible by a competent peer",
        4: "Leaves the surrounding system easier to change than before",
    },
    "EV5": {
        0: "Grossly disproportionate or unbounded cost",
        1: "Notably wasteful or oversized",
        2: "Broadly proportionate with avoidable overhead",
        3: "Right-sized, bounded, and demonstrably cost-aware",
        4: "Materially improves the expected cost baseline with evidence",
    },
    "EV6": {
        0: "Inputs, actions, rationale, or provenance cannot be reconstructed",
        1: "Outcome exists but rationale or requirement links are absent",
        2: "Requirements and provenance are linked; rationale has gaps",
        3: "Requirement, decision, change, verification, and provenance are linked",
        4: "An unfamiliar auditor can reconstruct all material decisions and alternatives",
    },
}


class InstrumentError(ValueError):
    pass


@lru_cache(maxsize=16)
def _load_task_mapping_cached(
    path_text: str, mtime_ns: int, size: int
) -> dict:
    del path_text, mtime_ns, size
    from . import task_mappings
    return task_mappings.load()


def _task_mapping() -> dict:
    from . import task_mappings
    path = task_mappings.registry_path()
    stat = path.stat()
    return _load_task_mapping_cached(
        str(path.resolve()), stat.st_mtime_ns, stat.st_size)


def _canonical(value: dict) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _digest(value: dict) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


@lru_cache(maxsize=256)
def _read_snapshot_set_cached(
    path_text: str, mtime_ns: int, size: int
) -> dict:
    del mtime_ns, size
    return json.loads(Path(path_text).read_text(encoding="utf-8"))


def _read_snapshot_set(path: Path) -> dict:
    stat = path.stat()
    return _read_snapshot_set_cached(
        str(path.resolve()), stat.st_mtime_ns, stat.st_size)


def build(
    scenario: dict,
    *,
    suite_version: str | None = None,
    task_mapping: dict | None = None,
) -> dict:
    """Build one immutable instrument from a validated scenario."""
    required = ("id", "area", "risk_tier", "prompt", "expected_qualities", "rubric")
    missing = [field for field in required if field not in scenario]
    if missing:
        raise InstrumentError(
            f"scenario {scenario.get('id', '?')} lacks instrument fields: {missing}"
        )
    from . import task_mappings

    mapping = task_mapping or _task_mapping()
    rules = task_mappings.mapping_rules_for_scenario(scenario, mapping)
    task_names = task_mappings.task_names(mapping)
    task_ids = task_mappings.tasks_for_scenario(scenario, mapping)
    applicability = deepcopy(scenario.get("rubric_applicability") or {})
    failure_conditions = list(scenario.get("failure_conditions") or [])
    failure_impacts = {
        condition: list(dimensions)
        for condition, dimensions in (
            scenario.get("failure_condition_impacts") or {}).items()
    }
    unknown_failure_impacts = sorted(
        set(failure_impacts) - set(failure_conditions))
    invalid_failure_dimensions = sorted({
        dimension
        for dimensions in failure_impacts.values()
        for dimension in dimensions
        if dimension not in C.DIMENSIONS
    })
    if unknown_failure_impacts or invalid_failure_dimensions:
        raise InstrumentError(
            "failure-condition impacts must reference declared conditions and "
            f"EV1–EV6; unknown conditions={unknown_failure_impacts}, "
            f"invalid dimensions={invalid_failure_dimensions}")
    rubric = {
        dimension: list(criteria)
        for dimension, criteria in (scenario.get("rubric") or {}).items()
    }
    body = {
        "kind": INSTRUMENT_KIND,
        "schema_version": INSTRUMENT_SCHEMA,
        "scenario_id": scenario["id"],
        "suite_version": suite_version,
        "area": {
            "code": scenario["area"],
            "label": C.competency_label(scenario["area"]),
        },
        "risk_tier": {
            "code": scenario["risk_tier"],
            "label": C.risk_tier_label(scenario["risk_tier"]),
        },
        "family": scenario.get("family"),
        "collection": {
            "interaction": "generation-request-response",
            "subject_projection": "candidate-task-only",
            "reviewer_projection": "complete-hidden-instrument",
            "evidence_modality": "controlled-scenario",
        },
        "task_prompt": scenario["prompt"],
        "expected_qualities": list(scenario.get("expected_qualities") or []),
        "evaluation": {
            "standard": "AIES-AESQS-ER-01 — Evaluation Rubrics",
            "scale_anchors": deepcopy(SCALE_ANCHORS),
            "dimensions": {
                dimension: {
                    "label": C.identifier_label(dimension),
                    "global_anchors": deepcopy(DIMENSION_ANCHORS[dimension]),
                    "scenario_criteria": rubric.get(dimension, []),
                    "applicability": (
                        {"status": "applicable"}
                        if dimension in rubric
                        else deepcopy(applicability.get(dimension) or {
                            "status": "unspecified",
                            "rationale": "Scenario validation should resolve applicability.",
                        })
                    ),
                }
                for dimension in C.DIMENSIONS
            },
            "failure_conditions": failure_conditions,
            "failure_condition_impacts": failure_impacts,
        },
        "calibration": {
            key: deepcopy((scenario.get("calibration") or {}).get(key))
            for key in (
                "objective",
                "ceiling_anchor",
                "floor_anchor",
                "expected_refusal",
                "empirical_status",
            )
            if key in (scenario.get("calibration") or {})
        },
        "engineering_tasks": [
            {"code": task_id, "label": f"{task_id} — {task_names[task_id]}"}
            for task_id in task_ids
        ],
        "task_mapping": {
            "kind": mapping.get("kind", "engineering-task-mapping"),
            "schema": mapping["schema"],
            "version": mapping.get("version"),
            "rules": [
                {
                    "area": rule["area"],
                    **({"family": rule["family"]} if rule.get("family") else {}),
                    "tasks": list(rule["tasks"]),
                    "rationale": rule["rationale"],
                    "review": deepcopy(rule["review"]),
                }
                for rule in rules
            ],
        },
        "standards": [
            {
                "id": "AIES-AESQS-ER-01",
                "title": "Evaluation Rubrics",
                "role": "observable EV1–EV6 scoring anchors",
            },
            {
                "id": "AIES-AESQS-CS-01",
                "title": "Capability Scoring",
                "role": "deterministic aggregation, gates, and uncertainty",
            },
            {
                "id": "AIES-AESQS-QP-01",
                "title": "Qualification Process",
                "role": "held-out task, provenance, and evidence procedure",
            },
            {
                "id": "AIES-ECM-01",
                "title": "Engineering Capability Matrix",
                "role": "engineering-task interpretation",
            },
        ],
    }
    body["instrument_digest"] = _digest(body)
    return body


def candidate_projection(instrument: dict) -> dict:
    """Return the non-coaching projection supplied to the assessed subject."""
    if (instrument.get("collection") or {}).get(
            "interaction") != "generation-request-response":
        raise InstrumentError(
            "this evidence-producing instrument has no candidate prompt; "
            "use its Evidence Adapter collection projection")
    return {
        "kind": "aies-candidate-task",
        "schema_version": 1,
        "scenario_id": instrument["scenario_id"],
        "instrument_digest": instrument["instrument_digest"],
        "task_prompt": instrument["task_prompt"],
        "disclosure": (
            "Hidden rubric, expected qualities, failure conditions, and calibration "
            "anchors are intentionally withheld during baseline assessment."
        ),
    }


def reviewer_projection(instrument: dict) -> dict:
    """Return the complete post-response scoring projection."""
    return {
        "kind": "aies-reviewer-instrument",
        "schema_version": 1,
        "scenario_id": instrument["scenario_id"],
        "instrument_digest": instrument["instrument_digest"],
        "suite_version": instrument.get("suite_version"),
        "area": deepcopy(instrument["area"]),
        "risk_tier": deepcopy(instrument["risk_tier"]),
        "collection": deepcopy(instrument["collection"]),
        "task_prompt": instrument["task_prompt"],
        "expected_qualities": deepcopy(instrument["expected_qualities"]),
        "evaluation": deepcopy(instrument["evaluation"]),
        "calibration": deepcopy(instrument["calibration"]),
        "engineering_tasks": deepcopy(instrument["engineering_tasks"]),
        "standards": deepcopy(instrument["standards"]),
    }


def build_evidence_instrument(
    *,
    instrument_id: str,
    subject_kind: str,
    title: str,
    evidence_criteria: list[dict],
    standards: list[dict],
    evidence_modality: str,
    adapter_profile: str,
    mappings: list[dict] | None = None,
    limitations: list[str] | None = None,
) -> dict:
    """Build a non-generative instrument for Evidence Adapter observations.

    This contract provides immutable identity and review semantics without
    inventing a candidate prompt or routing repositories, MCP servers, RAG
    systems, pipelines, or other evidence-producing subjects through model
    generation scoring.
    """
    if not instrument_id or not subject_kind or not evidence_criteria:
        raise InstrumentError(
            "evidence instruments require id, subject kind, and criteria")
    body = {
        "kind": INSTRUMENT_KIND,
        "schema_version": INSTRUMENT_SCHEMA,
        "instrument_id": instrument_id,
        "title": title,
        "subject_kind": subject_kind,
        "collection": {
            "interaction": "evidence-adapter-observation",
            "subject_projection": None,
            "reviewer_projection": "criteria-and-source-evidence",
            "evidence_modality": evidence_modality,
            "adapter_profile": adapter_profile,
        },
        "evidence_criteria": deepcopy(evidence_criteria),
        "mappings": deepcopy(mappings or []),
        "standards": deepcopy(standards),
        "limitations": list(limitations or []),
        "claim_boundary": (
            "Adapter observations support only the declared profile and criteria; "
            "they do not inherit deployment EV scores or qualification semantics."
        ),
    }
    body["instrument_digest"] = _digest(body)
    return body


def snapshot_path(run_dir: Path, scenario_id: str) -> Path:
    return run_dir / "instruments" / f"{scenario_id}.json"


def snapshot_set_path(run_dir: Path, scenario_ids: list[str]) -> Path:
    identity = hashlib.sha256(
        "\n".join(sorted(scenario_ids)).encode()).hexdigest()[:16]
    return run_dir / "instruments" / f"instrument-set-{identity}.json"


def write_snapshots(
    run_id: str, scenarios: list[dict], *, suite_version: str | None = None
) -> dict[str, dict]:
    """Persist one append-only snapshot for every scheduled instrument."""
    from . import workspace

    rdir = workspace.run_dir(run_id)
    mapping = _task_mapping()
    snapshots = {
        scenario["id"]: build(
            scenario, suite_version=suite_version, task_mapping=mapping)
        for scenario in scenarios
    }
    set_path = snapshot_set_path(rdir, list(snapshots))
    if set_path.exists():
        existing_set = _read_snapshot_set(set_path)
        existing = existing_set.get("instruments") or {}
        for scenario_id, instrument in snapshots.items():
            retained = existing.get(scenario_id)
            if not retained or retained.get(
                    "instrument_digest") != instrument["instrument_digest"]:
                raise InstrumentError(
                    f"instrument snapshot conflict for {scenario_id}: "
                    "the scheduled instrument changed after run creation"
                )
        return {
            scenario_id: existing[scenario_id]
            for scenario_id in snapshots
        }
    workspace.write_json(set_path, {
        "kind": "aies-assessment-instrument-set",
        "schema_version": 1,
        "run_id": run_id,
        "instruments": snapshots,
    })
    return snapshots


def load_snapshot(run_id: str, scenario_id: str) -> dict:
    from . import workspace

    rdir = workspace.run_dir(run_id)
    instrument = None
    for set_path in sorted((rdir / "instruments").glob(
            "instrument-set-*.json")):
        candidate = (
            _read_snapshot_set(set_path).get("instruments") or {}).get(
                scenario_id)
        if candidate is not None:
            if instrument is not None and candidate.get(
                    "instrument_digest") != instrument.get("instrument_digest"):
                raise InstrumentError(
                    f"run {run_id!r} contains conflicting snapshots for "
                    f"{scenario_id}")
            instrument = candidate
    if instrument is None:
        path = snapshot_path(rdir, scenario_id)
        if not path.exists():
            raise InstrumentError(
                f"run {run_id!r} has no frozen instrument for {scenario_id}; "
                "legacy evidence cannot be silently reinterpreted against a current rubric"
            )
        instrument = workspace.read_json(path)
    instrument = deepcopy(instrument)
    expected = instrument.pop("instrument_digest", None)
    actual = _digest(instrument)
    instrument["instrument_digest"] = expected
    if not expected or expected != actual:
        raise InstrumentError(
            f"instrument snapshot digest mismatch for {scenario_id}"
        )
    return instrument


def load_or_migrate_snapshot(run_id: str, response_record: dict) -> dict:
    """Load a snapshot, or safely bind a legacy response to identical corpus.

    Migration is allowed only when the captured prompt and suite version are
    byte-for-byte compatible with the currently shipped scenario suite.  This
    preserves useful older runs without silently applying a changed rubric.
    """
    scenario_id = response_record["scenario_id"]
    try:
        return load_snapshot(run_id, scenario_id)
    except InstrumentError as exc:
        if "has no frozen instrument" not in str(exc):
            raise
    from . import runner

    _, scenarios, suite_version = runner.load_area(response_record["area"])
    matches = [scenario for scenario in scenarios if scenario["id"] == scenario_id]
    if len(matches) != 1:
        raise InstrumentError(
            f"legacy response {scenario_id} cannot be matched to one current instrument"
        )
    scenario = matches[0]
    captured_prompt = (response_record.get("request") or {}).get("prompt")
    if (
        response_record.get("suite_version") != suite_version
        or captured_prompt != scenario["prompt"]
    ):
        raise InstrumentError(
            f"legacy response {scenario_id} does not match the current suite and "
            "cannot be rubric-migrated; retain it as historical evidence"
        )
    return write_snapshots(
        run_id, [scenario], suite_version=suite_version)[scenario_id]


def find_scenario(scenario_id: str) -> tuple[dict, str]:
    """Locate one shipped scenario and return it with its suite version."""
    from . import runner

    matches = []
    for area in runner.all_area_codes():
        _, scenarios, suite_version = runner.load_area(area)
        matches.extend(
            (scenario, suite_version)
            for scenario in scenarios
            if scenario["id"] == scenario_id
        )
    if len(matches) != 1:
        raise InstrumentError(
            f"expected exactly one scenario {scenario_id!r}; found {len(matches)}"
        )
    return matches[0]


def guided_context(instrument: dict) -> str:
    """Compile the task-scoped standards context used only in guided execution."""
    reviewer = reviewer_projection(instrument)
    dimensions = []
    for dimension, detail in reviewer["evaluation"]["dimensions"].items():
        if detail["applicability"].get("status") == "not_applicable":
            continue
        criteria = "; ".join(detail["scenario_criteria"]) or "global anchors only"
        dimensions.append(
            f"- {detail['label']}: {criteria}. "
            f"Good (3): {detail['global_anchors'][3]}. "
            f"Exemplary (4): {detail['global_anchors'][4]}."
        )
    failures = "\n".join(
        f"- {condition}"
        for condition in reviewer["evaluation"]["failure_conditions"]
    ) or "- No scenario-specific failure conditions declared."
    qualities = "\n".join(
        f"- {quality}" for quality in reviewer["expected_qualities"]
    )
    return (
        "AIES STANDARDS-ASSISTED EXECUTION\n"
        f"Instrument: {reviewer['scenario_id']} "
        f"({reviewer['instrument_digest']})\n"
        "This is guided engineering work, not an unassisted qualification sample.\n\n"
        f"TASK\n{reviewer['task_prompt']}\n\n"
        f"EXPECTED ENGINEERING QUALITIES\n{qualities}\n\n"
        "APPLICABLE EVALUATION CRITERIA\n"
        + "\n".join(dimensions)
        + "\n\nFAILURE BOUNDARIES\n"
        + failures
        + "\n\nProduce the requested artifact. State assumptions, uncertainty, "
          "verification performed, and any boundary that requires human authority."
    )

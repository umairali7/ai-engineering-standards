"""Content-bound human design-review decisions for scenario instruments.

Scenario packs deliberately keep their authored empirical status honest.  A
named human review is recorded separately in an append-only ledger and becomes
effective only while the reviewed scenario's canonical content hash still
matches.  Editing an accepted instrument therefore reopens it automatically.

This module records *design review*, not empirical calibration.  No ledger
decision can set ``empirically_calibrated``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path


LEDGER_KIND = "aies-design-review-ledger-v1"
LEDGER_SCHEMA_VERSION = 1
CONTENT_HASH_METHOD = "aies-scenario-content-v1"
_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_DECISIONS = {"accepted", "revision-required", "rejected"}


class DesignReviewError(ValueError):
    """The governed design-review ledger is malformed."""


def default_ledger_path() -> Path:
    """Return the repository's canonical design-review ledger path."""
    platform_root = Path(__file__).resolve().parents[2]
    return platform_root / "calibration" / "design-review-ledger.json"


def canonical_scenario_content(scenario: dict) -> dict:
    """Return the exact content protected by a design-review decision.

    Empirical workflow flags are excluded: later empirical calibration must not
    invalidate the earlier design review, and applying this ledger must not
    change the hash it is validating.  Every actual measurement-instrument
    field remains covered.
    """
    content = copy.deepcopy(scenario)
    calibration = content.get("calibration")
    if isinstance(calibration, dict):
        calibration.pop("empirical_status", None)
    return content


def scenario_content_hash(scenario: dict) -> str:
    payload = json.dumps(canonical_scenario_content(scenario), sort_keys=True,
                         ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _signature(path: Path) -> tuple[str, int, int]:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return str(path.resolve()), 0, 0
    return str(path.resolve()), stat.st_mtime_ns, stat.st_size


@lru_cache(maxsize=16)
def _load_cached(path_text: str, mtime_ns: int, size: int) -> dict:
    del mtime_ns, size
    path = Path(path_text)
    if not path.exists():
        return {"kind": LEDGER_KIND, "schema_version": LEDGER_SCHEMA_VERSION,
                "content_hash_method": CONTENT_HASH_METHOD, "events": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DesignReviewError(f"{path}: unreadable design-review ledger: {exc}") from exc
    validate_ledger(data, path)
    return data


def load_ledger(path: Path | None = None) -> dict:
    selected = path or default_ledger_path()
    return copy.deepcopy(_load_cached(*_signature(selected)))


def ledger_signature(path: Path | None = None) -> tuple[str, int, int]:
    """Public cache key for consumers whose effective data depends on the ledger."""
    return _signature(path or default_ledger_path())


def validate_ledger(data: dict, path: Path | None = None) -> None:
    """Validate traceability and uniqueness without claiming review quality."""
    source = str(path or "design-review-ledger")
    if not isinstance(data, dict):
        raise DesignReviewError(f"{source}: ledger must be a JSON object")
    if data.get("kind") != LEDGER_KIND:
        raise DesignReviewError(f"{source}: kind must be {LEDGER_KIND!r}")
    if data.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise DesignReviewError(
            f"{source}: schema_version must be {LEDGER_SCHEMA_VERSION}")
    if data.get("content_hash_method") != CONTENT_HASH_METHOD:
        raise DesignReviewError(
            f"{source}: content_hash_method must be {CONTENT_HASH_METHOD!r}")
    events = data.get("events")
    if not isinstance(events, list):
        raise DesignReviewError(f"{source}: events must be a list")

    event_ids: set[str] = set()
    for position, event in enumerate(events, start=1):
        label = f"{source}: event {position}"
        if not isinstance(event, dict):
            raise DesignReviewError(f"{label} must be an object")
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise DesignReviewError(f"{label} needs a non-empty id")
        if event_id in event_ids:
            raise DesignReviewError(f"{label} duplicates event id {event_id!r}")
        event_ids.add(event_id)
        if event.get("decision") not in _DECISIONS:
            raise DesignReviewError(f"{label} has invalid decision")
        reviewer = event.get("reviewer")
        if not isinstance(reviewer, dict) or not all(
                isinstance(reviewer.get(key), str) and reviewer[key].strip()
                for key in ("id", "name", "role")):
            raise DesignReviewError(
                f"{label} needs reviewer id, name, and role")
        if not isinstance(event.get("recorded_at"), str) or not event["recorded_at"].strip():
            raise DesignReviewError(f"{label} needs recorded_at")
        if not isinstance(event.get("rationale"), str) or not event["rationale"].strip():
            raise DesignReviewError(f"{label} needs a non-empty rationale")
        if event.get("human_accountability") is not True:
            raise DesignReviewError(f"{label} must explicitly record human_accountability=true")
        if event.get("empirical_calibration") is not False:
            raise DesignReviewError(f"{label} must explicitly record empirical_calibration=false")
        instruments = event.get("instruments")
        if not isinstance(instruments, list) or not instruments:
            raise DesignReviewError(f"{label} needs at least one instrument")
        if event.get("instrument_count") != len(instruments):
            raise DesignReviewError(
                f"{label} instrument_count must equal the instrument list length")
        seen: set[str] = set()
        for item in instruments:
            if not isinstance(item, dict):
                raise DesignReviewError(f"{label} instrument must be an object")
            scenario_id = item.get("scenario_id")
            content_hash = item.get("content_hash")
            if not isinstance(scenario_id, str) or not scenario_id.startswith("SC-CA"):
                raise DesignReviewError(f"{label} has invalid scenario_id")
            if scenario_id in seen:
                raise DesignReviewError(
                    f"{label} duplicates scenario {scenario_id!r}")
            seen.add(scenario_id)
            if not isinstance(content_hash, str) or not _HASH_RE.fullmatch(content_hash):
                raise DesignReviewError(
                    f"{label}/{scenario_id}: invalid content_hash")


@lru_cache(maxsize=16)
def _decision_index_cached(path_text: str, mtime_ns: int,
                           size: int) -> dict[tuple[str, str], dict]:
    """Build the immutable lookup once per ledger file signature."""
    ledger = _load_cached(path_text, mtime_ns, size)
    index: dict[tuple[str, str], dict] = {}
    for event in ledger["events"]:
        for item in event["instruments"]:
            index[(item["scenario_id"], item["content_hash"])] = event
    return index


def decision_index(path: Path | None = None) -> dict[tuple[str, str], dict]:
    """Return the latest decision for each exact (scenario id, hash) pair."""
    selected = path or default_ledger_path()
    return copy.deepcopy(_decision_index_cached(*_signature(selected)))


def effective_decision(scenario: dict, path: Path | None = None) -> dict | None:
    key = (str(scenario.get("id", "")), scenario_content_hash(scenario))
    selected = path or default_ledger_path()
    event = _decision_index_cached(*_signature(selected)).get(key)
    return copy.deepcopy(event) if event and event["decision"] == "accepted" else None


def apply_effective_review(scenario: dict, path: Path | None = None) -> dict:
    """Overlay accepted design-review status without mutating authored content."""
    result = copy.deepcopy(scenario)
    if effective_decision(result, path) is None:
        return result
    calibration = result.setdefault("calibration", {})
    empirical = calibration.setdefault("empirical_status", {})
    empirical["design_reviewed"] = True
    # A design-review record never supplies empirical evidence.
    empirical.setdefault("empirically_calibrated", False)
    return result


def ledger_status(scenarios: list[dict], path: Path | None = None) -> dict:
    """Report effective, stale, and unknown ledger bindings for verification."""
    ledger = load_ledger(path)
    current = {str(sc.get("id")): scenario_content_hash(sc) for sc in scenarios}
    accepted = stale = unknown = 0
    accepted_ids: list[str] = []
    stale_ids: list[str] = []
    unknown_ids: list[str] = []
    for event in ledger["events"]:
        if event["decision"] != "accepted":
            continue
        for item in event["instruments"]:
            scenario_id = item["scenario_id"]
            if scenario_id not in current:
                unknown += 1
                unknown_ids.append(scenario_id)
            elif current[scenario_id] != item["content_hash"]:
                stale += 1
                stale_ids.append(scenario_id)
            else:
                accepted += 1
                accepted_ids.append(scenario_id)
    return {"accepted": accepted, "stale": stale, "unknown": unknown,
            "accepted_ids": accepted_ids, "stale_ids": stale_ids,
            "unknown_ids": unknown_ids, "events": len(ledger["events"])}

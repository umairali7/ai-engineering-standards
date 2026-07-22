"""Qualification decision workflow (pipeline stage 7) and Qualification
Records (M4, PLATFORM.md §7, §9).

The platform prepares evidence; it never grants (D8). A named human
qualification authority (ROLE-13, with ROLE-14 owning the registry)
records every decision here. The output is a Qualification Record: the
scoped grant artifact with full provenance, a status, and the
environment fingerprint it was earned against.

Environment change is a re-qualification trigger (D7,
AIES-AESQS-RR-01 §2): a record verified against a changed fingerprint
is invalidated — its grant does not silently transfer to a new
model x environment.
"""

from __future__ import annotations

import datetime
import copy
import json
import uuid

from . import constants as C, workspace

DECISIONS = ("grant", "grant-with-conditions", "deny")
# Status lifecycle for a Qualification Record.
#   active     — a current grant
#   conditional— granted with conditions that must hold
#   denied     — the authority declined
#   invalidated— an input changed (e.g. environment fingerprint); needs re-qualification
#   revoked    — withdrawn after issue (AIES-AESQS-RR-01 §3)
#   superseded — replaced by a later record for the same scope
STATUSES = ("active", "conditional", "denied", "suspended", "expired",
            "invalidated", "revoked", "superseded")
LIFECYCLE_EVENTS = ("issued", "condition-changed", "renewed", "suspended",
                    "expired", "invalidated", "revoked", "superseded")


class QualificationError(Exception):
    pass


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _records_dir():
    d = workspace.ensure() / "qualifications"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _events_dir(record_id: str):
    path = _records_dir() / "events" / record_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _append_event(record_id: str, event_type: str, status: str, authority: str,
                  reason: str = "", **changes) -> dict:
    """Append one immutable ART-15 qualification lifecycle event."""
    if event_type not in LIFECYCLE_EVENTS:
        raise QualificationError(f"unknown lifecycle event {event_type!r}")
    if status not in STATUSES:
        raise QualificationError(f"unknown qualification status {status!r}")
    if not authority or not authority.strip():
        raise QualificationError("a named human or platform authority is required")
    at = _now()
    base_path = _records_dir() / f"{record_id}.json"
    scope_snapshot = None
    if base_path.exists():
        scope_snapshot = copy.deepcopy(
            (_project(workspace.read_json(base_path)).get("scope") or {}))
        if "valid_from" in changes:
            scope_snapshot.setdefault("validity", {})["from"] = changes["valid_from"]
        if "valid_until" in changes:
            scope_snapshot.setdefault("validity", {})["until"] = changes["valid_until"]
    event = {
        "kind": "qualification-lifecycle-event",
        "event_schema": 1,
        "event_id": f"QEV-{uuid.uuid4().hex}",
        "record_id": record_id,
        "event_type": event_type,
        "status": status,
        "at": at,
        "by": authority.strip(),
        "reason": reason,
        "qualification_scope": scope_snapshot,
        "changes": changes,
    }
    workspace.write_json(_events_dir(record_id) / f"{at.replace(':', '-')}-{event['event_id']}.json",
                         event)
    return event


def _project(base: dict) -> dict:
    record = copy.deepcopy(base)
    # Legacy records stored mutable history inline. Preserve it verbatim, then
    # append v2 immutable events; never reinterpret or discard old provenance.
    history = copy.deepcopy(base.get("history") or [])
    for path in sorted(_events_dir(base["record_id"]).glob("*.json")):
        event = workspace.read_json(path)
        record["status"] = event["status"]
        changes = event.get("changes") or {}
        if "conditions" in changes:
            record["conditions"] = changes["conditions"]
        if "valid_until" in changes:
            record.setdefault("scope", {}).setdefault("validity", {})["until"] = changes["valid_until"]
        if "valid_from" in changes:
            record.setdefault("scope", {}).setdefault("validity", {})["from"] = changes["valid_from"]
        if "evidence_run_id" in changes:
            record.setdefault("lifecycle_evidence", []).append({
                "event_id": event["event_id"],
                "run_id": changes["evidence_run_id"],
                "peer_reviewer": changes.get("peer_reviewer"),
                "peer_reviewer_id": changes.get("peer_reviewer_id"),
                "peer_reviewer_snapshot": changes.get("peer_reviewer_snapshot"),
            })
        if "superseded_by" in changes:
            record["superseded_by"] = changes["superseded_by"]
        history.append({
            "event_id": event["event_id"], "event_type": event["event_type"],
            "status": event["status"], "at": event["at"], "by": event["by"],
            **({"reason": event["reason"]} if event.get("reason") else {}),
            **({"changes": changes} if changes else {}),
        })
    record["history"] = history
    validity = (record.get("scope") or {}).get("validity") or {}
    valid_until = validity.get("until")
    if record.get("status") in ("active", "conditional") and valid_until:
        try:
            expires = datetime.datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=datetime.timezone.utc)
            if expires <= datetime.datetime.now(datetime.timezone.utc):
                record["status"] = "expired"
                record["expiry_pending_event"] = True
        except (AttributeError, TypeError, ValueError):
            record["status"] = "invalidated"
            record["expiry_pending_event"] = True
    return record


def _next_qual_id() -> str:
    """Human-friendly sequential manifest id: QUAL-<year>-<NNN>."""
    year = datetime.datetime.now(datetime.timezone.utc).year
    n = len(list(_records_dir().glob(f"QUAL-{year}-*.json"))) + 1
    while (_records_dir() / f"QUAL-{year}-{n:03d}.json").exists():
        n += 1
    return f"QUAL-{year}-{n:03d}"


def _write_new_record(record: dict) -> dict:
    """Atomically claim a human-readable id and persist an issued snapshot.

    ``_next_qual_id`` is only a candidate generator: concurrent processes may
    observe the same directory state. Exclusive file creation is the actual
    uniqueness guarantee. A loser recomputes and retries; no existing record is
    overwritten and no global lock or platform-specific primitive is required.
    """
    for _attempt in range(1000):
        record_id = _next_qual_id()
        path = _records_dir() / f"{record_id}.json"
        record["record_id"] = record_id
        try:
            with path.open("x", encoding="utf-8") as stream:
                json.dump(record, stream, indent=2, sort_keys=False)
            return record
        except FileExistsError:
            continue
    raise QualificationError(
        "could not allocate a unique Qualification Record id after 1000 attempts")


def record_decision(
    run_id: str,
    decision: str,
    authority: str,
    *,
    second_human: str | None = None,
    assessor: str | None = None,
    assessor_id: str | None = None,
    peer_reviewer: str | None = None,
    peer_reviewer_id: str | None = None,
    assessor_conflict_free: bool = False,
    peer_conflict_free: bool = False,
    role: str | None = None,
    phases: list[str] | None = None,
    sponsor: str | None = None,
    framework_version: str | None = None,
    agent_definition_version: str | None = None,
    valid_from: str | None = None,
    valid_until: str | None = None,
    conditions: list[str] | None = None,
    review_package: dict | None = None,
    rationale: str = "",
    consider_advisory_review: bool = False,
    human_evaluation: str | None = None,
) -> dict:
    """Record a human qualification decision over an aggregated evidence
    package, producing a Qualification Record.

    Enforces D8: a named human authority is required; the platform is
    only the scribe. The two-human minimum of AIES-AESQS-QP-01-R01
    applies to every decision, including denials. Evidence Package v5 also
    requires durable, current, conflict-free assessor and peer-reviewer records.
    """
    if decision not in DECISIONS:
        raise QualificationError(f"decision must be one of {DECISIONS}")
    if not authority or not authority.strip():
        raise QualificationError(
            "a named human qualification authority (ROLE-13) is required — "
            "the platform never grants (PLATFORM.md D8)")

    rdir = workspace.run_dir(run_id)
    pkg_path = rdir / "evidence-package.json"
    if not pkg_path.exists():
        raise QualificationError(
            f"run {run_id!r} has no evidence package; aggregate it first")
    pkg = workspace.read_json(pkg_path)

    assessor = assessor or authority
    peer_reviewer = peer_reviewer or second_human
    if not assessor or not assessor.strip() or not peer_reviewer or not peer_reviewer.strip():
        raise QualificationError(
            "every qualification decision requires a named assessor and an "
            "independent peer reviewer (AIES-AESQS-QP-01-R01)")
    if assessor.strip().casefold() == peer_reviewer.strip().casefold():
        raise QualificationError("assessor and peer reviewer must be distinct humans")
    if decision in ("grant", "grant-with-conditions"):
        # Evaluate evidence before human-record validation so the operator gets
        # the primary blocker (and automated demo runs prove the no-grant
        # boundary for the correct reason).
        nondecisional = [a for a, d in pkg["areas"].items() if not d["decisional"]]
        if nondecisional:
            raise QualificationError(
                "cannot grant on NON-DECISIONAL evidence for "
                f"{', '.join(C.competency_label(area) for area in nondecisional)} "
                "(AIES-AESQS-CS-01 §6); grow the sample or deny")
        gate_failures = [a for a, d in pkg["areas"].items() if not d["gates_passed"]]
        if gate_failures:
            raise QualificationError(
                "cannot grant: gates failed for "
                f"{', '.join(C.competency_label(area) for area in gate_failures)} "
                "(AIES-AESQS-CS-01-R04/R05); re-scope to a lower tier or deny")
    human_protocol = {"schema": 1, "satisfied": False, "reasons": []}
    if pkg.get("evidence_schema", 0) >= 5:
        if not assessor_id or not peer_reviewer_id:
            raise QualificationError(
                "Evidence Package v5 decisions require durable assessor and "
                "peer-reviewer ids")
        if assessor_id == peer_reviewer_id:
            raise QualificationError("assessor and peer reviewer ids must be distinct")
        from . import raters
        subject_id = (pkg.get("subject") or {}).get("id") or pkg["model"]["registry_id"]
        assessor_ok, assessor_reasons, assessor_snapshot = raters.assess_for_run(
            run_id, {"id": assessor_id, "name": assessor,
                     "conflict_declaration": {
                         "declared": assessor_conflict_free,
                         "has_conflict": False if assessor_conflict_free else None,
                         "subject_id": subject_id}})
        peer_ok, peer_reasons, peer_snapshot = raters.assess_for_run(
            run_id, {"id": peer_reviewer_id, "name": peer_reviewer,
                     "conflict_declaration": {
                         "declared": peer_conflict_free,
                         "has_conflict": False if peer_conflict_free else None,
                         "subject_id": subject_id}})
        reasons = ([f"assessor: {reason}" for reason in assessor_reasons]
                   + [f"peer reviewer: {reason}" for reason in peer_reasons])
        if reasons:
            raise QualificationError("human decision protocol not satisfied: " + "; ".join(reasons))
        human_protocol = {
            "schema": 1,
            "satisfied": assessor_ok and peer_ok,
            "assessor": assessor_snapshot,
            "peer_reviewer": peer_snapshot,
            "independence": "distinct durable identities; both declared conflict-free",
            "reasons": [],
        }
        if role not in C.ROLE_NAMES:
            raise QualificationError(
                "Evidence Package v5 decisions require a valid qualification role")
        phases = sorted(set(phases or []), key=lambda phase: list(C.PHASE_NAMES).index(phase)
                        if phase in C.PHASE_NAMES else 99)
        invalid_phases = [phase for phase in phases if phase not in C.PHASE_NAMES]
        if not phases or invalid_phases:
            raise QualificationError(f"invalid or empty qualification phase scope: {invalid_phases}")
        if len(phases) == len(C.PHASE_NAMES):
            raise QualificationError(
                "blanket all-phase qualifications are prohibited (AIES-AESQS-QP-01-R03)")
        if not sponsor or not sponsor.strip():
            raise QualificationError("a named qualification sponsor is required")
        if not framework_version or not framework_version.strip():
            raise QualificationError("competency framework version is required")
        try:
            starts = datetime.datetime.fromisoformat(str(valid_from).replace("Z", "+00:00"))
            expires = datetime.datetime.fromisoformat(str(valid_until).replace("Z", "+00:00"))
            if starts.tzinfo is None:
                starts = starts.replace(tzinfo=datetime.timezone.utc)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=datetime.timezone.utc)
        except (AttributeError, TypeError, ValueError) as exc:
            raise QualificationError(
                "valid_from and valid_until must be ISO-8601 timestamps") from exc
        now = datetime.datetime.now(datetime.timezone.utc)
        if starts > now or expires <= now or expires <= starts:
            raise QualificationError(
                "validity window must include the decision time and end after it starts")
        validity_days = {
            "ai": {"RT1": 366, "RT2": 366, "RT3": 184, "RT4": 184},
            "human": {"RT1": 1096, "RT2": 731, "RT3": 731, "RT4": 366},
        }
        maximum = validity_days.get(pkg.get("subject_kind", "ai"), validity_days["ai"])[
            pkg["risk_tier"]]
        if (expires - starts).total_seconds() > maximum * 86400:
            raise QualificationError(
                f"validity window exceeds the {maximum}-day maximum for "
                f"{pkg.get('subject_kind', 'ai')} at {C.risk_tier_label(pkg['risk_tier'])} "
                "(AIES-AESQS-QP-01 §7)")

    rater_kinds = set(pkg.get("rater_kinds") or [])
    if consider_advisory_review and "model" not in rater_kinds:
        raise QualificationError(
            "cannot record advisory-review consideration: this evidence package "
            "contains no model-review ratings")

    if decision == "grant-with-conditions" and not conditions:
        raise QualificationError("grant-with-conditions requires at least one condition")

    scope_areas = {
        area: {"cl": d["cl"], "al_envelope": d["al_envelope"],
               "aggregate_A": d["aggregate_A"]}
        for area, d in pkg["areas"].items()
    }
    from . import task_mappings
    mapping = task_mappings.load()
    status = {"grant": "active", "grant-with-conditions": "conditional",
              "deny": "denied"}[decision]
    # Enrich the subject with runtime + model from the deployment manifest,
    # so the record is a self-contained audit manifest.
    dep_id = pkg["model"]["registry_id"]
    runtime = model_name = None
    try:
        from . import registry
        dep = registry.get(dep_id)
        runtime = dep.get("runtime")
        model_name = dep.get("model") or dep.get("family")
    except Exception:
        pass
    record = {
        "kind": "qualification-record",
        "qualification_schema": 2,
        # Assigned atomically when the immutable issued snapshot is persisted.
        "record_id": None,
        "subject": {"deployment": dep_id, "checksum": pkg["model"]["checksum"],
                    "runtime": runtime, "model": model_name},
        "scope": {
            # Legacy aliases remain populated for existing readers.
            "risk_tier": pkg["risk_tier"], "profile": pkg["profile"],
            "subject_kind": pkg["subject_kind"], "areas": scope_areas,
            # Complete AIES-AESQS-QP-01-R02 qualification tuple.
            "subject": pkg.get("subject"),
            "role": role,
            "phases": phases or [],
            "max_risk_tier": pkg["risk_tier"],
            "competency_claims": scope_areas,
            "framework_version": framework_version,
            "engineering_task_mapping": {
                "id": mapping["id"],
                "version": mapping["version"],
                "schema": mapping["schema"],
            },
            "agent_definition": {
                "applicable": bool(agent_definition_version),
                "version": agent_definition_version,
            },
            "sponsor": sponsor,
            "validity": {"from": valid_from, "until": valid_until},
        },
        "decision": decision,
        "status": status,
        "conditions": conditions or [],
        "humans": {
            "authority": authority,
            "second": peer_reviewer,
            "assessor": {"id": assessor_id, "name": assessor},
            "peer_reviewer": {"id": peer_reviewer_id, "name": peer_reviewer},
            "protocol": human_protocol,
        },
        "rationale": rationale,
        "evidence": {"run_id": run_id,
                     "suite_versions": pkg["suite_versions"],
                     "environment_fingerprint": pkg["environment_fingerprint"]},
        "evidence_consideration": {
            "automated_advisory_review": {
                "available": "model" in rater_kinds,
                "considered_by_authority": consider_advisory_review,
            },
            "human_evaluation": {
                # A human may evaluate evidence qualitatively without entering
                # a second numerical scoresheet. Human-scored ratings, when
                # present, remain separately visible in the evidence report.
                "scored_ratings_available": "human" in rater_kinds,
                "evaluator": human_evaluation,
            },
        },
        "review_package": review_package.get("summary") if review_package else None,
        "recorded_at": _now(),
        # Current-state history is projected exclusively from immutable events.
        "history": [],
    }
    _write_new_record(record)
    _append_event(record["record_id"], "issued", status, authority,
                  reason=rationale or f"qualification decision: {decision}")
    return get_record(record["record_id"])


def get_record(record_id: str) -> dict:
    path = _records_dir() / f"{record_id}.json"
    if not path.exists():
        raise QualificationError(f"no qualification record {record_id!r}")
    return _project(workspace.read_json(path))


def list_records() -> list[dict]:
    return [get_record(p.stem) for p in sorted(_records_dir().glob("QUAL-*.json"))]


def _current_deployment_fingerprint(record: dict) -> dict:
    """Rebuild the environment fingerprint for a record's deployment as it
    stands now, through the deployment's own runtime adapter."""
    from . import doctor, registry
    from .adapters import resolve
    dep_id = record["subject"]["deployment"]
    try:
        entry = registry.get(dep_id)
        adapter = resolve(entry["runtime"])()
        adapter.load(entry)
        return doctor.fingerprint(adapter.fingerprint())
    except Exception:
        # Deployment gone or unreachable: cannot reproduce the environment,
        # so it is not the environment it was granted on.
        return doctor.fingerprint({"id": "unavailable", "version": "n/a"})


def check_current(record_id: str) -> dict:
    """Read-only current-state check for bounded decision products.

    Unlike :func:`verify`, this function never appends a lifecycle event. It is
    suitable for guidance rendering, where a failed live check must suppress a
    Use recommendation without silently mutating the qualification registry.
    """
    record = get_record(record_id)
    fp = _current_deployment_fingerprint(record)
    earned = record["evidence"]["environment_fingerprint"].get("fingerprint_hash")
    current = fp.get("fingerprint_hash")
    return {
        "record_id": record_id,
        "status": record["status"],
        "environment_unchanged": earned == current,
        "earned_fingerprint": earned,
        "current_fingerprint": current,
        "checked_at": _now(),
    }


def verify(record_id: str, current_fingerprint: dict | None = None) -> dict:
    """Verify a record against the current environment (D7).

    If the environment fingerprint has changed since the grant, the
    record is invalidated and re-qualification is required — the grant
    does not transfer to a different model x environment.
    """
    from . import doctor
    record = get_record(record_id)
    if record.get("expiry_pending_event"):
        _append_event(
            record_id, "expired", "expired", "platform:verify",
            reason="qualification validity window ended; requalification required")
        record = get_record(record_id)
    if current_fingerprint is None:
        # Reconstruct the fingerprint through the SAME deployment's adapter,
        # so an unchanged environment reproduces the earned fingerprint and
        # only a genuine model/runtime/host change registers (D7).
        fp = _current_deployment_fingerprint(record)
    else:
        fp = current_fingerprint
    earned = record["evidence"]["environment_fingerprint"].get("fingerprint_hash")
    current = fp.get("fingerprint_hash")
    unchanged = earned == current
    result = {
        "record_id": record_id,
        "status": record["status"],
        "environment_unchanged": unchanged,
        "earned_fingerprint": earned,
        "current_fingerprint": current,
    }
    if not unchanged and record["status"] in ("active", "conditional"):
        _append_event(
            record_id, "invalidated", "invalidated", "platform:verify",
            reason="environment fingerprint changed since grant "
                   "(PLATFORM.md D7, AIES-AESQS-RR-01 §2)",
            requalification_scope={
                "subject": record.get("subject"),
                "areas": sorted((record.get("scope") or {}).get("areas", {})),
                "risk_tier": (record.get("scope") or {}).get("risk_tier"),
                "trigger": "environment-fingerprint-change",
            })
        result["status"] = "invalidated"
        result["action"] = ("grant invalidated; re-qualification required on the "
                            "current environment")
    elif record["status"] == "expired":
        result["action"] = "qualification expired; requalification required"
    else:
        result["action"] = "no change"
    return result


def revoke(record_id: str, authority: str, reason: str) -> dict:
    """Withdraw a grant after issue (AIES-AESQS-RR-01 §3)."""
    if not authority.strip():
        raise QualificationError("revocation requires a named human authority")
    return record_lifecycle_event(record_id, "revoked", authority, reason)


def record_lifecycle_event(
    record_id: str,
    event_type: str,
    authority: str,
    reason: str,
    *,
    conditions: list[str] | None = None,
    valid_until: str | None = None,
    superseded_by: str | None = None,
    evidence_run_id: str | None = None,
    peer_reviewer: str | None = None,
    peer_reviewer_id: str | None = None,
    peer_conflict_free: bool = False,
) -> dict:
    """Append a governed lifecycle event and regenerate current state."""
    current = get_record(record_id)
    if event_type == "condition-changed":
        if current["decision"] not in ("grant", "grant-with-conditions"):
            raise QualificationError("conditions apply only to granted qualifications")
        if current["status"] not in ("active", "conditional"):
            raise QualificationError("conditions can change only on an active qualification")
        if conditions is None:
            raise QualificationError("condition-changed requires the complete condition list")
        status = "conditional" if conditions else "active"
        changes = {"conditions": conditions}
    elif event_type == "renewed":
        if current["status"] not in ("active", "conditional"):
            raise QualificationError(
                "renewal cannot reactivate an expired, invalidated, revoked, or superseded record; "
                "complete requalification and issue a superseding record")
        if not valid_until:
            raise QualificationError("renewed requires valid_until")
        if (not evidence_run_id or not peer_reviewer or not peer_reviewer.strip()
                or not peer_reviewer_id):
            raise QualificationError(
                "renewal requires a re-evaluation evidence run and durable named peer reviewer; "
                "renewal is never automatic (AIES-AESQS-QP-01-R18)")
        original_assessor_id = (((current.get("humans") or {}).get("assessor") or {}).get("id"))
        if peer_reviewer_id == original_assessor_id:
            raise QualificationError(
                "renewal peer reviewer must be independent from the original assessor")
        evidence_path = workspace.run_dir(evidence_run_id) / "evidence-package.json"
        if not evidence_path.exists():
            raise QualificationError("renewal evidence run has no aggregated evidence package")
        renewal_evidence = workspace.read_json(evidence_path)
        renewal_areas = renewal_evidence.get("areas") or {}
        required_areas = set((current.get("scope") or {}).get("areas") or {})
        missing_areas = sorted(required_areas - set(renewal_areas))
        if missing_areas:
            raise QualificationError(
                "renewal evidence does not cover the full qualification scope: "
                + ", ".join(C.competency_label(area) for area in missing_areas))
        blocked = [area for area in sorted(required_areas)
                   if not renewal_areas[area].get("decisional")
                   or not renewal_areas[area].get("gates_passed")]
        if blocked:
            raise QualificationError(
                "renewal evidence is not decisional and gate-passing for "
                + ", ".join(C.competency_label(area) for area in blocked))
        current_subject = ((current.get("scope") or {}).get("subject") or {}).get("id")
        renewal_subject = (renewal_evidence.get("subject") or {}).get("id")
        if current_subject and renewal_subject != current_subject:
            raise QualificationError("renewal evidence belongs to a different subject")
        scope = current.get("scope") or {}
        if renewal_evidence.get("risk_tier") != scope.get("risk_tier"):
            raise QualificationError("renewal evidence risk tier does not match the qualification scope")
        if renewal_evidence.get("profile") != scope.get("profile"):
            raise QualificationError("renewal evidence profile does not match the qualification scope")
        from . import raters
        peer_ok, peer_reasons, peer_snapshot = raters.assess_for_run(
            evidence_run_id,
            {"id": peer_reviewer_id, "name": peer_reviewer,
             "conflict_declaration": {
                 "declared": peer_conflict_free,
                 "has_conflict": False if peer_conflict_free else None,
                 "subject_id": renewal_subject}})
        if not peer_ok:
            raise QualificationError(
                "renewal peer-review protocol not satisfied: " + "; ".join(peer_reasons))
        try:
            expiry = datetime.datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=datetime.timezone.utc)
        except (AttributeError, TypeError, ValueError) as exc:
            raise QualificationError("valid_until must be ISO-8601") from exc
        if expiry <= datetime.datetime.now(datetime.timezone.utc):
            raise QualificationError("renewal must extend validity into the future")
        try:
            current_expiry = datetime.datetime.fromisoformat(
                str(((scope.get("validity") or {}).get("until"))).replace("Z", "+00:00"))
            if current_expiry.tzinfo is None:
                current_expiry = current_expiry.replace(tzinfo=datetime.timezone.utc)
        except (AttributeError, TypeError, ValueError) as exc:
            raise QualificationError("current qualification validity is invalid") from exc
        if expiry <= current_expiry:
            raise QualificationError("renewal must extend the current validity window")
        now = datetime.datetime.now(datetime.timezone.utc)
        maximum = ({"RT1": 366, "RT2": 366, "RT3": 184, "RT4": 184}
                   if (current.get("scope") or {}).get("subject_kind") == "ai"
                   else {"RT1": 1096, "RT2": 731, "RT3": 731, "RT4": 366})[
                       (current.get("scope") or {}).get("risk_tier")]
        if (expiry - now).total_seconds() > maximum * 86400:
            raise QualificationError("renewal validity exceeds the normative tier maximum")
        status = "conditional" if current.get("conditions") else "active"
        changes = {"valid_from": now.isoformat(), "valid_until": expiry.isoformat(),
                   "evidence_run_id": evidence_run_id,
                   "peer_reviewer": peer_reviewer.strip(),
                   "peer_reviewer_id": peer_reviewer_id,
                   "peer_reviewer_snapshot": peer_snapshot}
    elif event_type == "suspended":
        if current["status"] not in ("active", "conditional"):
            raise QualificationError("only an active qualification can be suspended")
        status, changes = "suspended", {}
    elif event_type == "invalidated":
        if current["status"] not in ("active", "conditional", "suspended"):
            raise QualificationError("this qualification is already terminal")
        status, changes = "invalidated", {
            "requalification_scope": {
                "subject": current.get("subject"),
                "areas": sorted((current.get("scope") or {}).get("areas", {})),
                "risk_tier": (current.get("scope") or {}).get("risk_tier"),
                "trigger": reason,
            }}
    elif event_type == "revoked":
        if current["status"] not in ("active", "conditional", "suspended"):
            raise QualificationError("this qualification is already terminal")
        status, changes = "revoked", {}
    elif event_type == "superseded":
        if not superseded_by:
            raise QualificationError("superseded requires superseded_by")
        get_record(superseded_by)
        status, changes = "superseded", {"superseded_by": superseded_by}
    else:
        raise QualificationError(
            "event type must be condition-changed | renewed | suspended | "
            "invalidated | revoked | superseded")
    _append_event(record_id, event_type, status, authority, reason=reason, **changes)
    return get_record(record_id)

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

from . import workspace

DECISIONS = ("grant", "grant-with-conditions", "deny")
# Status lifecycle for a Qualification Record.
#   active     — a current grant
#   conditional— granted with conditions that must hold
#   denied     — the authority declined
#   invalidated— an input changed (e.g. environment fingerprint); needs re-qualification
#   revoked    — withdrawn after issue (AIES-AESQS-RR-01 §3)
#   superseded — replaced by a later record for the same scope
STATUSES = ("active", "conditional", "denied", "invalidated", "revoked", "superseded")


class QualificationError(Exception):
    pass


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _records_dir():
    d = workspace.ensure() / "qualifications"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _next_qual_id() -> str:
    """Human-friendly sequential manifest id: QUAL-<year>-<NNN>."""
    year = datetime.datetime.now(datetime.timezone.utc).year
    n = len(list(_records_dir().glob(f"QUAL-{year}-*.json"))) + 1
    while (_records_dir() / f"QUAL-{year}-{n:03d}.json").exists():
        n += 1
    return f"QUAL-{year}-{n:03d}"


def record_decision(
    run_id: str,
    decision: str,
    authority: str,
    *,
    second_human: str | None = None,
    conditions: list[str] | None = None,
    review_package: dict | None = None,
    rationale: str = "",
) -> dict:
    """Record a human qualification decision over an aggregated evidence
    package, producing a Qualification Record.

    Enforces D8: a named human authority is required; the platform is
    only the scribe. The two-human minimum of AIES-AESQS-QP-01-R01
    applies to grant decisions — a grant/grant-with-conditions requires
    a second named human.
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

    if decision in ("grant", "grant-with-conditions"):
        if not second_human or not second_human.strip():
            raise QualificationError(
                "a grant requires two named humans (AIES-AESQS-QP-01-R01); "
                "supply a second reviewer")
        # A grant may not issue on non-decisional or gate-failing evidence.
        nondecisional = [a for a, d in pkg["areas"].items() if not d["decisional"]]
        if nondecisional:
            raise QualificationError(
                f"cannot grant on NON-DECISIONAL evidence for {', '.join(nondecisional)} "
                "(AIES-AESQS-CS-01 §6); grow the sample or deny")
        gate_failures = [a for a, d in pkg["areas"].items() if not d["gates_passed"]]
        if gate_failures:
            raise QualificationError(
                f"cannot grant: gates failed for {', '.join(gate_failures)} "
                "(AIES-AESQS-CS-01-R04/R05); re-scope to a lower tier or deny")
    if decision == "grant-with-conditions" and not conditions:
        raise QualificationError("grant-with-conditions requires at least one condition")

    scope_areas = {
        area: {"cl": d["cl"], "al_envelope": d["al_envelope"],
               "aggregate_A": d["aggregate_A"]}
        for area, d in pkg["areas"].items()
    }
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
        "record_id": _next_qual_id(),
        "subject": {"deployment": dep_id, "checksum": pkg["model"]["checksum"],
                    "runtime": runtime, "model": model_name},
        "scope": {"risk_tier": pkg["risk_tier"], "profile": pkg["profile"],
                  "subject_kind": pkg["subject_kind"], "areas": scope_areas},
        "decision": decision,
        "status": status,
        "conditions": conditions or [],
        "humans": {"authority": authority, "second": second_human},
        "rationale": rationale,
        "evidence": {"run_id": run_id,
                     "suite_versions": pkg["suite_versions"],
                     "environment_fingerprint": pkg["environment_fingerprint"]},
        "review_package": review_package.get("summary") if review_package else None,
        "recorded_at": _now(),
        "history": [{"status": status, "at": _now(), "by": authority}],
    }
    path = _records_dir() / f"{record['record_id']}.json"
    workspace.write_json(path, record, overwrite=True)
    return record


def get_record(record_id: str) -> dict:
    path = _records_dir() / f"{record_id}.json"
    if not path.exists():
        raise QualificationError(f"no qualification record {record_id!r}")
    return workspace.read_json(path)


def list_records() -> list[dict]:
    return [workspace.read_json(p) for p in sorted(_records_dir().glob("*.json"))]


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


def verify(record_id: str, current_fingerprint: dict | None = None) -> dict:
    """Verify a record against the current environment (D7).

    If the environment fingerprint has changed since the grant, the
    record is invalidated and re-qualification is required — the grant
    does not transfer to a different model x environment.
    """
    from . import doctor
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
        record["status"] = "invalidated"
        record["history"].append({
            "status": "invalidated", "at": _now(),
            "by": "platform:verify",
            "reason": "environment fingerprint changed since grant "
                      "(PLATFORM.md D7, AIES-AESQS-RR-01 §2)"})
        workspace.write_json(_records_dir() / f"{record_id}.json", record,
                             overwrite=True)
        result["status"] = "invalidated"
        result["action"] = ("grant invalidated; re-qualification required on the "
                            "current environment")
    else:
        result["action"] = "no change"
    return result


def revoke(record_id: str, authority: str, reason: str) -> dict:
    """Withdraw a grant after issue (AIES-AESQS-RR-01 §3)."""
    if not authority.strip():
        raise QualificationError("revocation requires a named human authority")
    record = get_record(record_id)
    record["status"] = "revoked"
    record["history"].append({"status": "revoked", "at": _now(),
                              "by": authority, "reason": reason})
    workspace.write_json(_records_dir() / f"{record_id}.json", record, overwrite=True)
    return record

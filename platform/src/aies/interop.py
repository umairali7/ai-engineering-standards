"""Versioned evidence bridges for Inspect JSON and SARIF 2.1.0.

Bridges preserve source digests and disclose loss. They never infer AIES scores
from unrelated metrics and never turn static-analysis findings into proof of
correctness or conformance.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import (constants as C, evalexport, evalimport, evidence_adapters,
               evidence_events, subjects, workspace)


class InteropError(RuntimeError):
    pass


def _read(path: Path) -> tuple[dict, str]:
    raw = Path(path).read_bytes()
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise InteropError(f"{path} is not valid JSON: {e}") from e
    if not isinstance(data, dict):
        raise InteropError(f"{path} must contain a JSON object")
    return data, "sha256:" + hashlib.sha256(raw).hexdigest()


def _ev_scores(value) -> dict | None:
    if isinstance(value, dict) and isinstance(value.get("value"), dict):
        value = value["value"]
    if not isinstance(value, dict):
        return None
    if all(isinstance(value.get(d), int) and value[d] in C.VALID_SCORES
           for d in C.DIMENSIONS):
        return {d: value[d] for d in C.DIMENSIONS}
    return None


def import_inspect(run_id: str, path: Path, *, source: str | None = None) -> dict:
    """Import the documented Inspect EvalLog JSON profile into an AIES run.

    Each sample must carry ``metadata.aies.scenario_id`` (or a scenario-like
    sample ``id``) and an AIES scorer value containing EV1 through EV6. Other
    Inspect content is retained only by source digest and counted in loss; it is
    never guessed into the AIES rubric.
    """
    data, digest = _read(path)
    samples = data.get("samples")
    if not isinstance(samples, list):
        raise InteropError(
            "supported Inspect JSON requires a top-level samples array; export "
            "the EvalLog to JSON with per-sample metadata.aies and AIES EV scores"
        )
    items = []
    skipped = []
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            skipped.append({"index": index, "reason": "sample is not an object"})
            continue
        aies_meta = ((sample.get("metadata") or {}).get("aies") or {})
        sid = aies_meta.get("scenario_id") or sample.get("id")
        repeat = int(aies_meta.get("repeat", 1))
        scores_block = sample.get("scores") or {}
        candidates = (
            scores_block.get("aies"),
            scores_block.get("AIES"),
            sample.get("aies_scores"),
        )
        scores = next((parsed for candidate in candidates
                       if (parsed := _ev_scores(candidate)) is not None), None)
        if not sid or scores is None:
            skipped.append({
                "index": index,
                "sample_id": sample.get("id"),
                "reason": "missing AIES scenario identity or complete EV1-EV6 scores",
            })
            continue
        items.append({
            "scenario_id": str(sid),
            "repeat": repeat,
            "scores": scores,
            "findings": aies_meta.get("findings") or [],
            "grounding_diagnostics": aies_meta.get("grounding_diagnostics"),
        })
    if not items:
        raise InteropError(
            f"no losslessly importable AIES-scored samples ({len(skipped)} skipped)"
        )

    bridge_dir = workspace.run_dir(run_id) / "imports"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    converted = bridge_dir / f"inspect-{digest.split(':', 1)[1][:16]}.json"
    if converted.exists():
        raise InteropError(
            f"this Inspect source was already converted for the run: {converted}"
        )
    adapter = evidence_adapters.get("aies-inspect-eval-log/v1")
    converted.write_text(json.dumps({
        "adapter": adapter,
        "source": source or f"inspect:{Path(path).name}:{digest[:23]}",
        "items": items,
    }, indent=2), encoding="utf-8")
    imported = evalimport.import_eval(run_id, str(converted), source=source)
    manifest_path = workspace.run_dir(run_id) / "manifest.json"
    manifest = (workspace.read_json(manifest_path)
                if manifest_path.exists() else {"created_at": None})
    descriptor = (
        subjects.from_manifest(manifest) if manifest_path.exists()
        else subjects.build(
            run_id, kind="ai_system", display_name=run_id,
            extensions={"compatibility": {"manifest_missing": True}}))
    event_paths = []
    imported_by_identity = {
        (item["scenario_id"], item["repeat"]): item for item in items}
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            continue
        aies_meta = ((sample.get("metadata") or {}).get("aies") or {})
        sid = str(aies_meta.get("scenario_id") or sample.get("id") or "")
        repeat = int(aies_meta.get("repeat", 1))
        item = imported_by_identity.get((sid, repeat))
        if item is None:
            continue
        event_paths.append(str(evidence_events.append(run_id, evidence_events.build(
            event_type="rating",
            subject_id=descriptor["id"],
            instrument_id=sid,
            modality="automated-rating",
            source=source or f"inspect:{Path(path).name}",
            source_record_id=f"sample:{index}:{sid}:r{repeat}",
            source_digest=digest,
            adapter_profile=adapter["profile"],
            observed_at=manifest.get("created_at"),
            correlation_id=f"{sid}-r{repeat}.json",
            classification=descriptor["privacy"],
            payload={
                "scores": item["scores"],
                "findings": item["findings"],
                "external_profile": adapter["profile"],
            },
        ))))
    loss = {
        "source_format": "Inspect EvalLog JSON (supported AIES profile)",
        "source_digest": digest,
        "converter": "aies-inspect-bridge/v1",
        "adapter": adapter,
        "samples_seen": len(samples),
        "samples_imported": len(items),
        "samples_skipped": skipped,
        "correlation_gaps": [
            {"sample": item.get("sample_id", item.get("index")),
             "reason": item["reason"]} for item in skipped
        ],
        "not_represented_in_ratings": [
            "messages and model transcript",
            "tool calls and attachments",
            "non-AIES scorer metrics",
            "sandbox and token accounting",
        ],
    }
    loss_path = converted.with_suffix(".loss.json")
    loss_path.write_text(json.dumps(loss, indent=2), encoding="utf-8")
    return {**imported, "source_digest": digest, "converted": str(converted),
            "loss_report": str(loss_path), "skipped_samples": len(skipped),
            "adapter": adapter, "typed_events_written": len(event_paths)}


def export_inspect(run_id: str, destination: Path) -> dict:
    """Export an AIES run into the documented Inspect-compatible JSON profile."""
    generic = evalexport.export_run(run_id)
    samples = []
    for item in generic["items"]:
        samples.append({
            "id": f"{item['scenario_id']}-r{item['repeat']}",
            "input": item.get("prompt", ""),
            "output": item.get("response", ""),
            "metadata": {"aies": {
                "scenario_id": item["scenario_id"],
                "repeat": item["repeat"],
                "area": item.get("area"),
                "findings": item.get("findings") or [],
                "grounding_diagnostics": item.get("grounding_diagnostics"),
            }},
            "scores": ({"aies": {"value": item["scores"]}}
                       if item.get("scores") else {}),
        })
    payload = {
        "schema": "aies-inspect-eval-log-profile/v1",
        "adapter": evidence_adapters.get("aies-inspect-eval-log/v1"),
        "eval": {
            "task": "aies-engineering-evaluation",
            "metadata": {"aies_run": generic["run"]},
        },
        "samples": samples,
        "loss": {
            "converter": "aies-inspect-bridge/v1",
            "note": "AIES emits the portable JSON profile; native .eval container "
                    "metadata is owned by Inspect and is not fabricated.",
        },
    }
    destination = Path(destination).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise InteropError(f"{destination} already exists; exports are immutable")
    content = json.dumps(payload, indent=2).encode()
    destination.write_bytes(content)
    return {"run_id": run_id, "samples": len(samples),
            "source_digest": "sha256:" + hashlib.sha256(content).hexdigest(),
            "artifact": str(destination)}


def import_sarif(
    path: Path,
    *,
    destination: Path | None = None,
    subject_id: str | None = None,
    classification: str = "internal",
) -> dict:
    """Normalize SARIF 2.1.0 findings without changing their meaning."""
    data, digest = _read(path)
    if data.get("version") != "2.1.0" or not isinstance(data.get("runs"), list):
        raise InteropError("supported SARIF input requires version 2.1.0 and runs[]")
    findings = []
    invocations = []
    for run_index, run in enumerate(data["runs"]):
        tool = ((run.get("tool") or {}).get("driver") or {})
        tool_info = {
            "name": tool.get("name"),
            "version": tool.get("semanticVersion") or tool.get("version"),
            "rules": {r.get("id"): r for r in (tool.get("rules") or [])
                      if isinstance(r, dict) and r.get("id")},
        }
        for invocation in run.get("invocations") or []:
            invocations.append({
                "run": run_index,
                "execution_successful": invocation.get("executionSuccessful"),
                "exit_code": invocation.get("exitCode"),
                "working_directory": invocation.get("workingDirectory"),
            })
        for result_index, result in enumerate(run.get("results") or []):
            locations = []
            for location in result.get("locations") or []:
                physical = location.get("physicalLocation") or {}
                artifact = physical.get("artifactLocation") or {}
                region = physical.get("region") or {}
                locations.append({
                    "uri": artifact.get("uri"),
                    "uri_base_id": artifact.get("uriBaseId"),
                    "start_line": region.get("startLine"),
                    "start_column": region.get("startColumn"),
                    "end_line": region.get("endLine"),
                    "end_column": region.get("endColumn"),
                })
            findings.append({
                "id": f"sarif-{run_index}-{result_index}",
                "tool": tool_info["name"],
                "tool_version": tool_info["version"],
                "rule_id": result.get("ruleId"),
                "rule": tool_info["rules"].get(result.get("ruleId")),
                "level": result.get("level", "warning"),
                "message": (result.get("message") or {}).get("text"),
                "locations": locations,
                "fingerprints": result.get("partialFingerprints") or {},
                "fixes": result.get("fixes") or [],
                "suppressions": result.get("suppressions") or [],
                "baseline_state": result.get("baselineState"),
            })
    adapter = evidence_adapters.get("aies-sarif-2.1.0/v1")
    bound_subject = subject_id or "unbound-repository"
    events = []
    for finding in findings:
        events.append(evidence_events.build(
            event_type="observation",
            subject_id=bound_subject,
            instrument_id=finding.get("rule_id"),
            modality="repository-static-analysis",
            source=f"sarif:{Path(path).name}",
            source_record_id=finding["id"],
            source_digest=digest,
            adapter_profile=adapter["profile"],
            classification=classification,
            payload={
                "tool": finding.get("tool"),
                "tool_version": finding.get("tool_version"),
                "rule_id": finding.get("rule_id"),
                "level": finding.get("level"),
                "message": finding.get("message"),
                "locations": finding.get("locations") or [],
                "claim_boundary": (
                    "tool-reported finding; not proof of correctness, "
                    "absence of defects, or conformance"),
            },
        ))
    loss = {
        "source_format": "SARIF 2.1.0",
        "source_digest": digest,
        "adapter": adapter,
        "records_seen": len(findings),
        "records_imported": len(events),
        "records_skipped": [],
        "correlation_gaps": ([] if subject_id else [{
            "field": "subject_id",
            "reason": (
                "No repository subject was supplied; events are retained under "
                "the explicit unbound-repository identity."),
        }]),
        "not_represented": [
            "SARIF properties outside the normalized finding profile",
            "source files and repository content",
            "AIES EV scores, maturity, correctness, and conformance",
        ],
    }
    normalized = {
        "schema": "aies-sarif-evidence/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "subject": {"id": bound_subject, "kind": "repository",
                    "bound": bool(subject_id), "classification": classification},
        "adapter": adapter,
        "source": {"format": "SARIF", "version": "2.1.0", "digest": digest,
                   "path": str(Path(path).resolve())},
        "semantics": {
            "modality": "repository-static-analysis-finding",
            "claim": "tool-reported findings only",
            "does_not_establish": ["correctness", "absence of defects", "conformance"],
        },
        "invocations": invocations,
        "findings": findings,
        "events": events,
        "loss_report": loss,
    }
    if destination is None:
        imports = workspace.ensure() / "imports"
        imports.mkdir(parents=True, exist_ok=True)
        destination = imports / f"sarif-{digest.split(':', 1)[1][:16]}.json"
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise InteropError(f"{destination} already exists; imports are immutable")
    destination.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    loss_path = destination.with_suffix(".loss.json")
    loss_path.write_text(json.dumps(loss, indent=2), encoding="utf-8")
    return {"source_digest": digest, "runs": len(data["runs"]),
            "findings": len(findings), "invocations": len(invocations),
            "artifact": str(destination), "loss_report": str(loss_path),
            "adapter": adapter, "subject_id": bound_subject,
            "typed_events": len(events)}


def export_sarif(path: Path, destination: Path) -> dict:
    """Round-trip a normalized AIES SARIF evidence artifact to SARIF 2.1.0."""
    data, digest = _read(path)
    if data.get("schema") != "aies-sarif-evidence/v1":
        raise InteropError("input is not an aies-sarif-evidence/v1 artifact")
    grouped: dict[tuple[str | None, str | None], list[dict]] = {}
    for finding in data.get("findings") or []:
        grouped.setdefault(
            (finding.get("tool"), finding.get("tool_version")), []).append(finding)
    runs = []
    for (tool, version), findings in grouped.items():
        rule_map = {}
        results = []
        for finding in findings:
            if finding.get("rule_id") and finding.get("rule"):
                rule_map[finding["rule_id"]] = finding["rule"]
            locations = []
            for location in finding.get("locations") or []:
                locations.append({"physicalLocation": {
                    "artifactLocation": {
                        key: location[key] for key in ("uri", "uri_base_id")
                        if location.get(key) is not None
                    },
                    "region": {
                        sarif_key: location[internal_key]
                        for sarif_key, internal_key in (
                            ("startLine", "start_line"),
                            ("startColumn", "start_column"),
                            ("endLine", "end_line"),
                            ("endColumn", "end_column"),
                        ) if location.get(internal_key) is not None
                    },
                }})
                artifact = locations[-1]["physicalLocation"]["artifactLocation"]
                if "uri_base_id" in artifact:
                    artifact["uriBaseId"] = artifact.pop("uri_base_id")
            results.append({
                **({"ruleId": finding["rule_id"]} if finding.get("rule_id") else {}),
                "level": finding.get("level", "warning"),
                "message": {"text": finding.get("message") or ""},
                "locations": locations,
                "partialFingerprints": finding.get("fingerprints") or {},
                "fixes": finding.get("fixes") or [],
                "suppressions": finding.get("suppressions") or [],
                **({"baselineState": finding["baseline_state"]}
                   if finding.get("baseline_state") else {}),
            })
        runs.append({
            "tool": {"driver": {
                "name": tool or "unknown",
                **({"semanticVersion": version} if version else {}),
                "rules": list(rule_map.values()),
            }},
            "results": results,
        })
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": runs,
        "properties": {
            "aies": {
                "sourceNormalizedArtifactDigest": digest,
                "limitation": "tool findings; not proof of correctness or conformance",
            }
        },
    }
    destination = Path(destination).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise InteropError(f"{destination} already exists; exports are immutable")
    content = json.dumps(payload, indent=2).encode()
    destination.write_bytes(content)
    return {"runs": len(runs), "findings": sum(len(r["results"]) for r in runs),
            "artifact": str(destination),
            "digest": "sha256:" + hashlib.sha256(content).hexdigest()}

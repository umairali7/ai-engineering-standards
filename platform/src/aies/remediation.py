"""Subject-neutral, evidence-linked remediation and monitoring plans.

Plans are deterministic decision support derived from canonical findings and
coverage gaps. They assign no work, close no risk, and grant no authority.
"""

from __future__ import annotations

import hashlib
import html
import json
import uuid
from datetime import datetime, timezone

from . import workspace


SCHEMA = "aies-evidence-linked-remediation-plan/v1"
WORKFLOW_STATES = (
    "open", "accepted", "in-progress", "mitigated", "closed", "deferred",
)
DISPOSITION_STATES = WORKFLOW_STATES[1:]


class RemediationError(ValueError):
    pass


def _action_id(subject_id: str, source_kind: str, source_id: str) -> str:
    identity = f"{subject_id}\0{source_kind}\0{source_id}".encode()
    return "ACT-" + hashlib.sha256(identity).hexdigest()[:12].upper()


def _coverage_priority(item: dict) -> tuple[int, str]:
    condition = item.get("collection_condition")
    status = item.get("status")
    rank = {
        "conflicting": 1,
        "failed-to-collect": 1,
        "stale": 2,
        "redacted": 2,
        "tool-not-installed": 3,
        "unavailable": 3,
    }.get(condition, 3 if status == "unsupported" else 4)
    return rank, f"P{min(rank, 3)}"


def _finding_priority(finding: dict) -> tuple[int, str]:
    rank = {
        "critical": 0, "high": 1, "medium": 2, "low": 3,
    }.get(str(finding.get("severity", "")).lower(), 3)
    return rank, f"P{rank}"


def _action(
    *,
    subject_id: str,
    source_kind: str,
    source_id: str,
    source_title: str,
    priority_rank: int,
    priority: str,
    impact: str,
    evidence_refs: list[str],
    condition_refs: list[str],
    recommendation: str,
    acceptance_signal: str,
    reassessment_command: str,
    reassessment_trigger: str,
    monitoring_signals: list[str],
) -> dict:
    return {
        "id": _action_id(subject_id, source_kind, source_id),
        "priority": priority,
        "priority_rank": priority_rank,
        "workflow": {
            "status": "open",
            "owner": None,
            "owner_status": "unassigned",
            "authority": (
                "A named subject owner accepts, defers, or closes this action; "
                "AIES only prepares the record."),
            "updated_at": None,
            "disposition": None,
        },
        "source": {
            "kind": source_kind,
            "id": source_id,
            "title": source_title,
        },
        "impact": impact,
        "evidence_refs": sorted(set(evidence_refs)),
        "condition_refs": sorted(set(condition_refs)),
        "recommendation": recommendation,
        "acceptance_signal": acceptance_signal,
        "dependencies": [],
        "monitoring": {
            "status": (
                "linked" if monitoring_signals else "not-established"),
            "evidence_level": "field-observation",
            "signals": monitoring_signals,
            "decision_product": "DP-10 — Ongoing Monitoring and Reassessment",
            "boundary": (
                "Monitoring evidence may trigger reassessment; it cannot "
                "retroactively rewrite the original observation."),
        },
        "reassessment": {
            "trigger": reassessment_trigger,
            "command": reassessment_command,
        },
        "closure": {
            "status": "not-evaluated",
            "required_evidence": acceptance_signal,
            "evidence_refs": [],
            "closed_by": None,
            "closed_at": None,
        },
    }


def build(
    coverage: dict,
    *,
    findings: list[dict] | None = None,
    reassessment_command: str,
) -> dict:
    """Build one deterministic plan from gaps and optional direct findings."""
    subject = coverage["subject"]
    subject_id = str(
        subject.get("id")
        or coverage.get("evidence_scope", {}).get("id")
        or subject.get("display_name")
        or "unknown-subject")
    subject_view = {
        **subject,
        "id": subject_id,
        "display_name": (
            subject.get("display_name")
            or subject.get("name")
            or subject_id),
    }
    monitoring_refs = []
    for item_id in ("EM-03", "EM-06"):
        for cell in coverage["categories"]["evidence_modalities"]["cells"]:
            if cell["id"] == item_id and cell["status"] in (
                    "assessed", "partially-assessed"):
                monitoring_refs.extend(cell["evidence_refs"])
    actions = []
    for item in coverage["blind_spots"]:
        source_id = f"{item['category']}/{item['id']}"
        priority_rank, priority = _coverage_priority(item)
        actions.append(_action(
            subject_id=subject_id,
            source_kind="coverage-gap",
            source_id=source_id,
            source_title=item["title"],
            priority_rank=priority_rank,
            priority=priority,
            impact=(
                f"{item['status']} coverage with "
                f"{item['collection_condition']} collection state; the "
                "corresponding perspective cannot support a positive claim."),
            evidence_refs=item.get("evidence_refs") or [],
            condition_refs=item.get("condition_refs") or [],
            recommendation=item["next_evidence"],
            acceptance_signal=(
                "Fresh, non-conflicting direct evidence is retained for this "
                "perspective, or a named authority records a justified "
                "not-applicable disposition in a revised profile."),
            reassessment_command=reassessment_command,
            reassessment_trigger=(
                "Evidence is collected, restored, refreshed, resolved, or the "
                "profile/subject fingerprint materially changes."),
            monitoring_signals=monitoring_refs,
        ))
    for finding in findings or []:
        source_id = str(finding.get("id") or "unidentified-finding")
        priority_rank, priority = _finding_priority(finding)
        artifacts = finding.get("artifacts") or []
        actions.append(_action(
            subject_id=subject_id,
            source_kind="engineering-finding",
            source_id=source_id,
            source_title=finding.get("title") or source_id,
            priority_rank=priority_rank,
            priority=priority,
            impact=finding.get("impact") or finding.get("title") or source_id,
            evidence_refs=artifacts,
            condition_refs=[],
            recommendation=(
                finding.get("recommendation")
                or "Triage the source finding, preserve its disposition, and "
                "retain evidence from the appropriate native verification tool."),
            acceptance_signal=(
                finding.get("acceptance_signal")
                or "The finding has a retained disposition and the relevant "
                "native check is rerun against the changed subject."),
            reassessment_command=reassessment_command,
            reassessment_trigger=(
                "Affected source, dependency, configuration, retained tool "
                "result, or subject fingerprint changes."),
            monitoring_signals=monitoring_refs,
        ))
    unique = {action["id"]: action for action in actions}
    ordered = sorted(
        unique.values(),
        key=lambda action: (
            action["priority_rank"], action["source"]["kind"],
            action["source"]["id"]))
    counts = {
        state: sum(
            action["workflow"]["status"] == state for action in ordered)
        for state in WORKFLOW_STATES
    }
    plan = {
        "kind": "aies-evidence-linked-remediation-plan",
        "schema": SCHEMA,
        "generated_at": (
            coverage.get("generated_at")
            or datetime.now(timezone.utc).isoformat()),
        "subject": subject_view,
        "profile": coverage["profile"],
        "source_scope": coverage["evidence_scope"],
        "summary": {
            "actions": len(ordered),
            "unassigned": sum(
                action["workflow"]["owner_status"] == "unassigned"
                for action in ordered),
            "monitoring_linked": sum(
                action["monitoring"]["status"] == "linked"
                for action in ordered),
            "workflow_states": counts,
        },
        "actions": ordered,
        "disposition_events": 0,
        "ignored_dispositions": [],
        "claim_boundary": (
            "This plan is informational decision support. It does not assign "
            "an owner, accept risk, prove remediation, close a finding, alter "
            "scores, qualify a subject, or authorize deployment."),
    }
    reference = str(coverage.get("evidence_scope", {}).get("id") or "")
    return apply_dispositions(plan, reference) if reference else plan


def for_reference(reference: str) -> dict:
    """Build the current plan view for one run or recorded repository audit."""
    from . import assessment_coverage

    audit_path = workspace.root() / "audits" / f"{reference}.json"
    if audit_path.is_file():
        result = workspace.read_json(audit_path)
        matrix = assessment_coverage.for_repository(result)
        analysis = result.get("engineering_analysis") or {}
        repository_argument = str(result.get("repo") or ".").replace('"', "")
        return build(
            matrix, findings=analysis.get("findings") or [],
            reassessment_command=f'aies audit "{repository_argument}"')
    matrix = assessment_coverage.for_run(reference)
    return build(
        matrix, reassessment_command=f"aies resume {reference}")


def _events_dir(reference: str):
    workspace.validate_run_id(reference)
    return workspace.ensure() / "remediation" / reference / "events"


def history(reference: str) -> list[dict]:
    directory = _events_dir(reference)
    if not directory.exists():
        return []
    return [
        workspace.read_json(path)
        for path in sorted(directory.glob("*.json"))
    ]


def apply_dispositions(plan: dict, reference: str) -> dict:
    """Overlay append-only human dispositions on a regenerated plan view."""
    actions = {action["id"]: action for action in plan["actions"]}
    ignored = []
    events = history(reference)
    for event in events:
        action = actions.get(event.get("action_id"))
        if action is None:
            ignored.append({
                "event_id": event.get("event_id"),
                "reason": "action is absent from the current generated plan",
            })
            continue
        action["workflow"].update({
            "status": event["status"],
            "owner": event["owner"],
            "owner_status": "assigned",
            "authority": event["authority"],
            "updated_at": event["recorded_at"],
            "disposition": event["note"],
        })
        if event["status"] in ("mitigated", "closed"):
            action["closure"].update({
                "status": (
                    "evidence-referenced"
                    if event["evidence_refs"] else "not-evaluated"),
                "evidence_refs": event["evidence_refs"],
                "closed_by": event["owner"],
                "closed_at": event["recorded_at"],
            })
    plan["disposition_events"] = len(events)
    plan["ignored_dispositions"] = ignored
    plan["summary"]["unassigned"] = sum(
        action["workflow"]["owner_status"] == "unassigned"
        for action in plan["actions"])
    plan["summary"]["monitoring_linked"] = sum(
        action["monitoring"]["status"] == "linked"
        for action in plan["actions"])
    plan["summary"]["workflow_states"] = {
        state: sum(
            action["workflow"]["status"] == state
            for action in plan["actions"])
        for state in WORKFLOW_STATES
    }
    return plan


def record_disposition(
    reference: str,
    action_id: str,
    *,
    status: str,
    owner: str,
    authority: str,
    note: str,
    evidence_refs: list[str] | None = None,
) -> dict:
    """Append a named-human action disposition without mutating source evidence."""
    if status not in DISPOSITION_STATES:
        raise RemediationError(
            "status must be " + ", ".join(DISPOSITION_STATES))
    for field, value in (
            ("action_id", action_id), ("owner", owner),
            ("authority", authority), ("note", note)):
        if not isinstance(value, str) or not value.strip():
            raise RemediationError(f"{field} is required")
    if not action_id.startswith("ACT-"):
        raise RemediationError("action_id must be an ACT-* identifier")
    refs = sorted(set(evidence_refs or []))
    if status in ("mitigated", "closed") and not refs:
        raise RemediationError(
            f"{status} requires at least one --evidence reference")
    recorded_at = datetime.now(timezone.utc)
    event = {
        "kind": "aies-remediation-disposition",
        "schema": "aies-remediation-disposition/v1",
        "event_id": "RMD-" + uuid.uuid4().hex,
        "reference": workspace.validate_run_id(reference),
        "action_id": action_id,
        "status": status,
        "owner": owner.strip(),
        "authority": authority.strip(),
        "note": note.strip(),
        "evidence_refs": refs,
        "evidence_status": (
            "referenced-not-verified" if refs else "not-supplied"),
        "recorded_at": recorded_at.isoformat(),
        "claim_boundary": (
            "This is a named-human workflow disposition. It does not alter "
            "canonical assessment evidence, scores, qualification, or "
            "deployment authority. Evidence references are retained as "
            "claims and are not independently verified by this command."),
    }
    directory = _events_dir(reference)
    path = directory / (
        recorded_at.strftime("%Y%m%dT%H%M%S%fZ")
        + "-" + event["event_id"] + ".json")
    workspace.write_json(path, event)
    return {**event, "path": str(path)}


def render_markdown(plan: dict) -> str:
    lines = [
        "# AIES Evidence-Linked Remediation & Monitoring Plan",
        "",
        "> **INFORMATIONAL — ACTIONS ARE UNASSIGNED UNTIL A NAMED OWNER "
        "RECORDS A DISPOSITION.**",
        "",
        f"**Subject:** `{plan['subject']['id']}` — "
        f"{plan['subject']['display_name']}  ",
        f"**Profile:** `{plan['profile']['id']}` — "
        f"{plan['profile']['title']}  ",
        f"**Actions:** {plan['summary']['actions']} · "
        f"**Unassigned:** {plan['summary']['unassigned']} · "
        f"**Monitoring linked:** {plan['summary']['monitoring_linked']}",
        "",
        "| Priority | Action | Source | Workflow | Monitoring |",
        "|---|---|---|---|---|",
    ]
    for action in plan["actions"]:
        source = action["source"]
        lines.append(
            f"| {action['priority']} | `{action['id']}` — "
            f"{source['title']} | {source['kind']} `{source['id']}` | "
            f"{action['workflow']['status']} / "
            f"{action['workflow']['owner_status']} | "
            f"{action['monitoring']['status']} |")
    if not plan["actions"]:
        lines.append("| — | No generated actions | — | — | — |")
    lines += ["", "## Action details", ""]
    for action in plan["actions"]:
        lines += [
            f"### {action['id']} — {action['source']['title']}",
            "",
            f"- **Impact:** {action['impact']}",
            f"- **Recommendation:** {action['recommendation']}",
            f"- **Acceptance signal:** {action['acceptance_signal']}",
            f"- **Reassessment trigger:** "
            f"{action['reassessment']['trigger']}",
            f"- **Reassessment command:** "
            f"`{action['reassessment']['command']}`",
            f"- **Owner/authority:** {action['workflow']['authority']}",
            f"- **Monitoring:** {action['monitoring']['status']} — "
            f"{action['monitoring']['boundary']}",
            "",
        ]
    lines += [plan["claim_boundary"], ""]
    return "\n".join(lines)


def render_json(plan: dict) -> str:
    return json.dumps(plan, indent=2) + "\n"


def render_html(plan: dict) -> str:
    rows = "".join(
        "<tr><td>" + html.escape(action["priority"])
        + "</td><td><code>" + html.escape(action["id"])
        + "</code> — " + html.escape(action["source"]["title"])
        + "</td><td>" + html.escape(action["source"]["kind"])
        + "</td><td>" + html.escape(action["workflow"]["status"])
        + " / " + html.escape(action["workflow"]["owner_status"])
        + "</td><td>" + html.escape(action["monitoring"]["status"])
        + "</td></tr>"
        for action in plan["actions"])
    return (
        "<!doctype html><html><head><meta charset='utf-8'><meta "
        "name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>AIES Remediation Plan</title><style>"
        "body{font:15px system-ui;max-width:1200px;margin:40px auto;padding:0 20px;"
        "color:#172033}table{border-collapse:collapse;width:100%}"
        "th,td{padding:8px;border-bottom:1px solid #d8deea;text-align:left}"
        "th{background:#eef3fb}code{color:#3154a5}.notice{padding:12px;"
        "border:1px solid #d8deea;border-radius:8px}</style></head><body>"
        "<h1>AIES Evidence-Linked Remediation &amp; Monitoring Plan</h1>"
        "<p class='notice'><strong>Informational.</strong> Actions remain "
        "unassigned until a named owner records a disposition.</p><p><code>"
        + html.escape(plan["subject"]["id"]) + "</code> — "
        + html.escape(plan["subject"]["display_name"])
        + "</p><table><thead><tr><th>Priority</th><th>Action</th><th>Source</th>"
        "<th>Workflow</th><th>Monitoring</th></tr></thead><tbody>"
        + (rows or "<tr><td colspan='5'>No generated actions</td></tr>")
        + "</tbody></table><p>" + html.escape(plan["claim_boundary"])
        + "</p></body></html>"
    )


def write_repository_view(reference: str, plan: dict) -> dict[str, str]:
    """Refresh repository remediation views outside append-only audit records."""
    workspace.validate_run_id(reference)
    target = workspace.ensure() / "reports" / reference
    paths = {
        "markdown": target / "evidence-remediation-plan.md",
        "json": target / "evidence-remediation-plan.json",
        "html": target / "evidence-remediation-plan.html",
    }
    workspace.write_view(paths["markdown"], render_markdown(plan))
    workspace.write_view(paths["json"], render_json(plan))
    workspace.write_view(paths["html"], render_html(plan))
    return {key: str(path) for key, path in paths.items()}

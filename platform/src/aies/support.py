"""Subject-support discovery from one versioned registry.

The registry is descriptive and cannot create assessment support. A subject is
implemented only when the registry names an executable profile and entry point.
"""

from __future__ import annotations

from copy import deepcopy

import yaml

from . import resources


class SupportError(ValueError):
    pass


VALID_STATUSES = ("implemented", "experimental", "planned")
REQUIRED_SUBJECTS = {
    "ai-deployment", "repository", "human", "team", "human-ai-pair",
    "ai-agent", "agent-swarm", "mcp-server", "coding-assistant",
    "prompt-library", "rag-system", "ai-pipeline", "ai-platform",
    "composite-system",
}


def load_registry() -> dict:
    path = resources.data_root() / "subject-support-v1.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SupportError(f"cannot load subject support registry: {exc}") from exc
    errors = validate(data)
    if errors:
        raise SupportError("; ".join(errors))
    return deepcopy(data)


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["registry must be a mapping"]
    if data.get("kind") != "aies-subject-support-registry":
        errors.append("kind must be aies-subject-support-registry")
    if data.get("schema") != 1:
        errors.append("schema must be 1")
    subjects = data.get("subjects")
    if not isinstance(subjects, list):
        return errors + ["subjects must be a list"]
    seen: set[str] = set()
    for index, subject in enumerate(subjects):
        where = f"subjects[{index}]"
        if not isinstance(subject, dict):
            errors.append(f"{where} must be a mapping")
            continue
        subject_id = subject.get("id")
        if not isinstance(subject_id, str) or not subject_id:
            errors.append(f"{where}.id is required")
        elif subject_id in seen:
            errors.append(f"duplicate subject id {subject_id}")
        else:
            seen.add(subject_id)
        if not subject.get("title"):
            errors.append(f"{where}.title is required")
        if not subject.get("descriptor_kind"):
            errors.append(f"{where}.descriptor_kind is required")
        if subject.get("status") not in VALID_STATUSES:
            errors.append(
                f"{where}.status must be one of {', '.join(VALID_STATUSES)}")
        if subject.get("status") == "implemented":
            for field in ("assessment_profiles", "executors", "instruments",
                          "decision_products", "entry_points", "limitations"):
                if not subject.get(field):
                    errors.append(
                        f"{where}.{field} is required for implemented support")
    missing = sorted(REQUIRED_SUBJECTS - seen)
    if missing:
        errors.append("missing envisioned subject kinds: " + ", ".join(missing))
    return errors


def describe(subject_id: str | None = None, *,
             status: str | None = None) -> dict:
    registry = load_registry()
    if status and status not in VALID_STATUSES:
        raise SupportError(
            f"unknown support status {status!r}; choose "
            + ", ".join(VALID_STATUSES))
    subjects = registry["subjects"]
    if subject_id:
        needle = subject_id.casefold()
        matches = [
            subject for subject in subjects
            if subject["id"].casefold() == needle
            or needle in {alias.casefold()
                          for alias in subject.get("aliases", [])}
        ]
        if not matches:
            raise SupportError(
                f"unknown subject kind {subject_id!r}; run `aies support` "
                "to see implemented, experimental, and planned support")
        subjects = matches
    if status:
        subjects = [subject for subject in subjects
                    if subject["status"] == status]
    counts = {
        value: sum(subject["status"] == value
                   for subject in registry["subjects"])
        for value in VALID_STATUSES
    }
    return {
        "kind": registry["kind"],
        "schema": registry["schema"],
        "version": registry["version"],
        "status": registry["status"],
        "governed_by": registry["governed_by"],
        "support_definitions": registry["statuses"],
        "counts": counts,
        "subjects": deepcopy(subjects),
        "claim_boundary": (
            "Only entries marked implemented have a shipped assessment path. "
            "Experimental contracts and planned architecture are not support claims."
        ),
    }


def render(result: dict) -> str:
    if len(result["subjects"]) == 1:
        subject = result["subjects"][0]
        lines = [
            f"{subject['id']} — {subject['title']}",
            f"Support status: {subject['status']}",
            f"Subject Descriptor kind: {subject['descriptor_kind']} "
            f"({subject.get('descriptor_contract', 'planned')})",
            "",
        ]
        sections = (
            ("Assessment profiles", "assessment_profiles"),
            ("Executors", "executors"),
            ("Evidence adapters", "evidence_adapters"),
        )
        for title, field in sections:
            lines.append(title + ":")
            items = subject.get(field, [])
            if not items:
                lines.append("  - not implemented")
            for item in items:
                lines.append(
                    f"  - {item['id']} — {item['title']} [{item['status']}]")
        for title, field in (
            ("Instruments", "instruments"),
            ("Decision products", "decision_products"),
            ("Entry points", "entry_points"),
            ("Limitations", "limitations"),
        ):
            lines.append(title + ":")
            values = subject.get(field, [])
            lines.extend(f"  - {value}" for value in values)
            if not values:
                lines.append("  - none; support is not implemented")
        lines.extend(["", result["claim_boundary"]])
        return "\n".join(lines)

    lines = [
        "AIES SUBJECT SUPPORT",
        "Implemented means executable now; experimental and planned do not "
        "claim assessment support.",
        "",
    ]
    for subject in result["subjects"]:
        profiles = ", ".join(
            item["title"] for item in subject.get("assessment_profiles", [])
            if item.get("status") == "implemented") or "not implemented"
        label = f"{subject['id']} — {subject['title']}"
        lines.append(label)
        lines.append(
            f"  status: {subject['status']} · assessment path: {profiles}")
    counts = result["counts"]
    lines.extend([
        "",
        "Registry: "
        f"{counts['implemented']} implemented · "
        f"{counts['experimental']} experimental · "
        f"{counts['planned']} planned",
        result["claim_boundary"],
    ])
    return "\n".join(lines)


def render_markdown(result: dict | None = None) -> str:
    result = result or describe()
    lines = [
        "# AIES Subject Support Matrix",
        "",
        "> Generated from `subject-support-v1.yaml`. Do not edit this matrix "
        "manually.",
        "",
        "**Implemented** means an executable assessment path ships now. "
        "**Experimental** and **planned** entries are not support claims.",
        "",
        "| Subject kind | Descriptor kind | Status | Implemented assessment path | Entry point |",
        "|---|---|---|---|---|",
    ]
    for subject in result["subjects"]:
        profiles = "<br>".join(
            item["title"] for item in subject.get("assessment_profiles", [])
            if item.get("status") == "implemented") or "—"
        entry = "<br>".join(
            f"`{value}`" for value in subject.get("entry_points", [])) or "—"
        lines.append(
            f"| `{subject['id']}` — {subject['title']} | "
            f"`{subject['descriptor_kind']}` | "
            f"{subject['status']} | {profiles} | {entry} |")
    lines.extend([
        "",
        "## Implemented details",
        "",
    ])
    for subject in result["subjects"]:
        if subject["status"] != "implemented":
            continue
        lines.extend([
            f"### `{subject['id']}` — {subject['title']}",
            "",
            "**Executor:** " + "; ".join(
                f"`{item['id']}` — {item['title']} ({item['status']})"
                for item in subject["executors"]) + ".",
            "",
            "**Evidence adapters:** " + (
                "; ".join(
                    f"`{item['id']}` — {item['title']} ({item['status']})"
                    for item in subject.get("evidence_adapters", []))
                or "None") + ".",
            "",
            "**Decision products:** "
            + "; ".join(subject["decision_products"]) + ".",
            "",
            "**Limitations:**",
            "",
        ])
        lines.extend(f"- {value}" for value in subject["limitations"])
        lines.append("")
    lines.extend([
        "## Claim boundary",
        "",
        result["claim_boundary"],
        "",
        "Architecture intent for a subject becomes implemented support only "
        "after a Subject Assessment Profile, executor or admitted evidence "
        "adapter, direct instruments, limitations, decision products, and "
        "discovery entry are executable and validated.",
        "",
    ])
    return "\n".join(lines)

"""Human- and machine-readable inventory of independently versioned contracts."""

from __future__ import annotations

from . import __version__, constants


def inventory() -> dict:
    # Import here to keep package initialization acyclic.
    from . import decision, ecm, evidence_events, report_view, subjects

    return {
        "kind": "aies-version-inventory",
        "schema_version": 1,
        "standard": {
            "version": decision.AIES_STANDARD_VERSION,
            "meaning": "version of the governed AIES standards corpus",
        },
        "platform": {
            "distribution": "aies-platform",
            "version": __version__,
            "meaning": "version of the executable reference implementation",
        },
        "artifact_contracts": {
            "evidence_package": constants.EVIDENCE_SCHEMA,
            "assessment_result": decision.RESULT_SCHEMA,
            "engineering_capability_matrix": ecm.ECM_SCHEMA,
            "run_report_view": report_view.SCHEMA_VERSION,
            "subject_descriptor": subjects.SUBJECT_SCHEMA,
            "run_manifest": subjects.RUN_MANIFEST_SCHEMA,
            "evidence_event": evidence_events.EVENT_SCHEMA,
        },
        "compatibility": (
            "These axes evolve independently. A platform version does not imply "
            "a standards status, and a schema version is not a capability claim."),
    }


def render_text(value: dict) -> str:
    contracts = value["artifact_contracts"]
    lines = [
        "AIES version inventory",
        f"  Standard: {value['standard']['version']} — governed content",
        f"  Platform: {value['platform']['version']} — aies-platform software",
        "  Artifact contracts:",
    ]
    lines.extend(f"    {name.replace('_', ' ')}: {version}"
                 for name, version in contracts.items())
    lines.extend(["", value["compatibility"]])
    return "\n".join(lines)

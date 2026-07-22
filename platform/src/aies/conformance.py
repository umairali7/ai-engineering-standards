"""Conformance claims (Task #7) — declaring and checking conformance to AIES.

A standard is only a standard if others can conform to it in a defined,
checkable way. This module implements the conformance model of
docs/CONFORMANCE.md (AIES-DOC-08):

- Two conformance CLASSES: `implementation` (a tool implements AESQS) and
  `adopter` (an organization qualifies its deployments per AIES).
- Three ASSURANCE levels: self-asserted, evidence-backed,
  independently-reviewed.

Honesty boundary: the checker verifies the *structure* of a statement and,
for evidence-backed claims, that the referenced Qualification Records
exist and are live grants. It does NOT verify the truth of the underlying
qualification, nor the independence of a named reviewer — those are human
judgments the statement records, not things a tool can certify.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml

from . import qualification, workspace

CLASSES = ("implementation", "adopter")
ASSURANCE = ("self-asserted", "evidence-backed", "independently-reviewed")

# Normative requirements the reference implementation enforces, mapped to
# where it enforces them — the traceability that underpins an
# `implementation`-class conformance claim (`aies conform requirements`).
ENFORCED_REQUIREMENTS = {
    "AIES-AESQS-ER-01-R04": "scoring.score_dimension — integer 0–4 rubric anchors, no half points",
    "AIES-AESQS-CS-01-R02/R11": "scoring.confidence_interval — decision value = lower 90% CI bound",
    "AIES-AESQS-CS-01-R03": "scoring.effective_weights — profile adjustment bound and EV3+EV6 floor",
    "AIES-AESQS-CS-01-R04": "scoring.apply_gates — EV3 hard gate; single-zero fail at RT3 — Significant through RT4 — Critical",
    "AIES-AESQS-CS-01-R07": "scoring.derive_cl — AI systems capped at CL3",
    "AIES-AESQS-CS-01-R08/R09": "scoring.al_envelope — min(RT cap, CL cap); AL4 never at initial grant",
    "AIES-AESQS-CS-01-§6": "scoring.score_area — per-tier decisional sample minimums (20/30/50/100)",
    "AIES-AESQS-QP-01-R01": "qualification.record_decision — two named humans required to grant",
    "AIES-AESQS-PR-01-R09": "review.reviewer_admitted — model review advisory unless qualified/calibrated",
    "AIES-AESQS-RR-01-R16": "workspace.write_json — append-only evidence records",
    "PLATFORM.md-D7": "qualification.verify — environment-change re-qualification trigger",
    "PLATFORM.md-D8": "qualification.record_decision — platform prepares evidence; a human grants",
}


class ConformanceError(Exception):
    pass


def template(cls: str = "adopter") -> dict:
    from . import __version__  # noqa: F401 (version of the tool, not the standard)
    return {
        "conformance_statement": {
            "claimant": "<organization or person making this claim>",
            "aies_version": "v0.4.0",
            "class": cls,
            "assurance": "evidence-backed",
            "reviewer": "<required only for independently-reviewed>",
            "date": "<YYYY-MM-DD>",
            "claims": [
                {"statement": "Deployment <id> is qualified for CA-05 at RT2 — Moderate (AL2 — Collaborative).",
                 "evidence": {"qualification_record": "QUAL-2026-001"}},
                {"statement": "Human approval gates operate per AIES-AEOS-HO-01.",
                 "evidence": {}},
            ],
        }
    }


def _check_claim(claim: dict) -> dict:
    stmt = claim.get("statement")
    if not stmt:
        return {"statement": "(missing)", "verdict": "invalid",
                "detail": "claim has no statement"}
    ev = claim.get("evidence") or {}
    rec_id = ev.get("qualification_record")
    if not rec_id:
        return {"statement": stmt, "verdict": "self-asserted",
                "detail": "no evidence attached; not tool-verifiable"}
    try:
        rec = qualification.get_record(rec_id)
    except qualification.QualificationError:
        return {"statement": stmt, "verdict": "unsupported",
                "detail": f"qualification record {rec_id} not found in this workspace"}
    if rec["status"] not in ("active", "conditional"):
        return {"statement": stmt, "verdict": "unsupported",
                "detail": f"{rec_id} exists but its status is {rec['status']!r}, "
                          "not a live grant"}
    scope = rec.get("scope", {})
    return {"statement": stmt, "verdict": "verified",
            "detail": f"{rec_id} is a live grant ({rec['decision']}, {rec['status']})",
            "record_scope": {"deployment": rec["subject"]["deployment"],
                             "risk_tier": scope.get("risk_tier"),
                             "areas": {a: d.get("cl") for a, d in scope.get("areas", {}).items()}}}


def check(statement_path: Path) -> dict:
    data = yaml.safe_load(Path(statement_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "conformance_statement" not in data:
        raise ConformanceError("file must contain a top-level `conformance_statement`")
    s = data["conformance_statement"]
    problems = []
    if not s.get("claimant"):
        problems.append("missing claimant")
    if s.get("class") not in CLASSES:
        problems.append(f"class must be one of {CLASSES}")
    if s.get("assurance") not in ASSURANCE:
        problems.append(f"assurance must be one of {ASSURANCE}")
    if s.get("assurance") == "independently-reviewed" and not s.get("reviewer"):
        problems.append("independently-reviewed statements require a named reviewer")
    if not s.get("aies_version"):
        problems.append("missing aies_version (the standard version claimed against)")
    claims = s.get("claims") or []
    if not claims:
        problems.append("statement has no claims")
    if problems:
        raise ConformanceError("invalid conformance statement:\n  - " + "\n  - ".join(problems))

    checked = [_check_claim(c) for c in claims]
    verified = sum(1 for c in checked if c["verdict"] == "verified")
    unsupported = [c for c in checked if c["verdict"] in ("unsupported", "invalid")]
    self_asserted = sum(1 for c in checked if c["verdict"] == "self-asserted")

    # An evidence-backed statement is substantiated only if every evidence-
    # bearing claim verified and none are unsupported. Self-asserted claims
    # are allowed but do not count as substantiation.
    if s["assurance"] == "self-asserted":
        substantiated = not unsupported
        note = "self-asserted: no claim is tool-verified; taken on the claimant's word"
    else:
        substantiated = not unsupported and verified > 0
        note = ("evidence-backed: substantiation requires every evidence-bearing "
                "claim to reference a live Qualification Record in this workspace")
        if s["assurance"] == "independently-reviewed":
            note += (f". Reviewer {s.get('reviewer')!r} is recorded but the tool "
                     "cannot verify their independence — that is a human attestation.")
    return {
        "kind": "conformance-check",
        "claimant": s["claimant"],
        "aies_version": s["aies_version"],
        "class": s["class"],
        "assurance": s["assurance"],
        "reviewer": s.get("reviewer"),
        "claims": checked,
        "summary": {"total": len(checked), "verified": verified,
                    "self_asserted": self_asserted, "unsupported": len(unsupported),
                    "substantiated": substantiated, "note": note},
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def render_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [f"# AIES Conformance Check — {report['claimant']}", "",
             f"**Class:** {report['class']}  ·  **Assurance:** {report['assurance']}  ·  "
             f"**Claimed against:** {report['aies_version']}", ""]
    if report.get("reviewer"):
        lines.append(f"**Reviewer:** {report['reviewer']}")
        lines.append("")
    lines.append(f"> **{'SUBSTANTIATED' if s['substantiated'] else 'NOT SUBSTANTIATED'}** — "
                 f"{s['verified']} verified, {s['self_asserted']} self-asserted, "
                 f"{s['unsupported']} unsupported of {s['total']} claims.")
    lines.append("")
    lines.append(f"_{s['note']}_")
    lines.append("")
    lines.append("| Verdict | Claim | Detail |")
    lines.append("|---|---|---|")
    mark = {"verified": "verified", "self-asserted": "self-asserted",
            "unsupported": "**UNSUPPORTED**", "invalid": "**INVALID**"}
    for c in report["claims"]:
        lines.append(f"| {mark.get(c['verdict'], c['verdict'])} | {c['statement']} | {c['detail']} |")
    lines.append("")
    lines.append("---")
    lines.append("A conformance check verifies statement structure and that "
                 "evidence-backed claims reference live Qualification Records. It does "
                 "not certify the truth of a qualification or a reviewer's independence "
                 "(docs/CONFORMANCE.md, AIES-DOC-08).")
    lines.append("")
    return "\n".join(lines)


def write_report(report: dict) -> str:
    d = workspace.ensure() / "reports"
    d.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in report["claimant"])[:40]
    path = d / f"conformance-{safe}.md"
    path.write_text(render_markdown(report), encoding="utf-8")
    return str(path)

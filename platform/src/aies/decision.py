"""Assessment Decision Engine (ADR-0005 D-B4) — FROZEN, engine-owned.

Consumes an aggregated **evidence package** and an **assessment definition** and
produces the **Canonical Assessment Result**: the outcome, structured reasons,
diagnostics, and analytics. It reads only the evidence and the assessment — no
inference — so a run **re-decides without re-collecting** (the same property
`aies qualify --resume` already relies on).

This module OWNS, and assessment authors never redefine:
  - outcome precedence (FAIL > INCONCLUSIVE > INSUFFICIENT EVIDENCE > PASS)
  - mandatory vs advisory semantics (only mandatory competencies decide)
  - gate evaluation and min-CL enforcement
  - the reason-kind vocabulary

Only the **normative** layer (per-mandatory PASS/FAIL + overall outcome) is
authoritative. Diagnostic numbers and informational analytics never decide.
"""

from __future__ import annotations

import datetime

from . import __version__, constants as C, workspace

OUTCOMES = ("PASS", "FAIL", "INCONCLUSIVE", "INSUFFICIENT EVIDENCE")
_SEVERITY = {"FAIL": 3, "INCONCLUSIVE": 2, "INSUFFICIENT EVIDENCE": 1, "PASS": 0}
_CL_RANK = {"CL1": 1, "CL2": 2, "CL3": 3, "CL4": 4}
REASON_KINDS = ("mandatory-gate", "min-cl", "min-confidence",
                "insufficient-evidence", "assessment-error")
AIES_STANDARD_VERSION = "v0.4.0"

# --- Versioned artifact envelope (STABILITY/COMPATIBILITY) --------------------
# The Canonical Assessment Result is a platform-owned contract; this stamps the
# shape so consumers can detect envelope changes. Field-append-only: bump only
# on a breaking shape change (see COMPATIBILITY.md).
RESULT_SCHEMA = 1

# Engine version vs semantics version are DIFFERENT questions (ADR-0005;
# normative in AESQS AIES-AESQS-CS-01 §8, R18-R21):
#   decision_engine_version   — which software decided (platform build)
#   decision_semantics_version — which normative AESQS decision policy was applied
# A platform build can change (bugfix) without changing semantics; AESQS can
# intentionally change decision policy without a mere rebuild. Never conflate.
# This engine implements AESQS decision-semantics version 1.0.
DECISION_SEMANTICS_VERSION = "1.0"


class DecisionError(Exception):
    pass


def _competency_outcome(area: str, comp: dict, areas_pkg: dict):
    """Return (outcome, reason|None) for one competency. Engine-owned rules."""
    d = areas_pkg.get(area)
    if d is None:
        return "INCONCLUSIVE", {"kind": "assessment-error",
                                "detail": f"{area} was not scored in this run"}
    if not d.get("decisional"):
        return "INSUFFICIENT EVIDENCE", {"kind": "insufficient-evidence",
                "detail": f"{d.get('n_scored')}/{d.get('min_sample')} scored items"}
    if d.get("ev3_hard_fail") or not d.get("gates_passed", True):
        failed = [g["dimension"] for g in d.get("gates", []) if not g.get("passed")]
        return "FAIL", {"kind": "mandatory-gate",
                        "detail": f"gate(s) failed: {', '.join(failed) or 'EV3'}"}
    min_cl = comp.get("min_cl")
    if min_cl and _CL_RANK.get(d.get("cl"), 0) < _CL_RANK.get(min_cl, 0):
        return "FAIL", {"kind": "min-cl",
                        "detail": f"{d.get('cl') or 'below CL1'} < required {min_cl}"}
    return "PASS", None


def decide(package: dict, assessment: dict) -> dict:
    """Pure function: (evidence package, assessment) -> Canonical Assessment Result."""
    areas_pkg = package.get("areas", {})
    comps = assessment.get("competencies", [])

    comp_results, reasons = [], []
    for comp in comps:
        area, req = comp["area"], comp.get("requirement", "mandatory")
        outcome, reason = _competency_outcome(area, comp, areas_pkg)
        d = areas_pkg.get(area, {})
        comp_results.append({
            "area": area, "requirement": req, "weight": comp.get("weight"),
            "min_cl": comp.get("min_cl"), "outcome": outcome,
            "cl": d.get("cl"), "decisional": d.get("decisional"),
        })
        if reason and req == "mandatory":          # only mandatory reasons block
            reasons.append({"area": area, **reason})

    mandatory = [c for c in comp_results if c["requirement"] == "mandatory"]
    overall = "PASS"
    if mandatory:
        overall = max((c["outcome"] for c in mandatory), key=lambda o: _SEVERITY[o])

    diagnostics = {area: {"aggregate": d.get("aggregate_A"), "cl": d.get("cl"),
                          "decisional": d.get("decisional")}
                   for area, d in areas_pkg.items()}

    n = len(comp_results)
    n_decisional = sum(1 for c in comp_results if c["decisional"])
    mand_pass = sum(1 for c in mandatory if c["outcome"] == "PASS")
    analytics = {
        "coverage": round(n_decisional / n, 3) if n else None,
        "mandatory_pass_rate": round(mand_pass / len(mandatory), 3) if mandatory else None,
        "note": "informational only — NOT the assessment result",
    }

    return {
        "kind": "assessment-result",
        "result_schema": RESULT_SCHEMA,
        "outcome": overall,
        "assessment": {"id": assessment.get("id"), "version": assessment.get("version"),
                       "schema": assessment.get("schema"), "profile": assessment.get("profile")},
        "subject": package.get("model", {}).get("registry_id"),
        "risk_tier": package.get("risk_tier"),
        "metadata": _metadata(package, assessment),
        "evidence": {area: {"decisional": d.get("decisional"), "n_scored": d.get("n_scored"),
                            "min_sample": d.get("min_sample"),
                            "gates_passed": d.get("gates_passed"),
                            "ev3_hard_fail": d.get("ev3_hard_fail")}
                     for area, d in areas_pkg.items()},
        "decisions": {"overall": overall, "competencies": comp_results, "reasons": reasons},
        "diagnostics": diagnostics,
        "analytics": analytics,
    }


def _metadata(package: dict, assessment: dict) -> dict:
    """Immutable execution metadata — reproducibility and drift explanation."""
    fp = package.get("environment_fingerprint", {})
    model = package.get("model", {})
    return {
        "assessment_id": assessment.get("id"),
        "assessment_version": assessment.get("version"),
        "assessment_schema": assessment.get("schema"),
        "profile": assessment.get("profile"),
        # The profile version as CAPTURED at run time (from the evidence
        # package), not re-read from disk — a later profile edit cannot rewrite
        # a past decision. UNVERSIONED if the run predates profile versioning.
        "profile_version": package.get("profile_version", "0.0.0"),
        "platform_version": __version__,
        # Engine (software that decided) vs semantics (which AESQS policy) — see
        # the module constants. Recorded so a re-decision under a new engine or a
        # new semantics version is a distinguishable, traceable event.
        "decision_engine_version": __version__,
        "decision_semantics_version": DECISION_SEMANTICS_VERSION,
        "aies_version": AIES_STANDARD_VERSION,
        # The evidence-package schema this result was decided over (the result
        # references the evidence artifact's version — replayability).
        "evidence_schema": package.get("evidence_schema"),
        "model": model.get("registry_id"),
        "model_checksum": model.get("checksum"),
        "runtime": (fp.get("runtime") or {}).get("id"),
        "environment_fingerprint": fp.get("fingerprint_hash"),
        "suite_versions": package.get("suite_versions"),
        "run_id": package.get("run_id"),
        "aggregated_at": package.get("aggregated_at"),
        "decided_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def assess_run(run_id: str) -> dict:
    """Decide the assessment outcome for an aggregated run (reads the evidence
    package + the run's recorded assessment; performs no inference). Persists and
    returns the Canonical Assessment Result."""
    rdir = workspace.run_dir(run_id)
    pkg_path = rdir / "evidence-package.json"
    if not pkg_path.exists():
        raise DecisionError(f"run {run_id!r} has no evidence package — "
                            f"aggregate it first (aies qualify --resume {run_id})")
    manifest = workspace.read_json(rdir / "manifest.json")
    assessment = manifest.get("assessment")
    if not assessment:
        raise DecisionError(f"run {run_id!r} was not run under an assessment "
                            "(use qualify --assessment <name>)")
    result = decide(workspace.read_json(pkg_path), assessment)
    workspace.write_json(rdir / "assessment-result.json", result, overwrite=True)
    return result


# --- Renderer (a VIEW of the canonical result; performs no decision) ----------
def render_markdown(result: dict) -> str:
    m = result["metadata"]
    dec = result["decisions"]
    out = [f"# Assessment Result — {result['assessment']['id']} "
           f"v{result['assessment']['version']}", ""]
    out.append(f"## {result['outcome']}")
    out.append("")
    out.append(f"**Subject:** `{result['subject']}` · **Risk tier:** "
               f"{C.risk_tier_label(result['risk_tier'])} · **Profile:** {result['assessment']['profile']}")
    out.append("")
    out.append("_The outcome is authoritative (conformity). The diagnostic and "
               "analytics sections below are informational and do not decide._")
    out.append("")

    # Layer 1 — Normative
    out += ["## 1. Normative (authoritative)", "",
            "| Competency | Requirement | Outcome |", "|---|---|---|"]
    for c in dec["competencies"]:
        out.append(f"| {c['area']} | {c['requirement']} | **{c['outcome']}** |")
    out.append("")
    out.append(f"**Overall outcome: {dec['overall']}** — decided over the "
               "mandatory competencies (advisory competencies never fail an "
               "assessment).")
    out.append("")
    if dec["reasons"]:
        out += ["### Reasons", ""]
        for r in dec["reasons"]:
            out.append(f"- **{r['area']}** — `{r['kind']}`: {r['detail']}")
        out.append("")

    # Layer 2 — Diagnostic
    out += ["## 2. Diagnostic (informational — engineering feedback)", "",
            "| Area | Aggregate | CL | Decisional |", "|---|---|---|---|"]
    for area, d in result["diagnostics"].items():
        out.append(f"| {area} | {d.get('aggregate') if d.get('aggregate') is not None else '-'} "
                   f"| {d.get('cl') or '-'} | {'yes' if d.get('decisional') else 'no'} |")
    out.append("")

    # Layer 3 — Informational analytics
    a = result["analytics"]
    out += ["## 3. Analytics (non-authoritative)", "",
            f"- coverage: {a.get('coverage')}",
            f"- mandatory pass rate: {a.get('mandatory_pass_rate')}",
            f"- _{a.get('note')}_", ""]

    out += ["## Execution metadata (immutable)", "",
            f"assessment `{m['assessment_id']}` v{m['assessment_version']} "
            f"(schema {m['assessment_schema']}) · profile {m['profile']} "
            f"v{m.get('profile_version', '0.0.0')} · "
            f"platform {m['platform_version']} · AIES {m['aies_version']}  ",
            f"model `{m['model']}` ({m['model_checksum']}) · runtime {m['runtime']} · "
            f"fingerprint `{m['environment_fingerprint']}`  ",
            f"run `{m['run_id']}` · aggregated {m['aggregated_at']} · decided {m['decided_at']}",
            "",
            "---",
            "*The platform prepares evidence and decides conformity to the "
            "assessment; a named human records any grant/certification (D8). "
            "PASS is an assessment outcome, not a deployment-readiness decision.*"]
    return "\n".join(out)


def render_html(result: dict) -> str:
    """Presentation-grade HTML view of the SAME Canonical Assessment Result —
    a rendering, never a decision (ADR-0005 D-B4: renderers are views). Single
    self-contained file (inline CSS, no external requests), theme-aware,
    print-ready. The outcome shown here is verbatim from the frozen engine."""
    from .report_html import _CSS, _esc

    m = result["metadata"]
    dec = result["decisions"]
    a = result["assessment"]
    outcome = result["outcome"]
    cls = "pass" if outcome == "PASS" else "fail"
    p: list[str] = []
    w = p.append

    w("<!doctype html><html lang=en><head><meta charset=utf-8>")
    w("<meta name=viewport content='width=device-width, initial-scale=1'>")
    w(f"<title>AIES Assessment Result — {_esc(a['id'])} v{_esc(a['version'])}</title>")
    w(f"<style>{_CSS}</style></head><body>")

    w(f"<h1>AIES Assessment Result &mdash; {_esc(a['id'])} "
      f"<span class=muted>v{_esc(a['version'])}</span></h1>")
    w(f"<div class='banner grant'><span class={cls}>{_esc(outcome)}</span></div>")
    w(f"<p><strong>Subject:</strong> <code>{_esc(result['subject'])}</code> "
      f"&middot; <strong>Risk tier:</strong> {_esc(C.risk_tier_label(result['risk_tier']))} "
      f"&middot; <strong>Profile:</strong> {_esc(a['profile'])}</p>")
    w("<p class=muted>The outcome is authoritative (conformity). The diagnostic "
      "and analytics sections below are informational and do not decide.</p>")

    # Layer 1 — Normative
    w("<h2>1. Normative (authoritative)</h2>")
    w("<table><tr><th>Competency</th><th>Requirement</th><th>Outcome</th></tr>")
    for c in dec["competencies"]:
        oc = "pass" if c["outcome"] == "PASS" else "fail"
        w(f"<tr><td>{_esc(c['area'])}</td><td>{_esc(c['requirement'])}</td>"
          f"<td class={oc}>{_esc(c['outcome'])}</td></tr>")
    w("</table>")
    ov = "pass" if dec["overall"] == "PASS" else "fail"
    w(f"<p><strong>Overall outcome: <span class={ov}>{_esc(dec['overall'])}</span></strong> "
      "&mdash; decided over the mandatory competencies (advisory competencies "
      "never fail an assessment).</p>")
    if dec["reasons"]:
        w("<h3>Reasons</h3><ul>")
        for r in dec["reasons"]:
            w(f"<li><strong>{_esc(r['area'])}</strong> &mdash; "
              f"<code>{_esc(r['kind'])}</code>: {_esc(r['detail'])}</li>")
        w("</ul>")

    # Layer 2 — Diagnostic
    w("<h2>2. Diagnostic <span class=muted>(informational — engineering feedback)</span></h2>")
    w("<table><tr><th>Area</th><th>Aggregate</th><th>CL</th><th>Decisional</th></tr>")
    for area, d in result["diagnostics"].items():
        agg = d.get("aggregate")
        w(f"<tr><td>{_esc(area)}</td><td>{_esc(agg) if agg is not None else '-'}</td>"
          f"<td>{_esc(d.get('cl') or '-')}</td>"
          f"<td>{'yes' if d.get('decisional') else 'no'}</td></tr>")
    w("</table>")

    # Layer 3 — Analytics
    an = result["analytics"]
    w("<h2>3. Analytics <span class=muted>(non-authoritative)</span></h2>")
    w(f"<ul><li>coverage: {_esc(an.get('coverage'))}</li>"
      f"<li>mandatory pass rate: {_esc(an.get('mandatory_pass_rate'))}</li>"
      f"<li class=muted>{_esc(an.get('note'))}</li></ul>")

    # Execution metadata
    w("<h2>Execution metadata <span class=muted>(immutable)</span></h2>")
    w("<table class=env>")
    for label, val in (
        ("assessment", f"{m['assessment_id']} v{m['assessment_version']} (schema {m['assessment_schema']})"),
        ("profile", f"{m['profile']} v{m.get('profile_version', '0.0.0')}"),
        ("platform / AIES", f"{m['platform_version']} / {m['aies_version']}"),
        ("model", f"{m['model']} ({m['model_checksum']})"),
        ("runtime", m["runtime"]),
        ("fingerprint", m["environment_fingerprint"]),
        ("run", m["run_id"]),
        ("aggregated / decided", f"{m['aggregated_at']} / {m['decided_at']}"),
    ):
        w(f"<tr><td>{_esc(label)}</td><td><code>{_esc(val)}</code></td></tr>")
    w("</table>")

    w("<footer>The platform prepares evidence and decides conformity to the "
      "assessment; a named human records any grant/certification (D8). "
      "PASS is an assessment outcome, not a deployment-readiness decision.</footer>")
    w("</body></html>")
    return "".join(p)

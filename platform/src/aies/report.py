"""Report generator for engineering evaluation and formal qualification views.

New runs declare their purpose. Engineering evaluation is non-blocking and
human evaluation is optional; formal qualification retains its governed
admission, decision, and grant-readiness semantics.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from . import constants as C
from . import workspace


def _area_verdict(d: dict) -> tuple[str, str]:
    """Grant-readiness verdict for one area (informs a human decision; the
    platform never grants)."""
    protocol = d.get("rater_protocol") or {}
    if protocol and not protocol.get("satisfied"):
        reasons = protocol.get("reasons") or ["verified human-rater protocol incomplete"]
        return "BLOCKED", "rater protocol incomplete: " + "; ".join(reasons)
    if not d["decisional"]:
        distinct = d.get("sample_adequacy_basis") == "distinct_scenarios"
        n = d.get("n_distinct_scenarios", d["n_scored"]) if distinct else d["n_scored"]
        unit = "distinct scenarios" if distinct else "scored items"
        return "BLOCKED", f"non-decisional ({n}/{d['min_sample']} {unit})"
    if d.get("ev3_hard_fail"):
        return "BLOCKED", "EV3 safety hard gate failed"
    if not d.get("gates_passed", True):
        failed = [g["dimension"] for g in d["gates"] if not g["passed"]]
        return "BLOCKED", f"gate failure: {', '.join(failed)}"
    return "THRESHOLD MET", f"admitted evidence informs a human grant review up to {d.get('cl') or 'CL?'}"


def _gate_status(d: dict) -> str:
    """Render gate state without turning missing evidence into a failure."""
    if not d.get("n_scored") or not d.get("dimensions"):
        return "NOT EVALUATED"
    if (d.get("rater_protocol") or {}).get("satisfied") is False:
        return "NOT ADMITTED"
    return ("PASS" if d.get("gates_passed") and not d.get("ev3_hard_fail")
            else "FAIL")


def _overall_readiness(verdicts: dict[str, str]) -> tuple[str, list[str]]:
    """Summarize the factual per-area verdicts using their actual vocabulary."""
    blocked = [area for area, verdict in verdicts.items()
               if verdict != "THRESHOLD MET"]
    return ("READY" if not blocked else "BLOCKED", blocked)


def _residual_risks(pkg: dict) -> list[str]:
    risks: list[str] = []
    if (pkg.get("rating_admission") or {}).get("advisory_ratings", 0):
        risks.append("Scores are **judge-produced** — advisory until the judge is "
                     "calibrated against human anchors (AIES-AESQS-PR-01-R09).")
    for area, d in pkg["areas"].items():
        area = C.competency_label(area)
        if not d["decisional"]:
            protocol = d.get("rater_protocol") or {}
            if protocol and not protocol.get("satisfied"):
                remedy = "complete verified human-rater admission, independence, agreement, and double-rating coverage"
            else:
                basis = d.get("sample_adequacy_basis")
                remedy = ("collect more distinct scenarios; exact repeats do not repair breadth"
                          if basis == "distinct_scenarios"
                          else "collect more independently admissible evidence")
            risks.append(f"**{area}**: non-decisional — {remedy}.")
        for g in d["gates"]:
            dv, th = g.get("decision_value"), g.get("threshold")
            if g.get("passed") and dv is not None and th is not None and (dv - th) < 0.5:
                sev = " — **safety gate**" if g["dimension"] == "EV3" else ""
                risks.append(f"**{area} {g['dimension']}**: passed by a thin margin "
                             f"(decision value {dv} vs threshold {th}){sev}.")
    if not risks:
        risks.append("No elevated residual risk flagged by the platform; a named "
                     "human still owns the grant decision (D8).")
    return risks


def _score_sources(run_id: str) -> dict[str, dict[str, dict[str, list[int]]]]:
    """Return per-area, per-source EV observations for report transparency.

    The evidence aggregate remains the canonical scored result. These source
    columns make it clear whether that evidence came from an automated reviewer,
    an optional human rater, or another imported automated source.
    """
    from . import rating

    rdir = workspace.run_dir(run_id)
    response_areas = {
        p.name: workspace.read_json(p).get("area", "unknown")
        for p in (rdir / "responses").glob("*.json")
    }
    out: dict[str, dict[str, dict[str, list[int]]]] = {}
    for record in rating.collect_ratings(run_id):
        kind = (record.get("provenance") or {}).get("rater_kind", "unknown")
        source = "human" if kind == "human" else "automated"
        area = response_areas.get(record.get("rates_response"), "unknown")
        buckets = out.setdefault(area, {}).setdefault(
            source, {dimension: [] for dimension in C.DIMENSIONS})
        for dimension, score in (record.get("scores") or {}).items():
            if dimension in buckets and isinstance(score, int):
                buckets[dimension].append(score)
    return out


def _source_cell(sources: dict, source: str, dimension: str) -> str:
    values = sources.get(source, {}).get(dimension, [])
    return f"{round(mean(values), 3)} (n={len(values)})" if values else "—"


def _human_review_record(run_id: str) -> dict | None:
    """Read the optional human consideration declared through `aies review`."""
    path = workspace.run_dir(run_id) / "review-package.json"
    if not path.exists():
        return None
    return (workspace.read_json(path).get("human_consideration") or None)


def _human_evaluation_label(evaluation_summary: dict) -> str:
    record = evaluation_summary.get("human_evaluation") or {}
    if record.get("status") == "reviewed":
        return f"☑ Reviewed — {record.get('evaluator') or 'named human'}"
    return "☐ Not reviewed (optional)"


def render_json(run_id: str) -> str:
    from . import evaluation as evaluation_view, run_mode

    rdir = workspace.run_dir(run_id)
    pkg = workspace.read_json(rdir / "evidence-package.json")
    manifest = workspace.read_json(rdir / "manifest.json")
    if run_mode.is_formal(manifest):
        return json.dumps(pkg, indent=2)
    return json.dumps({
        "kind": "engineering-evaluation-report",
        "engineering_report_schema": 1,
        "run_id": run_id,
        "status": evaluation_view.summarize(run_id)["status"],
        "run_purpose": run_mode.purpose(manifest),
        "engineering_evaluation": evaluation_view.summarize(run_id),
        "formal_qualification": {"status": "not-requested"},
        "canonical_evidence": {
            "artifact": "evidence-package.json",
            "rating_observations": pkg.get("rating_observations") or {},
            "raters": pkg.get("raters") or [],
            "suite_versions": pkg.get("suite_versions") or {},
            "environment_fingerprint": pkg.get("environment_fingerprint") or {},
            "note": (
                "The canonical artifact preserves rating provenance for replay. "
                "Formal admission fields in that artifact are not an engineering-"
                "evaluation verdict."),
        },
    }, indent=2)


def render_markdown(run_id: str, *, matrix: dict | None = None) -> str:
    from . import diagnostics, evaluation as evaluation_view, run_mode

    rdir = workspace.run_dir(run_id)
    pkg = workspace.read_json(rdir / "evidence-package.json")
    manifest = workspace.read_json(rdir / "manifest.json")
    formal = run_mode.is_formal(manifest)
    fp = pkg["environment_fingerprint"]
    source_scores = _score_sources(run_id)
    human_review = _human_review_record(run_id)
    lines: list[str] = []
    a = lines.append

    a("# AIES Qualification Evidence Package" if formal
      else "# AIES Engineering Evaluation Report")
    a("")
    a(f"**Run:** `{pkg['run_id']}`  ")
    subject = pkg.get("subject") or {}
    a(f"**Subject:** `{subject.get('id', pkg['model']['registry_id'])}` "
      f"({subject.get('kind', 'ai_deployment')}; executor: "
      f"{subject.get('executor_kind', 'deployment')})  ")
    a(f"**Deployment / model evidence:** `{pkg['model']['registry_id']}` "
      f"({pkg['model']['checksum']})  ")
    a(f"**Profile:** {pkg['profile']} | **Scoped risk tier:** {C.risk_tier_label(pkg['risk_tier'])} | "
      f"**Assessment subject class:** {C.identifier_label(pkg['subject_kind'])}")
    a("")
    a(f"> **{pkg['grant_status'].upper()}**" if formal
      else f"> **ENGINEERING EVALUATION "
           f"{evaluation_view.summarize(run_id)['status'].upper()}**")
    a("")

    if formal and (pkg.get("rating_admission") or {}).get("advisory_ratings", 0):
        a("> **SCORES ARE JUDGE-PRODUCED (automated).** A judge model rated these "
          "responses; scores reflect the judge's opinion, not ground truth. "
          "Automated ratings are retained as engineering-evaluation and "
          "corroborating-review observations, but are never the sole basis of "
          "qualification evidence (AIES-AESQS-ER-01-R10; ADR-0012).")
        a("")

    nondecisional = [area for area, d in pkg["areas"].items() if not d["decisional"]]
    if formal and nondecisional:
        a("> **NON-DECISIONAL** - sample below the AESQS minimum for "
          f"{', '.join(C.competency_label(area) for area in nondecisional)} (AIES-AESQS-CS-01 §6). These results "
          "MUST NOT be presented as qualification evidence.")
        a("")

    evaluation = evaluation_view.summarize(run_id)
    a("## Engineering Evaluation")
    a("")
    a(f"**Evaluation status: {str(evaluation.get('status', 'not-scored')).upper()}**  ")
    a(f"**Human evaluation:** {_human_evaluation_label(evaluation)}")
    a("")
    a("Automated scores are sufficient to complete this informational engineering "
      "evaluation and its ECM decision products. Human evaluation is optional here; "
      "formal qualification and grants use a separate explicit protocol.")
    a("")
    a("| Area | Automated score coverage | Observed automated mean | Human eval | Evaluation status |")
    a("|---|---|---|---|---|")
    for area, evaluation_area in (evaluation.get("areas") or {}).items():
        automated = (evaluation_area.get("sources") or {}).get("automated") or {}
        mean_value = automated.get("observed_mean")
        completed_by = evaluation_area.get("completed_by")
        status = str(evaluation_area.get("status", "not-scored")).upper()
        if completed_by:
            status += f" — {completed_by}"
        a(f"| {C.competency_label(area)} | "
          f"{automated.get('responses_scored', 0)}/{automated.get('responses_total', 0)} "
          f"({automated.get('coverage_percent', 0):.1f}%) | "
          f"{mean_value if mean_value is not None else '—'} | "
          f"{_human_evaluation_label(evaluation)} | **{status}** |")
    a("")
    a(diagnostics.render_report_section_markdown(
        diagnostics.summarize(run_id)).rstrip())
    a("")

    if not formal:
        a("## Automated Score Detail")
        a("")
        a("Scores below are observed reviewer measurements. Human evaluation is "
          "optional and appears in a separate column when supplied.")
        a("")
        for area in evaluation.get("areas") or {}:
            a(f"### {C.competency_label(area)}")
            a("")
            a("| Dimension | Automated review | Human eval (optional) |")
            a("|---|---:|---:|")
            for dim in C.DIMENSIONS:
                a(f"| {C.identifier_label(dim)} | "
                  f"{_source_cell(source_scores.get(area, {}), 'automated', dim)} | "
                  f"{_source_cell(source_scores.get(area, {}), 'human', dim)} |")
            a("")
        a("## Environment Fingerprint")
        a("")
        a("| Field | Value |")
        a("|---|---|")
        for key in ("machine", "cpu", "gpu", "ram_gb", "os", "python"):
            a(f"| {key} | {fp.get(key, 'unknown')} |")
        rt_fp = fp.get("runtime", {})
        a(f"| runtime | {rt_fp.get('id', '?')} v{rt_fp.get('version', '?')} |")
        a(f"| fingerprint | `{fp.get('fingerprint_hash', 'unknown')}` |")
        a("")
        from . import ecm
        matrix = matrix or ecm.engineering_capability_matrix(run_id)
        a(ecm.render_capability_summary_markdown(matrix).rstrip())
        a("")
        a("## Optional Formal Qualification")
        a("")
        a("Formal qualification was **not requested** and therefore has no "
          "readiness verdict in this report. To intentionally apply the "
          "human-governed protocol, start the run with `--formal-qualification` "
          "or render the separate formal result explicitly.")
        a("")
        a("Decision products: [Engineering Assessment Result]"
          "(engineering-assessment-result.md) · [Engineering Capability Matrix]"
          "(engineering-capability-matrix.md) · [Engineering Fit Guidance]"
          "(engineering-fit-guidance.md) · [Executive Summary]"
          "(executive-summary.md).")
        a("")
        a("---")
        a(f"Raters: {', '.join(pkg['raters'])} | Aggregated: "
          f"{pkg['aggregated_at']} | Generated by AIES Engineering Assessment "
          "Platform (see docs/PLATFORM.md, AIES-DOC-06)")
        a("")
        return "\n".join(lines)

    # Grant-readiness summary (synthesis of the per-area detail below).
    a("## Grant Readiness (Formal Qualification)")
    a("")
    a("| Area | Decisional | Gates | CL | Verdict — informs a human grant |")
    a("|---|---|---|---|---|")
    verdicts = {}
    for area, d in pkg["areas"].items():
        v, why = _area_verdict(d)
        verdicts[area] = v
        gates = _gate_status(d)
        a(f"| {C.competency_label(area)} | {'yes' if d['decisional'] else '**no**'} | {gates} | "
          f"{d.get('cl') or '-'} | **{v}** — {why} |")
    a("")
    readiness, blocked = _overall_readiness(verdicts)
    if readiness == "READY":
        a("**Overall: READY** — every scoped area is decisional and passes its "
          "gates. A named human authority may record a grant "
          "(`aies grant <run> …`); the platform does not grant (D8).")
    else:
        a(f"**Overall: BLOCKED** — formal qualification is not grant-ready for "
          f"{', '.join(C.competency_label(area) for area in blocked)}. This does "
          "not block the completed Engineering Evaluation above.")
    a("")
    a("### Residual risk")
    a("")
    for r in _residual_risks(pkg):
        a(f"- {r}")
    a("")

    if human_review:
        advisory = human_review.get("automated_advisory_review") or {}
        evaluator = (human_review.get("human_evaluation") or {}).get("evaluator")
        a("## Optional Human Evaluation Record")
        a("")
        a("| Review input | Human record |")
        a("|---|---|")
        a(f"| Advisory automated scores | "
          f"{'considered' if advisory.get('considered') else 'not declared'} |")
        a(f"| Human evaluation | {'☑ Reviewed — ' + evaluator if evaluator else '☐ Not reviewed (optional)'} |")
        a("")
        a("This is a human review declaration over evidence; it is not a grant. "
          "Formal grants remain blocked until decisional and gate-passing evidence exists.")
        a("")

    a("## Environment Fingerprint")
    a("")
    a("| Field | Value |")
    a("|---|---|")
    for k in ("machine", "cpu", "gpu", "ram_gb", "os", "python"):
        a(f"| {k} | {fp.get(k, 'unknown')} |")
    rt_fp = fp.get("runtime", {})
    a(f"| runtime | {rt_fp.get('id', '?')} v{rt_fp.get('version', '?')} |")
    a(f"| fingerprint | `{fp.get('fingerprint_hash', 'unknown')}` |")
    a("")
    a("Evidence is bound to this fingerprint; a changed fingerprint is a "
      "re-qualification trigger (PLATFORM.md D7).")
    a("")

    for area, d in pkg["areas"].items():
        a(f"## {C.competency_label(area)} — {C.risk_tier_label(pkg['risk_tier'])}")
        a("")
        protocol = d.get("rater_protocol") or {}
        a(f"Suite version: `{pkg['suite_versions'].get(area, 'unknown')}` | "
          f"resolved evidence items: {d['n_scored']}; verified admitted observations: "
          f"{d.get('admitted_ratings', 0)}; distinct scored scenarios: "
          f"{d.get('n_distinct_scenarios', d['n_scored'])} "
          f"(adequacy minimum {d['min_sample']} by "
          f"{'distinct scenarios' if d.get('sample_adequacy_basis') == 'distinct_scenarios' else 'legacy scored items'}); "
          f"advisory automated ratings: {d.get('advisory_ratings', 0)} | "
          f"decisional: {'**yes**' if d['decisional'] else '**NO**'}")
        a("")
        if protocol:
            a(f"Rater protocol: **{'SATISFIED' if protocol.get('satisfied') else 'INCOMPLETE'}** | "
              f"verified item coverage {protocol.get('qualification_eligible_items', 0)}/"
              f"{protocol.get('total_items', 0)} | independent double-rating "
              f"{protocol.get('double_rating_fraction', 0):.1%} "
              f"(required {protocol.get('required_double_rating_fraction', 0):.0%}) | "
              f"adjacent agreement {protocol.get('agreement_fraction', 0):.1%} "
              f"(required {protocol.get('agreement_threshold', 0):.0%}).")
            for reason in protocol.get("reasons") or []:
                a(f"- Protocol gap: {reason}")
            a("")
        a("| Dimension | Automated review | Human eval (optional) | Resolved item n | Resolved item mean | 90% CI | Decision value | Gate | Result |")
        a("|---|---|---|---|---|---|---|---|---|")
        gates = {g["dimension"]: g for g in d["gates"]}
        for dim in C.DIMENSIONS:
            ds = d["dimensions"].get(dim)
            g = gates.get(dim, {})
            automated = _source_cell(source_scores.get(area, {}), "automated", dim)
            human = _source_cell(source_scores.get(area, {}), "human", dim)
            if ds:
                a(f"| {C.identifier_label(dim)} | {automated} | {human} | "
                  f"{ds['n']} | {ds['mean']} | "
                  f"[{ds['ci90_low']}, {ds['ci90_high']}] | **{ds['ci90_low']}** | "
                  f">= {g.get('threshold', '-')} | "
                  f"{'PASS' if g.get('passed') else '**FAIL**'} |")
            else:
                a(f"| {C.identifier_label(dim)} | {automated} | {human} | "
                  "0 | - | - | - | "
                  f">= {g.get('threshold', '-')} | **FAIL** (no evidence) |")
        a("")
        a("Automated-review and human-review values are displayed separately. "
          "A human score is optional for this evidence view; a named human "
          "authority is still required for any grant.")
        a("")
        for g in d["gates"]:
            if not g["passed"] and g.get("reason"):
                a(f"- FAIL **{g['dimension']}**: {g['reason']}")
        if d["ev3_hard_fail"]:
            a("- **EV3 HARD GATE FAILED** - qualification MUST be denied at "
              "this tier regardless of the aggregate (AIES-AESQS-CS-01-R04).")
        a("")
        a(f"**Aggregate A (over decision values, profile-weighted): "
          f"{d['aggregate_A'] if d['aggregate_A'] is not None else '-'}**")
        a("")
        a(f"**Score-bounded competency level:** {C.identifier_label(d['cl']) if d['cl'] else 'none'} - {d['cl_note']}")
        a("")
        a("### Recommended autonomy envelope (min of RT cap and CL-earned cap)")
        a("")
        a("| Risk tier | Recommended max AL |")
        a("|---|---|")
        for rt, al in d["al_envelope"].items():
            a(f"| **{C.risk_tier_label(rt)}** | **{C.autonomy_level_label(al)}** |")
        a("")
        a("AL4 is never recommended at initial qualification "
          "(AIES-AESQS-CS-01-R08). Recommendations inform a human decision; "
          "they are not grants.")
        a("")

    from . import ecm
    matrix = matrix or ecm.engineering_capability_matrix(run_id)
    a(ecm.render_capability_summary_markdown(matrix).rstrip())
    a("")
    a("For the standalone, engineer-facing artifact, see the "
      "[Engineering Capability Matrix](engineering-capability-matrix.md).")
    a("")
    a("Related decision products: [Executive Summary](executive-summary.md) · "
      "[Deployment Guidance](deployment-guidance.md).")
    a("")

    a("---")
    a(f"Raters: {', '.join(pkg['raters'])} | Aggregated: {pkg['aggregated_at']} | "
      f"Generated by AIES Engineering Assessment Platform (see docs/PLATFORM.md, AIES-DOC-06)")
    a("")
    return "\n".join(lines)


def write_reports(run_id: str) -> dict[str, str]:
    """Write the complete, self-contained report bundle for an evidence run.

    Every caller that aggregates evidence receives the same artifact set.  In
    particular, HTML is not an optional follow-up owned by one CLI path: it is
    part of the evidence-package presentation bundle alongside the Markdown,
    JSON, and standalone Engineering Capability Matrix (ECM) views.
    """
    from . import (decision, diagnostics, ecm, engineering_assessment, evaluation,
                   executive_summary, guidance, report_html, run_mode)

    rdir = workspace.run_dir(run_id)
    matrix = ecm.engineering_capability_matrix(run_id)
    md = render_markdown(run_id, matrix=matrix)
    workspace.write_view(rdir / "report.md", md)
    js = render_json(run_id)
    workspace.write_view(rdir / "report.json", js)
    evaluation_path = rdir / "engineering-evaluation.json"
    workspace.write_view(
        evaluation_path, json.dumps(evaluation.summarize(run_id), indent=2) + "\n")
    ecm_contents = {
        "markdown": ecm.render_markdown(matrix),
        "json": json.dumps(matrix, indent=2) + "\n",
        "html": ecm.render_html(matrix),
    }
    ecm_paths: dict[str, str] = {}
    suffixes = {"markdown": "md", "json": "json", "html": "html"}
    for format, content in ecm_contents.items():
        path = rdir / f"engineering-capability-matrix.{suffixes[format]}"
        workspace.write_view(path, content)
        ecm_paths[f"ecm_{format}"] = str(path)
    html_path = rdir / "report.html"
    workspace.write_view(html_path, report_html.render_html(run_id, matrix=matrix))

    # A declarative assessment produces its canonical outcome and three views.
    # Runs without an assessment still receive the other audience-specific
    # products; the bundle manifest records the absence explicitly.
    assessment_paths: dict[str, str] = {}
    assessment_result = None
    manifest = workspace.read_json(rdir / "manifest.json")
    if manifest.get("assessment"):
        if run_mode.is_formal(manifest):
            assessment_result = decision.assess_run(run_id)
            assessment_md = rdir / "assessment-result.md"
            assessment_html = rdir / "assessment-result.html"
            workspace.write_view(
                assessment_md, decision.render_markdown(assessment_result))
            workspace.write_view(
                assessment_html, decision.render_html(assessment_result))
            assessment_paths = {
                "assessment_markdown": str(assessment_md),
                "assessment_json": str(rdir / "assessment-result.json"),
                "assessment_html": str(assessment_html),
            }
        else:
            assessment_result, assessment_paths = (
                engineering_assessment.write_artifacts(run_id))

    # Evaluation runs receive non-authorizing Engineering Fit Guidance.
    # Explicit formal runs retain qualification-bounded Deployment Guidance.
    if run_mode.is_formal(manifest):
        guidance_paths = guidance.write_artifacts(run_id, matrix=matrix)
        guidance_result = workspace.read_json(rdir / "deployment-guidance.json")
        guidance_prefix = "guidance"
    else:
        guidance_paths = guidance.write_fit_artifacts(run_id, matrix=matrix)
        guidance_result = workspace.read_json(rdir / "engineering-fit-guidance.json")
        guidance_prefix = "fit_guidance"
    summary = executive_summary.build(
        run_id, matrix, guidance_result, assessment_result=assessment_result)
    executive_paths = {
        "executive_markdown": rdir / "executive-summary.md",
        "executive_json": rdir / "executive-summary.json",
        "executive_html": rdir / "executive-summary.html",
    }
    workspace.write_view(
        executive_paths["executive_markdown"], executive_summary.render_markdown(summary))
    workspace.write_view(
        executive_paths["executive_json"], executive_summary.render_json(summary))
    workspace.write_view(
        executive_paths["executive_html"], executive_summary.render_html(summary))

    diagnostic_summary = diagnostics.summarize(run_id)
    diagnostic_paths = {
        "diagnostics_markdown": rdir / "grounding-diagnostics.md",
        "diagnostics_json": rdir / "grounding-diagnostics.json",
        "diagnostics_html": rdir / "grounding-diagnostics.html",
    }
    workspace.write_view(
        diagnostic_paths["diagnostics_markdown"],
        diagnostics.render_markdown(diagnostic_summary))
    workspace.write_view(
        diagnostic_paths["diagnostics_json"], diagnostics.render_json(diagnostic_summary))
    workspace.write_view(
        diagnostic_paths["diagnostics_html"], diagnostics.render_html(diagnostic_summary))

    paths = {
        "markdown": str(rdir / "report.md"), "json": str(rdir / "report.json"),
        "html": str(html_path), "engineering_evaluation": str(evaluation_path),
        **ecm_paths, **assessment_paths,
        **{f"{guidance_prefix}_{format}": path
           for format, path in guidance_paths.items()},
        **{key: str(path) for key, path in executive_paths.items()},
        **{key: str(path) for key, path in diagnostic_paths.items()},
    }
    bundle = {
        "kind": "aies-report-bundle", "report_bundle_schema": 1,
        "run_id": run_id, "status": "informational-index",
        "measurement_claims": {
            "contract": "aies-measurement-claims/v1",
            "status": "draft",
            "documentation": "MEASUREMENT_CLAIMS.md",
        },
        "artifacts": {key: Path(path).name for key, path in paths.items()},
        "audience_boundaries": {
            "engineering_report": "evaluation results for engineers and reviewers",
            "assessment_result": (
                "authoritative formal outcome" if run_mode.is_formal(manifest)
                else "non-blocking engineering assessment completion"),
            "engineering_capability_matrix": "engineers",
            "guidance": (
                "qualification-bounded operations guidance"
                if run_mode.is_formal(manifest)
                else "engineering fit; no deployment authority"),
            "executive_summary": "leadership",
            "grounding_diagnostics": "source-separated informational reviewer observations",
        },
    }
    bundle_path = rdir / "report-bundle.json"
    workspace.write_view(bundle_path, json.dumps(bundle, indent=2) + "\n")
    paths["bundle_manifest"] = str(bundle_path)
    return paths

"""Report generator for engineering evaluation and formal qualification views.

New runs declare their purpose. Engineering evaluation is non-blocking and
human evaluation is optional; formal qualification retains its governed
admission, decision, and grant-readiness semantics.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import constants as C
from . import workspace


def _area_verdict(d: dict) -> tuple[str, str]:
    from .report_view import area_verdict
    return area_verdict(d)


def _gate_status(d: dict) -> str:
    from .report_view import gate_status
    return gate_status(d)


def _overall_readiness(verdicts: dict[str, str]) -> tuple[str, list[str]]:
    from .report_view import overall_readiness
    return overall_readiness(verdicts)


def _residual_risks(pkg: dict) -> list[str]:
    from .report_view import _residual_risks as residual_risks
    return [risk["message"] for risk in residual_risks(pkg)]


def _score_sources(run_id: str) -> dict[str, dict[str, dict[str, list[int]]]]:
    from .report_view import _source_observations
    return _source_observations(run_id)


def _source_cell(sources: dict, source: str, dimension: str) -> str:
    from .report_view import _source_stat, source_display
    return source_display(_source_stat(sources, source, dimension))


def _human_review_record(run_id: str) -> dict | None:
    from .report_view import _human_review
    return _human_review(run_id)


def _human_evaluation_label(evaluation_summary: dict) -> str:
    from .report_view import human_evaluation_label
    return human_evaluation_label(evaluation_summary)


def render_json(run_id: str, *, context=None) -> str:
    """Render the backward-compatible report JSON contract.

    Formal runs historically expose the Evidence Package at ``report.json``;
    engineering runs retain ``engineering_report_schema: 1``. The richer
    shared model is written separately as ``report-view.json``.
    """
    from . import report_view

    context = context or report_view.build_context(run_id)
    pkg = context.package
    view = context.view
    if view["formal_qualification_requested"]:
        return json.dumps(pkg, indent=2)
    return json.dumps({
        "kind": "engineering-evaluation-report",
        "engineering_report_schema": 1,
        "run_id": run_id,
        "status": view["status"]["engineering_evaluation"],
        "run_purpose": view["run_purpose"],
        "engineering_evaluation": view["engineering_evaluation"],
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


def render_view_json(run_id: str, *, context=None) -> str:
    from . import report_view

    context = context or report_view.build_context(run_id)
    return json.dumps(context.view, indent=2) + "\n"


def render_markdown(
    run_id: str,
    *,
    matrix: dict | None = None,
    context=None,
) -> str:
    from . import diagnostics, report_view

    context = context or report_view.build_context(run_id, matrix=matrix)
    view = context.view
    formal = view["formal_qualification_requested"]
    fp = view["environment"]
    human_review = view["human_review"]
    evaluation = view["engineering_evaluation"]
    diagnostic_summary = view["grounding_diagnostics"]
    matrix = context.matrix
    area_models = {area["code"]: area for area in view["areas"]}
    lines: list[str] = []
    a = lines.append

    a(f"# {view['title']}")
    a("")
    a(f"**Run:** `{view['run_id']}`  ")
    subject = view["subject"]
    scope = view["scope"]
    a(f"**Subject:** `{subject['id']}` "
      f"({subject['kind']}; executor: {subject['executor_kind']})  ")
    a(f"**Deployment / model evidence:** "
      f"`{subject['deployment_evidence']}` ({subject['checksum']})  ")
    a(f"**Evaluation composition:** {scope['composition']['label']}  ")
    a(f"**Weighting:** {scope['profile']} profile "
      f"({scope['profile_role']}) | **Scoped risk tier:** "
      f"{scope['risk_tier_label']} | **Assessment subject class:** "
      f"{scope['subject_kind_label']}")
    a("")
    a(f"> **{view['status']['grant_status'].upper()}**" if formal
      else f"> **ENGINEERING EVALUATION "
           f"{view['status']['engineering_evaluation'].upper()}**")
    a("")

    admission = view["qualification"]["rating_admission"]
    if formal and admission.get("advisory_ratings", 0):
        a("> **SCORES ARE JUDGE-PRODUCED (automated).** A judge model rated these "
          "responses; scores reflect the judge's opinion, not ground truth. "
          "Automated ratings are retained as engineering-evaluation and "
          "corroborating-review observations, but are never the sole basis of "
          "qualification evidence (AIES-AESQS-ER-01-R10; ADR-0012).")
        a("")

    nondecisional = view["qualification"]["nondecisional_areas"]
    if formal and nondecisional:
        a("> **NON-DECISIONAL** - sample below the AESQS minimum for "
          f"{', '.join(C.competency_label(area) for area in nondecisional)} (AIES-AESQS-CS-01 §6). These results "
          "MUST NOT be presented as qualification evidence.")
        a("")

    a("## Engineering Evaluation")
    a("")
    a(f"**Evaluation status: {str(evaluation.get('status', 'not-scored')).upper()}**  ")
    a(f"**Human evaluation:** {_human_evaluation_label(evaluation)}")
    a("")
    a("Automated scores are sufficient to complete this informational engineering "
      "evaluation and its ECM decision products. Human evaluation is optional here; "
      "formal qualification and grants use a separate explicit protocol.")
    a("")
    automated_review = evaluation.get("automated_review") or {}
    if automated_review.get("reviewer"):
        a(f"**Automated judge:** `{automated_review['reviewer']}` — "
          f"{automated_review.get('calibration_status', 'calibration unknown')}. "
          f"{automated_review.get('interpretation', '')}")
        if automated_review.get("reason"):
            a(f"Qualification admission: {automated_review['reason']}.")
        a("")
    finding_integrity = evaluation.get("finding_integrity") or {}
    if finding_integrity.get("status") == "warning":
        a("> **REVIEWER FINDING METADATA WARNING:** "
          f"{finding_integrity.get('score_inconsistencies', 0)} of "
          f"{finding_integrity.get('findings_total', 0)} written findings have "
          "dimension/score metadata that disagrees with the EV score table. "
          "The numeric EV scores are retained; do not use those finding labels "
          "for dimension-level traceability.")
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
        diagnostic_summary).rstrip())
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
            for dimension in area_models[area]["dimensions"]:
                a(f"| {dimension['label']} | "
                  f"{report_view.source_display(dimension['sources']['automated'])} | "
                  f"{report_view.source_display(dimension['sources']['human'])} |")
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
          "(executive-summary.md) · [Assessment Coverage & Blind Spots]"
          "(assessment-coverage.md) · [Evidence-Linked Remediation Plan]"
          "(evidence-remediation-plan.md) · [Standards Traceability]"
          "(standards-traceability.md).")
        a("")
        a("---")
        provenance = view["provenance"]
        a(f"Raters: {', '.join(provenance['raters'])} | Aggregated: "
          f"{provenance['aggregated_at']} | Generated by AIES Engineering Assessment "
          "Platform (see docs/PLATFORM.md, AIES-DOC-06)")
        a("")
        return "\n".join(lines)

    # Grant-readiness summary (synthesis of the per-area detail below).
    a("## Grant Readiness (Formal Qualification)")
    a("")
    a("| Area | Decisional | Gates | CL | Verdict — informs a human grant |")
    a("|---|---|---|---|---|")
    for area in view["areas"]:
        readiness = area["readiness"]
        competency = area["competency_level"]
        a(f"| {area['label']} | "
          f"{'yes' if area['evidence']['decisional'] else '**no**'} | "
          f"{readiness['gate_status']} | "
          f"{competency['label'] or '-'} | "
          f"**{readiness['verdict']}** — {readiness['reason']} |")
    a("")
    readiness = view["qualification"]["readiness"]["status"]
    blocked = view["qualification"]["readiness"]["blocked_areas"]
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
    for risk in view["qualification"]["residual_risks"]:
        a(f"- {risk['message']}")
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

    for area in view["areas"]:
        evidence = area["evidence"]
        a(f"## {area['label']} — {view['scope']['risk_tier_label']}")
        a("")
        protocol = area["rater_protocol"]
        basis = (
            "distinct scenarios"
            if evidence["adequacy_basis"] == "distinct_scenarios"
            else "legacy scored items")
        a(f"Suite version: `{area['suite_version']}` | "
          f"resolved evidence items: {evidence['resolved_items']}; "
          f"verified admitted observations: "
          f"{evidence['admitted_observations']}; distinct scored scenarios: "
          f"{evidence['distinct_scenarios']} "
          f"(adequacy minimum {evidence['minimum']} by {basis}); "
          f"advisory automated ratings: "
          f"{evidence['advisory_automated_ratings']} | "
          f"decisional: "
          f"{'**yes**' if evidence['decisional'] else '**NO**'}")
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
        for dimension in area["dimensions"]:
            resolved = dimension["resolved"]
            gate = dimension["gate"]
            automated = report_view.source_display(
                dimension["sources"]["automated"])
            human = report_view.source_display(
                dimension["sources"]["human"])
            if resolved:
                a(f"| {dimension['label']} | {automated} | {human} | "
                  f"{resolved['n']} | {resolved['mean']} | "
                  f"[{resolved['ci90_low']}, {resolved['ci90_high']}] | "
                  f"**{resolved['decision_value']}** | "
                  f">= {gate['threshold'] if gate['threshold'] is not None else '-'} | "
                  f"{'PASS' if gate['passed'] else '**FAIL**'} |")
            else:
                a(f"| {dimension['label']} | {automated} | {human} | "
                  "0 | - | - | - | "
                  f">= {gate['threshold'] if gate['threshold'] is not None else '-'} | "
                  "**FAIL** (no evidence) |")
        a("")
        a("Automated-review and human-review values are displayed separately. "
          "A human score is optional for this evidence view; a named human "
          "authority is still required for any grant.")
        a("")
        for dimension in area["dimensions"]:
            gate = dimension["gate"]
            if not gate["passed"] and gate.get("reason"):
                a(f"- FAIL **{dimension['label']}**: {gate['reason']}")
        if area["ev3_hard_fail"]:
            a("- **EV3 HARD GATE FAILED** - qualification MUST be denied at "
              "this tier regardless of the aggregate (AIES-AESQS-CS-01-R04).")
        a("")
        a(f"**Aggregate A (over decision values, profile-weighted): "
          f"{area['aggregate'] if area['aggregate'] is not None else '-'}**")
        a("")
        competency = area["competency_level"]
        a(f"**Score-bounded competency level:** "
          f"{competency['label'] or 'none'} - {competency['note']}")
        a("")
        a("### Recommended autonomy envelope (min of RT cap and CL-earned cap)")
        a("")
        a("| Risk tier | Recommended max AL |")
        a("|---|---|")
        for envelope in area["autonomy_envelope"]:
            a(f"| **{envelope['risk_tier_label']}** | "
              f"**{envelope['autonomy_level_label']}** |")
        a("")
        a("AL4 is never recommended at initial qualification "
          "(AIES-AESQS-CS-01-R08). Recommendations inform a human decision; "
          "they are not grants.")
        a("")

    from . import ecm
    a(ecm.render_capability_summary_markdown(matrix).rstrip())
    a("")
    a("For the standalone, engineer-facing artifact, see the "
      "[Engineering Capability Matrix](engineering-capability-matrix.md).")
    a("")
    a("Related decision products: [Executive Summary](executive-summary.md) · "
      "[Deployment Guidance](deployment-guidance.md) · "
      "[Assessment Coverage & Blind Spots](assessment-coverage.md) · "
      "[Evidence-Linked Remediation Plan](evidence-remediation-plan.md) · "
      "[Standards Traceability](standards-traceability.md).")
    a("")

    a("---")
    provenance = view["provenance"]
    a(f"Raters: {', '.join(provenance['raters'])} | "
      f"Aggregated: {provenance['aggregated_at']} | "
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
    from . import (assessment_coverage, decision, diagnostics, ecm,
                   engineering_assessment, executive_summary, guidance,
                   report_html, report_view, run_mode, standards_traceability)

    rdir = workspace.run_dir(run_id)
    matrix = ecm.engineering_capability_matrix(run_id)
    context = report_view.build_context(run_id, matrix=matrix)
    md = render_markdown(run_id, context=context)
    workspace.write_view(rdir / "report.md", md)
    js = render_json(run_id, context=context)
    workspace.write_view(rdir / "report.json", js)
    report_view_path = rdir / "report-view.json"
    workspace.write_view(
        report_view_path, render_view_json(run_id, context=context))
    evaluation_path = rdir / "engineering-evaluation.json"
    workspace.write_view(
        evaluation_path,
        json.dumps(context.view["engineering_evaluation"], indent=2) + "\n")
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
    workspace.write_view(
        html_path, report_html.render_html(run_id, context=context))

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

    diagnostic_summary = context.view["grounding_diagnostics"]
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

    coverage_matrix = assessment_coverage.for_run(
        run_id, capability_matrix=matrix)
    coverage_paths = assessment_coverage.write_run_artifacts(
        run_id, coverage_matrix)
    traceability_paths = standards_traceability.write_artifacts(run_id)

    paths = {
        "markdown": str(rdir / "report.md"), "json": str(rdir / "report.json"),
        "html": str(html_path), "report_view": str(report_view_path),
        "engineering_evaluation": str(evaluation_path),
        **ecm_paths, **assessment_paths,
        **{f"{guidance_prefix}_{format}": path
           for format, path in guidance_paths.items()},
        **{key: str(path) for key, path in executive_paths.items()},
        **{key: str(path) for key, path in diagnostic_paths.items()},
        **coverage_paths,
        **traceability_paths,
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
            "assessment_coverage": (
                "evidence availability, applicability, reuse, and blind spots; "
                "not subject quality"),
            "standards_traceability": (
                "standard → competency → instrument → response → rating → "
                "EV → Engineering Task lineage; informational only"),
            "evidence_remediation_plan": (
                "unassigned evidence-linked actions, monitoring links, and "
                "reassessment triggers; not risk acceptance or authorization"),
        },
    }
    bundle_path = rdir / "report-bundle.json"
    workspace.write_view(bundle_path, json.dumps(bundle, indent=2) + "\n")
    paths["bundle_manifest"] = str(bundle_path)
    return paths

"""aies — the AIES Engineering Assessment Platform CLI.

Verb dispatch and output rendering only; no qualification logic lives
here (PLATFORM.md §4). Data-producing verbs support --json where applicable.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import io
import json
import math
import os
import shlex
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from . import __version__, constants as C


def _out(data, as_json: bool, human: str | None = None) -> None:
    if as_json:
        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(data)
        print(json.dumps(data, indent=2, default=str))
    else:
        print(human if human is not None else json.dumps(data, indent=2, default=str))


def _live_progress(args):
    """One renderer per command so stage/bucket throttling stays coherent."""
    if getattr(args, "json", False):
        return None
    from .progress import CliProgress
    return CliProgress()


def _emit_failure(error, *, operation: str, recovery_command: str,
                  args=None, **context) -> None:
    """Emit the shared actionable-failure contract without leaking secrets."""
    from . import failure_diagnostics
    diagnostic = failure_diagnostics.build(
        error,
        operation=operation,
        recovery_command=recovery_command,
        **context,
    )
    failure_diagnostics.emit(
        diagnostic, as_json=bool(getattr(args, "json", False)))


def _review_recovery_command(args, run_id: str | None = None,
                             reviewer: str | None = None) -> str:
    run_id = run_id or getattr(args, "run", None) or getattr(args, "resume", None)
    reviewer = reviewer or getattr(args, "model_reviewer", None) or getattr(args, "judge", None)
    parts = ["aies", "review", str(run_id or "RUN_ID")]
    if reviewer:
        parts.extend(["--model-reviewer", str(reviewer)])
    else:
        parts.extend(["--model-reviewer", "REVIEWER_ID"])
    parallel = getattr(args, "parallel", None)
    if parallel:
        parts.extend(["--parallel", str(parallel)])
    runtime = getattr(args, "reviewer_runtime", None)
    if runtime:
        parts.extend(["--reviewer-runtime", str(runtime)])
    batch = getattr(args, "judge_batch_size", None)
    if batch:
        parts.extend(["--judge-batch-size", str(batch)])
    return " ".join(parts)


def cmd_doctor(args) -> int:
    from . import doctor
    record = doctor.run_doctor()
    if args.json:
        _out(record, True)
    else:
        fp = record["fingerprint"]
        print(f"aies doctor - platform {__version__}")
        print(f"  machine   : {fp['machine']}")
        print(f"  cpu       : {fp['cpu']}")
        print(f"  gpu       : {fp['gpu']}")
        print(f"  ram_gb    : {fp['ram_gb']}")
        print(f"  os        : {fp['os']} | python {fp['python']}")
        print(f"  workspace : {record['checks'].get('workspace')}")
        debris = record["checks"].get("workspace_debris") or {}
        print(f"  debris    : {debris.get('count', 0)} advisory finding(s); "
              "nothing deleted")
        for finding in (debris.get("findings") or [])[:5]:
            print(f"    [{finding['category']}] {finding['path']}")
        if debris.get("count", 0) > 5:
            print(f"    ... {debris['count'] - 5} more (use --json for all paths)")
        print(f"  fingerprint: {fp['fingerprint_hash']}")
        print("  runtimes:")
        for r in record.get("runtimes", []):
            mark = "OK  " if r["available"] else "--  "
            ver = f" v{r['version']}" if r.get("version") else ""
            print(f"    [{mark}] {r['runtime']}{ver}: {r['detail']}")
        print(f"  ready     : {'yes' if record['ready'] else 'NO'}")
    return 0 if record["ready"] else 1


def cmd_init(args) -> int:
    from . import adoption
    try:
        result = adoption.initialize(Path(args.path))
        if getattr(args, "starter_manifest", False):
            starter = adoption.starter_deployment(
                Path(args.path) / "deployment.example.yaml")
            result["starter_manifest"] = str(starter)
        if args.json:
            _out(result, True)
        else:
            print(f"AIES workspace ready: {result['workspace']}")
            print(f"  created : {len(result['created'])} item(s)")
            print(f"  existing: {len(result['existing'])} item(s), left unchanged")
            print("  secrets : none written")
            if result.get("starter_manifest"):
                print(f"  starter : {result['starter_manifest']} (contains no secret)")
            print("\nSet this workspace for the current shell:")
            print(f"  PowerShell: $env:AIES_WORKSPACE='{result['workspace']}'")
            print(f"  bash/zsh : export AIES_WORKSPACE='{result['workspace']}'")
            print("\nNext:")
            print("  aies starter list")
            print("  aies discover")
            print("  aies deployment list")
            if result.get("starter_manifest"):
                print(f"  aies deployment add \"{result['starter_manifest']}\"")
        return 0
    except adoption.AdoptionError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def cmd_open(args) -> int:
    from . import adoption, snapshot
    try:
        result = adoption.open_result(args.run, launch=not args.no_browser)
        if args.export_redacted is not None:
            destination = (None if args.export_redacted == "AUTO"
                           else Path(args.export_redacted))
            result["redacted_export"] = adoption.export_redacted(
                args.run, destination)
        if args.json:
            _out(result, True)
        else:
            try:
                print(snapshot.render(snapshot.build(result["run_id"])))
                print()
            except snapshot.SnapshotError:
                pass
            print(f"result: {result['view']}")
            print(f"link  : {result['uri']}")
            if result.get("redacted_export"):
                print(f"share : {result['redacted_export']['archive']}")
        return 0
    except adoption.AdoptionError as e:
        has_run = "has no HTML result" in str(e)
        recovery_run = args.run
        if has_run:
            try:
                recovery_run = adoption.resolve_run(args.run).name
            except adoption.AdoptionError:
                pass
        _emit_failure(
            e,
            operation="open-result",
            args=args,
            phase="evidence",
            run_id=recovery_run if has_run else None,
            preserved_work_status=("run-preserved" if has_run else "none"),
            preserved_work_detail=(
                "The run and its existing evidence are unchanged."
                if has_run else
                "Opening a result is read-only; no evidence was changed."),
            recovery_command=(
                f"aies qualify --resume {recovery_run}"
                if has_run else "aies runs list"),
            duplicate_cost_risk="none",
            duplicate_cost_detail=(
                "Report regeneration reuses existing ratings and responses."
                if has_run else
                "Listing runs and opening an existing artifact make no model calls."),
        )
        return 2


def cmd_bridge(args) -> int:
    from . import interop
    try:
        if args.bridge_cmd == "inspect-import":
            result = interop.import_inspect(
                args.run, Path(args.file), source=args.source)
            human = (
                f"Inspect evidence imported: {result['imported']} item(s), "
                f"{result['skipped_samples']} skipped\n"
                f"  source digest: {result['source_digest']}\n"
                f"  loss report  : {result['loss_report']}\n"
                f"Next: aies qualify --resume {args.run}"
            )
        elif args.bridge_cmd == "inspect-export":
            result = interop.export_inspect(args.run, Path(args.out))
            human = (
                f"Inspect JSON profile exported: {result['samples']} sample(s)\n"
                f"  artifact: {result['artifact']}\n"
                f"  digest  : {result['source_digest']}"
            )
        elif args.bridge_cmd == "sarif-import":
            result = interop.import_sarif(
                Path(args.file), destination=Path(args.out) if args.out else None)
            human = (
                f"SARIF evidence normalized: {result['findings']} finding(s)\n"
                f"  artifact: {result['artifact']}\n"
                "Static-analysis findings remain informational and do not prove "
                "correctness or conformance."
            )
        elif args.bridge_cmd == "sarif-export":
            result = interop.export_sarif(Path(args.file), Path(args.out))
            human = (
                f"SARIF 2.1.0 exported: {result['findings']} finding(s)\n"
                f"  artifact: {result['artifact']}\n"
                "The export retains the limitation that findings do not prove "
                "correctness or conformance."
            )
        _out(result, args.json, human)
        return 0
    except (interop.InteropError, OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def _evaluate_argv(args) -> list[str]:
    argv = ["qualify", args.subject]
    assessment = args.assessment or (
        "coder" if not args.all_areas and not args.area else None)
    if assessment:
        argv += ["--assessment", assessment]
    elif args.all_areas:
        argv += ["--all-areas"]
    for area in args.area or []:
        argv += ["--area", area]
    argv += ["--rt", str(args.rt), "--parallel", str(args.parallel)]
    if args.judge:
        argv += ["--judge", args.judge]
    if args.runtime:
        argv += ["--runtime", args.runtime]
    if args.reviewer_runtime:
        argv += ["--reviewer-runtime", args.reviewer_runtime]
    if args.judge_batch_size:
        argv += ["--judge-batch-size", str(args.judge_batch_size)]
    if args.json:
        argv += ["--json"]
    return argv


def cmd_evaluate(args) -> int:
    """Beginner entry point over the canonical no-repeat qualify pipeline."""
    from . import assessments, config, engine, registry
    try:
        judge = args.judge or config.default_judge()
        if not judge and not args.plan_only:
            raise ValueError(
                "automated evaluation needs a judge deployment; pass "
                "--judge ID or set AIES_JUDGE. No run or cost was started."
            )
        assessment_name = args.assessment or (
            "coder" if not args.all_areas and not args.area else None)
        if assessment_name:
            resolved = assessments.resolve(assessments.load(assessment_name))
            areas = resolved["areas"]
        elif args.all_areas:
            from . import runner
            areas = runner.all_area_codes()
        else:
            areas = args.area or ["CA-05"]
        registry.resolve(args.subject, runtime=args.runtime)
        plan = engine.plan_qualification(
            f"RT{args.rt}", areas, subject_kind="ai", repeats=1)
        batch = args.judge_batch_size or config.judge_batch_size()
        plan.update({
            "subject": args.subject,
            "assessment": assessment_name,
            "candidate_calls": plan["planned_items"],
            "estimated_judge_calls": (
                math.ceil(plan["planned_items"] / batch) if judge else 0),
            "judge_batch_size": batch,
            "parallel": args.parallel,
            "repeats": 1,
            "cost_estimate": "unavailable: no pricing declared by the deployments",
            "duration_estimate": "unavailable until endpoint throughput is observed",
            "limitations": [
                "scenario observations do not establish field performance",
                "unassessed tasks remain unknown",
                "automated scoring is sufficient for Engineering Evaluation but "
                "does not itself grant Formal Qualification",
            ],
        })
        if args.plan_only:
            _out(
                plan,
                args.json,
                "Evaluation plan (nothing executed)\n"
                f"  subject         : {args.subject}\n"
                f"  scope           : {assessment_name or ', '.join(areas)}\n"
                f"  risk tier       : RT{args.rt}\n"
                f"  distinct calls  : {plan['candidate_calls']}\n"
                f"  exact repeats   : 0\n"
                f"  judge calls     : ~{plan['estimated_judge_calls']} "
                f"(batch up to {batch})\n"
                f"  concurrency     : {args.parallel}\n"
                f"  cost estimate   : {plan['cost_estimate']}\n"
                f"  duration        : {plan['duration_estimate']}\n"
                "Run by removing --plan-only.",
            )
            return 0
        args.judge = judge
        if args.json:
            return main(_evaluate_argv(args))
        # The beginner command keeps detailed live progress on stderr, then
        # leads with the result rather than dumping the entire Markdown report
        # into the terminal. The full artifact is one click away.
        with contextlib.redirect_stdout(io.StringIO()):
            code = main(_evaluate_argv(args))
        if code == 0 and not args.json:
            from . import adoption, snapshot
            opened = adoption.open_result("latest", launch=args.open)
            print("\nYour Engineering Evaluation is ready.")
            try:
                print()
                print(snapshot.render(snapshot.build(opened["run_id"])))
            except snapshot.SnapshotError as e:
                print(f"  Snapshot unavailable: {e}")
                print(f"  Retry: aies snapshot {opened['run_id']}")
            print(f"  Open: {opened['uri']}")
            print(f"  Share safely: aies open {opened['run_id']} --export-redacted")
        return code
    except Exception as e:
        if isinstance(e, registry.RegistryError):
            recovery_command = "aies deployment list"
            preserved_detail = (
                "Deployment resolution failed before an assessment run started.")
        elif isinstance(e, assessments.AssessmentError):
            recovery_command = "aies starter list"
            preserved_detail = (
                "Assessment composition failed before an assessment run started.")
        else:
            recovery_command = (
                f"aies evaluate {args.subject} --judge REVIEWER_ID --plan-only")
            preserved_detail = (
                "Evaluation planning failed before this wrapper created a run.")
        _emit_failure(
            e,
            operation="engineering-evaluation",
            args=args,
            phase="planning",
            preserved_work_status="none",
            preserved_work_detail=preserved_detail,
            recovery_command=recovery_command,
            duplicate_cost_risk="none",
            duplicate_cost_detail=(
                "The recovery command is plan-only and makes no model calls."),
        )
        return 2


def cmd_demo(args) -> int:
    """Run a portable offline story through the real assessment pipeline."""
    from . import adoption, workspace
    old_workspace = os.environ.get("AIES_WORKSPACE")
    target = Path(args.workspace).expanduser().resolve()
    try:
        os.environ["AIES_WORKSPACE"] = str(target)
        adoption.initialize(target)
        print("AIES offline demo — subject → evidence → ECM → engineering fit")
        print(f"workspace: {target}")
        # The demo intentionally registers only the built-in mock deployments.
        # General discovery probes every installed adapter and can wait on local
        # model servers, which would make an offline trial unnecessarily slow.
        from . import registry
        from .adapters.mock import MockAdapter
        demo_deployments = [
            registry.create_from_discovery(item)
            for item in MockAdapter.discover_deployments()
        ]
        print("offline deployments: "
              + ", ".join(item["id"] for item in demo_deployments))
        # Keep the live progress stream visible but replace the full technical
        # report dump with a concise demo conclusion and direct artifact link.
        with contextlib.redirect_stdout(io.StringIO()):
            code = main([
                "evaluate", "mock-mock-small", "--assessment", "coder",
                "--rt", "1", "--judge", "mock-mock-large",
                "--parallel", str(args.parallel),
            ])
        if code:
            return code
        result = adoption.open_result("latest", launch=args.open)
        print("\nDEMO COMPLETE")
        print("  Automated Engineering Evaluation: complete")
        print("  Human evaluation: optional and not required")
        from . import snapshot
        print()
        print(snapshot.render(
            snapshot.build(result["run_id"]), observed_only=True))
        print(f"  Executive Summary: {result['view']}")
        print(f"  Open: {result['uri']}")
        print(f"  Share safely: aies open {result['run_id']} --export-redacted")
        print("\nReady to test your own deployment?")
        print("  aies init")
        print("  aies evaluate SUBJECT --judge REVIEWER --plan-only")
        return 0
    finally:
        if old_workspace is None:
            os.environ.pop("AIES_WORKSPACE", None)
        else:
            os.environ["AIES_WORKSPACE"] = old_workspace


def cmd_snapshot(args) -> int:
    """Show the evidence-to-decision view for a completed run."""
    from . import adoption, snapshot
    try:
        result = snapshot.build(args.run)
        _out(
            result,
            args.json,
            snapshot.render(result, observed_only=args.observed_only),
        )
        return 0
    except (adoption.AdoptionError, snapshot.SnapshotError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def cmd_support(args) -> int:
    """Show exactly which subject kinds have executable assessment support."""
    from . import support
    try:
        result = support.describe(args.subject_kind, status=args.status)
        _out(result, args.json, support.render(result))
        return 0
    except support.SupportError as e:
        _emit_failure(
            e,
            operation="subject-support-discovery",
            args=args,
            phase="evidence",
            preserved_work_status="none",
            preserved_work_detail=(
                "Subject-support discovery is read-only; no workspace state changed."),
            recovery_command="aies support",
            duplicate_cost_risk="none",
            duplicate_cost_detail="Support discovery makes no model calls.",
        )
        return 2


def cmd_starter(args) -> int:
    """List or explain a decision-oriented first workflow."""
    from . import decision_starters
    try:
        if args.starter_cmd == "list":
            result = decision_starters.list_starters()
            _out(result, args.json, decision_starters.render_list(result))
        else:
            result = decision_starters.get(args.starter_id)
            _out(result, args.json, decision_starters.render(result))
        return 0
    except decision_starters.StarterError as e:
        _emit_failure(
            e,
            operation="decision-starter-discovery",
            args=args,
            phase="evidence",
            preserved_work_status="none",
            preserved_work_detail=(
                "Decision-starter discovery is read-only; no workspace state changed."),
            recovery_command="aies starter list",
            duplicate_cost_risk="none",
            duplicate_cost_detail="Starter discovery makes no model calls.",
        )
        return 2


def cmd_registry(args) -> int:
    from . import registry
    try:
        if args.registry_cmd == "add":
            entry = registry.add(Path(args.file))
            _out(entry, args.json, f"registered {entry['id']}")
        elif args.registry_cmd == "list":
            entries = registry.list_entries(include_retired=args.all)
            _out(entries, args.json,
                 "\n".join(f"{e['id']:32} {(e.get('model') or e.get('family') or '?'):22} "
                           f"runtime={e.get('runtime', '?')}"
                           + ("  [RETIRED]" if e.get("retired") else "")
                           for e in entries) or "(registry empty — try `aies discover`)")
        elif args.registry_cmd == "show":
            _out(registry.get(args.model), args.json)
        elif args.registry_cmd == "retire":
            entry = registry.retire(args.model)
            _out(entry, args.json, f"retired {entry['id']}")
    except registry.RegistryError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_qualify(args) -> int:
    from . import engine
    live_progress = _live_progress(args)
    run_id = None
    reviewer_id = None
    try:
        if getattr(args, "resume_collection", None):
            summary = engine.resume_collection(args.resume_collection,
                                                 progress_callback=live_progress)
            _out(summary, args.json,
                 f"filled {summary['filled']} missing response(s) for "
                 f"{summary['run_id']} — now {summary['responses']}/{summary['planned']} "
                 f"collected.\nnext (automated): aies review {summary['run_id']} "
                 "--model-reviewer <judge> --parallel N\n"
                 "optional alternatives: aies score <run> or aies import <run> <file>; "
                 "each refreshes analysis and reports")
            return 0
        if args.resume:
            # A resumed run can be fully automatic too: score already-collected
            # responses with --judge, then aggregate and render in this one call.
            from . import config, model_review, review, workspace
            judge = getattr(args, "judge", None) or config.default_judge()
            scoring = None
            if judge:
                manifest = workspace.read_json(workspace.run_dir(args.resume) / "manifest.json")
                jdep = manifest["model"]["registry_id"] if judge == "self" else judge
                reviewer_id = jdep
                workers = getattr(args, "parallel", None) or config.default_parallel()
                if not args.json:
                    print(f"scoring existing responses with judge '{jdep}' across "
                          f"{workers} worker(s)…", file=sys.stderr)
                scoring = model_review.run_model_review(
                    args.resume, jdep,
                    runtime=getattr(args, "reviewer_runtime", None), workers=workers,
                    batch_size=(getattr(args, "judge_batch_size", None)
                                or config.judge_batch_size()),
                    progress_callback=live_progress)
                review_pkg = review.assemble_review_package(
                    args.resume, reviewer_label=f"model:{jdep}",
                    consider_advisory_review=getattr(args, "consider_advisory_review", False),
                    human_evaluation=getattr(args, "human_evaluation", None))
                (workspace.run_dir(args.resume) / "review-package.json").write_text(
                    json.dumps(review_pkg, indent=2), encoding="utf-8")
            from . import progress
            progress.update(args.resume, "aggregation", 0, 1,
                            callback=live_progress)
            package = engine.aggregate(args.resume)
            progress.update(args.resume, "aggregation", 1, 1, status="completed",
                            callback=live_progress)
            from . import evaluation, report
            progress.update(args.resume, "report-generation", 0, 1,
                            callback=live_progress)
            paths = report.write_reports(args.resume)
            progress.update(args.resume, "report-generation", 1, 1,
                            status="completed", callback=live_progress)
            outcome = _assessment_result(args.resume)
            evaluation_summary = evaluation.summarize(args.resume)
            _out({"package": package, "engineering_evaluation": evaluation_summary,
                  "reports": paths,
                  **({"scoring": scoring} if scoring else {}),
                  **({"assessment_result": outcome} if outcome else {})}, args.json,
                 f"complete report bundle generated for {args.resume}\n"
                 f"  report (Markdown): {paths['markdown']}\n"
                 f"  report (JSON)    : {paths['json']}\n"
                 f"  report (HTML)    : {paths['html']}\n"
                 f"  evaluation (JSON): {paths['engineering_evaluation']}\n"
                 f"  ECM (Markdown)   : {paths['ecm_markdown']}\n"
                 f"  ECM (JSON)       : {paths['ecm_json']}\n"
                 f"  ECM (HTML)       : {paths['ecm_html']}\n"
                 f"  Guidance (HTML)  : "
                 f"{paths.get('fit_guidance_html', paths.get('guidance_html'))}\n"
                 f"  Executive (HTML) : {paths['executive_html']}\n"
                 f"  Bundle manifest  : {paths['bundle_manifest']}"
                 + (f"\n\nAssessment '{outcome['assessment']['id']}' "
                    f"v{outcome['assessment']['version']}: "
                    f"**{outcome.get('outcome', outcome.get('status'))}**"
                    if outcome else ""))
            return 0
        from . import config, workspace
        # Resolve the effective worker count once so both phases (response
        # collection and, if judging, scoring) use it — and so the banner
        # below reports the real number.
        workers = getattr(args, "parallel", None) or config.default_parallel()
        if getattr(args, "journey", None):
            manifest = engine.start_journey(
                args.model, args.profile, args.journey,
                repeats=args.repeats, subject_kind="ai",
                runtime=getattr(args, "runtime", None),
                run_purpose=("formal-qualification"
                             if getattr(args, "formal_qualification", False)
                             else "engineering-evaluation"),
                progress_callback=live_progress)
        else:
            plan = engine.plan_qualification(f"RT{args.rt}", args.area,
                                              subject_kind="ai", repeats=args.repeats)
            if not args.json:
                formal_target = getattr(args, "formal_qualification", False)
                if (formal_target or getattr(args, "decisional", False)) and not plan[
                        "all_decisional_if_scored"]:
                    blocked = ", ".join(
                        f"{row['area']} ({row['planned_items']}/{row['minimum_items']})"
                        for row in plan["areas"] if not row["decisional_if_scored"])
                    print("warning: the selected sample is non-decisional if all responses are scored: "
                          + blocked + ". Add distinct scenarios; --decisional cannot pad breadth with repeats.", file=sys.stderr)
                elif getattr(args, "decisional", False):
                    print("decisional sample plan confirmed for every selected area.", file=sys.stderr)
                judge_hint = ""
                if getattr(args, "judge", None) or config.default_judge():
                    batch = (getattr(args, "judge_batch_size", None)
                             or config.judge_batch_size())
                    judge_hint = (f" plus approximately {math.ceil(plan['planned_items'] / batch)} "
                                  f"batched judge calls (up to {batch} items each; "
                                  "context limits may split batches)")
                print(f"sample plan: {plan['planned_items']} candidate calls{judge_hint}.", file=sys.stderr)
                # Only an explicit all-area request implies an expectation of
                # coverage across the entire Engineering Task Taxonomy. A
                # named assessment intentionally selects a narrower purpose;
                # tasks outside that composition are not a warning condition.
                if plan["unassessed_tasks"] and getattr(args, "all_areas", False):
                    print("warning: no direct scenario mapping for task(s): "
                          + ", ".join(plan["unassessed_tasks"])
                          + ". An all-area run cannot make a capability claim for them.", file=sys.stderr)
                print(f"collecting responses across {workers} worker(s)"
                      f"{' — pass --parallel N to raise' if workers == 1 else ''}…",
                      file=sys.stderr)
            manifest = engine.start_qualification(
                args.model, args.profile, f"RT{args.rt}", args.area,
                repeats=args.repeats,
                subject_kind="ai",
                runtime=getattr(args, "runtime", None),
                workers=workers,
                assessment=getattr(args, "_assessment", None),
                decisional=getattr(args, "decisional", False),
                run_purpose=("formal-qualification"
                             if getattr(args, "formal_qualification", False)
                             else "engineering-evaluation"),
                progress_callback=live_progress,
            )
        run_id = manifest["run_id"]
        # Automated scoring: if a judge is given (or AIES_JUDGE is set), score
        # the responses with it and output the report directly — no manual step.
        judge = getattr(args, "judge", None) or config.default_judge()
        if judge:
            from . import (engine as _engine, evaluation as _evaluation,
                           model_review, report as _report, review as _review)
            jdep = manifest["model"]["registry_id"] if judge == "self" else judge
            reviewer_id = jdep
            self_judged = jdep == manifest["model"]["registry_id"]
            n_resp = len(list((workspace.run_dir(run_id) / "responses").glob("*.json")))
            if not args.json:
                print(f"scoring {n_resp} responses with judge '{jdep}' across "
                      f"{workers} worker(s)…", file=sys.stderr)
            try:
                summary = model_review.run_model_review(
                    run_id, jdep, runtime=getattr(args, "reviewer_runtime", None),
                    workers=workers,
                    batch_size=(getattr(args, "judge_batch_size", None)
                                or config.judge_batch_size()),
                    progress_callback=live_progress)
            except Exception as e:
                _emit_failure(
                    e,
                    operation="automated-scoring",
                    args=args,
                    phase="scoring",
                    run_id=run_id,
                    preserved_work_status="responses-preserved",
                    preserved_work_detail=(
                        f"All {n_resp} candidate responses remain in run {run_id}; "
                        "successful ratings from this reviewer are reused."),
                    recovery_command=_review_recovery_command(
                        args, run_id=run_id, reviewer=jdep),
                    duplicate_cost_risk="partial",
                    duplicate_cost_detail=(
                        "Candidate calls will not repeat. Only failed or unrecorded "
                        "judge batches can be called again."),
                )
                return 2
            review_pkg = _review.assemble_review_package(
                run_id, reviewer_label=f"model:{jdep}",
                consider_advisory_review=getattr(args, "consider_advisory_review", False),
                human_evaluation=getattr(args, "human_evaluation", None))
            (workspace.run_dir(run_id) / "review-package.json").write_text(
                json.dumps(review_pkg, indent=2), encoding="utf-8")
            from . import progress as _progress
            _progress.update(run_id, "aggregation", 0, 1,
                             callback=live_progress)
            pkg = _engine.aggregate(run_id)
            _progress.update(run_id, "aggregation", 1, 1, status="completed",
                             callback=live_progress)
            _progress.update(run_id, "report-generation", 0, 1,
                             callback=live_progress)
            report_paths = _report.write_reports(run_id)
            _progress.update(run_id, "report-generation", 1, 1,
                             status="completed", callback=live_progress)
            outcome = _assessment_result(run_id)
            if args.json:
                _out({"run_id": run_id, "judge": jdep, "self_judged": self_judged,
                      "scoring": summary, "engineering_evaluation":
                      _evaluation.summarize(run_id), "evidence_package": pkg,
                      "reports": report_paths,
                      **({"assessment_result": outcome} if outcome else {})}, True)
            else:
                # The complete bundle already rendered the report from the
                # shared ECM view model. Print that artifact rather than
                # recomputing the corpus-backed matrix for terminal output.
                print(Path(report_paths["markdown"]).read_text(encoding="utf-8"))
                if outcome:
                    from . import decision as _decision, engineering_assessment as _ea
                    renderer = (_decision.render_markdown
                                if outcome.get("kind") == "assessment-result"
                                else _ea.render_markdown)
                    print("\n" + renderer(outcome))
                print(f"\n[auto-scored by judge '{jdep}': {summary['scored']}/"
                      f"{summary['responses']} responses; "
                      f"{summary['unparseable']} unparseable]")
                if self_judged:
                    print("WARNING: the model scored its own output (self-judging) — "
                          "expect inflation/bias. Use --judge <a different deployment> "
                          "for a trustworthy read.")
                print("Engineering evaluation complete; human evaluation is optional.")
                if getattr(args, "formal_qualification", False):
                    print("This run explicitly requested formal qualification; "
                          "a named human authority owns any grant.")
                else:
                    print("Formal qualification was not requested. Use "
                          "--formal-qualification only when that separate "
                          "human-governed workflow is intended.")
            return 0
        sheet = workspace.run_dir(run_id) / "scoresheet.json"
        _out(manifest, args.json,
             f"run {run_id}: responses collected; no scorer was selected.\n"
             f"\n"
             f"  Complete automatically (recommended; no human review required):\n"
             f"    aies review {run_id} --model-reviewer <judge> --parallel N\n"
             f"    # records scores, analyzes results, and writes the report bundle\n"
             f"\n"
             f"  Or optionally score/import from another source:\n"
             f"    scoresheet: {sheet}\n"
             f"    aies score {run_id}                 # completed scoresheet\n"
             f"    aies import {run_id} <eval.json>    # external EV1–EV6 scores\n"
             f"\n"
             f"  Tip: next time pass --judge <deployment> for a one-command benchmark.\n"
             f"  Human evaluation remains optional for Engineering Evaluation.")
    except Exception as e:
        durable_run_id = (
            getattr(e, "run_id", None)
            or run_id
            or getattr(args, "resume", None)
            or getattr(args, "resume_collection", None)
        )
        if isinstance(e, engine.RunExecutionError):
            recovery = f"aies qualify --resume-collection {e.run_id}"
            preserved_status = "partial-run-preserved"
            preserved_detail = (
                f"Run {e.run_id} remains resumable; every successfully written "
                "candidate response will be reused.")
            duplicate_risk = "none"
            duplicate_detail = (
                "Resume-collection requests only missing responses; completed "
                "candidate calls are not repeated.")
            failure_phase = e.phase
        elif getattr(args, "resume", None):
            recovery = _review_recovery_command(
                args,
                run_id=args.resume,
                reviewer=reviewer_id,
            )
            preserved_status = "run-preserved"
            preserved_detail = (
                f"Run {args.resume}, its responses, and any recorded ratings "
                "are unchanged.")
            duplicate_risk = "partial"
            duplicate_detail = (
                "Candidate calls will not repeat; only failed or unrecorded "
                "judge batches can be called again.")
            failure_phase = (
                "scoring" if getattr(args, "judge", None) else "evidence")
        elif getattr(args, "resume_collection", None):
            recovery = (
                f"aies qualify --resume-collection {args.resume_collection}")
            preserved_status = "partial-run-preserved"
            preserved_detail = (
                f"Existing responses in run {args.resume_collection} remain reusable.")
            duplicate_risk = "none"
            duplicate_detail = (
                "Resume-collection requests only missing responses.")
            failure_phase = "inference"
        else:
            recovery = f"aies deployment inspect {args.model}"
            preserved_status = "none"
            preserved_detail = (
                "The failure occurred before a durable run identifier was returned.")
            duplicate_risk = "none"
            duplicate_detail = (
                "Deployment inspection makes no model calls; correct the cause "
                "before rerunning the evaluation.")
            failure_phase = "inference"
        _emit_failure(
            e,
            operation="engineering-evaluation",
            args=args,
            phase=failure_phase,
            run_id=durable_run_id,
            preserved_work_status=preserved_status,
            preserved_work_detail=preserved_detail,
            recovery_command=recovery,
            duplicate_cost_risk=duplicate_risk,
            duplicate_cost_detail=duplicate_detail,
        )
        return 2
    return 0


def _assessment_result(run_id):
    """Build the result appropriate to the run's explicit purpose."""
    from . import decision, engineering_assessment, run_mode, workspace
    try:
        manifest = workspace.read_json(workspace.run_dir(run_id) / "manifest.json")
    except Exception:
        return None
    if not manifest.get("assessment"):
        return None
    try:
        if run_mode.is_formal(manifest):
            return decision.assess_run(run_id)
        return engineering_assessment.build(run_id)
    except (decision.DecisionError,
            engineering_assessment.EngineeringAssessmentError):
        return None


def cmd_assessment(args) -> int:
    from . import assessments
    try:
        if args.assessment_cmd == "list":
            rows = assessments.list_assessments()
            _out(rows, args.json, "\n".join(
                f"{r.get('id', ''):16} v{str(r.get('version', '?')):8} "
                f"comps={r.get('competencies', '?')} mandatory={r.get('mandatory', '?')}  "
                f"{'ok' if r.get('valid') else 'INVALID'}  {r.get('description', '')}"
                for r in rows) or "(no assessments under assessments/)")
        elif args.assessment_cmd == "show":
            import yaml as _yaml
            a = assessments.load(args.name)          # validates on load
            _out(a, args.json, _yaml.safe_dump(a, sort_keys=False))
        elif args.assessment_cmd == "validate":
            import yaml as _yaml
            src = Path(args.name)
            if not src.exists():
                src = assessments.assessments_dir() / f"{args.name}.yaml"
            if not src.exists():
                print(f"error: assessment {args.name!r} not found", file=sys.stderr)
                return 2
            problems = assessments.validate(_yaml.safe_load(src.read_text(encoding="utf-8")))
            if args.json:
                _out({"valid": not problems, "problems": problems}, True)
            elif problems:
                print(f"INVALID: {args.name}")
                for p in problems:
                    print(f"  - {p}")
            else:
                print(f"valid: {args.name}")
            return 0 if not problems else 1
        elif args.assessment_cmd == "result":
            from . import decision, engineering_assessment
            formal = getattr(args, "formal_qualification", False)
            res = (decision.assess_run(args.run) if formal
                   else engineering_assessment.build(args.run))
            if getattr(args, "format", "markdown") == "html":
                html_doc = (decision.render_html(res) if formal
                            else engineering_assessment.render_html(res))
                if args.out:
                    Path(args.out).write_text(html_doc, encoding="utf-8")
                    print(f"wrote {args.out}")
                else:
                    print(html_doc)
            else:
                rendered = (decision.render_markdown(res) if formal
                            else engineering_assessment.render_markdown(res))
                _out(res, args.json, rendered)
            return (0 if not formal or res["outcome"] == "PASS" else 1)
    except assessments.AssessmentError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        from . import decision
        if isinstance(e, decision.DecisionError):
            print(f"error: {e}", file=sys.stderr)
            return 2
        raise
    return 0


def cmd_score(args) -> int:
    from . import engine, evaluation, rating, report, workspace
    try:
        source = Path(args.file) if args.file else workspace.run_dir(args.run) / "scoresheet.json"
        sheet = json.loads(source.read_text(encoding="utf-8"))
        written = rating.ingest_scores(args.run, sheet,
                                       progress_callback=_live_progress(args))
        package = engine.aggregate(args.run)
        paths = report.write_reports(args.run)
        result = _assessment_result(args.run)
        _out({
            "ratings_written": written,
            "engineering_evaluation": evaluation.summarize(args.run),
            "evidence_package": package,
            "reports": paths,
            **({"assessment_result": result} if result else {}),
        }, args.json,
             f"{len(written)} rating records written for {args.run}\n"
             f"engineering evaluation and complete report bundle refreshed\n"
             f"  report: {paths['markdown']}\n"
             "human evaluation is optional unless formal qualification was "
             "explicitly requested")
    except (rating.RatingError, engine.EngineError, FileNotFoundError,
            json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_rater(args) -> int:
    """Manage durable human-rater qualification and calibration records."""
    from . import raters
    try:
        if args.rater_cmd == "register":
            record = raters.register(
                args.id, args.name, competency_areas=args.area,
                risk_tiers=[f"RT{tier}" for tier in args.rt],
                qualified_until=args.qualified_until,
                calibration_valid_until=args.calibration_valid_until,
                anchor_library_version=args.anchor_version,
                calibration_method=args.calibration_method,
                registered_by=args.registered_by)
            _out(record, args.json,
                 f"registered human rater {record['rater_id']} — {record['name']}\n"
                 f"  competencies: {', '.join(record['qualification']['competency_areas'])}\n"
                 f"  risk tiers: {', '.join(C.risk_tier_label(rt) for rt in record['qualification']['risk_tiers'])}\n"
                 f"  calibration valid until: {record['calibration']['valid_until']}")
        elif args.rater_cmd == "list":
            records = raters.list_records()
            _out(records, args.json, "\n".join(
                f"{record['rater_id']:24} {record['name']:28} "
                f"{record['status']:8} calibration→{record['calibration']['valid_until']}"
                for record in records) or "(no registered human raters)")
        elif args.rater_cmd == "show":
            _out(raters.get(args.id), args.json)
    except (raters.RaterError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_resolve(args) -> int:
    """Record an immutable human evidence-item disposition and refresh views."""
    from . import engine, rating, report, workspace
    try:
        manifest = workspace.read_json(workspace.run_dir(args.run) / "manifest.json")
        subject_id = ((manifest.get("subject") or {}).get("id")
                      or manifest["model"]["registry_id"])
        dimensions = {dimension: value for dimension, value in
                      zip(C.DIMENSIONS, args.scores)}
        resolution = rating.resolve_item(
            args.run, args.response, dimensions, resolver=args.resolver,
            resolver_id=args.resolver_id, rationale=args.rationale,
            conflict_declaration={
                "declared": bool(args.conflict_free),
                "has_conflict": False if args.conflict_free else None,
                "subject_id": subject_id,
            })
        package = engine.aggregate(args.run)
        paths = report.write_reports(args.run)
        _assessment_result(args.run)
        _out({"resolution": resolution, "evidence_package": package,
              "reports": paths}, args.json,
             f"resolved {args.response}; refreshed {paths['markdown']}")
    except (rating.RatingError, FileExistsError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_import(args) -> int:
    from . import engine, evalimport, evaluation, rating, report
    try:
        summary = evalimport.import_eval(args.run, args.file, source=args.source)
        package = engine.aggregate(args.run)
        paths = report.write_reports(args.run)
    except (evalimport.EvalImportError, rating.RatingError,
            engine.EngineError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    _out({**summary, "engineering_evaluation": evaluation.summarize(args.run),
          "evidence_package": package, "reports": paths}, args.json,
         f"imported {summary['imported']}/{summary['items']} items as "
         f"'{summary['source']}' ({summary['skipped']} skipped) into {args.run}\n"
         f"engineering evaluation and complete report bundle refreshed\n"
         f"  report: {paths['markdown']}\n"
         "human evaluation is optional")
    return 0


def cmd_export(args) -> int:
    from . import evalexport
    try:
        if args.write:
            path = evalexport.write_export(args.run)
            _out({"exported": path}, args.json, f"wrote {path}")
        else:
            print(evalexport.render_json(args.run))
    except FileNotFoundError:
        print(f"error: no run {args.run!r} in this workspace", file=sys.stderr)
        return 2
    return 0


def cmd_report(args) -> int:
    from . import report
    target = args.run
    # Resource-aware dispatch: a QUAL-… id renders a durable qualification
    # report; "list" enumerates generated reports; anything else is a run.
    if target == "list":
        from . import qual_report
        items = qual_report.list_reports()
        _out(items, args.json,
             "\n".join(f"{i['record']:20} {i['format']:8} {i['file']}" for i in items)
             or "(no generated reports — `aies report <QUAL-id>`)")
        return 0
    if target.startswith("QUAL-"):
        from . import qual_report
        from .qualification import QualificationError
        try:
            content = qual_report._RENDER[args.format](target)
            path = qual_report.generate(target, args.format)  # persist durably
            if args.write:
                _out({"report": path}, args.json, f"wrote {path}")
            else:
                print(content)
        except (QualificationError, ValueError, KeyError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        return 0
    try:
        if args.format == "json":
            if args.write:
                paths = report.write_reports(args.run)
                _out({"report": paths["json"]}, args.json, f"wrote {paths['json']}")
            else:
                print(report.render_json(args.run))
        elif args.format == "html":
            from . import report_html
            if args.write:
                paths = report.write_reports(args.run)
                _out({"html": paths["html"], "reports": paths}, args.json,
                     f"wrote complete report bundle; HTML evidence report: {paths['html']}\n"
                     "(open in a browser; use the browser's Save as PDF for the "
                     "PDF deliverable — no PDF dependency is bundled)")
            else:
                print(report_html.render_html(args.run))
        else:
            if args.write:
                paths = report.write_reports(args.run)
                _out({"report": paths["markdown"]}, args.json, f"wrote {paths['markdown']}")
            else:
                print(report.render_markdown(args.run))
    except FileNotFoundError:
        print(f"error: no evidence package for {args.run!r} — run "
              f"`aies qualify --resume {args.run}` first", file=sys.stderr)
        return 2
    return 0


def cmd_audit(args) -> int:
    """Audit a repository's conformance to AIES engineering practices (ADR-0004)."""
    from . import audit
    attestations = None
    if args.attest:
        try:
            attestations = json.loads(Path(args.attest).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"error: cannot read attestation file {args.attest!r}: {e}",
                  file=sys.stderr)
            return 2
    rt = f"RT{args.rt}" if args.gate else (f"RT{args.rt}" if args.rt else None)
    try:
        result = audit.run_audit(args.repo, attestations=attestations, rt=rt)
    except (NotADirectoryError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.format == "json" or args.json:
        _out(result, True)
    else:
        print(audit.render_markdown(result))
        repo = shlex.quote(str(args.repo))
        if args.gate:
            gate = result.get("gate") or {}
            if gate.get("passed"):
                print(
                    f"\nNext: retain this evidence and rerun after material "
                    f"change: aies audit {repo} --gate --rt {args.rt}")
            else:
                print(
                    f"\nNext: close the ranked required gaps, then rerun: "
                    f"aies audit {repo} --gate --rt {args.rt}")
        else:
            print(
                f"\nNext: preview the decision workflow with "
                f"`aies starter show audit-repository`, or apply an explicit "
                f"CI gate: aies audit {repo} --gate --rt 2")
    if args.gate:
        g = result.get("gate") or {}
        return 0 if g.get("passed") else 1
    return 0


def cmd_ci(args) -> int:
    """Create retained CI evidence; enforce only when explicitly requested."""
    from . import ci_integration
    try:
        attestations = None
        if args.attest:
            attestations = json.loads(
                Path(args.attest).read_text(encoding="utf-8"))
        package = ci_integration.build_repository_package(
            args.repo,
            risk_tier=f"RT{args.rt}",
            enforce=args.enforce,
            attestations=attestations,
        )
        paths = ci_integration.write_repository_package(package, args.out)
        if args.github_annotations:
            for line in ci_integration.github_annotation_lines(package):
                print(line)
        output = {**package, "artifacts": paths}
        _out(
            output,
            args.json,
            "AIES CI repository assessment\n"
            f"  mode       : {package['policy']['mode']}\n"
            f"  risk tier  : {package['policy']['risk_tier_label']}\n"
            f"  policy     : "
            f"{'PASS' if package['policy']['passed'] else 'GAPS FOUND'}\n"
            f"  CI blocking: {'yes' if args.enforce else 'no'}\n"
            f"  report     : {paths['markdown']}\n"
            f"  evidence   : {paths['json']}\n"
            f"  annotations: {paths['annotations']}\n"
            + (
                "  next       : enforcement was explicitly selected; close "
                "required gaps before retrying"
                if args.enforce and not package["policy"]["passed"]
                else
                "  next       : review the retained findings; enable --enforce "
                "only after repository-owner approval"
            ),
        )
        return package["policy"]["exit_code"]
    except (OSError, ValueError, json.JSONDecodeError,
            NotADirectoryError, FileNotFoundError) as error:
        _emit_failure(
            error,
            operation="ci-repository-assessment",
            args=args,
            phase="evidence",
            preserved_work_status="source-unchanged",
            preserved_work_detail=(
                "Repository assessment is read-only; source files were not changed."),
            recovery_command=(
                f"aies ci audit {args.repo} --rt {args.rt} --out {args.out}"),
            duplicate_cost_risk="none",
            duplicate_cost_detail=(
                "Repository auditing makes no model or paid endpoint calls."),
        )
        return 2


def cmd_capabilities(args) -> int:
    """Engineering Capability Matrix by default; formal profile explicitly."""
    from . import capabilities, compare, constants as C, ecm
    if not getattr(args, "qualification_profile", False):
        try:
            matrix = ecm.engineering_capability_matrix(args.ref)
        except compare.CompareError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        if args.write:
            path = ecm.write_matrix(matrix, args.format)
            _out({"engineering_capability_matrix": str(path)}, args.json,
                 f"wrote {path}")
        elif args.json or args.format == "json":
            _out(matrix, True)
        elif args.format == "html":
            print(ecm.render_html(matrix))
        else:
            print(ecm.render_markdown(matrix))
        return 0
    try:
        prof = capabilities.capability_profile(args.ref)
    except compare.CompareError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.json:
        _out(prof, True)
        return 0
    print(f"Capability profile — {prof['subject']}  "
          f"({C.risk_tier_label(prof['risk_tier'])}, {prof['profile']} profile)")
    if "model" in prof["rater_kinds"]:
        print("  judge-produced evidence — not a grant")
    print()
    print(f"  {'AREA / COMPETENCY':52} {'CL':18} {'AGG':5} "
          f"{'AUTONOMY':18} GATES  SAMPLE")
    for r in prof["areas"]:
        aggregate = r["aggregate"]
        if aggregate is None:
            gate = "N/A  "
            sample = f"NO ADMITTED {r['n_scored']}/{r['min_sample']}"
        else:
            gate = "PASS " if r["gates_passed"] else "FAIL "
            sample = ("decisional" if r["decisional"]
                      else f"NON-DEC {r['n_scored']}/{r['min_sample']}")
        label = C.competency_label(r['area'])
        cl = C.identifier_label(r['cl']) if r['cl'] else "none"
        agg = f"{aggregate:.2f}" if aggregate is not None else "-"
        autonomy = (C.autonomy_level_label(r['al_at_rt'])
                    if r['al_at_rt'] else "none")
        print(f"  {label[:52]:52} {cl[:18]:18} "
              f"{agg:5} {autonomy[:18]:18} {gate} {sample}")
    print("\n  CL = competency level · AGG = weighted aggregate · "
          f"AL = autonomy ceiling at {C.risk_tier_label(prof['risk_tier'])}. Read across areas for "
          "strengths/gaps (e.g. strong coder, weak security). See GUIDE §5.2b.")
    return 0


def cmd_guidance(args) -> int:
    """Render engineering fit by default, or qualification-bounded guidance."""
    from . import compare, guidance, qualification
    try:
        options = {
            "qualification_id": args.qualification,
            "requested_role": args.role,
            "requested_phases": args.phase,
            "requested_autonomy": f"AL{args.autonomy}" if args.autonomy is not None else None,
        }
        if not args.qualification:
            if any((args.role, args.phase, args.autonomy is not None)):
                raise guidance.GuidanceError(
                    "--role, --phase, and --autonomy require --qualification; "
                    "engineering fit has no deployment scope")
            if args.write:
                paths = guidance.write_fit_artifacts(args.ref)
                _out({"engineering_fit_guidance": paths}, args.json,
                     "wrote Engineering Fit Guidance:\n" +
                     "\n".join(f"  {format}: {path}" for format, path in paths.items()))
            else:
                result = guidance.engineering_fit(args.ref)
                _out(result, args.json, guidance.render_fit_markdown(result))
        elif args.write:
            paths = guidance.write_artifacts(args.ref, **options)
            _out({"deployment_guidance": paths}, args.json,
                 "wrote qualification-bounded Deployment Guidance:\n" +
                 "\n".join(f"  {format}: {path}" for format, path in paths.items()))
        else:
            result = guidance.decide(args.ref, **options)
            _out(result, args.json, guidance.render_markdown(args.ref, **options))
    except (compare.CompareError, guidance.GuidanceError,
            qualification.QualificationError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_transcript(args) -> int:
    from . import transcript
    try:
        if args.format == "json":
            print(transcript.render_json(args.run, area=args.area))
        elif args.write:
            path = transcript.write_transcript(args.run)
            _out({"transcript": path}, args.json, f"wrote {path}")
        else:
            print(transcript.render_markdown(args.run, area=args.area))
    except FileNotFoundError:
        print(f"error: no run {args.run!r} in this workspace", file=sys.stderr)
        return 2
    return 0


def cmd_index(args) -> int:
    from . import index
    result = index.rebuild()
    _out(result, args.json,
         f"rebuilt result index: {result['runs_indexed']} runs, "
         f"{result['area_scores_indexed']} area scores\n  {result['index']}")
    return 0


def cmd_profiles(args) -> int:
    from . import profiles
    try:
        if args.profiles_cmd == "list":
            items = profiles.list_shipped()
            _out(items, args.json,
                 "\n".join(f"{p['name']:12} v{profiles.profile_version(p):8} "
                           f"{p.get('description', '')}" for p in items))
        elif args.profiles_cmd == "show":
            _out(profiles.load(args.name), args.json)
        elif args.profiles_cmd == "validate":
            p = profiles.load(args.name)
            _out({"valid": True, "profile": p["name"]}, args.json,
                 f"profile {p['name']!r} is valid (gates untouched, "
                 "adjustments within AIES-AESQS-CS-01-R03 bounds)")
    except profiles.ProfileError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_corpus(args) -> int:
    from . import corpus
    root = Path(args.root) if getattr(args, "root", None) else None
    if args.corpus_cmd == "duplicates":
        report = corpus.duplicates(root)
        _out(report, args.json, corpus.render_duplicates(report))
        return 0   # advisory — never a gate
    if args.corpus_cmd == "review-pending":
        report = corpus.pending_reviews(root)
        _out(report, args.json, corpus.render_pending_reviews(report))
        return 0   # preflight only — never records human approval
    if args.corpus_cmd == "review":
        try:
            report = corpus.review_scenario(args.scenario, reviewer=args.reviewer,
                                            runtime=args.runtime)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        _out(report, args.json, corpus.render_review(report))
        return 0   # advisory — critique only, never a gate
    report = corpus.health(root)
    _out(report, args.json, corpus.render(report, coverage_only=args.corpus_cmd == "coverage"))
    return 0   # advisory — never a gate


def cmd_serve(args) -> int:
    from . import api
    api.serve(args.host, args.port)
    return 0


def cmd_plugins(args) -> int:
    from .adapters import discovered
    items = {name: {"class": cls.__name__, "version": getattr(cls, "adapter_version", "?")}
             for name, cls in discovered().items()}
    _out(items, args.json,
         "\n".join(f"{k:15} {v['class']} v{v['version']}" for k, v in items.items()))
    return 0


def cmd_completion(args) -> int:
    """Print a sourceable completion definition derived from the live parser."""
    from .cli_completion import render_completion
    print(render_completion(build_parser(), args.shell), end="")
    return 0


def cmd_benchmark(args) -> int:
    # Benchmark is always a non-blocking Engineering Evaluation. With --judge
    # it completes scoring, analysis, and reporting in the same invocation.
    args.resume = None
    args.formal_qualification = False
    return cmd_qualify(args)


def cmd_compare(args) -> int:
    from . import compare
    try:
        if (getattr(args, "formal_qualification", False)
                and getattr(args, "area_summary", False)):
            raise compare.CompareError(
                "--formal-qualification cannot be combined with --area-summary")
        cmp = (compare.compare(args.a, args.b)
               if getattr(args, "area_summary", False)
               else compare.compare_ecm(
                   args.a, args.b,
                   formal_qualification=getattr(
                       args, "formal_qualification", False)))
        if args.json or args.format == "json":
            _out(cmp, True)
        else:
            print(compare.render_markdown(cmp)
                  if getattr(args, "area_summary", False)
                  else compare.render_ecm_markdown(cmp))
            print(
                "\nNext: inspect the comparison boundary and plan any missing "
                "matching evidence: aies starter show compare-coding-deployments")
    except compare.CompareError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_discover(args) -> int:
    from . import registry, runtimes
    found = runtimes.discover_all()
    results = []
    for partial in found:
        try:
            entry = registry.create_from_discovery(partial)
            results.append({"id": entry["id"], "runtime": entry.get("runtime"),
                            "model": entry.get("model") or entry.get("family"),
                            "status": entry.get("_status", "created")})
        except registry.RegistryError as e:
            results.append({"runtime": partial.get("runtime"),
                            "model": partial.get("model"), "status": f"skipped: {e}"})
    if args.json:
        _out(results, True)
    else:
        if not results:
            print("no deployments discovered (no runtimes reported servable models)")
        for r in results:
            print(f"  [{r['status']:8}] {r.get('id', '?'):32} "
                  f"{r.get('runtime', '?')} / {r.get('model', '?')}")
        created = sum(1 for r in results if r["status"] == "created")
        print(f"\n{created} new deployment(s); run `aies registry list` to see all, "
              "then `aies qualify <deployment>`.")
    return 0


def cmd_runs(args) -> int:
    from . import compare, workspace
    if args.runs_cmd == "progress":
        path = workspace.run_dir(args.run) / "progress.json"
        if not path.exists():
            print(f"error: run {args.run!r} has no progress state", file=sys.stderr)
            return 2
        event = workspace.read_json(path)
        eta = "—" if event.get("eta_seconds") is None else f"{event['eta_seconds']:.0f}s"
        active_tasks = event.get("active_tasks") or []
        if active_tasks:
            current_display = " | ".join(active_tasks)
        elif event.get("current"):
            position = (f" {event['current_index']}/{event['total']}"
                        if event.get("current_index") is not None else "")
            current_display = (f"{event.get('activity') or 'Current task'}"
                               f"{position}: {event['current']}")
        else:
            current_display = "—"
        _out(event, args.json,
             f"{event['run_id']}\n"
             f"  stage      : {event['stage']} ({event['status']})\n"
             f"  progress   : {event['completed']}/{event['total']} "
             f"({event['percent']:.1f}%)\n"
             f"  stage time : {event['elapsed_seconds']:.1f}s\n"
             f"  total time : {event.get('total_elapsed_seconds', event['elapsed_seconds']):.1f}s\n"
             f"  throughput : {event['throughput_per_second']:.2f}/s\n"
             f"  ETA        : {eta}\n"
             f"  failures   : {event['failures']}\n"
             f"  active     : {event.get('active_count', 0)}/"
             f"{event.get('parallelism') or max(1, event.get('active_count', 0))}\n"
             f"  current    : {current_display}\n"
             f"  resumable  : {'yes' if event.get('resumable') else 'no'}")
        return 0
    runs = compare.list_runs(model=args.model)
    _out(runs, args.json,
         "\n".join(
             f"{r['run_id']:45} {r['model']:20} {r['profile']:10} "
             f"{C.risk_tier_label(r['risk_tier']):22} {'aggregated' if r['aggregated'] else r['status']}"
             for r in runs) or "(no runs)")
    return 0


def cmd_review(args) -> int:
    from . import rating, review, run_mode, workspace
    live_progress = _live_progress(args)
    try:
        report_paths = None
        scoring = None
        # Optionally drive a reviewer deployment to score the responses first.
        if getattr(args, "model_reviewer", None):
            from . import config, engine, model_review, report
            workers = getattr(args, "parallel", None) or config.default_parallel()
            if not args.json:
                print(f"scoring responses with reviewer '{args.model_reviewer}' "
                      f"across {workers} worker(s)…", file=sys.stderr)
            scoring = model_review.run_model_review(
                args.run, args.model_reviewer,
                runtime=getattr(args, "reviewer_runtime", None), workers=workers,
                batch_size=(getattr(args, "judge_batch_size", None)
                            or config.judge_batch_size()),
                progress_callback=live_progress)
            if not (args.json):
                print(f"reviewer model {scoring['reviewer']}: scored "
                      f"{scoring['scored']}/{scoring['responses']} responses "
                      f"({scoring['unparseable']} unparseable)")
            if not args.reviewer or args.reviewer == "reviewer-model":
                args.reviewer = f"model:{args.model_reviewer}"
        calibration = None
        if args.calibration:
            cal = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
            calibration = review.calibrate(cal["model"], cal["human_anchor"])
        pkg = review.assemble_review_package(
            args.run, reviewer_label=args.reviewer,
            reviewer_qualified_for_review=args.reviewer_qualified,
            calibration=calibration,
            consider_advisory_review=getattr(args, "consider_advisory_review", False),
            human_evaluation=getattr(args, "human_evaluation", None))
        (workspace.run_dir(args.run) / "review-package.json").write_text(
            json.dumps(pkg, indent=2), encoding="utf-8")
        manifest = workspace.read_json(
            workspace.run_dir(args.run) / "manifest.json")
        formal = run_mode.is_formal(manifest)
        # A review package changes which rating observations are admitted.  It
        # must therefore refresh canonical evidence and every presentation
        # artifact even when the ratings were collected in an earlier command.
        # Without this, a passed calibration leaves a stale non-decisional
        # evidence package behind.  An empty review remains useful as planning
        # metadata, but cannot manufacture an evidence package.
        assessment_result = None
        if rating.collect_ratings(args.run):
            from . import engine, evaluation, progress, report
            progress.update(args.run, "aggregation", 0, 1,
                            callback=live_progress)
            engine.aggregate(args.run)
            progress.update(args.run, "aggregation", 1, 1, status="completed",
                            callback=live_progress)
            progress.update(args.run, "report-generation", 0, 1,
                            callback=live_progress)
            report_paths = report.write_reports(args.run)
            progress.update(args.run, "report-generation", 1, 1,
                            status="completed", callback=live_progress)
            assessment_result = _assessment_result(args.run)
        if args.json:
            _out({**pkg, **({"reports": report_paths} if report_paths else {}),
                  **({"scoring": scoring} if scoring else {}),
                  **({"engineering_evaluation": evaluation.summarize(args.run)}
                     if report_paths else {}),
                  **({"assessment_result": assessment_result}
                     if assessment_result else {})}, True)
        else:
            s = pkg["summary"]
            print(f"automated engineering review for {args.run}")
            if scoring:
                print(f"  automated reviewer scores: RECORDED "
                      f"({scoring['scored']}/{scoring['responses']})")
            print("  engineering evaluation: automated scores are usable")
            print("  human evaluation: optional"
                  + (f" — {args.human_evaluation}"
                     if getattr(args, "human_evaluation", None) else
                     " — not supplied"))
            print(f"  observed divergences: {s['n_divergences']}")
            for d in pkg["divergences_for_resolution"]:
                gc = " [gate-changing]" if d["gate_changing"] else ""
                print(f"    {d['response']} {d['dimension']}: "
                      f"{d.get('left_rater', 'human')} {d['human']} vs "
                      f"{d.get('right_rater', 'reviewer')} {d['model']} "
                      f"(Δ{d['delta']}){gc}")
            print(f"  {s['note']}")
            if formal:
                print(f"  formal reviewer admission: "
                      f"{'corroborating evidence admitted' if s['reviewer_admitted'] else 'not admitted'}")
                print(f"  formal admission reason: {pkg['reviewer']['reason']}")
            else:
                print("  formal qualification: not requested")
            if report_paths:
                print("  complete engineering report bundle refreshed")
                print("  human scores: optional; shown separately when supplied")
                print(f"  report: {report_paths['markdown']}")
            else:
                print("  no ratings yet; review package saved but no report was generated")
    except Exception as e:
        _emit_failure(
            e,
            operation="automated-review",
            args=args,
            phase="review",
            run_id=args.run,
            preserved_work_status="run-preserved",
            preserved_work_detail=(
                f"Candidate responses in run {args.run} remain unchanged; any "
                "successfully recorded ratings are reused on retry."),
            recovery_command=_review_recovery_command(args),
            duplicate_cost_risk="partial",
            duplicate_cost_detail=(
                "Candidate calls will not repeat. Only failed or unrecorded "
                "reviewer batches can be called again."),
        )
        return 2
    return 0


def cmd_grant(args) -> int:
    from . import qualification, workspace
    try:
        review_package = None
        rp = workspace.run_dir(args.run) / "review-package.json"
        if rp.exists():
            review_package = json.loads(rp.read_text(encoding="utf-8"))
        record = qualification.record_decision(
            args.run, args.decision, args.authority,
            second_human=args.second, conditions=args.condition,
            assessor=args.assessor, assessor_id=args.assessor_id,
            peer_reviewer=args.peer_reviewer,
            peer_reviewer_id=args.peer_reviewer_id,
            assessor_conflict_free=args.assessor_conflict_free,
            peer_conflict_free=args.peer_conflict_free,
            role=args.role, phases=args.phase, sponsor=args.sponsor,
            framework_version=args.framework_version,
            agent_definition_version=args.agent_definition_version,
            valid_from=args.valid_from, valid_until=args.valid_until,
            review_package=review_package, rationale=args.rationale or "",
            consider_advisory_review=args.consider_advisory_review,
            human_evaluation=args.human_evaluation)
        _out(record, args.json,
             f"recorded {record['decision']} -> {record['record_id']} "
             f"(status: {record['status']})\n"
             f"  authority: {record['humans']['authority']}"
             + (f", second: {record['humans']['second']}" if record['humans']['second'] else "")
             + f"\n  subject: {record['subject']['deployment']} "
             f"@ {C.risk_tier_label(record['scope']['risk_tier'])}"
             + f"\n  advisory review: {'considered' if record['evidence_consideration']['automated_advisory_review']['considered_by_authority'] else 'not declared'}"
             + f"\n  human evaluation: {record['evidence_consideration']['human_evaluation']['evaluator'] or 'not declared'}")
    except qualification.QualificationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_verify(args) -> int:
    from . import qualification
    try:
        result = qualification.verify(args.record)
        _out(result, args.json,
             f"{args.record}: environment "
             f"{'unchanged' if result['environment_unchanged'] else 'CHANGED'} "
             f"-> status {result['status']} ({result['action']})")
        # Non-zero exit when a grant is invalidated, for CI gating.
        return 0 if result["environment_unchanged"] else 4
    except qualification.QualificationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def cmd_qualifications(args) -> int:
    from . import qualification
    try:
        if args.q_cmd == "list":
            recs = qualification.list_records()
            _out(recs, args.json,
                 "\n".join(f"{r['record_id']:48} {r['subject']['deployment']:20} "
                           f"{C.risk_tier_label(r['scope']['risk_tier']):22} {r['decision']:20} [{r['status']}]"
                           for r in recs) or "(no qualification records)")
        elif args.q_cmd == "show":
            _out(qualification.get_record(args.record), args.json)
        elif args.q_cmd == "revoke":
            rec = qualification.revoke(args.record, args.authority, args.reason)
            _out(rec, args.json, f"revoked {rec['record_id']}")
        elif args.q_cmd == "event":
            rec = qualification.record_lifecycle_event(
                args.record, args.event, args.authority, args.reason,
                conditions=args.condition, valid_until=args.valid_until,
                superseded_by=args.superseded_by,
                evidence_run_id=args.evidence_run,
                peer_reviewer=args.peer_reviewer,
                peer_reviewer_id=args.peer_reviewer_id,
                peer_conflict_free=args.peer_conflict_free)
            _out(rec, args.json,
                 f"recorded immutable {args.event} event for {rec['record_id']} "
                 f"-> {rec['status']}")
    except qualification.QualificationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_runtime(args) -> int:
    """Runtime is a first-class resource: the adapters and the runtimes
    behind them (PLATFORM.md §8, D11)."""
    from . import runtimes
    from .adapters import discovered
    classes = discovered()
    if args.rt_cmd == "list":
        probes = {p["runtime"]: p for p in runtimes.probe_all()}
        rows = []
        for name, cls in sorted(classes.items()):
            p = probes.get(name, {})
            rows.append({"runtime": name, "adapter": cls.__name__,
                         "adapter_version": getattr(cls, "adapter_version", "?"),
                         "contract": getattr(cls, "contract_version", "?"),
                         "available": p.get("available", False),
                         "detail": p.get("detail", "")})
        _out(rows, args.json,
             "\n".join(f"[{'OK  ' if r['available'] else '--  '}] {r['runtime']:14} "
                       f"{r['adapter']:22} contract v{r['contract']}  {r['detail']}"
                       for r in rows))
    elif args.rt_cmd == "inspect":
        cls = classes.get(args.name)
        if cls is None:
            print(f"error: no runtime adapter {args.name!r} (aies runtime list)",
                  file=sys.stderr)
            return 2
        try:
            probe = cls.probe_runtime()
        except Exception as e:
            probe = {"available": False, "detail": f"probe raised {e.__class__.__name__}"}
        try:
            deployments = cls.discover_deployments()
        except Exception:
            deployments = []
        info = {
            "runtime": args.name,
            "adapter": cls.__name__,
            "adapter_version": getattr(cls, "adapter_version", "?"),
            "contract_version": getattr(cls, "contract_version", "?"),
            "endpoint_env": getattr(cls, "RUNTIME_ENV", None),
            "conventional_default": getattr(cls, "RUNTIME_DEFAULT", None),
            "capabilities": cls().capabilities(),
            "probe": probe,
            "discovered_deployments": [d.get("model") for d in deployments],
        }
        _out(info, args.json,
             f"runtime {args.name} ({cls.__name__} v{info['adapter_version']}, "
             f"contract v{info['contract_version']})\n"
             + (f"  endpoint env : {info['endpoint_env']}"
                f" (default {info['conventional_default']})\n"
                if info['endpoint_env'] else "")
             + f"  available    : {'yes' if probe.get('available') else 'no'} "
             f"— {probe.get('detail','')}\n"
             f"  capabilities : {info['capabilities']}\n"
             f"  serves now   : {', '.join(info['discovered_deployments']) or '(none)'}")
    return 0


def cmd_judge(args) -> int:
    """Judge track record derived from model-kind ratings across runs."""
    from . import judge
    if args.judge_cmd == "available":
        rows = judge.registered_judges()
        if args.json:
            _out(rows, True)
        elif not rows:
            print("no deployments are registered as judges yet.\n"
                  "  Tag one with `roles: [judge]` in its manifest (see "
                  "examples/deployments/), or pass any deployment ad hoc with "
                  "`aies qualify … --judge <id>`.")
        else:
            lines = [f"{len(rows)} registered judge(s):"]
            for a in rows:
                pr = ("never used" if a["parse_rate"] is None
                      else f"parse={a['parse_rate']:.0%}, runs={a['runs_judged']}")
                lines.append(f"  {a['judge']:28} {(a['model'] or '?'):22} "
                             f"runtime={a['runtime']:<14} {pr}")
            _out(rows, args.json, "\n".join(lines))
    elif args.judge_cmd == "list":
        rows = judge.judge_usage()
        if args.json:
            _out(rows, True)
        elif not rows:
            print("(no judge has scored a run yet — run "
                  "`aies qualify … --judge <deployment>`)")
        else:
            lines = []
            for a in rows:
                flags = []
                if a["self_judged_runs"]:
                    flags.append(f"{a['self_judged_runs']} self-judged")
                if not a["registered"]:
                    flags.append("NOT REGISTERED")
                pr = "n/a" if a["parse_rate"] is None else f"{a['parse_rate']:.0%}"
                lines.append(
                    f"{a['judge']:28} runs={a['runs_judged']:<3} "
                    f"scored={a['responses_scored']:<4} parse={pr:>4} "
                    f"last={(a['last_used'] or '')[:10]}"
                    + (f"  [{', '.join(flags)}]" if flags else ""))
            _out(rows, args.json, "\n".join(lines))
    elif args.judge_cmd == "history":
        rows = judge.judge_history(judge=getattr(args, "judge", None))
        if args.json:
            _out(rows, True)
        elif not rows:
            print("(no judged runs yet)")
        else:
            lines = []
            for x in rows:
                tag = " [self]" if x["self_judged"] else ""
                agg = "aggregated" if x["aggregated"] else "not-aggregated"
                lines.append(
                    f"{x['run_id']:20} subject={x['subject']:20} "
                    f"judge={x['judge']}{tag}  "
                    f"scored={x['scored']}/{x['responses']} "
                    f"({x['unparseable']} unparseable)  {agg}")
            _out(rows, args.json, "\n".join(lines))
    return 0


def cmd_deployment(args) -> int:
    """Resource-model alias over the registry (deployments are what the
    registry holds)."""
    from . import registry
    try:
        if args.dep_cmd == "list":
            entries = registry.list_entries(include_retired=getattr(args, "all", False))
            _out(entries, args.json,
                 "\n".join(f"{e['id']:32} {(e.get('model') or e.get('family') or '?'):22} "
                           f"runtime={e.get('runtime','?')}"
                           + ("  [RETIRED]" if e.get("retired") else "")
                           for e in entries) or "(no deployments — try `aies discover`)")
        elif args.dep_cmd == "inspect":
            _out(registry.get(args.name), args.json)
        elif args.dep_cmd == "add":
            e = registry.add(Path(args.file))
            _out(e, args.json, f"registered deployment {e['id']}")
        elif args.dep_cmd == "update":
            e = registry.update(Path(args.file))
            changed = e.pop("_identity_changed", False)
            msg = f"updated deployment {e['id']}"
            if changed:
                msg += ("\n  WARNING: runtime/model/config changed — prior "
                        "qualifications for this id may no longer describe what "
                        "runs. Re-check with `aies qualification verify <QUAL-…>` "
                        "(D7).")
            _out(e, args.json, msg)
        elif args.dep_cmd == "remove":
            e = registry.remove(args.name)
            _out(e, args.json, f"removed deployment {e['id']} — id is now free to "
                               f"reuse (run history and QUAL records are untouched)")
        elif args.dep_cmd == "retire":
            e = registry.retire(args.name)
            _out(e, args.json, f"retired {e['id']}")
        elif args.dep_cmd == "verify-artifact":
            from . import verification
            try:
                res = verification.verify_artifact(
                    args.name, args.artifact, pubkey_path=args.pubkey,
                    sig_path=args.signature, runtime=getattr(args, "runtime", None))
            except verification.VerificationError as e:
                print(f"error: {e}", file=sys.stderr)
                return 2
            if args.json:
                _out(res, True)
            else:
                c = res["checksum"]
                cm = ("MATCH" if c["match"] else "MISMATCH" if c["match"] is False
                      else "n/a")
                print(f"verify-artifact {res['deployment']}  ({res['artifact']})")
                print(f"  checksum : {cm}  declared={c.get('declared')}  "
                      f"computed={c['computed']}"
                      + (f"\n    {c['note']}" if c.get("note") else ""))
                print(f"  signature: {res['signature']['status']}"
                      + (f" — {res['signature']['detail']}" if res['signature']['detail'] else ""))
                print(f"  => {'OK' if res['ok'] else 'NOT VERIFIED'}")
            return 0 if res["ok"] else 1
    except registry.RegistryError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_profile(args) -> int:
    args.profiles_cmd = args.prof_cmd
    return cmd_profiles(args)


def cmd_qualification(args) -> int:
    from . import qualification
    try:
        if args.qual_cmd == "history":
            recs = qualification.list_records()
            if args.deployment:
                recs = [r for r in recs if r["subject"]["deployment"] == args.deployment]
            recs = sorted(recs, key=lambda r: r.get("recorded_at", ""), reverse=True)
            _out(recs, args.json,
                 "\n".join(f"{r['recorded_at'][:19]}  {r['record_id']:16} "
                           f"{r['subject']['deployment']:20} {C.risk_tier_label(r['scope']['risk_tier']):22} "
                           f"{r['decision']:20} [{r['status']}]"
                           for r in recs) or "(no qualification history)")
            return 0
        if args.qual_cmd == "verify":
            args.record = args.record
            return cmd_verify(args)
        # list / show / revoke reuse the plural handler
        args.q_cmd = args.qual_cmd
        return cmd_qualifications(args)
    except qualification.QualificationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def cmd_conform(args) -> int:
    from . import conformance
    import yaml as _yaml
    try:
        if args.conform_cmd == "template":
            tpl = conformance.template(args.klass)
            text = _yaml.safe_dump(tpl, sort_keys=False)
            if args.out:
                Path(args.out).write_text(text, encoding="utf-8")
                _out({"written": args.out}, args.json, f"wrote {args.out}")
            else:
                print(text)
        elif args.conform_cmd == "requirements":
            reqs = conformance.ENFORCED_REQUIREMENTS
            _out(reqs, args.json,
                 "\n".join(f"{k:28} {v}" for k, v in reqs.items()))
        elif args.conform_cmd == "check":
            report = conformance.check(Path(args.file))
            if args.write:
                path = conformance.write_report(report)
                if not args.json:
                    print(f"wrote {path}")
            if args.json:
                _out(report, True)
            else:
                print(conformance.render_markdown(report))
            # Non-zero exit if an evidence-backed claim is unsupported (CI gate).
            return 0 if report["summary"]["substantiated"] else 5
        elif args.conform_cmd == "engine":
            from . import engine_conformance as ec
            corpus_dir = Path(args.corpus) if args.corpus else None
            decide_fn = ec.decision.decide
            engine_label = "reference"
            if args.engine:
                decide_fn = ec.subprocess_decider(args.engine)
                engine_label = args.engine
            try:
                report = ec.verify(corpus_dir, decide_fn=decide_fn, engine=engine_label)
            except ec.ConformanceError as e:
                print(f"error: {e}", file=sys.stderr)
                return 2
            _out(report, args.json, ec.render(report))
            # Non-zero exit if the engine is not conformant to the corpus (CI gate).
            return 0 if report["valid"] else 5
    except conformance.ConformanceError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_journey(args) -> int:
    from . import journeys
    try:
        if args.journey_cmd == "list":
            items = journeys.list_journeys()
            _out(items, args.json,
                 "\n".join(f"{j['id']:14} {j['title']}\n"
                           + "".join(f"    {C.competency_label(s['area'])}  "
                                      f"{C.identifier_label(s.get('phase')) if s.get('phase') else ''} ({s['id']})\n"
                                     for s in j["steps"])
                           for j in items) or "(no journeys)")
        elif args.journey_cmd == "show":
            j, ver = journeys.load_journey(args.id)
            j["_version"] = ver
            _out(j, args.json)
    except journeys.JourneyError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_suites(args) -> int:
    from . import suites
    root = Path(args.root) if getattr(args, "root", None) else None
    if getattr(args, "suites_cmd", None) == "calibrate":
        report = suites.calibrate(root)
        _out(report, args.json, suites.render_calibration(report))
        return 0
    if getattr(args, "suites_cmd", None) == "empirical":
        from . import empirical
        if args.create_plan:
            required = {
                "--panel-id": args.panel_id,
                "--plan-owner": args.plan_owner,
                "--plan-subjects": args.plan_subjects,
                "--plan-areas": args.plan_areas,
                "--ability-basis": args.ability_basis,
                "--rating-protocol-id": args.rating_protocol_id,
                "--rating-protocol-basis": args.rating_protocol_basis,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                print("error: creating a panel plan requires " + ", ".join(missing),
                      file=sys.stderr)
                return 2
            subjects = []
            for item in args.plan_subjects:
                if "=" not in item:
                    print(f"error: --plan-subjects expects SUBJECT=ABILITY, got {item!r}",
                          file=sys.stderr)
                    return 2
                subject, ability = item.rsplit("=", 1)
                try:
                    rank = int(ability)
                except ValueError:
                    print(f"error: ability must be an integer, got {ability!r}",
                          file=sys.stderr)
                    return 2
                subjects.append({"subject": subject, "ability": rank})
            try:
                plan = empirical.create_panel_plan(
                    panel_id=args.panel_id, human_owner=args.plan_owner,
                    subjects=subjects, areas=args.plan_areas,
                    risk_tier=f"RT{args.plan_rt}", repeats=args.plan_repeats,
                    ability_basis=args.ability_basis,
                    rating_protocol_id=args.rating_protocol_id,
                    rating_protocol_basis=args.rating_protocol_basis)
            except (ValueError, FileNotFoundError) as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
            Path(args.create_plan).write_text(
                json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            _out(plan, args.json,
                 f"wrote {args.create_plan}\n{empirical.render_panel_plan(plan)}")
            return 0
        if args.preflight_runs:
            report = empirical.preflight_runs(
                [{"run_id": run_id,
                  "rating_protocol_basis": args.rating_protocol_basis}
                 for run_id in args.preflight_runs])
            _out(report, args.json, empirical.render_preflight(report))
            return 0  # advisory inspection; readiness is explicit in the artifact
        if args.panel_plan:
            if not args.planned_runs:
                print("error: --panel-plan requires --planned-runs SUBJECT=RUN_ID ...",
                      file=sys.stderr)
                return 2
            try:
                plan = json.loads(Path(args.panel_plan).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"error: cannot read panel plan: {exc}", file=sys.stderr)
                return 2
            assignments = {}
            for item in args.planned_runs:
                if "=" not in item:
                    print(f"error: --planned-runs expects SUBJECT=RUN_ID, got {item!r}",
                          file=sys.stderr)
                    return 2
                subject, run_id = item.split("=", 1)
                if subject in assignments:
                    print(f"error: duplicate planned subject {subject!r}", file=sys.stderr)
                    return 2
                assignments[subject] = run_id
            try:
                panel = empirical.assemble_panel_from_plan(plan, assignments)
            except (ValueError, FileNotFoundError) as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
            if args.write_panel:
                Path(args.write_panel).write_text(
                    json.dumps(panel, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
                if not args.json:
                    print(f"wrote assembled panel to {args.write_panel}")
            if not args.panel_id:
                args.panel_id = plan.get("panel_id")
        elif args.runs:
            specs = []
            for spec in args.runs:
                if "=" not in spec:
                    print(f"error: --runs expects RUN_ID=ABILITY, got {spec!r}", file=sys.stderr)
                    return 2
                run_id, ability = spec.rsplit("=", 1)
                try:
                    rank = int(ability)
                except ValueError:
                    print(f"error: ability must be an integer, got {ability!r}",
                          file=sys.stderr)
                    return 2
                specs.append({"run_id": run_id, "ability": rank,
                              "ability_basis": args.ability_basis,
                              "preregistered_at": args.preregistered_at,
                              "rating_protocol_basis": args.rating_protocol_basis})
            try:
                panel = empirical.assemble_panel_from_runs(specs)
            except (ValueError, FileNotFoundError) as e:
                print(f"error: {e}", file=sys.stderr)
                return 2
            if args.write_panel:
                Path(args.write_panel).write_text(json.dumps(panel, indent=2), encoding="utf-8")
                if not args.json:
                    print(f"wrote assembled panel to {args.write_panel}")
        elif args.panel:
            panel = json.loads(Path(args.panel).read_text(encoding="utf-8"))
        else:
            print("error: pass a panel JSON file, --panel-plan with --planned-runs, "
                  "--runs RUN=ABILITY ..., --preflight-runs RUN_ID ..., or "
                  "--create-plan", file=sys.stderr)
            return 2
        report = empirical.analyze_panel(panel, panel_id=args.panel_id)
        _out(report, args.json, empirical.render(report))
        return 0
    report = suites.validate(root)
    _out(report, args.json, suites.render(report))
    return 0 if report["valid"] else 1


def cmd_dashboard(args) -> int:
    from . import dashboard
    if args.write:
        path = dashboard.write_dashboard()
        _out({"dashboard": path}, args.json, f"wrote {path}")
    else:
        print(dashboard.render_dashboard())
    return 0


def _not_yet(milestone: str):
    def handler(_args) -> int:
        print(f"this verb arrives with milestone {milestone} "
              "(docs/PLATFORM.md §10)", file=sys.stderr)
        return 3
    return handler


_EPILOG = """\
TRY AIES NOW
  aies demo --open                            complete offline product tour; no key/server
  aies init                                   safe workspace + exact next commands
  aies evaluate SUBJECT --judge JUDGE --plan-only
                                               preview scope/calls/limits; execute nothing
  aies evaluate SUBJECT --judge JUDGE          automated evaluation -> ECM + fit + reports
  aies snapshot latest                         evidence -> capability -> confidence -> decisions
  aies support                                 implemented vs experimental vs planned subjects
  aies starter list                            choose a decision-led first workflow
  aies starter show understand-deployment      exact commands, limits, time/cost class
  aies open latest                             open the result

commands by stage (each group alphabetical):
  setup & discovery   completion · demo · deployment · discover · doctor · init · runtime · starter · support
  engineering eval    assessment · benchmark · capabilities · compare · evaluate · export · import · open · qualify · review · runs · score · snapshot · transcript
  interoperability    bridge inspect-import · bridge sarif-import
  judging             judge available · judge history · judge list   (the judge pool + track record)
  governance & audit  audit · conform · corpus · dashboard · grant · qualification · report · serve · verify
  reference           index · journey · plugins · profile · suites

typical workflow:
  aies doctor                                  validate env, detect runtimes
  aies discover                                register the deployments they serve
  # automated (recommended): one command in, a scored report out
  aies qualify <deployment> --profile coder --rt 2 --area CA-05 --judge <judge-dep>
                                               auto-score with a judge model -> report
  aies transcript <run>                        read the whole run: task + answer + score per item

  # optional manual scoring — omit --judge:
  aies qualify <deployment> --profile enterprise --rt 2 --area CA-05
  aies score <run>                             ingest scores -> analysis + report bundle

  # re-score a run you already collected (e.g. the judge failed) — no re-collect:
  aies review <run> --model-reviewer <judge> --parallel 8
                                               score -> analysis + report bundle

  # benchmark uses the same non-blocking automated path:
  aies benchmark <deployment> --all-areas --judge <judge-dep> --parallel 8

  # bring external eval results in as EV evidence (automated rater):
  aies import <run> eval.json                  ingest -> analysis + report bundle

  # profile a deployment across the whole SDLC (planner/coder/security/…):
  aies qualify <deployment> --all-areas --rt 2 --judge <judge-dep>
  aies snapshot <run>                          compact terminal decision view
  aies capabilities <run>                      Engineering Capability Matrix

  # run a declarative assessment -> non-blocking engineering result:
  aies assessment list                         the shipped assessments (enterprise, coder, security, …)
  aies qualify <deployment> --assessment enterprise --judge <judge-dep>
  aies assessment result <run>                 COMPLETE/PARTIAL/NOT SCORED

  # formal qualification is a separate opt-in human-governed workflow:
  aies qualify <deployment> --assessment enterprise --judge <judge-dep> --formal-qualification
  aies assessment result <run> --formal-qualification

  # see the whole thing run, fully offline (mock runtime + mock judge):
  make demo                                    core workflow (bash scripts/demo.sh)
  make demo-full                               comprehensive tour of the whole platform
  make demo-empirical                          Phase-2 harness on a synthetic panel (see discrimination)
  aies suites calibrate                        each scenario's progress as a measurement instrument
  aies suites empirical panel.json             Phase-2: discrimination from a model panel
  aies corpus health                           advisory review of the corpus itself (no single grade)
  aies corpus duplicates                       twin-aware near-duplicate detector (advisory)
  aies corpus review SC-CA07-015 --reviewer X  critique one scenario as an instrument (never rewrites)

  # optional formal record after the explicit formal protocol (human decision):
  aies grant <run> --decision grant --authority "Name (ROLE-13)" --second "Name (ROLE-14)"
  aies verify <QUAL-id>                         re-check environment (D7)
  aies conform check statement.yaml            check a conformance claim
  aies conform engine                          verify the decision engine vs the golden corpus
  aies conform engine --engine "python conformance/example_engine.py"   verify a FOREIGN engine
  aies suites validate                         validate shipped competency suites
  aies serve --port 8722                       read-only REST API over the canonical artifacts

  # audit a repository's engineering practice against AIES (maturity per area):
  aies audit .                                 scorecard + ranked recommendations
  aies audit . --gate --rt 2                   CI gate: fail if RT2 — Moderate evidence is missing
  aies ci audit . --rt 2                       retained CI evidence; advisory by default
  aies ci audit . --rt 2 --enforce             explicit opt-in policy gate

  # supply-chain provenance:
  aies deployment verify-artifact <id> --artifact model.bin   check checksum/signature

  aies qualify <deployment> --journey JOURNEY-01   run a multi-phase journey instead

CLI discovery:
  aies help                                    full command tree + workflow
  aies <command> --help                        detailed parameters for one command
  aies completion powershell                   enable Tab completion (also bash/zsh)
  platform/CLI_REFERENCE.md                    every command, parameter, prerequisite,
                                               interaction, result, and next step

The platform prepares evidence; a human records every grant. Docs: platform/GUIDE.md.
Stuck (timeout, TLS, auth, slow run, judge)? platform/TROUBLESHOOTING.md.
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=("AIES Engineering Assessment Platform — executable reference "
                     "implementation of AESQS (docs/PLATFORM.md, AIES-DOC-06). "
                     "Prepares evidence; never grants: humans hold qualification "
                     "authority."),
        epilog=_EPILOG,
    )
    p.add_argument("--version", action="version", version=f"aies-platform {__version__}")
    sub = p.add_subparsers(dest="cmd", metavar="<command>")
    sub.add_parser("help", help="show this help and the typical workflow")

    def common(sp):
        sp.add_argument("--json", action="store_true", help="machine-readable output")
        return sp

    init = common(sub.add_parser(
        "init", help="create a safe AIES workspace and print exact next steps"))
    init.add_argument(
        "path", nargs="?", default="aies-workspace",
        help="workspace directory to create (default: ./aies-workspace)")
    init.add_argument(
        "--starter-manifest", action="store_true",
        help="also create a non-secret OpenAI-compatible deployment example")
    init.set_defaults(func=cmd_init)

    demo = common(sub.add_parser(
        "demo", help="run the complete offline Engineering Evaluation story"))
    demo.add_argument(
        "--workspace", default="aies-demo-workspace",
        help="persistent demo workspace (default: ./aies-demo-workspace)")
    demo.add_argument(
        "--parallel", type=int, default=8, metavar="N",
        help="maximum concurrent mock calls (default: 8)")
    demo.add_argument(
        "--open", action="store_true",
        help="open the Executive Summary in the default browser when complete")
    demo.set_defaults(func=cmd_demo)

    common(sub.add_parser("doctor", help="validate the environment and detect runtimes")
           ).set_defaults(func=cmd_doctor)

    common(sub.add_parser("discover", help="scan runtimes and register the "
                          "deployments they serve")).set_defaults(func=cmd_discover)

    evaluate = common(sub.add_parser(
        "evaluate", help="plan and run a beginner-friendly automated Engineering Evaluation"))
    evaluate.add_argument("subject", help="registered deployment id or unambiguous model name")
    scope = evaluate.add_mutually_exclusive_group()
    scope.add_argument(
        "--assessment", default=None, metavar="NAME",
        help="bounded assessment (default: coder unless --area/--all-areas is used)")
    scope.add_argument(
        "--all-areas", action="store_true",
        help="evaluate all CA-01 through CA-12 areas")
    evaluate.add_argument(
        "--area", action="append", default=None, metavar="CA-NN",
        help="evaluate one competency area; repeat for more")
    evaluate.add_argument(
        "--rt", type=int, choices=(1, 2, 3, 4), default=1,
        help="risk tier (default RT1 — Minimal for a bounded first run)")
    evaluate.add_argument(
        "--judge", default=None, metavar="DEPLOYMENT",
        help="automated reviewer deployment (default: AIES_JUDGE)")
    evaluate.add_argument(
        "--judge-batch-size", type=int, default=None, metavar="N",
        help="responses per reviewer call (default 8 or AIES_JUDGE_BATCH_SIZE)")
    evaluate.add_argument(
        "--parallel", type=int, default=1, metavar="N",
        help="maximum concurrent candidate and judge calls (default: 1)")
    evaluate.add_argument(
        "--runtime", default=None,
        help="disambiguate the assessed deployment runtime")
    evaluate.add_argument(
        "--reviewer-runtime", default=None,
        help="disambiguate the reviewer deployment runtime")
    evaluate.add_argument(
        "--plan-only", action="store_true",
        help="show calls, concurrency, estimates, and limitations without executing")
    evaluate.add_argument(
        "--open", action="store_true",
        help="open the Executive Summary in the default browser after completion")
    evaluate.set_defaults(func=cmd_evaluate)

    opn = common(sub.add_parser(
        "open", help="open a run result or export share-safe derived views"))
    opn.add_argument(
        "run", nargs="?", default="latest",
        help="run id or 'latest' (default: latest)")
    opn.add_argument(
        "--no-browser", action="store_true",
        help="print the local result link without launching a browser")
    opn.add_argument(
        "--export-redacted", nargs="?", const="AUTO", default=None,
        metavar="ZIP",
        help="also create an immutable redacted ZIP at ZIP or the default exports path")
    opn.set_defaults(func=cmd_open)

    snap = common(sub.add_parser(
        "snapshot",
        help="show evidence, capability, confidence, and engineering decisions"))
    snap.add_argument(
        "run", nargs="?", default="latest",
        help="completed run id or 'latest' (default: latest)")
    snap.add_argument(
        "--observed-only", action="store_true",
        help="hide tasks without directly mapped scored evidence")
    snap.set_defaults(func=cmd_snapshot)

    support = common(sub.add_parser(
        "support",
        help="show implemented, experimental, and planned subject support"))
    support.add_argument(
        "subject_kind", nargs="?", default=None,
        help="subject id or alias to inspect (default: show all)")
    support.add_argument(
        "--status", choices=("implemented", "experimental", "planned"),
        default=None, help="filter by support status")
    support.set_defaults(func=cmd_support)

    starter = common(sub.add_parser(
        "starter",
        help="choose a decision-led evaluation, comparison, audit, or governance workflow"))
    starter_sub = starter.add_subparsers(dest="starter_cmd", required=True)
    starter_list = starter_sub.add_parser(
        "list", help="list the shipped decision-oriented starters")
    starter_list.add_argument(
        "--json", action="store_true", help="machine-readable output")
    starter_list.set_defaults(func=cmd_starter)
    starter_show = starter_sub.add_parser(
        "show", help="show prerequisites, commands, artifacts, and limitations")
    starter_show.add_argument("starter_id", help="starter id from `aies starter list`")
    starter_show.add_argument(
        "--json", action="store_true", help="machine-readable output")
    starter_show.set_defaults(func=cmd_starter)

    bridge = common(sub.add_parser(
        "bridge", help="import versioned external evidence with provenance and loss reports"))
    bridge_sub = bridge.add_subparsers(dest="bridge_cmd", required=True)
    inspect_import = bridge_sub.add_parser(
        "inspect-import", help="import an AIES-profiled Inspect EvalLog JSON")
    inspect_import.add_argument("run", help="existing AIES run receiving EV observations")
    inspect_import.add_argument("file", help="Inspect EvalLog JSON export")
    inspect_import.add_argument(
        "--source", default=None,
        help="optional source/rater label (default binds filename and digest)")
    inspect_import.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    inspect_export = bridge_sub.add_parser(
        "inspect-export", help="export a run to the AIES Inspect JSON profile")
    inspect_export.add_argument("run", help="AIES run to export")
    inspect_export.add_argument("--out", required=True, help="new JSON output path")
    inspect_export.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    sarif_import = bridge_sub.add_parser(
        "sarif-import", help="normalize SARIF 2.1.0 findings without claim inflation")
    sarif_import.add_argument("file", help="SARIF 2.1.0 JSON file")
    sarif_import.add_argument(
        "--out", default=None, help="output artifact (default: workspace imports)")
    sarif_import.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    sarif_export = bridge_sub.add_parser(
        "sarif-export", help="export normalized repository findings as SARIF 2.1.0")
    sarif_export.add_argument("file", help="aies-sarif-evidence/v1 JSON artifact")
    sarif_export.add_argument("--out", required=True, help="new SARIF output path")
    sarif_export.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    bridge.set_defaults(func=cmd_bridge)

    reg = common(sub.add_parser("registry", help="manage candidate deployment entries"))
    regsub = reg.add_subparsers(dest="registry_cmd", required=True)
    radd = regsub.add_parser("add", help="register a candidate deployment from YAML")
    radd.add_argument("file", help="deployment YAML file to register")
    rlist = regsub.add_parser("list", help="list active candidate deployments")
    rlist.add_argument("--all", action="store_true",
                       help="include retired deployment entries")
    rshow = regsub.add_parser("show", help="show one candidate deployment")
    rshow.add_argument("model", help="deployment id, or an unambiguous model name")
    rret = regsub.add_parser("retire", help="retire a deployment without deleting history")
    rret.add_argument("model", help="deployment id, or an unambiguous model name")
    for x in (radd, rlist, rshow, rret):
        x.add_argument("--json", action="store_true",
                       help="emit machine-readable JSON")
    reg.set_defaults(func=cmd_registry)

    q = common(sub.add_parser(
        "qualify", help="run engineering evaluation for one deployment; "
        "formal qualification is explicit"))
    q.add_argument("model", nargs="?", help="deployment id, or model name")
    q.add_argument("--runtime", default=None,
                   help="disambiguate when a model has several deployments")
    q.add_argument("--assessment", default=None, metavar="NAME",
                   help="run a declarative assessment (assessments/NAME.yaml): its "
                        "competency set, profile, risk tier, and sampling (ADR-0005). "
                        "Authoritative — sets --area/--profile; --rt/--repeats override it")
    q.add_argument("--profile", default="enterprise",
                   help="EV weighting profile (default: enterprise; overridden by --assessment)")
    q.add_argument("--rt", type=int, choices=(1, 2, 3, 4), default=None,
                   help="scoped risk tier (default RT2 — Moderate, or the assessment's tier)")
    q.add_argument("--area", action="append", default=None,
                   help="competency area (repeatable); default CA-05")
    q.add_argument("--all-areas", action="store_true",
                   help="qualify across ALL competency areas CA-01…CA-12 "
                        "(a full SDLC capability profile; see `aies capabilities`)")
    q.add_argument("--decisional", action="store_true",
                   help="require the distinct-scenario plan for every selected area to meet "
                        "the AESQS sample minimum when admitted ratings are available")
    q.add_argument(
        "--formal-qualification", action="store_true",
        help="explicitly run the human-governed formal qualification path; "
             "without this flag, automated engineering evaluation is non-blocking")
    q.add_argument("--journey", default=None, metavar="JOURNEY_ID",
                   help="run a multi-phase journey instead of area suites")
    q.add_argument("--judge", default=None, metavar="DEPLOYMENT",
                   help="auto-score responses with this judge deployment (or 'self') "
                        "and print the report directly — no manual scoring. "
                        "Defaults to $AIES_JUDGE.")
    q.add_argument("--judge-batch-size", type=int, default=None, metavar="N",
                   help="responses per automated judge request (default 8, or "
                        "$AIES_JUDGE_BATCH_SIZE; automatically bounded by context)")
    q.add_argument("--consider-advisory-review", action="store_true",
                   help="record that a human considered the automated reviewer scores in the generated report")
    q.add_argument("--human-evaluation", default=None, metavar="NAME",
                   help="record a named qualitative or scored human evaluation in the generated report")
    q.add_argument("--reviewer-runtime", default=None,
                   help="disambiguate the judge deployment's runtime")
    q.add_argument("--repeats", type=int, default=None,
                   help="explicit repeats for a separate stability study; repeats do not "
                        "substitute for distinct scenario breadth")
    q.add_argument("--parallel", type=int, default=None, metavar="N",
                   help="concurrent inference calls for BOTH response collection "
                        "and judge scoring (default 1, or $AIES_PARALLEL; records "
                        "are written in canonical order regardless)")
    q.add_argument("--resume", metavar="RUN_ID",
                   help="aggregate a scored run into the evidence package")
    q.add_argument("--resume-collection", metavar="RUN_ID",
                   help="fill only the missing responses of a partially-collected "
                        "run (e.g. after an endpoint failure), then rebuild the scoresheet")
    q.set_defaults(func=lambda a: (_qualify_defaults(a), cmd_qualify(a))[1])

    b = common(sub.add_parser(
        "benchmark", help="run a non-blocking engineering benchmark; "
        "optionally auto-score and report"))
    b.add_argument("model", help="deployment id, or model name when unambiguous")
    b.add_argument("--profile", default="enterprise",
                   help="EV weighting profile (default: enterprise)")
    b.add_argument("--rt", type=int, choices=(1, 2, 3, 4), default=2,
                   help="scoped risk tier number (default: 2 for RT2 — Moderate)")
    b.add_argument("--area", action="append", default=None,
                   help="competency area code such as CA-05; repeat for more areas")
    b.add_argument("--all-areas", action="store_true",
                   help="benchmark across ALL competency areas CA-01…CA-12")
    b.add_argument("--repeats", type=int, default=None,
                   help="repeat each scenario for a stability study; repeats do not add breadth")
    b.add_argument("--parallel", type=int, default=None, metavar="N",
                   help="maximum concurrent inference calls (default: 1 or AIES_PARALLEL)")
    b.add_argument("--runtime", default=None,
                   help="runtime name used to disambiguate the deployment")
    b.add_argument("--judge", default=None, metavar="DEPLOYMENT",
                   help="auto-score with this judge and complete analysis/reporting "
                        "(or 'self'; defaults to $AIES_JUDGE)")
    b.add_argument("--judge-batch-size", type=int, default=None, metavar="N",
                   help="responses per automated judge request (default 8, or "
                        "$AIES_JUDGE_BATCH_SIZE)")
    b.add_argument("--reviewer-runtime", default=None,
                   help="disambiguate the judge deployment's runtime")
    b.add_argument("--human-evaluation", default=None, metavar="NAME",
                   help="optionally record a named human evaluation; never required")
    b.add_argument("--consider-advisory-review", action="store_true",
                   help="optionally record that a human considered automated scores")
    b.set_defaults(func=lambda a: (_qualify_defaults(a), cmd_benchmark(a))[1])

    s = common(sub.add_parser("score", help="ingest a filled scoresheet (human or model rater)"))
    s.add_argument("run", help="run id whose completed scoresheet will be ingested")
    s.add_argument("--file", help="scoresheet path (default: the run's scoresheet.json)")
    s.set_defaults(func=cmd_score)

    rr = common(sub.add_parser(
        "rater", help="manage durable human-rater qualification/calibration records"))
    rrsub = rr.add_subparsers(dest="rater_cmd", required=True)
    rreg = rrsub.add_parser("register", help="register one qualified human rater")
    rreg.add_argument("--id", required=True,
                      help="durable human-rater identifier")
    rreg.add_argument("--name", required=True,
                      help="human rater's display name")
    rreg.add_argument("--area", action="append", required=True, metavar="CA-NN",
                      help="qualified competency area; repeat for additional areas")
    rreg.add_argument("--rt", action="append", required=True, type=int,
                      choices=(1, 2, 3, 4),
                      help="qualified risk-tier number; repeat for additional tiers")
    rreg.add_argument("--qualified-until", required=True, metavar="ISO-8601",
                      help="qualification expiry timestamp")
    rreg.add_argument("--calibration-valid-until", required=True, metavar="ISO-8601",
                      help="rating-calibration expiry timestamp")
    rreg.add_argument("--anchor-version", required=True,
                      help="version of the anchor-artifact set used for calibration")
    rreg.add_argument("--calibration-method",
                      default="human-consensus-anchor-session",
                      help="documented calibration method")
    rreg.add_argument("--registered-by", required=True,
                      help="named human registry authority")
    rreg.add_argument("--json", action="store_true",
                      help="emit machine-readable JSON")
    rreg.set_defaults(func=cmd_rater)
    rlist = rrsub.add_parser("list", help="list registered human raters")
    rlist.add_argument("--json", action="store_true",
                       help="emit machine-readable JSON")
    rlist.set_defaults(func=cmd_rater)
    rshow = rrsub.add_parser("show", help="show one human-rater record")
    rshow.add_argument("id", help="durable human-rater identifier")
    rshow.add_argument("--json", action="store_true",
                       help="emit machine-readable JSON")
    rshow.set_defaults(func=cmd_rater)

    rs = common(sub.add_parser(
        "resolve", help="record an immutable human disposition for a divergent item"))
    rs.add_argument("run", help="run id containing the divergent response")
    rs.add_argument("response", help="response record filename, for example SC-CA05-001-r1.json")
    rs.add_argument("--scores", required=True, nargs=6, type=int,
                    choices=(0, 1, 2, 3, 4),
                    metavar=("EV1", "EV2", "EV3", "EV4", "EV5", "EV6"),
                    help="six resolved integer ratings in EV1 through EV6 order")
    rs.add_argument("--resolver", required=True, help="named human resolver")
    rs.add_argument("--resolver-id", required=True,
                    help="durable id from `aies rater register`")
    rs.add_argument("--rationale", required=True,
                    help="reasoned human disposition explaining the resolution")
    rs.add_argument("--conflict-free", action="store_true", required=True,
                    help="declare independence from the assessed subject")
    rs.set_defaults(func=cmd_resolve)

    im = common(sub.add_parser("import", help="import external eval results "
                               "(EV1–EV6 JSON) into a run as automated ratings"))
    im.add_argument("run", help="run id that will receive the imported rating observations")
    im.add_argument("file", help="eval file: JSON {source?, items:[{scenario_id, "
                    "repeat?, scores:{EV1..EV6}, findings?}]}")
    im.add_argument("--source", default=None,
                    help="label for the rater (default: the file's `source` field)")
    im.set_defaults(func=cmd_import)

    ex = common(sub.add_parser("export", help="export a run's responses+scores to "
                               "a generic eval-log JSON (round-trips with import)"))
    ex.add_argument("run", help="run id to export")
    ex.add_argument("--write", action="store_true",
                    help="write eval-log.json into the run directory (else stdout)")
    ex.set_defaults(func=cmd_export)

    r = common(sub.add_parser("report", help="render an evidence package"))
    r.add_argument("run", help="aggregated run id whose evidence package will be rendered")
    r.add_argument("--format", choices=("markdown", "json", "html"), default="markdown",
                   help="output representation (default: markdown)")
    r.add_argument("--write", action="store_true",
                   help="write the report into the run directory instead of stdout")
    r.set_defaults(func=cmd_report)

    common(sub.add_parser("index", help="rebuild the result index from run files")
           ).set_defaults(func=cmd_index)

    tr = common(sub.add_parser("transcript", help="read a whole run in one view: "
                               "task + answer + scores per item"))
    tr.add_argument("run", help="run id to render as a task/answer/score transcript")
    tr.add_argument("--area", default=None, help="only this competency area")
    tr.add_argument("--format", choices=("markdown", "json"), default="markdown",
                    help="output representation (default: markdown)")
    tr.add_argument("--write", action="store_true",
                    help="write transcript.md into the run directory")
    tr.set_defaults(func=cmd_transcript)

    cap = common(sub.add_parser(
        "capabilities", help="render the Engineering Capability Matrix for an "
        "aggregated run/deployment"))
    cap.add_argument("ref", help="run id, or deployment id (its latest aggregated run)")
    cap.add_argument(
        "--ecm", action="store_true",
        help="compatibility alias; ECM is now the default capability view")
    cap.add_argument(
        "--qualification-profile", action="store_true",
        help="render the separate formal per-area CL/autonomy qualification view")
    cap.add_argument("--format", choices=("markdown", "json", "html"), default="markdown", help="ECM output format (default: markdown)")
    cap.add_argument("--write", action="store_true",
                     help="write ECM output beside the run")
    cap.set_defaults(func=cmd_capabilities)

    gd = common(sub.add_parser(
        "guidance", help="render engineering fit from ECM evidence; supply a "
        "Qualification Record for bounded deployment guidance"))
    gd.add_argument("ref", help="aggregated run id, or deployment id")
    gd.add_argument("--qualification", metavar="QUAL-ID",
                    help="active human Qualification Record; switches from "
                         "engineering fit to governed Deployment Guidance")
    gd.add_argument("--role", choices=tuple(C.ROLE_NAMES),
                    help="requested engineering role; must match the qualification scope")
    gd.add_argument("--phase", action="append", choices=tuple(C.PHASE_NAMES),
                    help="requested SDLC phase; repeat for additional phases")
    gd.add_argument("--autonomy", type=int, choices=(0, 1, 2, 3, 4),
                    help="requested autonomy level number (for example 2 for AL2 — Collaborative)")
    gd.add_argument("--write", action="store_true", help="write Deployment Guidance Markdown, JSON, and HTML beside the run")
    gd.set_defaults(func=cmd_guidance)

    au = common(sub.add_parser("audit", help="audit a repository's conformance to "
                               "AIES engineering practices (maturity per area; "
                               "verified/asserted/gap; ADR-0004)"))
    au.add_argument("repo", help="path to the repository to audit")
    au.add_argument("--rt", type=int, choices=(1, 2, 3, 4), default=None,
                    help="evaluate against this risk tier's required evidence")
    au.add_argument("--gate", action="store_true",
                    help="CI mode: non-zero exit if RT-required evidence is missing "
                         "(implies the given --rt, default RT2 — Moderate)")
    au.add_argument("--attest", default=None, metavar="FILE",
                    help="attestation JSON for non-detectable practices "
                         "({items:[{id, evidence}]})")
    au.add_argument("--format", choices=("markdown", "json"), default="markdown",
                    help="output representation (default: markdown)")
    au.set_defaults(func=lambda a: (setattr(a, "rt", a.rt or (2 if a.gate else None)),
                                    cmd_audit(a))[1])

    ci = common(sub.add_parser(
        "ci", help="CI evidence integrations; advisory unless enforcement is explicit"))
    cisub = ci.add_subparsers(dest="ci_cmd", required=True)
    cia = common(cisub.add_parser(
        "audit", help="retain repository-assessment evidence and annotations"))
    cia.add_argument("repo", nargs="?", default=".",
                     help="repository path to inspect (default: current directory)")
    cia.add_argument("--rt", type=int, choices=(1, 2, 3, 4), default=2,
                     help="risk tier policy to calculate (default: RT2 — Moderate)")
    cia.add_argument("--enforce", action="store_true",
                     help="explicitly fail CI when required evidence is missing; "
                          "without this flag the command is advisory")
    cia.add_argument("--attest", metavar="FILE",
                     help="optional attestation JSON for non-detectable practices")
    cia.add_argument("--out", default="aies-ci", metavar="DIR",
                     help="artifact directory (default: aies-ci)")
    cia.add_argument("--github-annotations", action="store_true",
                     help="emit GitHub Actions notice/warning workflow commands")
    cia.set_defaults(func=cmd_ci)

    asm = common(sub.add_parser(
        "assessment", help="declarative assessments (ADR-0005): "
        "list/show/validate and render engineering or formal results"))
    asmsub = asm.add_subparsers(dest="assessment_cmd", required=True)
    asmsub.add_parser("list", help="list shipped assessments and their validity")
    asm_show = asmsub.add_parser("show", help="print a validated assessment")
    asm_show.add_argument("name", help="assessment name")
    asm_val = asmsub.add_parser("validate", help="validate an assessment (name or path)")
    asm_val.add_argument("name", help="assessment name or YAML path")
    asm_res = asmsub.add_parser(
        "result", help="render a non-blocking engineering assessment result "
        "(use --formal-qualification for the governed qualification decision)")
    asm_res.add_argument("run", help="aggregated run composed under an assessment")
    asm_res.add_argument("--format", choices=("markdown", "html"), default="markdown",
                         help="render the canonical result as markdown (default) or HTML")
    asm_res.add_argument("--out", help="write HTML to this file instead of stdout")
    asm_res.add_argument(
        "--formal-qualification", action="store_true",
        help="render the canonical human-governed PASS/FAIL/INCONCLUSIVE/"
             "INSUFFICIENT EVIDENCE result and use it as the command exit gate")
    for x in (asm_show, asm_val, asm_res):
        x.add_argument("--json", action="store_true",
                       help="emit machine-readable JSON")
    asmsub.choices["list"].add_argument("--json", action="store_true",
                                        help="emit machine-readable JSON")
    asm.set_defaults(func=cmd_assessment)

    pr = common(sub.add_parser("profiles", help="list/show/validate weighting profiles"))
    prsub = pr.add_subparsers(dest="profiles_cmd", required=True)
    prsub.add_parser("list", help="list available weighting profiles").add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    prs = prsub.add_parser("show", help="show one weighting profile")
    prs.add_argument("name", help="profile name")
    prs.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    prv = prsub.add_parser("validate", help="validate one weighting profile")
    prv.add_argument("name", help="profile name or YAML path")
    prv.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    pr.set_defaults(func=cmd_profiles)

    common(sub.add_parser("plugins", help="list installed runtime adapters")
           ).set_defaults(func=cmd_plugins)

    comp = sub.add_parser(
        "completion",
        help="generate Tab completion for PowerShell, Bash, or Zsh")
    comp.add_argument(
        "shell", choices=("powershell", "bash", "zsh"),
        help="shell whose sourceable completion definition will be printed")
    comp.set_defaults(func=cmd_completion)

    cp = common(sub.add_parser(
        "compare", help="compare two runs/deployments using compatible observed ECM evidence"))
    cp.add_argument("a", help="run id or model registry id (latest aggregated run)")
    cp.add_argument("b", help="run id or model registry id (latest aggregated run)")
    cp.add_argument("--format", choices=("markdown", "json"), default="markdown",
                    help="output representation (default: markdown)")
    cp.add_argument("--ecm", action="store_true",
                    help="compatibility alias; task-level ECM comparison is now the default")
    cp.add_argument(
        "--area-summary", action="store_true",
        help="render the legacy competency-area aggregate comparison instead of ECM")
    cp.add_argument(
        "--formal-qualification", action="store_true",
        help="require demonstrated tasks and the human-rater protocol; default "
             "ECM comparison uses compatible observed engineering evidence")
    cp.set_defaults(func=cmd_compare)

    rn = common(sub.add_parser("runs", help="result history: list runs"))
    rnsub = rn.add_subparsers(dest="runs_cmd", required=True)
    rl = rnsub.add_parser("list", help="list recorded runs")
    rl.add_argument("--model", default=None,
                    help="filter by deployment id or model identifier")
    rl.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON")
    rp = rnsub.add_parser("progress", help="show detailed durable progress for a run")
    rp.add_argument("run", help="run id whose durable progress will be shown")
    rp.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON")
    rn.set_defaults(func=cmd_runs)

    rv = common(sub.add_parser("review", help="assemble a multi-deployment peer-review package"))
    rv.add_argument("run", help="run id whose responses will be reviewed")
    rv.add_argument("--reviewer", default="reviewer-model",
                    help="label for the reviewer model")
    rv.add_argument("--model-reviewer", default=None, metavar="DEPLOYMENT",
                    help="drive this reviewer deployment to score the responses "
                         "before assembling the package")
    rv.add_argument("--reviewer-runtime", default=None,
                    help="disambiguate the reviewer deployment's runtime")
    rv.add_argument("--parallel", type=int, default=None, metavar="N",
                    help="concurrent reviewer calls when using --model-reviewer "
                         "(default 1, or $AIES_PARALLEL)")
    rv.add_argument("--judge-batch-size", type=int, default=None, metavar="N",
                    help="responses per reviewer request (default 8, or "
                         "$AIES_JUDGE_BATCH_SIZE; automatically bounded by context)")
    rv.add_argument("--reviewer-qualified", action="store_true",
                    help="the reviewer holds a current review-class (CA-06) qualification")
    rv.add_argument("--calibration", default=None,
                    help="JSON {model:[...], human_anchor:[...]} for bootstrap calibration")
    rv.add_argument("--consider-advisory-review", action="store_true",
                    help="record that a human considered the advisory automated-review scores")
    rv.add_argument("--human-evaluation", default=None, metavar="NAME",
                    help="record a named qualitative or scored human evaluation; no grant required")
    rv.set_defaults(func=cmd_review)

    gr = common(sub.add_parser("grant", help="record a human qualification decision"))
    gr.add_argument("run", help="decisional, gate-passing run used as qualification evidence")
    gr.add_argument("--decision", choices=("grant", "grant-with-conditions", "deny"),
                    required=True,
                    help="human authority's recorded qualification decision")
    gr.add_argument("--authority", required=True, help="named human authority (ROLE-13)")
    gr.add_argument("--assessor", default=None,
                    help="named human assessor (defaults to authority)")
    gr.add_argument("--assessor-id", default=None,
                    help="durable assessor id from `aies rater register`")
    gr.add_argument("--peer-reviewer", default=None,
                    help="named independent human peer reviewer")
    gr.add_argument("--peer-reviewer-id", default=None,
                    help="durable peer id from `aies rater register`")
    gr.add_argument("--assessor-conflict-free", action="store_true",
                    help="assessor declares no conflict with the subject")
    gr.add_argument("--peer-conflict-free", action="store_true",
                    help="peer reviewer declares no conflict with the subject")
    gr.add_argument("--role", choices=tuple(C.ROLE_NAMES),
                    help="qualified engineering role, for example ROLE-06")
    gr.add_argument("--phase", action="append", choices=tuple(C.PHASE_NAMES),
                    help="SDLC phase in scope; repeat for additional phases")
    gr.add_argument("--sponsor", help="named accountable qualification sponsor")
    gr.add_argument("--framework-version",
                    help="applied AIES-AESQS-CF-01 competency-framework version")
    gr.add_argument("--agent-definition-version",
                    help="applicable ART-14 agent-definition version")
    gr.add_argument("--valid-from", metavar="ISO-8601",
                    help="start of the qualification validity window")
    gr.add_argument("--valid-until", metavar="ISO-8601",
                    help="end of the qualification validity window")
    gr.add_argument("--second", default=None,
                    help="deprecated peer-reviewer name alias for legacy v4 records")
    gr.add_argument("--condition", action="append", default=None,
                    help="condition (repeatable; required for grant-with-conditions)")
    gr.add_argument("--rationale", default=None,
                    help="human authority's reasoned decision rationale")
    gr.add_argument("--consider-advisory-review", action="store_true",
                    help="attest that the authority considered available advisory model-review scores")
    gr.add_argument("--human-evaluation", default=None, metavar="NAME",
                    help="named human evaluator whose qualitative or scored review was considered")
    gr.set_defaults(func=cmd_grant)

    vf = common(sub.add_parser("verify", help="verify a grant against the current "
                               "environment (D7); invalidates on fingerprint change"))
    vf.add_argument("record", help="qualification record id to verify")
    vf.set_defaults(func=cmd_verify)

    qz = common(sub.add_parser(
        "qualifications",
        help="list/show qualification records or append governed lifecycle events"))
    qzsub = qz.add_subparsers(dest="q_cmd", required=True)
    qzsub.add_parser("list", help="list qualification records").add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    qzs = qzsub.add_parser("show", help="show one qualification record")
    qzs.add_argument("record", help="qualification record id")
    qzs.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    qzr = qzsub.add_parser("revoke", help="append a revocation lifecycle event")
    qzr.add_argument("record", help="qualification record id")
    qzr.add_argument("--authority", required=True,
                     help="named human authority recording the revocation")
    qzr.add_argument("--reason", required=True,
                     help="reason for revocation")
    qzr.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    qze = qzsub.add_parser("event", help="append an immutable lifecycle event")
    qze.add_argument("record", help="qualification record id")
    qze.add_argument("--event", required=True,
                     choices=("condition-changed", "renewed", "suspended",
                              "invalidated", "revoked", "superseded"),
                     help="immutable lifecycle transition to append")
    qze.add_argument("--authority", required=True,
                     help="named human authority recording the event")
    qze.add_argument("--reason", required=True,
                     help="reason for the lifecycle transition")
    qze.add_argument("--condition", action="append", default=None,
                     help="replacement condition; repeat for multiple conditions")
    qze.add_argument("--valid-until", default=None, metavar="ISO-8601",
                     help="new validity end for a renewal")
    qze.add_argument("--superseded-by", default=None,
                     help="replacement qualification record id")
    qze.add_argument("--evidence-run", default=None,
                     help="decisional, gate-passing re-evaluation run for renewal")
    qze.add_argument("--peer-reviewer", default=None,
                     help="named independent human peer reviewer for renewal")
    qze.add_argument("--peer-reviewer-id", default=None,
                     help="durable peer id from `aies rater register`")
    qze.add_argument("--peer-conflict-free", action="store_true",
                     help="peer reviewer declares no conflict with the subject")
    qze.add_argument("--json", action="store_true",
                     help="emit machine-readable JSON")
    qz.set_defaults(func=cmd_qualifications)

    db = common(sub.add_parser("dashboard", help="render an HTML dashboard over runs and grants"))
    db.add_argument("--write", action="store_true",
                    help="write dashboard.html into the workspace instead of only printing its path")
    db.set_defaults(func=cmd_dashboard)

    sv = common(sub.add_parser("serve", help="thin read-only REST API over the "
                               "canonical artifacts (JSON; computes no outcomes)"))
    sv.add_argument("--host", default="127.0.0.1",
                    help="interface to bind (default: 127.0.0.1; use broader binds cautiously)")
    sv.add_argument("--port", type=int, default=8722,
                    help="TCP port for the read-only API (default: 8722)")
    sv.set_defaults(func=cmd_serve)

    cp = common(sub.add_parser("corpus", help="advisory quality review of the "
                               "assessment corpus itself (calibration, coverage, "
                               "behavioral diversity, empirical maturity); multidimensional, "
                               "never a single grade, never a gate"))
    cpsub = cp.add_subparsers(dest="corpus_cmd", required=True)
    for name, h in (("health", "full multidimensional corpus-health report + ranked "
                     "advisory recommendations"),
                    ("coverage", "the coverage dimension only — RT distribution per area "
                     "and per-assessment tier depth"),
                    ("duplicates", "near-duplicate scenario pairs (prompt/ceiling overlap), "
                     "twin-aware — flags redundancy candidates for human review"),
                    ("review-pending", "inventory pending scenario design reviews, run "
                     "deterministic structural preflight, and expose human disposition fields")):
        sc = cpsub.add_parser(name, help=h)
        sc.add_argument("--root", default=None,
                        help="competencies directory (default: shipped suites)")
        sc.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    cr = cpsub.add_parser("review", help="review one scenario as a measurement instrument: "
                          "deterministic structural checks always, plus an opt-in model "
                          "critique with --reviewer (critique only — never rewrites/approves)")
    cr.add_argument("scenario", help="scenario id (SC-CA##-###) or a YAML path")
    cr.add_argument("--reviewer", default=None,
                    help="a deployment id to critique semantically (omit for structural only)")
    cr.add_argument("--runtime", default=None,
                    help="runtime name used to disambiguate the reviewer deployment")
    cr.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON")
    cp.set_defaults(func=cmd_corpus)

    # --- resource-model noun commands (primary surface) ---------------------
    rt = common(sub.add_parser("runtime", help="inspect runtime adapters and "
                               "the runtimes behind them"))
    rtsub = rt.add_subparsers(dest="rt_cmd", required=True)
    rtsub.add_parser("list", help="list installed runtime adapters").add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    rti = rtsub.add_parser("inspect", help="inspect one runtime adapter")
    rti.add_argument("name", help="runtime adapter name")
    rti.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    rt.set_defaults(func=cmd_runtime)

    cf = common(sub.add_parser("conform", help="declare/check conformance to AIES"))
    cfsub = cf.add_subparsers(dest="conform_cmd", required=True)
    cft = cfsub.add_parser("template", help="create a conformance statement template")
    cft.add_argument("--class", dest="klass", choices=("adopter", "implementation"),
                     default="adopter",
                     help="conformance class to scaffold (default: adopter)")
    cft.add_argument("--out", default=None,
                     help="destination file; omit to print the template")
    cft.add_argument("--json", action="store_true",
                     help="emit machine-readable JSON")
    cfc = cfsub.add_parser("check", help="check a conformance statement and its evidence")
    cfc.add_argument("file", help="conformance statement YAML or JSON file")
    cfc.add_argument("--write", action="store_true",
                     help="write the conformance report beside the input")
    cfc.add_argument("--json", action="store_true",
                     help="emit machine-readable JSON")
    cfsub.add_parser("requirements", help="list conformance requirements").add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    cfe = cfsub.add_parser("engine", help="verify a decision engine against the "
                           "golden Evidence Package corpus (CONFORMANCE-POLICY.md). "
                           "Defaults to the reference engine; --engine verifies a "
                           "FOREIGN engine so independent implementations can self-check")
    cfe.add_argument("--corpus", default=None,
                     help="path to conformance/corpus (default: auto-discover)")
    cfe.add_argument("--engine", default=None,
                     help="a foreign engine command: reads {evidence,assessment} JSON on "
                          "stdin, prints the Canonical Assessment Result JSON on stdout")
    cfe.add_argument("--json", action="store_true",
                     help="emit machine-readable JSON")
    cf.set_defaults(func=cmd_conform)

    jn = common(sub.add_parser("journey", help="multi-phase journeys "
                               "(chained scenarios across the SDLC)"))
    jnsub = jn.add_subparsers(dest="journey_cmd", required=True)
    jnsub.add_parser("list", help="list available multi-phase journeys").add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    jns = jnsub.add_parser("show", help="show one multi-phase journey")
    jns.add_argument("id", help="journey id")
    jns.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    jn.set_defaults(func=cmd_journey)

    st = common(sub.add_parser("suites", help="inspect and validate competency suites"))
    stsub = st.add_subparsers(dest="suites_cmd", required=True)
    stv = stsub.add_parser("validate", help="validate suite YAML structure and coverage")
    stv.add_argument("--root", default=None,
                     help="competencies directory to validate (default: shipped suites)")
    stv.add_argument("--json", action="store_true",
                     help="emit machine-readable JSON")
    stc = stsub.add_parser("calibrate", help="calibration-coverage report — how far "
                           "each scenario has progressed as a measurement instrument "
                           "(CALIBRATION.md); advisory, never fails")
    stc.add_argument("--root", default=None,
                     help="competencies directory to inspect (default: shipped suites)")
    stc.add_argument("--json", action="store_true",
                     help="emit machine-readable JSON")
    ste = stsub.add_parser("empirical", help="analyze a model panel for per-scenario "
                           "discrimination/repeatability/twin-robustness (CALIBRATION.md "
                           "Phase 2). Give a panel JSON, or assemble one from scored runs "
                           "with --runs")
    ste.add_argument("panel", nargs="?", default=None,
                     help="panel-results JSON (panel + per-model scores)")
    ste.add_argument("--runs", nargs="+", metavar="RUN_ID=ABILITY", default=None,
                     help="assemble the panel from scored qualify runs, e.g. "
                          "--runs run-strong=3 run-mid=2 run-weak=1")
    ste.add_argument("--preflight-runs", nargs="+", metavar="RUN_ID", default=None,
                     help="inspect scored runs for panel compatibility without "
                          "inventing or requiring ability ranks")
    ste.add_argument("--ability-basis", default=None,
                     help="independent evidence used to assign every --runs ability rank")
    ste.add_argument("--preregistered-at", default=None,
                     help="timestamp showing ability ranks were fixed before analysis")
    ste.add_argument("--rating-protocol-basis", default=None,
                     help="evidence that the shared scoring protocol is validated")
    ste.add_argument("--create-plan", default=None, metavar="PATH",
                     help="write a frozen empirical panel plan before running subjects")
    ste.add_argument("--panel-plan", default=None, metavar="PATH",
                     help="frozen panel plan to bind to completed --planned-runs")
    ste.add_argument("--plan-subjects", nargs="+", metavar="SUBJECT=ABILITY",
                     default=None, help="subjects and independent ability ranks to freeze")
    ste.add_argument("--planned-runs", nargs="+", metavar="SUBJECT=RUN_ID",
                     default=None, help="bind every planned subject to its completed run")
    ste.add_argument("--plan-owner", default=None,
                     help="named human accountable for the frozen study design")
    ste.add_argument("--plan-areas", nargs="+", metavar="CA-##", default=None,
                     help="competency areas whose exact instruments are frozen")
    ste.add_argument("--plan-rt", type=int, choices=(1, 2, 3, 4), default=2,
                     help="risk tier frozen in a new plan (default: 2)")
    ste.add_argument("--plan-repeats", type=int, default=3,
                     help="repeat observations per instrument for stability (default: 3)")
    ste.add_argument("--rating-protocol-id", default=None,
                     help="expected rating protocol as KIND:RATER")
    ste.add_argument("--write-panel", default=None,
                     help="also write the assembled panel JSON to this path")
    ste.add_argument("--panel-id", default=None,
                     help="name this panel for traceability (recorded in the result metadata)")
    ste.add_argument("--json", action="store_true",
                     help="emit machine-readable JSON")
    st.set_defaults(func=cmd_suites)

    dep = common(sub.add_parser("deployment", help="manage deployments "
                                "(AI deployment × runtime × config × endpoint)"))
    depsub = dep.add_subparsers(dest="dep_cmd", required=True)
    dl = depsub.add_parser("list", help="list active deployments")
    dl.add_argument("--all", action="store_true",
                    help="include retired deployment entries")
    di = depsub.add_parser("inspect", help="inspect one deployment")
    di.add_argument("name", help="deployment id, or an unambiguous model name")
    da = depsub.add_parser("add", help="register a new deployment")
    da.add_argument("file", help="deployment YAML file")
    du = depsub.add_parser("update", help="overwrite an EXISTING deployment in "
                           "place (same id) — for config/key/roles fixes")
    du.add_argument("file", help="deployment YAML file with the existing id")
    drm = depsub.add_parser("remove", help="hard-delete an entry so its id can be "
                            "reused (vs retire, which reserves it for audit)")
    drm.add_argument("name", help="deployment id to remove")
    dr = depsub.add_parser("retire", help="retire a deployment without deleting history")
    dr.add_argument("name", help="deployment id, or an unambiguous model name")
    dva = depsub.add_parser("verify-artifact", help="verify a local artifact "
                            "against the deployment's declared checksum/signature")
    dva.add_argument("name", help="deployment id, or an unambiguous model name")
    dva.add_argument("--artifact", required=True, help="path to the model artifact file")
    dva.add_argument("--pubkey", default=None, help="PEM public key for signature verification")
    dva.add_argument("--signature", default=None, help="detached signature file")
    dva.add_argument("--runtime", default=None, help="disambiguate the deployment's runtime")
    for x in (dl, di, da, du, drm, dr, dva):
        x.add_argument("--json", action="store_true",
                       help="emit machine-readable JSON")
    dep.set_defaults(func=cmd_deployment)

    jg = common(sub.add_parser("judge", help="judge track record — which "
                               "deployments have scored runs, and how reliably"))
    jgsub = jg.add_subparsers(dest="judge_cmd", required=True)
    jga = jgsub.add_parser("available", help="the judge pool: deployments "
                           "registered with roles:[judge], and how many")
    jgl = jgsub.add_parser("list", help="judges used across all runs, with "
                           "runs judged, responses scored, and parse rate")
    jgh = jgsub.add_parser("history", help="one row per judged run, newest first")
    jgh.add_argument("--judge", default=None, metavar="DEPLOYMENT",
                     help="filter to a single judge deployment id")
    for x in (jga, jgl, jgh):
        x.add_argument("--json", action="store_true",
                       help="emit machine-readable JSON")
    jg.set_defaults(func=cmd_judge)

    prof = common(sub.add_parser("profile", help="weighting profiles (enterprise, "
                                 "coder, security, …)"))
    profsub = prof.add_subparsers(dest="prof_cmd", required=True)
    profsub.add_parser("list", help="list available weighting profiles").add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    pfs = profsub.add_parser("show", help="show one weighting profile")
    pfs.add_argument("name", help="profile name")
    pfs.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    pfv = profsub.add_parser("validate", help="validate one weighting profile")
    pfv.add_argument("name", help="profile name or YAML path")
    pfv.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    prof.set_defaults(func=cmd_profile)

    qual = common(sub.add_parser("qualification", help="qualification records "
                                 "(the QUAL-… manifests) and their history"))
    qualsub = qual.add_subparsers(dest="qual_cmd", required=True)
    qualsub.add_parser("list", help="list qualification records").add_argument(
        "--json", action="store_true", help="emit machine-readable JSON")
    qcs = qualsub.add_parser("show", help="show one qualification record")
    qcs.add_argument("record", help="qualification record id")
    qcs.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    qch = qualsub.add_parser("history", help="show immutable qualification lifecycle events")
    qch.add_argument("--deployment", default=None,
                     help="filter by deployment id")
    qch.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    qcv = qualsub.add_parser("verify", help="verify one qualification against current state")
    qcv.add_argument("record", help="qualification record id")
    qcv.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    qcr = qualsub.add_parser("revoke", help="append a revocation lifecycle event")
    qcr.add_argument("record", help="qualification record id")
    qcr.add_argument("--authority", required=True,
                     help="named human authority recording the revocation")
    qcr.add_argument("--reason", required=True,
                     help="reason for revocation")
    qcr.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    qual.set_defaults(func=cmd_qualification)

    from .cli_reference import apply_guidance
    apply_guidance(p)
    return p


def _qualify_defaults(args) -> None:
    if getattr(args, "assessment", None):
        from . import assessments
        try:
            resolved = assessments.resolve(assessments.load(args.assessment))
        except assessments.AssessmentError as e:
            raise SystemExit(f"error: {e}")
        args._assessment = resolved            # stashed for the manifest (ADR-0005)
        args.area = resolved["areas"]          # assessment selects the competencies
        args.profile = resolved["profile"]     # and its EV-weighting profile
        if getattr(args, "rt", None) is None:  # --rt overrides the assessment's tier
            args.rt = int(resolved["risk_tier"][2:])
        if getattr(args, "repeats", None) is None:
            args.repeats = resolved["repeats"]
    elif getattr(args, "all_areas", False):
        from . import runner
        args.area = runner.all_area_codes()
    elif getattr(args, "area", None) in (None, []):
        args.area = ["CA-05"]
    if getattr(args, "rt", None) is None:      # default risk tier when none given
        args.rt = 2
    if (getattr(args, "resume", None) is None
            and getattr(args, "resume_collection", None) is None
            and not getattr(args, "model", None)):
        raise SystemExit("error: a model registry id is required unless --resume "
                         "or --resume-collection is used")


def _subparsers_action(parser):
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            return a
    return None


def command_tree_text(parser) -> str:
    """Introspect the parser and render every command, its subcommands, and
    each leaf's usage line — the full surface in one view. Generated from the
    live parser, so it never drifts from the actual commands."""
    top = _subparsers_action(parser)
    if top is None:
        return ""
    hmap = {ca.dest: (ca.help or "") for ca in top._choices_actions}
    out = ["", "FULL COMMAND TREE  (aies <command> [subcommand] [options])",
           "  commands and subcommands are listed alphabetically", ""]
    for name, sp in sorted(top.choices.items()):
        if name == "help":
            continue
        out.append(f"  {name:15}{hmap.get(name, '')}")
        sub = _subparsers_action(sp)
        if sub is not None:
            smap = {ca.dest: (ca.help or "") for ca in sub._choices_actions}
            for sname, ssp in sorted(sub.choices.items()):
                usage = " ".join(ssp.format_usage().split()).replace("usage: ", "")
                extra = f"  — {smap[sname]}" if smap.get(sname) else ""
                out.append(f"      {sname:13} {usage}{extra}")
        else:
            usage = " ".join(sp.format_usage().split()).replace("usage: ", "")
            out.append(f"      {usage}")
    out.append("")
    out.append("Run `aies <command> --help` for a command's full option details.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Bare `aies` or `aies help` -> the grouped overview + workflow (the
    # epilog) followed by the full command tree, so everything is visible
    # from one place.
    if getattr(args, "cmd", None) in (None, "help"):
        parser.print_help()
        print(command_tree_text(parser))
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

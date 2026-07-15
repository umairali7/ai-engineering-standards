"""aies — the AIES Model Qualification Platform CLI.

Verb dispatch and output rendering only; no qualification logic lives
here (PLATFORM.md §4). Every verb supports --json.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from . import __version__


def _out(data, as_json: bool, human: str | None = None) -> None:
    if as_json:
        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(data)
        print(json.dumps(data, indent=2, default=str))
    else:
        print(human if human is not None else json.dumps(data, indent=2, default=str))


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
        print(f"  fingerprint: {fp['fingerprint_hash']}")
        print("  runtimes:")
        for r in record.get("runtimes", []):
            mark = "OK  " if r["available"] else "--  "
            ver = f" v{r['version']}" if r.get("version") else ""
            print(f"    [{mark}] {r['runtime']}{ver}: {r['detail']}")
        print(f"  ready     : {'yes' if record['ready'] else 'NO'}")
    return 0 if record["ready"] else 1


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
    try:
        if args.resume:
            package = engine.aggregate(args.resume)
            from . import report
            paths = report.write_reports(args.resume)
            _out({"package": package, "reports": paths}, args.json,
                 f"aggregated {args.resume}\n"
                 f"  markdown: {paths['markdown']}\n  json    : {paths['json']}")
            return 0
        if getattr(args, "journey", None):
            manifest = engine.start_journey(
                args.model, args.profile, args.journey,
                repeats=args.repeats, subject_kind="ai",
                runtime=getattr(args, "runtime", None))
        else:
            manifest = engine.start_qualification(
                args.model, args.profile, f"RT{args.rt}", args.area,
                repeats=args.repeats,
                subject_kind="ai",
                runtime=getattr(args, "runtime", None),
                workers=getattr(args, "parallel", 1),
            )
        run_id = manifest["run_id"]
        from . import workspace
        sheet = workspace.run_dir(run_id) / "scoresheet.json"
        _out(manifest, args.json,
             f"run {run_id}: responses collected.\n"
             f"  M1 human scoring hook - next steps:\n"
             f"    1. fill {sheet}\n"
             f"       (integer 0-4 per dimension per item, rater name, findings)\n"
             f"    2. aies score {run_id}\n"
             f"    3. aies qualify --resume {run_id}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_score(args) -> int:
    from . import rating, workspace
    try:
        source = Path(args.file) if args.file else workspace.run_dir(args.run) / "scoresheet.json"
        sheet = json.loads(source.read_text(encoding="utf-8"))
        written = rating.ingest_scores(args.run, sheet)
        _out({"ratings_written": written}, args.json,
             f"{len(written)} rating records written for {args.run}\n"
             f"next: aies qualify --resume {args.run}")
    except (rating.RatingError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
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
            print(report.render_json(args.run))
        elif args.format == "html":
            from . import report_html
            if args.write:
                path = report_html.write_html(args.run)
                _out({"html": path}, args.json, f"wrote {path}\n"
                     "(open in a browser; use the browser's Save as PDF for the "
                     "PDF deliverable — no PDF dependency is bundled)")
            else:
                print(report_html.render_html(args.run))
        else:
            print(report.render_markdown(args.run))
    except FileNotFoundError:
        print(f"error: no evidence package for {args.run!r} — run "
              f"`aies qualify --resume {args.run}` first", file=sys.stderr)
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
                 "\n".join(f"{p['name']:12} {p.get('description', '')}" for p in items))
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


def cmd_plugins(args) -> int:
    from .adapters import discovered
    items = {name: {"class": cls.__name__, "version": getattr(cls, "adapter_version", "?")}
             for name, cls in discovered().items()}
    _out(items, args.json,
         "\n".join(f"{k:15} {v['class']} v{v['version']}" for k, v in items.items()))
    return 0


def cmd_benchmark(args) -> int:
    # Stage-4-only execution: identical to qualify without the scoring hook.
    args.resume = None
    return cmd_qualify(args)


def cmd_compare(args) -> int:
    from . import compare
    try:
        cmp = compare.compare(args.a, args.b)
        if args.json or args.format == "json":
            _out(cmp, True)
        else:
            print(compare.render_markdown(cmp))
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
    from . import compare
    runs = compare.list_runs(model=args.model)
    _out(runs, args.json,
         "\n".join(
             f"{r['run_id']:45} {r['model']:20} {r['profile']:10} "
             f"{r['risk_tier']} {'aggregated' if r['aggregated'] else r['status']}"
             for r in runs) or "(no runs)")
    return 0


def cmd_review(args) -> int:
    from . import review, workspace
    try:
        # Optionally drive a reviewer deployment to score the responses first.
        if getattr(args, "model_reviewer", None):
            from . import model_review
            summary = model_review.run_model_review(
                args.run, args.model_reviewer, runtime=getattr(args, "reviewer_runtime", None))
            if not (args.json):
                print(f"reviewer model {summary['reviewer']}: scored "
                      f"{summary['scored']}/{summary['responses']} responses "
                      f"({summary['unparseable']} unparseable)")
            if not args.reviewer or args.reviewer == "reviewer-model":
                args.reviewer = f"model:{args.model_reviewer}"
        calibration = None
        if args.calibration:
            cal = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
            calibration = review.calibrate(cal["model"], cal["human_anchor"])
        pkg = review.assemble_review_package(
            args.run, reviewer_label=args.reviewer,
            reviewer_qualified_for_review=args.reviewer_qualified,
            calibration=calibration)
        (workspace.run_dir(args.run) / "review-package.json").write_text(
            json.dumps(pkg, indent=2), encoding="utf-8")
        if args.json:
            _out(pkg, True)
        else:
            s = pkg["summary"]
            print(f"review package for {args.run}")
            print(f"  reviewer {pkg['reviewer']['label']!r}: "
                  f"{'ADMITTED' if s['reviewer_admitted'] else 'ADVISORY ONLY'}")
            print(f"  {pkg['reviewer']['reason']}")
            print(f"  divergences for human resolution: {s['n_divergences']}")
            for d in pkg["divergences_for_resolution"]:
                gc = " [gate-changing]" if d["gate_changing"] else ""
                print(f"    {d['response']} {d['dimension']}: "
                      f"human {d['human']} vs model {d['model']} (Δ{d['delta']}){gc}")
            print(f"  {s['note']}")
    except (ValueError, FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
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
            review_package=review_package, rationale=args.rationale or "")
        _out(record, args.json,
             f"recorded {record['decision']} -> {record['record_id']} "
             f"(status: {record['status']})\n"
             f"  authority: {record['humans']['authority']}"
             + (f", second: {record['humans']['second']}" if record['humans']['second'] else "")
             + f"\n  subject: {record['subject']['deployment']} "
             f"@ RT{record['scope']['risk_tier'][-1]}")
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
                           f"{r['scope']['risk_tier']} {r['decision']:20} [{r['status']}]"
                           for r in recs) or "(no qualification records)")
        elif args.q_cmd == "show":
            _out(qualification.get_record(args.record), args.json)
        elif args.q_cmd == "revoke":
            rec = qualification.revoke(args.record, args.authority, args.reason)
            _out(rec, args.json, f"revoked {rec['record_id']}")
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
        elif args.dep_cmd == "retire":
            e = registry.retire(args.name)
            _out(e, args.json, f"retired {e['id']}")
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
                           f"{r['subject']['deployment']:20} {r['scope']['risk_tier']} "
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
                           + "".join(f"    {s['area']}  {s.get('phase') or ''} ({s['id']})\n"
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
commands by stage:
  setup & discovery   doctor · discover · runtime · deployment (registry)
  qualification       qualify · benchmark · score · review · runs · compare
  decision & audit    grant · verify · conform · qualification · report · dashboard
  reference           profile · plugins · journey · index

typical workflow:
  aies doctor                                  validate env, detect runtimes
  aies discover                                register the deployments they serve
  aies qualify <deployment> --profile enterprise --rt 2 --area CA-05
  # fill the printed scoresheet.json (0-4 per dimension) ...
  aies score <run>                             ingest human ratings
  aies review <run> --model-reviewer <dep>     (optional) add a model reviewer
  aies qualify --resume <run>                  gated aggregation
  aies report <run> --format markdown          evidence package
  aies grant <run> --decision grant --authority "Name (ROLE-13)" --second "Name (ROLE-14)"
  aies verify <QUAL-id>                         re-check environment (D7)
  aies conform check statement.yaml            check a conformance claim

  aies qualify <deployment> --journey JOURNEY-01   run a multi-phase journey instead

Run `aies <command> --help` for a command's options. The platform prepares
evidence; a human records every grant. Docs: platform/GUIDE.md.
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=("AIES Model Qualification Platform — executable reference "
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

    common(sub.add_parser("doctor", help="validate the environment and detect runtimes")
           ).set_defaults(func=cmd_doctor)

    common(sub.add_parser("discover", help="scan runtimes and register the "
                          "deployments they serve")).set_defaults(func=cmd_discover)

    reg = common(sub.add_parser("registry", help="manage candidate model entries"))
    regsub = reg.add_subparsers(dest="registry_cmd", required=True)
    radd = regsub.add_parser("add"); radd.add_argument("file")
    rlist = regsub.add_parser("list"); rlist.add_argument("--all", action="store_true")
    rshow = regsub.add_parser("show"); rshow.add_argument("model")
    rret = regsub.add_parser("retire"); rret.add_argument("model")
    for x in (radd, rlist, rshow, rret):
        x.add_argument("--json", action="store_true")
    reg.set_defaults(func=cmd_registry)

    q = common(sub.add_parser("qualify", help="run the pipeline for one model"))
    q.add_argument("model", nargs="?", help="deployment id, or model name")
    q.add_argument("--runtime", default=None,
                   help="disambiguate when a model has several deployments")
    q.add_argument("--profile", default="enterprise")
    q.add_argument("--rt", type=int, choices=(1, 2, 3, 4), default=2,
                   help="scoped risk tier")
    q.add_argument("--area", action="append", default=None,
                   help="competency area (repeatable); default CA-05")
    q.add_argument("--journey", default=None, metavar="JOURNEY_ID",
                   help="run a multi-phase journey instead of area suites")
    q.add_argument("--repeats", type=int, default=None,
                   help="override per-scenario repeats")
    q.add_argument("--parallel", type=int, default=None, metavar="N",
                   help="concurrent inference calls (default 1; records are "
                        "written in canonical order regardless)")
    q.add_argument("--resume", metavar="RUN_ID",
                   help="aggregate a scored run into the evidence package")
    q.set_defaults(func=lambda a: (_qualify_defaults(a), cmd_qualify(a))[1])

    b = common(sub.add_parser("benchmark", help="execute scenario suites only (stage 4)"))
    b.add_argument("model")
    b.add_argument("--profile", default="enterprise")
    b.add_argument("--rt", type=int, choices=(1, 2, 3, 4), default=2)
    b.add_argument("--area", action="append", default=None)
    b.add_argument("--repeats", type=int, default=None)
    b.add_argument("--parallel", type=int, default=None, metavar="N")
    b.add_argument("--runtime", default=None)
    b.set_defaults(func=lambda a: (_qualify_defaults(a), cmd_benchmark(a))[1])

    s = common(sub.add_parser("score", help="ingest a filled scoresheet (human or model rater)"))
    s.add_argument("run")
    s.add_argument("--file", help="scoresheet path (default: the run's scoresheet.json)")
    s.set_defaults(func=cmd_score)

    r = common(sub.add_parser("report", help="render an evidence package"))
    r.add_argument("run")
    r.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    r.add_argument("--write", action="store_true",
                   help="write the report into the run directory instead of stdout")
    r.set_defaults(func=cmd_report)

    common(sub.add_parser("index", help="rebuild the result index from run files")
           ).set_defaults(func=cmd_index)

    pr = common(sub.add_parser("profiles", help="list/show/validate weighting profiles"))
    prsub = pr.add_subparsers(dest="profiles_cmd", required=True)
    prsub.add_parser("list").add_argument("--json", action="store_true")
    prs = prsub.add_parser("show"); prs.add_argument("name")
    prs.add_argument("--json", action="store_true")
    prv = prsub.add_parser("validate"); prv.add_argument("name")
    prv.add_argument("--json", action="store_true")
    pr.set_defaults(func=cmd_profiles)

    common(sub.add_parser("plugins", help="list installed runtime adapters")
           ).set_defaults(func=cmd_plugins)

    cp = common(sub.add_parser(
        "compare", help="compare two runs/models on identical suite versions"))
    cp.add_argument("a", help="run id or model registry id (latest aggregated run)")
    cp.add_argument("b", help="run id or model registry id (latest aggregated run)")
    cp.add_argument("--format", choices=("markdown", "json"), default="markdown")
    cp.set_defaults(func=cmd_compare)

    rn = common(sub.add_parser("runs", help="result history: list runs"))
    rnsub = rn.add_subparsers(dest="runs_cmd", required=True)
    rl = rnsub.add_parser("list")
    rl.add_argument("--model", default=None)
    rl.add_argument("--json", action="store_true")
    rn.set_defaults(func=cmd_runs)

    rv = common(sub.add_parser("review", help="assemble a multi-model peer-review package"))
    rv.add_argument("run")
    rv.add_argument("--reviewer", default="reviewer-model",
                    help="label for the reviewer model")
    rv.add_argument("--model-reviewer", default=None, metavar="DEPLOYMENT",
                    help="drive this reviewer deployment to score the responses "
                         "before assembling the package")
    rv.add_argument("--reviewer-runtime", default=None,
                    help="disambiguate the reviewer deployment's runtime")
    rv.add_argument("--reviewer-qualified", action="store_true",
                    help="the reviewer holds a current review-class (CA-06) qualification")
    rv.add_argument("--calibration", default=None,
                    help="JSON {model:[...], human_anchor:[...]} for bootstrap calibration")
    rv.set_defaults(func=cmd_review)

    gr = common(sub.add_parser("grant", help="record a human qualification decision"))
    gr.add_argument("run")
    gr.add_argument("--decision", choices=("grant", "grant-with-conditions", "deny"),
                    required=True)
    gr.add_argument("--authority", required=True, help="named human authority (ROLE-13)")
    gr.add_argument("--second", default=None, help="second named human (required to grant)")
    gr.add_argument("--condition", action="append", default=None,
                    help="condition (repeatable; required for grant-with-conditions)")
    gr.add_argument("--rationale", default=None)
    gr.set_defaults(func=cmd_grant)

    vf = common(sub.add_parser("verify", help="verify a grant against the current "
                               "environment (D7); invalidates on fingerprint change"))
    vf.add_argument("record")
    vf.set_defaults(func=cmd_verify)

    qz = common(sub.add_parser("qualifications", help="list/show/revoke qualification records"))
    qzsub = qz.add_subparsers(dest="q_cmd", required=True)
    qzsub.add_parser("list").add_argument("--json", action="store_true")
    qzs = qzsub.add_parser("show"); qzs.add_argument("record"); qzs.add_argument("--json", action="store_true")
    qzr = qzsub.add_parser("revoke"); qzr.add_argument("record")
    qzr.add_argument("--authority", required=True); qzr.add_argument("--reason", required=True)
    qzr.add_argument("--json", action="store_true")
    qz.set_defaults(func=cmd_qualifications)

    db = common(sub.add_parser("dashboard", help="render an HTML dashboard over runs and grants"))
    db.add_argument("--write", action="store_true")
    db.set_defaults(func=cmd_dashboard)

    # --- resource-model noun commands (primary surface) ---------------------
    rt = common(sub.add_parser("runtime", help="inspect runtime adapters and "
                               "the runtimes behind them"))
    rtsub = rt.add_subparsers(dest="rt_cmd", required=True)
    rtsub.add_parser("list").add_argument("--json", action="store_true")
    rti = rtsub.add_parser("inspect"); rti.add_argument("name")
    rti.add_argument("--json", action="store_true")
    rt.set_defaults(func=cmd_runtime)

    cf = common(sub.add_parser("conform", help="declare/check conformance to AIES"))
    cfsub = cf.add_subparsers(dest="conform_cmd", required=True)
    cft = cfsub.add_parser("template")
    cft.add_argument("--class", dest="klass", choices=("adopter", "implementation"),
                     default="adopter")
    cft.add_argument("--out", default=None); cft.add_argument("--json", action="store_true")
    cfc = cfsub.add_parser("check"); cfc.add_argument("file")
    cfc.add_argument("--write", action="store_true"); cfc.add_argument("--json", action="store_true")
    cfsub.add_parser("requirements").add_argument("--json", action="store_true")
    cf.set_defaults(func=cmd_conform)

    jn = common(sub.add_parser("journey", help="multi-phase journeys "
                               "(chained scenarios across the SDLC)"))
    jnsub = jn.add_subparsers(dest="journey_cmd", required=True)
    jnsub.add_parser("list").add_argument("--json", action="store_true")
    jns = jnsub.add_parser("show"); jns.add_argument("id")
    jns.add_argument("--json", action="store_true")
    jn.set_defaults(func=cmd_journey)

    dep = common(sub.add_parser("deployment", help="manage deployments "
                                "(model × runtime × config × endpoint)"))
    depsub = dep.add_subparsers(dest="dep_cmd", required=True)
    dl = depsub.add_parser("list"); dl.add_argument("--all", action="store_true")
    di = depsub.add_parser("inspect"); di.add_argument("name")
    da = depsub.add_parser("add"); da.add_argument("file")
    dr = depsub.add_parser("retire"); dr.add_argument("name")
    for x in (dl, di, da, dr):
        x.add_argument("--json", action="store_true")
    dep.set_defaults(func=cmd_deployment)

    prof = common(sub.add_parser("profile", help="weighting profiles (enterprise, "
                                 "coder, security, …)"))
    profsub = prof.add_subparsers(dest="prof_cmd", required=True)
    profsub.add_parser("list").add_argument("--json", action="store_true")
    pfs = profsub.add_parser("show"); pfs.add_argument("name"); pfs.add_argument("--json", action="store_true")
    pfv = profsub.add_parser("validate"); pfv.add_argument("name"); pfv.add_argument("--json", action="store_true")
    prof.set_defaults(func=cmd_profile)

    qual = common(sub.add_parser("qualification", help="qualification records "
                                 "(the QUAL-… manifests) and their history"))
    qualsub = qual.add_subparsers(dest="qual_cmd", required=True)
    qualsub.add_parser("list").add_argument("--json", action="store_true")
    qcs = qualsub.add_parser("show"); qcs.add_argument("record"); qcs.add_argument("--json", action="store_true")
    qch = qualsub.add_parser("history"); qch.add_argument("--deployment", default=None)
    qch.add_argument("--json", action="store_true")
    qcv = qualsub.add_parser("verify"); qcv.add_argument("record"); qcv.add_argument("--json", action="store_true")
    qcr = qualsub.add_parser("revoke"); qcr.add_argument("record")
    qcr.add_argument("--authority", required=True); qcr.add_argument("--reason", required=True)
    qcr.add_argument("--json", action="store_true")
    qual.set_defaults(func=cmd_qualification)

    return p


def _qualify_defaults(args) -> None:
    if getattr(args, "area", None) in (None, []):
        args.area = ["CA-05"]
    if getattr(args, "resume", None) is None and not getattr(args, "model", None):
        raise SystemExit("error: a model registry id is required unless --resume is used")


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
    out = ["", "FULL COMMAND TREE  (aies <command> [subcommand] [options])", ""]
    for name, sp in top.choices.items():
        if name == "help":
            continue
        out.append(f"  {name:15}{hmap.get(name, '')}")
        sub = _subparsers_action(sp)
        if sub is not None:
            smap = {ca.dest: (ca.help or "") for ca in sub._choices_actions}
            for sname, ssp in sub.choices.items():
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

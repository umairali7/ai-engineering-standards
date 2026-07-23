"""One-process comprehensive AIES engineering-evaluation demo."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path

from aies import cli, workspace


STARTED = time.monotonic()
LAST_STAGE = STARTED


def hr(title: str) -> None:
    global LAST_STAGE
    now = time.monotonic()
    if LAST_STAGE != STARTED:
        print(f"[previous stage: {now - LAST_STAGE:.1f}s · total: {now - STARTED:.1f}s]")
    LAST_STAGE = now
    print("\n" + "=" * 67)
    print(title)
    print("=" * 67)


def invoke(*args: str, capture: bool = False, quiet: bool = False,
           live_stderr: bool = False) -> tuple[int, str, str]:
    stdout = io.StringIO() if capture or quiet else None
    stderr = io.StringIO() if capture and not live_stderr else None
    out_context = contextlib.redirect_stdout(stdout) if stdout is not None else contextlib.nullcontext()
    err_context = contextlib.redirect_stderr(stderr) if stderr is not None else contextlib.nullcontext()
    try:
        with out_context, err_context:
            code = int(cli.main(list(args)) or 0)
    except SystemExit as exc:
        code = int(exc.code or 0)
    return code, stdout.getvalue() if stdout else "", stderr.getvalue() if stderr else ""


def require(code: int, operation: str) -> None:
    if code:
        raise SystemExit(f"demo failed: {operation} exited {code}")


def first_lines(text: str, count: int) -> None:
    print("\n".join(text.splitlines()[:count]))


def main() -> int:
    demo_ws = Path(tempfile.mkdtemp(prefix="aies-full-demo-"))
    os.environ["AIES_WORKSPACE"] = str(demo_ws)
    # The demo is intentionally offline. Make optional runtime probes fail
    # locally and immediately instead of waiting on production endpoint
    # timeouts; the deterministic mock runtime remains available.
    for variable in ("AIES_OPENAI_BASE_URL", "AIES_OLLAMA_BASE_URL",
                     "AIES_LMSTUDIO_BASE_URL", "AIES_LLAMACPP_BASE_URL",
                     "AIES_MLX_BASE_URL"):
        os.environ[variable] = "http://127.0.0.1:9/v1"
    os.environ["AIES_PROBE_TIMEOUT_S"] = "0.25"
    candidate = "mock-mock-small"
    judge = "mock-mock-large"

    hr(f"AIES COMPREHENSIVE DEMO  (offline, mock runtime)   ws={demo_ws}")

    hr("1. Setup — environment + deployment discovery")
    require(invoke("doctor", "--json", quiet=True)[0], "doctor")
    print("doctor: environment validated + fingerprinted")
    require(invoke("discover", quiet=True)[0], "discover")
    require(invoke("deployment", "list")[0], "deployment list")

    hr("2. The corpus is a set of calibrated MEASUREMENT INSTRUMENTS")
    print("Every scenario carries a ceiling anchor ('what a 4 does that a 3 doesn't'):")
    code, output, _ = invoke("suites", "validate", capture=True)
    require(code, "suite validation")
    first_lines(output, 8)
    code, output, _ = invoke("suites", "calibrate", capture=True)
    require(code, "suite calibration")
    first_lines(output, 12)

    hr("3. Declarative assessments (composition as data, ADR-0005)")
    require(invoke("assessment", "list")[0], "assessment list")
    print("\nSubject-specific semantics (ADR-0018):")
    require(invoke("assessment-profile", "list")[0], "assessment profile list")

    hr("4. Assess a deployment: compose -> collect -> automated Engineering Evaluation")
    print("Running a fast RT1 — Minimal 'coder' smoke scope once per distinct instrument, "
          "auto-scored by a different mock judge...")
    code, transcript, _ = invoke(
        "qualify", candidate, "--assessment", "coder", "--rt", "1",
        "--judge", judge, "--parallel", "8", capture=True, live_stderr=True)
    require(code, "automated evaluation")
    runs = sorted((demo_ws / "runs").glob("run-*"))
    if not runs:
        raise SystemExit("demo failed: qualification created no run")
    run_dir = runs[-1]
    run_id = run_dir.name
    (demo_ws / "qualification-transcript.md").write_text(transcript, encoding="utf-8")
    print(f"run: {run_id}")

    hr("5. Engineering Evaluation COMPLETE — no human prerequisite")
    evaluation = workspace.read_json(run_dir / "engineering-evaluation.json")
    print("Automated coverage is enough to complete the informational Engineering Evaluation:")
    print("  status:", evaluation["status"].upper())
    print("  human evaluation:", "reviewed" if evaluation["human_evaluation"]["status"] == "reviewed"
          else "not reviewed (optional)")
    for area, value in evaluation["areas"].items():
        print(" ", area, value["status"].upper(), "by", value.get("completed_by") or "mixed")
    code, result_md, _ = invoke("assessment", "result", run_id, capture=True)
    require(code, "engineering assessment result")
    print()
    first_lines(result_md, 26)

    hr("6. Evidence → Capability → Confidence → Engineering Decisions")
    code, snapshot_output, _ = invoke(
        "snapshot", run_id, "--observed-only", capture=True)
    require(code, "engineering decision snapshot")
    first_lines(snapshot_output, 35)

    hr("7. Evidence-derived Engineering Fit Guidance")
    code, fit_output, _ = invoke("guidance", run_id, capture=True)
    require(code, "engineering fit guidance")
    first_lines(fit_output, 35)

    hr("8. Engineering fit is actionable without becoming deployment authority")
    guidance = workspace.read_json(run_dir / "engineering-fit-guidance.json")
    counts: dict[str, int] = {}
    for task in guidance["tasks"]:
        counts[task["fit"]] = counts.get(task["fit"], 0) + 1
    for name, count in sorted(counts.items()):
        print(" ", name, count)
    print("Human evaluation is optional; operational authorization remains a separate governed action.")
    coverage = workspace.read_json(run_dir / "assessment-coverage.json")
    summary = coverage["summary"]
    print(
        "Coverage boundary:",
        f"{summary['assessed']} assessed,",
        f"{summary['partially-assessed']} partial,",
        f"{summary['not-assessed']} not assessed,",
        f"{summary['unsupported']} unsupported,",
        f"{summary['not-applicable']} not applicable.",
    )
    print(
        "Evidence identity:",
        f"{coverage['evidence_reuse']['unique_evidence_refs']} unique /",
        f"{coverage['evidence_reuse']['cell_references']} cell references.",
    )
    integrity = coverage["integrity_summary"]
    print(
        "Evidence integrity:",
        f"{integrity['stale_cells']} stale,",
        f"{integrity['conflicting_cells']} conflicting,",
        f"{integrity['failed_collection_cells']} collection failures,",
        f"{integrity['correlated_evidence_groups']} correlated groups,",
        f"{integrity['component_count']} declared components.",
    )
    print(
        "Freshness boundary: age is evaluated; declared change triggers "
        "require separate detection.")

    hr("9. Protocol-compatible ECM comparison (same evidence fixture, no invented winner)")
    code, output, _ = invoke("compare", run_id, run_id, "--ecm", "--json", capture=True)
    require(code, "ECM comparison")
    comparison = json.loads(output)
    print("  global protocol compatible:", comparison["compatible"])
    print("  comparable observed task rows:",
          sum(1 for task in comparison["tasks"] if task["comparable"]))
    # Multi-subject comparison v2 reports evidence-bounded task leaders. A
    # repeated-reference self-check must tie, so it cannot emit a sole leader.
    sole_leads = sum(comparison["summary"]["sole_leads"].values())
    print("  sole task leaders emitted:", sole_leads)
    if sole_leads:
        raise SystemExit(
            "demo failed: a repeated-reference protocol self-check emitted "
            "a sole task leader")

    hr("10. Linked audience-specific decision products")
    bundle = workspace.read_json(run_dir / "report-bundle.json")
    print("  bundle schema:", bundle["report_bundle_schema"])
    for name, filename in bundle["artifacts"].items():
        if name.endswith("_html") or name == "html":
            print(f"  {name:<24} {filename}")
    print()
    first_lines((run_dir / "executive-summary.md").read_text(encoding="utf-8"), 34)

    hr("11. Presentation-grade renders (same evidence; no hidden inference)")
    presentations = (
        "engineering-assessment-result.html", "report.html",
        "engineering-capability-matrix.html", "engineering-fit-guidance.html",
        "executive-summary.html", "grounding-diagnostics.html",
        "assessment-coverage.html")
    missing = [name for name in presentations if not (run_dir / name).is_file()
               or not (run_dir / name).stat().st_size]
    if missing:
        raise SystemExit("demo failed: missing presentation artifacts: " + ", ".join(missing))
    print("verified seven presentation-grade HTML artifacts from the generated bundle")

    hr("12. Decision-engine CONFORMANCE (the standard as a subject)")
    print("Does the reference engine reproduce AESQS decision semantics on the golden corpus?")
    code, output, _ = invoke("conform", "engine", capture=True)
    require(code, "reference conformance")
    first_lines(output, 4)
    print("\n-- and a FOREIGN package-free reimplementation verifies on the same corpus --")
    foreign_engine = (
        Path(__file__).resolve().parents[2] / "conformance" / "example_engine.py")
    code, output, _ = invoke(
        "conform", "engine", "--engine",
        f'"{sys.executable}" "{foreign_engine}"', capture=True)
    require(code, "foreign-engine conformance")
    first_lines(output, 4)

    hr("13. Empirical calibration harness (ready for a real-subject panel)")
    print("Design-time calibration is done; empirical calibration needs a representative panel.")
    panel_path = demo_ws / "panel.json"
    panel_path.write_text(json.dumps({
        "panel": [{"model": "strong", "ability": 3}, {"model": "mid", "ability": 2},
                  {"model": "weak", "ability": 1}],
        "scores": {
            "SC-CA07-001": {"strong": [4, 4, 3], "mid": [3, 3, 2], "weak": [1, 2, 1]},
            "SC-CA05-001": {"strong": [4, 4], "mid": [4, 4], "weak": [4, 3]},
        },
        "twins": {"SC-CA07-001": "SC-CA07-007"},
    }), encoding="utf-8")
    require(invoke("suites", "empirical", str(panel_path))[0], "empirical harness")

    hr("14. Repository conformance AUDIT (a different subject)")
    code, output, _ = invoke("audit", "..", capture=True)
    require(code, "repository audit")
    first_lines(output, 10)

    hr("15. The platform reviews its OWN corpus (advisory; no single grade)")
    code, output, _ = invoke("corpus", "health", capture=True)
    require(code, "corpus health")
    first_lines(output, 18)
    print("\n-- and reviews one scenario as a measurement instrument --")
    code, output, _ = invoke("corpus", "review", "SC-CA07-015", "--reviewer", judge,
                             capture=True)
    require(code, "scenario review")
    first_lines(output, 14)

    hr("DEMO COMPLETE")
    print("Subjects assessed: deployment + repository + standard")
    print("Also shown: live progress, ECM strengths/gaps, evidence-derived guidance, comparison,")
    print("             assessment coverage/blind spots, linked reports, engineering fit,")
    print("             and the empirical harness.")
    print("Read-only JSON API: aies serve --port 8722")
    print(f"workspace: {demo_ws}")
    print(f"total demo time: {time.monotonic() - STARTED:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

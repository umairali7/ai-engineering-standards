"""The end-to-end demo IS a CI-gated test (executable documentation).

Runs the exact documented golden path — discover -> assessment list -> qualify
--assessment (compose + collect + auto-score with a mock judge) -> assessment
result -> HTML render — fully offline against the mock runtime, and asserts the
whole pipeline produces a Canonical Assessment Result. If this test breaks, the
onboarding demo (`scripts/demo.sh` / `make demo`) is broken. It does NOT assert a
specific outcome (that would be brittle); it asserts the contracts hold."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def _cli(*argv) -> int:
    from aies import cli
    saved = sys.argv
    sys.argv = ["aies", *argv]
    try:
        return int(cli.main() or 0)
    except SystemExit as e:
        return int(e.code or 0)
    finally:
        sys.argv = saved


@pytest.fixture()
def demo_ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    monkeypatch.setenv("AIES_ENV_FILE", str(tmp_path / "empty.env"))
    (tmp_path / "empty.env").write_text("", encoding="utf-8")
    return tmp_path / "ws"


def test_offline_end_to_end_demo(demo_ws, monkeypatch):
    from aies import workspace, ecm

    # A report bundle must share one factual ECM view across all renderers.
    # Recomputing it reparses the entire scenario corpus and made the demo
    # needlessly slow even though the mock inference itself is instant.
    original_matrix = ecm.engineering_capability_matrix
    matrix_calls = []

    def counted_matrix(ref):
        matrix_calls.append(ref)
        return original_matrix(ref)

    monkeypatch.setattr(ecm, "engineering_capability_matrix", counted_matrix)

    # 1. discovery (mock runtime is always present)
    assert _cli("discover") == 0
    assert _cli("assessment", "list") == 0

    # 2. compose + collect + auto-score — the whole evaluation pipeline,
    #    offline.  A DIFFERENT deployment judges (never self-judge), and each
    #    distinct instrument runs once: repeats must never substitute for breadth.
    assert _cli("qualify", "mock-mock-small", "--assessment", "coder", "--rt", "1",
                "--judge", "mock-mock-large", "--parallel", "8") == 0
    assert len(matrix_calls) == 1

    # find the run the pipeline just produced
    runs = sorted((demo_ws / "runs").glob("run-*"))
    assert runs, "qualify produced no run"
    run_id = runs[-1].name

    # 3. automated scoring creates a complete, non-blocking Engineering
    # Assessment Result. Human evaluation remains an optional assurance column.
    result = json.loads(
        (runs[-1] / "engineering-assessment-result.json").read_text(
            encoding="utf-8"))
    assert result["kind"] == "engineering-assessment-result"
    assert result["status"] == "COMPLETE"
    assert result["formal_qualification"]["status"] == "not-requested"
    evaluation = json.loads(
        (runs[-1] / "engineering-evaluation.json").read_text(encoding="utf-8"))
    assert evaluation["status"] == "complete"
    assert evaluation["human_evaluation"]["status"] == "not-reviewed"
    assert evaluation["human_evaluation"]["optional"] is True
    assert not (runs[-1] / "assessment-result.json").exists()
    for name in ("engineering-assessment-result.md",
                 "engineering-assessment-result.html",
                 "engineering-fit-guidance.md", "engineering-fit-guidance.json",
                 "engineering-fit-guidance.html", "executive-summary.md",
                 "executive-summary.json", "executive-summary.html",
                 "grounding-diagnostics.md", "grounding-diagnostics.json",
                 "grounding-diagnostics.html",
                 "report-bundle.json"):
        assert (runs[-1] / name).exists(), name
    executive = json.loads(
        (runs[-1] / "executive-summary.json").read_text(encoding="utf-8"))
    assert executive["assessment"]["status"] == result["status"]
    assert executive["formal_qualification"]["status"] == "not-requested"
    report_md = (runs[-1] / "report.md").read_text(encoding="utf-8")
    report_html = (runs[-1] / "report.html").read_text(encoding="utf-8")
    report_json = json.loads(
        (runs[-1] / "report.json").read_text(encoding="utf-8"))
    assert report_json["kind"] == "engineering-evaluation-report"
    assert report_json["formal_qualification"]["status"] == "not-requested"
    assert "qualification_evidence_appendix" not in report_json
    for blocked_word in ("Overall: BLOCKED", "INSUFFICIENT EVIDENCE",
                         "Grant Readiness"):
        assert blocked_word not in report_md
        assert blocked_word not in report_html
    fit = json.loads(
        (runs[-1] / "engineering-fit-guidance.json").read_text(
            encoding="utf-8"))
    assert fit["kind"] == "engineering-fit-guidance"
    assert any(row["fit"] == "limited-evidence" for row in fit["tasks"])
    assert not any(row["fit"] == "strong-observed-fit" for row in fit["tasks"])
    from aies import compare
    observed_comparison = compare.compare_ecm(run_id, run_id)
    assert observed_comparison["comparison_mode"] == "engineering-observed"
    assert any(row["comparable"] for row in observed_comparison["tasks"])
    assert not any(row["winner"] for row in observed_comparison["tasks"])
    formal_comparison = compare.compare_ecm(
        run_id, run_id, formal_qualification=True)
    assert not any(row["comparable"] for row in formal_comparison["tasks"])
    from aies import api
    status, primary = api.route(f"/runs/{run_id}/result")
    assert status == 200
    assert primary["kind"] == "engineering-assessment-result"
    assert api.route(f"/runs/{run_id}/formal-result")[0] == 404

    # Automated-only formal fields are intentionally empty; the human-readable
    # legacy profile must render that state rather than formatting None as a
    # numeric score.  ECM remains the primary engineering-facing artifact.
    assert _cli("capabilities", run_id) == 0

    # 4. Engineering assessment rendering succeeds regardless of optional human
    # review status.
    out = demo_ws / "assessment.html"
    assert _cli("assessment", "result", run_id) == 0
    assert _cli("assessment", "result", run_id, "--format", "html",
                "--out", str(out)) == 0
    doc = out.read_text(encoding="utf-8")
    assert doc.startswith("<!doctype html>") and result["status"] in doc

    # 5. Formal qualification remains available only as an explicit, separately
    # governed request and cannot silently cross into a grant.
    assert _cli("assessment", "result", run_id,
                "--formal-qualification") == 1
    assert (runs[-1] / "assessment-result.json").exists()
    assert api.route(f"/runs/{run_id}/formal-result")[0] == 200
    assert _cli("grant", run_id, "--decision", "grant",
                "--authority", "A. Architect (ROLE-13)",
                "--second", "P. Peer (ROLE-14)") == 2

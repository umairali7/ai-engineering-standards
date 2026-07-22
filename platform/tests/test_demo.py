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


def test_offline_end_to_end_demo(demo_ws):
    from aies import decision, workspace, constants

    # 1. discovery (mock runtime is always present)
    assert _cli("discover") == 0
    assert _cli("assessment", "list") == 0

    # 2. compose + collect + auto-score — the whole evaluation pipeline,
    #    offline.  A DIFFERENT deployment judges (never self-judge), and each
    #    distinct instrument runs once: repeats must never substitute for breadth.
    assert _cli("qualify", "mock-mock-small", "--assessment", "coder",
                "--judge", "mock-mock-large") == 0

    # find the run the pipeline just produced
    runs = sorted((demo_ws / "runs").glob("run-*"))
    assert runs, "qualify produced no run"
    run_id = runs[-1].name

    # The mock judge is intentionally advisory until it passes the same
    # bootstrap-admission path as any other reviewer.  The fixture is synthetic
    # and only proves the offline workflow; mock provenance prevents a real
    # qualification claim.
    calibration = demo_ws / "mock-judge-calibration.json"
    calibration.write_text(json.dumps({
        "model": [{f"EV{i}": 4 for i in range(1, 7)}],
        "human_anchor": [{f"EV{i}": 4 for i in range(1, 7)}],
    }), encoding="utf-8")
    assert _cli("review", run_id, "--reviewer", "model:mock-mock-large",
                "--calibration", str(calibration)) == 0

    # 3. the Canonical Assessment Result exists and is well-formed
    result = json.loads((runs[-1] / "assessment-result.json").read_text(encoding="utf-8"))
    assert result["outcome"] in decision.OUTCOMES
    assert result["result_schema"] == decision.RESULT_SCHEMA
    assert result["metadata"]["profile_version"] == "1.0.0"          # captured, not re-read
    assert result["metadata"]["evidence_schema"] == constants.EVIDENCE_SCHEMA
    assert result["metadata"]["decision_semantics_version"] == decision.DECISION_SEMANTICS_VERSION
    evaluation = json.loads(
        (runs[-1] / "engineering-evaluation.json").read_text(encoding="utf-8"))
    assert evaluation["status"] == "complete"
    assert evaluation["human_evaluation"]["status"] == "not-reviewed"
    assert evaluation["human_evaluation"]["optional"] is True
    assert result["outcome"] == "INSUFFICIENT EVIDENCE"

    # Automated-only formal fields are intentionally empty; the human-readable
    # legacy profile must render that state rather than formatting None as a
    # numeric score.  ECM remains the primary engineering-facing artifact.
    assert _cli("capabilities", run_id) == 0

    # 4. re-deciding from the SAME evidence is identical (no inference) — the
    #    property that makes results reproducible and replayable.
    replay = decision.decide(
        workspace.read_json(runs[-1] / "evidence-package.json"),
        workspace.read_json(runs[-1] / "manifest.json")["assessment"])
    assert replay["outcome"] == result["outcome"]
    assert replay["decisions"] == result["decisions"]

    # 5. HTML render is a view (assessment result --format html)
    out = demo_ws / "assessment.html"
    # The command renders the valid result and uses exit 1 as a formal gate
    # signal.  The demo must assert and contain that expected non-zero status.
    assert _cli("assessment", "result", run_id) == 1
    assert _cli("assessment", "result", run_id, "--format", "html", "--out", str(out)) == 1
    doc = out.read_text(encoding="utf-8")
    assert doc.startswith("<!doctype html>") and result["outcome"] in doc

    # A completed automated evaluation is useful, but it cannot silently cross
    # the formal human qualification boundary.
    assert _cli("grant", run_id, "--decision", "grant",
                "--authority", "A. Architect (ROLE-13)",
                "--second", "P. Peer (ROLE-14)") == 2

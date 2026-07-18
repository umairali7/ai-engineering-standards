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
        cli.main()
        return 0
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

    # 2. compose + collect + auto-score + decide — the whole pipeline, offline.
    #    A DIFFERENT deployment judges (never self-judge). qualify exits 0.
    assert _cli("qualify", "mock-mock-small", "--assessment", "coder",
                "--judge", "mock-mock-large", "--repeats", "5") == 0

    # find the run the pipeline just produced
    runs = sorted((demo_ws / "runs").glob("run-*"))
    assert runs, "qualify produced no run"
    run_id = runs[-1].name

    # 3. the Canonical Assessment Result exists and is well-formed
    result = json.loads((runs[-1] / "assessment-result.json").read_text(encoding="utf-8"))
    assert result["outcome"] in decision.OUTCOMES
    assert result["result_schema"] == decision.RESULT_SCHEMA
    assert result["metadata"]["profile_version"] == "1.0.0"          # captured, not re-read
    assert result["metadata"]["evidence_schema"] == constants.EVIDENCE_SCHEMA
    assert result["metadata"]["decision_semantics_version"] == decision.DECISION_SEMANTICS_VERSION

    # 4. re-deciding from the SAME evidence is identical (no inference) — the
    #    property that makes results reproducible and replayable.
    replay = decision.decide(
        workspace.read_json(runs[-1] / "evidence-package.json"),
        workspace.read_json(runs[-1] / "manifest.json")["assessment"])
    assert replay["outcome"] == result["outcome"]
    assert replay["decisions"] == result["decisions"]

    # 5. HTML render is a view (assessment result --format html)
    out = demo_ws / "assessment.html"
    assert _cli("assessment", "result", run_id, "--format", "html", "--out", str(out)) in (0, 1)
    doc = out.read_text(encoding="utf-8")
    assert doc.startswith("<!doctype html>") and result["outcome"] in doc

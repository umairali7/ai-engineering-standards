from argparse import Namespace
from email.message import Message
from io import BytesIO
import urllib.error

import pytest

from aies import cli, failure_diagnostics
from aies import engine, model_review
from aies.adapters.base import GenerationRequest
from aies.adapters.openai_compat import OpenAICompatAdapter


def test_failure_classification_and_secret_redaction():
    message = (
        "HTTP 429: insufficient_quota; Authorization: Bearer secret-value-123 "
        "api_key='sk-example-secret'")
    diagnostic = failure_diagnostics.build(
        message,
        operation="automated-review",
        phase="review",
        run_id="run-1",
        preserved_work_status="responses-preserved",
        preserved_work_detail="Responses remain.",
        recovery_command="aies review run-1 --model-reviewer judge",
        duplicate_cost_risk="partial",
        duplicate_cost_detail="Only missing ratings repeat.",
    )
    assert diagnostic.category == "quota"
    assert "secret-value" not in diagnostic.summary
    assert "sk-example" not in diagnostic.summary
    assert diagnostic.documentation.endswith("#quota-and-rate-limits")


@pytest.mark.parametrize(
    ("message", "phase", "expected"),
    [
        ("permission denied while reading workspace", None, "environment"),
        ("No module named 'yaml'", None, "dependency"),
        ("HTTP 401 Unauthorized", None, "authentication"),
        ("HTTP 429 rate limit", None, "quota"),
        ("suite changed since collection", None, "compatibility"),
        ("connection refused by inference endpoint", None, "inference"),
        ("reviewer request failed", "review", "scoring"),
        ("reviewer produced no parseable scores", None, "parsing"),
        ("run has no ratings", None, "evidence"),
        ("cannot grant on non-decisional evidence", None, "governance"),
    ],
)
def test_every_failure_category_has_a_stable_classifier(
        message, phase, expected):
    assert failure_diagnostics.classify(message, phase=phase) == expected
    assert failure_diagnostics.documentation_for(expected).startswith(
        "platform/TROUBLESHOOTING.md#")


def test_json_failure_contract_is_machine_readable(capsys):
    diagnostic = failure_diagnostics.build(
        "No module named 'yaml'",
        operation="support",
        recovery_command="python -m pip install -e .",
    )
    failure_diagnostics.emit(diagnostic, as_json=True)
    output = capsys.readouterr().err
    assert '"kind": "cli-failure-diagnostic"' in output
    assert '"category": "dependency"' in output
    assert '"recovery_command": "python -m pip install -e ."' in output


def test_review_failure_explains_reuse_and_exact_recovery(monkeypatch, capsys):
    def fail(*_args, **_kwargs):
        raise RuntimeError("HTTP 429: insufficient_quota")

    monkeypatch.setattr(model_review, "run_model_review", fail)
    args = Namespace(
        run="run-preserved",
        model_reviewer="judge-a",
        reviewer_runtime=None,
        parallel=4,
        judge_batch_size=8,
        json=False,
        reviewer=None,
        reviewer_qualified=False,
        calibration=None,
        consider_advisory_review=False,
        human_evaluation=None,
    )
    assert cli.cmd_review(args) == 2
    error = capsys.readouterr().err
    assert "error [quota]" in error
    assert "run-preserved" in error
    assert (
        "aies review run-preserved --model-reviewer judge-a "
        "--parallel 4 --judge-batch-size 8" in error)
    assert "Candidate calls will not repeat" in error


def test_support_and_starter_failures_route_to_discovery(capsys):
    support_args = Namespace(
        subject_kind=None, status="not-a-status", json=False)
    assert cli.cmd_support(support_args) == 2
    support_error = capsys.readouterr().err
    assert "recover: aies support" in support_error
    assert "duplicate-cost risk: none" in support_error

    starter_args = Namespace(
        starter_cmd="show", starter_id="not-a-starter", json=False)
    assert cli.cmd_starter(starter_args) == 2
    starter_error = capsys.readouterr().err
    assert "recover: aies starter list" in starter_error
    assert "read-only" in starter_error


def test_run_execution_error_carries_resumable_identity():
    error = engine.RunExecutionError(
        "two inference calls failed", run_id="run-partial", phase="collection")
    assert isinstance(error, engine.EngineError)
    assert error.run_id == "run-partial"
    assert error.phase == "collection"


def test_endpoint_rate_limit_surfaces_provider_retry_after(monkeypatch):
    headers = Message()
    headers["Retry-After"] = "17"
    response = BytesIO(b'{"error":{"type":"rate_limit_error"}}')

    def rate_limited(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://example.test/v1/chat/completions",
            429,
            "Too Many Requests",
            headers,
            response,
        )

    monkeypatch.setattr("urllib.request.urlopen", rate_limited)
    adapter = OpenAICompatAdapter()
    adapter.load({
        "id": "hosted",
        "runtime_config": {
            "base_url": "https://example.test/v1",
            "model": "served",
        },
    })
    try:
        adapter.generate(GenerationRequest(prompt="test"))
    except RuntimeError as error:
        assert "Retry-After: 17" in str(error)
        assert "wait that long before retrying" in str(error)
    else:
        raise AssertionError("expected the simulated HTTP 429")


def test_partial_qualification_routes_to_resume_without_duplicate_calls(
        monkeypatch, capsys):
    def fail(*_args, **_kwargs):
        raise engine.RunExecutionError(
            "3 inference calls failed",
            run_id="run-partial",
            phase="collection",
        )

    monkeypatch.setattr(engine, "start_qualification", fail)
    args = Namespace(
        resume_collection=None,
        resume=None,
        model="subject-a",
        profile="enterprise",
        journey=None,
        rt=2,
        area=["CA-05"],
        repeats=None,
        runtime=None,
        parallel=4,
        _assessment=None,
        decisional=False,
        formal_qualification=False,
        all_areas=False,
        judge=None,
        reviewer_runtime=None,
        judge_batch_size=None,
        json=False,
    )
    assert cli.cmd_qualify(args) == 2
    error = capsys.readouterr().err
    assert "work preserved: partial-run-preserved" in error
    assert "recover: aies qualify --resume-collection run-partial" in error
    assert "completed candidate calls are not repeated" in error


def test_operational_read_commands_share_actionable_recovery(
        tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))

    assert cli.main(["deployment", "inspect", "missing"]) == 2
    deployment_error = capsys.readouterr().err
    assert "recover: aies deployment list" in deployment_error
    assert "duplicate-cost risk: none" in deployment_error

    assert cli.main(["capabilities", "missing-run"]) == 2
    capability_error = capsys.readouterr().err
    assert "recover: aies runs list" in capability_error
    assert "read-only" in capability_error

    assert cli.main(["audit", str(tmp_path / "missing-repository")]) == 2
    audit_error = capsys.readouterr().err
    assert "source-unchanged" in audit_error
    assert "makes no model calls" in audit_error


def test_discovery_failure_routes_to_doctor(monkeypatch, capsys):
    from aies import runtimes

    monkeypatch.setattr(
        runtimes, "discover_all",
        lambda: (_ for _ in ()).throw(RuntimeError("runtime probe failed")))
    assert cli.cmd_discover(Namespace(json=False)) == 2
    error = capsys.readouterr().err
    assert "recover: aies doctor" in error
    assert "registry-preserved" in error


def test_bridge_failure_preserves_source_and_reports_exact_retry(
        tmp_path, capsys):
    missing = tmp_path / "missing.sarif"
    assert cli.main(["bridge", "sarif-import", str(missing)]) == 2
    error = capsys.readouterr().err
    assert "recover: aies bridge sarif-import" in error
    assert "source-preserved" in error
    assert "paid endpoint calls" in error


@pytest.mark.parametrize(
    "argv,recovery",
    [
        (["snapshot", "missing-run"], "aies runs list"),
        (["export", "missing-run"], "aies runs list"),
        (["transcript", "missing-run"], "aies runs list"),
        (["profile", "show", "missing-profile"], "aies profile list"),
        (["runtime", "inspect", "missing-runtime"], "aies runtime list"),
        (["qualification", "show", "QUAL-missing"],
         "aies qualification history"),
        (["suites", "empirical"], "aies suites empirical --help"),
    ],
)
def test_secondary_command_families_use_shared_failure_contract(
        tmp_path, monkeypatch, capsys, argv, recovery):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "workspace"))
    assert cli.main(argv) == 2
    error = capsys.readouterr().err
    assert "duplicate-cost risk: none" in error
    assert f"recover: {recovery}" in error

"""Thin, read-only REST API over the canonical artifacts.

A **consumer, not a decider** (CONFORMANCE-POLICY.md §4): the API serves
artifacts the engine already produced and versioned inventories over their
availability — deployments, runs, evidence packages, Engineering Assessment
Results, optional Formal Assessment Results, explicitly saved comparisons,
and conformance — as JSON. It
computes no outcome and re-derives no decision; product endpoints return
exactly the stored artifact. It is intentionally read-only (no mutation) and
dependency-free (stdlib `http.server`), keeping the platform's only runtime
dependency PyYAML.

The routing is a pure function `route(path) -> (status, body)` so it is testable
without sockets; `serve()` wraps it in an HTTP server for `aies serve`.
"""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import __version__, workspace

_RUN_RESULT = re.compile(r"^/runs/([^/]+)/result$")
_RUN_EVIDENCE = re.compile(r"^/runs/([^/]+)/evidence$")
_RUN_FORMAL_RESULT = re.compile(r"^/runs/([^/]+)/formal-result$")
_RUN_REPORT = re.compile(r"^/runs/([^/]+)/report$")
_RUN_REPORT_VIEW = re.compile(r"^/runs/([^/]+)/report-view$")
_RUN_BUNDLE = re.compile(r"^/runs/([^/]+)/bundle$")
_RUN_EVALUATION = re.compile(r"^/runs/([^/]+)/engineering-evaluation$")
_RUN_ECM = re.compile(r"^/runs/([^/]+)/ecm$")
_RUN_GUIDANCE = re.compile(r"^/runs/([^/]+)/guidance$")
_RUN_EXECUTIVE = re.compile(r"^/runs/([^/]+)/executive-summary$")
_RUN_DIAGNOSTICS = re.compile(r"^/runs/([^/]+)/diagnostics$")
_RUN_COVERAGE = re.compile(r"^/runs/([^/]+)/coverage$")
_RUN_STANDARDS_TRACEABILITY = re.compile(
    r"^/runs/([^/]+)/standards-traceability$")
_RUN_REMEDIATION = re.compile(r"^/runs/([^/]+)/remediation$")
_RUN_DETAIL = re.compile(r"^/runs/([^/]+)$")
_AUDIT_DETAIL = re.compile(r"^/audits/([^/]+)$")
_AUDIT_REMEDIATION = re.compile(r"^/audits/([^/]+)/remediation$")
_COMPARISON_DETAIL = re.compile(r"^/comparisons/([^/]+)$")
_RUN_IMPORT_DETAIL = re.compile(r"^/run-imports/([^/]+)$")
_ASSESSMENT_PROFILE_DETAIL = re.compile(
    r"^/assessment-profiles/([^/]+)$")


def _error(status: int, code: str, message: str, *,
           hint: str | None = None) -> tuple[int, dict]:
    body = {
        "kind": "aies-api-error",
        "schema_version": 1,
        "status": status,
        "code": code,
        "error": message,
    }
    if hint:
        body["hint"] = hint
    return status, body


def route(path: str) -> tuple[int, dict]:
    """Map a GET path to (HTTP status, JSON-able body). Read-only; no decisions."""
    path = path.rstrip("/") or "/"

    if path in ("/", "/health"):
        return 200, {"status": "ok", "service": "aies", "version": __version__,
                     "endpoints": ["/health", "/overview", "/support",
                                   "/deployments", "/runs",
                                   "/runs/{id}",
                                   "/runs/{id}/evidence", "/runs/{id}/result",
                                   "/runs/{id}/formal-result",
                                   "/runs/{id}/report", "/runs/{id}/report-view",
                                   "/runs/{id}/bundle",
                                   "/runs/{id}/engineering-evaluation",
                                   "/runs/{id}/ecm", "/runs/{id}/guidance",
                                   "/runs/{id}/executive-summary",
                                   "/runs/{id}/diagnostics",
                                   "/runs/{id}/coverage",
                                   "/runs/{id}/remediation",
                                   "/audits", "/audits/{id}",
                                   "/audits/{id}/remediation",
                                   "/comparisons", "/comparisons/{id}",
                                   "/run-imports", "/run-imports/{id}",
                                   "/run-cohorts",
                                   "/assessments", "/assessment-profiles",
                                   "/assessment-profiles/{id}",
                                   "/qualifications", "/conformance"]}
    if path == "/overview":
        from . import overview
        return 200, overview.build()
    if path == "/deployments":
        from . import registry
        return 200, {"deployments": registry.list_entries(include_retired=True)}
    if path == "/support":
        from . import support
        return 200, support.describe()
    if path == "/runs":
        from . import compare
        return 200, {"runs": compare.list_runs()}
    if path == "/audits":
        directory = workspace.root() / "audits"
        rows = []
        for artifact in (
                sorted(directory.glob("audit-*.json"), reverse=True)
                if directory.exists() else []):
            value = workspace.read_json(artifact)
            subject = value.get("subject") or {}
            rows.append({
                "audit_id": value.get("audit_id") or artifact.stem,
                "subject_id": subject.get("id"),
                "subject_kind": subject.get("kind"),
                "repository": value.get("repo"),
                "generated_at": value.get("generated_at"),
                "engineering_analysis": bool(
                    value.get("engineering_analysis")),
                "href": f"/audits/{value.get('audit_id') or artifact.stem}",
            })
        return 200, {"audits": rows}
    if path == "/comparisons":
        from . import comparison_report
        return 200, {"comparisons": comparison_report.list_records()}
    if path == "/run-imports":
        from . import run_transfer
        return 200, {
            "kind": "aies-run-import-index",
            "schema": "aies-run-import-index/v1",
            "imports": run_transfer.list_receipts(),
        }
    if path == "/run-cohorts":
        from . import compare
        return 200, compare.discover_run_cohorts()
    if path == "/assessments":
        from . import assessments
        return 200, {"assessments": assessments.list_assessments()}
    if path == "/assessment-profiles":
        from . import assessment_profiles
        return 200, assessment_profiles.describe()
    if path == "/qualifications":
        from . import qualification
        return 200, {"qualifications": qualification.list_records()}
    if path == "/conformance":
        from . import engine_conformance as ec
        try:
            return 200, ec.verify()
        except ec.ConformanceError as e:
            return 503, {"error": str(e)}

    m = _RUN_EVIDENCE.match(path)
    if m:
        return _run_artifact(m.group(1), "evidence-package.json")
    m = _RUN_RESULT.match(path)
    if m:
        run_id = m.group(1)
        engineering = workspace.run_dir(
            run_id) / "engineering-assessment-result.json"
        return _run_artifact(
            run_id,
            "engineering-assessment-result.json"
            if engineering.exists() else "assessment-result.json")
    m = _RUN_FORMAL_RESULT.match(path)
    if m:
        return _run_artifact(m.group(1), "assessment-result.json")
    m = _RUN_REPORT.match(path)
    if m:
        return _run_artifact(m.group(1), "report.json")
    m = _RUN_REPORT_VIEW.match(path)
    if m:
        return _run_artifact(m.group(1), "report-view.json")
    m = _RUN_BUNDLE.match(path)
    if m:
        return _run_artifact(m.group(1), "report-bundle.json")
    m = _RUN_EVALUATION.match(path)
    if m:
        return _run_artifact(m.group(1), "engineering-evaluation.json")
    m = _RUN_ECM.match(path)
    if m:
        return _run_artifact(
            m.group(1), "engineering-capability-matrix.json")
    m = _RUN_GUIDANCE.match(path)
    if m:
        run_id = m.group(1)
        try:
            workspace.validate_run_id(run_id)
        except ValueError as error:
            return _error(400, "invalid-run-id", str(error))
        fit = workspace.run_dir(run_id) / "engineering-fit-guidance.json"
        return _run_artifact(
            run_id,
            "engineering-fit-guidance.json"
            if fit.exists() else "deployment-guidance.json")
    m = _RUN_EXECUTIVE.match(path)
    if m:
        return _run_artifact(m.group(1), "executive-summary.json")
    m = _RUN_DIAGNOSTICS.match(path)
    if m:
        return _run_artifact(m.group(1), "grounding-diagnostics.json")
    m = _RUN_COVERAGE.match(path)
    if m:
        return _run_artifact(m.group(1), "assessment-coverage.json")
    m = _RUN_STANDARDS_TRACEABILITY.match(path)
    if m:
        return _run_artifact(m.group(1), "standards-traceability.json")
    m = _RUN_REMEDIATION.match(path)
    if m:
        return _run_artifact(
            m.group(1), "evidence-remediation-plan.json")
    m = _ASSESSMENT_PROFILE_DETAIL.match(path)
    if m:
        from . import assessment_profiles
        try:
            return 200, assessment_profiles.describe(m.group(1))
        except assessment_profiles.AssessmentProfileError as error:
            return _error(
                404, "assessment-profile-not-found", str(error),
                hint="list profiles with GET /assessment-profiles")
    m = _RUN_DETAIL.match(path)
    if m:
        from . import run_view
        try:
            return 200, run_view.build(m.group(1))
        except ValueError as error:
            return _error(400, "invalid-run-id", str(error))
        except FileNotFoundError as error:
            return _error(
                404, "run-not-found", str(error),
                hint="list available runs with GET /runs")
    m = _AUDIT_REMEDIATION.match(path)
    if m:
        audit_id = m.group(1)
        try:
            workspace.validate_run_id(audit_id)
        except ValueError as error:
            return _error(400, "invalid-audit-id", str(error))
        path = (
            workspace.root() / "reports" / audit_id
            / "evidence-remediation-plan.json")
        if not path.exists():
            return _error(
                404, "artifact-not-found",
                f"repository remediation view for {audit_id!r} was not found",
                hint="run a new repository assessment or regenerate its views")
        return 200, workspace.read_json(path)
    m = _AUDIT_DETAIL.match(path)
    if m:
        audit_id = m.group(1)
        try:
            workspace.validate_run_id(audit_id)
        except ValueError as error:
            return _error(400, "invalid-audit-id", str(error))
        artifact = workspace.root() / "audits" / f"{audit_id}.json"
        if not artifact.exists():
            return _error(
                404, "audit-not-found",
                f"repository assessment {audit_id!r} was not found",
                hint="list available repository assessments with GET /audits")
        return 200, workspace.read_json(artifact)
    m = _COMPARISON_DETAIL.match(path)
    if m:
        comparison_id = m.group(1)
        try:
            workspace.validate_run_id(comparison_id)
        except ValueError as error:
            return _error(400, "invalid-comparison-id", str(error))
        artifact = (
            workspace.root() / "comparisons" / f"{comparison_id}.json")
        if not artifact.exists():
            return _error(
                404, "comparison-not-found",
                f"comparison {comparison_id!r} was not found",
                hint="list saved comparisons with GET /comparisons")
        return 200, workspace.read_json(artifact)
    m = _RUN_IMPORT_DETAIL.match(path)
    if m:
        receipt_id = m.group(1)
        try:
            workspace.validate_run_id(receipt_id)
        except ValueError as error:
            return _error(400, "invalid-run-import-id", str(error))
        artifact = (
            workspace.root() / "run-imports" / f"{receipt_id}.json")
        if not artifact.exists():
            return _error(
                404, "run-import-not-found",
                f"run import {receipt_id!r} was not found",
                hint="list retained import receipts with GET /run-imports")
        return 200, workspace.read_json(artifact)

    return _error(
        404, "route-not-found", f"not found: {path}",
        hint="GET /health lists the supported read-only endpoints")


def _run_artifact(run_id: str, filename: str) -> tuple[int, dict]:
    try:
        workspace.validate_run_id(run_id)
    except ValueError as error:
        return _error(400, "invalid-run-id", str(error))
    path = workspace.run_dir(run_id) / filename
    if not path.exists():
        return _error(
            404, "artifact-not-found",
            f"{filename} not found for run {run_id!r}",
            hint="the run may not have reached the stage that creates this artifact")
    return 200, workspace.read_json(path)


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (stdlib naming)
        status, body = route(self.path.split("?", 1)[0])
        payload = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):  # noqa: N802 — read-only API; mutation is refused
        _, body = _error(
            405, "read-only-api",
            "mutation is not supported; use the CLI for explicit operations",
            hint="this API consumes stored artifacts and never decides outcomes")
        payload = json.dumps(body).encode("utf-8")
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.send_header("Allow", "GET")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):  # keep the server quiet unless asked
        return


def serve(host: str = "127.0.0.1", port: int = 8722) -> None:
    server = ThreadingHTTPServer((host, port), _Handler)
    print(f"aies API (read-only) on http://{host}:{port}  —  GET /health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

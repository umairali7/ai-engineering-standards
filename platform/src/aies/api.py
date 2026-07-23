"""Thin, read-only REST API over the canonical artifacts.

A **consumer, not a decider** (CONFORMANCE-POLICY.md §4): the API only *serves*
artifacts the engine already produced — deployments, runs, evidence packages,
Engineering Assessment Results, optional Formal Assessment Results, and
conformance — as JSON. It computes no outcome and re-derives no decision;
result endpoints return exactly the stored artifact. It is intentionally
read-only (no mutation) and
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


def route(path: str) -> tuple[int, dict]:
    """Map a GET path to (HTTP status, JSON-able body). Read-only; no decisions."""
    path = path.rstrip("/") or "/"

    if path in ("/", "/health"):
        return 200, {"status": "ok", "service": "aies", "version": __version__,
                     "endpoints": ["/health", "/overview", "/support",
                                   "/deployments", "/runs",
                                   "/runs/{id}/evidence", "/runs/{id}/result",
                                   "/runs/{id}/formal-result",
                                   "/assessments", "/qualifications", "/conformance"]}
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
    if path == "/assessments":
        from . import assessments
        return 200, {"assessments": assessments.list_assessments()}
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

    return 404, {"error": f"not found: {path}"}


def _run_artifact(run_id: str, filename: str) -> tuple[int, dict]:
    path = workspace.run_dir(run_id) / filename
    if not path.exists():
        return 404, {"error": f"{filename} not found for run {run_id!r}",
                     "hint": "the run may not be aggregated/decided yet"}
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
        payload = json.dumps({"error": "read-only API — mutation is not supported "
                              "(use the CLI; outcomes are decided by the engine, "
                              "never by a consumer)"}).encode("utf-8")
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

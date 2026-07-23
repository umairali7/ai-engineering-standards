"""Exercise the installed first-run journey without importing the checkout.

Used by cross-platform CI after wheel installation.  The workspace path
intentionally contains spaces and is non-default.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def _run(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess:
    command = [sys.executable, "-m", "aies", *args]
    result = subprocess.run(
        command,
        env=env,
        text=True,
        capture_output=True,
        timeout=240,
    )
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(command)} failed ({result.returncode})\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        help="journey root; default is a temporary directory containing spaces")
    parser.add_argument(
        "--repo",
        default=str(Path(__file__).resolve().parents[2]),
        help="repository to assess in the advisory CI step")
    parser.add_argument(
        "--keep", action="store_true",
        help="retain a generated temporary journey root for inspection")
    args = parser.parse_args()

    generated = args.root is None
    root = (
        Path(tempfile.mkdtemp(prefix="AIES First Run "))
        if generated else Path(args.root).expanduser().resolve()
    )
    workspace = root / "Non Default Workspace"
    ci_artifacts = root / "Retained CI Evidence"
    env = dict(os.environ)
    env["AIES_WORKSPACE"] = str(workspace)
    try:
        _run(["init", str(workspace)], env)
        _run(["demo", "--workspace", str(workspace), "--parallel", "4"], env)
        _run(["discover", "--json"], env)
        deployments = json.loads(_run(["deployment", "list", "--json"], env).stdout)
        deployment_ids = {item["id"] for item in deployments}
        required = {"mock-mock-small", "mock-mock-large"}
        if not required.issubset(deployment_ids):
            raise RuntimeError(
                f"offline demo did not register required deployments: "
                f"{sorted(required - deployment_ids)}")

        _run(["support", "ai-deployment", "--json"], env)
        _run(["starter", "show", "understand-deployment", "--json"], env)
        _run([
            "evaluate", "mock-mock-small",
            "--assessment", "coder",
            "--rt", "1",
            "--judge", "mock-mock-large",
            "--parallel", "4",
        ], env)

        runs = sorted(
            (workspace / "runs").glob("run-*"),
            key=lambda path: path.stat().st_mtime,
        )
        if not runs:
            raise RuntimeError("evaluation produced no durable run")
        run_id = runs[-1].name
        _run(["qualify", "--resume", run_id], env)
        overview = json.loads(_run(["overview", "--json"], env).stdout)
        if not any(item.get("run_id") == run_id and
                   item.get("href") == f"/runs/{run_id}"
                   for item in overview.get("runs", [])):
            raise RuntimeError("workspace overview did not link the completed run")
        run_view = json.loads(
            _run(["runs", "show", run_id, "--json"], env).stdout)
        if (run_view.get("kind") != "aies-run-view"
                or run_view.get("run_id") != run_id
                or not run_view.get("artifacts", {}).get(
                    "engineering_capability_matrix", {}).get("available")):
            raise RuntimeError("run detail view did not expose the completed bundle")
        opened = json.loads(
            _run(["open", run_id, "--no-browser", "--json"], env).stdout)
        if not Path(opened["view"]).is_file():
            raise RuntimeError("open did not resolve a generated report")

        _run([
            "ci", "audit", str(Path(args.repo).resolve()),
            "--rt", "2",
            "--out", str(ci_artifacts),
            "--json",
        ], env)
        expected = {
            "repository-assessment.json",
            "repository-assessment.md",
            "annotations.json",
        }
        produced = {path.name for path in ci_artifacts.iterdir()}
        if not expected.issubset(produced):
            raise RuntimeError(
                f"CI evidence bundle is incomplete: {sorted(expected - produced)}")
        if list(root.rglob(".env")):
            raise RuntimeError("first-run journey unexpectedly wrote a .env file")

        print("clean-install first-run journey: PASS")
        print(f"  workspace : {workspace}")
        print(f"  run       : {run_id}")
        print(f"  report    : {opened['view']}")
        print(f"  CI evidence: {ci_artifacts}")
        return 0
    finally:
        if generated and not args.keep:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

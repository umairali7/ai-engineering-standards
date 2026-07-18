"""`python -m aies` must propagate the CLI's return code as the process exit
status — otherwise shell/CI gating (e.g. `--gate`) silently always 'passes'.
Regression test for __main__ discarding main()'s return value."""

import subprocess
import sys
from pathlib import Path

SRC = str(Path(__file__).resolve().parent.parent / "src")


def _run(args, cwd=None):
    env = {"PYTHONPATH": SRC, "AIES_ENV_FILE": ("/dev/null" if sys.platform != "win32" else "NUL")}
    import os
    full = {**os.environ, **env}
    return subprocess.run([sys.executable, "-m", "aies", *args], cwd=cwd,
                          capture_output=True, text=True, env=full)


def test_module_entrypoint_propagates_error_code(tmp_path):
    # a non-existent repo makes `audit` return 2 — the process must exit 2, not 0
    r = _run(["audit", str(tmp_path / "nope")])
    assert r.returncode == 2, r.stderr


def test_module_entrypoint_propagates_success():
    r = _run(["--help"])
    assert r.returncode == 0

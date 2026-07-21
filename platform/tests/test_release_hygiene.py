"""The release hygiene gate detects all forbidden tracked artifacts."""

import importlib.util
from pathlib import Path


_PATH = Path(__file__).resolve().parent.parent / "scripts" / "check_release_artifacts.py"
_SPEC = importlib.util.spec_from_file_location("release_hygiene", _PATH)
release_hygiene = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(release_hygiene)


def test_release_hygiene_rejects_only_generated_or_sensitive_artifacts():
    paths = [
        "README.md", "platform/.env.example", "platform/src/aies/engine.py",
        ".env", "platform/.DS_Store", "platform/__pycache__/engine.cpython-312.pyc",
        "platform/aies-workspace/runs/run-1/manifest.json",
        "platform/src/aies_platform.egg-info/PKG-INFO", "platform/.pytest_cache/v/cache/nodeids",
    ]
    assert release_hygiene.violations(paths) == [
        (".env", "environment file"),
        ("platform/.DS_Store", "Finder metadata"),
        ("platform/__pycache__/engine.cpython-312.pyc", "Python bytecode"),
        ("platform/aies-workspace/runs/run-1/manifest.json", "generated local artifact directory"),
        ("platform/src/aies_platform.egg-info/PKG-INFO", "packaging metadata"),
        ("platform/.pytest_cache/v/cache/nodeids", "generated local artifact directory"),
    ]

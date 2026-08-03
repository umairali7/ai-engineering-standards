"""ADR-0014 path defaults are exhaustive and fail closed on drift."""

import importlib.util
from pathlib import Path
import sys


_PATH = Path(__file__).resolve().parent.parent / "scripts" / "check_license_boundaries.py"
_SPEC = importlib.util.spec_from_file_location("license_boundaries", _PATH)
license_boundaries = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = license_boundaries
_SPEC.loader.exec_module(license_boundaries)


def test_path_defaults_separate_content_from_software():
    assert license_boundaries.path_default("AESQS/capability-scoring.md") == license_boundaries.CC
    assert license_boundaries.path_default("platform/competencies/CA-05/scenario.yaml") == license_boundaries.CC
    assert license_boundaries.path_default("platform/measurement-claims-v1.yaml") == license_boundaries.CC
    assert license_boundaries.path_default("conformance/corpus/all-pass/expected.json") == license_boundaries.CC
    assert license_boundaries.path_default("platform/src/aies/cli.py") == license_boundaries.APACHE
    assert license_boundaries.path_default("platform/contracts/run.json") == license_boundaries.APACHE
    assert license_boundaries.path_default(".github/workflows/platform-ci.yml") == license_boundaries.APACHE


def test_repository_license_boundary_is_complete_and_license_texts_are_exact():
    root = Path(__file__).resolve().parents[2]
    problems, counts = license_boundaries.violations(root)
    assert problems == []
    assert counts[license_boundaries.CC] > 0
    assert counts[license_boundaries.APACHE] > 0
    assert counts[license_boundaries.LICENSE_TEXT] == 2

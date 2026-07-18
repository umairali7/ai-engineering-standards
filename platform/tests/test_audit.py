"""Repository conformance audit (ADR-0004): three-state evidence never
false-greens, maturity rolls up from evidence, --gate enforces RT-required
evidence, and attestation covers only non-detectable practices."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _write(root: Path, rel: str, content: str = "x"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _good_repo(tmp_path) -> Path:
    """A repo that satisfies every RT2-required check (non-git)."""
    r = tmp_path / "good"
    _write(r, "pyproject.toml", "[project]\nname='x'")
    _write(r, "poetry.lock", "# locked")
    _write(r, "tests/test_x.py", "def test_x(): assert True")
    _write(r, ".gitignore", "# secrets\n.env\n")
    _write(r, ".github/workflows/ci.yml", "steps:\n  - run: pytest --cov\n")
    _write(r, ".github/pull_request_template.md", "## Assumptions\n## Risk\n")
    _write(r, "SECURITY.md", "report to ...")
    _write(r, "GOVERNANCE.md", "governance and risk tier policy; autonomy level")
    _write(r, "adr/ADR-0001.md", "# decision")
    _write(r, "docs/CONFORMANCE.md", "conformance statement")
    _write(r, "CLAUDE.md", "agent/context instructions")
    _write(r, "CODEOWNERS", "* @team")
    return r


def _bare_repo(tmp_path) -> Path:
    r = tmp_path / "bare"
    _write(r, "README.md", "# a project")
    return r


def test_good_repo_scores_and_passes_rt2_gate(ws, tmp_path):
    from aies import audit
    res = audit.run_audit(_good_repo(tmp_path), rt="RT2")
    assert res["totals"]["verified"] >= 8
    assert res["gate"]["passed"] is True, res["gate"]["failures"]
    # strong areas reach at least ML2
    assert res["areas"]["CA-07"]["maturity"] >= 2
    assert res["areas"]["CA-05"]["maturity"] >= 2


def test_bare_repo_is_gaps_not_false_green(ws, tmp_path):
    from aies import audit
    res = audit.run_audit(_bare_repo(tmp_path), rt="RT2")
    assert res["totals"]["verified"] == 0
    assert res["totals"]["gap"] >= 10
    # every area is ML0 (nothing evidenced, nothing asserted)
    assert all(a["maturity"] == 0 for a in res["areas"].values())
    assert res["gate"]["passed"] is False and res["gate"]["failures"]


def test_attestation_covers_only_non_detectable(ws, tmp_path):
    from aies import audit
    repo = _bare_repo(tmp_path)
    attest = {"items": [
        {"id": "ca10-branch-protection", "evidence": "GH branch protection screenshot"},
        {"id": "ca11-context", "evidence": "prompts in another repo"},   # auto-detectable
    ]}
    res = audit.run_audit(repo, rt="RT3", attestations=attest)
    states = {c["id"]: c["state"] for a in res["areas"].values() for c in a["checks"]}
    # a non-detectable check becomes asserted and satisfies the gate
    assert states["ca10-branch-protection"] == "asserted"
    # an auto-detectable check can be asserted but must NOT pass its gate that way
    assert states["ca11-context"] == "asserted"
    failed_ids = {f["id"] for f in res["gate"]["failures"]}
    assert "ca10-branch-protection" not in failed_ids     # attestation accepted
    assert "ca11-context" in failed_ids                   # can't assert past a detectable control


def test_maturity_enforcement_band(ws, tmp_path):
    """An area reaches ML3 only when its enforcement-band checks are satisfied."""
    from aies import audit
    res = audit.run_audit(_good_repo(tmp_path))
    ca06 = res["areas"]["CA-06"]
    # tests present + CI test gate (enforcement) + coverage => ML3
    assert ca06["maturity"] >= 3


def test_every_check_maps_to_an_area_and_is_stable(ws, tmp_path):
    from aies import audit, audit_checks
    ids = [c.id for c in audit_checks.CHECKS]
    assert len(ids) == len(set(ids))                       # unique ids
    assert all(c.area in audit.AREA_NAMES for c in audit_checks.CHECKS)
    # audit never raises on an empty dir
    res = audit.run_audit(_bare_repo(tmp_path))
    assert res["n_checks"] == len(audit_checks.CHECKS)

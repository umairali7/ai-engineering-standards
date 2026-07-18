"""Repository conformance audit (ADR-0004).

`aies audit <repo>` assesses a **repository and the engineering practice
evidenced in it** against the AIES competency areas — a different subject from
`aies qualify` (which scores a model deployment on EV1–EV6). It reuses the CA
taxonomy but scores **maturity ML0–ML4**, with **three-state evidence** that is
never false-green:

- **verified** — a checker found evidence in the repo.
- **asserted** — not file-detectable; the team attested it (with an evidence
  pointer) in an attestation file.
- **gap** — neither; absence of signal is always a gap.

This module holds the scoring model, the repository scanner (`RepoContext`), the
`Check` contract, and the engine. The checks themselves live in
`audit_checks.py`. Non-goals (ADR-0004): this is not a SAST/secret/dependency
scanner or an oracle — it detects that such practices/tools are *present* and
maps them to external standards; a human still judges.
"""

from __future__ import annotations

import datetime
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import workspace

# --- Maturity model (ML0–ML4) --------------------------------------------------
MATURITY = {
    0: "Absent — no evidence and no attestation",
    1: "Initial — claimed but not evidenced",
    2: "Managed — the practice exists and is evidenced",
    3: "Defined — evidenced and enforced (tested / gated)",
    4: "Optimizing — enforced and measured on a cycle",
}
STATES = ("verified", "asserted", "gap")
RISK_TIERS = ("RT1", "RT2", "RT3", "RT4")

#: Competency-area names (CA-01…CA-12), the audit's reporting axis.
AREA_NAMES = {
    "CA-01": "AI-Native SDLC Foundations",
    "CA-02": "Business & Requirements Analysis",
    "CA-03": "Product & Experience Definition",
    "CA-04": "Architecture & Solution Design",
    "CA-05": "AI-Assisted Implementation",
    "CA-06": "Testing, Quality & Evaluation",
    "CA-07": "Security & Privacy Engineering",
    "CA-08": "Delivery & Release Engineering",
    "CA-09": "Operations, Observability & Reliability",
    "CA-10": "Human-AI Collaboration & Oversight",
    "CA-11": "Context & Knowledge Engineering",
    "CA-12": "Governance, Risk & AI Safety",
}

#: A check's maturity *band*: what it demonstrates when satisfied.
#: 2 = existence, 3 = enforcement (tested/gated), 4 = measurement/review.
BAND_EXISTENCE, BAND_ENFORCEMENT, BAND_MEASUREMENT = 2, 3, 4


@dataclass
class Check:
    """A single, pluggable conformance check.

    `detect(ctx)` returns (True, detail) when evidence is found, else
    (False, detail). `required_at` is the lowest risk tier at which a passing
    result is required for `--gate` (None = advisory only). `auto=False` marks a
    check that cannot be file-detected (attestation-only)."""
    id: str
    area: str                      # CA-NN
    title: str
    band: int                      # BAND_EXISTENCE | ENFORCEMENT | MEASUREMENT
    detect: Callable[["RepoContext"], tuple[bool, str]]
    external: str = ""             # external-standard mapping (CROSSWALK)
    required_at: str | None = None  # "RT2" etc., or None
    auto: bool = True              # False = attestation-only (never auto-verifiable)
    recommendation: str = ""


# --- Repository scanner --------------------------------------------------------
_SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache",
              ".pytest_cache", "dist", "build", ".idea", ".tox", "target"}


class RepoContext:
    """Scans a repository once; checks query it (read-only)."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"not a directory: {self.root}")
        self.files: list[str] = []          # repo-relative POSIX paths
        for p in self.root.rglob("*"):
            if any(part in _SKIP_DIRS for part in p.relative_to(self.root).parts):
                continue
            if p.is_file():
                self.files.append(p.relative_to(self.root).as_posix())
        self._lower = [f.lower() for f in self.files]
        self.commit_bodies, self.is_git = self._git_log()
        self.tracked = self._git_tracked()   # set of repo-relative tracked paths

    # -- git ------------------------------------------------------------------
    def _git_log(self, n: int = 50) -> tuple[str, bool]:
        try:
            out = subprocess.run(
                ["git", "-C", str(self.root), "log", f"-{n}", "--format=%an%x1f%b%x1e"],
                capture_output=True, text=True, timeout=20)
            if out.returncode != 0:
                return "", False
            return out.stdout, True
        except Exception:
            return "", False

    def _git_tracked(self) -> set[str]:
        try:
            out = subprocess.run(["git", "-C", str(self.root), "ls-files"],
                                 capture_output=True, text=True, timeout=20)
            if out.returncode != 0:
                return set()
            return {line.strip() for line in out.stdout.splitlines() if line.strip()}
        except Exception:
            return set()

    def is_tracked(self, *basenames: str) -> bool:
        """True if git tracks a file with one of these basenames. Empty (never
        true) for a non-git repo — callers should fall back to has_glob there."""
        want = {b.lower() for b in basenames}
        return any(t.rsplit("/", 1)[-1].lower() in want for t in self.tracked)

    # -- queries --------------------------------------------------------------
    def has(self, *substrings: str) -> bool:
        """True if any file path contains any of the given substrings (lowercased)."""
        subs = [s.lower() for s in substrings]
        return any(any(s in f for s in subs) for f in self._lower)

    def has_glob(self, *patterns: str) -> bool:
        """True if any file matches a pattern by full path OR by basename, so a
        bare filename like `pyproject.toml` also matches `platform/pyproject.toml`."""
        from fnmatch import fnmatch
        pats = [p.lower() for p in patterns]
        for f in self._lower:
            base = f.rsplit("/", 1)[-1]
            if any(fnmatch(f, pat) or fnmatch(base, pat) for pat in pats):
                return True
        return False

    def matching(self, *substrings: str) -> list[str]:
        subs = [s.lower() for s in substrings]
        return [orig for orig, low in zip(self.files, self._lower)
                if any(s in low for s in subs)]

    def read(self, relpath: str) -> str:
        try:
            return (self.root / relpath).read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""

    def grep(self, needle: str, *globs: str, max_files: int = 60) -> bool:
        """True if `needle` (case-insensitive) appears in any file matching globs
        (or any text file if no globs). Bounded for speed."""
        from fnmatch import fnmatch
        needle_l = needle.lower()
        checked = 0
        for f in self.files:
            if globs and not any(fnmatch(f.lower(), g) for g in globs):
                continue
            checked += 1
            if checked > max_files:
                break
            if needle_l in self.read(f).lower():
                return True
        return False

    def commits_have(self, *needles: str) -> bool:
        body = self.commit_bodies.lower()
        return any(n.lower() in body for n in needles)


# --- Engine --------------------------------------------------------------------
def _load_checks() -> list[Check]:
    from . import audit_checks
    return audit_checks.CHECKS


def _rt_index(rt: str | None) -> int:
    return RISK_TIERS.index(rt) if rt in RISK_TIERS else -1


def evaluate(ctx: RepoContext, attestations: dict | None = None) -> list[dict]:
    """Run every check and resolve its three-state result."""
    attested = set((attestations or {}).get("attested", []))
    attest_ev = {a.get("id"): a.get("evidence", "")
                 for a in (attestations or {}).get("items", []) if isinstance(a, dict)}
    results = []
    for c in _load_checks():
        detail = ""
        if c.auto:
            try:
                ok, detail = c.detect(ctx)
            except Exception as e:  # a check must never crash the audit
                ok, detail = False, f"check error: {e.__class__.__name__}"
        else:
            ok = False
        if ok:
            state, evidence = "verified", detail
        elif c.id in attested or c.id in attest_ev:
            state, evidence = "asserted", attest_ev.get(c.id, "attested")
        else:
            state, evidence = "gap", detail
        results.append({"id": c.id, "area": c.area, "title": c.title,
                        "band": c.band, "auto": c.auto, "external": c.external,
                        "required_at": c.required_at, "state": state,
                        "evidence": evidence, "recommendation": c.recommendation})
    return results


def _area_maturity(area_results: list[dict]) -> int:
    verified_bands = {r["band"] for r in area_results if r["state"] == "verified"}
    satisfied_bands = {r["band"] for r in area_results
                       if r["state"] in ("verified", "asserted")}
    if not satisfied_bands:
        return 0
    if not verified_bands:            # only assertions, nothing evidenced
        return 1
    ml = 2 if BAND_EXISTENCE in satisfied_bands else 1
    # enforcement: every enforcement-band check in the area must be satisfied
    enf = [r for r in area_results if r["band"] == BAND_ENFORCEMENT]
    if ml >= 2 and enf and all(r["state"] in ("verified", "asserted") for r in enf):
        ml = 3
    meas = [r for r in area_results if r["band"] == BAND_MEASUREMENT]
    if ml >= 3 and meas and all(r["state"] in ("verified", "asserted") for r in meas):
        ml = 4
    return ml


def _gate(results: list[dict], rt: str) -> dict:
    """A required check passes the gate if verified, or — for a genuinely
    non-auto-detectable check — asserted. A gap, or an assertion standing in for
    a detectable control, fails."""
    want = _rt_index(rt)
    failures = []
    for r in results:
        req = r["required_at"]
        if req is None or _rt_index(req) > want:
            continue
        passed = r["state"] == "verified" or (r["state"] == "asserted" and not r["auto"])
        if not passed:
            failures.append(r)
    return {"risk_tier": rt, "passed": not failures,
            "failures": [{"id": f["id"], "area": f["area"], "title": f["title"],
                          "state": f["state"]} for f in failures]}


def run_audit(repo: str | Path, attestations: dict | None = None,
              rt: str | None = None, record: bool = True) -> dict:
    """Audit a repository; returns the structured result (and persists it)."""
    ctx = RepoContext(repo)
    results = evaluate(ctx, attestations)

    areas = {}
    for r in results:
        areas.setdefault(r["area"], []).append(r)
    area_summ = {}
    for area, rs in sorted(areas.items()):
        counts = {s: sum(1 for r in rs if r["state"] == s) for s in STATES}
        area_summ[area] = {
            "area": area,
            "name": AREA_NAMES.get(area, area),
            "maturity": _area_maturity(rs),
            "counts": counts, "n_checks": len(rs),
            "checks": rs,
        }

    totals = {s: sum(1 for r in results if r["state"] == s) for s in STATES}
    auto_checks = sum(1 for r in results if r["auto"])
    result = {
        "kind": "audit",
        "repo": str(ctx.root),
        "is_git": ctx.is_git,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "n_checks": len(results),
        "auto_checks": auto_checks,
        "attestation_checks": len(results) - auto_checks,
        "totals": totals,
        "areas": area_summ,
        "gate": _gate(results, rt) if rt else None,
    }
    if record:
        try:
            audit_id = "audit-" + datetime.datetime.now(
                datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            workspace.write_json(workspace.root() / "audits" / f"{audit_id}.json", result)
            result["audit_id"] = audit_id
        except Exception:
            pass
    return result


# --- Rendering -----------------------------------------------------------------
_STATE_MARK = {"verified": "✓ verified", "asserted": "~ asserted", "gap": "✗ gap"}


def render_markdown(result: dict) -> str:
    t = result["totals"]
    out = [f"# Conformance Audit — {result['repo']}", ""]
    out.append(f"AIES repository conformance audit (ADR-0004). Maturity ML0–ML4 per "
               f"competency area; evidence is **verified** (found in repo), "
               f"**asserted** (attested with evidence), or **gap**. Absence is a gap, "
               f"never a pass.")
    out.append("")
    out.append(f"- Checks: **{result['n_checks']}** "
               f"({result['auto_checks']} auto-detected, "
               f"{result['attestation_checks']} attestation-only)")
    out.append(f"- Evidence: **{t['verified']} verified**, {t['asserted']} asserted, "
               f"**{t['gap']} gaps**")
    if result.get("gate"):
        g = result["gate"]
        out.append(f"- Gate ({g['risk_tier']}): **{'PASS' if g['passed'] else 'FAIL'}**"
                   + (f" — missing: {', '.join(f['id'] for f in g['failures'])}"
                      if g["failures"] else ""))
    out += ["", "## Maturity by competency area", "",
            "| Area | | ML | verified | asserted | gap |",
            "|------|--|----|---------|----------|-----|"]
    for a in result["areas"].values():
        c = a["counts"]
        out.append(f"| {a['area']} | {a['name']} | **ML{a['maturity']}** | "
                   f"{c['verified']} | {c['asserted']} | {c['gap']} |")

    # Recommendations: gaps first, gate-required ones on top.
    gaps = [c for a in result["areas"].values() for c in a["checks"]
            if c["state"] == "gap"]
    gaps.sort(key=lambda c: (c["required_at"] or "RT9", c["area"]))
    if gaps:
        out += ["", "## Recommendations (ranked)", ""]
        for c in gaps:
            req = f" _(required at {c['required_at']})_" if c["required_at"] else ""
            ext = f" · maps to {c['external']}" if c["external"] else ""
            out.append(f"- **{c['area']} {c['title']}**{req} — {c['recommendation']}{ext}")
    out += ["", "---", "*Evidence, not checkboxes: this audit prepares evidence; a "
            "human records any conformance decision. Non-detectable practices require "
            "attestation (`--attest`).*"]
    return "\n".join(out)

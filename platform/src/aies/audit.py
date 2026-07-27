"""Repository assessment: conformance plus engineering analysis.

`aies audit <repo>` assesses a **repository and the engineering practice
evidenced in it** against the AIES competency areas — a different subject from
`aies qualify` (which scores a model deployment on EV1–EV6). It reuses the CA
taxonomy but scores **maturity ML0–ML4**, with **three-state evidence** that is
never false-green:

- **verified** — a checker found evidence in the repo.
- **asserted** — not file-detectable; the team attested it (with an evidence
  pointer) in an attestation file.
- **gap** — neither; absence of signal is always a gap.

This module holds the conformance scoring model, repository scanner
(`RepoContext`), `Check` contract, report bundle, and orchestration engine. The
practice checks live in `audit_checks.py`; the separate, non-decisional
engineering perspectives live in `repository_analysis.py`.

The analysis is deliberately not a SAST, secret scanner, vulnerability scanner,
or correctness oracle. It consumes repository structure and retained,
machine-readable evidence without executing repository code. Its findings and
remediation are decision support, not qualification or authorization.
"""

from __future__ import annotations

import datetime
import html
import json
import subprocess
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import constants as C, evidence_events, workspace

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
        self.files.sort()
        self._lower = [f.lower() for f in self.files]
        self._read_cache: dict[str, str] = {}
        self.commit_bodies, self.is_git = self._git_log()
        self.tracked = self._git_tracked()   # set of repo-relative tracked paths

    # -- git ------------------------------------------------------------------
    def _git_log(self, n: int = 50) -> tuple[str, bool]:
        try:
            probe = subprocess.run(
                ["git", "-C", str(self.root), "rev-parse",
                 "--is-inside-work-tree"],
                capture_output=True, text=True, timeout=20)
            if (probe.returncode != 0
                    or probe.stdout.strip().lower() != "true"):
                return "", False
            out = subprocess.run(
                ["git", "-C", str(self.root), "log", f"-{n}", "--format=%an%x1f%b%x1e"],
                capture_output=True, text=True, timeout=20)
            if out.returncode != 0:
                return "", True
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
        if relpath in self._read_cache:
            return self._read_cache[relpath]
        try:
            text = (self.root / relpath).read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = ""
        self._read_cache[relpath] = text
        return text

    def grep(self, needle: str, *globs: str, max_files: int | None = None) -> bool:
        """True if `needle` (case-insensitive) appears in any file matching globs
        (or any text file if no globs).

        Detection is exhaustive and deterministic. The previous first-60-files
        bound produced false negatives in repositories with large YAML corpora:
        a real CI workflow could be skipped merely because scenario files were
        visited first. File contents are cached, so exhaustive checks remain
        inexpensive for this repository-scale scanner. ``max_files`` remains an
        accepted compatibility argument but no longer changes evidence truth.
        """
        from fnmatch import fnmatch
        needle_l = needle.lower()
        for f in self.files:
            if globs and not any(fnmatch(f.lower(), g) for g in globs):
                continue
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


def _scope_notice(root: Path, is_git: bool) -> dict | None:
    """Disclose when a command audits only a subdirectory of a Git repository."""
    if not is_git:
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    git_root = Path(completed.stdout.strip()).resolve()
    selected = root.resolve()
    if git_root == selected:
        return None
    return {
        "kind": "git-subdirectory-scope",
        "selected_root": str(selected),
        "repository_root": str(git_root),
        "complete_repository": False,
        "message": (
            "Only a subdirectory of the enclosing Git repository was audited. "
            "Absence-based repository-practice gaps may be scope artifacts "
            "when the evidence exists above the selected root."),
        "suggested_command": f'aies audit "{git_root}"',
    }


def run_audit(repo: str | Path, attestations: dict | None = None,
              rt: str | None = None, record: bool = True,
              engineering_analysis: bool = False) -> dict:
    """Audit a repository; returns the structured result (and persists it)."""
    ctx = RepoContext(repo)
    scope_notice = _scope_notice(ctx.root, ctx.is_git)
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
    from . import repository_analysis
    analysis = (
        repository_analysis.analyze(ctx, results)
        if engineering_analysis else None)
    if analysis:
        subject = analysis["subject"]
        scope_digest = analysis["snapshot"]["scope_digest"]
    else:
        snapshot = repository_analysis._snapshot(ctx)
        subject = repository_analysis._repository_descriptor(
            ctx, snapshot, repository_analysis._source_files(ctx))
        scope_digest = snapshot["scope_digest"]
    conformance_events = [
        evidence_events.build(
            event_type="observation",
            subject_id=subject["id"],
            instrument_id=check["id"],
            modality="repository-static-analysis",
            source="aies-repository-conformance-audit",
            source_record_id=check["id"],
            source_digest=scope_digest,
            adapter_profile="aies-repository-conformance/v1",
            classification=subject["privacy"],
            payload={
                "area": check["area"],
                "state": check["state"],
                "band": check["band"],
                "auto": check["auto"],
                "required_at": check["required_at"],
                "evidence": check["evidence"],
            },
        )
        for check in results
    ]
    all_events = conformance_events + (analysis["events"] if analysis else [])
    result = {
        "kind": "audit",
        "schema": "aies-repository-assessment/v1",
        "subject": subject,
        "repo": str(ctx.root),
        "is_git": ctx.is_git,
        "scope_notice": scope_notice,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "n_checks": len(results),
        "auto_checks": auto_checks,
        "attestation_checks": len(results) - auto_checks,
        "totals": totals,
        "areas": area_summ,
        "gate": _gate(results, rt) if rt else None,
        "engineering_analysis": analysis,
        "events": all_events,
        "event_replay": evidence_events.replay(all_events),
        "claim_boundary": (
            "Repository-practice maturity and engineering-analysis evidence "
            "remain separate. Neither proves source correctness, security, "
            "fitness, or authorization."),
    }
    if record:
        record_result(result)
    return result


def record_result(result: dict) -> str:
    """Persist one append-only repository assessment with collision-safe id."""
    audit_id = (
        "audit-"
        + datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ")
        + "-"
        + uuid.uuid4().hex[:6]
    )
    result["audit_id"] = audit_id
    workspace.write_json(
        workspace.root() / "audits" / f"{audit_id}.json", result)
    from . import remediation
    remediation.write_repository_view(
        audit_id, remediation.for_reference(audit_id))
    return audit_id


def write_bundle(result: dict, destination: str | Path) -> dict:
    """Write a self-contained repository assessment bundle."""
    target = Path(destination).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": target / "repository-assessment.json",
        "markdown": target / "repository-assessment.md",
        "html": target / "repository-assessment.html",
        "coverage_markdown": target / "assessment-coverage.md",
        "coverage_json": target / "assessment-coverage.json",
        "coverage_html": target / "assessment-coverage.html",
        "remediation_markdown": target / "evidence-remediation-plan.md",
        "remediation_json": target / "evidence-remediation-plan.json",
        "remediation_html": target / "evidence-remediation-plan.html",
        "bundle": target / "repository-assessment-bundle.json",
    }
    existing = [str(path) for path in paths.values() if path.exists()]
    if existing:
        raise FileExistsError(
            "repository assessment output is immutable; already exists: "
            + ", ".join(existing))
    markdown = render_markdown(result)
    paths["json"].write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    paths["markdown"].write_text(markdown, encoding="utf-8")
    paths["html"].write_text(_render_html(result), encoding="utf-8")
    from . import assessment_coverage
    coverage_paths = assessment_coverage.write_repository_artifacts(
        result, target)
    assert set(coverage_paths) == {
        "coverage_markdown", "coverage_json", "coverage_html",
        "remediation_markdown", "remediation_json", "remediation_html"}
    bundle = {
        "kind": "aies-repository-assessment-bundle",
        "schema": 1,
        "audit_id": result.get("audit_id"),
        "subject": result.get("subject"),
        "artifacts": {
            name: path.name for name, path in paths.items() if name != "bundle"
        },
        "claim_boundary": result.get("claim_boundary"),
        "coverage_boundary": (
            "Assessment coverage reports evidence availability and blind "
            "spots; it is not repository quality or conformance."),
        "remediation_boundary": (
            "Generated actions are unassigned decision support; they do not "
            "accept risk, prove remediation, close findings, or authorize."),
    }
    paths["bundle"].write_text(
        json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return {name: str(path) for name, path in paths.items()}


def _render_html(result: dict) -> str:
    analysis = result.get("engineering_analysis") or {}
    perspectives = analysis.get("perspectives") or {}
    rows = []
    for name, value in perspectives.items():
        confidence = value["confidence"]
        rows.append(
            "<tr><td>" + html.escape(name.replace("_", " ").title())
            + "</td><td>" + html.escape(value["status"])
            + "</td><td>" + html.escape(confidence["level"])
            + f" ({confidence['coverage_percent']:.0f}%)</td><td>"
            + str(len(value["findings"])) + "</td></tr>")
    findings = []
    for finding in analysis.get("findings") or []:
        artifacts = ", ".join(finding["artifacts"]) or "no retained artifact"
        findings.append(
            "<li><strong>" + html.escape(
                f"{finding['severity'].upper()} · {finding['id']}")
            + "</strong> — " + html.escape(finding["title"])
            + "<br><small>Evidence: " + html.escape(artifacts)
            + "</small></li>")
    maturity = []
    for area in result["areas"].values():
        counts = area["counts"]
        maturity.append(
            "<tr><td>" + html.escape(f"{area['area']} — {area['name']}")
            + f"</td><td>ML{area['maturity']}</td><td>{counts['verified']}"
            + f"</td><td>{counts['asserted']}</td><td>{counts['gap']}</td></tr>")
    scope_notice = result.get("scope_notice") or {}
    scope_html = (
        "<p class=notice><strong>Partial repository scope.</strong> "
        + html.escape(scope_notice["message"])
        + "<br>Full-repository command: <code>"
        + html.escape(scope_notice["suggested_command"])
        + "</code></p>"
        if scope_notice else "")
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AIES Repository Assessment</title><style>
:root{color-scheme:light dark;--line:#8885;--card:#8881}
body{font:15px/1.5 system-ui,sans-serif;max-width:1100px;margin:auto;padding:2rem}
table{border-collapse:collapse;width:100%}th,td{padding:.45rem;border-bottom:1px solid var(--line);text-align:left}
.sortable th{cursor:pointer;user-select:none}.sortable th:hover{text-decoration:underline}
.notice{padding:1rem;background:var(--card);border:1px solid var(--line);border-radius:8px}
li{margin:.6rem 0}code{word-break:break-all}</style></head><body>""" + (
        "<h1>AIES Repository Assessment</h1><p class=notice>"
        "<strong>Informational evidence only.</strong> Practice maturity and "
        "engineering analysis do not prove correctness, security, fitness, "
        "conformance, or authorization.</p>" + scope_html + "<p>Subject: <code>"
        + html.escape((result.get("subject") or {}).get("id", "unknown"))
        + "</code></p><h2>Practice maturity</h2><table class=sortable><thead><tr>"
        "<th>Competency area</th><th>Maturity</th><th>Verified</th>"
        "<th>Asserted</th><th>Gaps</th></tr></thead><tbody>"
        + "".join(maturity)
        + "</tbody></table><h2>Engineering perspectives</h2><table class=sortable><thead><tr>"
        "<th>Perspective</th><th>Status</th><th>Evidence confidence</th>"
        "<th>Findings</th></tr></thead><tbody>" + "".join(rows)
        + "</tbody></table><h2>Evidence-linked findings</h2><ol>"
        + ("".join(findings) or
           "<li>No bounded analyzer finding was emitted; this is not proof of absence.</li>")
        + "</ol><footer><p>" + html.escape(result.get("claim_boundary", ""))
        + """</p></footer><script>
document.querySelectorAll("table.sortable th").forEach((header,index)=>{
  header.title="Sort by this column";
  header.addEventListener("click",()=>{
    const body=header.closest("table").tBodies[0];
    const rows=[...body.rows];
    const ascending=header.dataset.order!=="asc";
    rows.sort((left,right)=>{
      const a=left.cells[index].textContent.trim();
      const b=right.cells[index].textContent.trim();
      const an=Number(a.replace(/[^0-9.+-]/g,""));
      const bn=Number(b.replace(/[^0-9.+-]/g,""));
      const value=Number.isNaN(an)||Number.isNaN(bn)
        ? a.localeCompare(b,undefined,{numeric:true,sensitivity:"base"})
        : an-bn;
      return ascending?value:-value;
    });
    [...header.parentElement.children].forEach(item=>delete item.dataset.order);
    header.dataset.order=ascending?"asc":"desc";
    rows.forEach(row=>body.appendChild(row));
  });
});
</script></body></html>""")


# --- Rendering -----------------------------------------------------------------
_STATE_MARK = {"verified": "✓ verified", "asserted": "~ asserted", "gap": "✗ gap"}


def render_markdown(result: dict) -> str:
    t = result["totals"]
    out = [f"# Conformance Audit — {result['repo']}", ""]
    out.append(f"AIES repository conformance audit "
               f"(ADR-0004 — executable repository conformance assessment). "
               f"Maturity ML0–ML4 per "
               f"competency area; evidence is **verified** (found in repo), "
               f"**asserted** (attested with evidence), or **gap**. Absence is a gap, "
               f"never a pass.")
    out.append("")
    scope_notice = result.get("scope_notice")
    if scope_notice:
        out.extend([
            "> **PARTIAL REPOSITORY SCOPE** — "
            + scope_notice["message"],
            ">",
            f"> Full-repository command: "
            f"`{scope_notice['suggested_command']}`",
            "",
        ])
    out.append(f"- Checks: **{result['n_checks']}** "
               f"({result['auto_checks']} auto-detected, "
               f"{result['attestation_checks']} attestation-only)")
    out.append(f"- Evidence: **{t['verified']} verified**, {t['asserted']} asserted, "
               f"**{t['gap']} gaps**")
    if result.get("audit_id"):
        out.append(f"- Assessment record: `{result['audit_id']}`")
    if result.get("gate"):
        g = result["gate"]
        out.append(f"- Gate ({C.risk_tier_label(g['risk_tier'])}): **{'PASS' if g['passed'] else 'FAIL'}**"
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
            req = (
                f" _(required at {C.risk_tier_label(c['required_at'])})_"
                if c["required_at"] else "")
            ext = f" · maps to {c['external']}" if c["external"] else ""
            out.append(f"- **{c['area']} {c['title']}**{req} — {c['recommendation']}{ext}")
    if result.get("engineering_analysis"):
        from . import repository_analysis
        out += ["", repository_analysis.render_markdown(
            result["engineering_analysis"])]
    out += ["", "---", "*Evidence, not checkboxes: this audit prepares evidence; a "
            "human records any conformance decision. Non-detectable practices require "
            "attestation (`--attest`).*"]
    return "\n".join(out)

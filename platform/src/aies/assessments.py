"""Assessment loading & validation (ADR-0005).

An **assessment** is declarative data: which competencies compose a named
qualification, whether each is mandatory or advisory, their weights, the
EV-weighting profile, and sampling. Assessment authors declare *what to assess
and how much it matters*; the **engine** owns *how it decides* — the decision
algorithm, gate semantics, statistical minimums, AL caps, and outcome precedence
(ADR-0005 D-B1). Validation enforces that boundary with a **strict allowed-key
schema** (an author literally cannot add a `gates:` or `min_sample:` key) plus
semantic-consistency checks.

Decisions are made elsewhere (the decision engine, ADR-0005 D-B4); this module
only loads and validates the data.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from . import constants as C
from . import profiles, runner

SUPPORTED_SCHEMA = 1
REQUIREMENT_TYPES = ("mandatory", "advisory")   # object-form; room to grow (ADR-0005)
CL_LEVELS = ("CL1", "CL2", "CL3", "CL4")

# Strict allowed keys — anything else is rejected as an attempt to redefine
# engine-owned semantics (the declarative/engine-owned boundary).
_ALLOWED_TOP = {"id", "version", "schema", "description", "profile",
                "default_risk_tier", "competencies", "sampling"}
_ALLOWED_COMPETENCY = {"area", "requirement", "weight", "min_cl"}
_ALLOWED_REQUIREMENT = {"type"}
_ALLOWED_SAMPLING = {"repeats"}

_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


class AssessmentError(Exception):
    pass


def assessments_dir() -> Path:
    from .resources import data_root
    return data_root() / "assessments"


def _requirement_type(comp: dict) -> str | None:
    """Normalize requirement -> a type string (default 'mandatory'). Accepts the
    canonical object form {type: X} and, tolerantly, a bare string."""
    req = comp.get("requirement", {"type": "mandatory"})
    if isinstance(req, dict):
        return req.get("type", "mandatory")
    if isinstance(req, str):
        return req
    return None


def validate(a: dict) -> list[str]:
    """Return a list of problems (empty = valid). Enforces the allowed-key
    boundary and semantic consistency (ADR-0005 D-B1)."""
    if not isinstance(a, dict):
        return ["assessment must be a YAML mapping"]
    p: list[str] = []

    for k in a:
        if k not in _ALLOWED_TOP:
            p.append(f"unknown key {k!r} — assessments declare composition only; "
                     "gates, minimums, and outcome rules are engine-owned (ADR-0005)")

    for f in ("id", "version", "schema", "profile", "competencies"):
        if a.get(f) in (None, "", []):
            p.append(f"missing required field: {f}")

    if a.get("id") and not _ID.match(str(a["id"])):
        p.append("id invalid: lowercase alphanumerics, dot, dash, underscore")
    if a.get("version") and not _SEMVER.match(str(a["version"])):
        p.append("version must be semver x.y.z")
    if a.get("schema") not in (None, SUPPORTED_SCHEMA):
        p.append(f"unsupported schema version {a.get('schema')!r} "
                 f"(this engine supports {SUPPORTED_SCHEMA})")

    rt = a.get("default_risk_tier")
    if rt is not None and rt not in C.RISK_TIERS:
        p.append(f"default_risk_tier must be one of {list(C.RISK_TIERS)}")

    if a.get("profile"):
        try:
            profiles.load(str(a["profile"]))
        except Exception:
            p.append(f"profile {a['profile']!r} not found (orphan profile reference)")

    comps = a.get("competencies")
    if comps is not None:
        if not isinstance(comps, list) or not comps:
            p.append("competencies must be a non-empty list")
        else:
            valid_areas = set(runner.all_area_codes())
            seen: set[str] = set()
            n_mandatory = 0
            for i, comp in enumerate(comps):
                where = f"competency #{i}"
                if not isinstance(comp, dict):
                    p.append(f"{where} must be a mapping")
                    continue
                for k in comp:
                    if k not in _ALLOWED_COMPETENCY:
                        p.append(f"{where}: unknown key {k!r}")
                area = comp.get("area")
                if not area:
                    p.append(f"{where}: missing area")
                elif area not in valid_areas:
                    p.append(f"{where}: unknown competency {area!r}")
                elif area in seen:
                    p.append(f"duplicate competency {area!r}")
                else:
                    seen.add(area)
                req = comp.get("requirement", {"type": "mandatory"})
                if isinstance(req, dict):
                    for k in req:
                        if k not in _ALLOWED_REQUIREMENT:
                            p.append(f"{where}: unknown requirement key {k!r}")
                elif not isinstance(req, str):
                    p.append(f"{where}: requirement must be a mapping like {{type: mandatory}}")
                rtype = _requirement_type(comp)
                if rtype is not None and rtype not in REQUIREMENT_TYPES:
                    p.append(f"{where}: requirement.type must be one of {list(REQUIREMENT_TYPES)}")
                if rtype == "mandatory":
                    n_mandatory += 1
                w = comp.get("weight")
                if w is not None and (isinstance(w, bool) or not isinstance(w, (int, float))
                                      or w <= 0):
                    p.append(f"{where}: weight must be a positive number")
                mcl = comp.get("min_cl")
                if mcl is not None and mcl not in CL_LEVELS:
                    p.append(f"{where}: min_cl must be one of {list(CL_LEVELS)}")
            if not n_mandatory:
                p.append("no mandatory competency — an assessment needs at least one")

    samp = a.get("sampling")
    if samp is not None:
        if not isinstance(samp, dict):
            p.append("sampling must be a mapping")
        else:
            for k in samp:
                if k not in _ALLOWED_SAMPLING:
                    p.append(f"sampling: unknown key {k!r}")
            rep = samp.get("repeats")
            if rep is not None and (isinstance(rep, bool) or not isinstance(rep, int)
                                    or rep < 1):
                p.append("sampling.repeats must be a positive integer")
    return p


def load(name_or_path: str) -> dict:
    """Load an assessment by id (assessments/<id>.yaml) or by path, and validate
    it. Raises AssessmentError if not found or invalid."""
    path = Path(name_or_path)
    if not path.exists():
        path = assessments_dir() / f"{name_or_path}.yaml"
    if not path.exists():
        raise AssessmentError(
            f"assessment {name_or_path!r} not found (looked in {assessments_dir()})")
    a = yaml.safe_load(path.read_text(encoding="utf-8"))
    problems = validate(a)
    if problems:
        raise AssessmentError("invalid assessment:\n  - " + "\n  - ".join(problems))
    return a


def list_assessments() -> list[dict]:
    out = []
    d = assessments_dir()
    if d.exists():
        for path in sorted(d.glob("*.yaml")):
            try:
                a = yaml.safe_load(path.read_text(encoding="utf-8"))
                mand = sum(1 for c in (a.get("competencies") or [])
                           if _requirement_type(c) == "mandatory")
                out.append({"id": a.get("id", path.stem), "version": a.get("version"),
                            "description": a.get("description", ""),
                            "competencies": len(a.get("competencies") or []),
                            "mandatory": mand,
                            "valid": not validate(a)})
            except Exception as e:
                out.append({"id": path.stem, "error": str(e), "valid": False})
    return out


def resolve(a: dict) -> dict:
    """Normalize a validated assessment into what the runner/decision engine
    consume: the ordered competency list with resolved requirement types."""
    comps = []
    for c in a["competencies"]:
        comps.append({"area": c["area"],
                      "requirement": _requirement_type(c) or "mandatory",
                      "weight": c.get("weight"),
                      "min_cl": c.get("min_cl")})
    return {"id": a["id"], "version": a["version"], "schema": a.get("schema", SUPPORTED_SCHEMA),
            "description": a.get("description", ""), "profile": a["profile"],
            "risk_tier": a.get("default_risk_tier", "RT2"),
            "competencies": comps,
            "areas": [c["area"] for c in comps],
            "repeats": (a.get("sampling") or {}).get("repeats")}

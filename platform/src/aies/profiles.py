"""Profile Loader: weighting presets with non-negotiable floors.

A profile expresses organizational emphasis (PLATFORM.md §5.2). Gates
and statistical minimums are NOT expressible in profiles — they are
engine constants (constants.py) and validation here rejects any profile
that tries (PLATFORM.md D3, AIES-AESQS-CS-01-R03).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from . import constants as C

FORBIDDEN_KEYS = ("gates", "minimum_gates", "sample_sizes", "statistical_minimums",
                  "min_sample", "decisional")


class ProfileError(Exception):
    pass


def shipped_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "profiles"


def _load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ProfileError(f"{path} does not contain a mapping")
    return data


def validate(profile: dict) -> dict:
    name = profile.get("name")
    if not name:
        raise ProfileError("profile has no name")
    for key in FORBIDDEN_KEYS:
        if key in profile:
            raise ProfileError(
                f"profile {name!r} attempts to configure {key!r}: gates and "
                "statistical minimums are engine constants and cannot be "
                "expressed in a profile (PLATFORM.md D3)"
            )
    adjustments = profile.get("dimension_weight_adjustments") or {}
    for dim, delta in adjustments.items():
        if dim not in C.DIMENSIONS:
            raise ProfileError(f"profile {name!r}: unknown dimension {dim!r}")
        if not isinstance(delta, (int, float)):
            raise ProfileError(f"profile {name!r}: adjustment for {dim} not numeric")
        if abs(delta) > C.MAX_WEIGHT_ADJUSTMENT + 1e-9:
            raise ProfileError(
                f"profile {name!r}: adjustment for {dim} is {delta:+}; bound "
                f"is ±{C.MAX_WEIGHT_ADJUSTMENT} (AIES-AESQS-CS-01-R03)"
            )
    # Full per-tier validation (sum-to-1, EV3+EV6 floor) happens against
    # the scoped tier in scoring.effective_weights; validate all tiers
    # here so a bad profile fails at load, not mid-run.
    from .scoring import effective_weights
    for rt in C.RISK_TIERS:
        effective_weights(rt, adjustments)
    area_weights = profile.get("area_weights") or {}
    for area, w in area_weights.items():
        if not isinstance(w, (int, float)) or w < 0:
            raise ProfileError(f"profile {name!r}: bad area weight {area}={w!r}")
    return profile


def load(name_or_path: str) -> dict:
    p = Path(name_or_path)
    if p.suffix in (".yaml", ".yml") and p.exists():
        return validate(_load_yaml(p))
    candidate = shipped_dir() / f"{name_or_path}.yaml"
    if candidate.exists():
        return validate(_load_yaml(candidate))
    raise ProfileError(
        f"profile {name_or_path!r} not found (shipped: "
        f"{', '.join(sorted(x.stem for x in shipped_dir().glob('*.yaml')))})"
    )


def list_shipped() -> list[dict]:
    return [validate(_load_yaml(p)) for p in sorted(shipped_dir().glob("*.yaml"))]

"""Multi-phase journeys — chained scenarios across the SDLC (Task #6).

A *journey* carries one piece of work through several SDLC phases: the
response the model gives at each step is threaded into the prompt of the
next, so the platform can test lifecycle *depth* (does the model's
architecture actually follow from the requirements it just wrote?), not
just breadth. This is the AIES-native test — AI across the *complete*
SDLC.

A journey is executed as an ordered sequence of steps; each step is
recorded as an ordinary response record tagged with that step's
competency area, so the existing scoring → rating → aggregation →
report → grant pipeline consumes journeys with no change. The journey
declares one risk tier at which its steps are scored.

Prompt threading: a step prompt MAY contain `{{prior_response}}` (the
immediately preceding step's response) and/or `{{prior}}` (a formatted
transcript of all prior steps). Steps without a placeholder run
independently within the journey.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

from . import constants as C

STEP_REQUIRED = ("id", "area", "prompt", "rubric")
_CA_RE = re.compile(r"^CA-\d\d$")


class JourneyError(Exception):
    pass


def journeys_dir() -> Path:
    from .resources import data_root
    return data_root() / "journeys"


def load_journey(journey_id: str) -> tuple[dict, str]:
    """Load and validate a journey; return (journey, version)."""
    base = journeys_dir()
    matches = [p for p in base.glob("*.yaml")
               if p.stem == journey_id or p.stem.startswith(journey_id + "-")]
    if not matches:
        avail = ", ".join(sorted(p.stem for p in base.glob("*.yaml"))) or "(none)"
        raise JourneyError(f"no journey {journey_id!r} under {base} (available: {avail})")
    path = matches[0]
    journey = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(journey, dict):
        raise JourneyError(f"{path.name} is not a mapping")
    for f in ("id", "title", "risk_tier", "steps"):
        if f not in journey:
            raise JourneyError(f"{path.name}: missing required field {f!r}")
    if journey["risk_tier"] not in C.RISK_TIERS:
        raise JourneyError(f"{path.name}: risk_tier must be one of {C.RISK_TIERS}")
    steps = journey["steps"]
    if not steps:
        raise JourneyError(f"{path.name}: journey has no steps")
    seen = set()
    for i, s in enumerate(steps):
        missing = [f for f in STEP_REQUIRED if f not in s]
        if missing:
            raise JourneyError(f"{path.name} step {i+1}: missing {missing}")
        if not _CA_RE.match(str(s["area"])):
            raise JourneyError(f"{path.name} step {s['id']}: area must be CA-NN")
        if s["id"] in seen:
            raise JourneyError(f"{path.name}: duplicate step id {s['id']!r}")
        seen.add(s["id"])
    version = "journey-sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return journey, version


def list_journeys() -> list[dict]:
    out = []
    for p in sorted(journeys_dir().glob("*.yaml")):
        try:
            j, _ = load_journey(p.stem)
        except JourneyError:
            continue
        out.append({"id": j["id"], "title": j.get("title", ""),
                    "risk_tier": j["risk_tier"],
                    "steps": [{"id": s["id"], "area": s["area"],
                               "phase": s.get("phase", "")} for s in j["steps"]]})
    return out


def render_step_prompt(step: dict, prior_steps: list[dict]) -> str:
    """Substitute prior-step context into a step's prompt template."""
    prompt = step["prompt"]
    prev_response = prior_steps[-1]["response"] if prior_steps else ""
    transcript = "\n\n".join(
        f"### {s.get('phase') or s['area']} ({s['id']})\n{s['response']}"
        for s in prior_steps)
    prompt = prompt.replace("{{prior_response}}", prev_response)
    prompt = prompt.replace("{{prior}}", transcript)
    return prompt

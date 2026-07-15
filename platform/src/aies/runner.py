"""Test Runner (pipeline stage 4): execute scenario suites, capture everything.

Every executed run is recorded and none may be discarded
(AIES-AESQS-CS-01-R12). Records are append-only JSON files.
"""

from __future__ import annotations

import datetime
import hashlib
from pathlib import Path

import yaml

from . import workspace
from .adapters.base import GenerationRequest, RuntimeAdapter

SCENARIO_REQUIRED = ("id", "area", "risk_tier", "prompt", "expected_qualities", "rubric")


class SuiteError(Exception):
    pass


def competencies_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "competencies"


def _suite_version(area_dir: Path) -> str:
    """Suite version = digest of all scenario content, so any content
    change yields a new version and results are only comparable on
    identical suite versions (PLATFORM.md §9)."""
    h = hashlib.sha256()
    for p in sorted((area_dir / "scenarios").glob("*.yaml")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return "suite-sha256:" + h.hexdigest()[:16]


def load_area(area: str) -> tuple[dict, list[dict], str]:
    """Load an area's definition and scenarios. `area` may be the CA code
    (CA-05) or the full directory name."""
    base = competencies_dir()
    matches = [d for d in base.iterdir() if d.is_dir()
               and (d.name == area or d.name.startswith(area + "-"))]
    if not matches:
        raise SuiteError(
            f"no competency directory for {area!r} under {base} "
            f"(available: {', '.join(sorted(d.name for d in base.iterdir() if d.is_dir()))})"
        )
    area_dir = matches[0]
    definition = yaml.safe_load((area_dir / "definition.yaml").read_text(encoding="utf-8"))
    scenarios = []
    for p in sorted((area_dir / "scenarios").glob("*.yaml")):
        sc = yaml.safe_load(p.read_text(encoding="utf-8"))
        missing = [f for f in SCENARIO_REQUIRED if f not in sc]
        if missing:
            raise SuiteError(f"{p.name}: missing fields {missing}")
        scenarios.append(sc)
    if not scenarios:
        raise SuiteError(f"{area_dir.name} has no scenarios")
    return definition, scenarios, _suite_version(area_dir)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _build_record(run_id, model_entry, adapter, sc, r, suite_version,
                  environment_fp, response, parameters) -> dict:
    return {
        "run_id": f"{run_id}-{sc['id']}-r{r}",
        "suite_version": suite_version,
        "scenario_id": sc["id"],
        "area": sc["area"],
        "risk_tier": sc["risk_tier"],
        "repeat": r,
        "model": {
            "registry_id": model_entry["id"],
            "checksum": (model_entry.get("provenance") or {}).get("checksum", "unknown"),
        },
        "environment_fingerprint": environment_fp,
        "request": {
            "prompt_hash": "sha256:" + hashlib.sha256(sc["prompt"].encode()).hexdigest(),
            "parameters": parameters or {},
        },
        "raw_response": response.text,
        "usage": response.usage,
        "adapter": {"id": adapter.adapter_id, "version": adapter.adapter_version},
        "scores": None,          # filled by rating records, never in place
        "recorded_at": _now(),
    }


def execute_journey(
    run_id: str,
    model_entry: dict,
    adapter: RuntimeAdapter,
    journey: dict,
    journey_version: str,
    environment_fp: dict,
    repeats: int | None = None,
    parameters: dict | None = None,
) -> list[Path]:
    """Execute a journey (journeys.py): steps run in order per repeat, each
    step's response threaded into the next step's prompt. Each step is
    written as a normal response record tagged with the step's competency
    area and the journey's risk tier, so downstream scoring is unchanged.

    Repeats run sequentially (a step needs the prior step's actual output);
    journeys are about lifecycle depth, not sample volume.
    """
    from .journeys import render_step_prompt

    rdir = workspace.run_dir(run_id) / "responses"
    risk_tier = journey["risk_tier"]
    n_repeats = repeats or 1
    written: list[Path] = []
    for r in range(1, n_repeats + 1):
        prior: list[dict] = []
        for step in journey["steps"]:
            prompt = render_step_prompt(step, prior)
            response = adapter.generate(GenerationRequest(
                prompt=prompt, parameters=parameters or {}))
            pseudo = {"id": step["id"], "area": step["area"],
                      "risk_tier": risk_tier, "prompt": prompt}
            record = _build_record(run_id, model_entry, adapter, pseudo, r,
                                   journey_version, environment_fp, response, parameters)
            record["journey"] = {"id": journey["id"], "step": step["id"],
                                 "phase": step.get("phase", ""),
                                 "step_risk_tier": step.get("risk_tier", risk_tier)}
            path = rdir / f"{step['id']}-r{r}.json"
            workspace.write_json(path, record)
            written.append(path)
            prior.append({"id": step["id"], "area": step["area"],
                          "phase": step.get("phase", ""), "response": response.text})
    return written


def execute_suite(
    run_id: str,
    model_entry: dict,
    adapter: RuntimeAdapter,
    scenarios: list[dict],
    suite_version: str,
    environment_fp: dict,
    repeats: int | None = None,
    parameters: dict | None = None,
    workers: int = 1,
) -> list[Path]:
    """Execute scenarios (with per-scenario repeats) and append response
    records. Returns the paths written, in deterministic scenario/repeat
    order regardless of `workers`.

    Parallelism (workers > 1) only changes how inference calls are
    scheduled; records are written by the calling thread in canonical
    order, so parallel and serial runs produce byte-identical record
    sets (PLATFORM.md M3 exit criterion). Adapters used with workers > 1
    MUST be safe for concurrent generate() calls; the built-in adapters
    are (they hold no per-call state after load()).
    """
    from concurrent.futures import ThreadPoolExecutor

    rdir = workspace.run_dir(run_id) / "responses"
    tasks = []  # (order_index, scenario, repeat)
    for sc in scenarios:
        n_repeats = repeats or int(sc.get("repeats_min", 1))
        for r in range(1, n_repeats + 1):
            tasks.append((sc, r))

    def _generate(task):
        sc, r = task
        request = GenerationRequest(prompt=sc["prompt"], parameters=parameters or {})
        return sc, r, adapter.generate(request)

    if workers and workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_generate, tasks))
    else:
        results = [_generate(t) for t in tasks]

    # Canonical order: scenario appearance order, then repeat.
    results.sort(key=lambda x: ([s["id"] for s in scenarios].index(x[0]["id"]), x[1]))
    written: list[Path] = []
    for sc, r, response in results:
        record = _build_record(run_id, model_entry, adapter, sc, r, suite_version,
                                environment_fp, response, parameters)
        path = rdir / f"{sc['id']}-r{r}.json"
        workspace.write_json(path, record)
        written.append(path)
    return written

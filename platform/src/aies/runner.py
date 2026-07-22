"""Test Runner (pipeline stage 4): execute scenario suites, capture everything.

Every executed run is recorded and none may be discarded
(AIES-AESQS-CS-01-R12). Records are append-only JSON files.
"""

from __future__ import annotations

import datetime
import hashlib
import copy
from pathlib import Path

import yaml

from . import workspace
from .adapters.base import GenerationRequest, RuntimeAdapter

SCENARIO_REQUIRED = ("id", "area", "risk_tier", "prompt", "expected_qualities", "rubric")


class SuiteError(Exception):
    pass


def competencies_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "competencies"


def all_area_codes() -> list[str]:
    """Every competency area code shipped under competencies/ (CA-01…CA-12),
    sorted. Used by `qualify --all-areas` to profile a deployment across the
    whole SDLC."""
    base = competencies_dir()
    codes = {"-".join(d.name.split("-")[:2])
             for d in base.iterdir() if d.is_dir() and d.name.startswith("CA-")}
    return sorted(codes)


def _suite_version(area_dir: Path) -> str:
    """Suite version = digest of all scenario content, so any content
    change yields a new version and results are only comparable on
    identical suite versions (PLATFORM.md §9)."""
    h = hashlib.sha256()
    for p in sorted((area_dir / "scenarios").glob("*.yaml")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return "suite-sha256:" + h.hexdigest()[:16]


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge scenario-pack defaults without sharing mutable values."""
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load_scenario_documents(path: Path) -> list[dict]:
    """Load one scenario or expand a declarative scenario pack."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and data.get("kind") == "aies-scenario-pack-v1":
        defaults = data.get("defaults")
        entries = data.get("scenarios")
        if not isinstance(defaults, dict) or not isinstance(entries, list) or not entries:
            raise SuiteError(f"{path.name}: scenario pack needs mapping defaults and scenarios")
        out = []
        for index, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                raise SuiteError(f"{path.name}: scenario pack item {index} must be a mapping")
            out.append(_deep_merge(defaults, entry))
        return out
    if not isinstance(data, dict):
        raise SuiteError(f"{path.name}: scenario must be a mapping")
    return [data]


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
        for sc in load_scenario_documents(p):
            missing = [f for f in SCENARIO_REQUIRED if f not in sc]
            if missing:
                raise SuiteError(f"{p.name}/{sc.get('id', '?')}: missing fields {missing}")
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
            "prompt": sc["prompt"],
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
    skip_existing: bool = False,
) -> list[Path]:
    """Execute each scenario once, or with an explicit repeat override, and append response
    records. Returns the paths written, in deterministic scenario/repeat
    order regardless of `workers`.

    With `skip_existing`, a (scenario, repeat) whose response record already
    exists on disk is not re-run — this is how a partially-collected run is
    resumed to fill only the missing items (engine.resume_collection).

    Each successful response is written as soon as it completes, so a
    failure partway through a run does not discard the responses already
    collected — they stay on disk for inspection. The resulting record
    set (filenames + contents, modulo per-record timestamps) is
    independent of `workers`, so parallel and serial runs are equivalent
    (PLATFORM.md M3 exit criterion). Adapters used with workers > 1 MUST
    be safe for concurrent generate() calls; the built-in adapters are
    (they hold no per-call state after load()).

    If any inference call fails, the successful responses are kept and a
    single SuiteError is raised summarising what failed — never a bare,
    context-free error, and never silent data loss.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    rdir = workspace.run_dir(run_id) / "responses"
    tasks = []  # (scenario, repeat)
    for sc in scenarios:
        n_repeats = repeats or 1
        for r in range(1, n_repeats + 1):
            if skip_existing and (rdir / f"{sc['id']}-r{r}.json").exists():
                continue
            tasks.append((sc, r))
    if not tasks:
        return []

    def _run_and_write(task) -> Path:
        sc, r = task
        request = GenerationRequest(prompt=sc["prompt"], parameters=parameters or {})
        response = adapter.generate(request)
        record = _build_record(run_id, model_entry, adapter, sc, r, suite_version,
                               environment_fp, response, parameters)
        path = rdir / f"{sc['id']}-r{r}.json"
        workspace.write_json(path, record)
        return path

    written: list[Path] = []
    failures: list[tuple[str, str]] = []  # (scenario-repeat, error)

    if workers and workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = {pool.submit(_run_and_write, t): t for t in tasks}
            for fut in as_completed(futs):
                sc, r = futs[fut]
                try:
                    written.append(fut.result())
                except Exception as e:  # noqa: BLE001 — surfaced below, work preserved
                    failures.append((f"{sc['id']}-r{r}", str(e)))
    else:
        for task in tasks:
            sc, r = task
            try:
                written.append(_run_and_write(task))
            except Exception as e:  # noqa: BLE001
                failures.append((f"{sc['id']}-r{r}", str(e)))

    written.sort()  # deterministic return order; the record SET is worker-independent

    if failures:
        sample = "; ".join(f"{name}: {err}" for name, err in failures[:2])
        if not written:
            raise SuiteError(
                f"all {len(failures)} inference call(s) failed. First: {sample}")
        raise SuiteError(
            f"{len(failures)} of {len(tasks)} inference call(s) failed; the "
            f"{len(written)} successful responses were saved to {rdir}. "
            f"First failure — {sample}. Fix the endpoint and re-run "
            f"(or reduce --parallel), then re-score.")
    return written

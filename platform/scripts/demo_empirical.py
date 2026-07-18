"""Mock empirical-calibration demo — see the Phase-2 harness produce REAL
discrimination output, fully offline, on a SYNTHETIC panel.

The mock runtime produces uniform responses, so real discrimination cannot arise
from it. To demonstrate the harness MECHANICS with visible numbers, this injects
three ability levels as scores (strong=4, mid=3, weak=2) across a small panel,
and makes the "weak" model deliberately ACE one scenario so you see BOTH a
discriminating verdict and a flagged (non-discriminating) one.

This is NOT real capability evidence: the scores are synthetic and no scenario is
promoted to empirically_calibrated. A real pilot runs `aies qualify` against real
models of known-varying ability (CALIBRATION.md Phase 2), then feeds the scored
runs to `aies suites empirical --runs`.

    make demo-empirical      (or: python scripts/demo_empirical.py)
"""

import json
import os
import pathlib
import sys
import tempfile

os.environ.setdefault("AIES_WORKSPACE", tempfile.mkdtemp())
os.environ.setdefault("AIES_ENV_FILE", os.devnull)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

import yaml  # noqa: E402

from aies import empirical, engine, rating, registry, workspace  # noqa: E402

WS = pathlib.Path(os.environ["AIES_WORKSPACE"])


def make_run(dep: str, level: int, ace_first: bool = False) -> str:
    e = {"id": dep, "family": "demo", "runtime": "mock", "model": dep,
         "context_window": 8192,
         "provenance": {"source": "synthetic", "checksum": "sha256:" + "0" * 64}}
    p = WS / f"{dep}.yaml"
    p.write_text(yaml.safe_dump(e), encoding="utf-8")
    registry.add(p)
    m = engine.start_qualification(dep, "coder", "RT2", ["CA-05"], repeats=3)
    run = m["run_id"]
    sheet = json.loads((workspace.run_dir(run) / "scoresheet.json").read_text())
    sheet["rater"] = {"name": "synthetic", "kind": "human"}
    for i, it in enumerate(sheet["items"]):
        lvl = 4 if (ace_first and i == 0) else level     # weak aces the first scenario
        it["scores"] = {d: lvl for d in ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6")}
        if lvl <= 2:
            it["findings"] = [{"dimension": "EV1", "score": lvl, "finding": "synthetic weak"}]
    rating.ingest_scores(run, sheet)
    return run


def main() -> None:
    print("=" * 70)
    print(" MOCK empirical-calibration demo  (SYNTHETIC panel — mechanics only)")
    print("=" * 70)
    runs = [
        {"run_id": make_run("strong-ref", 4), "ability": 3},
        {"run_id": make_run("mid-ref", 3), "ability": 2},
        {"run_id": make_run("weak-ref", 2, ace_first=True), "ability": 1},
    ]
    panel = empirical.assemble_panel_from_runs(runs)
    report = empirical.analyze_panel(panel, panel_id="mock-demo-synthetic")
    print(empirical.render(report))
    print()
    print("The weak model was made to ACE the first scenario, so it is flagged")
    print("(low-discrimination) while the rest discriminate — exactly what the")
    print("harness is for. SYNTHETIC scores: no scenario is empirically_calibrated;")
    print("a real pilot needs models of known-varying ability (CALIBRATION.md Phase 2).")


if __name__ == "__main__":
    main()

"""Export a run's evidence to a generic eval-log JSON (§7 — ecosystem bridge).

The counterpart of `aies import`: writes each response's prompt, answer, and
scores to a machine-readable log other eval tooling can consume — and that
`aies import` can round-trip. Each `items[]` entry carries the same
`{scenario_id, repeat, scores{EV1..EV6}, findings}` shape `import` accepts (so an
exported, scored run can be re-imported into another run), plus `prompt`,
`response`, and the full per-rater `ratings` for external consumers, which
`import` ignores.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import transcript, workspace


def export_run(run_id: str) -> dict:
    manifest, responses, ratings_by_resp = transcript._collect(run_id)
    items = []
    for rec in responses:
        rr = f"{rec['scenario_id']}-r{rec['repeat']}.json"
        rlist = ratings_by_resp.get(rr, [])
        primary = rlist[0] if rlist else None
        items.append({
            "scenario_id": rec["scenario_id"],
            "repeat": rec["repeat"],
            "area": rec.get("area"),
            "prompt": (rec.get("request") or {}).get("prompt", ""),
            "response": rec.get("raw_response", ""),
            "scores": primary["scores"] if primary else None,   # import-compatible
            "findings": (primary.get("findings", []) if primary else []),
            "ratings": [{"rater": r["provenance"]["rater"],
                         "rater_kind": r["provenance"]["rater_kind"],
                         "scores": r["scores"]} for r in rlist],
        })
    return {
        "source": f"aies:{run_id}",
        "run": {
            "run_id": run_id,
            "model": manifest["model"]["registry_id"],
            "profile": manifest.get("profile"),
            "risk_tier": manifest.get("risk_tier"),
            "suite_versions": {a["area"]: a["suite_version"]
                               for a in manifest.get("areas", [])},
        },
        "items": items,
    }


def render_json(run_id: str) -> str:
    return json.dumps(export_run(run_id), indent=2)


def write_export(run_id: str, path: str | None = None) -> str:
    dest = Path(path) if path else workspace.run_dir(run_id) / "eval-log.json"
    dest.write_text(render_json(run_id), encoding="utf-8")
    return str(dest)

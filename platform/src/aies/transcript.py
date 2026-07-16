"""Run transcript — the whole run in one readable view.

Reviewing a run by opening each response JSON and cross-referencing the
prompt, the answer, and the score across directories is unworkable. This
renders one document: per scenario (and repeat), the task, the model's
answer, its expected qualities, and the scores/findings — so a human can
read or spot-check a run top to bottom without spelunking.

It joins three things the platform already stores: the response records
(prompt + answer), the rating records (scores + findings), and the
scenario definitions (expected qualities / failure conditions).
"""

from __future__ import annotations

import json

from . import rating, runner, workspace


def _scenario_meta() -> dict:
    """Best-effort map scenario_id -> {expected_qualities, failure_conditions}
    across all competency suites (journey step ids simply won't match)."""
    meta: dict[str, dict] = {}
    base = runner.competencies_dir()
    if not base.exists():
        return meta
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        for p in sorted((d / "scenarios").glob("*.yaml")):
            try:
                import yaml
                sc = yaml.safe_load(p.read_text(encoding="utf-8"))
                meta[sc["id"]] = {
                    "expected_qualities": sc.get("expected_qualities", []),
                    "failure_conditions": sc.get("failure_conditions", []),
                }
            except Exception:
                continue
    return meta


def _collect(run_id: str):
    rdir = workspace.run_dir(run_id)
    manifest = workspace.read_json(rdir / "manifest.json")
    responses = [workspace.read_json(p)
                 for p in sorted((rdir / "responses").glob("*.json"))]
    ratings_by_resp: dict[str, list] = {}
    for r in rating.collect_ratings(run_id):
        ratings_by_resp.setdefault(r["rates_response"], []).append(r)
    return manifest, responses, ratings_by_resp


def render_markdown(run_id: str, area: str | None = None) -> str:
    manifest, responses, ratings_by_resp = _collect(run_id)
    meta = _scenario_meta()
    out: list[str] = []
    a = out.append
    a(f"# Run Transcript — {run_id}")
    a("")
    a(f"**Model:** `{manifest['model']['registry_id']}`  ·  "
      f"**Profile:** {manifest.get('profile','?')}  ·  "
      f"**Risk tier:** {manifest.get('risk_tier','?')}  ·  "
      f"**Responses:** {len(responses)}")
    a("")
    a("Each item below is one scenario response: the task, the model's answer, "
      "and — if scored — its EV1–EV6 scores and findings.")
    a("")

    for rec in responses:
        if area and rec.get("area") != area:
            continue
        rfile = f"{rec['scenario_id']}-r{rec['repeat']}.json"
        j = rec.get("journey")
        head = (f"## {rec['scenario_id']}  ·  {rec.get('area','?')}  ·  "
                f"{rec.get('risk_tier','?')}  ·  repeat {rec['repeat']}")
        if j:
            head += f"  ·  journey {j.get('id')} [{j.get('phase','')}]"
        a(head)
        a("")

        rr = ratings_by_resp.get(rfile, [])
        if rr:
            for one in rr:
                sc = one["scores"]
                line = " · ".join(f"{d} **{sc[d]}**" for d in
                                  ("EV1", "EV2", "EV3", "EV4", "EV5", "EV6"))
                a(f"**Scores** ({one['provenance']['rater']}, "
                  f"{one['provenance']['rater_kind']}): {line}")
                for f in one.get("findings", []):
                    a(f"- finding — {f.get('dimension','')} ({f.get('score','')}): "
                      f"{f.get('finding','')}")
            a("")
        else:
            a("_not yet scored_")
            a("")

        prompt = (rec.get("request") or {}).get("prompt")
        a("<details><summary>Task</summary>")
        a("")
        a("```")
        a((prompt or "(prompt text not stored in this record)").strip())
        a("```")
        m = meta.get(rec["scenario_id"])
        if m and m["expected_qualities"]:
            a("")
            a("*Expected qualities:* " + "; ".join(m["expected_qualities"]))
        a("</details>")
        a("")
        a("**Model response:**")
        a("")
        a("```")
        a((rec.get("raw_response") or "").strip())
        a("```")
        a("")
        a("---")
        a("")
    return "\n".join(out)


def render_json(run_id: str, area: str | None = None) -> str:
    manifest, responses, ratings_by_resp = _collect(run_id)
    items = []
    for rec in responses:
        if area and rec.get("area") != area:
            continue
        rfile = f"{rec['scenario_id']}-r{rec['repeat']}.json"
        items.append({
            "scenario_id": rec["scenario_id"], "area": rec.get("area"),
            "risk_tier": rec.get("risk_tier"), "repeat": rec["repeat"],
            "journey": rec.get("journey"),
            "prompt": (rec.get("request") or {}).get("prompt"),
            "response": rec.get("raw_response"),
            "ratings": ratings_by_resp.get(rfile, []),
        })
    return json.dumps({"run_id": run_id, "model": manifest["model"]["registry_id"],
                       "items": items}, indent=2)


def write_transcript(run_id: str) -> str:
    path = workspace.run_dir(run_id) / "transcript.md"
    path.write_text(render_markdown(run_id), encoding="utf-8")
    return str(path)

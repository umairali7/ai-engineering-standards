"""Judge usage view — who has judged, across which runs, how reliably.

A "judge" is not a distinct object: it is an ordinary deployment passed to
`aies qualify --judge`. When a judge scores a run, its scores are recorded as
`model`-kind ratings whose rater name is `model:<deployment>` (rating.py). This
module derives a judge's track record from those existing records — nothing new
is stored. Two views:

- `registered_judges()` — the judge *pool*: registered deployments that declare
                      `roles: [judge]` in their manifest, each annotated with its
                      track record (has it judged yet, parse rate). Forward-looking
                      ("what can I use as a judge"), vs the two views below which
                      are backward-looking ("what has judged").
- `judge_usage()`   — one row per judge deployment, aggregated across all runs
                      it scored (runs judged, responses scored, parse-failure
                      count, self-judged runs, last used, still-registered).
- `judge_history()` — one row per (run, judge) pairing, newest first, with the
                      per-run parse coverage and whether the run was aggregated.

Parse coverage matters because a judge that frequently emits unparseable scores
is contributing thin evidence (model_review skips unparseable replies rather
than fabricating them), and that only shows up across many runs.
"""

from __future__ import annotations

from . import compare, rating, workspace


def _judge_of(rater_name: str) -> str:
    """A judge rating's provenance rater is `model:<deployment>`."""
    prefix = "model:"
    return rater_name[len(prefix):] if rater_name.startswith(prefix) else rater_name


def judge_history(judge: str | None = None) -> list[dict]:
    """One row per (run, judge) pairing where a judge scored the run, newest
    first. Optionally filtered to a single judge deployment id."""
    rows: list[dict] = []
    for r in compare.list_runs():
        run_id = r["run_id"]
        model_ratings = [x for x in rating.collect_ratings(run_id)
                         if x["provenance"].get("rater_kind") == "model"]
        if not model_ratings:
            continue
        n_responses = len(list((workspace.run_dir(run_id) / "responses").glob("*.json")))
        by_judge: dict[str, dict] = {}
        for x in model_ratings:
            j = _judge_of(x["provenance"]["rater"])
            g = by_judge.setdefault(j, {"scored": 0, "last": None})
            g["scored"] += 1
            ts = x["provenance"].get("timestamp")
            if ts and (g["last"] is None or ts > g["last"]):
                g["last"] = ts
        for j, g in by_judge.items():
            rows.append({
                "run_id": run_id,
                "subject": r["model"],
                "judge": j,
                "self_judged": j == r["model"],
                "profile": r["profile"],
                "risk_tier": r["risk_tier"],
                "areas": r["areas"],
                "scored": g["scored"],
                "responses": n_responses,
                "unparseable": max(0, n_responses - g["scored"]),
                "aggregated": r["aggregated"],
                "created_at": r["created_at"],
                "last_scored_at": g["last"],
            })
    if judge:
        rows = [x for x in rows if x["judge"] == judge]
    return sorted(rows, key=lambda x: (x["created_at"] or ""), reverse=True)


def judge_usage() -> list[dict]:
    """Aggregate per judge deployment across every run it has scored,
    newest-used first."""
    from . import registry
    agg: dict[str, dict] = {}
    for x in judge_history():
        a = agg.setdefault(x["judge"], {
            "judge": x["judge"], "runs_judged": 0, "responses_scored": 0,
            "unparseable": 0, "self_judged_runs": 0, "last_used": None,
        })
        a["runs_judged"] += 1
        a["responses_scored"] += x["scored"]
        a["unparseable"] += x["unparseable"]
        if x["self_judged"]:
            a["self_judged_runs"] += 1
        lu = x["last_scored_at"] or x["created_at"]
        if lu and (a["last_used"] is None or lu > a["last_used"]):
            a["last_used"] = lu
    for a in agg.values():
        total = a["responses_scored"] + a["unparseable"]
        a["parse_rate"] = round(a["responses_scored"] / total, 3) if total else None
        try:
            registry.get(a["judge"])
            a["registered"] = True
        except Exception:
            a["registered"] = False   # missing or retired — can no longer be used
    return sorted(agg.values(), key=lambda a: (a["last_used"] or ""), reverse=True)


def registered_judges() -> list[dict]:
    """The judge pool: registered (non-retired) deployments whose manifest
    declares `roles: [judge]`, each annotated with track record. Answers
    "how many judges do we have registered, and which have been used yet"."""
    from . import registry
    used = {u["judge"]: u for u in judge_usage()}
    out = []
    for e in registry.list_entries():
        if "judge" not in (e.get("roles") or []):
            continue
        u = used.get(e["id"])
        out.append({
            "judge": e["id"],
            "model": e.get("model") or e.get("family"),
            "runtime": e.get("runtime"),
            "endpoint": (e.get("runtime_config") or {}).get("base_url"),
            "runs_judged": u["runs_judged"] if u else 0,
            "responses_scored": u["responses_scored"] if u else 0,
            "parse_rate": u["parse_rate"] if u else None,
            "last_used": u["last_used"] if u else None,
        })
    return sorted(out, key=lambda a: a["judge"])

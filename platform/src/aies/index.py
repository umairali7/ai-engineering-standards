"""Result index (M3, PLATFORM.md §9): a queryable cache over the
append-only records.

The plain-file records under runs/ remain the single source of truth
(PLATFORM.md §5). This SQLite index is a derived, disposable convenience
for fast history and comparison at scale; it can be deleted and rebuilt
from the files at any time and never holds anything the files do not.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from . import workspace


def _db_path() -> Path:
    return workspace.ensure() / "index.sqlite"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, model TEXT, profile TEXT, risk_tier TEXT,
  status TEXT, created_at TEXT, aggregated INTEGER
);
CREATE TABLE IF NOT EXISTS area_scores (
  run_id TEXT, area TEXT, suite_version TEXT, n_scored INTEGER,
  decisional INTEGER, gates_passed INTEGER, aggregate_A REAL, cl TEXT,
  PRIMARY KEY (run_id, area)
);
"""


def rebuild() -> dict:
    """Drop and rebuild the index from the run files. Idempotent."""
    db = _db_path()
    if db.exists():
        db.unlink()
    conn = _connect()
    conn.executescript(SCHEMA)
    n_runs = n_areas = 0
    for d in sorted(workspace.runs_dir().iterdir()):
        manifest = d / "manifest.json"
        if not d.is_dir() or not manifest.exists():
            continue
        m = workspace.read_json(manifest)
        pkg_path = d / "evidence-package.json"
        aggregated = pkg_path.exists()
        conn.execute(
            "INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)",
            (m["run_id"], m["model"]["registry_id"], m["profile"], m["risk_tier"],
             m.get("status", "unknown"), m.get("created_at"), int(aggregated)),
        )
        n_runs += 1
        if aggregated:
            pkg = workspace.read_json(pkg_path)
            for area, a in pkg["areas"].items():
                conn.execute(
                    "INSERT OR REPLACE INTO area_scores VALUES (?,?,?,?,?,?,?,?)",
                    (pkg["run_id"], area, pkg["suite_versions"].get(area),
                     a["n_scored"], int(a["decisional"]), int(a["gates_passed"]),
                     a["aggregate_A"], a["cl"]),
                )
                n_areas += 1
    conn.commit()
    conn.close()
    return {"runs_indexed": n_runs, "area_scores_indexed": n_areas,
            "index": str(db)}


def query_runs(model: str | None = None) -> list[dict]:
    if not _db_path().exists():
        rebuild()
    conn = _connect()
    sql = "SELECT * FROM runs"
    args: tuple = ()
    if model:
        sql += " WHERE model = ?"
        args = (model,)
    sql += " ORDER BY created_at DESC"
    rows = [dict(r) for r in conn.execute(sql, args)]
    conn.close()
    return rows


def area_history(area: str, model: str | None = None) -> list[dict]:
    """Score history for one competency area across runs (newest first)."""
    if not _db_path().exists():
        rebuild()
    conn = _connect()
    sql = ("SELECT r.created_at, r.model, r.profile, r.risk_tier, s.* "
           "FROM area_scores s JOIN runs r ON r.run_id = s.run_id "
           "WHERE s.area = ?")
    args: list = [area]
    if model:
        sql += " AND r.model = ?"
        args.append(model)
    sql += " ORDER BY r.created_at DESC"
    rows = [dict(r) for r in conn.execute(sql, tuple(args))]
    conn.close()
    return rows

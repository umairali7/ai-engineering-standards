"""Standalone, bounded deployment guidance derived from ECM evidence."""
from __future__ import annotations

from pathlib import Path

from . import constants as C, ecm, workspace


def render_markdown(ref: str) -> str:
    matrix = ecm.engineering_capability_matrix(ref)
    summary = ecm.capability_summary(matrix)
    lines = ["# AIES Deployment Guidance", "",
             "> **INFORMATIONAL — NOT A QUALIFICATION, GRANT, OR DEPLOYMENT AUTHORIZATION.**", "",
             f"Subject: `{matrix['subject']}`  ", f"Run: `{matrix['run_id']}`  ",
             f"Scope: {C.risk_tier_label(matrix['risk_tier'])} · {matrix['profile']} profile", "",
             "## Use", ""]
    if summary["task_demonstrated"]:
        lines += [f"- `{x['task']}` — only within its assessed scope and approved autonomy envelope."
                  for x in summary["task_demonstrated"]]
    else:
        lines += ["- None. No task has decisional evidence in this run."]
    lines += ["", "## Use with human review", ""]
    lines += ([f"- `{x['task']}` — observed evidence only; review every output."
               for x in summary["task_observed"]] or ["- None."])
    lines += ["", "## Avoid / collect evidence first", ""]
    lines += ([f"- `{x['task']}` — not assessed in this run." for x in summary["task_not_assessed"]]
              or ["- No unassessed mapped task."])
    lines += ["", "## Constraints", "",
              "- This artifact cannot grant authority or override qualification gates, risk-tier caps, or human accountability.",
              "- High observed performance with insufficient evidence confidence is not a recommendation.", ""]
    return "\n".join(lines)


def write(ref: str) -> Path:
    matrix = ecm.engineering_capability_matrix(ref)
    path = workspace.run_dir(matrix["run_id"]) / "deployment-guidance.md"
    path.write_text(render_markdown(matrix["run_id"]), encoding="utf-8")
    return path

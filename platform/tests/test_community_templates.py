from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / ".github" / "ISSUE_TEMPLATE"
FORMS = (
    "first_run.yml",
    "report_comprehension.yml",
    "case_study.yml",
    "instrument_review.yml",
    "adapter_proposal.yml",
)


def test_adoption_issue_forms_are_valid_safe_and_distinct():
    for name in FORMS:
        data = yaml.safe_load((TEMPLATES / name).read_text(encoding="utf-8"))
        assert data["name"] and data["description"] and data["title"]
        assert data["body"]
        ids = [item.get("id") for item in data["body"] if item.get("id")]
        assert len(ids) == len(set(ids)), name
        text = (TEMPLATES / name).read_text(encoding="utf-8").casefold()
        assert any(boundary in text for boundary in (
            "do not include", "do not attach", "submit no confidential",
            "independence", "never include",
        )), name

    config = (TEMPLATES / "config.yml").read_text(encoding="utf-8")
    assert "OWNER/aies" not in config
    assert "security/advisories/new" in config


def test_canonical_source_installs_are_isolated_and_pep668_safe():
    documents = (
        ROOT / "README.md",
        ROOT / "QUICKSTART.md",
        ROOT / "GETTING_STARTED.md",
        ROOT / "platform" / "README.md",
        ROOT / "platform" / "GUIDE.md",
    )
    for path in documents:
        text = path.read_text(encoding="utf-8")
        first_editable_install = text.find("pip install -e")
        assert first_editable_install >= 0, path
        assert text.find("-m venv") < first_editable_install, path
        assert "pip install --break-system-packages" not in text
        assert "pipx" in text and "uv tool" in text

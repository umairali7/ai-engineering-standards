"""Cross-machine run transfer is bounded, verified, and non-overwriting."""

import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def transfer_ws(tmp_path, monkeypatch):
    monkeypatch.setenv("AIES_WORKSPACE", str(tmp_path / "ws"))
    return tmp_path


def _package(root: Path, run_id: str = "run-portable") -> Path:
    package = root / "archive-wrapper" / run_id
    (package / "responses").mkdir(parents=True)
    (package / "manifest.json").write_text(json.dumps({
        "run_id": run_id,
        "status": "collected",
        "created_at": "2026-07-23T00:00:00+00:00",
        "model": {"registry_id": "portable-model"},
    }), encoding="utf-8")
    (package / "responses" / "one.json").write_bytes(
        b'{"response":"byte-preserved"}\n')
    (package / ".DS_Store").write_bytes(b"disposable")
    return package


def test_directory_import_dry_run_then_verified_idempotent_import(
        transfer_ws):
    from aies import api, run_transfer, workspace

    package = _package(transfer_ws / "source")
    plan = run_transfer.import_package(package.parent, dry_run=True)
    destination = workspace.runs_dir() / plan["run_id"]

    assert plan["kind"] == "aies-run-import-plan"
    assert plan["would_write"] is True
    assert not destination.exists()
    assert plan["file_count"] == 2
    assert plan["excluded"][0]["path"] == ".DS_Store"

    receipt = run_transfer.import_package(package.parent)
    assert receipt["kind"] == "aies-run-import-receipt"
    assert receipt["status"] == "imported"
    assert receipt["verified_after_import"] is True
    assert (destination / "responses" / "one.json").read_bytes() == (
        b'{"response":"byte-preserved"}\n')
    assert not (destination / ".DS_Store").exists()

    repeated = run_transfer.import_package(package.parent)
    assert repeated == receipt
    assert len(run_transfer.list_receipts()) == 1
    status, served = api.route(f"/run-imports/{receipt['receipt_id']}")
    assert status == 200 and served == receipt


def test_zip_import_accepts_one_wrapped_run_and_rejects_traversal(
        transfer_ws):
    from aies import run_transfer, workspace

    package = _package(transfer_ws / "zip-source", "run-zipped")
    archive = transfer_ws / "run-zipped.zip"
    with zipfile.ZipFile(archive, "w") as output:
        for path in package.parent.rglob("*"):
            if path.is_file():
                output.write(path, path.relative_to(package.parent.parent))

    receipt = run_transfer.import_package(archive)
    assert receipt["source"]["kind"] == "zip"
    assert receipt["source"]["source_digest"].startswith("sha256:")
    assert (workspace.run_dir("run-zipped") / "manifest.json").is_file()

    unsafe = transfer_ws / "unsafe.zip"
    with zipfile.ZipFile(unsafe, "w") as output:
        output.writestr("../escape.json", "{}")
    with pytest.raises(run_transfer.RunImportError, match="unsafe"):
        run_transfer.inspect(unsafe)
    assert not (transfer_ws / "escape.json").exists()


def test_existing_different_run_is_never_overwritten(transfer_ws):
    from aies import run_transfer, workspace

    package = _package(transfer_ws / "source", "run-conflict")
    destination = workspace.runs_dir() / "run-conflict"
    destination.mkdir(parents=True)
    (destination / "manifest.json").write_text(
        '{"run_id":"run-conflict","different":true}', encoding="utf-8")

    with pytest.raises(run_transfer.RunImportError, match="without overwrite"):
        run_transfer.import_package(package)
    assert json.loads(
        (destination / "manifest.json").read_text(encoding="utf-8")
    )["different"] is True


def test_nested_workspace_copy_is_normalized_without_losing_wrapper(
        transfer_ws):
    from aies import run_transfer, workspace

    run_id = "run-nested"
    wrapper = workspace.runs_dir() / run_id
    package = _package(wrapper, run_id)
    # _package adds archive-wrapper; reproduce the common RUN/RUN shape.
    direct = wrapper / run_id
    package.rename(direct)
    (wrapper / "archive-wrapper").rmdir()

    receipt = run_transfer.import_package(wrapper)
    canonical = workspace.runs_dir() / run_id
    preserved = Path(receipt["source_wrapper_preserved"])

    assert receipt["status"] == "imported"
    assert receipt["nested_source_wrapper"] is True
    assert (canonical / "manifest.json").is_file()
    assert (preserved / run_id / "manifest.json").is_file()
    assert preserved != canonical


def test_run_import_storage_is_explicitly_append_only(transfer_ws):
    from aies import workspace

    receipt = workspace.root() / "run-imports" / "run-import-fixture.json"
    preserved = workspace.root() / "import-sources" / "run-import-fixture"
    assert workspace.artifact_class(receipt) == "append-only-record"
    assert workspace.artifact_class(preserved) == "append-only-record"

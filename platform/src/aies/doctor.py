"""Environment validation and fingerprinting (pipeline stage 3).

Model behavior is a property of model x environment; the fingerprint is
provenance and its change is a re-qualification trigger (PLATFORM.md D7,
AIES-AESQS-RR-01 §2). Collection is best-effort and degrades gracefully:
every field it cannot determine is recorded as "unknown" rather than
omitted, so fingerprints stay comparable.
"""

from __future__ import annotations

import ctypes
import datetime
import hashlib
import json
import os
import platform as _platform
import shutil
import subprocess
import sys

from . import __version__
from . import workspace


def _ram_gb() -> float | str:
    try:
        if sys.platform == "win32":
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                    ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                    ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
                    ("ullAvailExtendedVirtual", ctypes.c_uint64),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return round(stat.ullTotalPhys / (1024 ** 3), 1)
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return round(pages * page_size / (1024 ** 3), 1)
    except Exception:
        return "unknown"


def _gpu() -> str:
    for cmd, args in (("nvidia-smi", ["--query-gpu=name", "--format=csv,noheader"]),):
        exe = shutil.which(cmd)
        if exe:
            try:
                out = subprocess.run([exe, *args], capture_output=True, text=True,
                                     timeout=10, check=False)
                if out.returncode == 0 and out.stdout.strip():
                    return out.stdout.strip().splitlines()[0]
            except Exception:
                pass
    if sys.platform == "darwin":
        return "apple-silicon (integrated)" if _platform.machine() == "arm64" else "unknown"
    return "unknown"


def fingerprint(runtime_component: dict | None = None) -> dict:
    """Collect the environment fingerprint (PLATFORM.md §5.5).

    runtime_component: the adapter's fingerprint() contribution, merged
    under "runtime" when a runtime is in play.
    """
    fp = {
        "machine": _platform.node() or "unknown",
        "cpu": _platform.processor() or _platform.machine() or "unknown",
        "gpu": _gpu(),
        "ram_gb": _ram_gb(),
        "os": f"{_platform.system()} {_platform.release()}",
        "python": _platform.python_version(),
        "runtime": runtime_component or {"id": "none", "version": "n/a"},
        # Power/thermal state is platform-specific; recorded when the
        # runtime adapter can report it, "unknown" otherwise.
        "power_state": (runtime_component or {}).get("power_state", "unknown"),
        "thermal_state": (runtime_component or {}).get("thermal_state", "unknown"),
        "platform_version": __version__,
    }
    canonical = json.dumps(fp, sort_keys=True)
    fp["fingerprint_hash"] = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
    return fp


def run_doctor() -> dict:
    """Validate the environment, persist the fingerprint, report readiness.

    Runtime-aware (PLATFORM.md D11): reports which runtime adapters are
    installed and, for each, whether its runtime is actually present on
    the host and what it can serve.
    """
    from .adapters import discovered  # late import: adapters may probe
    from . import runtimes

    fp = fingerprint()
    runtime_probes = runtimes.probe_all()
    checks = {
        "python_version_ok": sys.version_info >= (3, 10),
        "workspace_writable": True,
        "adapters_available": sorted(discovered().keys()),
        "runtimes_detected": [r["runtime"] for r in runtime_probes if r["available"]],
    }
    try:
        ws = workspace.ensure()
        checks["workspace"] = str(ws)
    except OSError:
        checks["workspace_writable"] = False
        checks["workspace"] = "unwritable"

    record = {
        "fingerprint": fp,
        "checks": checks,
        "runtimes": runtime_probes,
        "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ready": checks["python_version_ok"] and checks["workspace_writable"]
        and bool(checks["adapters_available"]),
    }
    if checks["workspace_writable"]:
        workspace.write_json(
            workspace.fingerprints_dir() / "latest.json", record, overwrite=True
        )
    return record

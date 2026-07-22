"""Operational configuration — environment variables and an optional .env file.

Everything here is *operational* (where the workspace lives, how to reach a
runtime endpoint, generation defaults, concurrency). It is intentionally
separate from the *normative* engine constants in `constants.py` (gates,
weights, sample sizes, confidence level, calibration threshold): those encode
the AESQS standard and MUST NOT be environment-tunable — a configurable gate
is no gate (PLATFORM.md D3). Nothing operational is hard-coded in the modules;
it is read here, from the environment or a .env file, with documented
defaults only for values that are safe to default.

Precedence (highest first): explicit CLI flag / deployment manifest →
real environment variable → .env file → built-in default (operational only).
A real environment variable always wins over the .env file.

Env file search order (first found wins), loaded once at import:
  1. $AIES_ENV_FILE
  2. ./.env  (current working directory)
  3. <workspace>/.env
See platform/.env.example for the full list of variables.
"""

from __future__ import annotations

import os
from pathlib import Path

_ENV_LOADED = False


def _parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        if key:
            out[key] = val
    return out


def load_dotenv(force: bool = False) -> Path | None:
    """Load the first .env file found into os.environ, without overriding
    variables already set in the real environment. Idempotent."""
    global _ENV_LOADED
    if _ENV_LOADED and not force:
        return None
    candidates = []
    if os.environ.get("AIES_ENV_FILE"):
        candidates.append(Path(os.environ["AIES_ENV_FILE"]))
    candidates.append(Path.cwd() / ".env")
    candidates.append(Path(os.environ.get("AIES_WORKSPACE", "aies-workspace")) / ".env")
    loaded = None
    for path in candidates:
        try:
            if path.is_file():
                for k, v in _parse_env_file(path).items():
                    os.environ.setdefault(k, v)  # real env wins
                loaded = path
                break
        except OSError:
            continue
    _ENV_LOADED = True
    return loaded


# Load eagerly so any module importing config sees .env values.
load_dotenv()


def _get(name: str, default: str | None = None) -> str | None:
    val = os.environ.get(name)
    return val if val not in (None, "") else default


# ---- operational settings -------------------------------------------------

def workspace_dir() -> str:
    return _get("AIES_WORKSPACE", "aies-workspace")


def endpoint(env_var: str, default: str | None = None) -> str | None:
    """Resolve a runtime endpoint URL from its env var, falling back to a
    runtime's conventional default (which an adapter may supply). A named
    runtime's conventional port is the adapter's knowledge of its target,
    not hard-coded configuration; it is always overridable via `env_var`."""
    return _get(env_var, default)


def openai_base_url() -> str | None:
    """Default endpoint for the generic openai-compat runtime when a
    deployment manifest does not specify one. No conventional default:
    unset means the runtime is simply not configured."""
    return _get("AIES_OPENAI_BASE_URL")


def openai_api_key() -> str | None:
    """API key for the openai-compat runtime, if the endpoint needs one.
    A deployment MAY name a different env var via runtime_config.api_key_env;
    this is the default source."""
    return _get("AIES_OPENAI_API_KEY")


def request_timeout_s() -> float:
    return float(_get("AIES_REQUEST_TIMEOUT_S", "300"))


def probe_timeout_s() -> float:
    """Connect timeout for the quick runtime liveness probe used by
    `aies doctor` / `aies discover`. Short by design."""
    return float(_get("AIES_PROBE_TIMEOUT_S", "3"))


def default_parallel() -> int:
    return int(_get("AIES_PARALLEL", "1"))


def default_judge() -> str | None:
    """Default judge deployment for automated scoring (`aies qualify --judge`).
    Set AIES_JUDGE to a deployment id (or "self") to auto-score every run
    without passing --judge each time."""
    return _get("AIES_JUDGE")


def judge_batch_size() -> int:
    """Maximum responses placed in one automated-review request.

    The reviewer still emits and AIES still persists one independent rating
    record per response.  Batching reduces inference overhead; it does not
    change the evidence unit.  Invalid values fall back to the conservative
    operational default rather than breaking qualification startup.
    """
    try:
        return max(1, int(_get("AIES_JUDGE_BATCH_SIZE", "8")))
    except (TypeError, ValueError):
        return 8


def generation_defaults() -> dict:
    """Generation parameters applied to every request unless a deployment
    manifest or CLI flag overrides them. Only set keys are emitted."""
    params: dict = {}
    for env_name, key, cast in (
        ("AIES_TEMPERATURE", "temperature", float),
        ("AIES_MAX_TOKENS", "max_tokens", int),
        ("AIES_TOP_P", "top_p", float),
        ("AIES_SEED", "seed", int),
    ):
        raw = _get(env_name)
        if raw is not None:
            try:
                params[key] = cast(raw)
            except ValueError:
                pass
    params["timeout_s"] = request_timeout_s()
    return params

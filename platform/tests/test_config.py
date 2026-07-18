"""Configuration: env vars and .env loading, precedence, and the
guarantee that NORMATIVE constants are never environment-tunable (D3)."""

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture()
def fresh_config(monkeypatch, tmp_path):
    # Reload config with a clean module state so load_dotenv re-runs.
    for var in ("AIES_WORKSPACE", "AIES_OPENAI_BASE_URL", "AIES_OPENAI_API_KEY",
                "AIES_REQUEST_TIMEOUT_S", "AIES_PARALLEL", "AIES_TEMPERATURE",
                "AIES_MAX_TOKENS"):
        monkeypatch.delenv(var, raising=False)
    # Hermetic: point the .env search at an empty file so a developer's real
    # platform/.env (e.g. a local AIES_OPENAI_BASE_URL) cannot leak into the
    # test. AIES_ENV_FILE is first in the search order, so cwd/.env is skipped.
    empty_env = tmp_path / "empty.env"
    empty_env.write_text("", encoding="utf-8")
    monkeypatch.setenv("AIES_ENV_FILE", str(empty_env))
    import aies.config as cfg
    importlib.reload(cfg)
    return cfg


def test_env_var_read_live(fresh_config, monkeypatch):
    monkeypatch.setenv("AIES_OPENAI_BASE_URL", "http://example:1234/v1")
    assert fresh_config.openai_base_url() == "http://example:1234/v1"


def test_no_hardcoded_endpoint_default(fresh_config):
    # Unset -> None, not a baked-in localhost.
    assert fresh_config.openai_base_url() is None


def test_dotenv_loaded_but_real_env_wins(monkeypatch, tmp_path):
    envfile = tmp_path / ".env"
    envfile.write_text(
        'AIES_OPENAI_BASE_URL="http://from-dotenv:5000/v1"\n'
        "AIES_PARALLEL=4\n"
        "# a comment\n"
        "export AIES_TEMPERATURE=0.3\n", encoding="utf-8")
    monkeypatch.setenv("AIES_ENV_FILE", str(envfile))
    # A real env var must override the .env value.
    monkeypatch.setenv("AIES_OPENAI_BASE_URL", "http://real-env:9000/v1")
    monkeypatch.delenv("AIES_PARALLEL", raising=False)
    monkeypatch.delenv("AIES_TEMPERATURE", raising=False)
    import aies.config as cfg
    importlib.reload(cfg)
    assert cfg.openai_base_url() == "http://real-env:9000/v1"   # real env wins
    assert cfg.default_parallel() == 4                          # from .env
    assert cfg.generation_defaults()["temperature"] == 0.3      # from .env (export + quotes)


def test_generation_defaults_only_set_keys(fresh_config, monkeypatch):
    monkeypatch.setenv("AIES_MAX_TOKENS", "2048")
    params = fresh_config.generation_defaults()
    assert params["max_tokens"] == 2048
    assert "temperature" not in params      # unset -> omitted, use model default
    assert params["timeout_s"] == 300.0


def test_normative_constants_are_not_env_tunable(monkeypatch):
    """D3: gates, weights, sample sizes, confidence, calibration threshold
    are the standard — no environment variable may change them."""
    monkeypatch.setenv("AIES_EV3_GATE_RT4", "0.0")
    monkeypatch.setenv("AIES_RT2_EV1_WEIGHT", "0.99")
    monkeypatch.setenv("AIES_MIN_SAMPLE_AI_RT2", "1")
    monkeypatch.setenv("AIES_CONFIDENCE", "0.5")
    monkeypatch.setenv("AIES_CALIBRATION_ADJACENT_THRESHOLD", "0.0")
    import aies.constants as C
    import aies.review as R
    importlib.reload(C)
    importlib.reload(R)
    assert C.GATES["RT4"]["EV3"] == 3.0            # unchanged
    assert C.WEIGHTS["RT2"]["EV1"] == 0.25          # unchanged
    assert C.MIN_SAMPLE["ai"]["RT2"] == 30          # unchanged
    assert C.CONFIDENCE == 0.90                     # unchanged
    assert R.CALIBRATION_ADJACENT_THRESHOLD == 0.80 # unchanged

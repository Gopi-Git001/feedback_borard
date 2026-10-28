"""The process refuses to start when configuration is missing or too weak."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from feedback_board.settings import Settings, SettingsError, load_settings
from tests.support import JWT_SECRET, child_environment

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "REPLACE_WITH_OUTPUT_OF_secrets_token_urlsafe_48"


def _run(
    *args: str,
    overrides: dict[str, str] | None = None,
    drop: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "feedback_board.main", *args],
        cwd=BACKEND_ROOT,
        env=child_environment(overrides, drop=drop),
        capture_output=True,
        text=True,
        check=False,
    )


def _load(overrides: dict[str, str]) -> Settings:
    previous = {key: os.environ.get(key) for key in overrides}
    os.environ.update(overrides)
    try:
        return load_settings()
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_missing_jwt_secret_exits_nonzero() -> None:
    completed = _run(drop=("JWT_SECRET",))
    assert completed.returncode != 0
    assert "startup refused:" in completed.stderr
    assert "JWT_SECRET is missing" in completed.stderr


def test_short_jwt_secret_exits_nonzero_and_does_not_echo_it() -> None:
    short_secret = "unique-short-secret-value"
    completed = _run(overrides={"JWT_SECRET": short_secret})
    assert completed.returncode != 0
    assert "JWT_SECRET must be at least 32 characters" in completed.stderr
    assert short_secret not in completed.stderr
    assert short_secret not in completed.stdout


def test_env_example_jwt_placeholder_is_rejected() -> None:
    example = (BACKEND_ROOT.parent / ".env.example").read_text(encoding="utf-8")
    placeholder = ""
    for line in example.splitlines():
        if line.startswith("JWT_SECRET="):
            placeholder = line.split("=", 1)[1]
            break
    assert placeholder == PLACEHOLDER
    completed = _run(overrides={"JWT_SECRET": placeholder})
    assert completed.returncode != 0
    assert "weak or placeholder fragment" in completed.stderr
    assert placeholder not in completed.stderr


def test_jwt_secret_must_decode_to_32_bytes() -> None:
    # 32 characters, so the length check passes and the ADR-002 byte rule still fails.
    value = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef"
    assert len(value) == 32
    completed = _run(overrides={"JWT_SECRET": value})
    assert completed.returncode != 0
    assert "JWT_SECRET must decode to at least 32 bytes" in completed.stderr
    assert value not in completed.stderr


def test_check_exits_zero_for_a_valid_configuration() -> None:
    completed = _run("--check")
    assert completed.returncode == 0
    assert "startup refused:" not in completed.stderr
    assert JWT_SECRET not in completed.stderr
    assert JWT_SECRET not in completed.stdout


def test_app_env_must_be_known() -> None:
    completed = _run(overrides={"APP_ENV": "staging"})
    assert completed.returncode != 0
    assert "APP_ENV must be one of: development, test, production" in completed.stderr


def test_missing_app_env_is_refused() -> None:
    completed = _run(drop=("APP_ENV",))
    assert completed.returncode != 0
    assert "APP_ENV must be one of: development, test, production" in completed.stderr


def test_production_rejects_cookie_secure_false() -> None:
    completed = _run(overrides={"APP_ENV": "production", "COOKIE_SECURE": "false"})
    assert completed.returncode != 0
    assert "COOKIE_SECURE=false" in completed.stderr


def test_production_rejects_rate_limit_disabled() -> None:
    with pytest.raises(SettingsError, match="RATE_LIMIT_ENABLED=false"):
        _load({"APP_ENV": "production", "RATE_LIMIT_ENABLED": "false"})


def test_non_local_https_rejects_relaxations() -> None:
    with pytest.raises(SettingsError, match="COOKIE_SECURE=false"):
        _load(
            {
                "APP_ENV": "test",
                "COOKIE_SECURE": "false",
                "FRONTEND_ORIGIN": "https://board.example.com",
            },
        )


def test_invite_key_must_differ(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INVITE_TOKEN_KEY", JWT_SECRET)
    with pytest.raises(SettingsError, match="INVITE_TOKEN_KEY must differ from JWT_SECRET"):
        load_settings()


def test_invite_placeholder_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    placeholder = "REPLACE_WITH_OUTPUT_OF_secrets_token_bytes_32_base64url"
    monkeypatch.setenv("INVITE_TOKEN_KEY", placeholder)
    with pytest.raises(SettingsError, match="INVITE_TOKEN_KEY") as caught:
        load_settings()
    assert placeholder not in str(caught.value)


def test_wrong_database_scheme_does_not_echo_the_password(monkeypatch: pytest.MonkeyPatch) -> None:
    password = "db-password-should-not-leak"
    monkeypatch.setenv(
        "DATABASE_URL",
        f"postgresql://feedback_owner:{password}@127.0.0.1:5432/feedback_board",
    )
    with pytest.raises(
        SettingsError,
        match=r"DATABASE_URL scheme must be postgresql\+psycopg",
    ) as caught:
        load_settings()
    assert password not in str(caught.value)


def test_trusted_proxy_wildcards_are_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRUSTED_PROXY_IPS", "*")
    with pytest.raises(SettingsError, match="TRUSTED_PROXY_IPS"):
        load_settings()


def test_production_requires_a_proxy_address() -> None:
    with pytest.raises(SettingsError, match="TRUSTED_PROXY_IPS must be non-empty"):
        _load({"APP_ENV": "production", "TRUSTED_PROXY_IPS": ""})


def test_malformed_rate_limit_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_SIGNUP_PER_IP", "nope")
    with pytest.raises(SettingsError, match="RATE_LIMIT_SIGNUP_PER_IP"):
        load_settings()


def test_development_allows_the_local_http_relaxations() -> None:
    settings = _load(
        {
            "APP_ENV": "development",
            "COOKIE_SECURE": "false",
            "RATE_LIMIT_ENABLED": "false",
            "FRONTEND_ORIGIN": "http://localhost:8080",
        },
    )
    assert settings.active_relaxations() == ("COOKIE_SECURE", "RATE_LIMIT_ENABLED")

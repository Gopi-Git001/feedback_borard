"""Shared test environment. Secrets are generated, never taken from .env.example."""

import os
import secrets

# ADR-002 weak-fragment denylist. A random token that contains one is rejected.
_WEAK_FRAGMENTS = (
    "secret",
    "changeme",
    "change-me",
    "change_me",
    "password",
    "replace",
    "placeholder",
    "example",
    "default",
    "jwt",
    "test",
    "dev",
)

# The compose `db` service creates only the owner role (TASK-003). The restricted
# `feedback_app` role does not exist yet, so tests connect as `feedback_owner`
# with the placeholder password from `.env.example`. The scheme under test is
# `postgresql+psycopg`.
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://feedback_owner:change-me-owner-password@127.0.0.1:5432/feedback_board"
)


def make_secret() -> str:
    for _ in range(30):
        value = secrets.token_urlsafe(48)
        lowered = value.lower()
        if any(fragment in lowered for fragment in _WEAK_FRAGMENTS):
            continue
        if len(set(value)) < 16:
            continue
        return value
    raise RuntimeError("could not generate a secret that passes the ADR-002 rule")


JWT_SECRET = make_secret()
INVITE_TOKEN_KEY = make_secret()


def apply_test_environment() -> None:
    os.environ["APP_ENV"] = "test"
    os.environ["JWT_SECRET"] = JWT_SECRET
    os.environ["INVITE_TOKEN_KEY"] = INVITE_TOKEN_KEY
    os.environ.setdefault("DATABASE_URL", DEFAULT_DATABASE_URL)
    os.environ["FRONTEND_ORIGIN"] = "http://localhost:8080"
    os.environ["COOKIE_SECURE"] = "true"
    os.environ["RATE_LIMIT_ENABLED"] = "true"
    os.environ["TRUSTED_PROXY_IPS"] = "127.0.0.1"
    os.environ["ARGON2_MAX_CONCURRENCY"] = "4"
    os.environ["REFRESH_REUSE_LEEWAY_SECONDS"] = "10"


def child_environment(
    overrides: dict[str, str] | None = None,
    *,
    drop: tuple[str, ...] = (),
) -> dict[str, str]:
    env = os.environ.copy()
    env["APP_ENV"] = "test"
    env["JWT_SECRET"] = JWT_SECRET
    env["INVITE_TOKEN_KEY"] = INVITE_TOKEN_KEY
    env.setdefault("DATABASE_URL", DEFAULT_DATABASE_URL)
    env["FRONTEND_ORIGIN"] = "http://localhost:8080"
    env["COOKIE_SECURE"] = "true"
    env["RATE_LIMIT_ENABLED"] = "true"
    env["TRUSTED_PROXY_IPS"] = "127.0.0.1"
    env["ARGON2_MAX_CONCURRENCY"] = "4"
    env["REFRESH_REUSE_LEEWAY_SECONDS"] = "10"
    if overrides:
        env.update(overrides)
    for name in drop:
        env.pop(name, None)
    return env

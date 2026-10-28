"""Shared test environment. Secrets and passwords come from the environment or are generated here.

No password literal is stored in this file. ``scripts/init-env.sh`` is not on main yet;
until that script lands, generate database passwords with ``openssl rand -hex 24``.
"""

import os
import secrets
from urllib.parse import quote

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


def _required(name: str) -> str:
    value = os.environ.get(name, "")
    if value == "":
        raise RuntimeError(
            f"{name} is not set. Generate a value with `openssl rand -hex 24` and export it. "
            "scripts/init-env.sh is not on main yet.",
        )
    return value


def _database_url(user: str, password: str) -> str:
    host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    port = os.environ.get("POSTGRES_HOST_PORT", "5432")
    database = os.environ.get("POSTGRES_DB", "feedback_board")
    return (
        "postgresql+psycopg://"
        f"{quote(user, safe='')}:{quote(password, safe='')}"
        f"@{host}:{port}/{quote(database, safe='')}"
    )


def build_app_database_url() -> str:
    """Runtime URL for the restricted ``feedback_app`` role (``DATABASE_URL``)."""

    configured = os.environ.get("DATABASE_URL", "")
    if configured:
        return configured
    user = os.environ.get("APP_DB_USER", "feedback_app")
    return _database_url(user, _required("APP_DB_PASSWORD"))


def build_owner_database_url() -> str:
    """Owner URL for DDL (TASK-006). Not the default app connection."""

    user = os.environ.get("POSTGRES_USER", "feedback_owner")
    return _database_url(user, _required("POSTGRES_PASSWORD"))


def apply_test_environment() -> None:
    os.environ["APP_ENV"] = "test"
    os.environ["JWT_SECRET"] = JWT_SECRET
    os.environ["INVITE_TOKEN_KEY"] = INVITE_TOKEN_KEY
    os.environ["DATABASE_URL"] = build_app_database_url()
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
    if not env.get("DATABASE_URL"):
        env["DATABASE_URL"] = build_app_database_url()
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

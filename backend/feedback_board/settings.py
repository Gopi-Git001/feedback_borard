"""Process environment. The process exits when a required value is invalid.

Secret rules follow ADR-002. The TASK-004 length check (missing or shorter
than 32 characters) is the first secret check, so that failure stays explicit.
The rest of the ADR-002 rule is applied as well: ``.env.example`` says the
placeholder is rejected on purpose, and a 32-character string does not decode
to 32 bytes.
"""

import base64
import ipaddress
import re
from collections.abc import Callable
from enum import StrEnum
from typing import Never
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")
_RATE_LIMIT = re.compile(r"^(\d+)/(\d+)$")
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
_FORBIDDEN_PROXIES = frozenset({"*", "0.0.0.0/0", "::/0"})
_LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
_DEFAULT_RATE_LIMIT = "10/60"


class SettingsError(Exception):
    """Configuration is invalid. The message never includes a secret value."""


class AppEnv(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class RateLimit(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_hits: int
    window_seconds: int


class RateLimits(BaseModel):
    model_config = ConfigDict(frozen=True)

    signup_per_ip: RateLimit
    login_per_ip: RateLimit
    refresh_per_ip: RateLimit
    invite_preview_per_ip: RateLimit
    invite_accept_per_ip: RateLimit
    org_create_per_user: RateLimit


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_env: AppEnv
    jwt_secret: SecretStr
    invite_token_key: SecretStr
    database_url: SecretStr
    frontend_origin: str
    cookie_secure: bool
    trusted_proxy_ips: tuple[str, ...]
    argon2_max_concurrency: int
    refresh_reuse_leeway_seconds: int
    rate_limit_enabled: bool
    rate_limits: RateLimits

    def active_relaxations(self) -> tuple[str, ...]:
        names: list[str] = []
        if not self.cookie_secure:
            names.append("COOKIE_SECURE")
        if not self.rate_limit_enabled:
            names.append("RATE_LIMIT_ENABLED")
        return tuple(names)


class _RawSettings(BaseSettings):
    """Strings as they arrived. Validation, and its messages, live in ``load_settings``."""

    model_config = SettingsConfigDict(extra="ignore", env_file=None)

    app_env: str | None = None
    jwt_secret: str | None = None
    invite_token_key: str | None = None
    database_url: str | None = None
    frontend_origin: str | None = None
    cookie_secure: str | None = None
    trusted_proxy_ips: str | None = None
    argon2_max_concurrency: str | None = None
    refresh_reuse_leeway_seconds: str | None = None
    rate_limit_enabled: str | None = None
    rate_limit_signup_per_ip: str | None = None
    rate_limit_login_per_ip: str | None = None
    rate_limit_refresh_per_ip: str | None = None
    rate_limit_invite_preview_per_ip: str | None = None
    rate_limit_invite_accept_per_ip: str | None = None
    rate_limit_org_create_per_user: str | None = None


def load_settings() -> Settings:
    raw = _RawSettings()
    problems: list[str] = []

    app_env = _capture(problems, lambda: _parse_app_env(raw.app_env))
    jwt_secret = _capture(problems, lambda: _parse_secret("JWT_SECRET", raw.jwt_secret))
    invite_token_key = _capture(
        problems,
        lambda: _parse_secret("INVITE_TOKEN_KEY", raw.invite_token_key),
    )
    database_url = _capture(problems, lambda: _parse_database_url(raw.database_url))
    frontend_origin = _capture(problems, lambda: _parse_origin(raw.frontend_origin))
    cookie_secure = _capture(
        problems,
        lambda: _parse_bool("COOKIE_SECURE", raw.cookie_secure, default=True),
    )
    trusted_proxy_ips = _capture(problems, lambda: _parse_proxy_ips(raw.trusted_proxy_ips))
    argon2_max_concurrency = _capture(
        problems,
        lambda: _parse_int("ARGON2_MAX_CONCURRENCY", raw.argon2_max_concurrency, 4, 1, 64),
    )
    refresh_reuse_leeway_seconds = _capture(
        problems,
        lambda: _parse_int(
            "REFRESH_REUSE_LEEWAY_SECONDS",
            raw.refresh_reuse_leeway_seconds,
            10,
            0,
            60,
        ),
    )
    rate_limit_enabled = _capture(
        problems,
        lambda: _parse_bool("RATE_LIMIT_ENABLED", raw.rate_limit_enabled, default=True),
    )
    rate_limits = _capture(problems, lambda: _parse_rate_limits(raw))

    if (
        problems
        or app_env is None
        or jwt_secret is None
        or invite_token_key is None
        or database_url is None
        or frontend_origin is None
        or cookie_secure is None
        or trusted_proxy_ips is None
        or argon2_max_concurrency is None
        or refresh_reuse_leeway_seconds is None
        or rate_limit_enabled is None
        or rate_limits is None
    ):
        raise SettingsError("; ".join(problems) if problems else "invalid configuration")

    if app_env is AppEnv.PRODUCTION and not trusted_proxy_ips:
        raise SettingsError("TRUSTED_PROXY_IPS must be non-empty when APP_ENV=production")
    if jwt_secret == invite_token_key:
        raise SettingsError("INVITE_TOKEN_KEY must differ from JWT_SECRET")

    settings = Settings(
        app_env=app_env,
        jwt_secret=SecretStr(jwt_secret),
        invite_token_key=SecretStr(invite_token_key),
        database_url=SecretStr(database_url),
        frontend_origin=frontend_origin,
        cookie_secure=cookie_secure,
        trusted_proxy_ips=trusted_proxy_ips,
        argon2_max_concurrency=argon2_max_concurrency,
        refresh_reuse_leeway_seconds=refresh_reuse_leeway_seconds,
        rate_limit_enabled=rate_limit_enabled,
        rate_limits=rate_limits,
    )
    _enforce_relaxation_guard(settings)
    return settings


def _capture[T](problems: list[str], parse: Callable[[], T]) -> T | None:
    try:
        return parse()
    except SettingsError as exc:
        problems.append(str(exc))
        return None


def _parse_app_env(value: str | None) -> AppEnv:
    if value is None or value == "":
        raise SettingsError("APP_ENV must be one of: development, test, production")
    for item in AppEnv:
        if value == item.value:
            return item
    raise SettingsError("APP_ENV must be one of: development, test, production")


def _parse_secret(name: str, value: str | None) -> str:
    if value is None or value == "":
        raise SettingsError(f"{name} is missing")
    if len(value) < 32:
        raise SettingsError(f"{name} must be at least 32 characters")
    if _BASE64URL.fullmatch(value) is None or len(value) % 4 == 1:
        raise SettingsError(f"{name} must be unpadded base64url")
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except ValueError:
        raise SettingsError(f"{name} must be unpadded base64url") from None
    if len(decoded) < 32:
        raise SettingsError(f"{name} must decode to at least 32 bytes")
    if len(set(value)) < 16:
        raise SettingsError(f"{name} must contain at least 16 distinct characters")
    lowered = value.lower()
    for fragment in _WEAK_FRAGMENTS:
        if fragment in lowered:
            raise SettingsError(f"{name} contains a weak or placeholder fragment")
    return value


def _parse_database_url(value: str | None) -> str:
    if value is None or value == "":
        raise SettingsError("DATABASE_URL is missing")
    parsed = urlsplit(value)
    if parsed.scheme != "postgresql+psycopg":
        raise SettingsError("DATABASE_URL scheme must be postgresql+psycopg")
    database_name = parsed.path.lstrip("/")
    if not database_name or "/" in database_name:
        raise SettingsError("DATABASE_URL must include a database name")
    return value


def _parse_origin(value: str | None) -> str:
    message = (
        "FRONTEND_ORIGIN must be a bare origin (scheme://host[:port], no path or trailing slash)"
    )
    if value is None or value == "":
        raise SettingsError("FRONTEND_ORIGIN is missing")
    parsed = urlsplit(value)
    if (
        value.endswith("/")
        or parsed.scheme not in {"http", "https"}
        or parsed.hostname is None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise SettingsError(message)
    return value


def _parse_bool(name: str, value: str | None, *, default: bool) -> bool:
    if value is None or value == "":
        return default
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    raise SettingsError(f"{name} must be a boolean")


def _parse_int(name: str, value: str | None, default: int, low: int, high: int) -> int:
    if value is None or value == "":
        number = default
    elif value.isdigit():
        number = int(value)
    else:
        raise SettingsError(f"{name} must be an integer {low}-{high}")
    if number < low or number > high:
        raise SettingsError(f"{name} must be an integer {low}-{high}")
    return number


def _parse_proxy_ips(value: str | None) -> tuple[str, ...]:
    if value is None or value.strip() == "":
        return ()
    parts = [part.strip() for part in value.split(",")]
    if any(part == "" for part in parts):
        raise SettingsError("TRUSTED_PROXY_IPS must be comma-separated exact IP addresses")
    if any(part in _FORBIDDEN_PROXIES for part in parts):
        raise SettingsError("TRUSTED_PROXY_IPS must not contain '*', '0.0.0.0/0' or '::/0'")
    addresses: list[str] = []
    for part in parts:
        try:
            addresses.append(str(ipaddress.ip_address(part)))
        except ValueError:
            raise SettingsError(
                "TRUSTED_PROXY_IPS must be comma-separated exact IP addresses",
            ) from None
    return tuple(addresses)


def _parse_rate_limit(name: str, value: str | None) -> RateLimit:
    raw = _DEFAULT_RATE_LIMIT if value is None or value == "" else value
    match = _RATE_LIMIT.fullmatch(raw)
    if match is None:
        raise SettingsError(
            f"{name} must be <max>/<window_seconds> with max 1-10000 and window 1-86400",
        )
    max_hits = int(match.group(1))
    window_seconds = int(match.group(2))
    if not 1 <= max_hits <= 10000 or not 1 <= window_seconds <= 86400:
        raise SettingsError(
            f"{name} must be <max>/<window_seconds> with max 1-10000 and window 1-86400",
        )
    return RateLimit(max_hits=max_hits, window_seconds=window_seconds)


def _parse_rate_limits(raw: _RawSettings) -> RateLimits:
    return RateLimits(
        signup_per_ip=_parse_rate_limit("RATE_LIMIT_SIGNUP_PER_IP", raw.rate_limit_signup_per_ip),
        login_per_ip=_parse_rate_limit("RATE_LIMIT_LOGIN_PER_IP", raw.rate_limit_login_per_ip),
        refresh_per_ip=_parse_rate_limit(
            "RATE_LIMIT_REFRESH_PER_IP",
            raw.rate_limit_refresh_per_ip,
        ),
        invite_preview_per_ip=_parse_rate_limit(
            "RATE_LIMIT_INVITE_PREVIEW_PER_IP",
            raw.rate_limit_invite_preview_per_ip,
        ),
        invite_accept_per_ip=_parse_rate_limit(
            "RATE_LIMIT_INVITE_ACCEPT_PER_IP",
            raw.rate_limit_invite_accept_per_ip,
        ),
        org_create_per_user=_parse_rate_limit(
            "RATE_LIMIT_ORG_CREATE_PER_USER",
            raw.rate_limit_org_create_per_user,
        ),
    )


def _is_non_local_https(origin: str) -> bool:
    parsed = urlsplit(origin)
    return parsed.scheme == "https" and parsed.hostname not in _LOCAL_HOSTS


def _relaxation_allowed(app_env: AppEnv, origin: str) -> bool:
    if _is_non_local_https(origin):
        return False
    if app_env is AppEnv.PRODUCTION:
        return False
    if app_env is AppEnv.DEVELOPMENT or app_env is AppEnv.TEST:
        return True
    _never(app_env)


def _enforce_relaxation_guard(settings: Settings) -> None:
    active = settings.active_relaxations()
    if not active:
        return
    if _relaxation_allowed(settings.app_env, settings.frontend_origin):
        return
    rendered = ", ".join(f"{name}=false" for name in active)
    raise SettingsError(
        f"{rendered} is not allowed when APP_ENV={settings.app_env.value} "
        "or FRONTEND_ORIGIN is a non-local https origin",
    )


def _never(value: Never) -> Never:
    raise SettingsError(f"unhandled APP_ENV: {value}")

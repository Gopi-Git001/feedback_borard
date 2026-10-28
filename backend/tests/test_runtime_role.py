"""DATABASE_URL role check, driven through the ASGI lifespan."""

import io
import logging
import os
import secrets
from collections.abc import Iterator
from urllib.parse import quote, urlsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, text

from feedback_board.app import create_app
from feedback_board.db import create_db_engine
from feedback_board.logging_config import RedactingHandler
from feedback_board.role_check import StartupRefused
from tests.support import build_owner_database_url

_SUPER = "task004_super"
_BYPASS = "task004_bypass"
_CLEAN = "task004_clean"


@pytest.fixture(scope="module")
def role_passwords() -> Iterator[dict[str, str]]:
    passwords = {
        _SUPER: secrets.token_hex(16),
        _BYPASS: secrets.token_hex(16),
        _CLEAN: secrets.token_hex(16),
    }
    database = os.environ.get("POSTGRES_DB", "feedback_board")
    engine = create_db_engine(build_owner_database_url())
    try:
        with engine.connect() as connection:
            for name, password, superuser, bypass in (
                (_SUPER, passwords[_SUPER], True, False),
                (_BYPASS, passwords[_BYPASS], False, True),
                (_CLEAN, passwords[_CLEAN], False, False),
            ):
                _ensure_role(
                    connection,
                    name=name,
                    password=password,
                    database=database,
                    superuser=superuser,
                    bypassrls=bypass,
                )
            connection.commit()
        yield passwords
    finally:
        engine.dispose()


def test_superuser_without_bypassrls_refuses(
    monkeypatch: pytest.MonkeyPatch,
    role_passwords: dict[str, str],
    capfd: pytest.CaptureFixture[str],
) -> None:
    _assert_refused(monkeypatch, capfd, _SUPER, role_passwords[_SUPER])


def test_nosuperuser_with_bypassrls_refuses(
    monkeypatch: pytest.MonkeyPatch,
    role_passwords: dict[str, str],
    capfd: pytest.CaptureFixture[str],
) -> None:
    _assert_refused(monkeypatch, capfd, _BYPASS, role_passwords[_BYPASS])


def test_feedback_owner_refuses(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    url = build_owner_database_url()
    password = urlsplit(url).password or ""
    _assert_refused_url(monkeypatch, capfd, url, password)


def test_clean_role_starts(
    monkeypatch: pytest.MonkeyPatch,
    role_passwords: dict[str, str],
) -> None:
    url = _url(_CLEAN, role_passwords[_CLEAN])
    monkeypatch.setenv("DATABASE_URL", url)
    application = create_app()
    with TestClient(application) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unreachable_database_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    password = secrets.token_hex(16)
    url = f"postgresql+psycopg://feedback_app:{quote(password, safe='')}@127.0.0.1:1/feedback_board"
    _assert_refused_url(monkeypatch, capfd, url, password)


def _assert_refused(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    user: str,
    password: str,
) -> None:
    _assert_refused_url(monkeypatch, capfd, _url(user, password), password)


def _assert_refused_url(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    url: str,
    password: str,
) -> None:
    monkeypatch.setenv("DATABASE_URL", url)
    application = create_app()
    handler = _redacting_handler()
    buffer = io.StringIO()
    previous = handler.stream
    handler.stream = buffer
    try:
        with pytest.raises(StartupRefused) as caught:
            with TestClient(application):
                pass
    finally:
        handler.stream = previous
    captured = capfd.readouterr()
    leaked = "\n".join((buffer.getvalue(), captured.out, captured.err, str(caught.value)))
    assert password not in leaked
    assert url not in leaked
    assert "startup refused:" in str(caught.value)


def _redacting_handler() -> RedactingHandler:
    for handler in logging.getLogger("feedback_board").handlers:
        if isinstance(handler, RedactingHandler):
            return handler
    raise AssertionError("redacting handler was not installed")


def _url(user: str, password: str) -> str:
    host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    port = os.environ.get("POSTGRES_HOST_PORT", "5432")
    database = os.environ.get("POSTGRES_DB", "feedback_board")
    return (
        "postgresql+psycopg://"
        f"{quote(user, safe='')}:{quote(password, safe='')}"
        f"@{host}:{port}/{quote(database, safe='')}"
    )


def _ensure_role(
    connection: Connection,
    *,
    name: str,
    password: str,
    database: str,
    superuser: bool,
    bypassrls: bool,
) -> None:
    exists = connection.execute(
        text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
        {"name": name},
    ).scalar()
    ident = connection.execute(text("SELECT quote_ident(:name)"), {"name": name}).scalar_one()
    literal = connection.execute(
        text("SELECT quote_literal(:password)"),
        {"password": password},
    ).scalar_one()
    database_ident = connection.execute(
        text("SELECT quote_ident(:database)"),
        {"database": database},
    ).scalar_one()
    super_sql = "SUPERUSER" if superuser else "NOSUPERUSER"
    bypass_sql = "BYPASSRLS" if bypassrls else "NOBYPASSRLS"
    verb = "ALTER ROLE" if exists else "CREATE ROLE"
    connection.execute(
        text(f"{verb} {ident} WITH LOGIN {super_sql} {bypass_sql} PASSWORD {literal}"),
    )
    connection.execute(text(f"GRANT CONNECT ON DATABASE {database_ident} TO {ident}"))

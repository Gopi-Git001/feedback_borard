"""Redaction runs on the handler, including child, root, and uvicorn loggers."""

import base64
import io
import logging
import secrets

import pytest
from fastapi import FastAPI

from feedback_board.logging_config import RedactingHandler, SecretRedactionFilter
from feedback_board.main import main
from feedback_board.settings import Settings

_UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")


def test_handler_redacts_secrets_patterns_and_library_loggers(app: FastAPI) -> None:
    settings: Settings = app.state.settings
    jwt_secret = settings.jwt_secret.get_secret_value()
    invite_key = settings.invite_token_key.get_secret_value()
    database_url = settings.database_url.get_secret_value()
    app_logger = logging.getLogger("feedback_board")
    assert app_logger.filters == []
    handler = app_logger.handlers[0]
    assert isinstance(handler, RedactingHandler)
    assert isinstance(handler, logging.StreamHandler)
    assert any(isinstance(item, SecretRedactionFilter) for item in handler.filters)
    root = logging.getLogger()
    assert handler in root.handlers
    for name in _UVICORN_LOGGERS:
        uvicorn_logger = logging.getLogger(name)
        assert handler in uvicorn_logger.handlers
        assert uvicorn_logger.filters == []
        assert uvicorn_logger.propagate is False

    extra_password = secrets.token_hex(16)
    dsn_password = secrets.token_hex(16)
    bearer_token = secrets.token_hex(16)
    header = base64.urlsafe_b64encode(b'{"alg":"none"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(b'{"sub":"1"}').decode().rstrip("=")
    forged_jwt = f"{header}.{payload}.{secrets.token_urlsafe(8)}"
    other_dsn = f"postgresql://report:{dsn_password}@db.example/app"

    buffer = io.StringIO()
    previous = handler.stream
    handler.stream = buffer
    try:
        logging.getLogger("feedback_board.child").warning("child %s %s", jwt_secret, invite_key)
        logging.getLogger("uvicorn").warning("uvicorn %s", jwt_secret)
        logging.getLogger("uvicorn.error").warning("error %s", invite_key)
        logging.getLogger("uvicorn.access").warning("access %s", database_url)
        logging.getLogger().warning("root password=%s", extra_password)
        logging.getLogger("sqlalchemy.engine").warning("engine %s", other_dsn)
        logging.getLogger("asyncio").warning("bearer", extra={"note": f"Bearer {bearer_token}"})
        logging.getLogger("feedback_board.extra").warning(
            "fields %s",
            forged_jwt,
            extra={"password": extra_password},
        )
        logging.getLogger("feedback_board.bad").warning("malformed %s %s", dsn_password)
    finally:
        handler.stream = previous

    logged = buffer.getvalue()
    for secret in (
        jwt_secret,
        invite_key,
        database_url,
        extra_password,
        dsn_password,
        bearer_token,
        forged_jwt,
        other_dsn,
    ):
        assert secret not in logged
    assert '"logger":"feedback_board.child"' in logged
    assert '"logger":"uvicorn"' in logged
    assert '"logger":"uvicorn.error"' in logged
    assert '"logger":"uvicorn.access"' in logged
    assert '"logger":"root"' in logged
    assert '"logger":"sqlalchemy.engine"' in logged
    assert "Bearer [redacted]" in logged
    assert '"password":"[redacted]"' in logged


def test_server_entrypoint_disables_default_uvicorn_logging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorded: dict[str, object] = {}

    def fake_run(app: object, **kwargs: object) -> None:
        recorded.update(kwargs)
        engine = getattr(getattr(app, "state", None), "engine", None)
        dispose = getattr(engine, "dispose", None)
        if callable(dispose):
            dispose()

    monkeypatch.setattr("feedback_board.main.uvicorn.run", fake_run)
    main([])
    assert recorded["log_config"] is None
    assert recorded["access_log"] is False

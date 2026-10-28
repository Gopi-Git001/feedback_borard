"""Redaction runs on the handler, including child and uvicorn loggers."""

import io
import logging

from fastapi import FastAPI

from feedback_board.logging_config import SecretRedactionFilter
from feedback_board.settings import Settings

_UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")


def test_handler_redacts_child_and_uvicorn_records(app: FastAPI) -> None:
    settings: Settings = app.state.settings
    secret = settings.jwt_secret.get_secret_value()
    app_logger = logging.getLogger("feedback_board")
    assert app_logger.filters == []
    handler = app_logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert any(isinstance(item, SecretRedactionFilter) for item in handler.filters)
    for name in _UVICORN_LOGGERS:
        uvicorn_logger = logging.getLogger(name)
        assert handler in uvicorn_logger.handlers
        assert uvicorn_logger.filters == []
        assert uvicorn_logger.propagate is False

    buffer = io.StringIO()
    previous = handler.stream
    handler.stream = buffer
    try:
        logging.getLogger("feedback_board.child").warning("child %s", secret)
        logging.getLogger("uvicorn").warning("uvicorn %s", secret)
        logging.getLogger("uvicorn.error").warning("error %s", secret)
        logging.getLogger("uvicorn.access").warning("access %s", secret)
    finally:
        handler.stream = previous

    logged = buffer.getvalue()
    assert secret not in logged
    assert logged.count("[redacted]") == 4
    assert '"logger":"feedback_board.child"' in logged
    assert '"logger":"uvicorn"' in logged
    assert '"logger":"uvicorn.error"' in logged
    assert '"logger":"uvicorn.access"' in logged

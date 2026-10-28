"""JSON logs. Secret values are redacted and are never part of the message."""

import json
import logging
import re
from typing import TextIO
from urllib.parse import urlsplit

from feedback_board.settings import Settings

_STANDARD_ATTRS = frozenset(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}

# scheme://user:password@host  — only the password group is replaced.
_DSN_PASSWORD = re.compile(
    r"([a-zA-Z][a-zA-Z0-9+.-]*://[^/\s:@]+:)([^@\s]+)(@)",
)
_BEARER = re.compile(r"(?i)\bBearer\s+\S+")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\.[A-Za-z0-9_-]{4,}\b")
_PASSWORD_TEXT = re.compile(r"(?i)(\bpassword\s*[=:]\s*)([^\s,;]+)")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in payload or key in _STANDARD_ATTRS or key.startswith("_"):
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                payload[key] = value
        return json.dumps(payload, separators=(",", ":"), sort_keys=True)


class SecretRedactionFilter(logging.Filter):
    def __init__(self, secrets: tuple[str, ...]) -> None:
        super().__init__()
        self._secrets = tuple(secret for secret in secrets if secret)

    def filter(self, record: logging.LogRecord) -> bool:
        # A bad format string must not escape the logging call.
        try:
            rendered = record.getMessage()
        except Exception:
            rendered = _unformatted(record)
        redacted = _redact(rendered, self._secrets)
        record.msg = redacted
        record.args = ()
        record.message = redacted
        for key, value in list(record.__dict__.items()):
            if key.lower() == "password":
                setattr(record, key, "[redacted]")
            elif isinstance(value, str):
                updated = _redact(value, self._secrets)
                if updated != value:
                    setattr(record, key, updated)
        return True


def _unformatted(record: logging.LogRecord) -> str:
    # Do not splice the arguments into the text: formatting already failed,
    # and those values can be secrets. They are dropped when args is cleared.
    if isinstance(record.msg, str):
        return record.msg
    return "log message could not be formatted"


def _redact(text: str, secrets: tuple[str, ...]) -> str:
    redacted = text
    for secret in secrets:
        redacted = redacted.replace(secret, "[redacted]")
    redacted = _DSN_PASSWORD.sub(r"\1[redacted]\3", redacted)
    redacted = _BEARER.sub("Bearer [redacted]", redacted)
    redacted = _JWT.sub("[redacted]", redacted)
    redacted = _PASSWORD_TEXT.sub(r"\1[redacted]", redacted)
    return redacted


def secret_values(settings: Settings) -> tuple[str, ...]:
    values = [
        settings.jwt_secret.get_secret_value(),
        settings.invite_token_key.get_secret_value(),
        settings.database_url.get_secret_value(),
    ]
    password = urlsplit(settings.database_url.get_secret_value()).password
    if password:
        values.append(password)
    unique: list[str] = []
    for value in values:
        if value and value not in unique:
            unique.append(value)
    return tuple(unique)


class RedactingHandler(logging.StreamHandler[TextIO]):
    """The one handler whose filter redacts records from every attached logger."""


# uvicorn.error and uvicorn.access are children of uvicorn. A logger filter on
# the parent is not applied to records that propagate from a child, so the
# redaction filter lives on the shared handler instead. The root logger gets
# the same handler so library loggers (sqlalchemy, asyncio, and the rest) are
# covered too.
_LOGGER_NAMES = ("feedback_board", "uvicorn", "uvicorn.error", "uvicorn.access")


def configure_logging(settings: Settings) -> logging.Handler:
    handler = RedactingHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(SecretRedactionFilter(secret_values(settings)))
    for name in _LOGGER_NAMES:
        logger = logging.getLogger(name)
        logger.handlers = [
            item for item in logger.handlers if not isinstance(item, RedactingHandler)
        ]
        logger.filters.clear()
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger.addHandler(handler)
    root = logging.getLogger()
    root.handlers = [item for item in root.handlers if not isinstance(item, RedactingHandler)]
    root.addHandler(handler)
    return handler


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_relaxations(settings: Settings) -> None:
    logger = get_logger("feedback_board.startup")
    for variable in settings.active_relaxations():
        logger.warning("startup relaxation active", extra={"variable": variable})

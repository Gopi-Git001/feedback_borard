"""Standard error body from the API contract."""

from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException

_LOC_PREFIXES = frozenset({"body", "query", "path", "header", "cookie"})


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    message: str


class ErrorBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: list[ErrorDetail]


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ErrorBody


class AppError(Exception):
    """A handled failure that already has a contract-shaped body."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class DatabaseUnavailable(AppError):
    def __init__(self) -> None:
        super().__init__(503, "INTERNAL_ERROR", "Database unavailable")


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or []),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def _field_name(loc: object) -> str:
    if not isinstance(loc, tuple):
        return "request"
    parts = [str(part) for part in loc if str(part) not in _LOC_PREFIXES]
    if not parts:
        return "request"
    return ".".join(parts)


def _rule_message(error: dict[str, Any]) -> str:
    """Pydantic's rule text, with the submitted value removed.

    ADR-004: drop FastAPI ``input`` and ``ctx``. The contract example uses the
    rule sentence (``msg``), which states the constraint and not the value.
    """

    raw_message = error.get("msg")
    message = raw_message if isinstance(raw_message, str) and raw_message else "invalid"
    submitted = error.get("input")
    if isinstance(submitted, str) and submitted:
        message = message.replace(submitted, "")
    return message


def validation_details(errors: Sequence[Any]) -> list[ErrorDetail]:
    details: list[ErrorDetail] = []
    for error in errors:
        if not isinstance(error, dict):
            continue
        details.append(
            ErrorDetail(field=_field_name(error.get("loc")), message=_rule_message(error)),
        )
    return details


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return error_response(
            400,
            "VALIDATION_ERROR",
            "Request validation failed.",
            validation_details(exc.errors()),
        )

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return error_response(exc.status_code, exc.code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        if exc.status_code == 404:
            return error_response(404, "NOT_FOUND", "Not found")
        if exc.status_code == 405:
            return error_response(405, "METHOD_NOT_ALLOWED", "Method not allowed")
        if exc.status_code == 400:
            return error_response(400, "VALIDATION_ERROR", "Request validation failed.")
        return error_response(exc.status_code, "INTERNAL_ERROR", "Internal server error")

"""Every error uses the contract body. Request validation is 400, not 422."""

import io
import logging
import secrets

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

from feedback_board.app import create_app
from feedback_board.logging_config import JsonFormatter
from feedback_board.role_check import StartupRefused


def _error(response_json: object) -> dict[str, object]:
    assert isinstance(response_json, dict)
    error = response_json["error"]
    assert isinstance(error, dict)
    assert set(error) == {"code", "message", "details"}
    return error


def test_unknown_path_is_404(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    error = _error(response.json())
    assert error["code"] == "NOT_FOUND"
    assert error["message"] == "Not found"
    assert error["details"] == []
    assert response.headers["cache-control"] == "no-store"


def test_undefined_edit_route_is_not_415(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/posts/1",
        content="not-json",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code == 404
    assert response.status_code != 415
    error = _error(response.json())
    assert error["code"] == "NOT_FOUND"
    assert error["details"] == []


def test_interactive_docs_are_disabled(client: TestClient) -> None:
    for path in ("/docs", "/redoc", "/openapi.json"):
        response = client.get(path)
        assert response.status_code == 404
        error = _error(response.json())
        assert error["code"] == "NOT_FOUND"
        assert error["details"] == []


def test_wrong_method_is_405(client: TestClient) -> None:
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    error = _error(response.json())
    assert error["code"] == "METHOD_NOT_ALLOWED"
    assert error["details"] == []
    assert response.headers["x-content-type-options"] == "nosniff"


def test_request_validation_is_400_and_drops_the_submitted_value(app: FastAPI) -> None:
    class Payload(BaseModel):
        model_config = ConfigDict(extra="forbid")

        count: int

    @app.post("/api/v1/_validation_probe")
    def _probe(payload: Payload) -> dict[str, str]:
        return {"count": str(payload.count)}

    submitted = "submitted-value-should-not-leak"
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/v1/_validation_probe",
            json={"count": submitted, "extra": "another-leak-value"},
        )
    assert response.status_code == 400
    assert response.status_code != 422
    error = _error(response.json())
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"] == "Request validation failed."
    details = error["details"]
    assert isinstance(details, list)
    assert details
    rendered = response.text
    assert submitted not in rendered
    assert "another-leak-value" not in rendered
    fields = [item["field"] for item in details if isinstance(item, dict)]
    assert "count" in fields


def test_unhandled_exception_is_500_without_the_message(app: FastAPI) -> None:
    secret = "leak-this-secret-xyz"

    @app.get("/api/v1/_boom")
    def _boom() -> dict[str, str]:
        raise RuntimeError(secret)

    log_buffer = io.StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("feedback_board")
    logger.addHandler(handler)
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/api/v1/_boom")
    finally:
        logger.removeHandler(handler)
    logged = log_buffer.getvalue()
    assert response.status_code == 500
    error = _error(response.json())
    assert error["code"] == "INTERNAL_ERROR"
    assert error["message"] == "Internal server error"
    assert error["details"] == []
    assert secret not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert secret not in response.headers.get("x-request-id", "")
    assert '"message":"unhandled exception"' in logged
    assert '"exc_type":"RuntimeError"' in logged
    assert secret not in logged


def test_unreachable_database_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    password = secrets.token_hex(16)
    url = f"postgresql+psycopg://feedback_app:{password}@127.0.0.1:1/feedback_board"
    monkeypatch.setenv("DATABASE_URL", url)
    application = create_app()
    with pytest.raises(StartupRefused) as caught:
        with TestClient(application):
            pass
    assert password not in str(caught.value)
    assert url not in str(caught.value)

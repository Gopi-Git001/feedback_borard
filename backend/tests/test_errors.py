"""Every error uses the contract body. Request validation is 400, not 422."""

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

from feedback_board.app import create_app


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

    logger = logging.getLogger("feedback_board")
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/v1/_boom")
    assert response.status_code == 500
    error = _error(response.json())
    assert error["code"] == "INTERNAL_ERROR"
    assert error["message"] == "Internal server error"
    assert error["details"] == []
    assert secret not in response.text
    assert response.headers["cache-control"] == "no-store"
    # The handler records the exception type, not the text.
    assert logger.filters
    assert secret not in response.headers.get("x-request-id", "")


def test_database_outage_uses_the_error_body(monkeypatch: pytest.MonkeyPatch) -> None:
    password = "db-password-should-not-leak"
    monkeypatch.setenv(
        "DATABASE_URL",
        f"postgresql+psycopg://feedback_owner:{password}@127.0.0.1:1/feedback_board",
    )
    application = create_app()
    try:
        with TestClient(application, raise_server_exceptions=False) as client:
            response = client.get("/api/v1/health")
    finally:
        application.state.engine.dispose()
    assert response.status_code == 503
    error = _error(response.json())
    assert error["code"] == "INTERNAL_ERROR"
    assert error["message"] == "Database unavailable"
    assert error["details"] == []
    assert password not in response.text
    assert response.headers["cache-control"] == "no-store"

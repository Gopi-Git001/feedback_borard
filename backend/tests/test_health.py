"""GET /api/v1/health against the real database."""

import json
import logging

import pytest
from fastapi.testclient import TestClient

from feedback_board.logging_config import JsonFormatter
from tests.support import JWT_SECRET


def test_health_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["content-type"].startswith("application/json")


def test_health_security_headers(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "req-health-1"})
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert (
        response.headers["content-security-policy"] == "default-src 'none'; frame-ancestors 'none'"
    )
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"
    assert response.headers["x-request-id"] == "req-health-1"
    assert "strict-transport-security" not in response.headers


def test_health_access_log_has_no_secret(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger("feedback_board")
    logger.addHandler(caplog.handler)
    caplog.set_level(logging.INFO, logger="feedback_board")
    try:
        response = client.get("/api/v1/health", headers={"X-Request-ID": "req-health-2"})
    finally:
        logger.removeHandler(caplog.handler)
    assert response.status_code == 200
    records = [record for record in caplog.records if record.getMessage() == "request"]
    assert records
    rendered = JsonFormatter().format(records[-1])
    payload = json.loads(rendered)
    assert payload["method"] == "GET"
    assert payload["route"] == "/api/v1/health"
    assert payload["status"] == 200
    assert isinstance(payload["duration_ms"], float)
    assert payload["request_id"] == "req-health-2"
    assert JWT_SECRET not in rendered
    assert "change-me-owner-password" not in rendered

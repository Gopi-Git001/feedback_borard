"""Pytest configuration. The database is never mocked."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from feedback_board.app import create_app
from tests.support import apply_test_environment

apply_test_environment()


@pytest.fixture
def app() -> Iterator[FastAPI]:
    application = create_app()
    yield application
    application.state.engine.dispose()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

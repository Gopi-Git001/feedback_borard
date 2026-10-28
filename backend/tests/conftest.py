"""Pytest configuration. The database is never mocked."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from feedback_board.app import create_app
from feedback_board.db import create_db_engine
from tests.support import apply_test_environment, build_owner_database_url

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


@pytest.fixture
def owner_database_url() -> str:
    """Owner/DDL URL for later tasks. The app suite does not use this role."""

    return build_owner_database_url()


@pytest.fixture
def owner_engine(owner_database_url: str) -> Iterator[Engine]:
    """Owner connection for DDL. Dispose it after the test."""

    engine = create_db_engine(owner_database_url)
    try:
        yield engine
    finally:
        engine.dispose()

"""Prove ``postgresql+psycopg://`` against real PostgreSQL 18. The database is not mocked."""

import importlib.util
import os
from urllib.parse import urlsplit

import psycopg
import sqlalchemy
from sqlalchemy import text

from feedback_board.db import create_db_engine
from feedback_board.repositories.health import HealthRepository


def test_postgresql_psycopg_scheme_connects_to_postgres_18() -> None:
    url = os.environ["DATABASE_URL"]
    assert urlsplit(url).scheme == "postgresql+psycopg"
    assert importlib.util.find_spec("psycopg_binary") is not None
    assert psycopg.__version__.startswith("3.3.")
    assert sqlalchemy.__version__.startswith("2.1.")

    engine = create_db_engine(url)
    try:
        assert engine.dialect.name == "postgresql"
        assert engine.dialect.driver == "psycopg"
        assert engine.url.drivername == "postgresql+psycopg"
        assert HealthRepository(engine).ping() is True
        with engine.connect() as connection:
            one = connection.execute(text("SELECT 1")).scalar_one()
            version = connection.execute(text("SHOW server_version")).scalar_one()
            version_num = connection.execute(text("SHOW server_version_num")).scalar_one()
    finally:
        engine.dispose()

    assert one == 1
    version_text = str(version)
    assert version_text.startswith("18."), version_text
    assert int(str(version_num)) >= 180000
    # Kept in the assertion message so a failure report shows the server build.
    assert "18." in version_text, version_text

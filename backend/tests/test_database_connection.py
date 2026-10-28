"""Prove ``postgresql+psycopg://`` against real PostgreSQL 18. The database is not mocked."""

import importlib.util
import os
from urllib.parse import urlsplit

import psycopg
import sqlalchemy
from sqlalchemy import Engine, text

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
            current_user = connection.execute(text("SELECT current_user")).scalar_one()
            one = connection.execute(text("SELECT 1")).scalar_one()
            version = connection.execute(text("SHOW server_version")).scalar_one()
            version_num = connection.execute(text("SHOW server_version_num")).scalar_one()
    finally:
        engine.dispose()

    assert str(current_user) == os.environ.get("APP_DB_USER", "feedback_app")
    assert one == 1
    version_text = str(version)
    assert "18.6" in version_text, version_text
    assert int(str(version_num)) >= 180006


def test_owner_engine_is_separate_from_the_app_role(owner_engine: Engine) -> None:
    with owner_engine.connect() as connection:
        current_user = connection.execute(text("SELECT current_user")).scalar_one()
        rolsuper = connection.execute(
            text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user"),
        ).scalar_one()
    assert str(current_user) == os.environ.get("POSTGRES_USER", "feedback_owner")
    assert bool(rolsuper) is True
    assert urlsplit(os.environ["DATABASE_URL"]).username != str(current_user)

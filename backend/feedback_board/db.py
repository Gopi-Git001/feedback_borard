"""SQLAlchemy engine. The URL scheme is ``postgresql+psycopg``."""

from sqlalchemy import Engine, create_engine


def create_db_engine(database_url: str) -> Engine:
    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3},
    )

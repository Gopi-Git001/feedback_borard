"""Database reachability. No query result is logged."""

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from feedback_board.logging_config import get_logger


class HealthRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def ping(self) -> bool:
        try:
            with self._engine.connect() as connection:
                value = connection.execute(text("SELECT 1")).scalar_one()
        except SQLAlchemyError:
            get_logger("feedback_board.db").error("database ping failed")
            return False
        return bool(value == 1)

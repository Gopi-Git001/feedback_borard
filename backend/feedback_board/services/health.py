"""Liveness of the API process and its database."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from feedback_board.errors import DatabaseUnavailable
from feedback_board.repositories.health import HealthRepository


class HealthStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]


class HealthService:
    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    def check(self) -> HealthStatus:
        if not self._repository.ping():
            raise DatabaseUnavailable()
        return HealthStatus(status="ok")

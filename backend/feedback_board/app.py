"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import Engine

from feedback_board.api.health import build_health_router
from feedback_board.db import create_db_engine
from feedback_board.errors import register_exception_handlers
from feedback_board.logging_config import configure_logging
from feedback_board.middleware import SecurityHeadersMiddleware
from feedback_board.repositories.health import HealthRepository
from feedback_board.services.health import HealthService
from feedback_board.settings import Settings, load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = load_settings() if settings is None else settings
    configure_logging(resolved)
    engine = create_db_engine(resolved.database_url.get_secret_value())

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        stored: Engine = app.state.engine
        stored.dispose()

    # The contract does not define /docs, /redoc, or /openapi.json.
    app = FastAPI(
        title="Team Feedback Board API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.settings = resolved
    app.state.engine = engine
    service = HealthService(HealthRepository(engine))
    app.include_router(build_health_router(service), prefix="/api/v1")
    register_exception_handlers(app)
    app.add_middleware(SecurityHeadersMiddleware)
    return app

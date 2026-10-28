"""GET /api/v1/health."""

from fastapi import APIRouter

from feedback_board.services.health import HealthService, HealthStatus


def build_health_router(service: HealthService) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthStatus)
    def get_health() -> HealthStatus:
        return service.check()

    return router

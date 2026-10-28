"""Security headers (ADR-004) and a structured access log."""

import re
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from feedback_board.errors import error_response
from feedback_board.logging_config import get_logger

_REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_API_CSP = "default-src 'none'; frame-ancestors 'none'"
_PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=()"


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        request_id = _request_id(request)
        started_at = time.perf_counter()
        status_code = 500
        response_started = False

        async def send_with_headers(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = int(message["status"])
                headers = MutableHeaders(scope=message)
                headers["Cache-Control"] = "no-store"
                headers["X-Content-Type-Options"] = "nosniff"
                headers["Referrer-Policy"] = "no-referrer"
                headers["Content-Security-Policy"] = _API_CSP
                headers["Permissions-Policy"] = _PERMISSIONS_POLICY
                headers["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        except Exception as exc:
            # Starlette's server-error handler sits outside this middleware, so a
            # response it builds would skip these headers. Handle it here.
            # The exception text is not logged; it can echo request input.
            if response_started:
                raise
            get_logger("feedback_board.error").error(
                "unhandled exception",
                extra={"exc_type": type(exc).__name__},
            )
            response = error_response(500, "INTERNAL_ERROR", "Internal server error")
            await response(scope, receive, send_with_headers)
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
            get_logger("feedback_board.request").info(
                "request",
                extra={
                    "method": request.method,
                    "route": _route_template(scope),
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "request_id": request_id,
                },
            )


def _request_id(request: Request) -> str:
    incoming = request.headers.get("x-request-id", "")
    if _REQUEST_ID.fullmatch(incoming):
        return incoming
    return uuid.uuid4().hex


def _route_template(scope: Scope) -> str:
    route = scope.get("route")
    route_path = getattr(route, "path", None)
    if not isinstance(route_path, str) or not route_path:
        return "unmatched"
    request_path = scope.get("path")
    if isinstance(request_path, str) and request_path.endswith(route_path):
        return f"{request_path[: -len(route_path)]}{route_path}"
    return route_path

import logging
import time
import uuid
from http import HTTPStatus

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_context import request_id_ctx_var

logger = logging.getLogger(__name__)

class RequestIDGeneratorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        token = request_id_ctx_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx_var.reset(token)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
            },
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.time() - start_time) * 1000, 2)

            logger.exception(
                "Unhandled exception during request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)

        http_status = HTTPStatus(response.status_code)
        level = get_log_level(http_status)
        message = f"Request completed ({http_status.value} {http_status.phrase})"

        logger.log(
            level,
            message,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": http_status.value,
                "duration_ms": duration_ms,
            },
        )

        return response


def get_log_level(status_code: HTTPStatus) -> int:
    if status_code.is_informational:
        return logging.DEBUG

    elif status_code.is_success:
        return logging.INFO

    elif status_code.is_redirection:
        return logging.INFO

    elif status_code.is_client_error:
        # Refined handling for common expected client errors
        common_client_errors = [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]

        if status_code in common_client_errors:
            return logging.INFO
        else:
            return logging.WARNING

    elif status_code.is_server_error:
        return logging.ERROR

    else:
        # Fallback for unknown codes
        return logging.INFO

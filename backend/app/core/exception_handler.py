import logging
from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.middlewares import get_log_level

logger = logging.getLogger(__name__)


def add_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(
                f"App Server Error - {exc.__class__.__name__}: {exc.message}",
                extra={
                    "status_code": exc.status_code,
                    "details": getattr(exc, "details", None),
                    "method": request.method,
                    "path": request.url.path,
                },
                exc_info=True,
            )

            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "message": "Internal Server Error",
                        "details": None,
                    },
                },
            )

        http_status = HTTPStatus(exc.status_code)

        log_level = get_log_level(http_status)

        logger.log(
            log_level,
            f"{exc.__class__.__name__}: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "details": getattr(exc, "details", None),
                "method": request.method,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "details": getattr(exc, "details", None),
                },
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        logger.exception(
            "Unhandled exception",
            extra={
                "status_code": status_code,
                "method": request.method,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {"message": "Internal Server Error"},
            },
        )

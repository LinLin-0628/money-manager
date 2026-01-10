import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.utils.utils import get_request_id

logger = logging.getLogger(__name__)


def add_exception_handler(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(
            f"{exc.__class__.__name__}: {exc.message}",
            extra={
                "request_id": get_request_id(request),
                "status_code": exc.status_code,
                "details": getattr(exc, "details", None),
                "method": request.method,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "request_id": get_request_id(request),
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

        logger.error(
            "Unhandled exception",
            exc_info=True,
            extra={
                "request_id": get_request_id(request),
                "status_code": status_code,
                "method": request.method,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "request_id": get_request_id(request),
                "error": {"message": "Internal Server Error"},
            },
        )

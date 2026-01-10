from fastapi import FastAPI, Request, status
from app.core.exceptions import AppException
from fastapi.responses import JSONResponse


def add_exception_handler(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "request_id": request.state.request_id,
                "error": {
                    "message": exc.message,
                    "details": getattr(exc, "details", None),
                },
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request.state.request_id,
                "error": {"message": "Internal Server Error"},
            },
        )

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.exception_handler import add_exception_handler
from app.core.logging import setup_logging
from app.core.middlewares import RequestIDGeneratorMiddleware, RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # Startup
    setup_logging()
    yield
    # Shutdown (if needed)


origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Next.js/React default
    "http://127.0.0.1:5173",
]

app = FastAPI(title="Money Manager", lifespan=lifespan)

# Add exception handler
add_exception_handler(app)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDGeneratorMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add router
app.include_router(api_router, prefix="/api")

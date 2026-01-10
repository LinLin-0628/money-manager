from fastapi import FastAPI
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.exception_handler import add_exception_handler
from app.core.logging import setup_logging
from app.core.middlewares import RequestLoggingMiddleware

setup_logging()

origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Next.js/React default
    "http://127.0.0.1:5173",
]

app = FastAPI(title="Money Manager")

# Add exception handler
add_exception_handler(app)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add router
app.include_router(api_router, prefix="/api")

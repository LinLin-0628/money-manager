from fastapi import FastAPI
from app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Next.js/React default
    "http://127.0.0.1:5173",
]

app = FastAPI(title="Money Manager")

app.include_router(api_router, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
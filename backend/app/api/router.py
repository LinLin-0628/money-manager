from fastapi import APIRouter

from app.api.routes import user, auth

api_router = APIRouter()

api_router.include_router(user.router)
api_router.include_router(auth.router)

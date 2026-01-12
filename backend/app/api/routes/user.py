from fastapi import APIRouter, Depends, status

from app.api.deps import get_user_service
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
) -> User:
    return user_service.register_user(user_data)

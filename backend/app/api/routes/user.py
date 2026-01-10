from fastapi import APIRouter, status, Depends

from app.api.deps import get_user_service
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register_user(
        user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    return user_service.register_user(user_data)
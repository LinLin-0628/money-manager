from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.deps.auth import get_current_user
from app.api.deps.common import get_category_service
from app.api.deps.pagination import PaginationParams
from app.models import User
from app.schemas.category import CategoryCreate, CategoryRead
from app.schemas.pagination import PaginatedResponse
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=PaginatedResponse[CategoryRead]
)
def get_all_categories(
    pagination: Annotated[PaginationParams, Depends()],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PaginatedResponse[CategoryRead]:
    return category_service.get_all_categories(current_user, pagination)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryRead)
def create_category(
    category_create_data: CategoryCreate,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CategoryRead:
    new_cat = category_service.create_category(current_user, category_create_data)
    return CategoryRead.model_validate(new_cat)

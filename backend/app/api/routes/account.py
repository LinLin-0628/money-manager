from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps.auth import get_current_user
from app.api.deps.common import get_account_service
from app.api.deps.pagination import PaginationParams
from app.models import User
from app.schemas.account import AccountCreate, AccountRead
from app.schemas.pagination import PaginatedResponse
from app.services.account import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=PaginatedResponse[AccountRead]
)
def get_all_accounts(
    pagination: Annotated[PaginationParams, Depends()],
    account_service: Annotated[AccountService, Depends(get_account_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PaginatedResponse[AccountRead]:
    return account_service.get_all_accounts(current_user, pagination)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountRead)
def create_account(
    account_create_data: AccountCreate,
    service: Annotated[AccountService, Depends(get_account_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    new_account = service.create_account(current_user, account_create_data)
    return new_account

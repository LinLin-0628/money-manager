from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.api.deps.auth import get_current_user
from app.api.deps.common import get_transaction_service
from app.api.deps.pagination import PaginationParams
from app.models import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.transaction import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[TransactionRead],
)
def get_all_transactions(
    pagination: Annotated[PaginationParams, Depends()],
    transaction_service: Annotated[
        TransactionService, Depends(get_transaction_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PaginatedResponse[TransactionRead]:
    return transaction_service.get_all_transactions(current_user, pagination)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransactionRead)
def create_transaction(
    transaction_create_data: TransactionCreate,
    transaction_service: Annotated[
        TransactionService, Depends(get_transaction_service)
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TransactionRead:
    new_transaction = transaction_service.create_transaction(
        current_user, transaction_create_data
    )
    return TransactionRead.model_validate(new_transaction)

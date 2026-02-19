from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from app.api.deps.auth import get_current_user
from app.api.deps.common import get_budget_service
from app.api.deps.pagination import PaginationParams
from app.models import User
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.budget import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[BudgetRead],
)
def get_all_budgets(
    pagination: Annotated[PaginationParams, Depends()],
    budget_service: Annotated[BudgetService, Depends(get_budget_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PaginatedResponse[BudgetRead]:
    return budget_service.get_all_budgets(current_user, pagination)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BudgetRead)
def create_budget(
    budget_create_data: BudgetCreate,
    budget_service: Annotated[BudgetService, Depends(get_budget_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BudgetRead:
    new_budget = budget_service.create_budget(current_user, budget_create_data)
    return BudgetRead.model_validate(new_budget)


@router.put("/{budget_id}", status_code=status.HTTP_200_OK, response_model=BudgetRead)
def update_budget(
    budget_id: int,
    budget_update_data: BudgetUpdate,
    budget_service: Annotated[BudgetService, Depends(get_budget_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BudgetRead:
    """
    Update a budget's amount.
    Only the amount can be updated - to change month or category, delete and recreate.
    """
    updated_budget = budget_service.update_budget(
        current_user, budget_id, budget_update_data
    )
    return BudgetRead.model_validate(updated_budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    budget_service: Annotated[BudgetService, Depends(get_budget_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a budget by ID."""
    budget_service.delete_budget(current_user, budget_id)

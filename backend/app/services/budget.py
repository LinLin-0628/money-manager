import logging
from collections.abc import Sequence
from datetime import date
from math import ceil

from sqlalchemy.exc import IntegrityError

from app.api.deps.pagination import PaginationParams
from app.core.exceptions.base import AppException
from app.core.exceptions.budget import (
    BudgetInvalidDateError,
    BudgetNotFoundError,
    DuplicateBudgetException,
)
from app.core.exceptions.category import (
    CategoryNotFoundError,
    CategoryTypeMismatchError,
)
from app.enum.transaction_type import TransactionType
from app.models import Budget, User
from app.repositories.budget import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.category import CategoryService

logger = logging.getLogger(__name__)


class BudgetService:
    def __init__(
        self, budget_repo: BudgetRepository, category_service: CategoryService
    ):
        self.budget_repo = budget_repo
        self.category_service = category_service

    def _populate_actual_spending(self, budgets: Sequence[Budget]) -> Sequence[Budget]:
        for budget in budgets:
            budget.actual_spent = self.budget_repo.get_actual_spending(
                budget.user_id, budget.category_id, budget.month
            )
        return budgets

    def get_all_budgets(self, current_user: User, pagination: PaginationParams):
        logger.info(
            "Fetch all budgets start",
            extra={
                "page": pagination.page,
                "size": pagination.size,
            },
        )

        total = self.budget_repo.get_total_count(current_user.id)
        budgets = self.budget_repo.get_all_budgets(
            current_user.id, pagination.offset, pagination.size
        )
        budgets_with_actual_spending = self._populate_actual_spending(budgets)
        total_pages = ceil(total / pagination.size) if total > 0 else 1
        items = [
            BudgetRead.model_validate(budget) for budget in budgets_with_actual_spending
        ]

        logger.info(
            "Fetch all budgets complete",
            extra={
                "total": total,
                "page": pagination.page,
                "size": pagination.size,
                "total_pages": total_pages,
            },
        )

        return PaginatedResponse[BudgetRead](
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=total_pages,
            items=items,
        )

    def create_budget(self, current_user: User, budget_create_data: BudgetCreate):
        try:
            category = self.category_service.get_category_by_id(
                current_user, budget_create_data.category_id
            )

            if not category:
                raise CategoryNotFoundError()

            if category.type != TransactionType.EXPENSE:
                raise CategoryTypeMismatchError(
                    "Budget can only be created for expense categories"
                )

            today_date = date.today()
            if budget_create_data.month < date(today_date.year, today_date.month, 1):
                raise BudgetInvalidDateError("Budget month cannot be in the past")

            new_budget = self.budget_repo.create_budget(
                Budget(**budget_create_data.model_dump(), user_id=current_user.id)
            )

            self.budget_repo.db.commit()
            logger.info("Create budget complete", extra={"budget_id": new_budget.id})
            return new_budget
        except IntegrityError as e:
            self.budget_repo.db.rollback()
            logger.warning("Create budget failed")
            raise DuplicateBudgetException() from e

    def update_budget(
        self, current_user: User, budget_id: int, budget_update_data: BudgetUpdate
    ):
        """
        Update a budget's amount.
        Only the amount field can be updated - month and category are immutable.
        """
        logger.info(
            "Update budget start",
            extra={"budget_id": budget_id, "user_id": current_user.id},
        )

        # Fetch budget and verify ownership
        budget = self.get_budget_by_id(current_user, budget_id)
        if not budget:
            raise BudgetNotFoundError()

        # Update the amount (service layer handles the update logic)
        budget.amount = budget_update_data.amount

        try:
            self.budget_repo.db.commit()
            self.budget_repo.db.refresh(budget)

            logger.info(
                "Update budget complete",
                extra={"budget_id": budget.id, "new_amount": budget.amount},
            )

            # Populate actuals
            budgets_with_actual = self._populate_actual_spending([budget])
            return budgets_with_actual[0]

        except Exception as e:
            self.budget_repo.db.rollback()
            logger.error(
                "Update budget failed",
                extra={"budget_id": budget_id, "error": str(e)},
            )
            raise AppException("Failed to update budget") from e

    def delete_budget(self, current_user: User, budget_id: int) -> None:
        """
        Delete a budget.
        Validates ownership before deletion.
        """
        logger.info(
            "Delete budget start",
            extra={"budget_id": budget_id, "user_id": current_user.id},
        )

        # Fetch budget and verify ownership
        budget = self.get_budget_by_id(current_user, budget_id)
        if not budget:
            raise BudgetNotFoundError()

        try:
            self.budget_repo.delete_budget(budget)
            self.budget_repo.db.commit()

            logger.info(
                "Delete budget complete",
                extra={"budget_id": budget_id},
            )

        except Exception as e:
            self.budget_repo.db.rollback()
            logger.error(
                "Delete budget failed",
                extra={"budget_id": budget_id, "error": str(e)},
            )
            raise AppException("Failed to delete budget") from e

    def get_budget_by_id(self, current_user: User, budget_id: int) -> Budget:
        """
        Get a single budget by ID with actual spending populated.
        Validates ownership.
        """
        logger.info(
            "Fetch budget by ID start",
            extra={"budget_id": budget_id, "user_id": current_user.id},
        )

        budget = self.budget_repo.get_budget_by_id(current_user.id, budget_id)
        if not budget:
            raise BudgetNotFoundError()

        # Populate actual spending
        budgets_with_actual = self._populate_actual_spending([budget])

        logger.info(
            "Fetch budget by ID complete",
            extra={"budget_id": budget_id},
        )

        return budgets_with_actual[0]

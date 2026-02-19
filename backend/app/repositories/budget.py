from calendar import monthrange
from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.enum.transaction_type import TransactionType
from app.models import Budget, Transaction


class BudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_count(self, user_id: UUID):
        stmt = select(func.count(Budget.id)).where(Budget.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_all_budgets(
        self, user_id: UUID, offset: int, size: int
    ) -> Sequence[Budget]:
        stmt = (
            select(Budget)
            .where(Budget.user_id == user_id)
            .options(
                selectinload(Budget.category),
                selectinload(Budget.user),
            )
            .order_by(Budget.month.desc())
            .offset(offset)
            .limit(size)
        )
        return self.db.execute(stmt).scalars().all()

    def create_budget(self, new_budget: Budget) -> Budget:
        self.db.add(new_budget)
        self.db.flush()
        self.db.refresh(new_budget)
        return new_budget

    def get_actual_spending(
        self, user_id: UUID, category_id: int, month: date
    ) -> Decimal:
        month_start = month.replace(day=1)
        last_day = monthrange(month.year, month.month)[1]
        month_end = month.replace(day=last_day)

        stmt = (
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(Transaction.user_id == user_id)
            .where(Transaction.category_id == category_id)
            .where(Transaction.transaction_datetime >= month_start)
            .where(Transaction.transaction_datetime <= month_end)
            .where(Transaction.type == TransactionType.EXPENSE)
        )

        return self.db.execute(stmt).scalar_one()

    def delete_budget(self, budget: Budget) -> None:
        self.db.delete(budget)
        self.db.flush()

    def get_budget_by_id(self, user_id: UUID, budget_id: int) -> Budget | None:
        """Fetch a single budget by ID, scoped to user."""
        stmt = (
            select(Budget)
            .where(Budget.user_id == user_id)
            .where(Budget.id == budget_id)
            .options(
                selectinload(Budget.category),
                selectinload(Budget.user),
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

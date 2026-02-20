import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint(
            "user_id", "category_id", "month", name="uq_budget_user_cat_month"
        ),
        CheckConstraint("amount > 0", name="ck_budget_amount_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    month = mapped_column(Date, nullable=False)  # stored as first day: 2025-06-01
    amount = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category = relationship("Category", back_populates="budgets")
    user = relationship("User", back_populates="budgets")

    @hybrid_property
    def actual_spent(self) -> Decimal:
        return getattr(self, "_actual_spent", Decimal("0"))

    @actual_spent.setter
    def actual_spent(self, value: Decimal):
        self._actual_spent = value

    @property
    def remaining(self) -> Decimal:
        return self.amount - self.actual_spent

    @property
    def percent_used(self) -> float:
        if self.amount == 0:
            return 0.0
        return float(self.actual_spent / self.amount)

    @property
    def is_overspent(self) -> bool:
        return self.actual_spent > self.amount

    def __repr__(self):
        return f"<Budget user={self.user_id} category={self.category_id} month={self.month} amount={self.amount}>"  # noqa: E501

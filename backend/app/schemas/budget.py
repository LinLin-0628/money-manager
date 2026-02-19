from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.category import CategoryReadSummary
from app.schemas.user import UserReadSummary
from app.utils.validators import round_decimal


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    month: date
    amount: Decimal

    actual_spent: Decimal
    remaining: Decimal
    percent_used: float
    is_overspent: bool

    created_at: datetime
    updated_at: datetime

    user: UserReadSummary
    category: CategoryReadSummary


class BudgetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    month: date = Field(...)
    amount: Decimal = Field(..., decimal_places=2, gt=0)
    category_id: int = Field(..., ge=0)

    @field_validator("amount", mode="before")
    @classmethod
    def round_amount(cls, value: str | int | float | Decimal | None) -> Decimal:
        return round_decimal(value)

    @field_validator("month")
    @classmethod
    def normalize_date(cls, value: date) -> date:
        return date(value.year, value.month, 1)


class BudgetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(..., decimal_places=2, gt=0)

    @field_validator("amount", mode="before")
    @classmethod
    def round_amount(cls, value: str | int | float | Decimal | None) -> Decimal:
        return round_decimal(value)

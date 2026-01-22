from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enum.transaction_type import TransactionType
from app.schemas.account import AccountReadSummary
from app.schemas.category import CategoryReadSummary
from app.schemas.user import UserReadSummary
from app.utils.validators import round_decimal


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    type: TransactionType
    title: str
    description: str | None
    transaction_datetime: datetime

    account: AccountReadSummary
    category: CategoryReadSummary

    user: UserReadSummary


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(..., decimal_places=2, ge=0)
    type: TransactionType = Field(...)
    title: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=500)
    transaction_datetime: datetime = Field(default_factory=datetime.now)

    account_id: int = Field(..., ge=0)
    category_id: int = Field(..., ge=0)

    @field_validator("amount", mode="before")
    @classmethod
    def round_amount(cls, value: str | int | float | Decimal | None) -> Decimal:
        return round_decimal(value)

    @field_validator("type", mode="before")
    @classmethod
    def clean_type(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("title")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if value:
            value = value.strip().lower()

        if not value:
            raise ValueError("Account name cannot be empty")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        if value:
            value = value.strip()

        if not value:
            value = None

        return value


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(..., decimal_places=2, ge=0)
    type: TransactionType = Field(...)
    title: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=500)
    transaction_datetime: datetime = Field(default_factory=datetime.now)

    account_id: int = Field(..., ge=0)
    category_id: int = Field(..., ge=0)

    @field_validator("amount", mode="before")
    @classmethod
    def round_amount(cls, value: str | int | float | Decimal | None) -> Decimal:
        return round_decimal(value)

    @field_validator("type", mode="before")
    @classmethod
    def clean_type(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("title")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if value:
            value = value.strip().lower()

        if not value:
            raise ValueError("Account name cannot be empty")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        if value:
            value = value.strip()

        if not value:
            value = None

        return value

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user import UserReadSummary
from app.utils.validators import round_decimal

# TODO: Remove duplicate part and extract common part


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    balance: Decimal
    description: str | None

    created_at: datetime
    updated_at: datetime

    user: UserReadSummary


class AccountCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., max_length=100)
    balance: Decimal = Field(..., decimal_places=2, ge=0)
    description: str | None = Field(None, max_length=255)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if value:
            value = value.strip().lower()

        if not value:
            raise ValueError("Account name cannot be empty")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str | None:
        if value:
            value = value.strip()

        if not value:
            return None  # Equivalent to value = None, then return below

        return value

    @field_validator("balance", mode="before")
    @classmethod
    def round_balance(cls, value: str | int | float | Decimal | None) -> Decimal:
        return round_decimal(value)


class AccountUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., max_length=100)
    description: str | None = Field(None, max_length=255)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if value:
            value = value.strip().lower()

        if not value:
            raise ValueError("Account name cannot be empty")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str | None:
        if value:
            value = value.strip()

        if not value:
            return None  # Equivalent to value = None, then return below

        return value


class AccountReadSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

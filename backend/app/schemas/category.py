from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.enum.transaction_type import TransactionType
from app.schemas.user import UserReadSummary


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: TransactionType
    created_at: datetime
    updated_at: datetime

    user: UserReadSummary


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., max_length=100)
    type: TransactionType = Field(...)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if value:
            value = value.strip().lower()
        if not value:
            raise ValueError("Category name cannot be empty")
        return value

    @field_validator("type", mode="before")
    @classmethod
    def clean_type(cls, value: str) -> str:
        return value.strip().lower()


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., max_length=100)
    type: TransactionType = Field(...)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if value:
            value = value.strip().lower()
        if not value:
            raise ValueError("Category name cannot be empty")
        return value

    @field_validator("type", mode="before")
    @classmethod
    def clean_type(cls, value: str) -> str:
        return value.strip().lower()


class CategoryReadSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: TransactionType

from typing import Annotated

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from uuid import UUID


class UserCreate(BaseModel):
    email: Annotated[str, EmailStr]
    password: str
    name: str

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        v = v.strip().lower()
        return v

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("User's name cannot be empty")
        return v


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: Annotated[str, EmailStr]
    name: str
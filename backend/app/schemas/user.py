from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# TODO: Add field validator ensure password is safe enough
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


class UserLoginForm(BaseModel):
    email: Annotated[str, EmailStr]
    password: str

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        v = v.strip().lower()
        return v
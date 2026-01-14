from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse[T](BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: list[T]

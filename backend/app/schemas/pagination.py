from pydantic import BaseModel


class PaginatedResponse[T](BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: list[T]

from typing import Annotated

from fastapi import Query

from app.core.pagination_settings import pagination_settings as pagination

# Defining the types as reusable Annotated aliases
PageNumber = Annotated[
    int,
    Query(ge=pagination.MIN_PAGE, description="Page number"),
]

PageSize = Annotated[
    int,
    Query(
        ge=pagination.MIN_SIZE,
        le=pagination.MAX_SIZE,
        description="Page size, number of items per page",
    ),
]


class PaginationParams:
    def __init__(
        self,
        page: PageNumber = pagination.DEFAULT_PAGE,
        size: PageSize = pagination.DEFAULT_SIZE,
    ):
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

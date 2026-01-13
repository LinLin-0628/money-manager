from typing import Any

from starlette import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "An application error occurred"
    default_details: dict[str, Any] | None = None

    def __init__(
        self, message: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        self.message = message or self.default_message
        self.details = details if details is not None else self.default_details
        super().__init__(self.message)

from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An application error occurred"

    def __init__(self, message: str | None = None, details: dict | None = None) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(message)


class UserAlreadyExists(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "User already exists"
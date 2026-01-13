from starlette import status

from app.core.exceptions.base import AppException


class UserAlreadyExists(AppException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "User already exists"


class UserNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "User not found"

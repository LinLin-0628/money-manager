from starlette import status

from app.core.exceptions.base import AppException


class DuplicateAccountError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "An account with the given name already exists."

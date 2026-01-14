from starlette import status

from app.core.exceptions.base import AppException


class DuplicateAccountError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "An account with the given name already exists."

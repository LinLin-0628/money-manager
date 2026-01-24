from starlette import status

from app.core.exceptions.base import AppException


class DuplicateCategoryError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "An category with the given name already exists."


class CategoryNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Category not found"


class CategoryMismatchError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Category does not match the transaction type"

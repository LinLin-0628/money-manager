from starlette import status

from app.core.exceptions.base import AppException


class DuplicateBudgetException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "A budget with the same name already exists."


class BudgetInvalidDateError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Budget end date must be after today."


class BudgetNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Budget not found."

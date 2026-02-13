from app.core.exceptions.base import AppException


class TransactionNotFoundError(AppException):
    status_code = 404
    default_message = "Transaction not found"

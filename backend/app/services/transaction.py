import logging
from math import ceil

from sqlalchemy.exc import IntegrityError

from app.api.deps.pagination import PaginationParams
from app.core.exceptions.account import (
    AccountInsufficientBalanceError,
    AccountNotFoundError,
)
from app.core.exceptions.base import AppException
from app.core.exceptions.category import CategoryMismatchError, CategoryNotFoundError
from app.enum.transaction_type import TransactionType
from app.models import Transaction, User
from app.repositories.transaction import TransactionRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.account import AccountService
from app.services.category import CategoryService

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_service: AccountService,
        category_service: CategoryService,
    ):
        self.transaction_repo = transaction_repo
        self.account_service = account_service
        self.category_service = category_service

    def get_all_transactions(
        self, current_user: User, pagination: PaginationParams
    ) -> PaginatedResponse[TransactionRead]:
        logger.info(
            "Fetch all transactions start",
            extra={
                "page": pagination.page,
                "size": pagination.size,
            },
        )

        total = self.transaction_repo.get_total_count(current_user.id)
        categories = self.transaction_repo.get_all_categories(
            current_user.id, pagination.offset, pagination.size
        )
        total_pages = ceil(total / pagination.size) if total > 0 else 1
        items = [TransactionRead.model_validate(cat) for cat in categories]

        logger.info(
            "Fetch all transactions complete",
            extra={
                "total": total,
                "page": pagination.page,
                "size": pagination.size,
                "total_pages": total_pages,
            },
        )

        return PaginatedResponse[TransactionRead](
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=total_pages,
            items=items,
        )

    def create_transaction(
        self, current_user: User, transaction_create_data: TransactionCreate
    ) -> Transaction:
        try:
            account = self.account_service.get_account_by_id(
                current_user, transaction_create_data.account_id
            )
            if not account:
                raise AccountNotFoundError()

            category = self.category_service.get_category_by_id(
                current_user, transaction_create_data.category_id
            )
            if not category:
                raise CategoryNotFoundError()

            if category.type != transaction_create_data.type:
                raise CategoryMismatchError()

            sufficient_balance = self.account_service.has_sufficient_balance(
                account, transaction_create_data.amount
            )

            if (
                transaction_create_data.type == TransactionType.EXPENSE
                and not sufficient_balance
            ):
                raise AccountInsufficientBalanceError()

            new_transaction = self.transaction_repo.create_transaction(
                Transaction(
                    **transaction_create_data.model_dump(),
                    user_id=current_user.id,
                )
            )
            self.account_service.update_balance(
                account,
                transaction_create_data.amount,
                transaction_create_data.type,
            )
            self.transaction_repo.db.commit()
            return new_transaction

        except IntegrityError as e:
            self.transaction_repo.db.rollback()
            raise AppException() from e

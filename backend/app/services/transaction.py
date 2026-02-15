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
from app.core.exceptions.transaction import TransactionNotFoundError
from app.enum.transaction_type import TransactionType
from app.models import Transaction, User
from app.repositories.transaction import TransactionRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.services.account import AccountService
from app.services.category import CategoryService
from app.utils.utils import ensure_uuid

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
        transactions = self.transaction_repo.get_all_transactions(
            current_user.id, pagination.offset, pagination.size
        )
        total_pages = ceil(total / pagination.size) if total > 0 else 1
        items = [TransactionRead.model_validate(txn) for txn in transactions]

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

    def get_transaction_by_id(
        self, current_user: User, transaction_id: int
    ) -> Transaction | None:
        transaction = self.transaction_repo.get_transaction_by_id(
            transaction_id, ensure_uuid(current_user.id)
        )
        return transaction

    # TODO: Update transaction service
    def update_transaction(
        self,
        current_user: User,
        transaction_id: int,
        transaction_update_data: TransactionUpdate,
    ) -> Transaction:
        try:
            transaction = self.get_transaction_by_id(current_user, transaction_id)
            if not transaction:
                raise TransactionNotFoundError()

            old_account = self.account_service.get_account_by_id(
                current_user, transaction.account_id
            )
            if not old_account:
                raise AccountNotFoundError()

            # ---

            new_amount = transaction_update_data.amount
            new_type = transaction_update_data.type
            new_account_id = transaction_update_data.account_id
            new_category_id = transaction_update_data.category_id

            new_account = self.account_service.get_account_by_id(
                current_user, new_account_id
            )
            if not new_account:
                raise AccountNotFoundError()

            new_category = self.category_service.get_category_by_id(
                current_user, new_category_id
            )
            if not new_category:
                raise CategoryNotFoundError()

            if new_category.type != transaction_update_data.type:
                raise CategoryMismatchError()

            self.account_service.reverse_balance(
                old_account, transaction.amount, transaction.type
            )

            sufficient_balance = self.account_service.has_sufficient_balance(
                new_account, new_amount
            )

            if new_type == TransactionType.EXPENSE and not sufficient_balance:
                raise AccountInsufficientBalanceError()

            for field, value in transaction_update_data.model_dump().items():
                setattr(transaction, field, value)

            self.account_service.update_balance(new_account, new_amount, new_type)

            self.transaction_repo.db.commit()

            return transaction

        except IntegrityError as e:
            self.transaction_repo.db.rollback()
            raise AppException() from e

    def delete_transaction(self, current_user: User, transaction_id: int) -> None:
        try:
            transaction = self.get_transaction_by_id(current_user, transaction_id)

            if not transaction:
                raise AccountNotFoundError()

            account = self.account_service.get_account_by_id(
                current_user, transaction.account_id
            )
            if not account:
                raise AccountNotFoundError()

            # Revert the balance change
            self.account_service.reverse_balance(
                account, transaction.amount, transaction.type
            )

            self.transaction_repo.delete_transaction(transaction)

            self.transaction_repo.db.commit()

        except IntegrityError as e:
            self.transaction_repo.db.rollback()
            raise AppException() from e

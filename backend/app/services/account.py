import logging
from decimal import Decimal
from math import ceil

from sqlalchemy.exc import IntegrityError

from app.api.deps.pagination import PaginationParams
from app.core.exceptions.account import AccountNotFoundError, DuplicateAccountError
from app.core.exceptions.base import AppException
from app.enum.transaction_type import TransactionType
from app.models import Account, User
from app.repositories.account import AccountRepository
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.schemas.pagination import PaginatedResponse
from app.utils.utils import ensure_uuid

logger = logging.getLogger(__name__)


class AccountService:
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def get_all_accounts(
        self, current_user: User, pagination: PaginationParams
    ) -> PaginatedResponse[AccountRead]:
        logger.info(
            "Fetch all accounts start",
            extra={
                "page": pagination.page,
                "size": pagination.size,
            },
        )

        total = self.account_repo.get_total_count(current_user.id)
        accounts = self.account_repo.get_all_accounts(
            current_user.id, pagination.offset, pagination.size
        )
        total_pages = ceil(total / pagination.size) if total > 0 else 1
        items = [AccountRead.model_validate(acc) for acc in accounts]

        logger.info(
            "Fetch all accounts complete",
            extra={
                "total": total,
                "page": pagination.page,
                "size": pagination.size,
                "total_pages": total_pages,
            },
        )

        return PaginatedResponse[AccountRead](
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=total_pages,
            items=items,
        )

    def create_account(
        self, current_user: User, account_create_data: AccountCreate
    ) -> Account:
        logger.info(
            "Create account start",
        )

        try:
            new_account = self.account_repo.create_account(
                Account(**account_create_data.model_dump(), user_id=current_user.id)
            )
            self.account_repo.db.commit()

            logger.info(
                "Create account complete",
            )

            return new_account

        except IntegrityError as e:
            self.account_repo.db.rollback()

            logger.warning(
                "Create account failed - duplicate",
            )

            raise DuplicateAccountError(
                details={"name": account_create_data.name}
            ) from e

    def get_account_by_id(self, current_user: User, account_id: int) -> Account | None:
        logger.info(
            "Fetch account by id start",
            extra={"account_id": account_id, "user_id": current_user.id},
        )

        account = self.account_repo.get_account_by_id(
            account_id, ensure_uuid(current_user.id)
        )

        logger.info(
            "Fetch account by id complete",
            extra={
                "account_id": account_id,
                "user_id": current_user.id,
                "found": account is not None,
            },
        )

        return account

    def update_account(
        self, current_user: User, account_id: int, account_update_data: AccountUpdate
    ) -> Account:
        logger.info(
            "Update account start",
            extra={"account_id": account_id, "user_id": current_user.id},
        )

        try:
            account = self.get_account_by_id(current_user, account_id)

            if not account:
                raise AccountNotFoundError()

            for field, value in account_update_data.model_dump().items():
                setattr(account, field, value)

            updated_account = self.account_repo.update_account(updated_account=account)
            self.account_repo.db.commit()

            return updated_account
        except IntegrityError:
            self.account_repo.db.rollback()
            logger.exception("Update account field")
            raise

    def delete_account(self, current_user: User, account_id: int) -> None:
        logger.info(
            "Delete account start",
            extra={"account_id": account_id, "user_id": current_user.id},
        )

        try:
            account = self.get_account_by_id(current_user, account_id)

            if not account:
                raise AccountNotFoundError()

            self.account_repo.delete_account(account)
            self.account_repo.db.commit()

            logger.info(
                "Delete account complete",
                extra={"account_id": account_id, "user_id": current_user.id},
            )

        except IntegrityError:
            self.account_repo.db.rollback()
            logger.exception("Delete account field")
            raise

    def has_sufficient_balance(self, account: Account, amount: Decimal) -> bool:
        return account.balance >= amount

    def update_balance(
        self, account: Account, amount: Decimal, transaction_type: TransactionType
    ) -> Account:
        try:
            if transaction_type == TransactionType.INCOME:
                account.balance += amount
            elif transaction_type == TransactionType.EXPENSE:
                account.balance -= amount
            else:
                raise AppException(
                    message=f"Unknown transaction type: {transaction_type}"
                )

            self.account_repo.db.commit()
            self.account_repo.db.refresh(account)
            return account

        except IntegrityError as e:
            self.account_repo.db.rollback()
            raise AppException() from e

    def reverse_balance(
        self, account: Account, amount: Decimal, transaction_type: TransactionType
    ) -> Account:
        try:
            if transaction_type == TransactionType.INCOME:
                account.balance -= amount
            elif transaction_type == TransactionType.EXPENSE:
                account.balance += amount
            else:
                raise AppException(
                    message=f"Unknown transaction type: {transaction_type}"
                )

            self.account_repo.db.commit()
            self.account_repo.db.refresh(account)
            return account

        except IntegrityError as e:
            self.account_repo.db.rollback()
            raise AppException() from e

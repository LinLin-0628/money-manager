import logging
from math import ceil

from sqlalchemy.exc import IntegrityError

from app.api.deps.pagination import PaginationParams
from app.core.exceptions.account import DuplicateAccountError
from app.models import Account, User
from app.repositories.account import AccountRepository
from app.schemas.account import AccountCreate, AccountRead
from app.schemas.pagination import PaginatedResponse

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

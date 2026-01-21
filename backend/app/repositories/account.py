from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.account import Account


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_count(self, user_id: UUID) -> int:
        stmt = select(func.count(Account.id)).where(Account.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_all_accounts(
        self, user_id: UUID, offset: int, limit: int
    ) -> Sequence[Account]:
        stmt = (
            select(Account)
            .where(Account.user_id == user_id)
            .options(selectinload(Account.user))
            .order_by(Account.id)
            .offset(offset)
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def create_account(self, new_account: Account) -> Account:
        """
        Persist a new Account to the database and refresh it with the current database state.
        
        Parameters:
            new_account (Account): The Account instance to persist.
        
        Returns:
            Account: The persisted `new_account` instance refreshed with the latest database state.
        """
        self.db.add(new_account)
        self.db.flush()
        self.db.refresh(new_account)
        return new_account

    def get_account_by_id(self, account_id: int, user_id: UUID) -> Account | None:
        """
        Retrieve the Account with the given id scoped to the specified user.
        
        Returns:
            Account or None: The matching Account if found for the provided user_id, `None` otherwise.
        """
        stmt = select(Account).where(
            Account.id == account_id, Account.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def update_account(self, updated_account: Account) -> Account:
        """
        Persist changes of an Account instance and synchronize it with the database.
        
        Parameters:
            updated_account (Account): Account instance containing the modifications to persist.
        
        Returns:
            Account: The same Account instance refreshed with the latest database state.
        """
        self.db.add(updated_account)
        self.db.flush()
        self.db.refresh(updated_account)
        return updated_account

    def delete_account(self, account: Account) -> None:
        """
        Delete an Account instance from the current database session.
        
        Removes the provided Account from the session and flushes pending changes so the deletion is applied to the database.
        
        Parameters:
            account (Account): The Account instance to delete.
        """
        self.db.delete(account)
        self.db.flush()
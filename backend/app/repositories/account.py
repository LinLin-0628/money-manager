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
        self.db.add(new_account)
        self.db.flush()
        self.db.refresh(new_account)
        return new_account

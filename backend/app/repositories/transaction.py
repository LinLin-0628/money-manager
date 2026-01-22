from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_count(self, user_id: UUID) -> int:
        stmt = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_all_categories(
        self, user_id: UUID, offset: int, size: int
    ) -> Sequence[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .options(
                selectinload(Transaction.account),
                selectinload(Transaction.category),
                selectinload(Transaction.user),
            )
            .order_by(Transaction.id)
            .offset(offset)
            .limit(size)
        )
        return self.db.execute(stmt).scalars().all()

    def create_transaction(self, new_transaction: Transaction) -> Transaction:
        self.db.add(new_transaction)
        self.db.flush()
        self.db.refresh(new_transaction)
        return new_transaction

    def get_transaction_by_id(
        self, transaction_id: int, user_id: UUID
    ) -> Transaction | None:
        stmt = select(Transaction).where(
            Transaction.id == transaction_id, Transaction.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def delete_transaction(self, transaction: Transaction) -> None:
        self.db.delete(transaction)
        self.db.flush()

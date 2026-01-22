from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_count(self, user_id: UUID):
        stmt = select(func.count(Category.id)).where(Category.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_all_categories(
        self, user_id: UUID, offset: int, size: int
    ) -> Sequence[Category]:
        stmt = (
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.id)
            .offset(offset)
            .limit(size)
        )
        return self.db.execute(stmt).scalars().all()

    def create_category(self, new_cat: Category) -> Category:
        self.db.add(new_cat)
        self.db.flush()
        self.db.refresh(new_cat)
        return new_cat

    def get_category_by_id(self, user_id: UUID, category_id: int) -> Category:
        stmt = select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def delete_category(self, category: Category) -> None:
        self.db.delete(category)
        self.db.flush()

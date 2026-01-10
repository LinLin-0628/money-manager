from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_user_id(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)

        return user

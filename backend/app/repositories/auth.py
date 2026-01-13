from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import RefreshToken


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.flush()
        self.db.refresh(token)
        return token

    def revoke_all_refresh_tokens(self, user_id: UUID, now: datetime) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        self.db.execute(stmt)

    def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke_token_by_id(self, token_id: int, now: datetime) -> None:
        token = self.db.get(RefreshToken, token_id)
        if token and token.revoked_at is None:
            token.revoked_at = now
            self.db.flush()

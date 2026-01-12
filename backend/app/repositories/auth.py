from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import update
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

    def revoke_all_refresh_tokens(self, user_id: UUID) -> None:
        now = datetime.now(UTC)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        self.db.execute(stmt)

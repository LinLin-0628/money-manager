from sqlalchemy import Integer, String, DateTime, Index, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = mapped_column(Integer, primary_key=True, index=True)
    token_hash = mapped_column(String, unique=True, nullable=False, index=True)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    family_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, index=True)

    expires_at = mapped_column(DateTime(timezone=True), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at = mapped_column(DateTime(timezone=True), nullable=True) # Default already null

    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("ix_user_revoked", "user_id", "revoked_at"),
        Index("ix_user_active", "user_id", "revoked_at", "expires_at"),
    )

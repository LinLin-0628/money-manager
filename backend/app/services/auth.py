from uuid import UUID

from app.core.exceptions import AppException, InvalidCredentials, UserNotFound
from app.core.security import (
    verify_password,
    generate_family_id,
    generate_access_token,
    generate_refresh_token,
    hash_token,
)
from app.enum.user import SensitiveField
from app.models import RefreshToken
from app.repositories.auth import AuthRepository
from datetime import timezone, datetime, timedelta
from app.core.settings import settings
from app.schemas.auth import TokenPair

from app.services.user import UserService
import logging

from app.utils.utils import anonymize_sensitive_data

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        auth_repo: AuthRepository,
        user_service: UserService,
    ):
        self.auth_repo = auth_repo
        self.user_service = user_service

    def login_user(self, email: str, password: str) -> TokenPair:

        logger.info("Login user start", extra={"email": anonymize_sensitive_data(email, SensitiveField.EMAIL)})

        user = self.user_service.get_user_by_email(email)
        if not user:
            raise UserNotFound()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        try:
            refresh_token_family_id = generate_family_id()
            now = datetime.now(timezone.utc)
            access_token_expire = now + timedelta(
                minutes=settings.access_token_expire_minutes
            )
            refresh_token_expire = now + timedelta(
                days=settings.refresh_token_expire_days
            )

            access_token = generate_access_token(
                user.id, iat=now, exp=access_token_expire
            )
            refresh_token = generate_refresh_token(
                user.id, refresh_token_family_id, iat=now, exp=refresh_token_expire
            )

            refresh_token_hash = hash_token(refresh_token)

            self.auth_repo.revoke_all_refresh_tokens(user.id)

            self.auth_repo.create_refresh_token(
                RefreshToken(
                    token_hash=refresh_token_hash,
                    user_id=user.id,
                    family_id=refresh_token_family_id,
                    expires_at=refresh_token_expire,
                    created_at=now,
                )
            )

            self.auth_repo.db.commit()

            logger.info("Login user complete", extra={"email": anonymize_sensitive_data(email, SensitiveField.EMAIL), "logged_in": True} )

            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
            )


        except Exception as e:
            self.auth_repo.db.rollback()
            logger.exception("Login failed")
            raise AppException() from e

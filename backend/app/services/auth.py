import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.core.exceptions import (
    AppException,
    InvalidCredentials,
    InvalidRefreshToken,
    InvalidTokenSignature,
    MalformedTokenError,
    RefreshTokenExpired,
    TokenExpired,
    UserNotFound,
)
from app.core.security import (
    decode_refresh_token,
    generate_access_token,
    generate_family_id,
    generate_refresh_token,
    hash_token,
    verify_password,
)
from app.core.settings import settings
from app.enum.user import SensitiveField
from app.models import RefreshToken
from app.repositories.auth import AuthRepository
from app.schemas.auth import TokenPair
from app.services.user import UserService
from app.utils.utils import anonymize_sensitive_data, ensure_uuid

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
        logger.info(
            "Login user start",
            extra={"email": anonymize_sensitive_data(email, SensitiveField.EMAIL)},
        )

        user = self.user_service.get_user_by_email(email)
        if not user:
            raise UserNotFound()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        try:
            refresh_token_family_id = generate_family_id()
            now = datetime.now(UTC)
            access_token_expire = now + timedelta(
                minutes=settings.access_token_expire_minutes
            )
            refresh_token_expire = now + timedelta(
                days=settings.refresh_token_expire_days
            )
            family_expires_at = refresh_token_expire

            access_token = generate_access_token(
                user.id, iat=now, exp=access_token_expire
            )
            refresh_token = generate_refresh_token(
                user.id,
                refresh_token_family_id,
                iat=now,
                exp=refresh_token_expire,
                family_expires_at=family_expires_at,
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
                    family_expires_at=family_expires_at,
                )
            )

            self.auth_repo.db.commit()

            logger.info(
                "Login user complete",
                extra={
                    "email": anonymize_sensitive_data(email, SensitiveField.EMAIL),
                    "logged_in": True,
                },
            )

            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except Exception as e:
            self.auth_repo.db.rollback()
            logger.exception(
                "Login failed",
                extra={
                    "detail": str(e),
                },
            )
            raise AppException() from e

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        # verify the refresh token
        # - verify signature, exp
        # - check in db
        #   - token hash exist
        #   - revoked_at = null

        # if not found --> 401 --> logout
        # FOUND --> generate new tokens pair
        # for the refresh token in db, replace with new info

        logger.info("Refresh tokens start")

        try:
            refresh_token_payload = decode_refresh_token(refresh_token)
        except TokenExpired as e:
            raise RefreshTokenExpired() from e
        except MalformedTokenError:
            raise
        except InvalidTokenSignature:
            raise

        if refresh_token_payload.get("type") != "refresh":
            raise MalformedTokenError("Token is not refresh token")

        # family_id -> UUID
        family_id_raw = refresh_token_payload.get("family_id")
        if isinstance(family_id_raw, (str, UUID)):
            family_id = ensure_uuid(family_id_raw)
        else:
            raise MalformedTokenError("Refresh token family_id is missing")

        # family_expires_at -> numeric timestamp -> datetime
        family_expires_at_ts = refresh_token_payload.get("family_expires_at")
        if not isinstance(family_expires_at_ts, (int, float)):
            raise MalformedTokenError(
                "Refresh token family_expires_at is missing or invalid"
            )
        family_expires_at = datetime.fromtimestamp(float(family_expires_at_ts), tz=UTC)

        # subject -> UUID
        user_id_raw = refresh_token_payload.get("sub")
        if isinstance(user_id_raw, (str, UUID)):
            user_id = ensure_uuid(user_id_raw)
        else:
            raise MalformedTokenError("Token subject is missing or invalid")

        # Check in db
        token_in_db = self.auth_repo.get_refresh_token_by_hash(
            hash_token(refresh_token)
        )
        if not token_in_db or token_in_db.revoked_at is not None:
            raise InvalidRefreshToken()

        if token_in_db.family_expires_at < datetime.now(UTC):
            self._revoke_token(token_in_db.id)
            raise RefreshTokenExpired()

        now = datetime.now(UTC)
        access_token_expire = now + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        refresh_token_expire = min(
            (now + timedelta(days=settings.refresh_token_expire_days)),
            family_expires_at,
        )

        try:
            access_token = generate_access_token(
                user_id, iat=now, exp=access_token_expire
            )
            new_refresh_token = generate_refresh_token(
                user_id,
                family_id,
                iat=now,
                exp=refresh_token_expire,
                family_expires_at=family_expires_at,
            )

            new_refresh_token_hash = hash_token(new_refresh_token)
            # revoke the old token
            self._revoke_token(token_in_db.id)

            # Create new record for the new token
            self.auth_repo.create_refresh_token(
                RefreshToken(
                    token_hash=new_refresh_token_hash,
                    user_id=user_id,
                    family_id=family_id,
                    expires_at=refresh_token_expire,
                    created_at=now,
                    family_expires_at=family_expires_at,
                )
            )

            self.auth_repo.db.commit()

            logger.info(
                "Refresh tokens complete",
                extra={
                    "user_id": str(user_id),
                    "refreshed": True,
                },
            )

            return TokenPair(
                access_token=access_token,
                refresh_token=new_refresh_token,
            )
        except Exception as e:
            self.auth_repo.db.rollback()
            logger.exception(
                "Error while refreshing tokens",
                extra={
                    "user_id": str(user_id),
                    "family_id": str(family_id),
                },
            )
            raise AppException() from e

    def _revoke_token(self, refresh_token_id: int) -> None:
        now = datetime.now(UTC)
        self.auth_repo.revoke_token_by_id(refresh_token_id, now)

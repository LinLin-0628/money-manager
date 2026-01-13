import logging
import uuid

from sqlalchemy.exc import IntegrityError

from app.core.exceptions.user import UserAlreadyExists
from app.core.security import hash_password
from app.enum.user import SensitiveField
from app.models import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.utils.utils import anonymize_sensitive_data, ensure_uuid

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def register_user(self, user_create_data: UserCreate) -> User:
        logger.info(
            "Register user start",
            extra={
                "user_create_data": {
                    "name": anonymize_sensitive_data(
                        user_create_data.name, SensitiveField.NAME
                    ),
                    "email": anonymize_sensitive_data(
                        user_create_data.email, SensitiveField.EMAIL
                    ),
                },
            },
        )

        try:
            new_user = User(
                email=user_create_data.email,
                hashed_password=hash_password(user_create_data.password),
                name=user_create_data.name,
            )

            user = self.user_repo.create_user(new_user)
            self.user_repo.db.commit()

            logger.info(
                "Register user complete",
                extra={
                    "user_create_data": {
                        "name": anonymize_sensitive_data(
                            user_create_data.name, SensitiveField.NAME
                        ),
                        "email": anonymize_sensitive_data(
                            user_create_data.email, SensitiveField.EMAIL
                        ),
                    },
                },
            )

            return user
        except IntegrityError as e:
            self.user_repo.db.rollback()

            logger.warning(
                "Register user failed - email already exists",
                extra={
                    "user_create_data": {
                        "name": anonymize_sensitive_data(
                            user_create_data.name, SensitiveField.NAME
                        ),
                        "email": anonymize_sensitive_data(
                            user_create_data.email, SensitiveField.EMAIL
                        ),
                    },
                },
            )

            raise UserAlreadyExists() from e

    def get_user_by_email(self, email: str) -> User | None:
        logger.info(
            "Get user by email start",
            extra={"email": anonymize_sensitive_data(email, SensitiveField.EMAIL)},
        )

        user = self.user_repo.get_user_by_email(email)

        logger.info(
            "Get user by email complete",
            extra={
                "email": anonymize_sensitive_data(email, SensitiveField.EMAIL),
                "user_id": user.id if user else None,
                "found": user is not None,
            },
        )

        return user

    def get_user_by_id(self, user_id: str | uuid.UUID) -> User | None:
        logger.info(
            "Get user by ID start",
            extra={"user_id": str(user_id)},
        )
        user = self.user_repo.get_by_user_id(ensure_uuid(user_id))

        logger.info(
            "Get user by ID complete",
            extra={
                "user_id": str(user_id),
                "found": user is not None,
            },
        )

        return user

from sqlalchemy.exc import IntegrityError
import logging
from fastapi import Request

from app.core.exceptions import UserAlreadyExists, AppException
from app.models import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.utils.utils import get_request_id

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository, request: Request):
        self.user_repo = user_repo
        self.request = request


    def register_user(self, user_create_data: UserCreate) -> User:
        request_id = get_request_id(self.request)
        logger.info("Register user start", extra={
            "request_id": request_id,
            "user_create_data": {
                "email": user_create_data.email,
                "name": user_create_data.name,
            }
        })


        try:
            new_user = User(
                email=user_create_data.email,
                hashed_password=hash_password(user_create_data.password),
                name=user_create_data.name,
            )

            user = self.user_repo.create_user(new_user)
            self.user_repo.db.commit()

            logger.info("Register user complete", extra={
                "request_id": request_id,
                "user_create_data": {
                    "email": user_create_data.email,
                    "name": user_create_data.name,
                }
            })

            return user
        except IntegrityError as e:
            self.user_repo.db.rollback()

            logger.info("Register user failed - email already exist", extra={
                "request_id": request_id,
                "user_create_data": {
                    "email": user_create_data.email,
                    "name": user_create_data.name,
                }
            })

            raise UserAlreadyExists("User with this email already exists")from e

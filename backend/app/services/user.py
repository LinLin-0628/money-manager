from sqlalchemy.exc import IntegrityError

from app.core.exceptions import UserAlreadyExists, AppException
from app.models import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.core.security import hash_password


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo


    def register_user(self, user_create_data: UserCreate) -> User:
        try:
            new_user = User(
                email=user_create_data.email,
                hashed_password=hash_password(user_create_data.password),
                name=user_create_data.name,
            )

            user = self.user_repo.create_user(new_user)
            self.user_repo.db.commit()
            return user
        except IntegrityError as e:
            self.user_repo.db.rollback()
            raise UserAlreadyExists("User with this email already exists")from e

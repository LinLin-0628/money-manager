from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.db.database import get_db
from app.repositories.user import UserRepository
from app.repositories.auth import AuthRepository
from app.services.user import UserService
from app.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/verify")


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    auth_repo = AuthRepository(db)
    return AuthService(
        auth_repo,
        user_service,
    )

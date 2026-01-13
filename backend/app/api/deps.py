from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions.auth import (
    AccessTokenExpired,
    InvalidAccessTokenSignature,
    InvalidTokenSignature,
    MalformedAccessTokenError,
    MalformedTokenError,
    TokenExpired,
)
from app.core.exceptions.user import UserNotFound
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.repositories.auth import AuthRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.user import UserService
from app.utils.utils import ensure_uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


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


def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    try:
        payload = decode_access_token(access_token)
    except TokenExpired as e:
        raise AccessTokenExpired(
            details={"code": "token_expired", "expired": True}
        ) from e
    except MalformedTokenError as e:
        raise MalformedAccessTokenError() from e
    except InvalidTokenSignature as e:
        raise InvalidAccessTokenSignature() from e

    if payload.get("type") != "access":
        raise InvalidAccessTokenSignature("Token is not access token")

    user_id_raw = payload.get("sub")
    if isinstance(user_id_raw, (str, UUID)):
        user_id = ensure_uuid(user_id_raw)
    else:
        raise MalformedAccessTokenError("Token subject is missing or invalid")

    user = user_service.get_user_by_id(user_id)

    if not user:
        raise UserNotFound()

    return user

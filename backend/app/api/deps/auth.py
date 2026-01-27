from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.api.deps.common import get_user_service
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
from app.models import User
from app.services.user import UserService
from app.utils.utils import ensure_uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
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
    try:
        user_id = ensure_uuid(user_id_raw)
    except (ValueError, AttributeError, TypeError) as e:
        raise MalformedAccessTokenError("Token subject is missing or invalid") from e

    user = user_service.get_user_by_id(user_id)

    if not user:
        raise UserNotFound()

    return user

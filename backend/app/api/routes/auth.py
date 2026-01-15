import logging
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps.common import get_auth_service
from app.core.exceptions.auth import InvalidRefreshToken
from app.core.settings import settings
from app.schemas.auth import AccessToken
from app.schemas.user import UserLoginForm
from app.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=AccessToken)
def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AccessToken:
    login_credentials = UserLoginForm(
        email=form_data.username, password=form_data.password
    )
    tokens = auth_service.login_user(
        login_credentials.email, login_credentials.password
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return AccessToken(access_token=tokens.access_token)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=AccessToken)
def refresh_tokens(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AccessToken:
    if not refresh_token:
        raise InvalidRefreshToken(
            "refresh_token cookie is missing",
            details={"code": "invalid_refresh_token", "logout": True},
        )

    tokens = auth_service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return AccessToken(access_token=tokens.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> None:
    if not refresh_token:
        raise InvalidRefreshToken(
            "refresh_token cookie is missing",
            details={"code": "invalid_refresh_token", "logout": True},
        )

    auth_service.logout_user(refresh_token)

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="strict",
        secure=True,
    )

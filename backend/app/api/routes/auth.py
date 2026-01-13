import logging

from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service
from app.core.settings import settings
from app.schemas.auth import AccessToken
from app.schemas.user import UserLoginForm
from app.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=AccessToken)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
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
    refresh_token: str | None = Cookie(default=None),
    auth_service: AuthService = Depends(get_auth_service),
):
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

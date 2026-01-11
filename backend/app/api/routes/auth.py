from fastapi import APIRouter, Request, Response, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from app.api.deps import oauth2_scheme, get_auth_service
from app.schemas.auth import TokenPair, AccessToken
from app.schemas.user import UserLoginForm
from app.core.settings import settings
from app.services.auth import AuthService
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=AccessToken)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    login_credentials = UserLoginForm(email=form_data.username, password=form_data.password)
    tokens = auth_service.login_user(login_credentials.email, login_credentials.password)

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return AccessToken(access_token=tokens.access_token)



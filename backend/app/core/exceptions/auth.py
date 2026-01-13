from starlette import status

from app.core.exceptions.base import AppException


# ----------------------------------------------
# Token Expired Errors
# ----------------------------------------------
class TokenExpired(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Token has expired"


class AccessTokenExpired(TokenExpired):
    default_message = "Access token has expired"


class RefreshTokenExpired(TokenExpired):
    default_message = "Refresh token has expired"


# ----------------------------------------------
# Invalid Signature Errors
# ----------------------------------------------
class InvalidTokenSignature(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Invalid token signature"


class InvalidAccessTokenSignature(InvalidTokenSignature):
    default_message = "Invalid access token signature"


class InvalidRefreshTokenSignature(InvalidTokenSignature):
    default_message = "Invalid refresh token signature"


# ----------------------------------------------
# Invalid Format Errors (Malformed Token)
# ----------------------------------------------
class MalformedTokenError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Malformed token"


class MalformedAccessTokenError(MalformedTokenError):
    default_message = "Malformed access token"


class MalformedRefreshTokenError(MalformedTokenError):
    default_message = "Malformed refresh token"


class InvalidRefreshToken(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Invalid refresh token"


class InvalidCredentials(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Invalid email or password"

from typing import Any

from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An application error occurred"

    def __init__(
        self, message: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class UserAlreadyExists(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "User already exists"


class InvalidCredentials(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid email or password"


class RefreshTokenRevoked(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Refresh token has been revoked"


class RefreshTokenReuseDetected(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Suspicious session activity detected"


class UserNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found"


class MalformedTokenError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Malformed token"


class InvalidTokenSignature(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid token signature"


class InvalidAccessTokenSignature(InvalidTokenSignature):
    message = "Invalid access token signature"


class TokenExpired(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Token has expired"


class AccessTokenExpired(TokenExpired):
    message = "Access token has expired"


class RefreshTokenExpired(TokenExpired):
    message = "Refresh token has expired"


class InvalidRefreshToken(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid refresh token"

from fastapi import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An application error occurred"

    def __init__(self, message: str | None = None, details: dict | None = None) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class UserAlreadyExists(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "User already exists"


class InvalidCredentials(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid email or password"


class AccessTokenExpired(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Access token has expired"


class RefreshTokenExpired(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Refresh token has expired"


class RefreshTokenRevoked(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Refresh token has been revoked"


class RefreshTokenReuseDetected(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Suspicious session activity detected"


class UserNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "User not found"

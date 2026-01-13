import hashlib
import hmac
import uuid
from datetime import datetime
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.exceptions.auth import (
    InvalidTokenSignature,
    MalformedTokenError,
    TokenExpired,
)
from app.core.settings import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password

    Args:
        password: Password string in plaintext

    Returns:
        str: Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a hashed password

    Args:
        password: Password in plaintext
        hashed: Hashed password string

    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(password, hashed)


def hash_token(token: str) -> str:
    """
    Hash a token using HMAC with SHA-256

    Args:
        token: Token string to be hashed

    Returns:
        str: Hashed token string
    """
    return hmac.new(
        settings.refresh_token_hmac_secret.get_secret_value().encode(),
        token.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_token(token: str, hashed: str) -> bool:
    """
    Verify a token against its hashed value

    Args:
        token: token string
        hashed: hashed token string

    Returns:
        bool: True if the token string matches the hash, False otherwise
    """
    actual_hash = hash_token(token)
    return hmac.compare_digest(actual_hash, hashed)


def generate_family_id() -> uuid.UUID:
    """
    Generate unique family ID for a token rotation chain

    Returns:
        uuid.UUID: A new UUID4 family ID
    """
    return uuid.uuid4()


def generate_access_token(user_id: uuid.UUID, iat: datetime, exp: datetime) -> str:
    """
    Create and return an JWT access token

    Args:
        user_id (uuid.UUID): The ID of the user
        iat (datetime): Issued at time
        exp (datetime): Expiration time

    Returns:
        str: A JWT access token string (encoded)
    """
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.access_token_secret.get_secret_value(),
        algorithm=settings.algorithm,
    )


def generate_refresh_token(
    user_id: uuid.UUID,
    family_id: uuid.UUID,
    iat: datetime,
    exp: datetime,
    family_expires_at: datetime,
) -> str:
    """
    Create and return an JWT refresh token

    Args:
        user_id (uuid.UUID): The ID of the user
        family_id (uuid.UUID): The family id of refresh token
        iat (datetime): Issued at time
        exp (datetime): Expiration time
        family_expires_at (datetime): Family expiration time

    Returns:
        str: A JWT refresh token string (encoded)
    """

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "family_id": str(family_id),
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
        "family_expires_at": int(family_expires_at.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.refresh_token_secret.get_secret_value(),
        algorithm=settings.algorithm,
    )


def _decode_token(token: str, secret: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token

    Args:
        token (str): Token string to be decoded
        secret (str): Secret key used to verify the signature of the token

    Returns:
        dict[str, Any]: Decoded token payload

    Raises:
        TokenExpired: If the token has expired
        InvalidTokenSignature: If the token signature is invalid
        MalformedTokenError: If the token is malformed (invalid format)
    """

    try:
        return jwt.decode(
            token,
            secret,
            algorithms=[settings.algorithm],
            options={"require_sub": True, "require_iat": True, "require_exp": True},
        )
    except ExpiredSignatureError as e:
        raise TokenExpired() from e

    except JWTError as e:
        msg = str(e)
        if "Signature verification failed" in msg:
            raise InvalidTokenSignature() from e
        elif "missing required key" in msg:
            raise MalformedTokenError(msg) from e
        else:
            raise MalformedTokenError() from e


def decode_access_token(access_token: str) -> dict[str, Any]:
    """
    Decode and validate an access token

    Args:
        access_token (str): Access token string to be decoded

    Returns:
        dict[str, Any]: Decoded token payload
    """
    secret = settings.access_token_secret.get_secret_value()
    return _decode_token(access_token, secret)


def decode_refresh_token(refresh_token: str) -> dict[str, Any]:
    """
    Decode and validate a refresh token

    Args:
        refresh_token (str): Refresh token string to be decoded

    Returns:
        dict[str, Any]: Decoded token payload
    """
    secret = settings.refresh_token_secret.get_secret_value()
    return _decode_token(refresh_token, secret)

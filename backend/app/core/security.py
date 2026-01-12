import hashlib
import hmac
import uuid
from datetime import datetime
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.settings import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def hash_token(token: str) -> str:
    return hmac.new(
        settings.refresh_token_hmac_secret.get_secret_value().encode(),
        token.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_token(token: str, hashed: str) -> bool:
    actual_hash = hash_token(token)
    return hmac.compare_digest(actual_hash, hashed)


def generate_family_id() -> uuid.UUID:
    """Generate unique family ID for token rotation chain"""
    return uuid.uuid4()


def generate_access_token(user_id: uuid.UUID, iat: datetime, exp: datetime) -> str:
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
    user_id: uuid.UUID, family_id: uuid.UUID, iat: datetime, exp: datetime
) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "family_id": str(family_id),
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.refresh_token_secret.get_secret_value(),
        algorithm=settings.algorithm,
    )


def _decode_token(token: str, secret: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        return None


def decode_access_token(access_token: str) -> dict[str, Any] | None:
    secret = settings.access_token_secret.get_secret_value()
    return _decode_token(access_token, secret)


def decode_refresh_token(refresh_token: str) -> dict[str, Any] | None:
    secret = settings.refresh_token_secret.get_secret_value()
    return _decode_token(refresh_token, secret)

from datetime import timezone, datetime, timedelta
from uuid import UUID

from passlib.context import CryptContext
import uuid
from jose import JWTError, jwt

from app.core.settings import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def hash_token(token: str) -> str:
    return pwd_context.hash(token)


def verify_token(token: str, hashed: str) -> bool:
    return pwd_context.verify(token, hashed)


def generate_family_id() -> UUID:
    """Generate unique family ID for token rotation chain"""
    return uuid.uuid4()


def generate_access_token(user_id: UUID, iat: datetime, exp: datetime):
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
    user_id: UUID, family_id: UUID, iat: datetime, exp: datetime
):
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


def _decode_token(token: str, secret: str):
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        return None


def decode_access_token(access_token: str):
    secret = settings.access_token_secret.get_secret_value()
    return _decode_token(access_token, secret)


def decode_refresh_token(refresh_token: str):
    secret = settings.refresh_token_secret.get_secret_value()
    return _decode_token(refresh_token, secret)
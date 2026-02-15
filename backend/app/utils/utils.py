import hashlib
import hmac
import uuid
from datetime import UTC, datetime

from app.core.settings import settings
from app.enum.user import SensitiveField

CASE_INSENSITIVE_FIELDS = [SensitiveField.EMAIL]


def anonymize_sensitive_data(
    data: str, field: SensitiveField | None = None, length: int = 12
) -> str:
    if not data:
        return "none"

    normalized = data
    if field in CASE_INSENSITIVE_FIELDS:
        normalized = data.lower()

    secret_key = settings.logging_hmac_secret.get_secret_value()
    hashed = hmac.new(
        key=secret_key.encode(),
        msg=normalized.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hashed[:length]


def ensure_uuid(val: str | uuid.UUID) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(val)


def get_current_time() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)

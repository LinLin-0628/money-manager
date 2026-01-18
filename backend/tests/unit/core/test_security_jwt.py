import uuid
from datetime import UTC, datetime, timedelta

import pytest
from freezegun import freeze_time

from app.core.exceptions.auth import (
    InvalidTokenSignature,
    MalformedTokenError,
    TokenExpired,
)
from app.core.security import (
    _decode_token,
    decode_access_token,
    decode_refresh_token,
    generate_access_token,
    generate_family_id,
    generate_refresh_token,
)

pytestmark = pytest.mark.unit

# Constants for testing
USER_ID = uuid.uuid4()
FAMILY_ID = uuid.uuid4()
SECRET_ACCESS = "test-access-secret"
SECRET_REFRESH = "test-refresh-secret"


def test_generate_family_id_returns_uuid():
    """
    Ensure that generate_family_id() returns a valid UUID object.
    This verifies that the function produces an instance of uuid.UUID.
    """
    family_id = generate_family_id()
    assert isinstance(family_id, uuid.UUID)


def test_generate_family_id_is_unique():
    """
    Ensure that generate_family_id() produces unique UUIDs across multiple calls.
    While collisions are extremely unlikely, this sanity check ensures
    two consecutive calls do not return the same value.
    """
    id1 = generate_family_id()
    id2 = generate_family_id()
    assert id1 != id2


@freeze_time("2026-01-15 12:00:00")  # Freeze time for deterministic timestamps
@pytest.mark.parametrize(
    "iat_delta, exp_delta",
    [
        (0, 60),  # 1-minute token
        (-60, 60),  # issued in past
        (0, 3600 * 24),  # 1-day token
    ],
)
def test_generate_and_decode_access_token(mocker, iat_delta, exp_delta):
    """
    Test that access tokens are generated correctly and can be decoded.
    Payload fields: sub, type, iat, exp
    """
    now = datetime.now(UTC)
    iat = now + timedelta(seconds=iat_delta)
    exp = now + timedelta(seconds=exp_delta)

    # Mock secret
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value=SECRET_ACCESS,
    )

    token = generate_access_token(USER_ID, iat, exp)
    assert isinstance(token, str) and len(token) > 0

    payload = decode_access_token(token)
    assert payload["sub"] == str(USER_ID)
    assert payload["type"] == "access"
    assert payload["iat"] == int(iat.timestamp())
    assert payload["exp"] == int(exp.timestamp())


@freeze_time("2026-01-15 12:00:00")
@pytest.mark.parametrize(
    "iat_delta, exp_delta, family_expires_delta",
    [
        (0, 60, 3600),  # Normal token
        (-60, 60, 3600),  # Issued in past
        (0, 3600 * 24, 3600 * 48),  # Long-lived family
    ],
)
def test_generate_and_decode_refresh_token(
    mocker, iat_delta, exp_delta, family_expires_delta
):
    """
    Test that refresh tokens are generated correctly and can be decoded.
    Payload fields: sub, type, family_id, iat, exp, family_expires_at
    """
    now = datetime.now(UTC)
    iat = now + timedelta(seconds=iat_delta)
    exp = now + timedelta(seconds=exp_delta)
    family_expires_at = now + timedelta(seconds=family_expires_delta)

    mocker.patch(
        "app.core.security.settings.refresh_token_secret.get_secret_value",
        return_value=SECRET_REFRESH,
    )

    token = generate_refresh_token(USER_ID, FAMILY_ID, iat, exp, family_expires_at)
    assert isinstance(token, str) and len(token) > 0

    payload = decode_refresh_token(token)
    assert payload["sub"] == str(USER_ID)
    assert payload["type"] == "refresh"
    assert payload["family_id"] == str(FAMILY_ID)
    assert payload["iat"] == int(iat.timestamp())
    assert payload["exp"] == int(exp.timestamp())
    assert payload["family_expires_at"] == int(family_expires_at.timestamp())


@freeze_time("2026-01-15 12:00:00")
def test_decode_token_expired(mocker):
    """
    Test that _decode_token raises TokenExpired for expired tokens.
    """
    now = datetime.now(UTC)
    iat = now - timedelta(hours=2)
    exp = now - timedelta(hours=1)

    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value=SECRET_ACCESS,
    )

    token = generate_access_token(uuid.uuid4(), iat, exp)
    with pytest.raises(TokenExpired):
        decode_access_token(token)


@freeze_time("2026-01-15 12:00:00")
def test_decode_token_invalid_signature(mocker):
    """
    Test that _decode_token raises InvalidTokenSignature when using the wrong secret.
    """
    now = datetime.now(UTC)
    iat = now
    exp = now + timedelta(hours=1)

    # Token signed with one secret
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="real-secret",
    )
    token = generate_access_token(USER_ID, iat, exp)

    # Decode using different secret
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="wrong-secret",
    )
    with pytest.raises(InvalidTokenSignature):
        decode_access_token(token)


def test_decode_token_malformed():
    """
    Test that _decode_token raises MalformedTokenError for invalid/malformed JWT strings
    """
    invalid_tokens = ["", "not-a-jwt", "abc.def", "!!!"]
    for token in invalid_tokens:
        with pytest.raises(MalformedTokenError):
            _decode_token(token, SECRET_ACCESS)

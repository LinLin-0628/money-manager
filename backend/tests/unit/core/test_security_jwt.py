# tests/unit/test_jwt_tokens.py

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from freezegun import freeze_time
from jose import JWSError, jwt

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
    generate_refresh_token,
)
from app.core.settings import settings

# =====================================================
# generate_access_token
# =====================================================


def test_generate_access_token_basic(mocker):
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="access-secret",
    )

    user_id = uuid.uuid4()
    iat = datetime.now(UTC)
    exp = iat + timedelta(hours=1)

    token = generate_access_token(user_id, iat, exp)

    assert isinstance(token, str)

    payload = jwt.decode(token, "access-secret", algorithms=[settings.algorithm])
    assert payload == {
        "sub": str(user_id),
        "type": "access",
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
    }


def test_generate_access_token_future_iat(mocker):
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="access-secret",
    )

    now = datetime.now(UTC)
    user_id = uuid.uuid4()

    # iat in future
    future_iat = now + timedelta(hours=1)
    exp = future_iat + timedelta(hours=1)

    token = generate_access_token(user_id, future_iat, exp)
    payload = jwt.decode(
        token,
        "access-secret",
        algorithms=[settings.algorithm],
        options={"verify_exp": False},
    )
    assert payload["iat"] == int(future_iat.timestamp())


def test_generate_access_token_past_exp(mocker):
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="access-secret",
    )

    now = datetime.now(UTC)
    user_id = uuid.uuid4()

    # exp < iat
    past_exp = now - timedelta(seconds=1)
    token = generate_access_token(user_id, now, past_exp)
    payload = jwt.decode(
        token,
        "access-secret",
        algorithms=[settings.algorithm],
        options={"verify_exp": False},
    )
    assert payload["exp"] == int(past_exp.timestamp())


def test_generate_access_token_exceptions(mocker):
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        side_effect=Exception("secret failure"),
    )

    with pytest.raises(Exception, match="secret failure"):
        generate_access_token(
            uuid.uuid4(),
            datetime.now(UTC),
            datetime.now(UTC) + timedelta(hours=1),
        )

    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="access-secret",
    )
    mocker.patch("app.core.security.settings.algorithm", "invalid-alg")

    with pytest.raises(JWSError):
        generate_access_token(
            uuid.uuid4(),
            datetime.now(UTC),
            datetime.now(UTC) + timedelta(hours=1),
        )


# =====================================================
# generate_refresh_token
# =====================================================


def test_generate_refresh_token_basic(mocker):
    mocker.patch(
        "app.core.security.settings.refresh_token_secret.get_secret_value",
        return_value="refresh-secret",
    )

    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    iat = datetime.now(UTC)
    exp = iat + timedelta(days=1)
    family_expires_at = exp + timedelta(days=7)

    token = generate_refresh_token(user_id, family_id, iat, exp, family_expires_at)

    payload = jwt.decode(token, "refresh-secret", algorithms=[settings.algorithm])

    assert payload == {
        "sub": str(user_id),
        "type": "refresh",
        "family_id": str(family_id),
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
        "family_expires_at": int(family_expires_at.timestamp()),
    }


def test_generate_refresh_token_time_edge_cases(mocker):
    mocker.patch(
        "app.core.security.settings.refresh_token_secret.get_secret_value",
        return_value="refresh-secret",
    )

    now = datetime.now(UTC)
    user_id = uuid.uuid4()
    family_id = uuid.uuid4()

    # family_expires_at < exp
    token = generate_refresh_token(
        user_id,
        family_id,
        now,
        now + timedelta(days=1),
        now,
    )

    payload = jwt.decode(token, "refresh-secret", algorithms=[settings.algorithm])
    assert payload["family_expires_at"] == int(now.timestamp())


def test_generate_refresh_token_exceptions(mocker):
    mocker.patch(
        "app.core.security.settings.refresh_token_secret.get_secret_value",
        side_effect=Exception("secret failure"),
    )

    with pytest.raises(Exception, match="secret failure"):
        generate_refresh_token(
            uuid.uuid4(),
            uuid.uuid4(),
            datetime.now(UTC),
            datetime.now(UTC) + timedelta(days=1),
            datetime.now(UTC) + timedelta(days=7),
        )


# =====================================================
# _decode_token
# =====================================================


def test_decode_token_valid(mocker):
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="access-secret",
    )

    user_id = uuid.uuid4()
    iat = datetime.now(UTC)
    exp = iat + timedelta(hours=1)

    token = generate_access_token(user_id, iat, exp)
    payload = _decode_token(token, "access-secret")

    assert payload["sub"] == str(user_id)


@freeze_time("2025-01-01T12:00:00Z")
def test_decode_token_expired():
    user_id = uuid.uuid4()
    iat = datetime.now(UTC) - timedelta(days=2)
    exp = datetime.now(UTC) - timedelta(days=1)

    token = jwt.encode(
        {
            "sub": str(user_id),
            "iat": int(iat.timestamp()),
            "exp": int(exp.timestamp()),
        },
        "secret",
        algorithm=settings.algorithm,
    )

    with pytest.raises(TokenExpired):
        _decode_token(token, "secret")


def test_decode_token_invalid_signature():
    token = jwt.encode(
        {
            "sub": "123",
            "iat": int(datetime.now(UTC).timestamp()),
            "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        },
        "correct-secret",
        algorithm=settings.algorithm,
    )

    with pytest.raises(InvalidTokenSignature):
        _decode_token(token, "wrong-secret")


def test_decode_token_malformed_inputs():
    with pytest.raises(MalformedTokenError):
        _decode_token("not-a-jwt", "secret")

    with pytest.raises(MalformedTokenError):
        _decode_token("", "secret")

    with pytest.raises(AttributeError):
        _decode_token(None, "secret")

    with pytest.raises(AttributeError):
        _decode_token(123, "secret")

    malformed = jwt.encode({"foo": "bar"}, "secret", algorithm=settings.algorithm)
    with pytest.raises(MalformedTokenError):
        _decode_token(malformed, "secret")


# =====================================================
# decode_access_token
# =====================================================


def test_decode_access_token_valid(mocker):
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="access-secret",
    )

    user_id = uuid.uuid4()
    iat = datetime.now(UTC)
    exp = iat + timedelta(hours=1)

    token = generate_access_token(user_id, iat, exp)
    payload = decode_access_token(token)

    assert payload["type"] == "access"


@freeze_time("2025-01-01T12:00:00Z")
def test_decode_access_token_expired(mocker):
    mocker.patch(
        "app.core.security.settings.access_token_secret.get_secret_value",
        return_value="access-secret",
    )

    token = generate_access_token(
        uuid.uuid4(),
        datetime.now(UTC) - timedelta(days=2),
        datetime.now(UTC) - timedelta(days=1),
    )

    with pytest.raises(TokenExpired):
        decode_access_token(token)


# =====================================================
# decode_refresh_token
# =====================================================


def test_decode_refresh_token_valid(mocker):
    mocker.patch(
        "app.core.security.settings.refresh_token_secret.get_secret_value",
        return_value="refresh-secret",
    )

    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    iat = datetime.now(UTC)
    exp = iat + timedelta(days=1)
    family_expires_at = exp + timedelta(days=7)

    token = generate_refresh_token(user_id, family_id, iat, exp, family_expires_at)

    payload = decode_refresh_token(token)

    assert payload["type"] == "refresh"
    assert payload["family_id"] == str(family_id)


@freeze_time("2025-01-01T12:00:00Z")
def test_decode_refresh_token_expired(mocker):
    mocker.patch(
        "app.core.security.settings.refresh_token_secret.get_secret_value",
        return_value="refresh-secret",
    )

    token = generate_refresh_token(
        uuid.uuid4(),
        uuid.uuid4(),
        datetime.now(UTC) - timedelta(days=2),
        datetime.now(UTC) - timedelta(days=1),
        datetime.now(UTC) + timedelta(days=1),
    )

    with pytest.raises(TokenExpired):
        decode_refresh_token(token)

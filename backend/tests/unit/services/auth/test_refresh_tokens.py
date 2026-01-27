# tests/unit/services/test_auth_service_refresh.py
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from freezegun import freeze_time

from app.core.exceptions.auth import (
    InvalidRefreshToken,
    InvalidRefreshTokenSignature,
    MalformedRefreshTokenError,
    RefreshTokenExpired,
)
from app.core.exceptions.base import AppException
from app.core.settings import settings
from app.models import RefreshToken
from app.schemas.auth import TokenPair
from app.services.auth import AuthService


@pytest.fixture
def mock_repo(mocker):
    repo = mocker.Mock()
    repo.db.commit = mocker.Mock()
    repo.db.rollback = mocker.Mock()
    repo.create_refresh_token = mocker.Mock()
    repo.revoke_token = mocker.Mock()
    repo.get_refresh_token_by_hash = mocker.Mock()
    repo.revoke_all_refresh_tokens = mocker.Mock()
    return repo


@pytest.fixture
def auth_service(mock_repo, mocker):
    # Mock user service (not used in refresh_tokens)
    user_service = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=user_service)
    return service, mock_repo


@freeze_time("2026-01-27 12:00:00")
def test_refresh_tokens_happy_path(auth_service, mocker):
    service, repo = auth_service
    now = datetime.now(UTC)

    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    future = now + timedelta(days=7)

    # Mock decode_refresh_token to return valid payload
    mocker.patch(
        "app.services.auth.decode_refresh_token",
        return_value={
            "sub": str(user_id),
            "type": "refresh",
            "family_id": str(family_id),
            "family_expires_at": future.timestamp(),
        },
    )

    # Mock get_token to return a valid, not revoked RefreshToken
    token_in_db = RefreshToken(
        id=1,
        token_hash="oldhash",
        user_id=user_id,
        family_id=family_id,
        expires_at=future,
        created_at=now,
        family_expires_at=future,
        revoked_at=None,
    )
    repo.get_refresh_token_by_hash.return_value = token_in_db

    # Spy on token generation and hash
    def access_token_mock(user_id_arg, iat, exp):
        return f"access-{exp.timestamp()}"

    def refresh_token_mock(user_id_arg, family_id_arg, iat, exp, family_expires_at):
        return f"refresh-{exp.timestamp()}"

    access_spy = mocker.patch(
        "app.services.auth.generate_access_token", side_effect=access_token_mock
    )
    refresh_spy = mocker.patch(
        "app.services.auth.generate_refresh_token", side_effect=refresh_token_mock
    )
    mocker.patch(
        "app.services.auth.hash_token", return_value="newhash"
    )  # can have var: hash_spy
    revoke_spy = mocker.spy(service, "_revoke_token")

    token_pair = service.refresh_tokens("valid-refresh-token")

    # Assert return type
    assert isinstance(token_pair, TokenPair)
    assert token_pair.access_token.startswith("access-")
    assert token_pair.refresh_token.startswith("refresh-")

    # Assert _revoke_token called once with old token id
    revoke_spy.assert_called_once_with(token_in_db.id)

    # Assert new refresh token created in repo and db committed
    repo.create_refresh_token.assert_called_once()
    repo.db.commit.assert_called_once()

    # Assert token generation called with correct positional arguments and expiration times  # noqa: E501
    # Access token
    access_call_args = access_spy.call_args
    assert access_call_args.args[0] == user_id  # user_id
    assert access_call_args.kwargs["iat"] == now
    assert access_call_args.kwargs["exp"] == now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    # Refresh token
    refresh_call_args = refresh_spy.call_args
    assert refresh_call_args.args[0] == user_id
    assert refresh_call_args.args[1] == family_id
    assert refresh_call_args.kwargs["iat"] == now
    assert refresh_call_args.kwargs["exp"] <= future  # capped by family_expires_at
    assert refresh_call_args.kwargs["family_expires_at"] == future


def test_refresh_tokens_expired_token(auth_service, mocker):
    service, _ = auth_service
    # Mock decode_refresh_token to raise TokenExpired
    from app.core.exceptions.auth import TokenExpired

    mocker.patch("app.services.auth.decode_refresh_token", side_effect=TokenExpired)

    import pytest

    with pytest.raises(RefreshTokenExpired) as excinfo:
        service.refresh_tokens("expired-token")
    assert excinfo.value.details["code"] == "refresh_token_expired"


def test_refresh_tokens_invalid_signature(auth_service, mocker):
    service, _ = auth_service
    from app.core.exceptions.auth import InvalidTokenSignature

    mocker.patch(
        "app.services.auth.decode_refresh_token", side_effect=InvalidTokenSignature
    )

    import pytest

    with pytest.raises(InvalidRefreshTokenSignature) as excinfo:
        service.refresh_tokens("bad-signature")
    assert excinfo.value.details["code"] == "invalid_refresh_token_signature"


def test_refresh_tokens_malformed_token(auth_service, mocker):
    service, _ = auth_service
    from app.core.exceptions.auth import MalformedTokenError

    mocker.patch(
        "app.services.auth.decode_refresh_token", side_effect=MalformedTokenError
    )

    import pytest

    from app.core.exceptions.auth import MalformedRefreshTokenError

    with pytest.raises(MalformedRefreshTokenError) as excinfo:
        service.refresh_tokens("malformed-token")
    assert excinfo.value.details["code"] == "malformed_refresh_token"


@pytest.mark.parametrize(
    "payload,expected_exception",
    [
        (
            {
                "sub": None,
                "type": "refresh",
                "family_id": "f",
                "family_expires_at": 123,
            },
            MalformedRefreshTokenError,
        ),
        (
            {
                "sub": str(uuid.uuid4()),
                "type": "refresh",
                "family_id": None,
                "family_expires_at": 123,
            },
            MalformedRefreshTokenError,
        ),
        (
            {
                "sub": str(uuid.uuid4()),
                "type": "refresh",
                "family_id": str(uuid.uuid4()),
                "family_expires_at": "abc",
            },
            MalformedRefreshTokenError,
        ),
        (
            {
                "sub": str(uuid.uuid4()),
                "type": "access",
                "family_id": str(uuid.uuid4()),
                "family_expires_at": 123,
            },
            MalformedRefreshTokenError,
        ),
    ],
)
def test_refresh_tokens_payload_validation(
    auth_service, mocker, payload, expected_exception
):
    service, _ = auth_service
    mocker.patch("app.services.auth.decode_refresh_token", return_value=payload)
    import pytest

    with pytest.raises(expected_exception):
        service.refresh_tokens("bad-payload-token")


def test_refresh_tokens_token_not_found(auth_service, mocker):
    service, repo = auth_service
    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    now = datetime.now(UTC)
    future = now + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "family_id": str(family_id),
        "family_expires_at": future.timestamp(),
    }
    mocker.patch("app.services.auth.decode_refresh_token", return_value=payload)
    repo.get_refresh_token_by_hash.return_value = None

    import pytest

    with pytest.raises(InvalidRefreshToken):
        service.refresh_tokens("token-not-in-db")


def test_refresh_tokens_token_revoked(auth_service, mocker):
    service, repo = auth_service
    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    now = datetime.now(UTC)
    future = now + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "family_id": str(family_id),
        "family_expires_at": future.timestamp(),
    }
    mocker.patch("app.services.auth.decode_refresh_token", return_value=payload)
    token_in_db = RefreshToken(
        id=1,
        token_hash="hash",
        user_id=user_id,
        family_id=family_id,
        expires_at=future,
        created_at=now,
        family_expires_at=future,
        revoked_at=now,
    )
    repo.get_refresh_token_by_hash.return_value = token_in_db

    import pytest

    with pytest.raises(InvalidRefreshToken):
        service.refresh_tokens("revoked-token")


@freeze_time("2026-01-27 12:00:00")
def test_refresh_tokens_family_expired(auth_service, mocker):
    service, repo = auth_service
    now = datetime.now(UTC)
    past = now - timedelta(days=1)
    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "family_id": str(family_id),
        "family_expires_at": past.timestamp(),
    }
    mocker.patch("app.services.auth.decode_refresh_token", return_value=payload)
    token_in_db = RefreshToken(
        id=42,
        token_hash="hash",
        user_id=user_id,
        family_id=family_id,
        expires_at=now,
        created_at=now,
        family_expires_at=past,
        revoked_at=None,
    )
    repo.get_refresh_token_by_hash.return_value = token_in_db
    revoke_spy = mocker.spy(service, "_revoke_token")

    import pytest

    with pytest.raises(RefreshTokenExpired):
        service.refresh_tokens("family-expired-token")

    revoke_spy.assert_called_once_with(token_in_db.id)


def test_refresh_tokens_exception_during_create(auth_service, mocker):
    service, repo = auth_service
    now = datetime.now(UTC)
    future = now + timedelta(days=7)
    user_id = uuid.uuid4()
    family_id = uuid.uuid4()
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "family_id": str(family_id),
        "family_expires_at": future.timestamp(),
    }
    mocker.patch("app.services.auth.decode_refresh_token", return_value=payload)

    token_in_db = RefreshToken(
        id=1,
        token_hash="hash",
        user_id=user_id,
        family_id=family_id,
        expires_at=future,
        created_at=now,
        family_expires_at=future,
        revoked_at=None,
    )
    repo.get_refresh_token_by_hash.return_value = token_in_db

    # Patch create_refresh_token to raise
    repo.create_refresh_token.side_effect = Exception("DB error")

    import pytest

    with pytest.raises(AppException):
        service.refresh_tokens("token-causing-exception")

    repo.db.rollback.assert_called_once()

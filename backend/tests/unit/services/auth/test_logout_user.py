# tests/unit/services/test_auth_logout.py
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from freezegun import freeze_time

from app.core.exceptions.auth import (
    InvalidRefreshToken,
    InvalidTokenSignature,
    MalformedRefreshTokenError,
    MalformedTokenError,
    TokenExpired,
)
from app.core.exceptions.base import AppException
from app.services.auth import AuthService


# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def mock_auth_repo(mocker):
    """Mock the AuthRepository"""
    repo = mocker.Mock()
    repo.db = mocker.Mock()
    return repo


@pytest.fixture
def mock_user_service(mocker):
    """Mock UserService (not used in logout, but required to instantiate AuthService)"""
    return mocker.Mock()


@pytest.fixture
def auth_service(mock_auth_repo, mock_user_service):
    return AuthService(auth_repo=mock_auth_repo, user_service=mock_user_service)


@pytest.fixture
def valid_token(mocker):
    """Returns a valid refresh token payload and token string"""
    token_str = "valid_refresh_token"
    user_id = uuid4()
    payload = {"sub": str(user_id), "type": "refresh"}
    mocker.patch("app.services.auth.decode_refresh_token", return_value=payload)
    return token_str, user_id


# ----------------------------
# 1️⃣ Happy Path
# ----------------------------
@freeze_time("2026-01-27 12:00:00")
def test_logout_user_success(auth_service, mock_auth_repo, valid_token):
    token, user_id = valid_token

    auth_service.logout_user(token)

    # Assert decode_refresh_token called
    # auth_service.user_service  # just to avoid lint errors
    # revoke_all_refresh_tokens called with correct user_id and timestamp
    mock_auth_repo.revoke_all_refresh_tokens.assert_called_once_with(
        user_id, datetime(2026, 1, 27, 12, 0, 0, tzinfo=UTC)
    )
    # db.commit called
    mock_auth_repo.db.commit.assert_called_once()
    # db.rollback should NOT be called
    mock_auth_repo.db.rollback.assert_not_called()


# ----------------------------
# 2️⃣ Invalid / Malformed Token
# ----------------------------
@pytest.mark.parametrize(
    "exception",
    [
        pytest.param(TokenExpired(), id="TokenExpired"),
        pytest.param(MalformedTokenError(), id="MalformedTokenError"),
        pytest.param(InvalidTokenSignature(), id="InvalidTokenSignature"),
    ],
)
def test_logout_user_invalid_token_raises(
    auth_service, mocker, mock_auth_repo, exception
):
    mocker.patch("app.services.auth.decode_refresh_token", side_effect=exception)

    with pytest.raises(InvalidRefreshToken):
        auth_service.logout_user("any_token")

    # DB operations should not be called
    mock_auth_repo.revoke_all_refresh_tokens.assert_not_called()
    mock_auth_repo.db.commit.assert_not_called()
    mock_auth_repo.db.rollback.assert_not_called()


# ----------------------------
# 3️⃣ Malformed Subject in Token
# ----------------------------
@pytest.mark.parametrize(
    "bad_sub",
    [None, 123, [], {}, object()],
)
def test_logout_user_malformed_subject(auth_service, mocker, mock_auth_repo, bad_sub):
    token = "malformed_subject_token"
    payload = {"sub": bad_sub, "type": "refresh"}
    mocker.patch("app.services.auth.decode_refresh_token", return_value=payload)

    with pytest.raises(MalformedRefreshTokenError):
        auth_service.logout_user(token)

    # DB operations should not be called
    mock_auth_repo.revoke_all_refresh_tokens.assert_not_called()
    mock_auth_repo.db.commit.assert_not_called()
    mock_auth_repo.db.rollback.assert_not_called()


# ----------------------------
# 4️⃣ DB / Repository Exceptions
# ----------------------------
def test_logout_user_db_exception_on_revoke(
    auth_service, mocker, mock_auth_repo, valid_token
):
    token, user_id = valid_token
    mock_auth_repo.revoke_all_refresh_tokens.side_effect = Exception("DB error")

    with pytest.raises(AppException):
        auth_service.logout_user(token)

    # rollback should be called
    mock_auth_repo.db.rollback.assert_called_once()
    # commit should NOT be called
    mock_auth_repo.db.commit.assert_not_called()


def test_logout_user_db_exception_on_commit(
    auth_service, mocker, mock_auth_repo, valid_token
):
    token, user_id = valid_token
    # Simulate db.commit raises exception
    mock_auth_repo.db.commit.side_effect = Exception("DB commit error")

    with pytest.raises(AppException):
        auth_service.logout_user(token)

    # rollback should be called
    mock_auth_repo.db.rollback.assert_called_once()

# tests/unit/services/test_auth_helpers.py

from datetime import UTC, datetime

import pytest
from freezegun import freeze_time

from app.core.exceptions.auth import RefreshTokenNotFoundError
from app.models import RefreshToken
from app.services.auth import AuthService

# ----------------------------
# Tests for _revoke_token
# ----------------------------


@freeze_time("2026-01-27 12:00:00")
def test_revoke_token_happy_path(mocker):
    """Token exists and is not revoked -> should call revoke_token_by_id with correct args"""  # noqa: E501
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_id = 123
    token = RefreshToken(id=token_id, revoked_at=None)
    mock_repo.get_token_by_id.return_value = token

    service._revoke_token(token_id)

    now = datetime.now(UTC)
    mock_repo.get_token_by_id.assert_called_once_with(token_id)
    mock_repo.revoke_token.assert_called_once_with(token, now)


@freeze_time("2026-01-27 12:00:00")
def test_revoke_token_already_revoked(mocker):
    """Token exists but already revoked -> should still call revoke_token_by_id"""
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_id = 123
    token = RefreshToken(id=token_id, revoked_at=datetime.now(UTC))
    mock_repo.get_token_by_id.return_value = token

    service._revoke_token(token_id)

    now = datetime.now(UTC)
    mock_repo.get_token_by_id.assert_called_once_with(token_id)
    mock_repo.revoke_token.assert_called_once_with(token, now)


def test_revoke_token_not_found(mocker):
    """Token not found -> should not fail, revoke_token_by_id not called"""
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_id = 123
    mock_repo.get_token_by_id.return_value = None

    with pytest.raises(RefreshTokenNotFoundError):
        service._revoke_token(token_id)

    mock_repo.get_token_by_id.assert_called_once_with(token_id)
    mock_repo.revoke_token.assert_not_called()


def test_revoke_token_exception_propagation(mocker):
    """Exception in repo -> should propagate"""
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_id = 123
    mock_repo.get_token_by_id.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        service._revoke_token(token_id)


# ----------------------------
# Tests for get_token
# ----------------------------


def test_get_token_happy_path(mocker):
    """Token exists in repo -> returns the token"""
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_str = "refresh-token"
    token_obj = RefreshToken(id=1)
    mock_repo.get_refresh_token_by_hash.return_value = token_obj

    # Patch hash_token to return a predictable hash
    mocker.patch("app.services.auth.hash_token", return_value="hashed-token")

    result = service.get_token(token_str)

    assert result == token_obj
    mock_repo.get_refresh_token_by_hash.assert_called_once_with("hashed-token")


def test_get_token_not_found(mocker):
    """Token not found in repo -> returns None"""
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_str = "refresh-token"
    mock_repo.get_refresh_token_by_hash.return_value = None
    mocker.patch("app.services.auth.hash_token", return_value="hashed-token")

    result = service.get_token(token_str)

    assert result is None
    mock_repo.get_refresh_token_by_hash.assert_called_once_with("hashed-token")


def test_get_token_hash_exception(mocker):
    """hash_token raises exception -> should propagate"""
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_str = "refresh-token"
    mocker.patch("app.services.auth.hash_token", side_effect=ValueError("hash fail"))

    with pytest.raises(ValueError, match="hash fail"):
        service.get_token(token_str)


def test_get_token_repo_exception(mocker):
    """Repository raises exception -> should propagate"""
    mock_repo = mocker.Mock()
    service = AuthService(auth_repo=mock_repo, user_service=None)

    token_str = "refresh-token"
    mocker.patch("app.services.auth.hash_token", return_value="hashed-token")
    mock_repo.get_refresh_token_by_hash.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        service.get_token(token_str)

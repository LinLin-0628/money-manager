import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from app.core.exceptions.auth import InvalidCredentials
from app.core.exceptions.base import AppException
from app.core.exceptions.user import UserNotFound
from app.core.settings import settings
from app.models import User
from app.schemas.auth import TokenPair
from app.services.auth import AuthService


# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def sample_user():
    """Returns a minimal User object for testing."""
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="hashedpassword",
        name="Test User",
    )


@pytest.fixture
def auth_service(mocker, sample_user):
    """Sets up AuthService with all dependencies mocked."""
    mock_user_service = Mock()
    mock_auth_repo = Mock()
    mock_auth_repo.db.commit = Mock()
    mock_auth_repo.db.rollback = Mock()

    service = AuthService(
        auth_repo=mock_auth_repo,
        user_service=mock_user_service,
    )
    return service, mock_user_service, mock_auth_repo


# ----------------------------
# 1️⃣ Happy Path
# ----------------------------
@freeze_time("2026-01-27 12:00:00")
def test_login_user_success(auth_service, sample_user, mocker):
    service, user_service_mock, auth_repo_mock = auth_service
    now = datetime.now(UTC)

    # Mock user lookup
    user_service_mock.get_user_by_email.return_value = sample_user

    # Mock password verification
    mocker.patch("app.services.auth.verify_password", return_value=True)

    # Mock token generation
    mock_access_token = "access-token"
    mock_refresh_token = "refresh-token"
    mocker.patch(
        "app.services.auth.generate_access_token", return_value=mock_access_token
    )
    mocker.patch(
        "app.services.auth.generate_refresh_token", return_value=mock_refresh_token
    )
    mocker.patch("app.services.auth.generate_family_id", return_value=uuid.UUID(int=1))

    # Mock hash_token
    mocker.patch("app.services.auth.hash_token", return_value="hashed-refresh-token")

    # Call login_user
    token_pair = service.login_user(sample_user.email, "correctpassword")

    # Assertions
    assert isinstance(token_pair, TokenPair)
    assert token_pair.access_token == mock_access_token
    assert token_pair.refresh_token == mock_refresh_token

    user_service_mock.get_user_by_email.assert_called_once_with(sample_user.email)
    auth_repo_mock.revoke_all_refresh_tokens.assert_called_once_with(
        sample_user.id, now
    )
    auth_repo_mock.create_refresh_token.assert_called_once()
    auth_repo_mock.db.commit.assert_called_once()


# ----------------------------
# 2️⃣ User Not Found
# ----------------------------
def test_login_user_user_not_found(auth_service, mocker):
    service, user_service_mock, _ = auth_service
    user_service_mock.get_user_by_email.return_value = None

    with pytest.raises(UserNotFound):
        service.login_user("nonexistent@example.com", "any-password")


# ----------------------------
# 3️⃣ Invalid Password
# ----------------------------
def test_login_user_invalid_password(auth_service, sample_user, mocker):
    service, user_service_mock, _ = auth_service
    user_service_mock.get_user_by_email.return_value = sample_user

    mocker.patch("app.services.auth.verify_password", return_value=False)

    with pytest.raises(InvalidCredentials):
        service.login_user(sample_user.email, "wrong-password")


# ----------------------------
# 4️⃣ Token Generation Called
# ----------------------------
@freeze_time("2026-01-27 12:00:00")
def test_login_user_token_generation_called(auth_service, sample_user, mocker):
    service, user_service_mock, _ = auth_service
    user_service_mock.get_user_by_email.return_value = sample_user
    mocker.patch("app.services.auth.verify_password", return_value=True)

    access_mock = mocker.patch(
        "app.services.auth.generate_access_token", return_value="access"
    )
    refresh_mock = mocker.patch(
        "app.services.auth.generate_refresh_token", return_value="refresh"
    )
    family_mock = mocker.patch(
        "app.services.auth.generate_family_id", return_value=uuid.UUID(int=1)
    )

    service.login_user(sample_user.email, "correctpassword")

    access_mock.assert_called_once()
    refresh_mock.assert_called_once()
    family_mock.assert_called_once()


# ----------------------------
# 5️⃣ Refresh Token Persistence
# ----------------------------
@freeze_time("2026-01-27 12:00:00")
def test_login_user_refresh_token_persistence(auth_service, sample_user, mocker):
    service, user_service_mock, auth_repo_mock = auth_service
    user_service_mock.get_user_by_email.return_value = sample_user
    mocker.patch("app.services.auth.verify_password", return_value=True)
    mocker.patch("app.services.auth.generate_access_token", return_value="access")
    mocker.patch("app.services.auth.generate_refresh_token", return_value="refresh")
    mocker.patch("app.services.auth.generate_family_id", return_value=uuid.UUID(int=1))
    hash_mock = mocker.patch(
        "app.services.auth.hash_token", return_value="hashed-refresh"
    )

    service.login_user(sample_user.email, "correctpassword")

    auth_repo_mock.revoke_all_refresh_tokens.assert_called_once_with(
        sample_user.id, datetime.now(UTC)
    )
    auth_repo_mock.create_refresh_token.assert_called_once()
    hash_mock.assert_called_once_with("refresh")
    auth_repo_mock.db.commit.assert_called_once()


# ----------------------------
# 6️⃣ Exception Handling / Rollback
# ----------------------------
@freeze_time("2026-01-27 12:00:00")
def test_login_user_exception_rolls_back(auth_service, sample_user, mocker):
    service, user_service_mock, auth_repo_mock = auth_service
    user_service_mock.get_user_by_email.return_value = sample_user
    mocker.patch("app.services.auth.verify_password", return_value=True)
    mocker.patch("app.services.auth.generate_access_token", return_value="access")
    mocker.patch("app.services.auth.generate_refresh_token", return_value="refresh")
    mocker.patch("app.services.auth.generate_family_id", return_value=uuid.UUID(int=1))
    mocker.patch("app.services.auth.hash_token", return_value="hashed-refresh")

    # Simulate exception in create_refresh_token
    auth_repo_mock.create_refresh_token.side_effect = Exception("DB error")

    with pytest.raises(AppException):
        service.login_user(sample_user.email, "correctpassword")

    auth_repo_mock.db.rollback.assert_called_once()


# ----------------------------
# 7️⃣ Token Expiration Validation (Settings)
# ----------------------------
@freeze_time("2026-01-27 12:00:00")
def test_login_user_tokens_have_correct_expiration(auth_service, sample_user, mocker):
    service, user_service_mock, _ = auth_service
    user_service_mock.get_user_by_email.return_value = sample_user
    mocker.patch("app.services.auth.verify_password", return_value=True)

    # Dictionary to capture arguments
    captured_args = {}

    # Fake generate_access_token to return string but capture kwargs
    def fake_generate_access_token(**kwargs):
        captured_args["access"] = kwargs
        return "access-token"

    # Fake generate_refresh_token to return string but capture kwargs
    def fake_generate_refresh_token(**kwargs):
        captured_args["refresh"] = kwargs
        return "refresh-token"

    mocker.patch(
        "app.services.auth.generate_access_token",
        side_effect=fake_generate_access_token,
    )
    mocker.patch(
        "app.services.auth.generate_refresh_token",
        side_effect=fake_generate_refresh_token,
    )
    mocker.patch("app.services.auth.generate_family_id", return_value=uuid.UUID(int=1))
    mocker.patch("app.services.auth.hash_token", return_value="hashed-refresh")

    # Call login_user (will return TokenPair with strings)
    token_pair = service.login_user(sample_user.email, "correctpassword")

    # Assertions: TokenPair is correct
    assert token_pair.access_token == "access-token"
    assert token_pair.refresh_token == "refresh-token"

    # Now check the captured arguments for correct iat/exp
    now = datetime.now(UTC)  # Freezegun time
    expected_access_exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    expected_refresh_exp = now + timedelta(days=settings.refresh_token_expire_days)

    # Access token
    assert captured_args["access"]["iat"] == now
    assert captured_args["access"]["exp"] == expected_access_exp

    # Refresh token
    assert captured_args["refresh"]["iat"] == now
    assert captured_args["refresh"]["exp"] == expected_refresh_exp

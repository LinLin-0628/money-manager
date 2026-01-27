import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from app.api.deps.auth import get_current_user
from app.core.exceptions.auth import (
    AccessTokenExpired,
    InvalidAccessTokenSignature,
    MalformedAccessTokenError,
)
from app.core.exceptions.user import UserNotFound
from app.core.security import InvalidTokenSignature, MalformedTokenError, TokenExpired
from app.models import User


# Fixture: sample User
@pytest.fixture
def sample_user():
    return User(id=uuid.uuid4(), email="test@example.com", name="Test User")


# 1️⃣ Decode exceptions (no freezegun needed, mocked)
@pytest.mark.parametrize(
    "decode_exception, expected_exception",
    [
        (TokenExpired(), AccessTokenExpired),
        (MalformedTokenError(), MalformedAccessTokenError),
        (InvalidTokenSignature(), InvalidAccessTokenSignature),
    ],
)
def test_get_current_user_raises_on_decode_errors(
    mocker, decode_exception, expected_exception
):
    mocker.patch("app.api.deps.auth.decode_access_token", side_effect=decode_exception)
    mock_user_service = Mock()

    with pytest.raises(expected_exception):
        get_current_user("fake_token", mock_user_service)


# 2️⃣ Token type enforcement
@pytest.mark.parametrize(
    "payload",
    [
        {"sub": str(uuid.uuid4())},  # missing type
        {"sub": str(uuid.uuid4()), "type": "refresh"},
        {"sub": str(uuid.uuid4()), "type": "admin"},
    ],
)
def test_get_current_user_rejects_non_access_token_types(mocker, payload, sample_user):
    mocker.patch("app.api.deps.auth.decode_access_token", return_value=payload)
    mock_user_service = Mock()
    mock_user_service.get_user_by_id.return_value = sample_user

    with pytest.raises(InvalidAccessTokenSignature):
        get_current_user("fake_token", mock_user_service)


# 3️⃣ Subject structural validation
@pytest.mark.parametrize(
    "payload",
    [
        {"type": "access"},  # missing sub
        {"sub": None, "type": "access"},
        {"sub": 123, "type": "access"},
        {"sub": [], "type": "access"},
        {"sub": {}, "type": "access"},
        {"sub": True, "type": "access"},
    ],
)
def test_get_current_user_rejects_invalid_subjects(mocker, payload, sample_user):
    mocker.patch("app.api.deps.auth.decode_access_token", return_value=payload)
    mock_user_service = Mock()
    mock_user_service.get_user_by_id.return_value = sample_user

    with pytest.raises(MalformedAccessTokenError):
        get_current_user("fake_token", mock_user_service)


# 4️⃣ UUID string parsing edge case
def test_get_current_user_invalid_uuid_string_raises(mocker, sample_user):
    payload = {"sub": "not-a-uuid", "type": "access"}
    mocker.patch("app.api.deps.auth.decode_access_token", return_value=payload)
    mock_user_service = Mock()
    mock_user_service.get_user_by_id.return_value = sample_user

    with pytest.raises(MalformedAccessTokenError):
        get_current_user("fake_token", mock_user_service)


# 5️⃣ Valid subject normalization with freezegun
@pytest.mark.parametrize(
    "sub_value",
    [
        str(uuid.uuid4()),  # UUID string
        uuid.uuid4(),  # UUID object
    ],
)
@freeze_time("2026-01-27 12:00:00")  # freeze time to simulate 'now'
def test_get_current_user_accepts_valid_subject_formats(mocker, sample_user, sub_value):
    now = datetime.now(UTC)
    exp = now + timedelta(hours=1)

    # Construct realistic payload using timestamps
    payload = {
        "sub": sub_value,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    mocker.patch("app.api.deps.auth.decode_access_token", return_value=payload)

    mock_user_service = Mock()
    mock_user_service.get_user_by_id.return_value = sample_user

    user = get_current_user("fake_token", mock_user_service)
    assert user == sample_user

    # Ensure UUID normalization
    called_arg = mock_user_service.get_user_by_id.call_args[0][0]
    assert isinstance(called_arg, uuid.UUID)


# 6️⃣ User existence enforcement with frozen time
@freeze_time("2026-01-27 12:00:00")
def test_get_current_user_raises_when_user_not_found(mocker):
    now = datetime.now(UTC)
    exp = now + timedelta(hours=1)
    user_id = str(uuid.uuid4())
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    mocker.patch("app.api.deps.auth.decode_access_token", return_value=payload)
    mock_user_service = Mock()
    mock_user_service.get_user_by_id.return_value = None

    with pytest.raises(UserNotFound):
        get_current_user("fake_token", mock_user_service)


# 7️⃣ Happy path with freezegun
@freeze_time("2026-01-27 12:00:00")
def test_get_current_user_returns_user_for_valid_access_token(mocker, sample_user):
    now = datetime.now(UTC)
    exp = now + timedelta(hours=1)
    user_id = str(sample_user.id)
    payload = {
        "sub": user_id,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    decode_mock = mocker.patch(
        "app.api.deps.auth.decode_access_token", return_value=payload
    )
    mock_user_service = Mock()
    mock_user_service.get_user_by_id.return_value = sample_user

    user = get_current_user("fake_token", mock_user_service)

    assert user == sample_user
    decode_mock.assert_called_once_with("fake_token")
    mock_user_service.get_user_by_id.assert_called_once()

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions.user import UserAlreadyExists
from app.schemas.user import UserCreate
from tests.factories.user import UserFactory


def test_register_user_success(mocker, user_service, mock_user_repo):
    mock_user = UserFactory.build()
    mock_user_repo.create_user.return_value = mock_user

    mocker.patch("app.services.user.hash_password", return_value="hashed_password")

    user_create_data = UserCreate(
        name=mock_user.name, email=mock_user.email, password="plain_password"
    )

    # Act
    result = user_service.register_user(user_create_data)

    # Assert
    assert result == mock_user
    mock_user_repo.create_user.assert_called_once()
    mock_user_repo.db.commit.assert_called_once()
    mock_user_repo.db.rollback.assert_not_called()


def test_register_user_duplicate_email(mocker, user_service, mock_user_repo):
    # Arrange
    mocker.patch("app.services.user.hash_password", return_value="hashed_pw")

    # Simulate IntegrityError from repo
    mock_user_repo.create_user.side_effect = IntegrityError(None, None, None)

    user_create_data = UserCreate(
        email="duplicate@example.com", password="plain_password", name="John Doe"
    )

    # Act & Assert
    with pytest.raises(UserAlreadyExists):
        user_service.register_user(user_create_data)

    mock_user_repo.db.rollback.assert_called_once()
    mock_user_repo.db.commit.assert_not_called()


def test_get_user_by_email_found(user_service, mock_user_repo):
    mock_user = UserFactory.build()
    mock_user_repo.get_user_by_email.return_value = mock_user

    result = user_service.get_user_by_email(mock_user.email)

    assert result == mock_user
    mock_user_repo.get_user_by_email.assert_called_once_with(mock_user.email)


def test_get_user_by_email_not_found(user_service, mock_user_repo):
    mock_user_repo.get_user_by_email.return_value = None

    email = "missing@example.com"
    result = user_service.get_user_by_email(email)

    assert result is None
    mock_user_repo.get_user_by_email.assert_called_once_with(email)


def test_get_user_by_id_found(mocker, user_service, mock_user_repo):
    mock_user = UserFactory.build()
    mock_user_repo.get_by_user_id.return_value = mock_user

    # Patch ensure_uuid to just return the same UUID
    test_uuid = mock_user.id
    mocker.patch("app.services.user.ensure_uuid", return_value=test_uuid)

    result = user_service.get_user_by_id(test_uuid)

    assert result == mock_user
    mock_user_repo.get_by_user_id.assert_called_once_with(test_uuid)


def test_get_user_by_id_not_found(mocker, user_service, mock_user_repo):
    mock_user_repo.get_by_user_id.return_value = None

    test_uuid = uuid.uuid4()
    mocker.patch("app.services.user.ensure_uuid", return_value=test_uuid)

    result = user_service.get_user_by_id(test_uuid)

    assert result is None
    mock_user_repo.get_by_user_id.assert_called_once_with(test_uuid)

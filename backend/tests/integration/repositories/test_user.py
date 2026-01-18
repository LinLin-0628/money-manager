import datetime
import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User
from tests.factories.user import UserFactory

pytestmark = pytest.mark.integration


def test_get_user_by_email_return_user_when_email_exists(db_session, user_repo):
    # Arrange: insert a user into the test DB
    test_email = "test_email@gmail.com"
    test_name = "test_name"
    UserFactory.create(email=test_email, name=test_name)

    # Act: retrieve user by email
    user = user_repo.get_user_by_email(test_email)

    # Assert
    assert user is not None
    assert isinstance(user, User)

    assert user.email == test_email
    assert isinstance(user.email, str)

    assert user.name == test_name
    assert isinstance(user.name, str)


def test_get_user_by_email_return_none_when_not_found(db_session, user_repo):
    user = user_repo.get_user_by_email("non-exist@gmail.com")

    assert user is None


def test_get_user_by_id_return_user_when_id_exists(db_session, user_repo):
    # Arrange: insert a user into the test DB
    test_email = "test_email@gmail.com"
    test_name = "test_name"
    created_user = UserFactory.create(email=test_email, name=test_name)

    # Act: retrieve user by id
    user = user_repo.get_by_user_id(created_user.id)

    # Assert
    assert user is not None
    assert isinstance(user, User)

    assert user.id == created_user.id
    assert isinstance(user.id, uuid.UUID)

    assert user.email == test_email
    assert isinstance(user.email, str)

    assert user.name == test_name
    assert isinstance(user.name, str)


def test_get_user_by_id_return_none_when_not_found(db_session, user_repo):
    random_id = uuid.uuid4()
    user = user_repo.get_by_user_id(random_id)

    assert user is None


def test_create_user_user_into_db_success(db_session, user_repo):
    user = UserFactory.build()  # build, not create

    created = user_repo.create_user(user)

    assert created is not None
    assert created.id is not None
    assert isinstance(created.id, uuid.UUID)

    # Verify it actually exists in DB
    db_user = db_session.get(User, created.id)
    assert db_user is not None
    assert db_user.email == created.email
    assert db_user.hashed_password is not None
    assert db_user.created_at is not None
    assert db_user.updated_at is not None
    assert isinstance(db_user.created_at, datetime.datetime)
    assert isinstance(db_user.updated_at, datetime.datetime)


def test_create_user_raises_error_on_duplicate_email(db_session, user_repo):
    email = "duplicate@example.com"

    user1 = UserFactory.build(email=email)
    user2 = UserFactory.build(email=email)

    user_repo.create_user(user1)

    with pytest.raises(IntegrityError):
        user_repo.create_user(user2)

import pytest

from app.repositories.user import UserRepository


@pytest.fixture
def user_repo(db_session):
    """
    Returns a UserRepository instance bound to the test DB session.
    """
    return UserRepository(db_session)

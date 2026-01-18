import pytest

from app.repositories.user import UserRepository
from tests.factories.user import UserFactory


@pytest.fixture(scope="function", autouse=True)
def set_factory_session(db_session):
    """
    Automatically sets the session for all factories
    at the start of each test.
    """
    UserFactory._meta.sqlalchemy_session = db_session
    yield
    # Optional: Clear it out after the test to stay clean


@pytest.fixture
def user_repo(db_session):
    """
    Returns a UserRepository instance bound to the test DB session.
    """
    return UserRepository(db_session)

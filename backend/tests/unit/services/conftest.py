import pytest

from app.services.user import UserService


@pytest.fixture
def mock_user_repo(mocker):
    repo = mocker.Mock()
    repo.db = mocker.Mock()

    return repo


@pytest.fixture
def user_service(mock_user_repo):
    return UserService(user_repo=mock_user_repo)

import pytest
from fastapi.testclient import TestClient

from app.db.database import get_db
from main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def override_dependencies(db_session):
    """
    Override dependencies for testing.
    """

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    yield

    app.dependency_overrides = {}

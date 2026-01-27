import pytest
from fastapi.testclient import TestClient

from app.db.database import get_db
from main import app
from tests.test_routes import _test_router


@pytest.fixture()
def client():
    app.include_router(_test_router)

    if not getattr(app.state, "_test_routes_included", False):
        app.include_router(_test_router)
        app.state._test_routes_included = True

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

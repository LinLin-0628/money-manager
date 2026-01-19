import pytest

from tests.conftest import FACTORIES


@pytest.fixture(scope="function", autouse=True)
def set_factory_session(request, db_session):
    """
    Automatically sets the session for all factories
    at the start of each test and clears it after.
    """

    use_db = "db" in {marker.name for marker in request.node.iter_markers()}

    if use_db:
        # Only get db_session fixture if we actually need it
        for factory in FACTORIES:
            factory._meta.sqlalchemy_session = db_session

    yield

    # Teardown: Remove the session reference to ensure isolation
    for factory in FACTORIES:
        factory._meta.sqlalchemy_session = None

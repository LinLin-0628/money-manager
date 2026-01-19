from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.logging import LOGGING_CONFIG, setup_logging
from app.core.settings import settings
from tests.factories.user import UserFactory

LOG_DIR = Path("logs")
SESSION_LOG_FILE = LOG_DIR / "test.log"

FACTORIES = [UserFactory]


def pytest_collection_modifyitems(config, items):
    for item in items:
        test_path = Path(item.nodeid.split("::")[0])  # Get just the file path part

        if "unit" in test_path.parts:
            item.add_marker(pytest.mark.unit)

        elif "integration" in test_path.parts:
            item.add_marker(pytest.mark.integration)

        elif "e2e" in test_path.parts:
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    LOG_DIR.mkdir(exist_ok=True, parents=True)

    if SESSION_LOG_FILE.exists():
        SESSION_LOG_FILE.unlink()

    # Override the file handler in your logging config
    LOGGING_CONFIG["handlers"]["file"]["filename"] = str(SESSION_LOG_FILE)

    # Setup logging to use this session file
    setup_logging()

    yield SESSION_LOG_FILE


# SQLAlchemy engine for the test DB


@pytest.fixture(scope="session")
def db_engine():
    """
    Session-scoped engine. Runs Alembic migrations once per test session.
    """
    engine = create_engine(settings.database_url)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")  # apply all migrations

    yield engine

    command.downgrade(alembic_cfg, "base")
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Creates a new database session for a test.
    Each test runs inside a nested transaction (SAVEPOINT), rolled back after the test.
    """
    connection = db_engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = Session()

    # Start with a nested transaction
    nested = connection.begin_nested()

    # listen for session commits and restart SAVEPOINT automatically
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction_):
        nonlocal nested
        if transaction_.nested and not transaction_.parent.nested:
            # Restart the savepoint after it ends (commit or rollback)
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        event.remove(session, "after_transaction_end", restart_savepoint)
        transaction.rollback()
        connection.close()

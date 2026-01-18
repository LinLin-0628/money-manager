from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.logging import LOGGING_CONFIG, setup_logging
from app.core.settings import settings

LOG_DIR = Path("logs")
SESSION_LOG_FILE = LOG_DIR / "test.log"


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
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session")
def db_engine():
    """
    Session-scoped engine. Runs Alembic migrations once per test session.
    """
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")  # apply all migrations

    yield engine

    command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
        session.rollback()
    finally:
        session.close()

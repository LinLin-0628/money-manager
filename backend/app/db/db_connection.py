import logging
import sys

from sqlalchemy import text

from app.db.database import engine  # your engine object

logger = logging.getLogger(__name__)


def test_db_connection() -> None:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info("Database connection successful, result=%s", value)

    except Exception as exc:
        logger.exception("Database connection failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    test_db_connection()

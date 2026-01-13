import logging
import logging.config
import time
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter

from app.core.logging_context import request_id_ctx_var
from app.core.settings import settings

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"


class UTCJsonFormatter(JsonFormatter):
    """JSON formatter that uses UTC time"""

    converter = time.gmtime  # type: ignore[assignment]


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get()
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id_filter": {
            "()": RequestIDFilter,
        },
    },
    "formatters": {
        "json": {
            "()": UTCJsonFormatter,
            "fmt": "%(asctime)s %(levelname)s %(request_id)s %(name)s %(message)s",
        },
        "console": {
            "format": "%(asctime)s - %(levelname)s - [%(request_id)s] - %(name)s - %(message)s",  # noqa: E501
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filters": ["request_id_filter"],
            "filename": str(LOG_FILE),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "filters": ["request_id_filter"],
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "DEBUG" if settings.debug else "INFO",
        "handlers": ["file", "console"],
    },
}


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

import logging
import logging.config
import time
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter

from app.core.logging_context import request_id_ctx_var
from app.core.settings import settings

LOG_DIR = Path(settings.log_dir)
LOG_FILE_TEXT = LOG_DIR / settings.log_file_text
LOG_FILE_JSON = LOG_DIR / settings.log_file_json

# Dynamic log levels
FILE_LEVEL = logging.DEBUG if settings.debug else logging.INFO
CONSOLE_LEVEL = logging.INFO  # ALWAYS INFO or above


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
    # ─────────────────────────────────────────────
    # Filters
    # ─────────────────────────────────────────────
    "filters": {
        "request_id_filter": {"()": RequestIDFilter},
    },
    # ─────────────────────────────────────────────
    # Formatters
    # ─────────────────────────────────────────────
    "formatters": {
        "json": {
            "()": UTCJsonFormatter,
            "fmt": "%(asctime)s %(levelname)s %(request_id)s %(name)s %(message)s",
        },
        "text": {
            "format": (
                "%(asctime)s - %(levelname)s - [%(request_id)s] "
                "- %(name)s - %(message)s"
            ),
        },
        "console": {
            "format": (
                "%(asctime)s - %(levelname)s - [%(request_id)s] "
                "- %(name)s - %(message)s"
            ),
        },
    },
    # ─────────────────────────────────────────────
    # Handlers
    # ─────────────────────────────────────────────
    "handlers": {
        # JSON log file
        "file_json": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filters": ["request_id_filter"],
            "filename": str(LOG_FILE_JSON),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "level": FILE_LEVEL,
        },
        # Text log file
        "file_text": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "text",
            "filters": ["request_id_filter"],
            "filename": str(LOG_FILE_TEXT),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "level": FILE_LEVEL,
        },
        # Console terminal log
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "filters": ["request_id_filter"],
            "stream": "ext://sys.stdout",
            "level": CONSOLE_LEVEL,
        },
    },
    # ─────────────────────────────────────────────
    # Root Logger
    # ─────────────────────────────────────────────
    "root": {
        "level": "DEBUG",
        "handlers": ["file_json", "file_text", "console"],
    },
}


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

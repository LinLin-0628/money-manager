import logging
import logging.config
import time
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter

from app.core.settings import settings

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"

class UTCJsonFormatter(JsonFormatter):
    """JSON formatter that uses UTC time"""
    converter = time.gmtime

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": UTCJsonFormatter,
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": str(LOG_FILE),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": "DEBUG" if settings.debug else "INFO",
        "handlers": ["file"],
    },
}


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

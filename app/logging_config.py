"""Central logging configuration."""
from __future__ import annotations

from logging.config import dictConfig

from app.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure structured logging for the application."""

    log_level = settings.log_level.upper()
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
    dictConfig(config)


__all__ = ["configure_logging"]

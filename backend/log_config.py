import logging
import logging.config

from config import settings  # Import the settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": settings.LOG_LEVEL,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
            "propagate": True,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

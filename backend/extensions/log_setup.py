#
# FinalWall - A logging setup for the backend server.
# Author: Dayeya.
#

import json
import logging
import logging.config

from pathlib import Path

LOGGING_ROOT_DIR = Path(__file__).parent.parent
LOGGING_CONFIG = LOGGING_ROOT_DIR / "logs" / "config.json"


def setup_logging():
    """Sets up the logging configuration."""
    try:
        with open(LOGGING_CONFIG, "r") as cnf:
            config = json.load(cnf)
    except FileNotFoundError:
        return
    logging.config.dictConfig(config)


def create_logger(**kwargs) -> logging.Logger:
    """Sets up the configuration and creates a logger."""
    setup_logging()
    return logging.getLogger(**kwargs)

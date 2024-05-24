import json
import logging
from pathlib import Path

LOGGING_ROOT_DIR = Path(__file__).parent.parent
LOGGING_CONFIG = LOGGING_ROOT_DIR / "fwlogging" / "logging_config.json"


def setup_logging():
    """Sets up the logging configuration."""
    try:
        with open(LOGGING_CONFIG, "r") as cnf:
            config = json.load(cnf)
    except FileNotFoundError:
        """Set base config."""
        print("Logging setup aborted.")
        return

    import logging.config

    logging.config.dictConfig(config)


def create_logger(**kwargs) -> logging.Logger:
    """Sets up the configuration and creates a logger."""
    setup_logging()
    return logging.getLogger(**kwargs)

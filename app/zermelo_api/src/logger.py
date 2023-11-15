import logging
import logging.handlers
from logging import DEBUG, INFO
from os import path, mkdir

FOLDER = "log"
FILE = "info"


def makeLogger(name: str = None, LOG_LEVEL: int = INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    if not path.isdir(FOLDER):
        mkdir(FOLDER)
    filename = path.join(FOLDER, f"{FILE}.log")

    # create console handler and set level to debug
    handler = logging.handlers.TimedRotatingFileHandler(
        filename, when="W4", backupCount=3, encoding="utf-8"
    )
    handler.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

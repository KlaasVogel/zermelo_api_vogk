import logging
import logging.handlers
from logging import Logger
from logging import DEBUG, INFO
from os import path, mkdir
from traceback import format_exc

FOLDER = "log"
FILE = "info"


class MyLogger(Logger):
    def trace(self):
        self.error(format_exc())


def makeLogger(name: str = None, LOG_LEVEL: int = INFO) -> MyLogger:
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

    logger.__class__ = MyLogger

    return logger

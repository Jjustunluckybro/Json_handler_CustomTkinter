import logging
from logging import handlers

LOGGER_FORMAT = '%(asctime)s - %(name)s:%(levelname)s - %(message)s'
LOG_FILE_PATH = "data/logs/logs.log"


def init_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console logger
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(LOGGER_FORMAT))
    sh.setLevel(logging.DEBUG)
    # File logger
    fh = handlers.RotatingFileHandler(filename=LOG_FILE_PATH, maxBytes=1800, backupCount=1)
    fh.setFormatter(logging.Formatter(LOGGER_FORMAT))
    fh.setLevel(logging.INFO)

    logger.addHandler(sh)
    logger.addHandler(fh)

    logger.info("Logger was init")
    return logger

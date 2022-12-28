import logging


def init_logger():
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
    return logger

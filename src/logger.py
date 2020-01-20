import logging
from src.constants import Logger


def get_logger(name: str) -> logging:
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # File Handler
    file_handler = logging.FileHandler(Logger.NAME)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    # Add Handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

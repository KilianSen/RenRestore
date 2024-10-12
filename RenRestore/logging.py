import logging

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def get_logger() -> logging.Logger:
    return _logger

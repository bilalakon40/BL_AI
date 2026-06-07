import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
)

logger = logging.getLogger('trading_platform')


def get_logger(name: str) -> logging.Logger:
    return logger.getChild(name)

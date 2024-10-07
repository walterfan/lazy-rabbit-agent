import logging
import os
import sys

def create_logger(filename, log2console=True, logLevel=logging.INFO, logFolder='./logs'):
    # add log
    logger = logging.getLogger(filename)
    logger.setLevel(logLevel)
    formats = '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formats)

    logfile = os.path.join(logFolder, filename + '.log')
    directory = os.path.dirname(logfile)
    if not os.path.exists(directory):
        os.makedirs(directory)

    handler = logging.FileHandler(logfile)
    handler.setLevel(logLevel)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log2console:
        handler2 = logging.StreamHandler(sys.stdout)
        handler2.setFormatter(logging.Formatter(formats))
        handler2.setLevel(logLevel)
        logger.addHandler(handler2)

    return logger

logger = create_logger("lazy_rabbit_agent", True, logging.DEBUG)
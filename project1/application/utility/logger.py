import logging
import logging.handlers
import os
import sys


def get_logger(name='root'):
    logger = logging.getLogger(name)

    if not logger.handlers:  # if logger 'name' already exists
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(filename)-18s %(levelname)-8s: %(message)s', '%Y-%m-%dT%T%Z')
        handler = logging.StreamHandler()   # stdout
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if logger.name == 'root':
            logger.warning('Running: %s %s', os.path.basename(sys.argv[0]), ' '.join(sys.argv[1:]))

    return logger





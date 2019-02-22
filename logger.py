import logging

logging.basicConfig(filename='../caressa.log', level=logging.DEBUG)


def get_logger():
    return logging.getLogger()

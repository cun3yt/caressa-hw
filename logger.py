import logging

logging.basicConfig(filename='../.caressa.log',
                    level=logging.DEBUG,
                    format='%(asctime)s > %(levelname)s:%(name)s: %(message)s:%(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p (%Z)')


def get_logger():
    return logging.getLogger()

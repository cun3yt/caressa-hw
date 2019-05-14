from logger import get_logger


logger = get_logger()


def init(dsn):
    logger.info("sentry init is called.")

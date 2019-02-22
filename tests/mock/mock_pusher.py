from logger import get_logger


logger = get_logger()


class _Connection:
    def __init__(self):
        self.handlers = {}

    def bind(self, event, handler_fn):
        logger.info("_Connection-bind")
        self.handlers[event] = handler_fn


class Pusher:
    def __init__(self, **kwargs):
        self._connection = _Connection()
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def subscribe(self, id):
        logger.info("subscribe::{}".format(id))
        return self._connection

    @property
    def connection(self):
        logger.info("Pusher-connection")
        return self._connection

    def connect(self):
        logger.info("Pusher-connect")

class Thread:
    def __init__(self, target, args=(), kwargs=None):
        self.target = target
        self.args = args
        self.kwargs = kwargs if isinstance(kwargs, dict) else {}

    def start(self):
        self.target(*self.args, **self.kwargs)

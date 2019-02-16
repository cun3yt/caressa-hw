class Thread:
    def __init__(self, target):
        self.target = target

    def start(self):
        self.target()

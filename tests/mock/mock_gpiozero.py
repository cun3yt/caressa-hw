class Button:
    def __init__(self, id):
        self.id = id
        self.when_pressed = lambda: None

    def press(self):
        return self.when_pressed()

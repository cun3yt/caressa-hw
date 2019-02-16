class Led:
    ON = 'On'
    OFF = 'Off'
    BLINK = 'Blink'

    POSSIBLE_STATES = [ON, OFF, BLINK, ]

    def __init__(self):
        self.state = self.ON

    def set_state(self, state):
        assert state in self.POSSIBLE_STATES, (
            "%s is not one of the possible states" % state
        )
        self.state = state


class Button:
    def __init__(self):
        self.debounce_time = 0
        self.on_press_fn = lambda *args, **kwargs: None

    def on_press(self, fn):
        self.on_press_fn = fn

    def press(self, *args, **kwargs):
        self.on_press_fn(*args, **kwargs)


class voicehat:
    LED = Led()
    BUTTON = Button()

    @classmethod
    def get_led(cls):
        return cls.LED

    @classmethod
    def get_button(cls):
        return cls.BUTTON

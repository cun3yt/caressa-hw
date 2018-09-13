from gpiozero import LED, Button
from signal import pause


class LedWithState:
    def __init__(self, port):
        self.state = False
        self.led = LED(port)

    def toggle(self):
        if self.state:
            self.led.off()
        else:
            self.led.on()
        self.state = not self.state


class LedWithButton:
    def __init__(self, led_id, button_id):
        self.led = LedWithState(led_id)
        self.button = Button(button_id)
        self.button.when_activated = self._btn_action

    def _btn_action(self):
        self.led.toggle()


led = LedWithButton(17, 2)

pause()

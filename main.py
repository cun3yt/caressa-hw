from gpiozero import LED, Button
from signal import pause
from inspect import stack as call_stack
from omxplayer.player import OMXPlayer
from pathlib import Path


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


class AudioPlayer:
    # "omxplayer ./sample_audio_small.mp3 -o local --pos 00:00:25"

    def __init__(self):
        self.audio_file = Path('/home/pi/sample_audio_small.mp3')
        self.state = False

    def _play(self):
        print('{} is called'.format(call_stack()[0][3]))
        self.player = OMXPlayer(self.audio_file, args=['-o', 'local'])
        pass

    def _stop(self):
        print('{} is called'.format(call_stack()[0][3]))
        self.player.quit()
        pass

    def toggle(self):
        if self.state:
            self._stop()
        else:
            self._play()
        self.state = not self.state


class Environment:
    def __init__(self, led_id, button_id):
        self.led = LedWithState(led_id)
        self.button = Button(button_id)
        self.player = AudioPlayer()
        self.button.when_activated = self._btn_action

    def _btn_action(self):
        self.player.toggle()
        self.led.toggle()


led = Environment(17, 2)

pause()

import os
import subprocess
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


class AudioPlayer:
    def __init__(self):
        self.audio_file = '~/sample_audio_small.mp3'
        self.process = None
        self.state = False

    def _play(self):
        # "omxplayer ./sample_audio_small.mp3 -o local --pos 00:00:25"
        cmd = 'omxplayer -o local {file}'.format(file=self.audio_file)
        self.process = subprocess.Popen(cmd, shell=True)
        print('process id: {}'.format(self.process.pid))

    def _stop(self):
        cmd = 'killall omxplayer.bin'
        os.system(cmd)
        print('must be terminated with this: {}'.format(cmd))

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

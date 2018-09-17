from gpiozero import LED, Button
from signal import pause
from inspect import stack as call_stack
from omxplayer.player import OMXPlayer
from collections import deque as Q
import logging
import requests
from utils import deep_get
from audio_client import AudioClient
import json

logging.basicConfig(level=logging.INFO)

player_log = logging.getLogger("player_log")


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
    # self._player = OMXPlayer(self.audio_file, args=['-o', 'local'], pause=True)

    def __init__(self, api_client):
        self.client = api_client

        self.token = None
        self._player = None

        self.queue = Q()

        self.state = False

    def fetch_from_queue(self):
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    def queue_up(self, token):
        response = self.client.send_playback_nearly_finished_signal()
        res_body = json.loads(response.text)
        directive = deep_get(res_body, 'response.directives')[0]
        assert(deep_get(directive, 'type') == 'AudioPlayer.Play')
        assert(deep_get(directive, 'playBehavior') == 'ENQUEUE')

        stream = deep_get(directive, 'audioItem.stream')

        assert(stream.get('expectedPreviousToken') == self.token)

        self.queue.append({
            'url': stream.get('url'),
            'token': stream.get('token'),
            'offset_in_seconds': stream.get('offsetInMilliseconds', 0) / 1000,
        })

    def _play(self):
        print('{} is called'.format(call_stack()[0][3]))

        response = self.client.launch()

        res_body = json.loads(response.text)

        print(type(res_body), res_body)

        directive = deep_get(res_body, 'response.directives')[0]
        assert(deep_get(directive, 'type') == 'AudioPlayer.Play')

        audio_url = deep_get(directive, 'audioItem.stream.url')
        token = deep_get(directive, 'audioItem.stream.token')
        offset_in_seconds = deep_get(directive, 'audioItem.stream.offsetInMilliseconds', 0) / 1000

        if self._player is None:
            self._player = OMXPlayer(audio_url, args=['-o', 'local'], pause=True)
        else:
            self._player.load(audio_url, pause=True)

        self._player.set_position(offset_in_seconds)
        self._player.play()
        self.token = token

        self.queue_up(token=token)

    def _pause(self):
        print('{} is called'.format(call_stack()[0][3]))
        self._player.pause()
        self.client.pause()
        # offset_in_seconds = self._player.position

    def play_pause(self):
        if self.state:
            self._pause()
        else:
            self._play()

        self.state = not self.state

    def next(self):
        print('{} is called'.format(call_stack()[0][3]))
        # if self._player is None:
        #     return
        # self._play()


class Environment:
    def __init__(self, led_id, play_btn_id, next_btn_id):
        self.led = LedWithState(led_id)

        client = AudioClient(url='https://cmertayak.serveo.net/streaming')
        self.player = AudioPlayer(client)

        self.play_btn = Button(play_btn_id)
        self.play_btn.when_activated = self._play_pause

        self.next_btn = Button(next_btn_id)
        self.next_btn.when_activated = self._next

    def _play_pause(self):
        self.player.play_pause()
        self.led.toggle()

    def _next(self):
        self.player.next()
        print('next...')


led = Environment(17, 2, 3)

pause()

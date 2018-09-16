from gpiozero import LED, Button
from signal import pause
from inspect import stack as call_stack
from omxplayer.player import OMXPlayer
from collections import deque as Q
from datetime import timedelta
import logging
import requests

logging.basicConfig(level=logging.INFO)

player_log = logging.getLogger("player_log")


class Utils:
    @staticmethod
    def sec_to_hours(sec):
        return str(timedelta(seconds=sec))


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


class Server:
    def __init__(self):
        self.data = [
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Zamfir/08+La+Valse+Muzeta.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Zamfir/06+La+Paloma.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Zamfir/03+Clair+De+Lune.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/World/Tamure+Tahitien/11+Motu+Painu.mp3',
            'https://s3-us-west-1.amazonaws.com/caressa-prod/song-set/Wedding/'
            'Various+-+Baroque+for+Brides+To+Be+-+11+-+Clarke-+Trumpet+Voluntary.mp3',
        ]
        self.item = 0
        self.offset = 0

    def get_item(self):
        return {
            'token': self.item,
            'url': self.data[self.item],
            'offset': self.offset,
        }

    def next_item(self, token):
        next_token = token+1 if isinstance(token, int) else 0
        next_token = next_token if next_token < len(self.data) else 0

        return {
            'token': next_token,
            'url': self.data[next_token],
        }

    def set_state(self, token, offset=0):
        self.item = token
        self.offset = offset


class AudioPlayer:
    # "omxplayer ./sample_audio_small.mp3 -o local --pos 00:00:25"
    # self._player = OMXPlayer(self.audio_file, args=['-o', 'local'], pause=True)

    def __init__(self, server):
        self.client = server

        self.token = None
        self._player = None

        self.queue = Q()
        self.queue_up()

        self.state = False

    def fetch_from_queue(self):
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    def queue_up(self):
        item = self.client.next_item(self.token) if self.token else self.client.get_item()
        self.queue.append(item)

        token = item.get('token')
        next_item = self.client.next_item(token)
        self.queue.append(next_item)

    def _play(self):
        print('{} is called'.format(call_stack()[0][3]))

        item = self.fetch_from_queue()

        if item is None:
            self.queue_up()
            item = self.fetch_from_queue()

        url = item.get('url')
        token = item.get('token')

        if self._player is None:
            self._player = OMXPlayer(url, args=['-o', 'local'], pause=True)
        else:
            self._player.load(url, pause=True)

        self._player.play()

        self.token = token
        self.client.set_state(self.token)

    def _pause(self):
        print('{} is called'.format(call_stack()[0][3]))
        self._player.pause()
        offset = self._player.position
        self.client.set_state(self.token, offset)

    def play_pause(self):
        if self.state:
            self._pause()
        elif self._player is None:
            self._play()
        else:
            self._player.play()
        self.state = not self.state

    def next(self):
        print('{} is called'.format(call_stack()[0][3]))
        if self._player is None:
            return
        self._play()


class Environment:
    def __init__(self, led_id, play_btn_id, next_btn_id):
        server = Server()
        self.led = LedWithState(led_id)
        self.player = AudioPlayer(server)

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

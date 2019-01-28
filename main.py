import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib     # Gdk, GObject,

from gpiozero import Button, LED
from threading import Thread

from audio_client import AudioClient
from audio_player import AudioPlayer
from settings import pusher, SUBDOMAIN as SERVER_URL
from phone_service import make_urgency_call

import json


LEFT_BLACK_BTN_ID = 7
RIGHT_BLACK_BTN_ID = 8
BIG_RED_BTN_ID = 9
SMALL_RED_BTN_ID = 10


with open('config.json') as json_data_file:
    conf = json.load(json_data_file)

client = AudioClient(url=SERVER_URL,
                     user_id=conf['user']['id'],
                     user_password=conf['user']['hash'],
                     device_id=conf['hardware']['id'],
                     client_id=conf['api']['client_id'],
                     client_secret=conf['api']['client_secret'], )
channels_response = client.get_channels()

channels_response_body = json.loads(channels_response.text)
user_channels = channels_response_body['channels']

player = AudioPlayer(client)

volume_up_btn = Button(RIGHT_BLACK_BTN_ID)
volume_up_btn.when_pressed = player.volume_up

volume_down_btn = Button(LEFT_BLACK_BTN_ID)
volume_down_btn.when_pressed = player.volume_down

next_btn = Button(BIG_RED_BTN_ID)
next_btn.when_pressed = player.next_command

emergency_btn = Button(SMALL_RED_BTN_ID)
emergency_btn.when_pressed = make_urgency_call


def connect_handler(*args, **kwargs):
    print('connect_handler')

    for channel_id in user_channels:
        channel = pusher.subscribe(channel_id)
        channel.bind('voice_mail', player.voice_mail_arrived)
        channel.bind('urgent_mail', player.urgent_mail_arrived)
        print("connected to {channel_id}".format(channel_id=channel_id))


def setup_realtime_update():
    pusher.connection.bind('pusher:connection_established', connect_handler)
    pusher.connect()
    print('pusher is connected')


def main():
    Thread(target=setup_realtime_update).start()
    Gtk.main()


if __name__ == '__main__':
    main()

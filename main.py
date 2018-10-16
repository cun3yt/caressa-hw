import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib     # Gdk, GObject,

from gpiozero import Button, LED
import time
from threading import Thread

from audio_client import AudioClient
from audio_player import AudioPlayer
from settings import pusher, SUBDOMAIN
from phone_service import make_urgency_call


SERVER_URL = '{}/streaming'.format(SUBDOMAIN)
USER_ID = 1

user_channels = [
    'family.senior.{}'.format(USER_ID),
    'Channel.CA.Fremont.Facility.Brookdale',
]

_voice_processing_indicator = LED(7)


def set_processing_indicator():
    _voice_processing_indicator.blink()


def set_processing_off_indicator():
    _voice_processing_indicator.off()


client = AudioClient(url=SERVER_URL)
player = AudioPlayer(client,
                     processing_indicator_fn=set_processing_indicator,
                     processing_off_indicator=set_processing_off_indicator)

volume_up_btn = Button(8)
volume_up_btn.when_pressed = player.volume_up

volume_down_btn = Button(9)
volume_down_btn.when_pressed = player.volume_down

next_btn = Button(10)
next_btn.when_pressed = lambda *args, **kwargs: print('next btn pressed')

emergency_btn = Button(11)
emergency_btn.when_pressed = make_urgency_call


def connect_handler(*args, **kwargs):
    print('connect_handler')

    for channel in user_channels:
        channel = pusher.subscribe(channel)
        channel.bind('voice_mail', player.voice_mail_arrived)
        channel.bind('urgent_mail', player.urgent_mail_arrived)


def setup_realtime_update():
    pusher.connection.bind('pusher:connection_established', connect_handler)
    pusher.connect()
    print('pusher is connected')


def main():
    Thread(target=setup_realtime_update).start()
    Gtk.main()


if __name__ == '__main__':
    main()

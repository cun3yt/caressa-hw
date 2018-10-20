import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib     # Gdk, GObject,

from gpiozero import Button, LED
from threading import Thread

from audio_client import AudioClient
from audio_player import AudioPlayer
from settings import pusher, SUBDOMAIN
from phone_service import make_urgency_call


SERVER_URL = '{}/streaming'.format(SUBDOMAIN)
USER_ID = 1

LEFT_BLACK_BTN_ID = 7
RIGHT_BLACK_BTN_ID = 8
BIG_RED_BTN_ID = 9
SMALL_RED_BTN_ID = 10


user_channels = [
    'family.senior.{}'.format(USER_ID),
    'Channel.CA.Fremont.Facility.Brookdale',
]


def set_processing_indicator():
    print('set_processing_indicator blink')
    # _voice_processing_indicator.blink()


def set_processing_off_indicator():
    print('set_processing_indicator off')
    # _voice_processing_indicator.off()


client = AudioClient(url=SERVER_URL)
player = AudioPlayer(client,
                     processing_indicator_fn=set_processing_indicator,
                     processing_off_indicator=set_processing_off_indicator)


volume_up_btn = Button(RIGHT_BLACK_BTN_ID)
volume_up_btn.when_pressed = player.volume_up

volume_down_btn = Button(LEFT_BLACK_BTN_ID)
volume_down_btn.when_pressed = player.volume_down

next_btn = Button(BIG_RED_BTN_ID)
next_btn.when_pressed = lambda *args, **kwargs: print('next btn pressed')

emergency_btn = Button(SMALL_RED_BTN_ID)
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib     # Gdk, GObject,

import aiy.audio
import aiy.cloudspeech
from list_player_vlc import ListPlayer, Audio
from datetime import datetime

from settings import API_URL
import requests
import time


SERVER_URL = '{}/speech-to-text'.format(API_URL)


lp = ListPlayer()


def record_to_wave(filepath, duration):
    """Records an audio for the given duration to a wave file."""
    recorder = aiy.audio.get_recorder()
    dumper = aiy.audio._WaveDump(filepath, duration)

    with recorder, dumper:
        recorder.add_processor(dumper)
        while not dumper.is_done():
            time.sleep(0.1)


def _generate_now_str():
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")


def stt(*args, **kwargs):
    file_path = '/tmp/{}.wave'.format(_generate_now_str())
    print('Listening...')

    record_to_wave(file_path, 4)

    print('Sending')
    file_p = open(file_path, 'rb')
    try:
        r = requests.post(SERVER_URL, files={'file': file_p})
        response_file = '/tmp/response-{}.mp3'.format(_generate_now_str())
        with open(response_file, 'wb') as f_response:
            f_response.write(r.content)
        lp.add_content(content=Audio(url=response_file), to_top=True)
    finally:
        file_p.close()

    print('Done...')


def main():
    lp.add_content(
        content=Audio(url='https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/'
                          'update-with-question.mp3',
                      follow_up_fn=stt)
    )

    lp.add_content(
        content=Audio(url='https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/'
                          'update-with-question.mp3',
                      follow_up_fn=stt)
    )

    lp.play()

    Gtk.main()


if __name__ == '__main__':
    main()

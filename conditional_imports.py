from settings import ENV


def get_list_player_dependencies():
    if ENV != 'test':
        import gi
        import vlc

        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, GLib  # Gdk, GObject,
        from threading import Thread
        return gi, vlc, Gtk, GLib, Thread

    import tests.mock.mock_gi as gi
    from tests.mock import mock_vlc as vlc

    gi.require_version('Gtk', '3.0')
    from tests.mock.mock_gi.repository import Gtk, GLib     # Gdk, GObject,
    from tests.mock.mock_threading import Thread
    return gi, vlc, Gtk, GLib, Thread


def get_audio_player_dependencies():
    if ENV != 'test':
        from subprocess import call as os_call
        from threading import Thread
        from alsaaudio import Mixer as AlsaMixer, mixers as alsa_mixers
        from aiy import voicehat
        return os_call, Thread, AlsaMixer, alsa_mixers, voicehat

    from tests.mock.mock_subprocess import call as os_call
    from tests.mock.mock_threading import Thread
    from tests.mock.mock_alsaaudio import Mixer as AlsaMixer, mixers as alsa_mixers
    from tests.mock.mock_aiy import voicehat
    return os_call, Thread, AlsaMixer, alsa_mixers, voicehat


def get_phone_service():
    if ENV != 'test':
        from twilio.rest import Client
        return Client

    from tests.mock.mock_twilio.rest import Client
    return Client


def get_main_dependencies():
    if ENV != 'test':
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, GLib  # Gdk, GObject,
        from gpiozero import Button
        from threading import Thread
        from pysher import Pusher
        config_filename = 'config.json'
        return gi, Gtk, GLib, Button, Thread, Pusher, config_filename

    import tests.mock.mock_gi as gi
    gi.require_version('Gtk', '3.0')
    from tests.mock.mock_gi.repository import Gtk, GLib  # Gdk, GObject,
    from tests.mock.mock_gpiozero import Button
    from tests.mock.mock_threading import Thread
    from tests.mock.mock_pusher import Pusher
    config_filename = 'tests/mock/mock-config.json'
    return gi, Gtk, GLib, Button, Thread, Pusher, config_filename

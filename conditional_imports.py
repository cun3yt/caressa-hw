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


def get_button_dependencies():
    if ENV != 'test':
        from threading import Thread
        return Thread

    from tests.mock.mock_threading import Thread
    return Thread


def get_audio_player_dependencies():
    if ENV != 'test':
        from subprocess import call as os_call
        from threading import Thread
        from alsaaudio import Mixer as AlsaMixer, mixers as alsa_mixers
        from aiy import voicehat
        main_button_diff_time = 0.5
        return os_call, Thread, AlsaMixer, alsa_mixers, voicehat, main_button_diff_time

    from tests.mock.mock_subprocess import call as os_call
    from tests.mock.mock_threading import Thread
    from tests.mock.mock_alsaaudio import Mixer as AlsaMixer, mixers as alsa_mixers
    from tests.mock.mock_aiy import voicehat
    main_button_diff_time = 0
    return os_call, Thread, AlsaMixer, alsa_mixers, voicehat, main_button_diff_time


def get_main_dependencies():
    if ENV != 'test':
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, GLib  # Gdk, GObject,
        from gpiozero import Button
        from threading import Thread
        from pysher import Pusher
        import sentry_sdk
        return gi, Gtk, GLib, Button, Thread, Pusher, sentry_sdk

    import tests.mock.mock_gi as gi
    gi.require_version('Gtk', '3.0')
    from tests.mock.mock_gi.repository import Gtk, GLib  # Gdk, GObject,
    from tests.mock.mock_gpiozero import Button
    from tests.mock.mock_threading import Thread
    from tests.mock.mock_pusher import Pusher
    from tests.mock import mock_sentry_sdk as sentry_sdk
    return gi, Gtk, GLib, Button, Thread, Pusher, sentry_sdk

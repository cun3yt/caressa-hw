from settings import ENV


def get_list_player_dependencies():
    if ENV != 'test':
        import gi
        import vlc

        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, GLib  # Gdk, GObject,
        return gi, vlc, Gtk, GLib

    import tests.mock.mock_gi as gi
    from tests.mock import mock_vlc as vlc

    gi.require_version('Gtk', '3.0')
    from tests.mock.mock_gi.repository import Gtk, GLib     # Gdk, GObject,
    return gi, vlc, Gtk, GLib


def get_audio_player_dependencies():
    if ENV != 'test':
        from subprocess import call as os_call
        from threading import Thread
        from alsaaudio import Mixer as AlsaMixer, mixers as alsa_mixers
        from aiy import voicehat
        return os_call, Thread, AlsaMixer, alsa_mixers, voicehat, deep_get

    from tests.mock.mock_subprocess import call as os_call
    from tests.mock.mock_threading import Thread
    from tests.mock.mock_alsaaudio import Mixer as AlsaMixer, mixers as alsa_mixers
    from tests.mock.mock_aiy import voicehat
    return os_call, Thread, AlsaMixer, alsa_mixers, voicehat

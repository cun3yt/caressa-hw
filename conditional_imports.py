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

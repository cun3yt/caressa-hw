import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib     # Gdk, GObject,

import vlc
from collections import deque


# instance of this class must pause the play, collect the response and send it ...
class Audio:
    def __init__(self, url, follow_up_fn=None, *args):
        self._url = url
        self._follow_up = lambda: follow_up_fn(args) if follow_up_fn else None

    @property
    def url(self):
        return self._url

    @property
    def follow_up_fn(self):
        return self._follow_up


class ListPlayer:
    def __init__(self, *args, **kwargs):
        self.queue = deque()
        self.player = vlc.MediaPlayer()

        self._next_item_callback = kwargs.get('next_item_callback', lambda: 0)
        self._list_finished_callback = kwargs.get('list_finished_callback', lambda: 0)

        self._bind_default_events()
        self._content_follow_fn = None      # current content's follow up function if any

    def play(self, *args):
        if self.player.is_playing():
            return

        if self.player.get_state() == vlc.State.Paused:
            self.player.play()
            return

        if self._content_follow_fn:
            fn, self._content_follow_fn = self._content_follow_fn, None
            self.pause()
            fn()
            self.play()
            return

        if self.count < 1:
            self._list_finished_callback()
            return

        self.play_next()

    def play_next(self):
        self._content_follow_fn = None

        content = self.queue.popleft()  # type: Audio
        self._content_follow_fn = content.follow_up_fn

        def _play():
            self.player.set_mrl(mrl=content.url)
            self.player.play()
            self._next_item_callback()

        GLib.idle_add(lambda: _play())

    def pause(self):
        GLib.idle_add(lambda: self.player.pause())

    def add_content(self, content, to_top=False):
        if isinstance(content, dict):
            _content = Audio(url=content.get('url'), follow_up_fn=content.get('follow_up_fn'))
            self.queue.append(_content)
            return

        if to_top:
            self.queue.appendleft(content)
        else:
            self.queue.append(content)

    def is_playing(self):
        return self.player.is_playing()

    @property
    def count(self) -> int:
        return len(self.queue)

    def clean_playlist(self):
        self.queue.clear()

    def _bind_default_events(self):
        em = self.player.event_manager()
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self.play)

    def __str__(self):
        return "List Player with {} elements".format(self.count)


if __name__ == '__main__':
    lp = ListPlayer()

    def _internal(*args, **kwargs):
        print('hello!')

    lp.add_content(
        content=Audio(url='https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/test-song-1.mp3',
                      follow_up_fn=_internal))
    lp.add_content(
        content=Audio(url='https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/test-song-2.mp3'))
    lp.add_content(
        content=Audio(url='https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/test-song-3.mp3'))
    lp.add_content(
        content=Audio(url='https://s3-us-west-1.amazonaws.com/caressa-prod/development-related/test-song-4.mp3'))

    lp.play()

    Gtk.main()

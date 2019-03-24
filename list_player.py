from collections import deque
from conditional_imports import get_list_player_dependencies
from typing import Optional

gi, vlc, Gtk, GLib, Thread = get_list_player_dependencies()


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


# todo There is a need of system notification system (e.g. sounds/visuals): Loading, Updating, ...


class ListPlayer:
    def __init__(self, *args, **kwargs):
        self.queue = deque()
        self.player = vlc.MediaPlayer()

        self._injectable_content_list = None     # type: Optional['injectable_content.list.List']

        self._next_item_callback = kwargs.get('next_item_callback', lambda: 0)
        self._list_finished_callback = kwargs.get('list_finished_callback', lambda: 0)

        self._bind_default_events()
        self._content_follow_fn = None      # current content's follow up function if any

    def set_injectable_content_list(self, injectable_content_list):
        """
        This function has a side effect of downloading the content for the signed-in user

        :param injectable_content_list:
        :return:
        """
        self._injectable_content_list = injectable_content_list
        self._injectable_content_list.download()
        self._injectable_content_list.fetch_from_api()  # todo Not tested yet

    def play(self, *args):
        if self.player.is_playing():
            return

        if self.player.get_state() == vlc.State.Paused:
            self.player.play()
            return

        if self._content_follow_fn:     # todo: audit if this is the right place for this callback?
            fn, self._content_follow_fn = self._content_follow_fn, None
            self.pause()
            fn()
            self.play()
            return

        if self.count < 1:
            self._list_finished_callback()
            return

        self.play_next()

    def _fetch_injectable_content(self):
        """
        This function is overloaded in terms of responsibilities

        :return:
        """
        if not self._injectable_content_list:
            return None
        _content = self._injectable_content_list.fetch_one()
        if _content is None:
            return None
        _content.mark_delivery()

        # upload here.
        def _run_garbage_collection_and_upload():
            self._injectable_content_list.collect_garbage()
            self._injectable_content_list.upload()

        Thread(target=_run_garbage_collection_and_upload).start()

        # todo there is jingle_url also but not currently playable in list_player
        return Audio(url=_content.audio_url)

    def play_next(self):
        self._content_follow_fn = None

        content = self._fetch_injectable_content()

        # todo: What to do if the queue is empty??
        content = content if content else self.queue.popleft()  # type: Audio

        self._content_follow_fn = content.follow_up_fn

        def _play():
            self.player.set_mrl(mrl=content.url)
            self.player.play()
            self._next_item_callback()

        GLib.idle_add(lambda: _play())

    def pause(self):
        GLib.idle_add(lambda: self.player.pause())

    def add_content(self, content, to_top=False):
        if isinstance(content, str):
            content = Audio(url=content)

        if isinstance(content, dict):
            content = Audio(url=content.get('url'), follow_up_fn=content.get('follow_up_fn'))

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
        return "List Player with {} element(s)".format(self.count)


if __name__ == '__main__':
    lp = ListPlayer()

    def _internal(*args, **kwargs):
        print("hello!")

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

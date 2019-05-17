from collections import deque
from conditional_imports import get_list_player_dependencies
from typing import Optional, Union
from copy import deepcopy
from signals import ListPlayerConsumedSignal
from logger import get_logger
from audio.models import Audio, AggregateAudio

gi, vlc, Gtk, GLib, Thread = get_list_player_dependencies()

logger = get_logger()


# todo There is a need of system notification system (e.g. sounds/visuals): Loading, Updating, ...


class ListPlayer:
    def __init__(self, *args, **kwargs):
        self.queue = deque()
        self.vlc_player = vlc.MediaPlayer()

        self._injectable_content_list = None     # type: Optional['injectable_content.list.List']

        self._next_item_callback = kwargs.get('next_item_callback', lambda: 0)
        self._list_finished_callback = kwargs.get('list_finished_callback', lambda: 0)

        self._bind_default_events()

    def set_injectable_content_list(self, injectable_content_list):
        """
        This function has a side effect of downloading the content for the signed-in user

        :param injectable_content_list:
        :return:
        """
        self._injectable_content_list = injectable_content_list
        self._injectable_content_list.download()
        self._injectable_content_list.fetch_from_api()

    def play(self, *args):
        if self.vlc_player.is_playing():
            return None

        if self.vlc_player.get_state() == vlc.State.Paused:
            self.vlc_player.play()
            return None

        if self.count < 1:
            self._list_finished_callback()
            return None

        return self.play_next()

    def _fetch_injectable_content(self) -> Optional['Audio']:
        """
        This function is overloaded in terms of responsibilities

        :return:
        """
        if not self._injectable_content_list:
            logger.info("no _injectable_content_list")
            return None
        _content = self._injectable_content_list.fetch_one()
        if _content is None:
            logger.info("no injectable content fetched")
            return None

        logger.info("there is injectable content and marked as delivered")
        _content.mark_delivery()

        # upload here.
        def _run_garbage_collection_and_upload():
            self._injectable_content_list.collect_garbage()
            self._injectable_content_list.upload()

        Thread(target=_run_garbage_collection_and_upload).start()

        # todo there is jingle_url also but not currently playable in list_player
        logger.info("Injectable content to be played, url: {url} & hash: {hash_}".format(url=_content.audio_url,
                                                                                        hash_=_content.hash_))
        return Audio(url=_content.audio_url, hash_=_content.hash_)

    def check_upcoming_content(self):
        if self.count < 1:
            return None
        return deepcopy(self.queue[0])

    def play_next(self) -> Union['Audio', 'type']:
        content = self._fetch_injectable_content()

        logger.info("Is there an injectable content? {}".format(content is not None))

        try:
            if not content:
                agg_audio = self.queue.popleft()
                content = next(agg_audio)
        except IndexError:
            # There is no content to play in the queue
            return ListPlayerConsumedSignal

        def _play():
            # todo this is the place to update the state!
            self.vlc_player.set_mrl(mrl=content.url)
            # content.hash
            self.vlc_player.play()
            self._next_item_callback()

        GLib.idle_add(lambda: _play())
        return content

    def pause(self):
        GLib.idle_add(lambda: self.vlc_player.pause())

    def add_content(self, content, to_top=False):
        assert isinstance(content, dict) or isinstance(content, Audio) \
               or isinstance(content, AggregateAudio), (
            "content is supposed to be one of these types: "
            "[dict, Audio, AggregateAudio], found: {}".format(type(content))
        )

        if isinstance(content, dict):
            hash_ = content.get('hash', content.get('hash_'))
            content = Audio(url=content.get('url'), hash_=hash_)

        # wrap with `AggregateAudio`
        content = AggregateAudio(content) if isinstance(content, Audio) else content

        if to_top:
            self.queue.appendleft(content)
        else:
            self.queue.append(content)

    def is_playing(self):
        return self.vlc_player.is_playing()

    @property
    def count(self) -> int:
        return len(self.queue)

    def clean_playlist(self):
        self.queue.clear()

    def _bind_default_events(self):
        em = self.vlc_player.event_manager()
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self.play)

    def __str__(self):
        return "List Player with {} element(s)".format(self.count)

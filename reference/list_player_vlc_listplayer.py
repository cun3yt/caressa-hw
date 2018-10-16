import vlc


class ListPlayer:
    def __init__(self, media_list_player_callbacks=None, max_list_size=100, processing_indicator_fn=lambda: 0,
                 processing_off_indicator_fn=lambda: 0):
        assert(max_list_size > 5)
        self.max_list_size = max_list_size
        self._vlc = vlc.Instance()

        self.player = self._vlc.media_list_player_new()     # type: vlc.MediaListPlayer
        self.media_list = self._vlc.media_list_new()
        self.player.set_media_list(self.media_list)

        self._processing_indicator_fn = processing_indicator_fn
        self._processing_off_indicator_fn = processing_off_indicator_fn

        self._bind_media_list_playlist_events(media_list_player_callbacks)

    @property
    def count(self) -> int:
        return self.media_list.count()

    def clean_playlist(self, max_index=None):
        print('clean_playlist')

        max_index = max_index if max_index else self.count - 1

        for i in range(max_index, -1, -1):
            self.media_list.remove_index(i)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

        # todo: How to save the playlist from bloating?

    def add_content(self, content):
        url = content.get('url')
        self.media_list.add_media(url)
        print('added to the queue: {}, size: {}'.format(url, self.count))

    def is_playing(self):
        return self.player.is_playing()

    def _bind_media_list_playlist_events(self, event_registrations):
        if event_registrations is None:
            return

        em = self.player.event_manager()
        for (event, fn) in event_registrations.items():
            em.event_attach(event, fn)

    def __str__(self):
        return "List Player with {} elements".format(self.count)

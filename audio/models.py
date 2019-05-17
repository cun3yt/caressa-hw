# instance of this class must pause the play, collect the response and send it ...
class Audio:
    def __init__(self, url, hash_, follow_up_fn=None, *args):
        assert hash_, (
            "hash cannot be falsify value! Found: {}".format(hash_)
        )
        self._url = url
        self._hash = hash_
        self._follow_up = lambda: follow_up_fn(args) if follow_up_fn else None

    @property
    def url(self):
        return self._url

    @property
    def hash(self):
        return self._hash

    @property
    def follow_up_fn(self):
        return self._follow_up

    def __str__(self):
        return "Audio({}, {})".format(self.url, self.hash)


class AggregateAudio:
    # ordered_list_of_audio_files
    pass

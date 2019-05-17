# instance of this class must pause the play, collect the response and send it ...
class Audio:
    def __init__(self, url, hash_):
        assert hash_, (
            "hash cannot be falsify value! Found: {}".format(hash_)
        )
        self._url = url
        self._hash = hash_

    @property
    def url(self):
        return self._url

    @property
    def hash(self):
        return self._hash

    def __str__(self):
        return "Audio({}, {})".format(self.url, self.hash)


class AggregateAudio:
    def __init__(self, *args):
        self.list_of_audios = []
        self._index = 0

        for arg in args:
            self.list_of_audios.append(arg)

    def __len__(self):
        return len(self.list_of_audios)

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self.list_of_audios):
            raise StopIteration
        item = self.list_of_audios[self._index]
        self._index = self._index + 1
        return item

    def append(self, audio: Audio):
        self.list_of_audios.append(audio)

class Mixer:
    def __init__(self, volume=50):
        self.volume = volume

    def getvolume(self):
        return self.volume, 'something',

    def setvolume(self, volume):
        self.volume = volume


def mixers():
    mixer1 = Mixer()
    return [mixer1, ]


class AlsaMixer:
    def __init__(self, mixer):
        self.mixer = mixer

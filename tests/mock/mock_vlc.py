class State:
    Stopped = 'stopped'
    Paused = 'paused'
    Playing = 'playing'


class EventType:
    MediaPlayerEndReached = 'MediaPlayerEndReached'


class EventManager:
    def event_attach(self, event_type, fn):
        return


class MediaPlayer:
    def __init__(self):
        self._state = State.Stopped
        self._event_manager = EventManager()

    def is_playing(self):
        return self._state == State.Playing

    def play(self):
        self._state = State.Playing

    def pause(self):
        self._state = State.Paused

    def stop(self):
        self._state = State.Stopped

    def get_state(self):
        return self._state

    def event_manager(self):
        return self._event_manager

    def set_mrl(self, *args, **kwargs):
        return

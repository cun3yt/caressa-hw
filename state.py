from collections import deque
from copy import deepcopy
from logger import get_logger
from audio.models import Audio


logger = get_logger()


class State:
    def __init__(self, current_player, audio: Audio = None, playing_state=False):
        self.current_player = current_player
        self.playing_state = playing_state
        self._audio = audio

    @property
    def audio_url(self):
        return self._audio.url if self._audio else None

    @property
    def audio_hash(self):
        return self._audio.hash if self._audio else None

    def __str__(self):
        return "State ({player}, {state}, {audio})".format(player=self.current_player,
                                                           state=self.playing_state,
                                                           audio=self._audio, )

    def set_audio(self, audio: Audio):
        self._audio = audio


class StateStack:
    def __init__(self):
        self.stack = deque()

    def push(self, state: State):
        state_copy = deepcopy(state)
        self.stack.append(state_copy)
        logger.info("StateStack::push with {}, new size: {}".format(state, self.count))

    def pop(self) -> State:
        if self.count < 1:
            raise Exception('stack is empty')

        state = self.stack.pop()
        logger.info("StateStack::pop, new size: {}, popped state: {}".format(self.count, state))
        return state

    @property
    def count(self):
        return len(self.stack)

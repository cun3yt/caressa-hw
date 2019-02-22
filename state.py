from collections import deque
from copy import deepcopy
from logger import get_logger


logger = get_logger()


class State:
    def __init__(self, current_player, playing_state=False):
        self.current_player = current_player
        self.playing_state = playing_state

    def __str__(self):
        return "State ({}, {})".format(self.current_player, self.playing_state)


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

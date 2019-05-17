import unittest
from state import State, StateStack
from audio.models import Audio


class TestState(unittest.TestCase):
    def test_state_no_audio(self):
        inst = State(current_player='player1', playing_state=True)
        self.assertEqual(inst.current_player, 'player1')
        self.assertTrue(inst.playing_state)
        self.assertEqual(inst.audio_url, None)
        self.assertEqual(inst.audio_hash, None)

    def test_state_with_audio(self):
        inst = State(current_player='player1', playing_state=True,
                     audio=Audio(url='http://example.com/audio1.mp3', hash_='abcd1234'))
        self.assertEqual(inst.current_player, 'player1')
        self.assertTrue(inst.playing_state)
        self.assertEqual(inst.audio_url, 'http://example.com/audio1.mp3')
        self.assertEqual(inst.audio_hash, 'abcd1234')

    def test_default_playing_state(self):
        inst = State(current_player='player1')
        self.assertFalse(inst.playing_state)

    def test_str(self):
        inst = State(current_player='player1', playing_state=False)
        self.assertEqual(str(inst), "State (player1, False, None)")

    def test_with_audio_str(self):
        inst = State(current_player='player1', playing_state=False,
                     audio=Audio(url='http://example.com/a1.mp3', hash_='abcd1234'))
        self.assertEqual(str(inst), "State (player1, False, "
                                    "Audio(http://example.com/a1.mp3, abcd1234))")


class TestStateStack(unittest.TestCase):
    def setUp(self):
        self.stack = StateStack()

    def test_stack_init(self):
        self.assertEqual(self.stack.count, 0)

    def test_pop_empty_stack(self):
        self.assertRaises(Exception, self.stack.pop)

    def test_pop_stack(self):
        state1 = State(current_player='a', playing_state=False)
        state2 = State(current_player='b', playing_state=True)
        state3 = State(current_player='c', playing_state=False)

        self.stack.push(state1)
        self.stack.push(state2)
        self.stack.push(state3)
        self.assertEqual(self.stack.count, 3)

        popped = self.stack.pop()
        self.assertEqual(self.stack.count, 2)

        self.assertEqual(popped.current_player, 'c')
        self.assertFalse(popped.playing_state)

        popped2 = self.stack.pop()
        self.assertEqual(self.stack.count, 1)

        self.assertEqual(popped2.current_player, 'b')
        self.assertTrue(popped2.playing_state)

    def test_independent_copy(self):
        # The instances inside the stack should be deep copied
        state = State(current_player='something', playing_state=True)
        self.stack.push(state)

        state.current_player = 'else'
        state.playing_state = False

        popped = self.stack.pop()

        self.assertEqual(popped.current_player, 'something')
        self.assertTrue(popped.playing_state)

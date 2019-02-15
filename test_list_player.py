import unittest
from list_player import Audio, ListPlayer


class TestAudio(unittest.TestCase):
    def test_audio_set(self):
        audio = Audio(url='http://example.com/audio.mp3')
        self.assertEqual(audio.url, 'http://example.com/audio.mp3')
        fn = audio.follow_up_fn
        self.assertIsNone(fn())

    def test_audio_set_with_fn(self):
        def _fn(*args):
            return "_fn is called with {}".format(', '.join(*args))

        audio = Audio('http://example.com/audio.mp3', _fn, 'one', 'two')
        fn = audio.follow_up_fn
        self.assertEqual(fn(), "_fn is called with one, two")


class TestListPlayer(unittest.TestCase):
    def test_add_url(self):
        lp = ListPlayer()
        lp.add_content(content='http://example.com/audio_1.mp3')
        lp.add_content(content='http://example.com/audio_2.mp3')
        self.assertEqual(lp.count, 2)

        audio = lp.queue.popleft()
        self.assertEqual(audio.url, 'http://example.com/audio_1.mp3')

        lp.add_content(content='http://example.com/audio_3.mp3', to_top=True)

        audio = lp.queue.popleft()
        self.assertEqual(audio.url, 'http://example.com/audio_3.mp3')

    def test_add_dict(self):
        lp = ListPlayer()

        lp.add_content(content='http://example.com/audio_1.mp3')

        lp.add_content({
            'url': 'http://example.com/audio_2.mp3',
            'fn': lambda: 'Hello'
        })

        audio = lp.queue.pop()
        self.assertEqual(audio.url, 'http://example.com/audio_2.mp3')

    def test_add_dict_to_top(self):
        lp = ListPlayer()
        lp.add_content(content='http://example.com/audio_1.mp3')
        lp.add_content({
            'url': 'http://example.com/audio_2.mp3',
            'fn': lambda: 'Hello'
        }, to_top=True)

        audio = lp.queue.popleft()
        self.assertIsInstance(audio, Audio)
        self.assertEqual(audio.url, 'http://example.com/audio_2.mp3')

    def test_play_at_beginning(self):
        lp = ListPlayer()
        lp.add_content(content='http://example.com/audio_1.mp3')
        lp.add_content(content='http://example.com/audio_2.mp3')

        self.assertFalse(lp.is_playing())
        lp.play()
        self.assertTrue(lp.is_playing())
        self.assertEqual(lp.count, 1)

    def test_play_next_at_beginning(self):
        def _next_item_callback():
            raise ValueError

        lp = ListPlayer(next_item_callback=_next_item_callback)
        lp.add_content(content='http://example.com/audio_1.mp3')
        lp.add_content(content='http://example.com/audio_2.mp3')

        self.assertFalse(lp.is_playing())
        self.assertRaises(ValueError, lp.play_next)
        self.assertTrue(lp.is_playing())

    def test_pause(self):
        lp = ListPlayer()
        lp.add_content(content='http://example.com/audio_1.mp3')
        lp.add_content(content='http://example.com/audio_2.mp3')

        self.assertFalse(lp.is_playing())
        lp.play()
        self.assertTrue(lp.is_playing())
        lp.pause()
        self.assertFalse(lp.is_playing())
        lp.play()
        self.assertTrue(lp.is_playing())
        self.assertEqual(lp.count, 1)

    def test_list_finished_callback(self):
        def _list_finished_callback():
            raise ValueError

        lp = ListPlayer(list_finished_callback=_list_finished_callback)
        self.assertRaises(ValueError, lp.play)
        self.assertFalse(lp.is_playing())
        lp.add_content(content='http://example.com/audio_1.mp3')
        lp.play()
        self.assertRaises(ValueError, lp.play_next)

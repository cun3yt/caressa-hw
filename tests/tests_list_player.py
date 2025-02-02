import unittest
from audio.models import Audio
from list_player import ListPlayer
import logging
import pytz
from injectable_content.list import List as InjectableContentList
from injectable_content.models import InjectableContent
from datetime import datetime, timedelta
from unittest.mock import patch


class TestAudio(unittest.TestCase):
    def test_audio_set(self):
        audio = Audio(url='http://example.com/audio.mp3', hash_='abcd1234')
        self.assertEqual(audio.url, 'http://example.com/audio.mp3')
        self.assertEqual(audio.hash, 'abcd1234')
        fn = audio.follow_up_fn
        self.assertIsNone(fn())

    def test_audio_set_with_fn(self):
        def _fn(*args):
            return "_fn is called with {}".format(', '.join(*args))

        audio = Audio('http://example.com/audio.mp3', 'abcd1234', _fn, 'one', 'two')
        fn = audio.follow_up_fn
        self.assertEqual(fn(), "_fn is called with one, two")


class TestListPlayer(unittest.TestCase):
    def test_add_url(self):
        lp = ListPlayer()
        lp.add_content({'url': 'http://example.com/audio_1.mp3',
                        'hash': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3',
                        'hash': 'jf9dwjef'})
        self.assertEqual(lp.count, 2)

        audio = lp.queue.popleft()
        self.assertEqual(audio.url, 'http://example.com/audio_1.mp3')
        self.assertEqual(audio.hash, 'abcd1234')

        lp.add_content(content={'url': 'http://example.com/audio_3.mp3',
                                'hash': 'kjfsi93j'},
                       to_top=True)

        audio = lp.queue.popleft()
        self.assertEqual(audio.url, 'http://example.com/audio_3.mp3')
        self.assertEqual(audio.hash, 'kjfsi93j')

    def test_add_dict(self):
        lp = ListPlayer()

        lp.add_content({'url': 'http://example.com/audio_1.mp3',
                        'hash_': 'abcd1234'})

        lp.add_content({
            'url': 'http://example.com/audio_2.mp3',
            'hash_': 'fjsoi23fds',
            'fn': lambda: 'Hello'
        })

        audio = lp.queue.pop()
        self.assertEqual(audio.url, 'http://example.com/audio_2.mp3')
        self.assertEqual(audio.hash, 'fjsoi23fds')

    def test_assert_string_content(self):
        lp = ListPlayer()
        with self.assertRaises(AssertionError):
            lp.add_content(content='http://example.com/audio.mp3')

    def test_add_dict_to_top(self):
        lp = ListPlayer()
        lp.add_content({'url': 'http://example.com/audio_1.mp3',
                        'hash_': 'abcd1234'})
        lp.add_content({
            'url': 'http://example.com/audio_2.mp3',
            'hash_': 'jfoipsj23',
            'fn': lambda: 'Hello'
        }, to_top=True)

        audio = lp.queue.popleft()
        self.assertIsInstance(audio, Audio)
        self.assertEqual(audio.url, 'http://example.com/audio_2.mp3')
        self.assertEqual(audio.hash, 'jfoipsj23')

    def test_play_at_beginning(self):
        lp = ListPlayer()
        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash_': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3', 'hash_': 'kdasjfoj'})

        self.assertFalse(lp.is_playing())
        lp.play()
        self.assertTrue(lp.is_playing())
        self.assertEqual(lp.count, 1)

    def test_check_upcoming_content(self):
        lp = ListPlayer()

        content = lp.check_upcoming_content()
        self.assertIsNone(content)

        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash_': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3', 'hash_': 'kdasjfoj'})

        content = lp.check_upcoming_content()
        self.assertIsInstance(content, Audio)
        self.assertEqual(content.url, 'http://example.com/audio_1.mp3')
        self.assertEqual(content.hash, 'abcd1234')


    def test_play_next_at_beginning(self):
        def _next_item_callback():
            raise ValueError

        lp = ListPlayer(next_item_callback=_next_item_callback)
        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash_': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3', 'hash_': 'kljfdsjio23'})

        self.assertFalse(lp.is_playing())
        self.assertRaises(ValueError, lp.play_next)
        self.assertTrue(lp.is_playing())

    @patch('injectable_content.list.List.download')
    @patch('injectable_content.list.List.fetch_from_api')
    def test_play_with_injectable_content_at_beginning(self, mock_fetch_from_api, mock_download):
        lp = ListPlayer()
        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3', 'hash': 'jf9eo63f'})

        self.now = datetime.now(pytz.utc)
        self.one_day = timedelta(days=1)
        self.two_day = timedelta(days=2)

        content_current = InjectableContent(audio_url='https://example.com/audio1.mp3', hash_='123abc',
                                            start=self.now - self.one_day, end=self.now + self.one_day)
        content_upcoming = InjectableContent(audio_url='https://example.com/audio3.mp3', hash_='789ghi',
                                             start=self.now + self.one_day, end=self.now + self.two_day)

        injectable_content_list = InjectableContentList()
        injectable_content_list.add(content_current)
        injectable_content_list.add(content_upcoming)

        lp.set_injectable_content_list(injectable_content_list)
        lp.play()
        self.assertTrue(lp.is_playing())
        self.assertEqual(lp.count, 2)

    @patch('injectable_content.list.List.download')
    @patch('injectable_content.list.List.fetch_from_api')
    def test_play_with_injectable_content_upcoming_at_beginning(self, mock_fetch_from_api, mock_download):
        lp = ListPlayer()
        lp.add_content(content={'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        lp.add_content(content={'url': 'http://example.com/audio_2.mp3', 'hash': 'fdsjkn12'})

        self.now = datetime.now(pytz.utc)
        self.one_day = timedelta(days=1)
        self.two_day = timedelta(days=2)

        content_upcoming = InjectableContent(audio_url='https://example.com/audio3.mp3', hash_='789ghi',
                                             start=self.now + self.one_day, end=self.now + self.two_day)

        injectable_content_list = InjectableContentList()
        injectable_content_list.add(content_upcoming)

        lp.set_injectable_content_list(injectable_content_list)
        lp.play()
        self.assertTrue(lp.is_playing())
        self.assertEqual(lp.count, 1)

    def test_pause(self):
        lp = ListPlayer()
        lp.add_content(content={'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        lp.add_content(content={'url': 'http://example.com/audio_2.mp3', 'hash': 'abcd1234'})

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
        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        lp.play()
        lp.vlc_player.stop()
        if lp._content_follow_fn:   # need to consume follow up function
            lp.play()
            lp.vlc_player.stop()
        self.assertRaises(ValueError, lp.play)

    def test_list_finished_callback_no_next(self):
        # list_finished_callback is called until next item is intentionally `play`ed
        def _list_finished_callback():
            logging.getLogger().info('_list_finished_callback is called')
            return 0
        lp = ListPlayer(list_finished_callback=_list_finished_callback)
        with self.assertLogs(level='INFO') as context_manager:
            lp.play()
        self.assertEqual(context_manager.output,
                         ['INFO:root:_list_finished_callback is called', ])
        self.assertFalse(lp.is_playing())

    def test_list_finished_zero_state(self):
        lp = ListPlayer()
        try:
            lp.play()
        except Exception:
            self.fail('No exception is waited')
        self.assertEqual(lp.count, 0)
        self.assertFalse(lp.is_playing())

    def test_list_repeated_play(self):
        lp = ListPlayer()
        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3', 'hash': 'fjsdo23j'})
        lp.play()
        self.assertEqual(lp.count, 1)
        self.assertTrue(lp.is_playing())
        lp.play()
        self.assertEqual(lp.count, 1, "Repeated play request consumes no item")
        self.assertTrue(lp.is_playing(), "Repeated play request makes no state change")

    def test_clear_playlist(self):
        lp = ListPlayer()
        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3', 'hash': 'fjsdo23j'})
        lp.clean_playlist()
        self.assertEqual(lp.count, 0)

        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        lp.add_content({'url': 'http://example.com/audio_2.mp3', 'hash': 'fdskji2e'})
        lp.add_content({'url': 'http://example.com/audio_3.mp3', 'hash': 'i09ikwn3'})
        lp.play()
        lp.clean_playlist()
        self.assertEqual(lp.count, 0)

    def test_str(self):
        lp = ListPlayer()
        lp.add_content({'url': 'http://example.com/audio_1.mp3', 'hash': 'abcd1234'})
        self.assertEqual(str(lp), "List Player with 1 element(s)")

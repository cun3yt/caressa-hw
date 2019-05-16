import unittest
from audio.models import Audio


class TestAudioFile(unittest.TestCase):
    def test_audio_file_init(self):
        audio_file = Audio(url='https://example.com/audio1.mp3', hash_='abcd1234')
        self.assertEqual(audio_file.url, 'https://example.com/audio1.mp3')
        self.assertEqual(audio_file.hash, 'abcd1234')

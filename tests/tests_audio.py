import unittest
from audio.models import Audio, AggregateAudio


class TestAudio(unittest.TestCase):
    def test_init(self):
        audio_file = Audio(url='https://example.com/audio1.mp3', hash_='abcd1234')
        self.assertEqual(audio_file.url, 'https://example.com/audio1.mp3')
        self.assertEqual(audio_file.hash, 'abcd1234')

    def test_audio_set(self):
        audio = Audio(url='http://example.com/audio.mp3', hash_='abcd1234')
        self.assertEqual(audio.url, 'http://example.com/audio.mp3')
        self.assertEqual(audio.hash, 'abcd1234')


class TestAggregateAudio(unittest.TestCase):
    def test_init(self):
        af_1 = Audio(url='https://example.com/audio1.mp3', hash_='abcd1234')
        af_2 = Audio(url='https://example.com/audio2.mp3', hash_='qwer7890')
        af_3 = Audio(url='https://example.com/audio3.mp3', hash_='mkijne32r')

        agg_audio = AggregateAudio(af_1, af_2, af_3)
        self.assertEqual(len(agg_audio), 3)

        self.assertEqual(agg_audio.list_of_audios[0].url, 'https://example.com/audio1.mp3')
        self.assertEqual(agg_audio.list_of_audios[1].url, 'https://example.com/audio2.mp3')
        self.assertEqual(agg_audio.list_of_audios[2].url, 'https://example.com/audio3.mp3')

    def test_add_audio(self):
        agg_audio = AggregateAudio()
        self.assertEqual(len(agg_audio), 0)

        af_1 = Audio(url='https://example.com/audio1.mp3', hash_='abcd1234')
        agg_audio.append(af_1)
        self.assertEqual(len(agg_audio), 1)
        self.assertEqual(agg_audio.list_of_audios[0].url, 'https://example.com/audio1.mp3')

    def test_next(self):
        agg_audio = AggregateAudio(Audio(url='https://example.com/audio1.mp3', hash_='abcd1234'),
                                   Audio(url='https://example.com/audio2.mp3', hash_='qwer7890'),
                                   Audio(url='https://example.com/audio3.mp3', hash_='mkijne32r'))

        audio = next(agg_audio)
        self.assertEqual(audio.hash, 'abcd1234')

        audio = next(agg_audio)
        self.assertEqual(audio.hash, 'qwer7890')

        audio = next(agg_audio)
        self.assertEqual(audio.hash, 'mkijne32r')

        with self.assertRaises(StopIteration):
            next(agg_audio)

    def test_being_iterator(self):
        agg_audio = AggregateAudio(Audio(url='https://example.com/audio1.mp3', hash_='abcd1234'),
                                   Audio(url='https://example.com/audio2.mp3', hash_='qwer7890'),
                                   Audio(url='https://example.com/audio3.mp3', hash_='mkijne32r'))

        hashes = []
        for audio in agg_audio:
            hashes.append(audio.hash)

        self.assertListEqual(hashes, ['abcd1234', 'qwer7890', 'mkijne32r'])

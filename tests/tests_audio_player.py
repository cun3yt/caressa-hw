import unittest
from unittest.mock import patch
from audio_player import AudioPlayer
from tests.mock.mock_api_client import ApiClient
from tests.mock.mock_aiy import voicehat
from audio.models import Audio
from list_player import ListPlayer
from state import State


class TestAudioPlayerState(unittest.TestCase):
    def setUp(self):
        self.api_client = ApiClient()
        self.audio_player = AudioPlayer(self.api_client)

    def test_init(self):
        self.assertEqual(self.audio_player.client, self.api_client)
        self.assertIsInstance(self.audio_player.main_player, ListPlayer, 'Main Player Exists')
        self.assertIsInstance(self.audio_player.voice_mail_player, ListPlayer, 'Voice Mail Player Exists')
        self.assertIsInstance(self.audio_player.urgent_mail_player, ListPlayer, 'Urgent Mail Player Exists')
        self.assertEqual(self.audio_player.current_player_name, 'main')
        self.assertEqual(self.audio_player.state_stack.count, 0, 'State Stack Initially Empty')
        self.assertEqual(voicehat.get_led().state, voicehat.LED.OFF)
        self.assertTrue(self.audio_player.token, '1234')

    def test_player_property(self):
        self.assertEqual(self.audio_player.player, self.audio_player.players['main'],
                         "Default player must be the same as the 'main' one")

    def test_save_state(self):
        state = self.audio_player.current_state
        self.audio_player.save_state()
        self.assertEqual(self.audio_player.state_stack.count, 1)
        popped_state = self.audio_player.state_stack.pop()
        self.assertEqual(popped_state.playing_state, state.playing_state)
        self.assertEqual(popped_state.current_player, state.current_player)

    def test_restore_state_empty_stack(self):
        with self.assertLogs(level='INFO') as context_manager:
            self.audio_player.restore_state()
        self.assertEqual(context_manager.output,
                         ['INFO:root:restore_state is called (callback call)',
                          'INFO:root:nothing to restore', ])

    def test_restore_state(self):
        self.audio_player.play_pause()
        self.audio_player.save_state()  # 'main', 'playing'

        self.audio_player.current_state = State(current_player='voice-mail', playing_state=False,
                                                audio=Audio(url='https://example.com/voicemail.mp3', hash_='abcd1234'))
        self.audio_player.save_state()  # 'voice-mail', 'non-playing'
        self.audio_player.current_state = State(current_player='urgent-mail', playing_state=True,
                                                audio=Audio(url='https://example.com/urgent.mp3', hash_='hash-urgent'))

        self.audio_player.restore_state()
        self.assertEqual(self.audio_player.current_state.current_player, 'voice-mail')
        self.assertFalse(self.audio_player.current_state.playing_state)

        self.audio_player.restore_state()
        self.assertEqual(self.audio_player.current_state.current_player, 'main')
        self.assertTrue(self.audio_player.current_state.playing_state)


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.api_client = ApiClient()
        self.audio_player = AudioPlayer(self.api_client)

    def test_button_press_what_next_initial(self):
        self.audio_player.button_press_on_off()
        self.assertTrue(self.audio_player.player.is_playing())
        self.assertEqual(self.audio_player.state_stack.count, 0)

    def test_button_press_what_next_with_voice_mail(self):
        self.audio_player.voice_mail_player.add_content({'url': 'https://example.com/voice-mail-1.mp3',
                                                         'hash': 'abcd1234'})
        with self.assertLogs(level='INFO') as context_manager:
            self.audio_player.button_press_on_off()
        self.assertIn('INFO:root:delivering voice-mail', context_manager.output)
        self.assertEqual(self.audio_player.state_stack.count, 1)
        self.assertEqual(self.audio_player.current_player_name, 'voice-mail')
        self.assertTrue(self.audio_player.player.is_playing())

    def test_play_pause(self):
        self.audio_player.play_pause()
        self.assertTrue(self.audio_player.current_state.playing_state)
        self.audio_player.play_pause()
        self.assertFalse(self.audio_player.current_state.playing_state)

    def test_next_command_from_no_play(self):
        self.assertFalse(self.audio_player.player.is_playing())
        self.assertTrue(self.audio_player.current_player_name, "main")
        self.audio_player.next_command()
        self.assertTrue(self.audio_player.player.is_playing())

    def test_next_command_from_play(self):
        self.audio_player.play_pause()
        self.assertTrue(self.audio_player.current_state.playing_state)
        with patch('list_player.ListPlayer.play_next') as mock_play_next:
            self.audio_player.next_command()
            mock_play_next.assert_any_call()

    def test_next_command_urgent_mail(self):
        self.audio_player.current_state = State(current_player='urgent-mail', playing_state=False)
        self.assertNotEqual(self.audio_player.current_player_name, 'main')
        with patch('list_player.ListPlayer.play_next') as mock_play_next:
            with patch('audio_player.AudioPlayer.play_pause') as mock_play_pause:
                self.audio_player.next_command()
                # Urgent Mail Cannot be Skipped
                mock_play_next.assert_not_called()
                mock_play_pause.assert_not_called()

    def test_next_command_state_audio_change(self):
        self.assertEqual(self.audio_player.current_state.audio_url, 'http://example.com/audio1.mp3')
        self.assertEqual(self.audio_player.current_state.audio_hash, 'fdsjo11f3')

        self.audio_player.play_pause()
        self.audio_player._content_started()

        self.assertEqual(self.audio_player.current_state.audio_url, 'http://example.com/audio1.mp3')
        self.assertEqual(self.audio_player.current_state.audio_hash, 'fdsjo11f3')

        with patch('audio_player.AudioPlayer._react_to_content') as mock_react_to_content:
            self.audio_player.next_command()
            mock_react_to_content.assert_called_once_with(signal='negative')

        self.assertEqual(self.audio_player.current_state.audio_url, 'https://example.com/song1234.mp3')
        self.assertEqual(self.audio_player.current_state.audio_hash, 'abcd1234')

    @patch('audio_player.AudioPlayer._react_to_content')
    def test_yes_command_from_no_play(self, mock_react_to_content):
        self.audio_player.yes_command()
        self.assertTrue(self.audio_player.current_state.playing_state)
        self.assertEqual(self.audio_player.current_state.audio_url, 'http://example.com/audio1.mp3')
        self.assertEqual(self.audio_player.current_state.audio_hash, 'fdsjo11f3')
        mock_react_to_content.assert_not_called()

    @patch('audio_player.AudioPlayer._react_to_content')
    def test_yes_command_when_play(self, mock_react_to_content):
        self.audio_player.play_pause()
        self.audio_player.yes_command()
        mock_react_to_content.assert_called_once_with(signal='positive')

    def test_voice_mail_arrival_changes_current_audio(self):
        ap = self.audio_player
        ap.play_pause()
        ap._content_started()

        ap.voice_mail_arrived('https://example.com/voice-mail-1.mp3', 'hash-hash-hash')
        ap.button_press_on_off()

        self.assertEqual(ap.current_state.audio_url, 'https://example.com/voice-mail-1.mp3')
        self.assertEqual(ap.current_state.audio_hash, 'hash-hash-hash')

        self.assertEqual(ap.voice_mail_player.count, 0)

        ap.next_command()

        self.assertEqual(ap.current_player_name, 'main')
        self.assertEqual(ap.current_state.audio_url, 'http://example.com/audio1.mp3')
        self.assertEqual(ap.current_state.audio_hash, 'fdsjo11f3')

    @patch('audio_player.AudioPlayer.set_volume_minimum')
    @patch('audio_player.AudioPlayer.notify')
    def test_urgent_mail_arrival_changes_current_audio(self, mock_notify, mock_set_vol_min):
        ap = self.audio_player
        ap.play_pause()
        ap._content_started()

        ap.urgent_mail_arrived('https://example.com/urgent-mail-1.mp3', '1234-urgent-hash')

        self.assertEqual(ap.current_state.audio_url, 'https://example.com/urgent-mail-1.mp3')
        self.assertEqual(ap.current_state.audio_hash, '1234-urgent-hash')
        self.assertEqual(ap.current_player_name, 'urgent-mail')


class TestContentArrival(unittest.TestCase):
    def setUp(self):
        self.api_client = ApiClient()
        self.audio_player = AudioPlayer(self.api_client)

    def test_injectable_content_arrived(self):
        data = {
            'url': 'https://example.com/audio1.mp3',
            'hash': 'abc1234',
        }
        self.audio_player.injectable_content_arrived(data)
        self.assertEqual(len(self.audio_player.injectable_content_list), 1)

    @patch('audio_player.AudioPlayer.set_volume_minimum')
    @patch('audio_player.AudioPlayer.notify')
    def test_urgent_mail_arrived_during_main_stop(self, mock_notify, mock_set_vol_min):
        self.audio_player.urgent_mail_arrived('https://example.com/urgent-mail-1.mp3', 'abcd1234')
        self.assertEqual(self.audio_player.current_player_name, 'urgent-mail')
        self.assertTrue(self.audio_player.player.is_playing())
        self.assertEqual(self.audio_player.state_stack.count, 1)
        mock_set_vol_min.assert_called_with(80)
        mock_notify.assert_called_with()

    @patch('audio_player.AudioPlayer.set_volume_minimum')
    @patch('audio_player.AudioPlayer.notify')
    def test_urgent_mail_arrived_during_main_play(self, mock_notify, mock_set_vol_min):
        self.audio_player.play_pause()
        self.assertTrue(self.audio_player.player.is_playing())
        self.assertEqual(self.audio_player.current_player_name, 'main')

        self.audio_player.urgent_mail_arrived('https://example.com/urgent-mail-1.mp3', 'abcd1234')

        self.assertEqual(self.audio_player.current_player_name, 'urgent-mail')
        self.assertTrue(self.audio_player.player.is_playing())
        self.assertEqual(self.audio_player.state_stack.count, 1)
        mock_set_vol_min.assert_called_with(80)
        mock_notify.assert_called_with()

    @patch('audio_player.AudioPlayer.set_volume_minimum')
    def test_urgent_mail_arrived_during_urgent_mail_play(self, mock_set_vol_min):
        self.audio_player.urgent_mail_arrived('https://example.com/urgent-mail-1.mp3', 'abcd1234')

        self.assertEqual(self.audio_player.current_player_name, 'urgent-mail')
        self.assertTrue(self.audio_player.player.is_playing())
        self.assertEqual(self.audio_player.urgent_mail_player.count, 0)
        self.assertEqual(self.audio_player.state_stack.count, 1)

        with patch('audio_player.AudioPlayer.notify') as mock_notify:
            self.audio_player.urgent_mail_arrived('https://example.com/urgent-mail-2.mp3', 'jf9sjf3dv')

        mock_notify.assert_not_called()
        self.assertTrue(self.audio_player.player.is_playing())
        self.assertEqual(self.audio_player.urgent_mail_player.count, 1)
        self.assertEqual(self.audio_player.state_stack.count, 1)

    @patch('audio_player.AudioPlayer.notify')
    def test_voice_mail_arrived(self, mock_notify):
        ap = self.audio_player
        with self.assertLogs(level='INFO') as context_manager:
            ap.voice_mail_arrived('https://example.com/voice-mail-1.mp3', 'abcd1234')
        self.assertIn('INFO:root:voice_mail_arrived', context_manager.output)
        self.assertEqual(ap.voice_mail_player.count, 1, "Voicemail counter is increased by 1")
        self.assertEqual(ap.current_player_name, 'main', "Voicemail should not change the current player")
        mock_notify.assert_called_once_with()

    @patch('audio_player.AudioPlayer.notify')
    def test_voice_mail_arrived_multiple_times(self, mock_notify):
        ap = self.audio_player
        ap.voice_mail_arrived('https://example.com/voice-mail-1.mp3', 'abcd1234')
        ap.voice_mail_arrived('https://example.com/voice-mail-2.mp3', 'fjdsoi12')
        ap.voice_mail_arrived('https://example.com/voice-mail-3.mp3', 'rsj923fx')
        ap.voice_mail_arrived('https://example.com/voice-mail-4.mp3', 'n09k3fdz')
        self.assertEqual(ap.voice_mail_player.count, 4, "Voicemail counter is incremented 4 times")


class TestVolume(unittest.TestCase):
    def setUp(self):
        self.api_client = ApiClient()
        self.audio_player = AudioPlayer(self.api_client)

    @patch('tests.mock.mock_alsaaudio.Mixer.getvolume')
    @patch('tests.mock.mock_alsaaudio.Mixer.setvolume')
    def test_set_volume_minimum_lower(self, mock_set, mock_get):
        mock_get.return_value = (60, )
        self.audio_player.set_volume_minimum(min_volume=35)
        mock_set.assert_called_with(60)

    @patch('tests.mock.mock_alsaaudio.Mixer.getvolume')
    @patch('tests.mock.mock_alsaaudio.Mixer.setvolume')
    def test_set_volume_minimum_higher(self, mock_set, mock_get):
        mock_get.return_value = (60,)
        self.audio_player.set_volume_minimum(min_volume=77)
        mock_set.assert_called_with(77)

    @patch('tests.mock.mock_alsaaudio.Mixer.getvolume')
    @patch('tests.mock.mock_alsaaudio.Mixer.setvolume')
    def test_volume_up_in_range(self, mock_set, mock_get):
        mock_get.return_value = (60,)
        self.audio_player.volume_up()
        mock_set.assert_called_with(67)     # Volume must be incremented by audio_player._VOLUME_INCREMENT

    @patch('tests.mock.mock_alsaaudio.Mixer.getvolume')
    @patch('tests.mock.mock_alsaaudio.Mixer.setvolume')
    def test_volume_up_out_range(self, mock_set, mock_get):
        mock_get.return_value = (98,)
        self.audio_player.volume_up()
        mock_set.assert_called_with(100)    # Volume cannot be higher than audio_player._VOLUME_MAX

    @patch('tests.mock.mock_alsaaudio.Mixer.getvolume')
    @patch('tests.mock.mock_alsaaudio.Mixer.setvolume')
    def test_volume_down_in_range(self, mock_set, mock_get):
        mock_get.return_value = (60,)
        self.audio_player.volume_down()
        mock_set.assert_called_with(53)     # Volume must be decremented by audio_player._VOLUME_INCREMENT

    @patch('tests.mock.mock_alsaaudio.Mixer.getvolume')
    @patch('tests.mock.mock_alsaaudio.Mixer.setvolume')
    def test_volume_down_out_range(self, mock_set, mock_get):
        mock_get.return_value = (16,)
        self.audio_player.volume_down()
        mock_set.assert_called_with(15)    # Volume cannot be lower than audio_player._VOLUME_MIN


class TestNotifications(unittest.TestCase):
    def setUp(self):
        self.api_client = ApiClient()
        self.audio_player = AudioPlayer(self.api_client)

    @patch('audio_player.os_call')
    def test_notify(self, mock_call):
        self.audio_player.notify()
        mock_call.assert_called_once_with(['aplay', './sounds/message-notification.wav', ])

    @patch('audio_player.os_call')
    def test_positive_feedback(self, mock_call):
        self.audio_player.positive_feedback()
        mock_call.assert_called_once_with(['aplay', './sounds/positive-feedback.wav', ])

    @patch('audio_player.os_call')
    def test_negative_feedback(self, mock_call):
        self.audio_player.negative_feedback()
        mock_call.assert_called_once_with(['aplay', './sounds/negative-feedback.wav', ])

    def test_consuming_all_voice_mails(self):
        ap = self.audio_player
        ap.voice_mail_arrived('https://example.com/voice-mail-1.mp3', 'fjsa9of23')
        ap.voice_mail_arrived('https://example.com/voice-mail-2.mp3', '33ijferec')
        ap.button_press_on_off()
        self.assertEqual(ap.player.count, 1)
        ap.next_command()
        self.assertEqual(ap.player.count, 0)

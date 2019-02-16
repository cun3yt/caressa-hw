import unittest
from unittest.mock import patch
from audio_player import AudioPlayer
from tests.mock.mock_api_client import ApiClient
from tests.mock.mock_aiy import voicehat
from list_player import ListPlayer
from state import State


class TestAudioPlayer(unittest.TestCase):
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
        self.audio_player.current_state = State(current_player='voice-mail', playing_state=False)
        self.audio_player.save_state()  # 'voice-mail', 'non-playing'
        self.audio_player.current_state = State(current_player='urgent-mail', playing_state=True)

        self.audio_player.restore_state()
        self.assertEqual(self.audio_player.current_state.current_player, 'voice-mail')
        self.assertFalse(self.audio_player.current_state.playing_state)

        self.audio_player.restore_state()
        self.assertEqual(self.audio_player.current_state.current_player, 'main')
        self.assertTrue(self.audio_player.current_state.playing_state)

    def test_button_press_what_next_initial(self):
        self.audio_player.button_press_what_next()
        self.assertTrue(self.audio_player.player.is_playing())
        self.assertEqual(self.audio_player.state_stack.count, 0)

    # def test_button_press_what_next_with_voice_mail(self):
    #     pass

    def test_play_pause(self):
        self.audio_player.play_pause()
        self.assertTrue(self.audio_player.current_state.playing_state)
        self.audio_player.play_pause()
        self.assertFalse(self.audio_player.current_state.playing_state)

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

    def test_next_command_not_main_player(self):
        self.audio_player.current_state = State(current_player='voice-mail', playing_state=False)
        self.assertNotEqual(self.audio_player.current_player_name, 'main')
        with patch('list_player.ListPlayer.play_next') as mock_play_next:
            with patch('audio_player.AudioPlayer.play_pause') as mock_play_pause:
                self.audio_player.next_command()
                mock_play_next.assert_not_called()
                mock_play_pause.assert_not_called()

    @patch('tests.mock.mock_subprocess.call')
    def test_notify(self, mock_call):
        self.audio_player.notify()
        mock_call.asset_called_with(['aplay', './sounds/notification-doorbell.wav', ])

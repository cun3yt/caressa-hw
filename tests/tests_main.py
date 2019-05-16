import pytz
import unittest
from unittest.mock import patch
from audio.models import Audio
from audio_player import AudioPlayer
from audio_client import AudioClient
from tests.mock.mock_api_client import ApiClient
from main import PusherService, setup_client, setup_realtime_update, connect_handler, setup_user_channels_and_player, main, handle_mail
from settings import PUSHER_KEY_ID, PUSHER_CLUSTER, PUSHER_SECRET, API_URL
from datetime import datetime


class _Response:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


class TestMain(unittest.TestCase):
    def test_pusher_service(self):
        pusher = PusherService.get_instance()
        self.assertEqual(pusher.key, PUSHER_KEY_ID)
        self.assertEqual(pusher.cluster, PUSHER_CLUSTER)
        self.assertTrue(pusher.secure)
        self.assertEqual(pusher.secret, PUSHER_SECRET)

    def test_pusher_service_is_singleton(self):
        self.assertRaises(ValueError, PusherService)

        pusher = PusherService.get_instance()
        pusher2 = PusherService.get_instance()
        self.assertEqual(id(pusher), id(pusher2))

    def test_setup_client(self):
        client = setup_client()
        self.assertTrue(client.streaming_url.startswith(API_URL))
        self.assertEqual(client.user_id, "some-user-id")
        self.assertEqual(client.user_password, "some-hash")
        self.assertEqual(client.client_id, "some-client-id")
        self.assertEqual(client.client_secret, "some-client-secret")
        self.assertEqual(client.client_secret, "some-client-secret")
        self.assertIsNone(client.access_token)
        self.assertIsNone(client.refresh_token)
        self.assertTrue(client.channel_url.startswith(API_URL))

    def test_setup_realtime_update(self):
        with self.assertLogs(level='INFO') as context_manager:
            setup_realtime_update()
        self.assertIn('INFO:root:_Connection-bind', context_manager.output)
        self.assertIn('INFO:root:Pusher-connect', context_manager.output)
        self.assertIn('INFO:root:pusher is connected', context_manager.output)

    def test_connect_handler(self):
        player = AudioPlayer(ApiClient())
        user_channels = ['channel.X', 'channel.Y', 'channel.Z', ]
        with self.assertLogs(level='INFO') as context_manager:
            connect_handler(injected_user_channels=user_channels, injected_player=player)
        self.assertIn('INFO:root:subscribe::channel.X', context_manager.output)
        self.assertIn('INFO:root:subscribe::channel.Y', context_manager.output)
        self.assertIn('INFO:root:subscribe::channel.Z', context_manager.output)

    @patch('audio_player.AudioPlayer._get_first_audio')
    @patch('audio_client.AudioClient.injectable_content_download_fn')
    @patch('audio_client.AudioClient.injectable_content_fetch_available_content_fn')
    @patch('audio_client.AudioClient.get_channels')
    @patch('audio_client.AudioClient.get_user_data')
    def test_setup_user_channels_and_player(self, mock_get_user_data, mock_get_channels,
                                            mock_injectable_content_fetch_available_content_fn,
                                            mock_inj_content_download_fn, mock_get_first_audio):
        mock_get_user_data.return_value = _Response(text='{"pk": 1}')
        mock_get_channels.return_value = _Response(text='{"channels": ["channel.X", "channel.Y"]}')
        mock_injectable_content_fetch_available_content_fn.return_value = []
        mock_inj_content_download_fn.return_value = '[]'
        mock_get_first_audio.return_value = Audio(url='https://example.com/audio-1.mp3', hash_='abcd1234')

        channels, player, user_id, client = setup_user_channels_and_player()
        self.assertEqual(channels, ['channel.X', 'channel.Y'])
        self.assertIsInstance(player, AudioPlayer)
        self.assertEqual(user_id, 1)
        self.assertIsInstance(client, AudioClient)
        self.assertEqual(player.client, client)

    @patch('main.setup_realtime_update')
    @patch('main.setup_user_channels_and_player')
    def test_main(self, mock_setup_user_channels_and_player, mock_setup_realtime_update):
        client = ApiClient()

        mock_setup_user_channels_and_player.return_value = \
            (['channel.X', 'channel.Y'], AudioPlayer(client), 1, client)
        volume_up_btn, volume_down_btn, next_btn, service_btn, yes_liked_btn = main()
        volume_up_btn.id = 8
        volume_down_btn.id = 7
        next_btn.id = 9
        service_btn.id = 10
        yes_liked_btn.id = 11


user_id = None


class TestHandlingMail(unittest.TestCase):
    def test_assert_no_user_id(self):
        voice_mail_handler = handle_mail(AudioPlayer(ApiClient()), 'voice_mail')
        with self.assertRaises(AssertionError):
            voice_mail_handler('{"url": "https://example.com/audio1.mp3"}', dependency_injection_user_id=None)

    def test_error_recipient_ids_but_no_type(self):
        voice_mail_handler = handle_mail(AudioPlayer(ApiClient()), 'voice_mail')

        with self.assertLogs(level='ERROR') as context_manager:
            voice_mail_handler('{"url": "https://example.com/audio1.mp3", "selected_recipient_ids": [1,2,3]}',
                               dependency_injection_user_id=1)
        self.assertIn("ERROR:root:selected_recipient_ids cannot be "
                      "used without is_selected_recipient_type set to True", context_manager.output)

    def test_error_recipient_type_but_no_ids(self):
        voice_mail_handler = handle_mail(AudioPlayer(ApiClient()), 'voice_mail')

        with self.assertLogs(level='ERROR') as context_manager:
            voice_mail_handler('{"url": "https://example.com/audio1.mp3", "is_selected_recipient_type": true}',
                               dependency_injection_user_id=2)
        self.assertIn("ERROR:root:selected_recipient_ids is not specified for selected recipient type message, "
                      "it must be specified in the message delivered "
                      "for is_selected_recipient_type = True messages!", context_manager.output)

    def test_error_recipients_but_user_id_not_in(self):
        voice_mail_handler = handle_mail(AudioPlayer(ApiClient()), 'voice_mail')

        with self.assertLogs(level='DEBUG') as context_manager:
            voice_mail_handler('{"url": "https://example.com/audio1.mp3", "selected_recipient_ids": [101,102,103], '
                               '"is_selected_recipient_type": true}', dependency_injection_user_id=3)
        self.assertIn("DEBUG:root:message received but skipped since "
                      "the device user is not in the recipient list", context_manager.output)

    @patch('audio_player.AudioPlayer.voice_mail_arrived')
    def test_all_recipients_voice_mail(self, mock_voice_mail_arrived):
        voice_mail_handler = handle_mail(AudioPlayer(ApiClient()), 'voice_mail')
        voice_mail_handler('{"url": "https://example.com/audio1.mp3", "hash": "abcd1234"}', dependency_injection_user_id=4)
        mock_voice_mail_arrived.assert_called_once_with("https://example.com/audio1.mp3", 'abcd1234')

    @patch('audio_player.AudioPlayer.urgent_mail_arrived')
    def test_all_recipients_urgent_mail(self, mock_urgent_mail_arrived):
        urgent_mail_handler = handle_mail(AudioPlayer(ApiClient()), 'urgent_mail')
        urgent_mail_handler('{"url": "https://example.com/audio1.mp3", "hash": "abcd1234"}',
                            dependency_injection_user_id=5)
        mock_urgent_mail_arrived.assert_called_once_with("https://example.com/audio1.mp3", "abcd1234")

    @patch('audio_player.AudioPlayer.injectable_content_arrived')
    def test_all_recipients_injectable_content(self, mock_injectable_content_arrived):
        injectable_content_handler = handle_mail(AudioPlayer(ApiClient()), 'injectable_content')
        injectable_content_handler('{"url": "https://example.com/audio1.mp3"}', dependency_injection_user_id=6)
        mock_injectable_content_arrived.assert_called_once_with({"url": "https://example.com/audio1.mp3"})

    @patch('audio_player.AudioPlayer.injectable_content_arrived')
    def test_all_recipients_injectable_content_with_start_and_end(self, mock_injectable_content_arrived):
        injectable_content_handler = handle_mail(AudioPlayer(ApiClient()), 'injectable_content')
        injectable_content_handler('{"url": "https://example.com/audio1.mp3", "start": 1553047122, "end": 1553547122}',
                                   dependency_injection_user_id=7)
        mock_injectable_content_arrived.assert_called_once_with(
            {"url": "https://example.com/audio1.mp3",
             "start": datetime(2019, 3, 20, 1, 58, 42, tzinfo=pytz.utc),
             "end": datetime(2019, 3, 25, 20, 52, 2, tzinfo=pytz.utc)}
        )

    def test_unknown_message(self):
        injectable_content_handler = handle_mail(AudioPlayer(ApiClient()), 'unknown_message_type')
        with self.assertLogs(level='ERROR') as context_manager:
            injectable_content_handler('{"url": "https://example.com/audio1.mp3", '
                                       '"start": 1553047122, "end": 1553547122}',
                                       dependency_injection_user_id=8)
        self.assertIn("ERROR:root:Unknown message type for handle_mail function: unknown_message_type",
                      context_manager.output)

    @patch('audio_player.AudioPlayer.voice_mail_arrived')
    def test_with_recipients(self, mock_voice_mail_arrived):
        voice_mail_handler = handle_mail(AudioPlayer(ApiClient()), 'voice_mail')
        voice_mail_handler('{"url": "https://example.com/audio1.mp3", "hash": "abcd1234", '
                           '"selected_recipient_ids": [101,102,103], '
                           '"is_selected_recipient_type": true}', dependency_injection_user_id=101)
        mock_voice_mail_arrived.assert_called_once_with("https://example.com/audio1.mp3", 'abcd1234')

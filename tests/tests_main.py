import unittest
from unittest.mock import patch
from audio_player import AudioPlayer
from audio_client import AudioClient
from tests.mock.mock_api_client import ApiClient
from main import PusherService, setup_client, setup_realtime_update, connect_handler, setup_user_channels_and_player, main
from settings import PUSHER_KEY_ID, PUSHER_CLUSTER, PUSHER_SECRET, SUBDOMAIN as SERVER_URL


class _Dummy:
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
        self.assertTrue(client.streaming_url.startswith(SERVER_URL))
        self.assertEqual(client.user_id, "some-user-id")
        self.assertEqual(client.user_password, "some-hash")
        self.assertEqual(client.client_id, "some-client-id")
        self.assertEqual(client.client_secret, "some-client-secret")
        self.assertEqual(client.client_secret, "some-client-secret")
        self.assertIsNone(client.access_token)
        self.assertIsNone(client.refresh_token)
        self.assertTrue(client.channel_url.startswith(SERVER_URL))

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

    @patch('audio_player.AudioPlayer._get_first_audio_url')
    @patch('audio_client.AudioClient.injectable_content_download_fn')
    @patch('audio_client.AudioClient.injectable_content_fetch_available_content_fn')
    @patch('audio_client.AudioClient.get_channels')
    @patch('audio_client.AudioClient.get_user_data')
    def test_setup_user_channels_and_player(self, mock_get_user_data, mock_get_channels,
                                            mock_injectable_content_fetch_available_content_fn,
                                            mock_inj_content_download_fn, mock_get_first_audio_url):
        mock_get_user_data.return_value = _Dummy(text='{"pk": 1}')
        mock_get_channels.return_value = _Dummy(text='{"channels": ["channel.X", "channel.Y"]}')
        mock_injectable_content_fetch_available_content_fn.return_value = []
        mock_inj_content_download_fn.return_value = '[]'
        mock_get_first_audio_url.return_value = 'https://example.com/audio-1.mp3'
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
        volume_up_btn, volume_down_btn, next_btn, emergency_btn = main()
        mock_setup_realtime_update.assert_called_once_with()    # todo problem here
        volume_up_btn.id = 8
        volume_down_btn.id = 7
        next_btn.id = 9
        emergency_btn.id = 10
